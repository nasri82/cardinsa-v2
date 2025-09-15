# NOTE: repository for CededBordereau; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class CededBordereauRepository:
    def __init__(self, db: Session):
        self.db = db
