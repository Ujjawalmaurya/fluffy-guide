# API Reference

All responses follow the format: `{success, data, message, error_code}`

## Auth

### POST /auth/request-otp
Request an OTP (check server terminal for the code).
```json
// Body
{ "email": "user@example.com" }
// Response
{ "success": true, "message": "OTP generated (check server logs)" }
```

### POST /auth/verify-otp
Verify OTP, get JWT tokens.
```json
// Body
{ "email": "user@example.com", "otp": "482913" }
// Response
{ "success": true, "data": { "access_token": "...", "refresh_token": "...", "user": {...} } }
```

### POST /auth/refresh
Get new token pair using refresh_token.
```json
{ "refresh_token": "..." }
```

### GET /auth/me *(requires Bearer token)*
Returns current user.

---

## Onboarding *(all require Bearer token)*

### POST /onboarding/user-type
```json
{ "user_type": "individual_youth" }
```

### POST /onboarding/profile
```json
{ "full_name": "Amit", "age": 24, "gender": "male", "state": "Uttar Pradesh", "city": "Lucknow", "education_level": "graduate", "languages": ["Hindi","English"] }
```

### POST /onboarding/preferences
```json
{ "career_interests": ["technology","logistics"], "expected_salary_min": 25000, "work_type": "any", "willing_to_relocate": false, "target_roles": ["developer"] }
```

### POST /onboarding/generate-questions
```json
{ "language": "en" }
// Response: { questions: [{id, question, type, options}] }
```

### POST /onboarding/submit-answers
```json
{ "answers": [{"question_id": "q1", "question_text": "...", "answer": "..."}] }
// Response: { session_id: "uuid" }
```

### GET /onboarding/process-stream?session_id=xxx
SSE stream — 6 events with {step, progress, message, status}.

### GET /onboarding/state
Returns current onboarding step progress.

---

## Profile *(requires Bearer token)*

### GET /profile/me
### PATCH /profile/me
```json
{ "full_name": "...", "phone": "...", "city": "..." }
```
### POST /profile/resume
Multipart form-data, field: `resume` (PDF, max 5MB).

### GET /profile/completion-score

---

## Dashboard *(requires Bearer token)*

### GET /dashboard/summary
Returns full dashboard data: user info, completion %, skills, job matches.

---

## Jobs

### GET /jobs/?state=&category=&job_type=&page=1&limit=20
### GET /jobs/{id}

### Admin (requires X-Admin-Secret header)
- POST /jobs/admin/create
- PATCH /jobs/admin/{id}
- DELETE /jobs/admin/{id}
- POST /jobs/admin/bulk — array of job objects

---

## Chat *(requires Bearer token)*

### POST /chat/message
SSE streaming response.
```json
{ "content": "What skills should I learn?", "language": "en" }
```

### GET /chat/history
### DELETE /chat/history
