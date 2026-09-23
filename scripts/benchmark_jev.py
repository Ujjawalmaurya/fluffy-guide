import asyncio
import time
import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_extractor import extract_resume_bundle
from app.modules.ai_chat.providers.jev_provider import JevProvider

async def benchmark_pdf_extraction(pdf_path: str) -> dict:
    """Benchmark PDF extraction latency and character volume."""
    if not os.path.exists(pdf_path):
        return {"error": "PDF not found"}

    with open(pdf_path, "rb") as f:
        content = f.read()

    times = []
    bundle = None
    for _ in range(5):
        t0 = time.perf_counter()
        bundle = extract_resume_bundle(content)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    avg_ms = sum(times) / len(times)
    min_ms = min(times)

    return {
        "file_size_kb": len(content) // 1024,
        "page_count": bundle.get("page_count", 0),
        "total_chars": len(bundle.get("text", "")),
        "avg_latency_ms": round(avg_ms, 2),
        "min_latency_ms": round(min_ms, 2),
        "links_detected": len(bundle.get("links", [])),
        "sections_detected": len(bundle.get("sections", {}))
    }

async def benchmark_chat_triage(jev: JevProvider) -> dict:
    """Benchmark chat guardrail triage latency."""
    messages = [
        "Can you recommend me top 3 government schemes for youth in Uttar Pradesh?",
        "Hello there, good morning!",
        "I need a high paying job in logistics with minimal education",
        "How can I prepare for an electrician trade certification test?",
        "What is the average salary of a CNC machine operator?"
    ]

    times = []
    for msg in messages:
        t0 = time.perf_counter()
        res = await jev.check_chat_guardrails(msg)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    return {
        "samples_count": len(messages),
        "avg_latency_ms": round(sum(times) / len(times), 2),
        "min_latency_ms": round(min(times), 2),
        "max_latency_ms": round(max(times), 2)
    }

async def benchmark_job_matching(jev: JevProvider) -> dict:
    """Benchmark batch job match scoring latency."""
    profile = {
        "primary_role": "Python Backend Engineer",
        "skills": ["Python", "FastAPI", "SQL", "Docker", "Git"],
        "total_experience_years": 3,
        "location": "Lucknow, Uttar Pradesh"
    }

    sample_jobs = [
        {"id": f"job-{i}", "title": f"Developer {i}", "required_skills": ["Python", "SQL"], "location_city": "Lucknow"}
        for i in range(10)
    ]

    t0 = time.perf_counter()
    tasks = [jev.score_job_match(profile, job) for job in sample_jobs]
    results = await asyncio.gather(*tasks)
    t1 = time.perf_counter()

    total_batch_ms = (t1 - t0) * 1000
    per_job_ms = total_batch_ms / len(sample_jobs)

    return {
        "job_batch_size": len(sample_jobs),
        "total_batch_latency_ms": round(total_batch_ms, 2),
        "per_job_latency_ms": round(per_job_ms, 2),
        "all_scored": len(results) == len(sample_jobs)
    }

async def benchmark_assessment_scoring(jev: JevProvider) -> dict:
    """Benchmark assessment answer scoring speed."""
    answers = [
        ("Describe your routine", "I manage the inventory ledger, unload incoming trucks, and supervise two junior handlers."),
        ("What tools do you use?", "I use Excel for stock records and a barcode scanner for dispatches."),
        ("Work environment", "I prefer collaborating with a team in warehouse operations rather than solo desk work.")
    ]

    times = []
    for q, a in answers:
        t0 = time.perf_counter()
        score = await jev.score_assessment_answer(q, a)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    return {
        "samples_count": len(answers),
        "avg_latency_ms": round(sum(times) / len(times), 2),
        "min_latency_ms": round(min(times), 2)
    }

async def run_all_benchmarks():
    print("=" * 60)
    print("SANKALP SYSTEM 1 & PERFORMANCE BENCHMARK SUITE")
    print("=" * 60)

    pdf_target = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "SkillBridgeAITeam_HackSquad.pptx.pdf")
    pdf_results = await benchmark_pdf_extraction(pdf_target)
    print("\n[1] PDF EXTRACTION ENGINE (PyMuPDF Block Layout)")
    for k, v in pdf_results.items():
        print(f"  - {k}: {v}")

    jev = JevProvider()

    print("\n[2] CHAT GUARDRAIL & INTENT TRIAGE")
    chat_results = await benchmark_chat_triage(jev)
    for k, v in chat_results.items():
        print(f"  - {k}: {v}")

    print("\n[3] JOB MATCH DECISION PASS (10 Candidates)")
    job_results = await benchmark_job_matching(jev)
    for k, v in job_results.items():
        print(f"  - {k}: {v}")

    print("\n[4] ASSESSMENT COMPETENCE SCORING")
    assessment_results = await benchmark_assessment_scoring(jev)
    for k, v in assessment_results.items():
        print(f"  - {k}: {v}")

    print("\n" + "=" * 60)
    return {
        "pdf": pdf_results,
        "chat": chat_results,
        "job_matching": job_results,
        "assessment": assessment_results
    }

if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
