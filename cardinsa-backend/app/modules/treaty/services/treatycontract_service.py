# NOTE: service for TreatyContract; hold business logic separate from routes
class TreatyContractService:
    def __init__(self, repo):
        self.repo = repo
