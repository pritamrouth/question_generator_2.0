from pydantic import BaseModel, Field
from typing import Optional,List
     
class Question(BaseModel):
    question: Optional[str] = Field(default=None, description="The Genrated question text")
    options: Optional[list] = Field(default=None, description="The Genrated option text")  # List of 4 options
    answer: Optional[str] = Field(default=None, description="The Genrated answer text")
    explanation: Optional[str] = Field(default=None, description="The Genrated explaination of the correct answer") # Ensures the explanation is not empty

class QuestionSet(BaseModel):
    questions: List[Question] = Field(default=None, description="The Genrated question text")