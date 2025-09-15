# NOTE: service for ClaimRecovery; hold business logic separate from routes
class ClaimRecoveryService:
    def __init__(self, repo):
        self.repo = repo
