# NOTE: repository for GLAccount; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class GLAccountRepository:
    def __init__(self, db: Session):
        self.db = db
