from crewai import Task

from agent import resume_screener_agent


def create_resume_screening_task(resume_text, job_description):
    task = Task(
        description=f"""
Analyze the following resume against the following job description.

================ RESUME ================
{resume_text}

================ JOB DESCRIPTION ================
{job_description}

===============================================

Perform the following analysis:

1. Calculate an estimated match score from 0 to 100.
2. Decide the final verdict:
   - Strong
   - Moderate
   - Weak
3. Identify the candidate's matching skills.
4. Identify important missing or weak skills.
5. Compare the candidate's education and experience with the job requirements.
6. Give a short explanation for the score.
7. Give practical suggestions for improving the resume for this particular job.

Use only information available in the resume and job description.
Do not invent qualifications, experience, certifications or skills.

Return the result using EXACTLY this format:

SCORE: <number>/100

VERDICT: <Strong/Moderate/Weak>

MATCHING SKILLS:
- <skill>
- <skill>

MISSING OR WEAK SKILLS:
- <skill>
- <skill>

EXPERIENCE ANALYSIS:
<short explanation>

EDUCATION ANALYSIS:
<short explanation>

SUMMARY:
<short explanation>

IMPROVEMENT SUGGESTIONS:
- <suggestion>
- <suggestion>
""",
        expected_output=(
            "A complete resume screening report containing score, verdict, "
            "matching skills, missing skills, experience analysis, education "
            "analysis, summary and improvement suggestions."
        ),
        agent=resume_screener_agent
    )

    return task