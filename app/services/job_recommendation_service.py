import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logger import logger
from app.core.database import get_supabase
from app.core.ai_models import get_embedding_model
from app.services.career_identity_service import CareerIdentityService

class JobRecommendationService:
    """
    Handles job recommendations using vector similarity and 
    hybrid matching strategies.
    """

    @staticmethod
    async def get_recommendations(
        user_id: str, 
        limit: int = 5,
        match_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Fetches top job recommendations for a user based on their career identity.
        """
        supabase = get_supabase()
        
        # 1. Get user profile (including embedding)
        profile_res = supabase.table("user_profiles").select("identity_embedding, state").eq("user_id", user_id).single().execute()
        
        if not profile_res.data:
            logger.warning(f"No profile found for user {user_id}")
            return []
            
        profile = profile_res.data
        embedding = profile.get("identity_embedding")
        user_state = profile.get("state")

        # 2. If no embedding, generate it now (lazy generation)
        if not embedding:
            logger.info(f"Identity embedding missing for {user_id}, generating...")
            career_service = CareerIdentityService()
            # This will generate identity text and embedding
            await career_service.generate_and_store_identity(user_id)
            
            # Re-fetch profile
            profile_res = supabase.table("user_profiles").select("identity_embedding").eq("user_id", user_id).single().execute()
            embedding = profile_res.data.get("identity_embedding") if profile_res.data else None

        if not embedding:
            logger.error(f"Failed to obtain embedding for user {user_id}")
            return []

        # 3. Call RPC function for vector similarity matching
        try:
            # We filter by state if possible, or leave it to RPC if null
            recommendations = supabase.rpc("match_jobs", {
                "query_embedding": embedding,
                "match_threshold": match_threshold,
                "match_count": limit,
                "filter_state": user_state
            }).execute()

            if not recommendations.data:
                logger.info(f"No vector matches found for user {user_id}")
                # Fallback to category-based matching if vector search yields nothing
                return await JobRecommendationService._fallback_recommendations(user_id, limit)

            return recommendations.data

        except Exception as e:
            logger.error(f"Error during vector matching: {str(e)}")
            return await JobRecommendationService._fallback_recommendations(user_id, limit)

    @staticmethod
    async def _fallback_recommendations(user_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Simple keyword/category fallback when vector search fails or has no matches.
        """
        supabase = get_supabase()
        
        # Get user preferences
        prefs_res = supabase.table("user_preferences").select("career_interests").eq("user_id", user_id).single().execute()
        if not prefs_res.data or not prefs_res.data.get("career_interests"):
            # absolute fallback: just latest jobs
            jobs = supabase.table("job_listings").select("*").eq("is_active", True).order("created_at", desc=True).limit(limit).execute()
            return jobs.data

        interests = prefs_res.data.get("career_interests")
        
        # Filter jobs by categories/interests
        jobs = supabase.table("job_listings") \
            .select("*") \
            .eq("is_active", True) \
            .in_("category", interests) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
            
        return jobs.data

    @staticmethod
    async def embed_all_jobs():
        """
        Utility task to embed all existing jobs that don't have embeddings.
        Should be run periodically or manually after scraping.
        """
        supabase = get_supabase()
        model = get_embedding_model()
        
        # Get jobs without embeddings
        jobs_res = supabase.table("job_listings").select("id, title, description, category").is_("job_embedding", "null").execute()
        
        if not jobs_res.data:
            logger.info("All jobs are already embedded.")
            return

        logger.info(f"Embedding {len(jobs_res.data)} jobs...")
        
        for job in jobs_res.data:
            text_to_embed = f"{job['title']}. {job['category']}. {job['description']}"
            embedding = model.encode(text_to_embed).tolist()
            
            supabase.table("job_listings").update({"job_embedding": embedding}).eq("id", job["id"]).execute()
            
        logger.info("Job embedding complete.")
