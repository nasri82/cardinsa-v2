# app/modules/pricing/programs/repositories/program_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from app.modules.pricing.programs.models.program_model import Program, ProgramStatus, ProgramType
from app.core.base_repository import BaseRepository


class ProgramRepository(BaseRepository):  # ✅ Fixed: Correct import and no generic parameters
    """Repository for Program operations"""

    def __init__(self, db: Session):
        super().__init__(Program, db)

    def get_by_code(self, program_code: str) -> Optional[Program]:
        """Get program by code"""
        return self.db.query(Program).filter(
            Program.program_code == program_code,
            Program.is_deleted == False
        ).first()

    def get_by_product(self, product_id: UUID, skip: int = 0, limit: int = 100) -> List[Program]:
        """Get programs by product"""
        return self.db.query(Program).filter(
            Program.product_id == product_id,
            Program.is_deleted == False
        ).offset(skip).limit(limit).all()

    def get_by_status(self, status: ProgramStatus, skip: int = 0, limit: int = 100) -> List[Program]:
        """Get programs by status"""
        return self.db.query(Program).filter(
            Program.status == status.value,
            Program.is_deleted == False
        ).offset(skip).limit(limit).all()

    def get_active_programs(self, skip: int = 0, limit: int = 100) -> List[Program]:
        """Get all active programs"""
        return self.db.query(Program).filter(
            Program.is_active == True,
            Program.is_deleted == False
        ).offset(skip).limit(limit).all()

    def get_by_partner(self, partner_org: str, skip: int = 0, limit: int = 100) -> List[Program]:
        """Get programs by partner organization"""
        return self.db.query(Program).filter(
            Program.partner_organization.ilike(f'%{partner_org}%'),
            Program.is_deleted == False
        ).offset(skip).limit(limit).all()

    def get_statistics(self) -> dict:
        """Get program statistics"""
        total = self.db.query(func.count(Program.id)).filter(
            Program.is_deleted == False
        ).scalar() or 0

        active = self.db.query(func.count(Program.id)).filter(
            Program.is_active == True,
            Program.is_deleted == False
        ).scalar() or 0

        by_type = {}
        for prog_type in ProgramType:
            count = self.db.query(func.count(Program.id)).filter(
                Program.program_type == prog_type.value,
                Program.is_deleted == False
            ).scalar() or 0
            by_type[prog_type.value] = count

        by_status = {}
        for status in ProgramStatus:
            count = self.db.query(func.count(Program.id)).filter(
                Program.status == status.value,
                Program.is_deleted == False
            ).scalar() or 0
            by_status[status.value] = count

        total_enrollment = self.db.query(func.sum(Program.current_enrollment)).filter(
            Program.is_deleted == False
        ).scalar() or 0

        return {
            'total_programs': total,
            'active_programs': active,
            'by_type': by_type,
            'by_status': by_status,
            'total_enrollment': int(total_enrollment)
        }
