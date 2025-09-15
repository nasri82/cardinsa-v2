# NOTE: service for GLPeriod; hold business logic separate from routes
class GLPeriodService:
    def __init__(self, repo):
        self.repo = repo
