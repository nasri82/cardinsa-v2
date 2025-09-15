# NOTE: repository for Cession; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class CessionRepository:
    def __init__(self, db: Session):
        self.db = db
