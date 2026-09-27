"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_full_text(prompt_data: dict) -> str:
    """Concatena o conteúdo de todas as mensagens do prompt em um único texto."""
    messages = prompt_data.get("messages", [])
    return "\n".join(m.get("content", "") for m in messages)

def get_system_content(prompt_data: dict) -> str:
    """Retorna o conteúdo da mensagem de role 'system' (ou vazio se não existir)."""
    for message in prompt_data.get("messages", []):
        if message.get("role") == "system":
            return message.get("content", "") or ""
    return ""

class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo existe e não está vazio."""
        prompt_data = load_prompts(PROMPT_PATH)
        system_content = get_system_content(prompt_data)

        assert system_content, "Prompt não possui mensagem de sistema (role: system) ou ela está vazia."
        assert len(system_content.strip()) > 0

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = load_prompts(PROMPT_PATH)
        system_content = get_system_content(prompt_data).lower()

        role_markers = [
            "você é um",
            "você é uma",
            "you are a",
            "you are an",
            "atue como",
            "act as",
        ]

        assert any(marker in system_content for marker in role_markers), (
            "Nenhuma definição de persona/role encontrada no prompt de sistema "
            "(esperado algo como 'Você é um...')."
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = load_prompts(PROMPT_PATH)
        full_text = get_full_text(prompt_data).lower()

        format_markers = [
            "markdown",
            "user story",
            "como:",
            "eu quero:",
            "para que:",
            "título:",
        ]

        assert any(marker in full_text for marker in format_markers), (
            "Prompt não menciona explicitamente um formato de saída "
            "(Markdown ou estrutura de User Story)."
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = load_prompts(PROMPT_PATH)
        full_text = get_full_text(prompt_data).lower()

        example_markers = [
            "exemplo 1",
            "exemplo 2",
            "example 1",
            "example 2",
        ]

        found_markers = [marker for marker in example_markers if marker in full_text]

        assert len(found_markers) >= 2, (
            "Prompt não contém pelo menos dois exemplos de entrada/saída "
            "(esperado 'Exemplo 1', 'Exemplo 2', etc.)."
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_data = load_prompts(PROMPT_PATH)
        full_text = get_full_text(prompt_data)

        todo_markers = ["[TODO]", "[todo]", "TODO:", "FIXME"]

        found = [marker for marker in todo_markers if marker in full_text]

        assert not found, f"Foram encontrados marcadores pendentes no prompt: {found}"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = load_prompts(PROMPT_PATH)
        metadata = prompt_data.get("metadata", {})
        techniques = metadata.get("techniques", [])

        assert isinstance(techniques, list), "Campo 'metadata.techniques' deve ser uma lista."
        assert len(techniques) >= 2, (
            f"Esperado pelo menos 2 técnicas listadas em metadata.techniques, "
            f"encontrado: {techniques}"
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])