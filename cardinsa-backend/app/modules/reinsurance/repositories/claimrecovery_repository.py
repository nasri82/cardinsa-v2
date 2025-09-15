# NOTE: repository for ClaimRecovery; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class ClaimRecoveryRepository:
    def __init__(self, db: Session):
        self.db = db
