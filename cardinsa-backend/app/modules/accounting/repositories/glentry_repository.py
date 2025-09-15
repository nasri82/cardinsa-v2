# NOTE: repository for GLEntry; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class GLEntryRepository:
    def __init__(self, db: Session):
        self.db = db
