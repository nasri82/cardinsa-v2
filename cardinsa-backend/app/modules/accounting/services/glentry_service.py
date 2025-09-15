# NOTE: service for GLEntry; hold business logic separate from routes
class GLEntryService:
    def __init__(self, repo):
        self.repo = repo
