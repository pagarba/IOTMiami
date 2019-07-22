
import os

from flask import Flask, jsonify, render_template

# Constants
ACCOUNT_MAX_SIZE    = 20
API_PORT_NUMBER     = 3000
PAYLOAD_MAX_SIZE    = 240
SERIAL_BAUD_RATE    = 9600
TYPE_REGISTER       = 0x00
TYPE_ACCOUNT        = 0x10
TYPE_BLOCK          = 0x11

app = Flask(__name__)

@app.route('/account', methods=['GET'])
def get_account():
    return render_template('templates/account.html')

@app.route('/recv', methods=['POST'])
def post_recv():
    return 'Recv!'

@app.route('/send', methods=['POST'])
def post_send():
    return 'Sent!'

@app.route('/', methods=['GET'])
def get_base():
    return render_template('templates/base.html')

if __name__ == '__main__':
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.run()