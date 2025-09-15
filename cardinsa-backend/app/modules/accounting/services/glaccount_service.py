# NOTE: service for GLAccount; hold business logic separate from routes
class GLAccountService:
    def __init__(self, repo):
        self.repo = repo
