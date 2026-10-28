import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    DEBUG      = os.getenv('FLASK_ENV') == 'development'

    # Paths
    BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR     = os.path.join(BASE_DIR, 'model')
    ENCODER_PATH  = os.path.join(MODEL_DIR, 'encoder_model.h5')
    DECODER_PATH  = os.path.join(MODEL_DIR, 'decoder_model.h5')
    TOKENIZER_PATH= os.path.join(MODEL_DIR, 'tokenizer.pkl')
    MODEL_CONFIG  = os.path.join(MODEL_DIR, 'model_config.json')
    FALLBACK_CONFIG= os.path.join(MODEL_DIR, 'fallback_config.json')

    # Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # Chatbot
    MAX_OUTPUT_LEN  = 50
    MAX_HISTORY     = 10