import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

client = Client()

def pull_prompts_from_langsmith():
    promptName = "leonanluppi/bug_to_user_story_v1"

    promptResponse = client.pull_prompt(
        promptName,
    )

    print(promptResponse)

    return promptResponse

def main():
    """Função principal"""
    response = pull_prompts_from_langsmith()

    data = {
        "messages": [
            {
                "content": message.prompt.template,
            }
            for message in response.messages
        ]
    }

    output_path = Path("prompts/bug_to_user_story_v1.yml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_yaml(data, output_path)

    print(f"Prompt salvo em: {output_path}")


if __name__ == "__main__":
    sys.exit(main())