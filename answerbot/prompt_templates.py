from string import Template
from pydantic import BaseModel, Field

from .prompt_builder import FunctionalPrompt, System, User


class Question(User):
    def plaintext(self) -> str:
        return '\nQuestion: ' + self.content
    def openai_message(self) -> dict:
        return { "role": "user", "content": 'Question: ' + self.content }

class NoExamplesReactPrompt(FunctionalPrompt):
    def __init__(self, question, file_list, max_llm_calls, reflection_class):
        if reflection_class is not None:
            prefix = reflection_class.__name__.lower() + "_and_"
        else:
            prefix = ''
        system_prompt = \
f"""
Proszę odpowiedz na poniższe pytanie od użytkownika.
Przy odpowiadaniu proszę używaj dokumentacji zawartej w plikach w formacie Markdown.
{file_list}
Musisz sformułować odpowiedź po {max_llm_calls - 1} krokach.
Przy każdym odczycie dostaniesz tylko fragment danego pliku - ale możesz przeczytać
inne jego fragmenty używając odpowiednich poleceń.
Do odczytywania dokumetacji używaj następujących funkcji:
- `{prefix}open_file` z parametrem nazwa pliku
- `{prefix}lookup` do wyszukiwania frazy będącej parametrem
- `{prefix}next` do przeskoczenia do następnego wystąpienia wyszukiwanej frazy
- `{prefix}read_chunk` do przeczytania następnego fragmentu tekstu
Na zakończenie proszę wywołaj funkcję `finish` z odpowiednimi parametrami.
Przy wyszukiwaniu fraz najlepiej używać pojedyńczych słów - bo więcej niż dwa słowa mogą w tekście
pojawić się w różnej kolejności - albo słowa mogą byc czymś przedzielone, wyszukiwanie
działa bardzo dosłownie.
"""
        #question_analysis =  "Think about ways in which the question might be ambiguous. How could it be made more precise? Can you guess the answer without consulting wikipedia? Think step by step."
        super().__init__([ System(system_prompt), Question(question) ])

PROMPTS = {
    'NERP': NoExamplesReactPrompt
}

QUESTION_CHECKS = {
    "category_and_amb": ["Jakiego rodzaju pytanie masz? Czy to pytanie TAK/NIE? Jaka powinna być odpowiedź na pytanie?", "Pomyśl o sposobach, w jakie pytanie może być dwuznaczne. Jak można je uczynić bardziej precyzyjnym?"],
    "None": [],
    "amb":  ["Pomyśl o sposobach, w jakie pytanie może być dwuznaczne. Jak można je uczynić bardziej precyzyjnym?"],
    "amb_and_plan": ["Pomyśl o sposobach, w jakie pytanie może być dwuznaczne. Jak można je uczynić bardziej precyzyjnym?", "Pomyśl, jakie informacje musisz uzyskać z Wikipedii, aby na nie odpowiedzieć. Myśl krok po kroku"],
    "category": ["Jakiego rodzaju pytanie masz? Czy to pytanie TAK/NIE? Jaka powinna być odpowiedź na pytanie?"],
}

class Reflection(BaseModel):
    how_relevant: int = Field(
        ...,
        description="Czy ostatnio pozyskane informacje były istotne dla odpowiedzi na to pytanie? Wybierz 1, 2, 3, 4 lub 5. Jeśli jeszcze nie pozyskano informacji, proszę wybrać 0"
    )
    why_relevant: str = Field(..., description="Dlaczego pozyskane informacje były istotne? Jeśli jeszcze nie pozyskano informacji, proszę odpowiedzieć pustym ciągiem znaków")
    next_actions_plan: str = Field(..., description="")

class ShortReflection(BaseModel):
    reflection: str = Field(..., description="Zastanów się nad dotychczas zebranymi informacjami. Czy ostatnio pozyskane informacje były istotne dla odpowiedzi na pytanie? Jakich dodatkowych informacji potrzebujesz, dlaczego i jak możesz je zdobyć? Myśl krok po kroku")

REFLECTIONS = {
    'None': {},
    'Reflection': { "class": Reflection },
    'ShortReflection': { "class": ShortReflection },
    'separate': { "message": "Zastanów się nad dotychczas zebranymi informacjami. Czy ostatnio pozyskane informacje były istotne dla odpowiedzi na pytanie? Jakich dodatkowych informacji potrzebujesz, dlaczego i jak możesz je zdobyć?" },
    'separate_cot': { "message": "Zastanów się nad dotychczas zebranymi informacjami. Czy ostatnio pozyskane informacje były istotne dla odpowiedzi na pytanie? Jakich dodatkowych informacji potrzebujesz, dlaczego i jak możesz je zdobyć? Myśl krok po kroku"}
}

