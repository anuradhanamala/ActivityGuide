"""
Smart Orchestration Agent using Google Gemini
Very fast and very cheap!
"""

# Change imports
from langchain_google_genai import ChatGoogleGenerativeAI  # Instead of ChatOpenAI

# ... rest of imports same ...

class SmartOrchestrationAgent:
    def __init__(self):
        """Initialize the agent with Gemini"""
        
        # Use Gemini instead of GPT!
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Fastest, cheapest
            temperature=0.1,
            google_api_key=settings.GOOGLE_API_KEY  # Need to add this to .env
        )
        
        # Alternative models:
        # model="gemini-1.5-pro"    # More intelligent
        # model="gemini-pro"        # Standard model
        
        # Rest of code stays THE SAME!

