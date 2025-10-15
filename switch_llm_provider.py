"""
Easy LLM Provider Switcher for Smart Agent
Just run this script and choose your provider!
"""

import sys

# Provider configurations
PROVIDERS = {
    "1": {
        "name": "Claude-3 Haiku (RECOMMENDED)",
        "cost": "$1.50/month",
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

def print_header():
    print("\n" + "="*80)
    print("  🤖 LLM Provider Switcher for Smart Orchestration Agent")
    print("="*80)

def print_menu():
    print("\n📋 Available Providers:\n")
    for key, provider in PROVIDERS.items():
        print(f"  {key}. {provider['name']:40} Cost: {provider['cost']}")
    print("\n  0. Exit")

def show_instructions(choice):
    if choice not in PROVIDERS:
        print("Invalid choice!")
        return
    
    provider = PROVIDERS[choice]
    
    print("\n" + "="*80)
    print(f"  Switching to: {provider['name']}")
    print("="*80)
    
    print(f"\n📦 STEP 1: Install Package")
    print(f"   {provider['install']}")
    
    print(f"\n🔑 STEP 2: Get API Key")
    print(f"   Visit: {provider['url']}")
    print(f"   Add to .env file: {provider['env']}")
    
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

