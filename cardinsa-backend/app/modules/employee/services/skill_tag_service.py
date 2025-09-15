from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.employee.schemas import skill_tag_schema


class SkillTagService:

    @staticmethod
    def get_all(db: Session):
        # Replace with actual query
        return []

    @staticmethod
    def create(db: Session, payload: skill_tag_schema.SkillTagCreate):
        # Replace with actual DB insert
        return payload

    @staticmethod
    def update(db: Session, item_id: UUID, payload: skill_tag_schema.SkillTagUpdate):
        # Replace with actual DB update
        return payload

    @staticmethod
    def delete(db: Session, item_id: UUID):
        # Replace with actual DB delete
        return {"deleted": item_id}