# NOTE: repository for GLPeriod; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class GLPeriodRepository:
    def __init__(self, db: Session):
        self.db = db
