# NOTE: repository for TreatyProgram; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class TreatyProgramRepository:
    def __init__(self, db: Session):
        self.db = db
