# NOTE: service for TreatyParticipation; hold business logic separate from routes
class TreatyParticipationService:
    def __init__(self, repo):
        self.repo = repo
