# NOTE: service for Reinsurer; hold business logic separate from routes
class ReinsurerService:
    def __init__(self, repo):
        self.repo = repo
