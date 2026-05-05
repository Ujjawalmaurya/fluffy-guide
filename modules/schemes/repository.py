from typing import List

class SchemeRepository:
    def __init__(self, client):
        self.client = client

    async def get_all_schemes(self) -> List[dict]:
        """Fetch all government schemes from DB."""
        return []

    async def get_user_profile(self, user_id: str) -> dict:
        """Fetch user demographic data for eligibility check."""
        return {}
