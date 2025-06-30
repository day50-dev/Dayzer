import os
import argparse
from openai import OpenAI

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple OpenAI Chat")
    parser.add_argument("endpoint", choices=["local", "openrouter"], 
                       help="Choose endpoint: 'local' for localhost:8080 or 'openrouter' for OpenRouter API")
    args = parser.parse_args()
    
    # Configure client based on endpoint choice
    if args.endpoint == "local":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: Please set the OPENAI_API_KEY environment variable")
            return
        
        client = OpenAI(
            api_key=api_key,
            base_url="http://localhost:8080"
        )
        print("Using local server at localhost:8080")
        
    elif args.endpoint == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: Please set the OPENROUTER_API_KEY environment variable")
            return
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        print("Using OpenRouter API")
    
    print("Simple OpenAI Chat (type 'quit' or 'exit' to end)")
    print("-" * 50)
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Send to OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}]
            )
            
            # Print assistant response
            assistant_message = response.choices[0].message.content
            print(f"Assistant: {assistant_message}")
            print()  # Add blank line for readability
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
