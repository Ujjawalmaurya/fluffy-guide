# Database Schema

## ER Diagram (ASCII)

```
users ──────────────────────────────────────────────────────
  │
  ├─ otp_store            (email only, no FK — by design)
  │
  ├─ user_profiles        (user_id → users.id)
  ├─ user_preferences     (user_id → users.id)
  ├─ onboarding_state     (user_id → users.id)
  ├─ questionnaire_sessions (user_id → users.id)
  ├─ profile_enrichments  (user_id → users.id)
  ├─ chat_messages        (user_id → users.id)
  │
  └─ [jobs are standalone — no user FK]
     job_listings
```

## Tables

### users
| Column | Type | Description |
|---|---|---|
| id | UUID PK | User identifier |
| email | TEXT UNIQUE | Login identifier |
| user_type | TEXT | One of 6 user type strings |
| preferred_lang | TEXT | 'en' or 'hi' |
| is_active | BOOLEAN | Soft disable flag |
| onboarding_done | BOOLEAN | Flipped after Step 5 |

### otp_store
| Column | Type | Description |
|---|---|---|
| otp_code | TEXT | 6-digit code |
| expires_at | TIMESTAMPTZ | 10 min from creation |
| is_used | BOOLEAN | Marked true after verify |

### questionnaire_sessions
JSONB fields:
- `questions_data`: `[{id, question, type, options}]`
- `answers_data`: `[{question_id, question_text, answer}]`

### profile_enrichments
JSONB field:
- `resume_parsed`: `{skills: [], education: [], experience: []}`

### job_listings
- `required_skills`: TEXT[] — used for matching
- `is_active`: BOOLEAN — soft delete, false = hidden from public API

### onboarding_state
- `completed_steps`: INTEGER[] — e.g. `{1,2,3}`
- `step_data`: JSONB — temporary in-progress step data
