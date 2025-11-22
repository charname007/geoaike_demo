from calendar import c
from config import DEEPSEEK_CONFIG
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from search_tool import search_tools
from m_prompt import *
# from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from typing import Union
from structured_output import *
llm = ChatOpenAI(
    model=DEEPSEEK_CONFIG["model"],
    api_key=DEEPSEEK_CONFIG["api_key"],
    base_url=DEEPSEEK_CONFIG["base_url"],
    temperature=DEEPSEEK_CONFIG["temperature"]
)


@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


orchestrator_agent = create_agent(
    model=llm,
    tools=search_tools,
    system_prompt=get_orchestrator_prompt(),
    # checkpointer=InMemorySaver(),
    middleware=[handle_tool_errors],
    response_format=OrchestratorResponse,
    name="OrchestratorAgent"
)

historical_researcher_agent = create_agent(
    model=llm,
    tools=search_tools,
    system_prompt=get_historical_researcher_prompt(),
    # checkpointer=InMemorySaver(),
    middleware=[handle_tool_errors],
    response_format=HistoricalResearcherResponse,
    name="HistoricalResearcherAgent"
)

geographical_researcher_agent = create_agent(
    model=llm,
    tools=search_tools,
    system_prompt=get_geographical_researcher_prompt(),
    # checkpointer=InMemorySaver(),
    middleware=[handle_tool_errors],
    response_format=GeographicalResearcherResponse,
    name="GeographicalResearcherAgent"
)

cultural_researcher_agent = create_agent(
    model=llm,
    tools=search_tools,
    system_prompt=get_cultural_researcher_prompt(),
    # checkpointer=InMemorySaver(),
    middleware=[handle_tool_errors],
    response_format=CulturalResearcherResponse,
    name="CulturalResearcherAgent"
)

scientific_researcher_agent = create_agent(
    model=llm,
    tools=search_tools,
    system_prompt=get_scientific_researcher_prompt(),
    # checkpointer=InMemorySaver(),
    middleware=[handle_tool_errors],
    response_format=ScientificResearcherResponse,
    name="ScientificResearcherAgent"
)

validator_synthesizer_agent = create_agent(
    model=llm,  
    tools=search_tools,
    system_prompt=get_validator_synthesizer_prompt(),
    # checkpointer=InMemorySaver(),
    middleware=[handle_tool_errors],
    response_format=ValidatorSynthesizerResponse,
    name="ValidatorSynthesizerAgent"
)

# researchers=[historical_researcher_agent, geographical_researcher_agent, cultural_researcher_agent, scientific_researcher_agent]
researchers={
    "HistoricalResearcher": historical_researcher_agent,
    "GeographicalResearcher": geographical_researcher_agent,
    "CulturalResearcher": cultural_researcher_agent,
    "ScientificResearcher": scientific_researcher_agent
}