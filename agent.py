import os
from dotenv import load_dotenv

from crewai import Agent, LLM

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY is missing. "
        "Please add it to your .env file."
    )

llm = LLM(
    model="openrouter/openai/gpt-4o-mini",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

resume_screener_agent = Agent(
    role="AI Resume Screener",
    goal=(
        "Analyze a candidate's resume against a job description "
        "and provide an accurate, fair and easy-to-understand assessment."
    ),
    backstory=(
        "You are an expert recruitment assistant. "
        "You compare resumes with job requirements, identify matching "
        "skills and missing requirements, and explain your decision clearly. "
        "You must only use information present in the provided resume "
        "and job description."
    ),
    llm=llm,
    verbose=False
)