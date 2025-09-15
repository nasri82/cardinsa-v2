# NOTE: service for TreatyProgram; hold business logic separate from routes
class TreatyProgramService:
    def __init__(self, repo):
        self.repo = repo
