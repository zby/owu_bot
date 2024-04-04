import logging

from pprint import pformat, pprint
from dotenv import load_dotenv

from answerbot.prompt_builder import System
from answerbot.prompt_templates import NoExamplesReactPrompt, Reflection, ShortReflection, QUESTION_CHECKS
from answerbot.react import get_answer

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Get a logger for the current module
logger = logging.getLogger(__name__)

# load OpenAI api key
load_dotenv()

if __name__ == "__main__":

    question = "Ile kosztuje ubezpieczenie które pokryłoby koszty leczenia szpitalnego po zachorowaniu na cholerę?"

    config = {
        "chunk_size": 400,
        "prompt_class": 'NERP',
        "reflection": 'None',
        "max_llm_calls": 7,
#        "model": "gpt-3.5-turbo-0613",
        "model": "gpt-4-1106-preview",
        "question_check": 'category_and_amb',
    }

    reactor = get_answer(question, config)
    print(pformat(reactor.prompt.to_messages()))
    pprint(reactor.reflection_errors)
