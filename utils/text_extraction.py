import PyPDF2
from PIL import Image
import pytesseract
import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler
from utils.web_scrap_processing import process_scraped_data

# Load environment variables
load_dotenv()

async def scrape_education_content(url):
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url)
        markdown_text = result.markdown
        
        # Process the scraped data
        processed_text = process_scraped_data(markdown_text)
        
        return str(processed_text)


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_image_file(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img)

if __name__ == "__main__":
    # Test the functions
    text = scrape_education_content("https://www.learncbse.in/chemical-reactions-and-equations-chapter-wise-important-questions-class-10-science/")
    print(text)