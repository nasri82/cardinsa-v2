# NOTE: repository for TreatyReinstatement; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class TreatyReinstatementRepository:
    def __init__(self, db: Session):
        self.db = db
