"""
Smart Orchestration Agent using Anthropic Claude
Much cheaper and faster than GPT!
"""

# Change imports
from langchain_anthropic import ChatAnthropic  # Instead of ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent  # Still works!

# ... rest of imports same ...

class SmartOrchestrationAgent:
    def __init__(self):
        """Initialize the agent with Claude"""
        
        # Use Claude instead of GPT!
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",  # Cheapest, fastest Claude
            temperature=0.1,
            anthropic_api_key=settings.ANTHROPIC_API_KEY  # Need to add this to .env
        )
        
        # Alternative models:
        # model="claude-3-sonnet-20240229"  # More intelligent
        # model="claude-3-opus-20240229"    # Most intelligent
        
        # Rest of code stays THE SAME!
        # Agent creation, tools, everything else identical

