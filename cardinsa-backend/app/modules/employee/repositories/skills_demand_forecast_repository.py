from sqlalchemy.orm import Session
from uuid import UUID
from app.models import skills_demand_forecast_model
from app.schemas import skills_demand_forecast_schema


class SkillsDemandForecastRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(skills_demand_forecast_model.SkillsDemandForecast).all()

    @staticmethod
    def create(db: Session, payload: skills_demand_forecast_schema.SkillsDemandForecastCreate):
        db_obj = skills_demand_forecast_model.SkillsDemandForecast(**payload.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, item_id: UUID, payload: skills_demand_forecast_schema.SkillsDemandForecastUpdate):
        db_obj = db.query(skills_demand_forecast_model.SkillsDemandForecast).filter(skills_demand_forecast_model.SkillsDemandForecast.id == item_id).first()
        if db_obj:
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, item_id: UUID):
        db_obj = db.query(skills_demand_forecast_model.SkillsDemandForecast).filter(skills_demand_forecast_model.SkillsDemandForecast.id == item_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj