# NOTE: service for TreatyLayer; hold business logic separate from routes
class TreatyLayerService:
    def __init__(self, repo):
        self.repo = repo
