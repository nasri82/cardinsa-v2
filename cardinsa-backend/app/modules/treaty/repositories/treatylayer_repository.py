# NOTE: repository for TreatyLayer; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class TreatyLayerRepository:
    def __init__(self, db: Session):
        self.db = db
