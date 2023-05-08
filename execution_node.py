import json
import socket
from flask import Flask, request
from flask_restx import Resource, Api

from node import Node
from transaction import Transaction

def get_ip_address() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    return ip

NODE_IP = get_ip_address()
NODE_PORT = 5000

app = Flask(__name__)
api = Api(app)



@api.route('/transactions')
class ExecutionNode(Resource):
    def __init__(self):
        self._node = Node(NODE_IP, execution_port=NODE_PORT)

    def post(self):
        raw_transaction = request.form['data']
        transaction_data = json.loads(raw_transaction)
        transaction = Transaction(
            transaction_data['sender'],
            transaction_data['recipient'],
            transaction_data['amount'],
            transaction_data['signature']
        )

if __name__ == "__main__":
    print("Node ip:", NODE_IP)
    app.run(host='0.0.0.0', port=NODE_PORT)