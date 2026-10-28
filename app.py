import sys
import os

# Pastikan root folder ada di path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_app.app import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7860)
