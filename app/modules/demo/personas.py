"""
personas.py — Pre-seeded demo user profiles for judging and evaluation.
"""
from typing import Dict, Any

PERSONA_MAP: Dict[str, Dict[str, Any]] = {
    "ravi": {
        "id": "daa14278-f26b-4404-95cc-5eb169925fed",
        "email": "ravi@demo.sankalp.gov.in",
        "name": "Ravi Kumar",
        "type": "rural_tech",
    },
    "meera": {
        "id": "cea951a5-b448-4dc4-8c37-b83d1d5b689b",
        "email": "meera@demo.sankalp.gov.in",
        "name": "Meera Devi",
        "type": "shg_leader",
    },
    "arjun": {
        "id": "52001edf-a140-4d78-9e33-4705ffeed9e8",
        "email": "arjun@demo.sankalp.gov.in",
        "name": "Arjun Subramanian",
        "type": "msme_owner",
    },
    "admin": {
        "id": "63112fdf-b251-5e89-1e44-5816ffeea1b9",
        "email": "admin@sankalp.gov.in",
        "name": "System Admin",
        "type": "admin",
    },
}
