import warnings
warnings.filterwarnings(action='ignore')

from src.flask.server import app

version = '0.1.0'

if __name__ == "__main__":
    while True:
        try:
            app.run(host='0.0.0.0', port=5000)

        except GeneratorExit:
            app.run(host='0.0.0.0', port=5000)
