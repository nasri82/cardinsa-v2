# app/modules/pricing/profiles/schemas/advanced_rule_schema.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

class ConditionNodeSchema(BaseModel):
    operator: str
    field: Optional[str] = None
    value: Any = None
    conditions: Optional[List['ConditionNodeSchema']] = None

class RuleImpactSchema(BaseModel):
    type: str
    value: Any
    formula: Optional[str] = None
    description: Optional[str] = None

class AdvancedRuleSchema(BaseModel):
    rule_id: UUID
    name: str
    description: Optional[str]
    conditions: ConditionNodeSchema
    impact: RuleImpactSchema
    priority: int = 0
    is_active: bool = True