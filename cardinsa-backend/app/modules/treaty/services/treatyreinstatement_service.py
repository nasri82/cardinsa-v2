# NOTE: service for TreatyReinstatement; hold business logic separate from routes
class TreatyReinstatementService:
    def __init__(self, repo):
        self.repo = repo
