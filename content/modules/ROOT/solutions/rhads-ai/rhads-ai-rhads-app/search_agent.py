import os
import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch, TavilyExtract, TavilyCrawl
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

class SearchAgent:
    """
    A class to encapsulate the web research agent's functionality.
    """
    def __init__(self):
        """
        Initializes the agent by loading environment variables and setting up
        the LLM, tools, and the agent executor.
        """
        self._load_config()
        self._init_llm()
        self._init_search_tools()
        self._init_tavily_client()

    def _load_config(self):
        """Loads environment variables from a .env file."""
        load_dotenv()
        self.llm_api_base = os.getenv("LLM_API_BASE_URL")
        self.model_name = os.getenv("MODEL_NAME")
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

        if not all([self.llm_api_base, self.model_name, self.llm_api_key, self.tavily_api_key]):
            raise ValueError("One or more required environment variables are missing.")

    def _init_llm(self):
        self.llm = ChatOpenAI(
            base_url=self.llm_api_base,
            api_key=self.llm_api_key,
            model=self.model_name,
            temperature=0
        )

        
        query = "Hi!"
        response = self.llm.invoke([{"role": "user", "content": query}])
        print(response.text())
        return response.text()

    def _init_tavily_client(self):
        """Initialize direct TavilyClient for crawl functionality"""
        self.tavily_client = TavilyClient(api_key=self.tavily_api_key)

    def direct_crawl_website(self, url: str) -> str:
        """Crawl a website using direct TavilyClient to avoid LangChain wrapper issues"""
        try:
            crawl_results = self.tavily_client.crawl(url=url)
            return str(crawl_results)
        except Exception as e:
            return f"Crawl failed for {url}: {str(e)}"

    def direct_extract_content(self, urls: str) -> str:
        """Extract content from specific URLs using direct TavilyClient"""
        try:
            # Handle both single URL and comma-separated URLs
            if ',' in urls:
                url_list = [url.strip() for url in urls.split(',')]
            else:
                url_list = [urls.strip()]

            extract_results = self.tavily_client.extract(urls=url_list)
            return str(extract_results)
        except Exception as e:
            return f"Extract failed for {urls}: {str(e)}"

    def _init_search_tools(self):
        search = TavilySearch()

        # Create custom tools using direct TavilyClient
        @tool
        def tavily_crawl_direct(url: str) -> str:
            """Crawl a website comprehensively. Provide just the URL."""
            return self.direct_crawl_website(url)

        @tool
        def tavily_extract_direct(urls: str) -> str:
            """Extract content from specific web pages. Provide URL or comma-separated URLs."""
            return self.direct_extract_content(urls)

        self.tools = [search, tavily_crawl_direct, tavily_extract_direct]

    def run(self, query: str):
        print("run method" )
        model_with_tools = self.llm.bind_tools(self.tools)
        today = datetime.datetime.today().strftime("%A, %B %d, %Y")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
                        f"""
                    You are a research agent equipped with web search, website crawling, and content extraction tools. Your mission is to conduct comprehensive, accurate, and up-to-date research, grounding your findings in credible web sources.

                    **CRITICAL TOOL USAGE:**
                    - Tavily Search: Use only 'query' parameter for web search
                    - Tavily Crawl Direct: Use only 'url' parameter for comprehensive website exploration
                    - Tavily Extract Direct: Use only 'urls' parameter for extracting specific page content

                    **Today's Date:** {today}

                    **Available Tools:**

                    1. **Tavily Web Search**
                    * **Purpose:** Retrieve relevant web pages based on a query.
                    * **Usage:** ONLY use 'query' parameter
                    * **Example:** Search for "LinkedIn NYC jobs"

                    2. **Tavily Crawl Direct**
                    * **Purpose:** Comprehensively explore a website's structure and content.
                    * **Usage:** ONLY use 'url' parameter
                    * **When to use:** When you need complete coverage of a website's content
                    * **Example:** Crawl "https://docs.python.org" for comprehensive documentation overview

                    3. **Tavily Extract Direct**
                    * **Purpose:** Extract detailed content from specific web pages.
                    * **Usage:** ONLY use 'urls' parameter (single URL or comma-separated)
                    * **When to use:** When you have specific page URLs and need their detailed content
                    * **Example:** Extract content from "https://docs.python.org/3/tutorial/introduction.html"


                    **Guidelines for Conducting Research:**
                    * **Citations:** Always support findings with source URLs as in-text citations.
                    * **Accuracy:** Rely solely on data obtained via provided tools—never fabricate information.
                    * **Methodology:** Follow a structured approach: Thought, Action, Observation, and repeat until you can provide a Final Answer.

                    **CRITICAL TOOL USAGE RULES - FOLLOW EXACTLY:**
                    * Tavily Search: Use ONLY query parameter. Example: tavily_search(query="your search text")
                    * Tavily Crawl: Use ONLY url parameter. Example: tavily_crawl(url="https://example.com")
                    * Tavily Extract: Use ONLY urls parameter as proper list. Example: tavily_extract(urls=["https://example.com"])
                    * NEVER use string representations of lists like '["url"]' - use actual lists ["url"]
                    * NEVER wrap parameters in 'properties' objects
                    * NEVER use optional parameters like include_domains, extract_depth, search_depth, time_range
                    You will now receive a research question from the user:
                    """,
                     ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for tool calls
        ])

        model = create_openai_tools_agent(llm=model_with_tools, tools=self.tools, prompt=self.prompt)
        #model = create_react_agent(model=self.llm, tools="")
        #input_message = {"role": "user", "content": query}
        #response= model.invoke({"messages": [input_message]})

        # Create an Agent Executor to handle tool execution
        agent_executor = AgentExecutor(agent=model,  tools=self.tools, prompt=self.prompt, verbose=True)
        # Construct input properly as a dictionary
        output = agent_executor.invoke({"messages": [HumanMessage(content=query)]})
        response = output['output']       
        
        print("Printing response from agent." + response)
        return response



    def _search(self):
        search = TavilySearch(max_results=2)
        search_results = search.invoke("What is the weather in SF")
        print(search_results)
        # If we want, we can create other tools.
        # Once we have all the tools we want, we can put them in a list that we will reference later.
        tools = [search]

# --- Example of How to Use the Class ---
if __name__ == "__main__":
    # 1. Instantiate the agent
    research_agent = SearchAgent()
