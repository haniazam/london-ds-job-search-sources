#!/usr/bin/env python3
"""Role-family classifier for the London DS search (shared by refresh_roles.py and
pay_enrich.py; run this file directly to execute its tests).

PRINCIPLE: classify by the title's CORE ROLE, never by incidental keywords.
A specialism modifier must never exclude a role. "Senior Data Scientist (Economist)",
"Data Scientist, Machine Learning", "Research Data Scientist", "Staff Scientist,
Experimentation" and "Director, Data Science" are all Standard DS. A title is
"Other DS-family" only when its core role IS a different discipline: Research
Scientist/Engineer, ML/AI Engineer or Scientist, Applied Scientist, Quant
Researcher/Trader/Developer, Data/Analytics Engineer, Data/Product Analyst,
Economist, Statistician, Software Engineer.

Why not a keyword blacklist: the previous filter rejected any title containing
research|machine learning|ml|applied|analyst|engineer|economist|quant, which silently
dropped exactly the senior product-DS titles the search is for. Add test cases below
whenever a real title is misclassified; never fix it by special-casing a company.
"""
import re, sys

# The Data-Scientist family as a CORE role. Prefix words (Senior, Staff, Applied,
# Research, Genomic, Telematics, Credit Risk ...) are allowed because they are
# modifiers of "Data Scientist", not a different job.
STANDARD_CORE = re.compile(r"""\b(
    data\s+scientists?
  | data\s+science\s+(manager|lead|leader|director|head|partner|team\s+lead|practice\s+lead)
  | (head|director|vp|vice\s+president|chief|manager|lead|principal|senior\s+manager|sr\.?\s+manager)
        \s*(,|:|-|–|of)?\s*(of\s+)?(\w+[\s&/]+){0,3}data\s+science\b
  | decision\s+scientists?
  | product\s+scientists?
  | analytics\s+scientists?
  | (experimentation|measurement|causal\s+inference|growth|marketing)\s+scientists?
)""", re.I | re.X)

# A different discipline as the CORE role. Only these exclude.
OTHER_CORE = re.compile(r"""\b(
    research\s+(scientist|engineer|lead|associate|fellow)
  | (machine\s+learning|ml|ai|deep\s+learning|nlp|computer\s+vision|llm)\s+(engineer|scientist|researcher|specialist)
  | applied\s+(scientist|researcher|ml|ai)
  | quant(itative)?\s+(researcher|analyst|trader|developer|strategist|engineer|portfolio)
  | (data|analytics|software|platform|backend|infrastructure|ml\s*ops|mlops)\s+engineer
  | (data|product|business|insights?|marketing|financial|commercial|growth|bi)\s+analyst
  | economist
  | statistician
  | bioinformatician
  | data\s+architect
  | actuary
)\b""", re.I | re.X)

# "Scientist" titles without the words "data science" that are product-DS roles.
SCIENTIST = re.compile(r"\bscientists?\b", re.I)
PRODUCT_DS_SIGNAL = re.compile(r"experiment|measurement|causal|product|analytics|growth|insight|decision|a/b|marketing", re.I)

def classify(title: str) -> str:
    """Return 'Standard DS' or 'Other DS-family'."""
    t = re.sub(r"\s+", " ", title or "").strip()
    if STANDARD_CORE.search(t):
        return "Standard DS"                      # core is Data Scientist family: modifiers never exclude
    if OTHER_CORE.search(t):
        return "Other DS-family"                  # core is another discipline
    if SCIENTIST.search(t) and PRODUCT_DS_SIGNAL.search(t):
        return "Standard DS"                      # e.g. "Staff Scientist, Experimentation"
    return "Other DS-family"

# Collection regex for the ATS sweep: everything the classifier might call Standard DS,
# plus the DS-family titles we keep in the CSV under "Other DS-family".
COLLECT = re.compile(r"data scien|decision scien|product scien|analytics scien|applied scien|research scien|"
                     r"machine learning|\bml scien|economist|\bquant|data analyst|"
                     r"(experimentation|measurement|causal|growth|marketing)[^|,]{0,25}scientist|"
                     r"scientist[^|]{0,25}(experimentation|measurement|causal|product analytics|growth)", re.I)

TESTS = [
    # --- must be Standard DS: high-value titles the old blacklist excluded ---
    ("Senior Data Scientist (Economist)", "Standard DS"),
    ("Data Scientist, Machine Learning", "Standard DS"),
    ("Senior Data Scientist, Machine Learning", "Standard DS"),
    ("Research Data Scientist", "Standard DS"),
    ("Staff Scientist, Experimentation", "Standard DS"),
    ("Principal Scientist, Product Analytics", "Standard DS"),
    ("Director, Data Science (AI)", "Standard DS"),
    ("Head of Telematics Data Science", "Standard DS"),
    ("Senior Manager, Product Data Science & Analytics", "Standard DS"),
    ("Sr. Manager, Data Science", "Standard DS"),
    ("Data Science Manager – Experimentation: Innovation & Research", "Standard DS"),
    ("Senior Data Scientist, Engineering Analytics", "Standard DS"),
    ("Applied Data Scientist", "Standard DS"),
    ("Data Scientist / Analyst", "Standard DS"),
    ("Quantitative Data Scientist", "Standard DS"),
    ("Senior Data Scientist - AI Tooling", "Standard DS"),
    ("Data Scientist - Research & Insights", "Standard DS"),
    ("Decision Scientist", "Standard DS"),
    ("Senior Product Data Scientist", "Standard DS"),
    ("Senior/Staff Data Scientist - Measurement, Experimentation & Causal Inference", "Standard DS"),
    ("Senior Data Science Lead - AML Risk", "Standard DS"),
    ("Lead Genomic Data Scientist - Cancer", "Standard DS"),
    ("Forward Deployed Data Scientist", "Standard DS"),
    ("Data Scientist II", "Standard DS"),
    ("Data Scientist (Mid and Senior Level)", "Standard DS"),
    ("Staff Product Data Scientist, Google Shopping", "Standard DS"),
    # --- must be Other: the core role is a different discipline ---
    ("Research Scientist, Reinforcement Learning", "Other DS-family"),
    ("Research Engineer, Frontier Safety", "Other DS-family"),
    ("Machine Learning Engineer", "Other DS-family"),
    ("Senior ML Engineer", "Other DS-family"),
    ("Applied Scientist, Prime Video", "Other DS-family"),
    ("Quantitative Researcher", "Other DS-family"),
    ("Quantitative Developer - Python", "Other DS-family"),
    ("Economist", "Other DS-family"),
    ("Senior Economist, Pricing", "Other DS-family"),
    ("Data Engineer", "Other DS-family"),
    ("Analytics Engineer", "Other DS-family"),
    ("Lead Product Analyst", "Other DS-family"),
    ("Senior Data Analyst", "Other DS-family"),
    ("Machine Learning Scientist", "Other DS-family"),
    ("Research Scientist, Product", "Other DS-family"),
    ("Applied Scientist, Experimentation", "Other DS-family"),
    ("Statistician", "Other DS-family"),
]

if __name__ == "__main__":
    bad = [(t, e, classify(t)) for t, e in TESTS if classify(t) != e]
    for t, e, g in bad: print(f"FAIL {t!r}: expected {e}, got {g}")
    print(f"{len(TESTS)-len(bad)}/{len(TESTS)} role-taxonomy tests pass")
    sys.exit(1 if bad else 0)
