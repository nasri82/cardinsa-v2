# app/modules/insurance/quotations/services/quotation_workflow_service.py

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import logging

from ..models import QuotationWorkflowLog, WorkflowEventType
from ..schemas import (
    QuotationWorkflowLogCreate, QuotationWorkflowLogResponse,
    QuotationWorkflowEventRequest, QuotationWorkflowTimeline,
    QuotationWorkflowMetrics, WorkflowEvent, EventCategory
)
from ..repositories import QuotationRepository
from app.core.exceptions import BusinessLogicError, ValidationError, NotFoundError


logger = logging.getLogger(__name__)


class QuotationWorkflowService:
    """
    Service class for Quotation Workflow management
    
    Handles workflow event logging, timeline tracking, performance metrics,
    and business process automation for quotations.
    """

    def __init__(self, db: Session):
        self.db = db
        self.quotation_repo = QuotationRepository(db)
        # Note: QuotationWorkflowLogRepository would be imported here when created

    # ========== EVENT LOGGING OPERATIONS ==========

    async def log_event(self, quotation_id: UUID, event: str, notes: str = None,
                       created_by: UUID = None) -> QuotationWorkflowLogResponse:
        """Log a workflow event for a quotation"""
        try:
            # Validate quotation exists
            quotation = self.quotation_repo.get(quotation_id)
            if not quotation:
                raise NotFoundError("Quotation not found")
            
            # Create workflow log entry
            log_data = QuotationWorkflowLogCreate(
                quotation_id=quotation_id,
                event=event,
                notes=notes,
                created_by=created_by
            )
            
            # This would use QuotationWorkflowLogRepository when implemented
            workflow_log = QuotationWorkflowLog(
                quotation_id=quotation_id,
                event=event,
                notes=notes,
                created_by=created_by
            )
            
            self.db.add(workflow_log)
            self.db.commit()
            self.db.refresh(workflow_log)
            
            logger.info(f"Logged workflow event '{event}' for quotation {quotation_id}")
            
            return QuotationWorkflowLogResponse.from_orm(workflow_log)
            
        except Exception as e:
            logger.error(f"Error logging workflow event: {str(e)}")
            raise BusinessLogicError(f"Failed to log workflow event: {str(e)}")

    async def log_lifecycle_event(self, quotation_id: UUID, event_type: WorkflowEventType,
                                 notes: str = None, created_by: UUID = None) -> QuotationWorkflowLogResponse:
        """Log a lifecycle event using predefined event types"""
        try:
            return await self.log_event(
                quotation_id=quotation_id,
                event=event_type.value,
                notes=notes,
                created_by=created_by
            )
            
        except Exception as e:
            logger.error(f"Error logging lifecycle event: {str(e)}")
            raise BusinessLogicError(f"Failed to log lifecycle event: {str(e)}")

    async def log_system_event(self, quotation_id: UUID, event_type: WorkflowEventType,
                              notes: str = None) -> QuotationWorkflowLogResponse:
        """Log a system-generated event"""
        try:
            return await self.log_event(
                quotation_id=quotation_id,
                event=event_type.value,
                notes=notes,
                created_by=None  # System events have no user
            )
            
        except Exception as e:
            logger.error(f"Error logging system event: {str(e)}")
            raise BusinessLogicError(f"Failed to log system event: {str(e)}")

    async def log_user_action(self, quotation_id: UUID, event: str, user_id: UUID,
                             notes: str = None) -> QuotationWorkflowLogResponse:
        """Log a user-triggered action"""
        try:
            return await self.log_event(
                quotation_id=quotation_id,
                event=event,
                notes=notes,
                created_by=user_id
            )
            
        except Exception as e:
            logger.error(f"Error logging user action: {str(e)}")
            raise BusinessLogicError(f"Failed to log user action: {str(e)}")

    # ========== WORKFLOW ANALYSIS ==========

    async def get_workflow_timeline(self, quotation_id: UUID, limit: int = 100) -> QuotationWorkflowTimeline:
        """Get complete workflow timeline for a quotation"""
        try:
            # This would use repository method when implemented
            # For now, simulate the structure
            events = []  # Would come from repository
            
            # Calculate timeline metrics
            total_events = len(events)
            
            event_categories = {}
            for event in events:
                category = self._categorize_event(event.event)
                event_categories[category] = event_categories.get(category, 0) + 1
            
            # Calculate time span
            time_span = None
            most_active_period = None
            
            if events:
                first_event = min(events, key=lambda x: x.created_at)
                last_event = max(events, key=lambda x: x.created_at)
                time_span = int((last_event.created_at - first_event.created_at).total_seconds() / 60)
                
                # Find most active period (simplified)
                most_active_period = "Morning"  # Would be calculated from actual data
            
            timeline = QuotationWorkflowTimeline(
                quotation_id=quotation_id,
                events=[QuotationWorkflowLogResponse.from_orm(event) for event in events],
                total_events=total_events,
                event_categories=event_categories,
                time_span=time_span,
                most_active_period=most_active_period
            )
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error retrieving workflow timeline: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve workflow timeline: {str(e)}")

    async def get_workflow_metrics(self, quotation_id: UUID) -> QuotationWorkflowMetrics:
        """Get workflow performance metrics"""
        try:
            # This would use repository methods when implemented
            # For now, simulate the structure
            events = []  # Would come from repository
            
            total_events = len(events)
            system_events = len([e for e in events if not e.created_by])
            user_events = total_events - system_events
            critical_events = len([e for e in events if self._is_critical_event(e.event)])
            
            # Calculate events by category
            events_by_category = {}
            for event in events:
                category = EventCategory(self._categorize_event(event.event))
                events_by_category[category] = events_by_category.get(category, 0) + 1
            
            # Calculate hourly distribution
            events_by_hour = {}
            for event in events:
                hour = event.created_at.hour
                events_by_hour[hour] = events_by_hour.get(hour, 0) + 1
            
            # Calculate averages
            if events:
                first_event = min(events, key=lambda x: x.created_at)
                last_event = max(events, key=lambda x: x.created_at)
                days = max(1, (last_event.created_at - first_event.created_at).days)
                average_events_per_day = total_events / days
            else:
                average_events_per_day = 0.0
            
            # Find peak activity hour
            peak_activity_hour = max(events_by_hour.keys(), key=events_by_hour.get) if events_by_hour else None
            
            metrics = QuotationWorkflowMetrics(
                quotation_id=quotation_id,
                total_events=total_events,
                system_events=system_events,
                user_events=user_events,
                critical_events=critical_events,
                events_by_category=events_by_category,
                events_by_hour=events_by_hour,
                average_events_per_day=average_events_per_day,
                peak_activity_hour=peak_activity_hour
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error retrieving workflow metrics: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve workflow metrics: {str(e)}")

    # ========== WORKFLOW AUTOMATION ==========

    async def trigger_automated_workflows(self, quotation_id: UUID, trigger_event: str,
                                         context: Dict[str, Any] = None) -> List[str]:
        """Trigger automated workflows based on events"""
        try:
            triggered_workflows = []
            
            # Define automation rules
            automation_rules = {
                'quotation_created': ['send_welcome_email', 'assign_to_agent'],
                'premium_calculated': ['generate_pdf', 'send_to_customer'],
                'quotation_approved': ['set_expiry_reminder', 'notify_customer'],
                'quotation_expired': ['send_renewal_notice', 'archive_quotation'],
                'quotation_converted': ['create_policy', 'send_confirmation']
            }
            
            workflows_to_trigger = automation_rules.get(trigger_event, [])
            
            for workflow in workflows_to_trigger:
                try:
                    success = await self._execute_workflow(quotation_id, workflow, context)
                    if success:
                        triggered_workflows.append(workflow)
                        
                        # Log the automated workflow execution
                        await self.log_system_event(
                            quotation_id=quotation_id,
                            event_type=WorkflowEventType.VALIDATION_PASSED,  # Use appropriate event type
                            notes=f"Automated workflow executed: {workflow}"
                        )
                        
                except Exception as workflow_error:
                    logger.error(f"Failed to execute workflow {workflow}: {str(workflow_error)}")
                    
                    # Log the failure
                    await self.log_system_event(
                        quotation_id=quotation_id,
                        event_type=WorkflowEventType.VALIDATION_FAILED,
                        notes=f"Automated workflow failed: {workflow} - {str(workflow_error)}"
                    )
            
            return triggered_workflows
            
        except Exception as e:
            logger.error(f"Error triggering automated workflows: {str(e)}")
            raise BusinessLogicError(f"Failed to trigger automated workflows: {str(e)}")

    async def schedule_workflow_reminders(self, quotation_id: UUID) -> List[str]:
        """Schedule workflow reminders based on quotation state"""
        try:
            quotation = self.quotation_repo.get(quotation_id)
            if not quotation:
                raise NotFoundError("Quotation not found")
            
            scheduled_reminders = []
            
            # Check for various reminder conditions
            if quotation.status == 'pending_approval':
                # Schedule approval reminder
                reminder_time = datetime.utcnow() + timedelta(hours=24)
                await self._schedule_reminder(quotation_id, 'approval_reminder', reminder_time)
                scheduled_reminders.append('approval_reminder')
            
            if quotation.quote_expires_at:
                # Schedule expiry reminder
                reminder_time = quotation.quote_expires_at - timedelta(days=3)
                if reminder_time > datetime.utcnow():
                    await self._schedule_reminder(quotation_id, 'expiry_reminder', reminder_time)
                    scheduled_reminders.append('expiry_reminder')
            
            if quotation.follow_up_date:
                # Schedule follow-up reminder
                reminder_time = datetime.combine(quotation.follow_up_date, datetime.min.time())
                await self._schedule_reminder(quotation_id, 'follow_up_reminder', reminder_time)
                scheduled_reminders.append('follow_up_reminder')
            
            return scheduled_reminders
            
        except Exception as e:
            logger.error(f"Error scheduling workflow reminders: {str(e)}")
            raise BusinessLogicError(f"Failed to schedule workflow reminders: {str(e)}")

    # ========== PERFORMANCE MONITORING ==========

    async def analyze_workflow_performance(self, quotation_id: UUID) -> Dict[str, Any]:
        """Analyze workflow performance and identify bottlenecks"""
        try:
            timeline = await self.get_workflow_timeline(quotation_id)
            
            performance_analysis = {
                'efficiency_score': 0.0,
                'bottlenecks': [],
                'recommendations': [],
                'stage_durations': {},
                'total_processing_time': 0
            }
            
            if not timeline.events:
                return performance_analysis
            
            # Calculate stage durations
            stages = self._identify_workflow_stages(timeline.events)
            stage_durations = {}
            
            for i, stage in enumerate(stages):
                if i < len(stages) - 1:
                    duration = (stages[i + 1].created_at - stage.created_at).total_seconds() / 60
                    stage_name = self._get_stage_name(stage.event)
                    stage_durations[stage_name] = duration
            
            performance_analysis['stage_durations'] = stage_durations
            
            # Calculate total processing time
            if len(timeline.events) > 1:
                first_event = min(timeline.events, key=lambda x: x.created_at)
                last_event = max(timeline.events, key=lambda x: x.created_at)
                total_time = (last_event.created_at - first_event.created_at).total_seconds() / 60
                performance_analysis['total_processing_time'] = total_time
            
            # Identify bottlenecks (stages taking longer than average)
            if stage_durations:
                avg_duration = sum(stage_durations.values()) / len(stage_durations)
                bottlenecks = [
                    stage for stage, duration in stage_durations.items() 
                    if duration > avg_duration * 1.5
                ]
                performance_analysis['bottlenecks'] = bottlenecks
            
            # Calculate efficiency score (inverse of processing time vs benchmark)
            benchmark_time = 60  # 1 hour benchmark
            if performance_analysis['total_processing_time'] > 0:
                efficiency_score = min(1.0, benchmark_time / performance_analysis['total_processing_time'])
                performance_analysis['efficiency_score'] = efficiency_score
            
            # Generate recommendations
            recommendations = []
            if performance_analysis['efficiency_score'] < 0.5:
                recommendations.append("Consider streamlining the approval process")
            
            if 'pending_approval' in performance_analysis['bottlenecks']:
                recommendations.append("Approval stage is taking longer than expected")
            
            if len(timeline.events) > 20:
                recommendations.append("High number of events may indicate process inefficiency")
            
            performance_analysis['recommendations'] = recommendations
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing workflow performance: {str(e)}")
            raise BusinessLogicError(f"Failed to analyze workflow performance: {str(e)}")

    # ========== HELPER METHODS ==========

    def _categorize_event(self, event: str) -> str:
        """Categorize workflow event"""
        event_categories = {
            'created': EventCategory.LIFECYCLE,
            'calculated': EventCategory.PRICING,
            'submitted': EventCategory.LIFECYCLE,
            'approved': EventCategory.APPROVAL,
            'rejected': EventCategory.APPROVAL,
            'modified': EventCategory.MODIFICATION,
            'expired': EventCategory.LIFECYCLE,
            'converted': EventCategory.LIFECYCLE,
            'locked': EventCategory.SECURITY,
            'unlocked': EventCategory.SECURITY,
            'document': EventCategory.DOCUMENTATION,
            'email': EventCategory.COMMUNICATION,
            'reminder': EventCategory.COMMUNICATION,
            'follow_up': EventCategory.COMMUNICATION,
            'viewed': EventCategory.INTERACTION,
            'assigned': EventCategory.ASSIGNMENT,
            'pricing': EventCategory.PRICING,
            'coverage': EventCategory.MODIFICATION,
            'validation': EventCategory.VALIDATION
        }
        
        event_lower = event.lower()
        for keyword, category in event_categories.items():
            if keyword in event_lower:
                return category.value
        
        return EventCategory.GENERAL.value

    def _is_critical_event(self, event: str) -> bool:
        """Check if event is critical"""
        critical_events = [
            WorkflowEventType.APPROVED.value,
            WorkflowEventType.REJECTED.value,
            WorkflowEventType.CONVERTED.value,
            WorkflowEventType.EXPIRED.value,
            WorkflowEventType.VALIDATION_FAILED.value
        ]
        return event in critical_events

    def _identify_workflow_stages(self, events: List) -> List:
        """Identify major workflow stages from events"""
        stage_events = []
        stage_keywords = ['created', 'calculated', 'submitted', 'approved', 'converted']
        
        for event in events:
            if any(keyword in event.event.lower() for keyword in stage_keywords):
                stage_events.append(event)
        
        return sorted(stage_events, key=lambda x: x.created_at)

    def _get_stage_name(self, event: str) -> str:
        """Get human-readable stage name from event"""
        stage_mapping = {
            'created': 'Creation',
            'calculated': 'Calculation',
            'submitted': 'Submission',
            'approved': 'Approval',
            'converted': 'Conversion',
            'rejected': 'Rejection',
            'expired': 'Expiration'
        }
        
        event_lower = event.lower()
        for keyword, stage_name in stage_mapping.items():
            if keyword in event_lower:
                return stage_name
        
        return 'Unknown Stage'

    async def _execute_workflow(self, quotation_id: UUID, workflow_name: str,
                               context: Dict[str, Any] = None) -> bool:
        """Execute a specific automated workflow"""
        try:
            workflow_handlers = {
                'send_welcome_email': self._send_welcome_email,
                'assign_to_agent': self._assign_to_agent,
                'generate_pdf': self._generate_pdf,
                'send_to_customer': self._send_to_customer,
                'set_expiry_reminder': self._set_expiry_reminder,
                'notify_customer': self._notify_customer,
                'send_renewal_notice': self._send_renewal_notice,
                'archive_quotation': self._archive_quotation,
                'create_policy': self._create_policy,
                'send_confirmation': self._send_confirmation
            }
            
            handler = workflow_handlers.get(workflow_name)
            if handler:
                return await handler(quotation_id, context)
            else:
                logger.warning(f"Unknown workflow: {workflow_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_name}: {str(e)}")
            return False

    async def _schedule_reminder(self, quotation_id: UUID, reminder_type: str,
                               reminder_time: datetime) -> bool:
        """Schedule a workflow reminder"""
        try:
            # This would integrate with a task scheduler/queue system
            # For now, just log the scheduling
            logger.info(f"Scheduled {reminder_type} for quotation {quotation_id} at {reminder_time}")
            
            # Log the reminder scheduling
            await self.log_system_event(
                quotation_id=quotation_id,
                event_type=WorkflowEventType.REMINDER_SENT,
                notes=f"Scheduled {reminder_type} for {reminder_time}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling reminder: {str(e)}")
            return False

    # ========== WORKFLOW HANDLERS ==========

    async def _send_welcome_email(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Send welcome email to customer"""
        try:
            # This would integrate with email service
            logger.info(f"Sending welcome email for quotation {quotation_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False

    async def _assign_to_agent(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Assign quotation to an agent"""
        try:
            # This would integrate with agent assignment logic
            logger.info(f"Assigning quotation {quotation_id} to agent")
            return True
        except Exception as e:
            logger.error(f"Error assigning to agent: {str(e)}")
            return False

    async def _generate_pdf(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Generate PDF document for quotation"""
        try:
            # This would integrate with document generation service
            logger.info(f"Generating PDF for quotation {quotation_id}")
            return True
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return False

    async def _send_to_customer(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Send quotation to customer"""
        try:
            # This would integrate with communication service
            logger.info(f"Sending quotation {quotation_id} to customer")
            return True
        except Exception as e:
            logger.error(f"Error sending to customer: {str(e)}")
            return False

    async def _set_expiry_reminder(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Set expiry reminder for quotation"""
        try:
            quotation = self.quotation_repo.get(quotation_id)
            if quotation and quotation.quote_expires_at:
                reminder_time = quotation.quote_expires_at - timedelta(days=3)
                return await self._schedule_reminder(quotation_id, 'expiry_reminder', reminder_time)
            return True
        except Exception as e:
            logger.error(f"Error setting expiry reminder: {str(e)}")
            return False

    async def _notify_customer(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Notify customer of quotation status"""
        try:
            logger.info(f"Notifying customer about quotation {quotation_id}")
            return True
        except Exception as e:
            logger.error(f"Error notifying customer: {str(e)}")
            return False

    async def _send_renewal_notice(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Send renewal notice for expired quotation"""
        try:
            logger.info(f"Sending renewal notice for quotation {quotation_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending renewal notice: {str(e)}")
            return False

    async def _archive_quotation(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Archive expired quotation"""
        try:
            success = self.quotation_repo.soft_delete(quotation_id)
            if success:
                logger.info(f"Archived quotation {quotation_id}")
            return success
        except Exception as e:
            logger.error(f"Error archiving quotation: {str(e)}")
            return False

    async def _create_policy(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Create policy from converted quotation"""
        try:
            # This would integrate with policy management service
            logger.info(f"Creating policy from quotation {quotation_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating policy: {str(e)}")
            return False

    async def _send_confirmation(self, quotation_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Send conversion confirmation to customer"""
        try:
            logger.info(f"Sending confirmation for quotation {quotation_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending confirmation: {str(e)}")
            return False