from re import search
from langchain_community.tools import DuckDuckGoSearchRun,WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
search_tools = [DuckDuckGoSearchRun(), WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())]

if __name__ == "__main__":
    query = "What are the key historical events that took place in Beijing during the Ming Dynasty?"
    for tool in search_tools:
        result = tool.run(query)
        print(f"Results from {tool.name}:\n{result}\n{'-'*60}\n")