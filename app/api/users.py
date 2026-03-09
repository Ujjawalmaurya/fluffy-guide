from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, admin_required
from app.models.user import User, UserType

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def read_user_me(current_user: User = Depends(get_current_user)):
    # Basic profile info based on type
    profile = {}
    if current_user.user_type == UserType.END_USER:
        profile = {
            "full_name": current_user.end_user_profile.full_name if current_user.end_user_profile else None,
            "career_goals": current_user.end_user_profile.career_goals if current_user.end_user_profile else None
        }
    elif current_user.user_type == UserType.ORGANIZATION:
        profile = {
            "org_name": current_user.org_profile.org_name if current_user.org_profile else None,
            "org_type": current_user.org_profile.org_type if current_user.org_profile else None
        }
    
    return {
        "email": current_user.email,
        "user_type": current_user.user_type,
        "profile": profile
    }

@router.get("/admin/stats", dependencies=[Depends(admin_required)])
def read_admin_stats():
    # Only admins can see this
    return {"message": "Welcome, Officer. Here are the career outcomes stats.", "outcomes": 42}
