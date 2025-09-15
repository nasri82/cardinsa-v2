from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.skills_demand_forecast_service import SkillsDemandForecastService
from app.modules.employee.schemas.skills_demand_forecast_schema import SkillsDemandForecastCreate, SkillsDemandForecastUpdate, SkillsDemandForecastOut

router = APIRouter()

@router.get("/", response_model=List[SkillsDemandForecastOut], dependencies=[Depends(require_permission_scoped("skillsdemandforecast", "read"))])
def list_items(db: Session = Depends(get_db)):
    return SkillsDemandForecastService.get_all(db)

@router.post("/", response_model=SkillsDemandForecastOut, dependencies=[Depends(require_permission_scoped("skillsdemandforecast", "create"))])
def create_item(payload: SkillsDemandForecastCreate, db: Session = Depends(get_db)):
    return SkillsDemandForecastService.create(db, payload)

@router.put("/{forecast_id}", response_model=SkillsDemandForecastOut, dependencies=[Depends(require_permission_scoped("skillsdemandforecast", "update"))])
def update_item(forecast_id: str, payload: SkillsDemandForecastUpdate, db: Session = Depends(get_db)):
    return SkillsDemandForecastService.update(db, forecast_id, payload)

@router.delete("/{forecast_id}", dependencies=[Depends(require_permission_scoped("skillsdemandforecast", "delete"))])
def delete_item(forecast_id: str, db: Session = Depends(get_db)):
    return SkillsDemandForecastService.delete(db, forecast_id)