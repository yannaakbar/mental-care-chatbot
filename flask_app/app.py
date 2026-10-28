import logging, time
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from .config import Config
from .chatbot_engine import chatbot_engine
from .gemini_fallback import gemini_fallback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


# ===== STARTUP =====
@app.before_request
def startup():
    if not chatbot_engine._loaded:
        chatbot_engine.load()
        gemini_fallback.initialize(
            gemini_model  = chatbot_engine.GEMINI_MODEL,
            system_prompt = chatbot_engine.SYSTEM_PROMPT,
        )


# ===== ROUTES =====
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({
        'status'          : 'ok',
        'model_loaded'    : chatbot_engine._loaded,
        'gemini_available': gemini_fallback._initialized,
        'tf_version'      : chatbot_engine.config['TF_VERSION'] if chatbot_engine._loaded else None,
    })

@app.route('/livechat')
def livechat():
    return render_template('livechat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data       = request.get_json(silent=True) or {}
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

    if len(user_input) > 500:
        return jsonify({'error': 'Pesan terlalu panjang (max 500 karakter)'}), 400

    # Ambil history dari session
    history    = session.get('chat_history', [])
    start_time = time.time()

    # Step 1: Coba Seq2Seq
    seq2seq_resp, confidence = chatbot_engine.predict(user_input)

    # Step 2: Evaluasi & fallback
    use_fallback = (
        confidence < chatbot_engine.CONFIDENCE_THRESHOLD or
        len(seq2seq_resp.split()) < chatbot_engine.MIN_RESPONSE_WORDS or
        not seq2seq_resp.strip()
    )

    if use_fallback:
        response, ok = gemini_fallback.get_response(user_input, history)
        source       = 'gemini' if ok else 'fallback_error'
    else:
        response = seq2seq_resp
        source   = 'seq2seq'

    # Update history
    history.append({'role': 'user',  'parts': [{'text': user_input}]})
    history.append({'role': 'model', 'parts': [{'text': response}]})

    # Batasi history
    if len(history) > Config.MAX_HISTORY * 2:
        history = history[-(Config.MAX_HISTORY * 2):]

    session['chat_history'] = history

    elapsed = round((time.time() - start_time) * 1000, 1)
    logger.info(
        f'[{source}] Q="{user_input[:50]}" '
        f'conf={confidence:.3f} t={elapsed}ms'
    )

    return jsonify({
        'response'  : response,
        'source'    : source,
        'confidence': round(confidence, 3),
        'time_ms'   : elapsed,
    })


@app.route('/reset', methods=['POST'])
def reset():
    session.pop('chat_history', None)
    return jsonify({'status': 'session_cleared'})


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)