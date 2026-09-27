import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).
    """
    errors = []

    messages = prompt_data.get("messages")
    if not messages:
        errors.append("Prompt não possui 'messages'.")
        return False, errors

    for i, message in enumerate(messages):
        if "role" not in message:
            errors.append(f"Mensagem {i} sem 'role'.")
        if "content" not in message or not message["content"]:
            errors.append(f"Mensagem {i} sem 'content'.")

    return len(errors) == 0, errors


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).
    """
    client = Client()

    messages = [(m["role"], m["content"]) for m in prompt_data["messages"]]
    prompt = ChatPromptTemplate.from_messages(messages)

    techniques = ["few-shot", "chain-of-thought", "role-prompting"]

    url = client.push_prompt(
        prompt_name,
        object=prompt,
        is_public=True,
        description=(
            "Prompt otimizado para transformar relatos de bugs em User Stories. "
            f"Técnicas utilizadas: {', '.join(techniques)}."
        ),
        tags=techniques
    )

    print(f"Push concluído: {url}")
    return True


def main():
    """Função principal"""
    print_section_header("Push de Prompt Otimizado para o LangSmith Hub")

    check_env_vars(["USERNAME_LANGSMITH_HUB"])
    username = os.getenv("USERNAME_LANGSMITH_HUB")

    prompt_data = load_yaml("prompts/bug_to_user_story_v2.yml")

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt inválido:")
        for error in errors:
            print(f"- {error}")
        return 1

    prompt_name = f"{username}/bug_to_user_story_v2"
    push_prompt_to_langsmith(prompt_name, prompt_data)

    return 0


if __name__ == "__main__":
    sys.exit(main())