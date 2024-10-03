
# Chat with DB

**Chat with DB** is an application designed to interact with different relational databases through a chatbot powered by large language models (LLM). The user-friendly Streamlit interface allows you to connect, make queries in natural language, and manage multiple connections seamlessly.

## Key Features

- **Multiple connections**: Create and maintain connections with different relational databases simultaneously.
- **Smart chatbot**: A chatbot capable of interacting with your databases using natural language, powered by models such as OpenAI, Anthropic, or even local models.
- **Persistent chat history**: Keeps the chat history even when switching databases, allowing you to cross-reference data without connecting the databases directly.

## Installation

Follow these steps to set up and run the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gianfrancolombardo/chat-with-db.git
   cd chat-with-db
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure secrets**:

   The `secrets.toml` file contains the necessary configurations for the app and language models (LLM). You need to rename the example file and then configure it according to your needs:

   - Rename the `secrets.mock.toml` file to `secrets.toml`:
     ```bash
     mv .streamlit/secrets.mock.toml .streamlit/secrets.toml
     ```
   - Open the `secrets.toml` file and adjust the settings:

     ```toml
     [app]
     name = "YourAppName"  # Name of the application (optional)
     icon = "🤖"  # App icon (optional)

     [llm]
     provider = "openai"  # Options: openai, anthropic, local

     [openai]
     api_key = "YOUR_OPENAI_API_KEY"
     model = "gpt-4o-mini"

     # [anthropic]
     # api_key = "YOUR_ANTHROPIC_API_KEY"
     # model = "claude-3-5-sonnet"

     # [local]
     # base_url = "http://localhost:1234/v1"
     ```

   You can choose between different LLM providers by changing the `provider` key:
   - **OpenAI**: Configure your API key and model in the `[openai]` section.
   - **Anthropic**: If you prefer to use Anthropic, uncomment and configure the `[anthropic]` section.
   - **Local models**: To use local models, uncomment the `[local]` section and set the `base_url` to the server where you have the model running (using tools like [Ollama](https://ollama.com/) or [LM Studio](https://lmstudio.ai/)).

5. **Run the application**:
   Start the application with the following command:
   ```bash
   streamlit run Chat.py
   ```

## Ready to chat with your data!

Once set up, you can access the interface in your browser and start managing connections and making queries in natural language through the chatbot. It’s that simple!

