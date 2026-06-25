from typing import List, Union, Literal
from pydantic import BaseModel, Field, field_validator

class MCQQuestion(BaseModel):
    question: str = Field(..., description="The text of the multiple-choice question.")
    options: List[str] = Field(..., description="A list of 4 options.", min_items=4, max_items=4)
    correct_answer: str = Field(..., description="The correct answer from the options.")

    @field_validator('question', mode="before")
    @classmethod
    def clean_question(cls, value: str) -> str:
        if isinstance(value, dict):
            return value.get("description", str(value))
        return str(value)
    
    
class FillBlankQuestion(BaseModel):
    question: str = Field(..., description="The text of the fill-in-the-blank question with '________'.")
    answer: str = Field(..., description="The correct word or phrase for the blank.")


class MCQQuizSuite(BaseModel):
    questions: List[MCQQuestion] = Field(..., description="A list of multiple-choice questions.")

class FillBlankQuizSuite(BaseModel):
    questions: List[FillBlankQuestion] = Field(..., description="A list of fill-in-the-blank questions.")