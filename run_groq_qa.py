import os
import pathlib
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Set it in your environment or in a .env file."
    )
 
groq_model = ChatGroq(
    model=GROQ_MODEL,
    temperature=0.2,
    max_tokens=1500,
    reasoning_format="parsed",
    max_retries=2,
)
 
class QAAgentState(TypedDict):
    requirement: str
    analysis: str
    test_cases: str
    security_review: str
    review: str
 
 
def safe_text(value: str) -> str:
    return str(value).encode("cp1252", errors="replace").decode("cp1252")
 
 
def call_specialist(system_prompt: str, task: str) -> str:
    response = groq_model.invoke([
        ("system", system_prompt),
        ("human", task),
    ])
    return response.content
 
 
def requirements_analyst(state: QAAgentState):
    analysis = call_specialist(
        "You are a senior QA requirements analyst. Identify actors, business rules, acceptance criteria, risks, dependencies, and ambiguous requirements. Be concise and do not invent missing facts.",
        f"Analyze this requirement for testing:\n\n{state['requirement']}",
    )
    return {"analysis": analysis}
 
 
def test_designer(state: QAAgentState):
    test_cases = call_specialist(
        "You are a senior test designer. Produce a compact Markdown table with ID, scenario, preconditions, steps, expected result, test type, and priority. Cover positive, negative, boundary, security, and failure paths.",
        f"Requirement:\n{state['requirement']}\n\nRequirements analysis:\n{state['analysis']}\n\nDesign executable test cases.",
    )
    return {"test_cases": test_cases}
 
 
def security_reviewer(state: QAAgentState):
    security_review = call_specialist(
        "You are a senior security reviewer. Evaluate the requirement and test cases for authentication, authorization, data protection, replay resistance, expiry, and generic error handling. Provide concise security findings and remediation recommendations.",
        f"Requirement:\n{state['requirement']}\n\nRequirements analysis:\n{state['analysis']}\n\nProposed test cases:\n{state['test_cases']}\n\nReview these artifacts for security gaps and recommendations.",
    )
    return {"security_review": security_review}
 
 
def qa_reviewer(state: QAAgentState):
    review = call_specialist(
        "You are a critical QA lead. Review the proposed tests for requirement coverage, missing edge cases, duplication, testability, business risk, and whether security findings were addressed. Finish with APPROVE or REVISE and a short reason.",
        f"Requirement:\n{state['requirement']}\n\nAnalysis:\n{state['analysis']}\n\nProposed tests:\n{state['test_cases']}\n\nSecurity review:\n{state['security_review']}",
    )
    return {"review": review}
 
 
builder = StateGraph(QAAgentState)
builder.add_node("requirements_analyst", requirements_analyst)
builder.add_node("test_designer", test_designer)
builder.add_node("security_reviewer", security_reviewer)
builder.add_node("qa_reviewer", qa_reviewer)
builder.add_edge(START, "requirements_analyst")
builder.add_edge("requirements_analyst", "test_designer")
builder.add_edge("test_designer", "security_reviewer")
builder.add_edge("security_reviewer", "qa_reviewer")
builder.add_edge("qa_reviewer", END)
 
qa_agent_chain = builder.compile()
 
 
def main() -> None:
    requirements_path = pathlib.Path(__file__).parent / "requirements_doc.md"
    if not requirements_path.exists():
        raise FileNotFoundError(f"Requirement document not found: {requirements_path}")
 
    requirement_text = requirements_path.read_text(encoding="utf-8").strip()
    if not requirement_text:
        raise ValueError("Requirement document is empty.")
 
    print(f"Loaded requirement from {requirements_path}:\n\n{requirement_text}\n")
 
    result = qa_agent_chain.invoke({
        "requirement": requirement_text,
        "analysis": "",
        "test_cases": "",
        "security_review": "",
        "review": "",
    })
 
    sections = [
        ("REQUIREMENTS ANALYST", "analysis"),
        ("TEST DESIGNER", "test_cases"),
        ("SECURITY REVIEWER", "security_review"),
        ("QA REVIEWER", "review"),
    ]
 
    for heading, key in sections:
        print(f"\n{'=' * 20} {heading} {'=' * 20}\n")
        print(safe_text(result[key]))
 
 
if __name__ == "__main__":
    main()