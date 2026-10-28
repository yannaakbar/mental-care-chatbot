import numpy as np
import pickle, json, re, logging
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from .config import Config

logger = logging.getLogger(__name__)

class ChatbotEngine:

    def __init__(self):
        self._loaded  = False
        self.encoder  = None
        self.decoder  = None
        self.tokenizer = None
        self.config   = None
        self.idx2word = None
        self.CONFIDENCE_THRESHOLD = None
        self.MIN_RESPONSE_WORDS   = None
        self.GEMINI_MODEL         = None
        self.SYSTEM_PROMPT        = None

    def load(self):
        if self._loaded:
            return
        logger.info('Loading model...')
        try:
            # Load model
            self.encoder  = load_model(Config.ENCODER_PATH)
            self.decoder  = load_model(Config.DECODER_PATH)

            # Load tokenizer
            with open(Config.TOKENIZER_PATH, 'rb') as f:
                self.tokenizer = pickle.load(f)

            # Load model config
            with open(Config.MODEL_CONFIG) as f:
                self.config = json.load(f)

            # Load fallback config
            with open(Config.FALLBACK_CONFIG) as f:
                fallback = json.load(f)

            self.CONFIDENCE_THRESHOLD = fallback['CONFIDENCE_THRESHOLD']
            self.MIN_RESPONSE_WORDS   = fallback['MIN_RESPONSE_WORDS']
            self.GEMINI_MODEL         = fallback['GEMINI_MODEL']
            self.SYSTEM_PROMPT        = fallback['SYSTEM_PROMPT']

            # Buat reverse word index
            self.idx2word = {v: k for k, v in self.tokenizer.word_index.items()}

            self._loaded = True
            logger.info(f'Model loaded. TF: {tf.__version__}')

        except Exception as e:
            logger.error(f'Failed to load model: {e}')
            raise

    def _preprocess(self, text):
        text = str(text).lower().strip()
        text = re.sub(r"[^a-zA-Z0-9\s?.!,']", '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def predict(self, user_input):
        if not self._loaded:
            self.load()

        cfg    = self.config
        clean  = self._preprocess(user_input)
        seq    = self.tokenizer.texts_to_sequences([clean])
        padded = pad_sequences(
            seq,
            maxlen=cfg['MAX_INPUT_LEN'],
            padding='post',
            truncating='post'
        )

        states     = self.encoder.predict(padded, verbose=0)
        target_seq = np.array([[cfg['START_TOKEN']]])

        decoded_words     = []
        confidence_scores = []

        for _ in range(Config.MAX_OUTPUT_LEN):
            out, h, c   = self.decoder.predict(
                [target_seq] + states, verbose=0
            )
            token_probs = out[0, 0, :]
            token_idx   = int(np.argmax(token_probs))
            max_prob    = float(token_probs[token_idx])
            confidence_scores.append(max_prob)

            if token_idx == cfg['END_TOKEN'] or token_idx == 0:
                break

            word = self.idx2word.get(token_idx, '')
            if word and word not in ['<start>', '<end>', '<OOV>']:
                decoded_words.append(word)

            target_seq = np.array([[token_idx]])
            states     = [h, c]

        response   = ' '.join(decoded_words)
        confidence = float(np.mean(confidence_scores)) if confidence_scores else 0.0
        return response, confidence


# Singleton instance
chatbot_engine = ChatbotEngine()