# NOTE: service for Cession; hold business logic separate from routes
class CessionService:
    def __init__(self, repo):
        self.repo = repo
