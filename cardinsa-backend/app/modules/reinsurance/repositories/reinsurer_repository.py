# NOTE: repository for Reinsurer; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class ReinsurerRepository:
    def __init__(self, db: Session):
        self.db = db
