import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
if not supabase_url or not supabase_key:
    print("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

personas = [
    {"email": "ramesh@sankalp.local", "password": "DemoSankalp2025!", "name": "Ramesh Verma"},
    {"email": "priya@sankalp.local", "password": "DemoSankalp2025!", "name": "Priya Sharma"},
    {"email": "officer@sankalp.local", "password": "DemoSankalp2025!", "name": "Ravi Officer"},
]

uuids = {}

for p in personas:
    # try to sign up or create
    email = p["email"]
    pwd = p["password"]
    try:
        # Use admin api
        res = supabase.auth.admin.create_user({
            "email": email,
            "password": pwd,
            "email_confirm": True,
            "user_metadata": {"full_name": p["name"]}
        })
        user = res.user
        uuids[email] = user.id
        print(f"Created {email} with UUID {user.id}")
    except Exception as e:
        # User might already exist, try to get them
        print(f"Error creating {email}: {e}")
        try:
            # We can list users and find them
            users_res = supabase.auth.admin.list_users()
            for u in users_res:
                if u.email == email:
                    uuids[email] = u.id
                    print(f"Found existing {email} with UUID {u.id}")
        except Exception as e2:
            print(f"Failed to find {email}: {e2}")

# Now inject UUIDs into seed script and print it
with open("scripts/seed_demo_personas.sql", "r") as f:
    sql = f.read()

if "ramesh@sankalp.local" in uuids:
    sql = sql.replace("daa14278-f26b-4404-95cc-5eb169925fed", uuids["ramesh@sankalp.local"])
if "priya@sankalp.local" in uuids:
    sql = sql.replace("cea951a5-b448-4dc4-8c37-b83d1d5b689b", uuids["priya@sankalp.local"])
if "officer@sankalp.local" in uuids:
    sql = sql.replace("52001edf-a140-4d78-9e33-4705ffeed9e8", uuids["officer@sankalp.local"])

with open("scripts/seed_demo_personas_injected.sql", "w") as f:
    f.write(sql)
print("Saved injected SQL to scripts/seed_demo_personas_injected.sql")
