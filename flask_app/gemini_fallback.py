import logging
from google import genai
from .config import Config

logger = logging.getLogger(__name__)

class GeminiFallback:

    def __init__(self):
        self._initialized = False
        self.client       = None
        self.model        = None
        self.system_prompt = None

    def initialize(self, gemini_model, system_prompt):
        if self._initialized:
            return
        if not Config.GEMINI_API_KEY:
            logger.warning('GEMINI_API_KEY tidak ditemukan!')
            return
        try:
            self.client       = genai.Client(api_key=Config.GEMINI_API_KEY)
            self.model        = gemini_model
            self.system_prompt = system_prompt
            self._initialized = True
            logger.info(f'Gemini initialized. Model: {gemini_model}')
        except Exception as e:
            logger.error(f'Gemini init failed: {e}')

    def get_response(self, user_input, history=None):
        '''
        Panggil Gemini API.
        history: list of dict {role, parts}
        Returns: (response_text, success_bool)
        '''
        if not self._initialized or not self.client:
            return 'Saya memahami perasaanmu. Pertimbangkan untuk berbicara dengan profesional kesehatan mental.', False

        try:
            messages = []

            # Tambahkan history
            if history:
                for turn in history:
                    messages.append(turn)

            # Tambahkan pesan user
            full_prompt = f"{self.system_prompt}\n\nUser: {user_input}"
            messages.append({
                'role'  : 'user',
                'parts' : [{'text': full_prompt}]
            })

            response = self.client.models.generate_content(
                model    = self.model,
                contents = messages,
            )
            return response.text.strip(), True

        except Exception as e:
            logger.error(f'Gemini error: {e}')
            return 'Saya memahami perasaanmu. Pertimbangkan untuk berbicara dengan profesional kesehatan mental.', False


# Singleton instance
gemini_fallback = GeminiFallback()