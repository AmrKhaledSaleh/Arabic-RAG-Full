import hashlib
import logging
import requests
from .config import AppConfig 
import streamlit as st
import uuid
from datetime import datetime  # Import datetime module
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Get the logger instance
logger = logging.getLogger(__name__)

def setup_logging():
    """
    Configures basic logging for the application.
    """
    logging.basicConfig(level=logging.INFO)
    
    # Configure Cloudinary
    config = AppConfig()
    cloudinary.config(
        cloud_name=config.CLOUDINARY_CLOUD_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True
    )

def get_file_hash(file_content):
    """
    Calculates the MD5 hash of the given file content.
    """
    return hashlib.md5(file_content).hexdigest()

def upload_image_to_fileio(file_path):
    """
    Uploads an image to Cloudinary and returns a URL to access the image.
    """
    try:
        upload_result = cloudinary.uploader.upload(file_path)
        image_url = upload_result.get("secure_url")
        if image_url:
            logger.info(f"Image successfully uploaded. URL: {image_url}")
        else:
            logger.error("Failed to upload image to Cloudinary")
        return image_url
    except Exception as e:
        logger.error(f"An error occurred while uploading to Cloudinary: {e}")
        return None

def extract_text_from_image_url(image_url):
    """
    Extracts and cleans text from an image URL using the Zyla OCR API.
    """
    
    config = AppConfig()
    # api_url = f"https://zylalabs.com/api/37/optical+character+recognition+api/108/image+analysis?url={image_url}"
    # api_url = f"https://zylalabs.com/api/5060/text+extractor+api/6431/text+from+image+url?url={image_url}" #backup_OCR
    api_url = f"https://zylalabs.com/api/2319/ocr+api/2227/ocr?url={image_url}" #backup_OCR_2
    headers = {
        'Authorization': f'Bearer {config.ZYLA_API_KEY}'
    }

    try:
        # response = requests.post(api_url, headers=headers)
        response = requests.request("GET", api_url, headers=headers) #backup_OCR
        response.raise_for_status()
        data = response.json()
        
        # text = data.get('results', [])[0].get('entities', [])[0].get('objects', [])[0].get('entities', [])[0].get('text', "")
        # text = data.get('data text', "") #backup_OCR
        text = data.get('body', {}).get('fullText', "")
        cleaned_text = '\n'.join(line.strip() for line in text.split('\n')) #backup_OCR_2

        return cleaned_text

    except Exception as e:
        logger.error(f"An error occurred while extracting text from image URL: {e}")
        return ""

def generate_session_id():
    """Generate a unique session ID with the current date and time"""
    if 'session_id' not in st.session_state:
        session_id = str(uuid.uuid4())
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # Get current date and time
        st.session_state.session_id = f"{current_time}_{session_id}"  # Format session ID
    return st.session_state.session_id