#!/usr/bin/env python3
import os
import argparse
from openai import OpenAI

# Parse command line arguments
parser = argparse.ArgumentParser(description="Simple OpenAI Chat")
parser.add_argument("endpoint", choices=["dayzer", "local", "openrouter"], 
                   help="Choose endpoint: 'local' for localhost:8000 or 'openrouter' for OpenRouter API")
parser.add_argument("--stream", action="store_true", 
                   help="Enable streaming responses")
args = parser.parse_args()

if args.endpoint == "local":
    client = OpenAI(
        api_key="sk-123",
        base_url="http://localhost:8080/v1"
    )
    model = "google/gemini-2.0-flash-exp:free"
    print("Using local server at localhost:8000")

# Configure client based on endpoint choice
if args.endpoint == "dayzer":
    client = OpenAI(
        api_key="sk-123",
        base_url="http://localhost:8000/v1"
    )
    model = "google/gemini-2.0-flash-exp:free"
    print("Using local server at localhost:8000")
    
elif args.endpoint == "openrouter":
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: Please set the OPENROUTER_API_KEY environment variable")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    model = "google/gemini-2.0-flash-exp:free"
    print("Using OpenRouter API with Gemini 2.0 Flash")

while True:
    try:
        user_input = input("You: ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Skip empty input
        if not user_input:
            continue
        
        stream = args.stream
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            stream=stream
        )

        # Handle streaming responses
        if stream:
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()  # Add newline after streaming
        else:
            # Print assistant response
            assistant_message = response.choices[0].message.content
            print(f"Assistant: {assistant_message}")
            print()  # Add blank line for readability
        
    except Exception as e:
        print(e)
        break
