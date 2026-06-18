from langchain_community.tools.tavily_search import TavilySearchResults

webSearchTool = TavilySearchResults(
    max_results=3,
    include_answer=True,
    include_raw_content=False
)