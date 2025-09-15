from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.skills_taxonomy_service import SkillsTaxonomyService
from app.modules.employee.schemas.skills_taxonomy_schema import SkillsTaxonomyCreate, SkillsTaxonomyUpdate, SkillsTaxonomyOut

router = APIRouter()

@router.get("/", response_model=List[SkillsTaxonomyOut], dependencies=[Depends(require_permission_scoped("skillstaxonomy", "read"))])
def list_items(db: Session = Depends(get_db)):
    return SkillsTaxonomyService.get_all(db)

@router.post("/", response_model=SkillsTaxonomyOut, dependencies=[Depends(require_permission_scoped("skillstaxonomy", "create"))])
def create_item(payload: SkillsTaxonomyCreate, db: Session = Depends(get_db)):
    return SkillsTaxonomyService.create(db, payload)

@router.put("/{taxonomy_id}", response_model=SkillsTaxonomyOut, dependencies=[Depends(require_permission_scoped("skillstaxonomy", "update"))])
def update_item(taxonomy_id: str, payload: SkillsTaxonomyUpdate, db: Session = Depends(get_db)):
    return SkillsTaxonomyService.update(db, taxonomy_id, payload)

@router.delete("/{taxonomy_id}", dependencies=[Depends(require_permission_scoped("skillstaxonomy", "delete"))])
def delete_item(taxonomy_id: str, db: Session = Depends(get_db)):
    return SkillsTaxonomyService.delete(db, taxonomy_id)