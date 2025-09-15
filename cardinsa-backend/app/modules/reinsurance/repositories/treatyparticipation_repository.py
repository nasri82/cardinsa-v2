# NOTE: repository for TreatyParticipation; implement queries aligned with your SQL schema
from sqlalchemy.orm import Session

class TreatyParticipationRepository:
    def __init__(self, db: Session):
        self.db = db
