import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import argparse

def main():
    parser = argparse.ArgumentParser(description="Send a prompt to Gemini.")
    parser.add_argument("prompt", nargs="+", help="The text prompt to send to Gemini.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    # Combine all prompt words into a single string
    user_prompt = " ".join(args.prompt)

    # Prepare messages for Gemini
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        sys.exit(1)

    if args.verbose:
        print("[DEBUG] Initializing Gemini client...")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )

    if args.verbose:
        print("User prompt: {user_prompt}")
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)
    print(response.text)


if __name__ == "__main__":
    main()
