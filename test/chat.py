#!/usr/bin/env python3
import logging
import os
import sys
import argparse
from openai import OpenAI

# Parse command line arguments
parser = argparse.ArgumentParser(description="Simple OpenAI Chat")
parser.add_argument("endpoint", choices=["dayzer", "local", "openrouter"], 
                   help="Choose endpoint: 'local' for localhost:8000 or 'openrouter' for OpenRouter API")
parser.add_argument("--address", action="store", default="localhost:8000/v1",
                   help="hostname")
parser.add_argument("--stream", action="store_true", 
                   help="Enable streaming responses")
parser.add_argument("--stdin", action="store_true", 
                   help="Enable streaming responses")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

args = parser.parse_args()
logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
logger = logging.getLogger(__name__)

message = None
if args.stdin:
    message = sys.stdin.read()
    print(f"Using stdin: size {len(message)}")

if args.endpoint == "local":
    client = OpenAI(
        api_key="sk-123",
        base_url=f"http://{args.address}"
    )
    model = "google/gemini-2.0-flash-exp:free"
    print("Using local server at localhost:8000")

# Configure client based on endpoint choice
if args.endpoint == "dayzer":
    client = OpenAI(
        api_key="sk-123",
        base_url=f"http://{args.address}"
    )
    model = "google/gemini-2.0-flash-exp:free"
    print(f"Using local server at {args.address}")
    
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
        if message:
            user_input = message
        else:
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
                logging.debug(chunk)
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()  # Add newline after streaming
        else:
            # Print assistant response
            assistant_message = response.choices[0].message.content
            print(f"Assistant: {assistant_message}")
            print()  # Add blank line for readability

        if message:
            sys.exit(0)
        
    except Exception as e:
        print(e)
        break
