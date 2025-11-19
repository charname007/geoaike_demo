from typing import Annotated, List, TypedDict, Union
import operator

from structured_output import *
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage

from langgraph.graph.message import add_messages

# 合并research_results字典
# 1. 定义合并函数 (Reducer)


def merge_dicts(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """将新字典合并到旧字典中"""
    if not left:
        left = {}
    if not right:
        right = {}
    # 字典合并：如果有相同的 Key，right 会覆盖 left
    # 但在你的场景中，每个 Researcher 的 Key (agent.name) 都是唯一的，所以是安全的
    return {**left, **right}

class AgentState(TypedDict):
    user_prompt: str
    theme: str
    task_analysis: str
    orchestrator_plan: Dict[str, Task]
    # messages: Annotated[List[AnyMessage], add_messages]
    # research_results: Annotated[Union[HistoricalResearcherResponse,  # 添加这行
    #                                  GeographicalResearcherResponse,
    #                                  CulturalResearcherResponse,
    #                                  ScientificResearcherResponse], operator.add]  # 添加这行
    research_results:Annotated[Dict[ALLOWED_RESEARCHERS, Union[HistoricalResearcherResponse,
                                         GeographicalResearcherResponse,
                                         CulturalResearcherResponse,
                                                               ScientificResearcherResponse]], merge_dicts]
    # research_results: Annotated[List[GeoFeature], operator.add]
    # final_results: ValidatorSynthesizerResponse



class InputState(TypedDict):
    user_prompt: str


class ResearcherState(TypedDict):
    user_prompt: str
    theme: str
    task_analysis: str
    internal_task: Task
    research_result: Union[HistoricalResearcherResponse,
                           GeographicalResearcherResponse,
                           CulturalResearcherResponse,
                           ScientificResearcherResponse]


class OutputState(TypedDict):
    final_results: ValidatorSynthesizerResponse




