# app/modules/pricing/profiles/services/rule_dependency_manager.py
"""
Rule Dependency Management System for Step 6 Completion
Handles rule dependencies, conflict detection, and resolution strategies
"""

from typing import List, Optional, Dict, Any, Set, Tuple
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConflictResolutionStrategy(str, Enum):
    """Strategies for resolving rule conflicts."""
    PRIORITY_BASED = "priority_based"  # Higher priority wins
    FIRST_MATCH = "first_match"        # First matching rule wins
    LAST_MATCH = "last_match"          # Last matching rule wins
    AGGREGATE = "aggregate"            # Combine all matching rules
    FAIL_ON_CONFLICT = "fail_on_conflict"  # Throw error on conflict


class DependencyType(str, Enum):
    """Types of rule dependencies."""
    PREREQUISITE = "prerequisite"      # Rule must execute before this one
    EXCLUSION = "exclusion"           # Rules cannot execute together
    CONDITIONAL = "conditional"       # Rule depends on condition result
    SEQUENCE = "sequence"             # Rules must execute in specific order


@dataclass
class RuleDependency:
    """Represents a dependency between two rules."""
    dependent_rule_id: UUID
    dependency_rule_id: UUID
    dependency_type: DependencyType
    condition: Optional[str] = None  # JSON condition for conditional dependencies
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RuleConflict:
    """Represents a conflict between rules."""
    conflict_id: str
    rule_ids: List[UUID]
    conflict_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    suggested_resolution: str
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RuleExecutionPlan:
    """Execution plan for a set of rules."""
    execution_order: List[UUID]
    conflicts: List[RuleConflict]
    resolution_strategy: ConflictResolutionStrategy
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuleDependencyManager:
    """
    Manages rule dependencies, detects conflicts, and creates execution plans.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.dependencies: Dict[UUID, List[RuleDependency]] = defaultdict(list)
        self.rule_priorities: Dict[UUID, int] = {}
        self.conflict_cache: Dict[str, RuleConflict] = {}
    
    # ============================================================================
    # DEPENDENCY MANAGEMENT
    # ============================================================================
    
    def add_dependency(
        self,
        dependent_rule_id: UUID,
        dependency_rule_id: UUID,
        dependency_type: DependencyType,
        condition: Optional[str] = None,
        description: Optional[str] = None
    ) -> RuleDependency:
        """
        Add a dependency relationship between two rules.
        
        Args:
            dependent_rule_id: Rule that depends on another
            dependency_rule_id: Rule that is depended upon
            dependency_type: Type of dependency
            condition: Optional condition for conditional dependencies
            description: Human-readable description
            
        Returns:
            Created dependency object
            
        Raises:
            ValidationError: If dependency would create circular reference
        """
        dependency = RuleDependency(
            dependent_rule_id=dependent_rule_id,
            dependency_rule_id=dependency_rule_id,
            dependency_type=dependency_type,
            condition=condition,
            description=description
        )
        
        # Check for circular dependencies before adding
        if self._would_create_circular_dependency(dependency):
            raise ValidationError(
                f"Adding dependency would create circular reference: "
                f"{dependent_rule_id} -> {dependency_rule_id}"
            )
        
        self.dependencies[dependent_rule_id].append(dependency)
        
        logger.info(
            f"Added {dependency_type} dependency: "
            f"{dependent_rule_id} -> {dependency_rule_id}"
        )
        
        return dependency
    
    def remove_dependency(
        self,
        dependent_rule_id: UUID,
        dependency_rule_id: UUID,
        dependency_type: Optional[DependencyType] = None
    ) -> bool:
        """
        Remove a dependency relationship.
        
        Args:
            dependent_rule_id: Rule that depends on another
            dependency_rule_id: Rule that is depended upon
            dependency_type: Optional specific type to remove
            
        Returns:
            True if dependency was removed, False if not found
        """
        if dependent_rule_id not in self.dependencies:
            return False
        
        dependencies = self.dependencies[dependent_rule_id]
        original_count = len(dependencies)
        
        # Filter out matching dependencies
        self.dependencies[dependent_rule_id] = [
            dep for dep in dependencies
            if not (
                dep.dependency_rule_id == dependency_rule_id and
                (dependency_type is None or dep.dependency_type == dependency_type)
            )
        ]
        
        removed = len(dependencies) - len(self.dependencies[dependent_rule_id])
        
        if removed > 0:
            logger.info(f"Removed {removed} dependencies between {dependent_rule_id} and {dependency_rule_id}")
        
        return removed > 0
    
    def get_dependencies(self, rule_id: UUID) -> List[RuleDependency]:
        """Get all dependencies for a rule."""
        return self.dependencies.get(rule_id, [])
    
    def get_dependents(self, rule_id: UUID) -> List[RuleDependency]:
        """Get all rules that depend on the given rule."""
        dependents = []
        for dependent_id, deps in self.dependencies.items():
            for dep in deps:
                if dep.dependency_rule_id == rule_id:
                    dependents.append(dep)
        return dependents
    
    # ============================================================================
    # CONFLICT DETECTION
    # ============================================================================
    
    def detect_conflicts(self, rule_ids: List[UUID]) -> List[RuleConflict]:
        """
        Detect conflicts between a set of rules.
        
        Args:
            rule_ids: List of rule IDs to check for conflicts
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check for exclusion conflicts
        conflicts.extend(self._detect_exclusion_conflicts(rule_ids))
        
        # Check for priority conflicts
        conflicts.extend(self._detect_priority_conflicts(rule_ids))
        
        # Check for field conflicts (rules affecting same field)
        conflicts.extend(self._detect_field_conflicts(rule_ids))
        
        # Check for dependency violations
        conflicts.extend(self._detect_dependency_violations(rule_ids))
        
        # Cache conflicts for performance
        for conflict in conflicts:
            self.conflict_cache[conflict.conflict_id] = conflict
        
        return conflicts
    
    def _detect_exclusion_conflicts(self, rule_ids: List[UUID]) -> List[RuleConflict]:
        """Detect rules that explicitly exclude each other."""
        conflicts = []
        
        for rule_id in rule_ids:
            dependencies = self.get_dependencies(rule_id)
            exclusions = [
                dep for dep in dependencies 
                if dep.dependency_type == DependencyType.EXCLUSION
            ]
            
            for exclusion in exclusions:
                if exclusion.dependency_rule_id in rule_ids:
                    conflict_id = f"exclusion_{min(rule_id, exclusion.dependency_rule_id)}_{max(rule_id, exclusion.dependency_rule_id)}"
                    
                    if conflict_id not in self.conflict_cache:
                        conflicts.append(RuleConflict(
                            conflict_id=conflict_id,
                            rule_ids=[rule_id, exclusion.dependency_rule_id],
                            conflict_type="EXCLUSION",
                            severity="HIGH",
                            description=f"Rules {rule_id} and {exclusion.dependency_rule_id} are mutually exclusive",
                            suggested_resolution="Remove one rule or modify exclusion dependency"
                        ))
        
        return conflicts
    
    def _detect_priority_conflicts(self, rule_ids: List[UUID]) -> List[RuleConflict]:
        """Detect rules with same priority that might conflict."""
        conflicts = []
        priority_groups = defaultdict(list)
        
        # Group rules by priority
        for rule_id in rule_ids:
            priority = self.rule_priorities.get(rule_id, 0)
            priority_groups[priority].append(rule_id)
        
        # Check for conflicts within same priority groups
        for priority, rules in priority_groups.items():
            if len(rules) > 1:
                conflict_id = f"priority_{priority}_{hash(tuple(sorted(rules)))}"
                conflicts.append(RuleConflict(
                    conflict_id=conflict_id,
                    rule_ids=rules,
                    conflict_type="PRIORITY",
                    severity="MEDIUM",
                    description=f"Multiple rules with same priority {priority}: {rules}",
                    suggested_resolution="Assign different priorities or use aggregation strategy"
                ))
        
        return conflicts
    
    def _detect_field_conflicts(self, rule_ids: List[UUID]) -> List[RuleConflict]:
        """Detect rules that modify the same field."""
        # This would require access to rule definitions to check field impacts
        # Placeholder for field conflict detection
        conflicts = []
        
        # TODO: Implement field conflict detection
        # This would involve:
        # 1. Get field names affected by each rule
        # 2. Group rules by affected fields
        # 3. Check for conflicting modifications
        
        return conflicts
    
    def _detect_dependency_violations(self, rule_ids: List[UUID]) -> List[RuleConflict]:
        """Detect violations of prerequisite dependencies."""
        conflicts = []
        
        for rule_id in rule_ids:
            dependencies = self.get_dependencies(rule_id)
            prerequisites = [
                dep for dep in dependencies 
                if dep.dependency_type == DependencyType.PREREQUISITE
            ]
            
            for prereq in prerequisites:
                if prereq.dependency_rule_id not in rule_ids:
                    conflict_id = f"missing_prereq_{rule_id}_{prereq.dependency_rule_id}"
                    conflicts.append(RuleConflict(
                        conflict_id=conflict_id,
                        rule_ids=[rule_id],
                        conflict_type="MISSING_PREREQUISITE",
                        severity="HIGH",
                        description=f"Rule {rule_id} requires prerequisite {prereq.dependency_rule_id} which is not included",
                        suggested_resolution=f"Include rule {prereq.dependency_rule_id} or remove dependency"
                    ))
        
        return conflicts
    
    # ============================================================================
    # EXECUTION PLANNING
    # ============================================================================
    
    def create_execution_plan(
        self,
        rule_ids: List[UUID],
        resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.PRIORITY_BASED
    ) -> RuleExecutionPlan:
        """
        Create an execution plan for a set of rules.
        
        Args:
            rule_ids: Rules to include in the plan
            resolution_strategy: How to resolve conflicts
            
        Returns:
            Execution plan with order and conflict information
        """
        # Detect conflicts
        conflicts = self.detect_conflicts(rule_ids)
        
        # Filter out conflicting rules based on resolution strategy
        filtered_rule_ids = self._resolve_conflicts(rule_ids, conflicts, resolution_strategy)
        
        # Create topological ordering based on dependencies
        execution_order = self._topological_sort(filtered_rule_ids)
        
        return RuleExecutionPlan(
            execution_order=execution_order,
            conflicts=conflicts,
            resolution_strategy=resolution_strategy,
            metadata={
                "original_rule_count": len(rule_ids),
                "final_rule_count": len(execution_order),
                "conflicts_detected": len(conflicts),
                "planning_timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def _resolve_conflicts(
        self,
        rule_ids: List[UUID],
        conflicts: List[RuleConflict],
        strategy: ConflictResolutionStrategy
    ) -> List[UUID]:
        """Resolve conflicts based on the chosen strategy."""
        
        if strategy == ConflictResolutionStrategy.FAIL_ON_CONFLICT:
            if conflicts:
                conflict_descriptions = [c.description for c in conflicts]
                raise BusinessLogicError(f"Rule conflicts detected: {conflict_descriptions}")
            return rule_ids
        
        elif strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            return self._resolve_by_priority(rule_ids, conflicts)
        
        elif strategy == ConflictResolutionStrategy.FIRST_MATCH:
            return self._resolve_by_first_match(rule_ids, conflicts)
        
        elif strategy == ConflictResolutionStrategy.LAST_MATCH:
            return self._resolve_by_last_match(rule_ids, conflicts)
        
        elif strategy == ConflictResolutionStrategy.AGGREGATE:
            # For aggregation, we keep all rules and handle conflicts during execution
            return rule_ids
        
        else:
            logger.warning(f"Unknown conflict resolution strategy: {strategy}")
            return rule_ids
    
    def _resolve_by_priority(self, rule_ids: List[UUID], conflicts: List[RuleConflict]) -> List[UUID]:
        """Resolve conflicts by keeping highest priority rules."""
        excluded_rules = set()
        
        for conflict in conflicts:
            if conflict.conflict_type in ["EXCLUSION", "PRIORITY"]:
                # Sort conflicting rules by priority (highest first)
                conflict_rules = [(rule_id, self.rule_priorities.get(rule_id, 0)) for rule_id in conflict.rule_ids]
                conflict_rules.sort(key=lambda x: x[1], reverse=True)
                
                # Keep highest priority rule, exclude others
                for rule_id, _ in conflict_rules[1:]:
                    excluded_rules.add(rule_id)
        
        return [rule_id for rule_id in rule_ids if rule_id not in excluded_rules]
    
    def _resolve_by_first_match(self, rule_ids: List[UUID], conflicts: List[RuleConflict]) -> List[UUID]:
        """Resolve conflicts by keeping the first matching rule."""
        excluded_rules = set()
        
        for conflict in conflicts:
            if len(conflict.rule_ids) > 1:
                # Keep first rule in original order, exclude others
                first_rule = conflict.rule_ids[0]
                for rule_id in conflict.rule_ids[1:]:
                    excluded_rules.add(rule_id)
        
        return [rule_id for rule_id in rule_ids if rule_id not in excluded_rules]
    
    def _resolve_by_last_match(self, rule_ids: List[UUID], conflicts: List[RuleConflict]) -> List[UUID]:
        """Resolve conflicts by keeping the last matching rule."""
        excluded_rules = set()
        
        for conflict in conflicts:
            if len(conflict.rule_ids) > 1:
                # Keep last rule in original order, exclude others
                last_rule = conflict.rule_ids[-1]
                for rule_id in conflict.rule_ids[:-1]:
                    excluded_rules.add(rule_id)
        
        return [rule_id for rule_id in rule_ids if rule_id not in excluded_rules]
    
    def _topological_sort(self, rule_ids: List[UUID]) -> List[UUID]:
        """
        Create topological ordering of rules based on dependencies.
        
        Args:
            rule_ids: Rules to sort
            
        Returns:
            Topologically sorted list of rule IDs
        """
        # Build adjacency list for rules with dependencies
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize in-degree for all rules
        for rule_id in rule_ids:
            in_degree[rule_id] = 0
        
        # Build graph based on prerequisite dependencies
        for rule_id in rule_ids:
            dependencies = self.get_dependencies(rule_id)
            prerequisites = [
                dep for dep in dependencies 
                if dep.dependency_type == DependencyType.PREREQUISITE and dep.dependency_rule_id in rule_ids
            ]
            
            for prereq in prerequisites:
                graph[prereq.dependency_rule_id].append(rule_id)
                in_degree[rule_id] += 1
        
        # Kahn's algorithm for topological sorting
        queue = deque([rule_id for rule_id in rule_ids if in_degree[rule_id] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for circular dependencies
        if len(result) != len(rule_ids):
            remaining_rules = [rule_id for rule_id in rule_ids if rule_id not in result]
            logger.warning(f"Circular dependencies detected for rules: {remaining_rules}")
            # Add remaining rules at the end
            result.extend(remaining_rules)
        
        return result
    
    # ============================================================================
    # CIRCULAR DEPENDENCY DETECTION
    # ============================================================================
    
    def _would_create_circular_dependency(self, new_dependency: RuleDependency) -> bool:
        """
        Check if adding a dependency would create a circular reference.
        
        Args:
            new_dependency: Dependency to check
            
        Returns:
            True if circular dependency would be created
        """
        # Only check for prerequisite and sequence dependencies
        if new_dependency.dependency_type not in [DependencyType.PREREQUISITE, DependencyType.SEQUENCE]:
            return False
        
        # Use DFS to detect cycles
        return self._has_path(
            new_dependency.dependency_rule_id,
            new_dependency.dependent_rule_id,
            set()
        )
    
    def _has_path(self, start: UUID, target: UUID, visited: Set[UUID]) -> bool:
        """
        Check if there's a path from start to target in the dependency graph.
        
        Args:
            start: Starting rule ID
            target: Target rule ID
            visited: Set of already visited rules
            
        Returns:
            True if path exists
        """
        if start == target:
            return True
        
        if start in visited:
            return False
        
        visited.add(start)
        
        # Check all rules that depend on the current rule
        for dependent_id, deps in self.dependencies.items():
            for dep in deps:
                if (dep.dependency_rule_id == start and 
                    dep.dependency_type in [DependencyType.PREREQUISITE, DependencyType.SEQUENCE]):
                    if self._has_path(dependent_id, target, visited.copy()):
                        return True
        
        return False
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def set_rule_priority(self, rule_id: UUID, priority: int):
        """Set priority for a rule."""
        self.rule_priorities[rule_id] = priority
        logger.debug(f"Set priority {priority} for rule {rule_id}")
    
    def get_rule_priority(self, rule_id: UUID) -> int:
        """Get priority for a rule (default: 0)."""
        return self.rule_priorities.get(rule_id, 0)
    
    def clear_dependencies(self, rule_id: UUID):
        """Clear all dependencies for a rule."""
        if rule_id in self.dependencies:
            del self.dependencies[rule_id]
        logger.info(f"Cleared all dependencies for rule {rule_id}")
    
    def export_dependency_graph(self) -> Dict[str, Any]:
        """Export the entire dependency graph for analysis or backup."""
        return {
            "dependencies": {
                str(rule_id): [
                    {
                        "dependency_rule_id": str(dep.dependency_rule_id),
                        "dependency_type": dep.dependency_type.value,
                        "condition": dep.condition,
                        "description": dep.description,
                        "created_at": dep.created_at.isoformat()
                    }
                    for dep in deps
                ]
                for rule_id, deps in self.dependencies.items()
            },
            "priorities": {str(k): v for k, v in self.rule_priorities.items()},
            "export_timestamp": datetime.utcnow().isoformat()
        }
    
    def import_dependency_graph(self, graph_data: Dict[str, Any]):
        """Import dependency graph from exported data."""
        # Clear existing data
        self.dependencies.clear()
        self.rule_priorities.clear()
        
        # Import dependencies
        for rule_id_str, deps_data in graph_data.get("dependencies", {}).items():
            rule_id = UUID(rule_id_str)
            for dep_data in deps_data:
                dependency = RuleDependency(
                    dependent_rule_id=rule_id,
                    dependency_rule_id=UUID(dep_data["dependency_rule_id"]),
                    dependency_type=DependencyType(dep_data["dependency_type"]),
                    condition=dep_data.get("condition"),
                    description=dep_data.get("description"),
                    created_at=datetime.fromisoformat(dep_data["created_at"])
                )
                self.dependencies[rule_id].append(dependency)
        
        # Import priorities
        for rule_id_str, priority in graph_data.get("priorities", {}).items():
            self.rule_priorities[UUID(rule_id_str)] = priority
        
        logger.info("Imported dependency graph successfully")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """Demonstrate the rule dependency manager."""
    manager = RuleDependencyManager()
    
    # Example rule IDs
    age_rule = UUID('11111111-1111-1111-1111-111111111111')
    premium_rule = UUID('22222222-2222-2222-2222-222222222222')
    discount_rule = UUID('33333333-3333-3333-3333-333333333333')
    loyalty_rule = UUID('44444444-4444-4444-4444-444444444444')
    
    # Set priorities
    manager.set_rule_priority(age_rule, 100)
    manager.set_rule_priority(premium_rule, 200)
    manager.set_rule_priority(discount_rule, 150)
    manager.set_rule_priority(loyalty_rule, 175)
    
    # Add dependencies
    manager.add_dependency(
        discount_rule, age_rule,
        DependencyType.PREREQUISITE,
        description="Discount rule requires age validation first"
    )
    
    manager.add_dependency(
        loyalty_rule, premium_rule,
        DependencyType.PREREQUISITE,
        description="Loyalty rule requires premium calculation first"
    )
    
    manager.add_dependency(
        discount_rule, loyalty_rule,
        DependencyType.EXCLUSION,
        description="Cannot apply both discount and loyalty benefits"
    )
    
    # Create execution plan
    rule_ids = [age_rule, premium_rule, discount_rule, loyalty_rule]
    plan = manager.create_execution_plan(rule_ids)
    
    print(f"Execution order: {plan.execution_order}")
    print(f"Conflicts detected: {len(plan.conflicts)}")
    for conflict in plan.conflicts:
        print(f"  - {conflict.conflict_type}: {conflict.description}")


if __name__ == "__main__":
    example_usage()