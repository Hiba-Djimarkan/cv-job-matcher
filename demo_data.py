"""demo_data.py - Pre-written example results used in demo mode (no API key needed).

These are NOT generated from the user's input: they only show what the
application's output looks like. The keys match what the real pipeline returns.
"""

DEMO_RESULT = {
    "match": {
        "score": 78,
        "strengths": [
            "Python, SQL and Git match the core requirements",
            "Bachelor's degree in computer science",
            "Fluent English (studied in an English-taught programme)",
        ],
        "missing_skills": [
            "No explicit REST API experience mentioned",
            "No work experience listed (internships or professional projects)",
        ],
        "reasoning": (
            "The candidate meets most technical requirements and has the right "
            "educational background. The main gap is practical experience with "
            "REST APIs, which could be shown through a project."
        ),
        "advice": [
            "Add a project that consumes or exposes a REST API",
            "Quantify results in the projects section",
            "Mention teamwork and version control practices",
        ],
    },
    "letter": (
        "Dear Hiring Manager,\n\n"
        "I am writing to apply for the Junior Python Developer position. "
        "With a Bachelor's degree in Computer Science Engineering and hands-on "
        "experience in Python, SQL and Git, I am eager to contribute to your team "
        "while continuing to learn.\n\n"
        "I would welcome the opportunity to discuss how my skills can support "
        "your projects.\n\n"
        "Kind regards,"
    ),
}

DEMO_REVIEW = {
    "overall_score": 72,
    "summary": (
        "A clear CV with a solid education section. It would be stronger with "
        "measurable results and a short professional summary."
    ),
    "sections_present": ["Contact information", "Education", "Skills", "Languages"],
    "sections_missing": ["Professional summary", "Projects", "Work experience"],
    "strengths": [
        "Relevant technical skills listed clearly",
        "Concise, easy to scan layout",
    ],
    "weaknesses": [
        "No measurable achievements",
        "No projects section to prove the listed skills",
    ],
    "improvements": [
        {
            "issue": "Missing professional summary",
            "suggestion": "Add 2-3 lines at the top describing your profile and goal.",
            "example": "Computer Science Engineering graduate with experience in Python and SQL, seeking an internship in AI and automation.",
        },
        {
            "issue": "Skills are not backed by evidence",
            "suggestion": "Add a Projects section with technologies used and the result.",
            "example": "Built a CV & Job Matcher web app (Python, Streamlit, LLM API) that scores CVs against job offers.",
        },
    ],
}