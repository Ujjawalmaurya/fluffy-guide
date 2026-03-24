import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env vars from .env if present
load_dotenv()

url = "https://kicfuxaaspcxbkcyiznr.supabase.co"
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not key:
    print("Error: SUPABASE_SERVICE_KEY not set")
    sys.exit(1)

supabase: Client = create_client(url, key)

PERSONAS = [
    {
        "id": "daa14278-f26b-4404-95cc-5eb169925fed",
        "email": "ravi@demo.sankalp.gov.in",
        "password": "DemoSankalp2025!",
        "full_name": "Ravi Kumar"
    },
    {
        "id": "cea951a5-b448-4dc4-8c37-b83d1d5b689b",
        "email": "meera@demo.sankalp.gov.in",
        "password": "DemoSankalp2025!",
        "full_name": "Meera Devi"
    },
    {
        "id": "52001edf-a140-4d78-9e33-4705ffeed9e8",
        "email": "arjun@demo.sankalp.gov.in",
        "password": "DemoSankalp2025!",
        "full_name": "Arjun Subramanian"
    },
    {
        "id": "63112fdf-b251-5e89-1e44-5816ffeea1b9",
        "email": "admin@sankalp.gov.in",
        "password": "DemoSankalp2025!",
        "full_name": "System Admin"
    }
]

def seed_auth():
    print("--- Seeding Demo Personas into Supabase Auth ---")
    
    # 1. List existing users
    res = supabase.auth.admin.list_users()
    # In some versions it's for 'res.users', in others it's just 'res'
    existing_users = getattr(res, 'users', res)
    existing_emails = {u.email for u in existing_users}
    existing_ids = {u.id for u in existing_users}
    
    for p in PERSONAS:
        if p["id"] in existing_ids:
            print(f"User {p['email']} already exists with ID {p['id']}. Updating...")
            supabase.auth.admin.update_user_by_id(
                p["id"],
                {
                    "email": p["email"],
                    "password": p["password"],
                    "user_metadata": {"full_name": p["full_name"]},
                    "email_confirm": True
                }
            )
        elif p["email"] in existing_emails:
            # User exists but with different ID - delete and recreate for consistency
            u_to_del = next(u for u in existing_users if u.email == p["email"])
            print(f"User {p['email']} exists with WRONG ID {u_to_del.id}. Deleting and recreating...")
            supabase.auth.admin.delete_user(u_to_del.id)
            supabase.auth.admin.create_user({
                "id": p["id"],
                "email": p["email"],
                "password": p["password"],
                "user_metadata": {"full_name": p["full_name"]},
                "email_confirm": True
            })
        else:
            print(f"Creating new user: {p['email']} with ID {p['id']}")
            supabase.auth.admin.create_user({
                "id": p["id"],
                "email": p["email"],
                "password": p["password"],
                "user_metadata": {"full_name": p["full_name"]},
                "email_confirm": True
            })

    print("--- Seeding Complete ---")

if __name__ == "__main__":
    seed_auth()
