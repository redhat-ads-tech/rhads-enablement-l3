import os
import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch, TavilyExtract, TavilyCrawl

class SearchAgent:
    """
    A class to encapsulate the web agent's functionality.
    """
    def __init__(self):
        """
        Initializes the agent by loading environment variables and setting up
        the LLM, tools, and the agent executor.
        """
        self._load_config()
        self._setup_llm_and_tools()
        self._create_agent()

    def _load_config(self):
        """Loads environment variables from a .env file."""
        load_dotenv()
        self.llm_api_base = os.getenv("LLM_API_BASE_URL")
        self.model_name = os.getenv("MODEL_NAME")
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

        if not all([self.llm_api_base, self.model_name, self.llm_api_key, self.tavily_api_key]):
            raise ValueError("One or more required environment variables are missing.")

    def _setup_llm_and_tools(self):
        """Initializes the LLM client and the research tools."""
        print(f"Connecting to model '{self.model_name}' at endpoint: {self.llm_api_base}")
        
        self.llm = ChatOpenAI(
            base_url=self.llm_api_base,
            api_key=self.llm_api_key,
            model=self.model_name
        )
        tavily_client = TavilyClient(api_key=self.tavily_api_key)
        search = TavilySearch(max_results=10, topic="general")

        extract = TavilyExtract(extract_depth="advanced")
        crawl = TavilyCrawl()

        # This list of tools will now be properly authenticated
        self.tools = [search, extract, crawl]


        
    def _create_agent(self):
        """Creates the agent prompt, binds tools, and sets up the executor."""
        today = datetime.datetime.today().strftime("%A, %B %d, %Y")
        
        # Force the agent to use a tool on each turn
        llm_with_tools = self.llm.bind_tools(self.tools, tool_choice=True)
        print(f"this are the tools '{self.tools}' ")
        self.agent = create_react_agent( 
            model=llm_with_tools,
            tools=self.tools,
            prompt=ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        f"""
                    You are a research agent equipped with advanced web tools: Tavily Web Search, Web Crawl, and Web Extract. Your mission is to conduct comprehensive, accurate, and up-to-date research, grounding your findings in credible web sources.

                    **Today's Date:** {today}

                    **Available Tools:**

                    1. **Tavily Web Search**
                    * **Purpose:** Retrieve relevant web pages based on a query.
                    * **Usage:** Provide a search query to receive semantically ranked results.
                    * **Best Practices:** Use specific queries and parameters like `time_range`.

                    2. **Tavily Web Crawl**
                    * **Purpose:** Explore a website's structure and gather content from linked pages for deep research.
                    * **Usage:** Input a base URL to crawl, specifying parameters like `max_depth`.
                    * **Best Practices:** Start with shallow crawls and use path filtering.

                    3. **Tavily Web Extract**
                    * **Purpose:** Extract the full content from specific web pages.
                    * **Usage:** Provide URLs to retrieve detailed content.
                    * **Best Practices:** Set `extract_depth` to "advanced" for detailed content.

                    **Guidelines for Conducting Research:**
                    * **Citations:** Always support findings with source URLs as in-text citations.
                    * **Accuracy:** Rely solely on data obtained via provided tools—never fabricate information.
                    * **Methodology:** Follow a structured approach: Thought, Action, Observation, and repeat until you can provide a Final Answer.

                    You will now receive a research question from the user:
                    """,
                            ),
                           # MessagesPlaceholder(variable_name="messages"),
                        ]
                    )
                )
        #self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, query: str):
        """
        Runs the agent with a specific query, streams the intermediate steps,
        and returns the final answer.
        """
        print(f"\n--- Running Agent with Query: '{query}' ---")
        
        user_input= {
            "messages": [
                HumanMessage(
                    content=query
                )
            ]
        }
        
        final_answer = None
        try:
            # Invoke the agent executor
            for stream in self.agent.stream(user_input, stream_mode="values"):
                message = stream["messages"][-1]
                final_message_1 = message
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
        except Exception as e:
            print(f"An error occurred while running the agent: {e}")
            final_answer = f"Error: {e}"
            
        print("\n--- Final Answer ---")
        print(final_answer)
        return final_answer

# --- Example of How to Use the Class ---
if __name__ == "__main__":
    # 1. Instantiate the agent
    research_agent = SearchAgent()

    # 2. Run a research task
    research_agent.run("What are the latest developments in quantum computing from the past month?")
    
    # 3. Run another task
    research_agent.run("Summarize the key features of the new Apple Vision Pro.")