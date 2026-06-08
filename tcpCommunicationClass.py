import threading
import socket 

class tcpCommunication:
    def __init__(self, onMessage, onShowWarning):
        self.conn = None
        self.sock = None
        self.isConnected = False
        self.onMessage = onMessage
        self.onShowWarning = onShowWarning
        self.startServerInfo = False
    def startServer(self):
        try:    
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(("0.0.0.0", 5000))
            self.sock.listen(1)
            self.onMessage("Server started on port 5000. Waiting for connection...")
            thread = threading.Thread(target=self.acceptClient, daemon=True)
            thread.start()
            self.startServerInfo = True
        except OSError:
            self.onShowWarning("Error", "Server is already running or port 5000 is busy.")

    def acceptClient(self):
        try: 
            self.conn, address = self.sock.accept()
        except OSError:
            self.startServerInfo = False
            return
        self.isConnected = True
        self.onMessage(f"Connected with {address}")
        thread = threading.Thread(target=self.reciveMessage, daemon=True)
        thread.start()

    def connectToServer(self, ip , port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((ip, int(port)))
        self.isConnected = True
        self.onMessage(f"Connected to {ip}:{port}") 
        thread = threading.Thread(target=self.reciveMessage, daemon=True)
        thread.start()
    
    def sendMessage(self, message):
        if not self.isConnected or self.conn is None:
            self.onShowWarning("Warning", "You are not connected.")
            return
        self.conn.sendall(message.encode("utf-8"))

    def reciveMessage(self):
        while True:
            try:
                data = self.conn.recv(1024)
                if not data:
                    break
                message = data.decode("utf-8")
                self.onMessage(message)
            except:
                 break
        self.startServerInfo = False            
        self.isConnected = False 
        
    def disconnectFromServer(self):
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
            if self.sock:
                self.sock.close()
                self.sock = None
            self.isConnected = False
            self.startServerInfo = False

            self.onMessage("Disconnected")

        except Exception as e:
            self.onShowWarning("Disconnect error", str(e))
