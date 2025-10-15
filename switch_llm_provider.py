"""
Easy LLM Provider Switcher for Smart Agent
Just run this script and choose your provider!
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Provider configurations
PROVIDERS = {
    "1": {
        "name": "Claude-3 Haiku (RECOMMENDED)",
        "cost": "$1.50/month",
        "env_var": "ANTHROPIC_API_KEY",
        "import": "from langchain_anthropic import ChatAnthropic",
        "code": '''self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.1,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )''',
        "install": "pip install langchain-anthropic",
        "env": "ANTHROPIC_API_KEY=your-key-from-console.anthropic.com",
        "url": "https://console.anthropic.com/"
    },
    "2": {
        "name": "GPT-3.5-Turbo (Current)",
        "cost": "$3-6/month",
        "env_var": "OPENAI_API_KEY",
        "import": "from langchain_openai import ChatOpenAI",
        "code": '''self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY
        )''',
        "install": "pip install langchain-openai",
        "env": "OPENAI_API_KEY=your-key-from-platform.openai.com",
        "url": "https://platform.openai.com/"
    },
    "3": {
        "name": "Gemini 1.5 Flash",
        "cost": "$2/month",
        "env_var": "GOOGLE_API_KEY",
        "import": "from langchain_google_genai import ChatGoogleGenerativeAI",
        "code": '''self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=settings.GOOGLE_API_KEY
        )''',
        "install": "pip install langchain-google-genai",
        "env": "GOOGLE_API_KEY=your-key-from-makersuite.google.com",
        "url": "https://makersuite.google.com/app/apikey"
    },
    "4": {
        "name": "Claude-3 Sonnet (More Intelligent)",
        "cost": "$18-30/month",
        "env_var": "ANTHROPIC_API_KEY",
        "import": "from langchain_anthropic import ChatAnthropic",
        "code": '''self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.1,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )''',
        "install": "pip install langchain-anthropic",
        "env": "ANTHROPIC_API_KEY=your-key-from-console.anthropic.com",
        "url": "https://console.anthropic.com/"
    },
    "5": {
        "name": "GPT-4-Turbo (Most Expensive)",
        "cost": "$60-120/month",
        "env_var": "OPENAI_API_KEY",
        "import": "from langchain_openai import ChatOpenAI",
        "code": '''self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY
        )''',
        "install": "pip install langchain-openai",
        "env": "OPENAI_API_KEY=your-key-from-platform.openai.com",
        "url": "https://platform.openai.com/"
    }
}

def check_available_keys():
    """Check which API keys are configured in .env"""
    available_keys = {}
    
    # Check each key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    available_keys["ANTHROPIC_API_KEY"] = bool(anthropic_key and anthropic_key.strip())
    available_keys["OPENAI_API_KEY"] = bool(openai_key and openai_key.strip())
    available_keys["GOOGLE_API_KEY"] = bool(google_key and google_key.strip())
    
    return available_keys


def print_header():
    print("\n" + "="*80)
    print("  🤖 LLM Provider Switcher for Smart Orchestration Agent")
    print("="*80)
    
    # Show configured keys
    available = check_available_keys()
    
    print("\n🔑 Your Configured API Keys:")
    for key, is_set in available.items():
        status = "✅ SET" if is_set else "❌ NOT SET"
        print(f"   {key}: {status}")
    
    if available["ANTHROPIC_API_KEY"]:
        print("\n🎉 Great! You have Anthropic key - Claude is READY to use!")
    elif available["OPENAI_API_KEY"]:
        print("\n✅ You have OpenAI key - GPT models available")
    else:
        print("\n⚠️  No AI provider keys found - you'll need to set one up")

def print_menu():
    print("\n📋 Available Providers:\n")
    
    available = check_available_keys()
    
    for key, provider in PROVIDERS.items():
        # Check if this provider's key is configured
        env_var = provider.get("env_var")
        is_ready = available.get(env_var, False) if env_var else False
        
        status = "✅ READY" if is_ready else "⚠️  Need API key"
        print(f"  {key}. {provider['name']:40} Cost: {provider['cost']:15} {status}")
    
    print("\n  0. Exit")

def show_instructions(choice):
    if choice not in PROVIDERS:
        print("Invalid choice!")
        return
    
    provider = PROVIDERS[choice]
    available = check_available_keys()
    
    env_var = provider.get("env_var")
    has_key = available.get(env_var, False) if env_var else False
    
    print("\n" + "="*80)
    print(f"  Switching to: {provider['name']}")
    print("="*80)
    
    # Check if key is already configured
    if has_key:
        print(f"\n✅ GREAT NEWS: {env_var} is already configured in your .env!")
        print(f"   You can use this provider immediately!")
    else:
        print(f"\n⚠️  {env_var} is NOT configured yet.")
    
    print(f"\n📦 STEP 1: Install Package")
    print(f"   {provider['install']}")
    
    if not has_key:
        print(f"\n🔑 STEP 2: Get API Key (REQUIRED)")
        print(f"   Visit: {provider['url']}")
        print(f"   Add to .env file: {provider['env']}")
    else:
        print(f"\n🔑 STEP 2: API Key")
        print(f"   ✅ ALREADY CONFIGURED - Skip this step!")
    
    print(f"\n💻 STEP 3: Update Code")
    print(f"\n   In app/agents/smart_orchestration_agent.py:")
    print(f"   Line ~20: Change import to:")
    print(f"   {provider['import']}")
    print(f"\n   Line ~392: Change LLM initialization to:")
    print(f"   {provider['code']}")
    
    print(f"\n🔄 STEP 4: Restart Backend")
    print(f"   python -m uvicorn app.main:app --reload")
    
    print("\n" + "="*80)
    print("✅ Done! Your agent will now use this provider.")
    print("="*80)
    
    # Offer to show the exact file locations
    print("\n📝 Want to see exact code changes? [y/n]: ", end="")
    if input().lower() == 'y':
        print(f"\n{'='*80}")
        print("EXACT CHANGES NEEDED:")
        print(f"{'='*80}")
        print(f"\nFile: app/agents/smart_orchestration_agent.py")
        print(f"\n# CHANGE THIS (around line 20):")
        print(f"# OLD: from langchain_openai import ChatOpenAI")
        print(f"# NEW: {provider['import']}")
        print(f"\n# CHANGE THIS (around line 392):")
        print(f"# OLD:")
        print('''self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY
        )''')
        print(f"\n# NEW:")
        print(provider['code'])
        print(f"\n{'='*80}")

def main():
    print_header()
    
    print("\n💡 RECOMMENDATION: Choose option 1 (Claude-3 Haiku)")
    print("   - Cheapest ($1.50/month vs $3-6/month)")
    print("   - Fastest responses")
    print("   - Best function calling")
    print("   - More intelligent")
    
    while True:
        print_menu()
        print("\nEnter your choice: ", end="")
        
        choice = input().strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        if choice in PROVIDERS:
            show_instructions(choice)
            
            print("\n\nSwitch to another provider? [y/n]: ", end="")
            if input().lower() != 'y':
                print("\n✅ All done! Happy coding! 🚀\n")
                break
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user. Goodbye!")
        sys.exit(0)

