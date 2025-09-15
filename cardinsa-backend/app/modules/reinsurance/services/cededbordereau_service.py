# NOTE: service for CededBordereau; hold business logic separate from routes
class CededBordereauService:
    def __init__(self, repo):
        self.repo = repo
