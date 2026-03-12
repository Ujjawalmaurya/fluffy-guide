# [ASSESSMENT] Phase definitions for the adaptive assessment.
# To add or modify a phase: change only this file.
# No other file needs to change when phases are updated.

PHASES = {
  1: {
    "name": "Current Situation",
    "goal": "Understand where user is now and their biggest frustration",
    "min_questions": 2,
    "max_questions": 2,
    "instruction": """Ask about their current work situation and main
      challenge. Do NOT ask about goals yet. Ask ONE focused question.
      For individual_bluecollar: ask about their daily work, not academics.
      For individual_youth: ask about studies or first job experience.
      For individual_informal: ask about their current livelihood activity.
      For org types: ask about the workforce they manage."""
  },
  2: {
    "name": "Skills Inventory",
    "goal": "Map actual skills with depth — not just names, but how well",
    "min_questions": 3,
    "max_questions": 4,
    "instruction": """Based on what they shared in Phase 1, ask about
      specific skills they use. If they mention a skill or tool, probe
      deeper — ask HOW they use it, not just IF they know it.
      Ask ONE skill at a time. Use simple language.
      Never ask generic questions like 'What are your skills?'
      Instead ask: 'You mentioned working with vehicles. Which parts
      do you fix most confidently — engine, electrical, or bodywork?'
      Match vocabulary to their education level. No technical jargon
      for blue-collar or informal workers."""
  },
  3: {
    "name": "Work Style",
    "goal": "Understand environment preferences for accurate job matching",
    "min_questions": 2,
    "max_questions": 2,
    "instruction": """Ask about preferred work environment and schedule.
      Keep it conversational and relatable.
      First question: 'Would you prefer working closely with a team
      every day, or mostly on your own?'
      Second question: ask about timing or location flexibility.
      Both questions must be short and easy to answer."""
  },
  4: {
    "name": "Goals and Blockers",
    "goal": "Surface real career goals AND what actually stops them",
    "min_questions": 2,
    "max_questions": 2,
    "instruction": """Do NOT ask 'What is your career goal?' directly.
      First question — ask situationally:
      'Imagine it is two years from now and things went really well
      for you. What does a good workday look like?'
      Second question — ask what feels like the biggest obstacle
      between now and that future.
      Probe real barriers: time, money, location, confidence, family.
      Use empathetic, non-judgmental language throughout."""
  },
  5: {
    "name": "Wildcard",
    "goal": "Reveal personality and hidden motivation",
    "min_questions": 1,
    "max_questions": 1,
    "instruction": """Ask ONE unexpected open-ended question that
      reveals genuine motivation. Choose the best option based on
      what the person has already shared:
      Option A: 'If you could learn one thing completely free
        starting tomorrow, what would it be?'
      Option B: 'What is something you are good at that most
        people around you do not know about?'
      Option C: 'When you imagine your ideal work five years from
        now, what is the one thing that must be different from today?'
      Pick the option most relevant to this person's conversation."""
  }
}

# Maps question numbers to phases.
# Question 1-2 → Phase 1, 3-6 → Phase 2, etc.
PHASE_QUESTION_RANGES = {
  1: (1, 2),
  2: (3, 6),
  3: (7, 8),
  4: (9, 10),
  5: (11, 11),
}

def get_phase_for_question(question_number: int) -> int:
  """
  Returns the phase number for a given question number.
  Falls back to phase 5 for any question beyond 11.
  """
  for phase, (start, end) in PHASE_QUESTION_RANGES.items():
    if start <= question_number <= end:
      return phase
  return 5

def get_phase_config(phase_number: int) -> dict:
  """Returns full phase config dict for a given phase number."""
  config = PHASES.get(phase_number, PHASES[5])
  return {**config, "phase_number": phase_number}
