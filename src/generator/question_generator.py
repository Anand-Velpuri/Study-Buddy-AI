from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQQuizSuite, FillBlankQuizSuite
from src.prompts.templates import mcq_suite_prompt_template, fill_blank_suite_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)
    
    def _retry_and_parse(self, prompt, parser, topic, difficulty, num_questions):
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic: {topic}, difficulty: {difficulty}, attempt: {attempt + 1}")
                response = self.llm.invoke(prompt.format(topic=topic, difficulty=difficulty, num_questions=num_questions))
                parsed = parser.parse(response.content)
                self.logger.info(f"Successfully generated question on attempt {attempt + 1}")
                return parsed
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(f"Failed to generate question after {settings.MAX_RETRIES} attempts.")
                
    
    def generate_questions_suite(self, topic: str, question_type: str, difficulty: str = "medium", num_questions: int = 5):
        try:
            if question_type == "Multiple Choice":
                parser = PydanticOutputParser(pydantic_object=MCQQuizSuite)
                prompt = mcq_suite_prompt_template
            else:
                parser = PydanticOutputParser(pydantic_object=FillBlankQuizSuite)
                prompt = fill_blank_suite_prompt_template

            quiz_suite = self._retry_and_parse(prompt, parser, topic, difficulty, num_questions)

            # Extra validation just for MCQs
            if question_type == "Multiple Choice":
                for q in quiz_suite.questions:
                    if len(q.options) != 4 or q.correct_answer not in q.options:
                        raise CustomException("A generated MCQ has invalid options.")
            
            self.logger.info(f"Generated a valid {question_type} suite for topic: {topic}")
            return quiz_suite
            
        except Exception as e:
            self.logger.error(f"Error generating {question_type} Suite: {e}")
            raise CustomException(f"Error generating {question_type} Suite: {e}")