from crewai import Crew

from task import create_resume_screening_task


def analyze_resume(resume_text, job_description):

    task = create_resume_screening_task(
        resume_text,
        job_description
    )

    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        verbose=False
    )

    result = crew.kickoff()

    return str(result)


if __name__ == "__main__":

    print("=" * 60)
    print("AI RESUME SCREENER")
    print("=" * 60)

    resume_file = input("Enter resume text/file path: ").strip()

    job_description = input(
        "Enter Job Description: "
    ).strip()

    with open(resume_file, "r", encoding="utf-8") as file:
        resume_text = file.read()

    result = analyze_resume(
        resume_text,
        job_description
    )

    print("\n")
    print("=" * 60)
    print("SCREENING RESULT")
    print("=" * 60)

    print(result)