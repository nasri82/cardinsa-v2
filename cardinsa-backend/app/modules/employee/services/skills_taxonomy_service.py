from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.employee.schemas import skills_taxonomy_schema


class SkillsTaxonomyService:

    @staticmethod
    def get_all(db: Session):
        # Replace with actual query
        return []

    @staticmethod
    def create(db: Session, payload: skills_taxonomy_schema.SkillsTaxonomyCreate):
        # Replace with actual DB insert
        return payload

    @staticmethod
    def update(db: Session, item_id: UUID, payload: skills_taxonomy_schema.SkillsTaxonomyUpdate):
        # Replace with actual DB update
        return payload

    @staticmethod
    def delete(db: Session, item_id: UUID):
        # Replace with actual DB delete
        return {"deleted": item_id}