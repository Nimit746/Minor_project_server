
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from typing import Annotated, Literal
from Agentic_wf.agents import build_question_generator_graph, build_roadmap_graph, build_ingestion_graph

# Initialize the agents
ques_agent = build_question_generator_graph()
roadmap_agent = build_roadmap_graph()
resume_parser_agent = build_ingestion_graph()
import operator
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver

# Initialize the Gemini model
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Define the tools for the initial routing
@tool
def roadmap(
    job_role: Annotated[str, "The job role for which the roadmap is to be generated."],
    experience: Annotated[str, "The experience level of the user."]
):
    """Generates a roadmap for a given job role and experience level."""
    return roadmap_agent.invoke({"job_role": job_role, "experience": experience})

@tool
def generate_questions(
    job_role: Annotated[str, "The job role for which the questions are to be generated."],
    experience: Annotated[str, "The experience level of the user."],
    num_questions: Annotated[int, "The number of questions to be generated."]
):
    """Generates interview questions for a given job role and experience level."""
    return ques_agent.invoke({"job_role": job_role, "experience": experience, "num_questions": num_questions})

@tool
def resume_parser(
    resume: Annotated[str, "The path to the resume file."]
):
    """Parses a resume and extracts relevant information."""
    return resume_parser_agent.invoke({"resume": resume})

# Create the router
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Your role is to understand the user's request and decide which of the following tools to use: 'roadmap', 'generate_questions', or 'resume_parser'.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
llm_with_tools = llm.bind_tools([roadmap, generate_questions, resume_parser])
router = prompt | llm_with_tools