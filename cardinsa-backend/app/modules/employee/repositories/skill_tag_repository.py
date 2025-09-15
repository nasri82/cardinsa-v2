from sqlalchemy.orm import Session
from uuid import UUID
from app.models import skill_tag_model
from app.schemas import skill_tag_schema


class SkillTagRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(skill_tag_model.SkillTag).all()

    @staticmethod
    def create(db: Session, payload: skill_tag_schema.SkillTagCreate):
        db_obj = skill_tag_model.SkillTag(**payload.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, item_id: UUID, payload: skill_tag_schema.SkillTagUpdate):
        db_obj = db.query(skill_tag_model.SkillTag).filter(skill_tag_model.SkillTag.id == item_id).first()
        if db_obj:
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, item_id: UUID):
        db_obj = db.query(skill_tag_model.SkillTag).filter(skill_tag_model.SkillTag.id == item_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj