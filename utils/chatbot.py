# utils/chatbot.py

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class ChatBotManager:
    def __init__(self, secrets):
        """
        Initializes the ChatBotManager with LLM configuration from secrets.
        """
        self.secrets = secrets
        self.llm = self.create_llm()
        self.agent = None
        self.chat_history = ChatMessageHistory()

    def create_llm(self):
        """
        Creates the LLM based on the provided secrets configuration.
        """
        llm_provider = self.secrets["llm"]["provider"]  # openai, anthropic or local

        if llm_provider == "openai":
            return ChatOpenAI(
                openai_api_key=self.secrets["openai"]["api_key"],
                model=self.secrets["openai"]["model"],
                temperature=0
            )
        elif llm_provider == "anthropic":
            return ChatAnthropic(
                anthropic_api_key=self.secrets["anthropic"]["api_key"],
                model=self.secrets["anthropic"]["model"]
            )
        elif llm_provider == "LOCAL":
            return ChatOpenAI(
                base_url=self.secrets["local"]["base_url"],
                api_key="lm-studio"
            )
        else:
            raise ValueError("Unsupported LLM provider")

    def initialize_agent(self, engine):
        """Initializes LangChain agent with SQL database and chat history."""
        db = SQLDatabase(engine)

        system = """You are an agent designed to interact with a SQL database.
            Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
            Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
            You can order the results by a relevant column to return the most interesting examples in the database.
            Never query for all the columns from a specific table, only ask for the relevant columns given the question.
            You have access to tools for interacting with the database.
            Only use the given tools. Only use the information returned by the tools to construct your final answer.
            You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

            DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

            Use the following chat history and tools to answer the user's questions.
            If is necessary, show the output in a table format."""

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])

        self.agent = create_sql_agent(
            llm=self.llm, 
            db=db, 
            prompt=prompt_template, 
            agent_type="tool-calling", 
            verbose=True
        )


    def process_question(self, question):
        """Processes the user's question using the initialized LangChain agent."""
        try:
            response = self.agent.run({
                "input": question,
                "chat_history": self.chat_history.messages,
                "agent_scratchpad": ""
            })
            return response
        except Exception as e:
            return f"Oops! Something went wrong while thinking: {e}"

    def add_user_message(self, message):
        """Adds a user message to the chat history."""
        self.chat_history.add_user_message(message)

    def add_ai_message(self, message):
        """Adds an AI message to the chat history."""
        self.chat_history.add_ai_message(message)
