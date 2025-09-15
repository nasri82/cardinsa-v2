from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SkillsTaxonomyCreate(BaseModel):
    name: str
    category: str
    subcategory: str
    proficiency_levels: List[str]
    technology_dependency: str
    obsolescence_risk: str


class SkillsTaxonomyUpdate(SkillsTaxonomyCreate):
    pass


class SkillsTaxonomyOut(SkillsTaxonomyCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime