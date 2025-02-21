from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from twisted.internet import reactor, protocol
from twisted.protocols import basic
from loguru import logger
import threading

logger.add("chat_web.log", rotation="500 MB", retention="10 days")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

class ChatProtocol(basic.LineReceiver):
    def connectionMade(self):
        self.factory.clients.append(self)
        logger.info(f"New client connected: {self.transport.getPeer().host}")

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        logger.info(f"Client disconnected: {self.transport.getPeer().host}")

    def lineReceived(self, line):
        message = f"{self.transport.getPeer().host}: {line.decode()}"
        logger.info(message)
        for client in self.factory.clients:
            if client != self:
                client.sendLine(message.encode())

class ChatFactory(protocol.Factory):
    def __init__(self):
        self.clients = []

    def buildProtocol(self, addr):
        return ChatProtocol()

def start_twisted_server():
    reactor.listenTCP(8080, ChatFactory())
    reactor.startRunning(installSignalHandlers=False)  # FIXED Twisted Issue

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_send_message_event(data):
    message = data['message']
    logger.info(f"Message from web: {message}")
    emit('receive_message', {'message': message}, broadcast=True)

if __name__ == "__main__":
    logger.info("Starting chat web server...")
    socketio.start_background_task(start_twisted_server)  # FIXED Threading Issue
    socketio.run(app, port=5000, debug=False)
