import os
from typing import Dict, Any
import json
import logging
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI as genai
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from models.pydantic_validators.pydantic_model import QuestionSet

load_dotenv()

class QuestionGenerator:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_GENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set GOOGLE_GENAI_API_KEY in your .env file.")
        
        self.model = genai(model='gemini-1.5-flash', google_api_key=self.api_key)

        # Load prompts
        self.bloom_prompts = self.load_json("prompts/blooms.json")
        self.question_type_prompts = self.load_json("prompts/question_types.json")
        self.difficulty_prompts = self.load_json("prompts/difficulty.json")


    @staticmethod
    def load_json(file_path):
        """Load and parse a JSON file."""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Error loading JSON file {file_path}: {e}")
            raise  

    def generate_questions(self, text, bloom_level, question_type, num_questions, difficulty_level) -> Dict[str, Any]:
        """Generate questions based on the provided parameters."""

        blooms_taxonomy = self.bloom_prompts[bloom_level]['prompt']
        question_type_prompt = self.question_type_prompts[question_type]['prompt']
        difficulty_prompt = self.difficulty_prompts[difficulty_level]['prompt']

        # Define the prompt template
        prompt_template = """### Based on the following Bloom's Taxonomy, Question Type, and Difficulty Level, generate {num_questions} questions from the given tex.

Important:
- Use the provided Bloom's Taxonomy, Question Type, and Difficulty Level to generate questions.
- Generate questions based on the topics present in the text.
- Generate answers that are accurate and well-supported.
- Generate explanation supporting the answer based on the question.

Additionally:
- The gnerated explanation should be based on the question and answer, not the text.
- Don't generate the same question twice.
- For each question, please ensure it aligns with the specified Bloom's Taxonomy level, question type, and difficulty level.
- If the text is not sufficient to generate the requested number of questions, generate questions based on the topic and context of the text.
- Provide options for multiple-choice questions only.
- Avoid generating questions that are too similar or repetitive.

### Output Format (in JSON):
{{
    "questions": [
        {{
            "question": "(The generated question)",
            "options": [
                "(Option 1)",
                "(Option 2)",
                "(Option 3)",
                "(Option 4)"
            ],
            "answer": "(The correct answer)",
            "explanation": "(A brief explanation for the answer)",
        }},
        ...
    ]
}}

### Bloom's Taxonomy: {bloom_level}
### Question Type: {question_type}
### Difficulty Level: {difficulty_level}
### Text: {text}

"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["bloom_level", "question_type", "difficulty_level", "num_questions", "text"]
        )

        # Set up the Pydantic output parser
        output_parser = PydanticOutputParser(pydantic_object=QuestionSet)
        output_fixing_parser = OutputFixingParser.from_llm(parser=output_parser, llm=self.model)

        # Create the processing chain
        summery_chain = prompt | self.model | output_fixing_parser
        final_output = summery_chain.invoke({
            "bloom_level": blooms_taxonomy,
            "question_type": question_type_prompt,
            "difficulty_level": difficulty_prompt,
            "num_questions": num_questions,
            "text": text
        })

        return final_output.dict()# Convert validated Pydantic model to dictionary

# Example usage
if __name__ == "__main__":
    generator = QuestionGenerator()
    text = "This is a sample text for testing."
    bloom_level = "Remembering"
    question_type = "Multiple Choice"
    num_questions = 5
    difficulty_level = "Easy"


