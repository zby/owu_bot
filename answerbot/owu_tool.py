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
    def get_documents(cls, directory: str, chunk_length: int) -> Dict[MarkdownDocument]:
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
        Finish the task and return the answer.
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
    def get(self, param: OpenFile):
        """
    Ładuje plik OWU, zachowuje go jako dokument bieżący i pokazuje jego początek.
        """
        document = self.documents_dict(param.filename)
        self.document = document
        sections = document.section_titles()
        sections_list_md = "\n".join(sections)
        observations = ''
        if len(sections) > 0:
            observations = observations + f'Dokument zawiera następujące rozdziały:\n{sections_list_md}\n\n'
        observations = observations + "Dokument zaczyna się:\n" + document.read_chunk() + "\n"
        return observations



if __name__ == "__main__":
    owu_tool = OWUTool('data/OWU')

    file=''
    searchparam = WikipediaSearch.Search(query=query)
    print(scraper.search(searchparam))
    linkparam = WikipediaSearch.FollowLink(link='Rock Chalk,_Jayhawk')
    print(scraper.follow_link(linkparam))
    exit()

#    title = 'Eileen Heckart'
#    getparam = WikipediaSearch.Get(title=title)
#    scraper.get(getparam)
#    if scraper.document:
#        print(f"{title} found\n")
#        pprint(scraper.document.text_to_url)
#
#    exit()
#
#    title = "Lewiston Maineiacs"
#    getparam = WikipediaSearch.Get(title=title)
#    scraper.get(getparam)
#    if scraper.document:
#        print(f"{title} found\n")
#        flink = scraper.FollowLink(link='Androscoggin Bank Colisée')
#        print(scraper.follow_link(flink))
#
#
#
#    exit()
    title = "Shirley Temple"
    title = "Kiss and Tell 1945 film"
    content_record = scraper.wiki_api_search(title)
    if content_record.document:
        print(f"Searching for {title}:\n")
        document = content_record.document
        print(document.read_chunk())
        keyword = 'Shirley Temple'
        print(f'\nLooking up {keyword}:\n')
        print(document.lookup(keyword))
    else:
        print("No document found")

    print('\n')
    print('------------------\n')
    exit()

    title = "Oxygen"
    content_record = scraper.wiki_api_search(title)
    if content_record.document:
        print(f"Searching for {title}:\n")
        document = content_record.document
        print(document.read_chunk())
        print('\nLooking up atomic weight:\n')
        print(document.lookup('atomic weight'))
        print('\nSection titles:\n')
        print(document.section_titles())
        print("\nRetrieval History:")
        for record in content_record.retrieval_history:
            print(record)
    else:
        print("No document found")

    print('\n')
    print('------------------\n')


#    search_query = "Machine learning"
#    search_record = scraper.search(search_query)
#    if search_record.document:
#        print(search_record.document.first_chunk())
#        print("\nRetrieval History:")
#        for record in search_record.retrieval_history:
#            print(record)
#    else:
#        print("No document found")
