# NOTE: service for TaxRule; hold business logic separate from routes
class TaxRuleService:
    def __init__(self, repo):
        self.repo = repo
