# NOTE: service for GLJournal; hold business logic separate from routes
class GLJournalService:
    def __init__(self, repo):
        self.repo = repo
