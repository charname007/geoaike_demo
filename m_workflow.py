
from ast import In
import re
import struct
from urllib import response
from langgraph.types import Send
from m_state import *

from langgraph.graph import StateGraph, START, END
from loguru import logger
from m_agents import *

from langchain_core.messages import AIMessageChunk

# from text_imager import generate_symbol_image, download_image
import asyncio
from text_imager import process_features_async
retry_count=10


#路由逻辑
def orchestrator_to_researchers(state: AgentState):
    """
    路由逻辑：将编排器的计划发送给各研究员
    """
    plan = state.get("orchestrator_plan")

    if not plan:
        # or not plan.task_allocation:
        # 如果没有分配任务，直接结束或跳到错误处理
        return []

    sends = []
    for role, task in plan.items():

        logger.info(f"Routing task {task} to {role}")
        sends.append(Send(role, {"internal_task": task}))

    return sends


def orchestrator_node(state: InputState) -> AgentState:
    """
    编排器节点逻辑
    """
    global retry_count
    user_prompt = state.get("user_prompt")
    if not user_prompt:
        raise ValueError("user_prompt is required for orchestrator.")

    response = orchestrator_agent.invoke({
        "messages": [
            # SystemMessage(content=get_orchestrator_prompt()),
            HumanMessage(content=user_prompt)]
    }
    )
    if response is None:
        #尝试重新调用
        while response is None and retry_count>0:
            logger.warning(f"Orchestrator response is None, retrying... {retry_count} attempts left.")
            response = orchestrator_agent.invoke({
                "messages": [
                    # SystemMessage(content=get_orchestrator_prompt()),
                    HumanMessage(content=user_prompt)]
            }
            )
            retry_count-=1
    
    if response is None:
        raise ValueError("Orchestrator failed to produce a response after retries.")
    

    orchestrator_data = response.get("structured_response")
    if not orchestrator_data:
        while orchestrator_data is None and retry_count>0:
            logger.warning(f"Orchestrator structured_response is None, retrying... {retry_count} attempts left.")
            response = orchestrator_agent.invoke({
                "messages": [
                    # SystemMessage(content=get_orchestrator_prompt()),
                    HumanMessage(content=f"{user_prompt}\n请确保返回符合结构化输出要求的响应格式。你的上一次响应{response}未能正确解析为结构化格式，请重新生成符合要求的响应。")
            ]}
            )
            orchestrator_data = response.get("structured_response")
            retry_count-=1
    if orchestrator_data is None:
        raise ValueError("Orchestrator failed to produce a structured_response after retries.")

    # 解析响应为 OrchestratorResponse 对象
    # orchestrator_plan = OrchestratorResponse.parse(response.content)
    
    logger.info(f"Orchestrator response: {orchestrator_data}")

    orchestrator_plan = orchestrator_data.task_allocation
    # state["orchestrator_plan"] = orchestrator_plan
    return {"orchestrator_plan": orchestrator_plan,
            "user_prompt": user_prompt,
            "theme": orchestrator_data.theme,
            "task_analysis": orchestrator_data.task_analysis
            }


def create_researcher_node(agent):
    def researcher_node(state: ResearcherState) -> AgentState:
        """
        研究员节点逻辑
        """
        global retry_count
        user_prompt = state.get("user_prompt")
        theme = state.get("theme")
        task_analysis = state.get("task_analysis")
        internal_task = state.get("internal_task")

        if not internal_task:
            raise ValueError("internal_task is required for researcher.")

        response = agent.invoke({
            "messages": [
                # SystemMessage(content=get_researcher_prompt(researcher_type)),
                HumanMessage(content=f"User Prompt: {user_prompt}\n经过分析，得到Task Analysis: {task_analysis}\n确认地图的主题为Theme: {theme}\n分配给你的Internal Task: {internal_task}")]
        }
        )
        if response is None:            #尝试重新调用
            while response is None and retry_count>0:
                logger.warning(f"{agent.name} response is None, retrying... {retry_count} attempts left.")
                response = agent.invoke({
                    "messages": [
                        # SystemMessage(content=get_researcher_prompt(researcher_type)),
                        HumanMessage(content=f"User Prompt: {user_prompt}\n经过分析，得到Task Analysis: {task_analysis}\n确认地图的主题为Theme: {theme}\n分配给你的Internal Task: {internal_task}")]
                }
                )
                retry_count-=1
        if response is None:
            raise ValueError(f"{agent.name} failed to produce a response after retries.")
        
        research_data = response.get("structured_response")

        if research_data is None:
            while research_data is None and retry_count>0:
                logger.warning(f"{agent.name} structured_response is None, retrying... {retry_count} attempts left.")
                response = agent.invoke({
                    "messages": [
                        # SystemMessage(content=get_researcher_prompt(researcher_type)),
                        HumanMessage(content=f"User Prompt: {user_prompt}\n经过分析，得到Task Analysis: {task_analysis}\n确认地图的主题为Theme: {theme}\n分配给你的Internal Task: {internal_task}\n请确保返回符合结构化输出要求的响应格式。你的上一次响应{response}未能正确解析为结构化格式，请重新生成符合要求的响应。")]
                }
                )
                research_data = response.get("structured_response")
                retry_count-=1
        if research_data is None:
            raise ValueError(f"{agent.name} failed to produce a structured_response after retries.")
        logger.info(f"{agent.name} response: {research_data}")
        return {"research_results": {agent.name: research_data}
                # , "user_prompt": user_prompt
                # , "theme": theme
                # , "task_analysis": task_analysis
                }
    return researcher_node


def validator_synthesizer_node(state: AgentState) -> OutputState:
    """
    验证者与综合者节点逻辑
    """
    global retry_count
    user_prompt = state.get("user_prompt")
    task_analysis = state.get("task_analysis")
    theme = state.get("theme")

    research_results = state.get("research_results", {})
    if not research_results:
        raise ValueError(
            "research_results are required for validator_synthesizer.")

    response = validator_synthesizer_agent.invoke({
        "messages": [
            # SystemMessage(content=get_validator_synthesizer_prompt()),
            HumanMessage(content=f"User Prompt: {user_prompt}\n经过分析，得到Task Analysis: {task_analysis}\n确认地图的主题为Theme: {theme}\n最终得到的Research Results: {research_results}")]
    }
    )
    if response is None:
        #尝试重新调用
        while response is None and retry_count>0:
            logger.warning(f"ValidatorSynthesizer response is None, retrying... {retry_count} attempts left.")
            response = validator_synthesizer_agent.invoke({
                "messages": [
                    # SystemMessage(content=get_validator_synthesizer_prompt()),
                    HumanMessage(content=f"User Prompt: {user_prompt}\n经过分析，得到Task Analysis: {task_analysis}\n确认地图的主题为Theme: {theme}\n最终得到的Research Results: {research_results}")]
            }
            )
            retry_count-=1
    if response is None:
        raise ValueError("ValidatorSynthesizer failed to produce a response after retries.")
    validator_synthesizer_data = response.get("structured_response")
    if validator_synthesizer_data is None:
        while validator_synthesizer_data is None and retry_count>0:
            logger.warning(f"ValidatorSynthesizer structured_response is None, retrying... {retry_count} attempts left.")
            response = validator_synthesizer_agent.invoke({
                "messages": [
                    # SystemMessage(content=get_validator_synthesizer_prompt()),
                    HumanMessage(content=f"User Prompt: {user_prompt}\n经过分析，得到Task Analysis: {task_analysis}\n确认地图的主题为Theme: {theme}\n最终得到的Research Results: {research_results}\n请确保返回符合结构化输出要求的响应格式。你的上一次响应{response}未能正确解析为结构化格式，请重新生成符合要求的响应。")]
            }
            )
            validator_synthesizer_data = response.get("structured_response")
            retry_count-=1
    if validator_synthesizer_data is None:
        raise ValueError("ValidatorSynthesizer failed to produce a structured_response after retries.")

    logger.info(
        f"validator_synthesizer_agent response: {validator_synthesizer_data}")
    # logger.info(f"ValidatorSynthesizer response: {response}")
    # validator_synthesizer_data = response.get("structured_response")
    retry_count=10  # 重置重试计数器
    return {
        "final_results": validator_synthesizer_data
    }


# def stream_and_logger(agent, input_data):
#     response = None
#     print(f"--- Starting {getattr(agent, 'name', 'Agent')} stream ---")

#     for chunk, metadata in agent.stream(input_data, stream_mode="messages"):

#         # 1. 累加完整的响应 (用于最后返回)
#         if response is None:
#             response = chunk
#         else:
#             response += chunk

#         # 2. 处理主要内容 (Text)
#         # 大多数模型(OpenAI/DeepSeek) content 是字符串
#         if chunk.content:
#             print(chunk.content, end="", flush=True)

#         # 3. 处理推理内容 (Reasoning) - 针对 DeepSeek R1 等
#         # DeepSeek 的推理内容通常在 additional_kwargs 的 reasoning_content 字段
#         if "reasoning_content" in chunk.additional_kwargs:
#             r_content = chunk.additional_kwargs["reasoning_content"]
#             if r_content:
#                 print(f"\n[Reasoning]: {r_content}", end="", flush=True)

#         # 4. 处理工具调用 (Tool Calls)
#         # LangChain 把工具流式放到了专门的字段
#         if chunk.tool_call_chunks:
#             for tool_chunk in chunk.tool_call_chunks:
#                 # 打印正在调用的工具名或参数片段
#                 if tool_chunk.get("name"):
#                     print(f"\n[Calling Tool]: {tool_chunk['name']}...")
#                 elif tool_chunk.get("args"):
#                     # 参数通常是碎片化的 JSON 字符串
#                     pass

#     print("\n--- Stream Finished ---")
#     # logger.info(f"Full Response: {response}")
#     return response


#文生图节点（异步版本）
async def text2imager(state: OutputState) -> OutputState:
    """文生图节点：并行为每个地理特征生成符号图像"""

    
    final_results = state.get("final_results")
    if not final_results:
        raise ValueError("final_results is required for text2imager.")
    
    map_data = getattr(final_results, 'map_data', None)
    if not map_data or not hasattr(map_data, 'features'):
        raise ValueError("map_data with features is required for text2imager.")
    theme= final_results.theme if hasattr(final_results, 'theme') else "地理特征"
    features = list(map_data.features)
    
    # 在当前事件循环中运行异步代码
    await process_features_async(features, theme)
    
    return {"final_results": final_results}

workflow = StateGraph(AgentState, input_schema=InputState,
                      output_schema=OutputState)
workflow.add_node("Orchestrator", action=orchestrator_node)
workflow.add_node(
    "ValidatorSynthesizer", validator_synthesizer_node)
for researcher_name, researcher_agent in researchers.items():
    researcher_node = create_researcher_node(researcher_agent)
    workflow.add_node(researcher_name, researcher_node)
    workflow.add_edge(
        researcher_name, "ValidatorSynthesizer")
    # globals()[f"{researcher_agent.system_prompt.split()[0].lower()}_node"] = researcher_node


workflow.add_edge(START, "Orchestrator")
workflow.add_conditional_edges(
    "Orchestrator", orchestrator_to_researchers, list(researchers.keys()))
# workflow.add_edge("ValidatorSynthesizer", END)


workflow.add_node("ImageGenerator", text2imager)
workflow.add_edge("ValidatorSynthesizer", "ImageGenerator")
workflow.add_edge("ImageGenerator", END)
m_graph = workflow.compile()
logger.info("Workflow compiled successfully.")

if __name__ == "__main__":
    # 测试工作流
    test_input = {
        "user_prompt": "请帮我创建一张展示李白人生足迹的地图，要求从历史记录，李白创作的诗歌中寻找。"
    }

    result =  m_graph.ainvoke(test_input)
    logger.info(f"Final Output: {result}")
    # 仅流式传输消息变化
    # for event in graph.stream(test_input):
    #     # event 的格式通常是: {'Node名字': {状态更新的内容}}
    #     for node_name, values in event.items():
    #         print(f"--- {node_name} 完成了工作 ---")
    #         print(f"最新结果: {values}")
    #         print("---------------------------")
