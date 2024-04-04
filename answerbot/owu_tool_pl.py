import requests
import html2text
import traceback
import os
import time

from pprint import pprint

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, NavigableString

from answerbot.document import MarkdownDocument
from llm_easy_tools import external_function, extraction_model
from urllib.parse import urlparse, urljoin

CHUNK_SIZE = 1024

class OWUTool:
    def __init__(self, directory, chunk_size=CHUNK_SIZE, documents_dict=None, current_document=None):
        self.directory = directory
        if documents_dict is None:
            self.documents_dict = self.get_documents(directory, chunk_size)
        else:
            self.documents_dict = documents_dict
        self.current_document = current_document

    @classmethod
    def get_documents(cls, directory: str, chunk_length: int) -> Dict[str, MarkdownDocument]:
        documents = {}

        # Iterate over files in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                file_path = os.path.join(directory, filename)

                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Create a MarkdownDocument object with chunked content
                document = MarkdownDocument(content, chunk_size=chunk_length)
                documents[filename] = document

        return documents

    def show_documents(self):
        observations = 'Mamy następujące dokumenty:\n'
        for filename in self.documents_dict:
            observations += filename + '\n'

        return observations


    @extraction_model()
    class Finish(BaseModel):
        """
        Zakończ zadanie i zwróć odpowiedź.
        """
        answer: str = Field(description="Krótka odpowiedź na pytanie użytkownika")
        answer_short: str = Field(description="Jeszcze krótsza wersja odpowiedzi")
        reasoning: str = Field(description="Uzasadnienie odpowiedzi. Krok za krokiem. Proszę wymień tutaj wszystkie założenia.")
#        ambiguity: Optional[str] = Field(description="Have you found anything in the retrieved information that makes the question ambiguous? For example a search for some name can show that there are many different entities with the same name.")

        def normalize_answer(self, answer):
            answer = answer.strip(' \n.\'"')
            answer = answer.replace('’', "'")  # Replace all curly apostrophes with straight single quotes
            answer = answer.replace('"', "'")  # Replace all double quotes with straight single quotes
            if answer.lower() == 'yes' or answer.lower() == 'no':
                answer = answer.lower()
            return answer

        def normalized_answer(self):
            return (
                self.normalize_answer(self.answer),
                self.normalize_answer(self.answer_short),
            )

    class OpenFile(BaseModel):
        filename: str = Field(description="Nazwa pliku OWU")
#    @external_function()
    def open_file(self, param: OpenFile):
        """
    Ładuje plik OWU, zachowuje go jako dokument bieżący i pokazuje jego początek.
        """
        document = self.documents_dict[param.filename]
        self.document = document
        sections = document.section_titles()
        sections_list_md = "\n".join(sections)
        observations = ''
        if len(sections) > 0:
            observations = observations + f'Dokument zawiera następujące rozdziały:\n{sections_list_md}\n\n'
        observations = observations + "Dokument zaczyna się:\n" + document.read_chunk() + "\n"
        return observations

    class Lookup(BaseModel):
        keyword: str = Field(description="Fraza do wyszukania")
    @external_function()
    def lookup(self, param: Lookup):
        """
Wyszukuje słowo na bieżącej stronie.
        """
        if self.document is None:
            observations = "No document defined, cannot lookup"
        else:
            text = self.document.lookup(param.keyword)
            observations = 'Wyszukiwana fraza "' + param.keyword + '" '
            if text:
                num_of_results = len(self.document.lookup_results)
                observations = observations + f"znaleziona w bieżącym dokumencie w {num_of_results} miejscach. Pierwsze wystąpienie:\n" + text
            else:
                observations = observations + "nie została znaleziona w bieżącym dokumencie"
        return observations

    class Next_Lookup(BaseModel):
        pass

    @external_function('next')
    def next_lookup(self, param: Next_Lookup):
        """
Skacze do następnego wystąpienia wyszukanego słowa.
        """
        if self.document is None:
            observations = "Nie ma bieżącego dokumentu i nie można w nim nic wyszukać"
        elif not self.document.lookup_results:
            observations = "Ostatnio wyszukiwana fraza nie została znaleziona w bieżącym dokumencie"
        else:
            text = self.document.next_lookup()
            observations = 'Fraza "' + self.document.lookup_word + '" znaleziona w: \n' + text
            num_of_results = len(self.document.lookup_results)
            observations = observations + f"\n{self.document.lookup_position} of {num_of_results} places"
        return observations

    class ReadChunk(BaseModel):
        pass

    @external_function()
    def read_chunk(self, param: ReadChunk):
        """
Wczytuje następny fragment tekstu zaczynając od miejsca gdzie skończył się ostatni fragment w bieżącym dokumencie.
        """
        if self.document is None:
            observations = "Nie bieżącego dokumentu"
        else:
            observations = self.document.read_chunk()
        return observations


if __name__ == "__main__":
    owu_tool = OWUTool('data/OWU')
    print(owu_tool.show_documents())

    file='Ogolne_warunki_dodatkowego_indywidualnego_ubezpieczenia_na_wypadek_ciezkich_chorob_obowiaz.md'
    param = OWUTool.OpenFile(filename=file)
    print(owu_tool.open_file(param))

