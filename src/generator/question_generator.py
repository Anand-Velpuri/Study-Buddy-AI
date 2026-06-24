from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.templates import mcq_prompt_template, fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)
    
    def _retry_and_parse(self, prompt, parser, topic, difficulty):
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic: {topic}, difficulty: {difficulty}, attempt: {attempt + 1}")
                response = self.llm.invoke(prompt.format(topic=topic, difficulty=difficulty))
                parsed = parser.parse(response.content)
                self.logger.info(f"Successfully generated question on attempt {attempt + 1}")
                return parsed
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(f"Failed to generate question after {settings.MAX_RETRIES} attempts.")
                
    
    def generate_mcq(self, topic: str, difficulty: str = "medium") -> MCQQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)
            question = self._retry_and_parse(mcq_prompt_template, parser, topic, difficulty)

            if len(question.options) != 4 or question.answer not in question.options:
                raise CustomException("Generated MCQ does not have exactly 4 options or the answer is not among the options.")
            
            self.logger.info(f"Generated a valid MCQ question for topic: {topic}, difficulty: {difficulty}")
            return question
        except Exception as e:
            self.logger.error(f"Error generating MCQ question: {e}")
            raise CustomException(f"Error generating MCQ question: {e}")

    def generate_fill_blank(self, topic: str, difficulty: str = "medium") -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)
            question = self._retry_and_parse(fill_blank_prompt_template, parser, topic, difficulty)

            self.logger.info(f"Generated a valid fill-in-the-blank question for topic: {topic}, difficulty: {difficulty}")
            return question
        except Exception as e:
            self.logger.error(f"Error generating fill-in-the-blank question: {e}")
            raise CustomException(f"Error generating fill-in-the-blank question: {e}")

