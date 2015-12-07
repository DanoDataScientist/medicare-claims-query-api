from flask import Flask
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World! How are you? I bet you are doing well!'


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if os.path.isfile(os.path.join(current_dir, 'PRODUCTION')):
        app.run()
    else:
        # Running dev server...
        app.run(host='0.0.0.0', debug=True)
