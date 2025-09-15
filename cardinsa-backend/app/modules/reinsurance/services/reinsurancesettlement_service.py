# NOTE: service for ReinsuranceSettlement; hold business logic separate from routes
class ReinsuranceSettlementService:
    def __init__(self, repo):
        self.repo = repo
