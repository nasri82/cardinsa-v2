# NOTE: repository for TaxRule; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class TaxRuleRepository:
    def __init__(self, db: Session):
        self.db = db
