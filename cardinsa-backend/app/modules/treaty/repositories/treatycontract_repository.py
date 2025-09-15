# NOTE: repository for TreatyContract; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class TreatyContractRepository:
    def __init__(self, db: Session):
        self.db = db
