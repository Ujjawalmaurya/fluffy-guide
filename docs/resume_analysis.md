# Resume Analysis Module

This module provides an enhanced resume analysis pipeline for SkillBridge AI. It uses Gemini 1.5 Flash for deep data extraction and Groq (Llama 3) for real-time bullet point improvements.

## Endpoints

### `POST /api/v1/resume/analyze`
- **Description**: Main analysis orchestrator. Accepts a PDF file and an optional target role.
- **Input**: `multipart/form-data` with `file` (PDF) and optional `target_role` (text).
- **Process**:
  1. Extracts raw text using `pdfplumber`.
  2. Parses text into JSON using Gemini 1.5 Flash.
  3. Calculates scores for ATS compatibility, quantification, completeness, and readability.
  4. Generates a professional summary and improves top empty/weak bullets.
  5. Persists the result to the Supabase `resume_analysis` table.
- **Output**: Full `ResumeAnalysisResult` JSON.

### `GET /api/v1/resume/analysis`
- **Description**: Fetches the latest resume analysis for the authenticated user.
- **Output**: `ResumeAnalysisResult` JSON.

### `GET /api/v1/resume/score-breakdown`
- **Description**: Lightweight endpoint for dashboard widgets.
- **Output**: `{quality_scores, overall_score, india_flags}`.

### `POST /api/v1/resume/improve-bullet`
- **Description**: Point-endpoint for improving a single resume bullet.
- **Input**: Form data with `bullet` and optional `target_role`.
- **Rate Limit**: 10 calls per user per day.
- **Output**: `{original, improved, reason}`.

## Scoring Algorithm

The `overall_score` is a weighted average of four primary dimensions:

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| **ATS Compatibility** | 25% | Penalizes photos, sensitive info (caste/religion), missing contact info, and complex layouts. |
| **Quantification** | 30% | Percentage of experience bullets that include numbers, metrics, or percentages. |
| **Completeness** | 20% | Checks presence of summary, skills, experience, education, certs, contact, and LinkedIn. |
| **Readability** | 25% | Penalizes long sentences (>25 words) and intensive use of passive voice phrases. |

*Note: If a `target_role` is provided, a "Keyword Relevance" score (15%) is blended in, reducing the weights of others proportionally.*

## Transferable Skills Mapping

The system automatically detects context from your resume and suggests "transferable skills":
- "route planning" → "logistics coordination"
- "cash handling" → "financial accountability"
- "customer dealing" → "client relationship management"
- "machine operation" → "technical equipment proficiency"
- "team supervision" → "team leadership"

## Technical Stack
- **AI**: Gemini 1.5 Flash (Extraction/Summary), Groq Llama 3 (Bullet Refinement).
- **Backend**: FastAPI, Pydantic v2.
- **DB**: Supabase (PostgreSQL).
- **PDF**: pdfplumber.
