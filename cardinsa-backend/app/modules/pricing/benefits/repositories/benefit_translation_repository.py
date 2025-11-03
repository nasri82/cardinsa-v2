
"""
app/modules/benefits/repositories/benefit_translation_repository.py

Repository for managing benefit translations and multi-language support.
Handles localization for different languages and regions.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.modules.pricing.benefits.models.benefit_translation_model import BenefitTranslation
from app.core.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class BenefitTranslationRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing benefit translations"""
    
    def __init__(self, db: Session):
        super().__init__(BenefitTranslation, db)
    
    async def get_by_entity(self, entity_type: str, entity_id: str) -> List[BenefitTranslation]:
        """Get all translations for an entity"""
        try:
            return self.db.query(BenefitTranslation).filter(
                and_(
                    BenefitTranslation.entity_type == entity_type,
                    BenefitTranslation.entity_id == entity_id,
                    BenefitTranslation.is_active == True
                )
            ).order_by(BenefitTranslation.language_code).all()
        except Exception as e:
            logger.error(f"Error fetching translations by entity: {str(e)}")
            raise
    
    async def get_by_language(self, language_code: str) -> List[BenefitTranslation]:
        """Get all translations for a specific language"""
        try:
            return self.db.query(BenefitTranslation).filter(
                and_(
                    BenefitTranslation.language_code == language_code,
                    BenefitTranslation.is_active == True
                )
            ).order_by(BenefitTranslation.entity_type, BenefitTranslation.entity_id).all()
        except Exception as e:
            logger.error(f"Error fetching translations by language: {str(e)}")
            raise
    
    async def get_translation(self, entity_type: str, entity_id: str, 
                           language_code: str) -> Optional[BenefitTranslation]:
        """Get specific translation"""
        try:
            return self.db.query(BenefitTranslation).filter(
                and_(
                    BenefitTranslation.entity_type == entity_type,
                    BenefitTranslation.entity_id == entity_id,
                    BenefitTranslation.language_code == language_code,
                    BenefitTranslation.is_active == True
                )
            ).first()
        except Exception as e:
            logger.error(f"Error fetching specific translation: {str(e)}")
            raise
    
    async def get_missing_translations(self, language_code: str) -> List[Dict[str, str]]:
        """Get entities missing translations for a language"""
        try:
            # This would typically involve complex queries to find entities
            # without translations. Simplified version here.
            existing_translations = await self.get_by_language(language_code)
            existing_entities = {(t.entity_type, t.entity_id) for t in existing_translations}
            
            # Would need to query all entities and compare
            # Implementation depends on specific requirements
            return []
        except Exception as e:
            logger.error(f"Error fetching missing translations: {str(e)}")
            raise
    
    async def get_available_languages(self) -> List[str]:
        """Get all available language codes"""
        try:
            result = self.db.query(BenefitTranslation.language_code).filter(
                BenefitTranslation.is_active == True
            ).distinct().all()
            
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error fetching available languages: {str(e)}")
            raise
