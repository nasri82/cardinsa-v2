from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.skills_gap_analysis_service import SkillsGapAnalysisService
from app.modules.employee.schemas.skills_gap_analysis_schema import SkillsGapAnalysisCreate, SkillsGapAnalysisUpdate, SkillsGapAnalysisOut

router = APIRouter()

@router.get("/", response_model=List[SkillsGapAnalysisOut], dependencies=[Depends(require_permission_scoped("skillsgapanalysis", "read"))])
def list_items(db: Session = Depends(get_db)):
    return SkillsGapAnalysisService.get_all(db)

@router.post("/", response_model=SkillsGapAnalysisOut, dependencies=[Depends(require_permission_scoped("skillsgapanalysis", "create"))])
def create_item(payload: SkillsGapAnalysisCreate, db: Session = Depends(get_db)):
    return SkillsGapAnalysisService.create(db, payload)

@router.put("/{gap_id}", response_model=SkillsGapAnalysisOut, dependencies=[Depends(require_permission_scoped("skillsgapanalysis", "update"))])
def update_item(gap_id: str, payload: SkillsGapAnalysisUpdate, db: Session = Depends(get_db)):
    return SkillsGapAnalysisService.update(db, gap_id, payload)

@router.delete("/{gap_id}", dependencies=[Depends(require_permission_scoped("skillsgapanalysis", "delete"))])
def delete_item(gap_id: str, db: Session = Depends(get_db)):
    return SkillsGapAnalysisService.delete(db, gap_id)