import os
from supabase import create_client, Client

url = "https://kicfuxaaspcxbkcyiznr.supabase.co"
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not key:
    print("Error: SUPABASE_SERVICE_ROLE_KEY not set")
    exit(1)

supabase: Client = create_client(url, key)

# 1. Delete my duplicates (the ones I created with 4c0b1735... etc)
# Actually, it's easier to just find the users with the target email and delete them if they don't match the IDs we want.
target_emails = ['ramesh@sankalp.ai', 'priya@sankalp.ai', 'officer@sankalp.ai']
old_emails = ['demo.ramesh@sankalp.ai', 'demo.priya@sankalp.ai', 'demo.officer@sankalp.ai']

# IDs we want to KEEP (from seed_demo_personas.sql)
keep_ids = {
    'ramesh@sankalp.ai': 'daa14278-f26b-4404-95cc-5eb169925fed',
    'priya@sankalp.ai': 'cea951a5-b448-4dc4-8c37-b83d1d5b689b',
    'officer@sankalp.ai': '52001edf-a140-4d78-9e33-4705ffeed9e8'
}

print("Cleaning up target accounts...")
for email in target_emails:
    res = supabase.auth.admin.list_users()
    users = res.users
    for u in users:
        if u.email == email and u.id != keep_ids[email]:
            print(f"Deleting duplicate/wrong-id user: {email} ({u.id})")
            supabase.auth.admin.delete_user(u.id)

print("Updating existing demo accounts to target emails and password...")
# Use the old emails to find and update
for i, old_email in enumerate(old_emails):
    target_email = target_emails[i]
    res = supabase.auth.admin.list_users()
    users = res.users
    user_to_update = next((u for u in users if u.email == old_email), None)
    
    if user_to_update:
        print(f"Updating {old_email} -> {target_email}")
        supabase.auth.admin.update_user_by_id(
            user_to_update.id,
            {
                "email": target_email,
                "password": "DemoSankalp2025!",
                "user_metadata": {"full_name": user_to_update.user_metadata.get("full_name")},
                "email_confirm": True
            }
        )
    else:
        # If not found by old email, check if it's already target email but needs password reset
        user_already_there = next((u for u in users if u.email == target_email), None)
        if user_already_there:
            print(f"Resetting password for {target_email}")
            supabase.auth.admin.update_user_by_id(
                user_already_there.id,
                {"password": "DemoSankalp2025!", "email_confirm": True}
            )

print("Final verification...")
res = supabase.auth.admin.list_users()
for u in res.users:
    if u.email in target_emails:
        print(f"User: {u.email}, ID: {u.id}, Confirmed: {u.email_confirmed_at}")
