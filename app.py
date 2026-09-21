from flask import Flask, render_template, request, jsonify
from utils.text_extraction import (
    extract_text_from_pdf,
    scrape_education_content,
    extract_text_from_image_file
)
import json
from models.langchain_gemini_model import QuestionGenerator       
import os
import logging
from flask_cors import CORS
import asyncio


app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    'http://localhost:5173',  # Local development
    'https://question-generator-3x5s.onrender.com',  # Hosted frontend
    'https://t-qgen.vercel.app/'
])

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the question generator
question_generator = QuestionGenerator()

# Initialize the Flask app
@app.route('/')
def index():
    return render_template('index.html',
                           bloom_levels=question_generator.bloom_prompts.keys(),
                           question_types=question_generator.question_type_prompts.keys(),
                           difficulty_levels=question_generator.difficulty_prompts.keys())

@app.route('/generate', methods=['POST'])
def generate():
    try:

        # Get form data
        bloom_level = request.form['bloom_level']
        question_type = request.form['question_type']
        difficulty_level = request.form['difficulty_level']
        num_questions = int(request.form['num_questions'])
        # Get text from input method
        data = request.form.to_dict()
        text = ""
        
        # Check each input method
        if 'pdfFile' in request.files and request.files['pdfFile'].filename:
            text = extract_text_from_pdf(request.files['pdfFile'])
        elif 'imageFile' in request.files and request.files['imageFile'].filename:
            text = extract_text_from_image_file(request.files['imageFile'])
        elif data.get('imageUrl'):
            text = asyncio.run(scrape_education_content(data['imageUrl']))
        elif data.get('context'):
            text = data['context']
        
        if not text.strip():
            return jsonify({'error': 'No text could be extracted from the input'})
        
       # Generate questions using the QuestionGenerator
        result_questions = question_generator.generate_questions(
            text,
            bloom_level,
            question_type,
            num_questions,
            difficulty_level
        )  
        # Return the questions as JSON
        logging.info(f"from main Generated {result_questions} questions.")
        return jsonify(result_questions)  # Use jsonify here to return JSON properly
    
    except Exception as e:
        print(f"Error in generate endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

