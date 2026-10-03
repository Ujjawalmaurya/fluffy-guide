from app.modules.analytics.repository import AnalyticsRepository

class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    def get_overview(self, city: str | None = None):
        return self.repository.get_overview(city)

    def get_district_funnel(self, city=None):
        return self.repository.get_district_funnel(city)

    def get_skill_gaps(self, limit=10, city: str | None = None):
        return self.repository.get_skill_gaps(limit, city)

    def get_training_outcomes(self, city: str | None = None):
        # Additional formatting or filtering logic can go here
        return self.repository.get_training_outcomes(city)
