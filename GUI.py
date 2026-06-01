#To Do 
# - przycisk na zamknięcie konwesrsacji 
# - wybór email i cała implementacja email
# - może zmienić theme jak już będę miał dużo czasu ??? fajnie by było 
# - zrobić loggi żeby zapisywać w pliku wysyłabne wiadomości czy coś 

from tkinter import *
from tkinter import ttk, messagebox
import socket
import threading
import smtplib
from email.message import EmailMessage 

class emailCommunication:
    def __init__(self):
        pass


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
        self.conn, address = self.sock.accept()
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
        self.onMessage("Connection closed.")




class mainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Communication application")
        self.tcp = tcpCommunication(self.safeDisplayMessage, self.showError)
        self.userName = ""
        self.userPassword = ""
        self.mainFrame = ttk.Frame(root, padding=(3, 3, 6, 6))
        self.mainFrame.grid(column=0, row=0, sticky=(N, W, E, S), columnspan=4, rowspan=8)        

        #Info 1 Label
        self.setName = Label(self.mainFrame, text="Insert username")
        self.setName.grid(column=0, row=1, sticky=W)

        #Pick Username Entry
        self.userName_entry = Entry(self.mainFrame)
        self.userName_entry.grid(column=0, row=2, columnspan=4, sticky=W)

        self.userName_entry.bind("<Return>", self.setUserName)
        
        #Password Label and entry
        self.setPassword = Label(self.mainFrame, text="Password:")
        self.userPasswordEntry = Entry(self.mainFrame, show="*")

        self.userPasswordEntry.bind("<Return>", self.setUserPassword)

        #Radio button
        self.protocol = StringVar(value="tcp") 
        home = ttk.Radiobutton(self.mainFrame, text='TCP', variable=self.protocol, value="tcp")
        office = ttk.Radiobutton(self.mainFrame, text='EMAIL', variable=self.protocol, value="email")

        home.grid(column=0, row=0, columnspan=1)
        office.grid(column=2, row=0, columnspan=1)
        
        self.protocolFormat = Label(self.mainFrame, text="Address format:")
        self.protocolFormat.grid(column=0, row=3, sticky=W)
        
        
        self.protocolExample = Label(self.mainFrame, text="")
        self.protocolExample.grid(column=1, row=3, columnspan=3, sticky=W)

        self.protocol.trace_add("write", self.protocolChanged)
        
        #Connect Button
        self.connectButton = Button(self.mainFrame, text="Connect", command=self.connectToServer)
        self.connectButton.grid(column=3, row=5, sticky=(W, E))

        #Protocol Entry
        self.addressEntry = Entry(self.mainFrame)
        self.addressEntry.grid(column=0, row=4, columnspan=4, sticky=(W,E))

        self.address = Label(self.mainFrame, text="Address to send to:")
        self.address.grid(column=0, row=5, sticky=W)

        #Address Label
        self.yourAddress = Label(self.mainFrame, text="")
        self.yourAddress.grid(column=1, row=5, columnspan=2, sticky=W)
        
        self.addressEntry.bind("<Return>", self.setAddress)

        #Text Label
        self.textFrame = ttk.Frame(self.mainFrame, borderwidth=5, relief="ridge", width=400, height=400)
        self.textFrame.grid(column=0,row=7, columnspan=4)

        self.chatBox = Text(self.mainFrame, width=50, height=20, state=DISABLED)
        self.chatBox.grid(column=0, row=7, columnspan=4, sticky=(N, W, E, S))
        
        #Text Entry
        self.textToSend = Entry(self.mainFrame)
        self.textToSend.grid(column=0, row=8, columnspan=3, sticky=(W, E))
        
        self.textToSend.bind("<Return>", self.addMessage)
        #Send Button 
        self.button = Button(self.mainFrame, text="Send", command=self.addMessage)
        self.button.grid(column=3, row=8, sticky=(W, E))

        #Start Server Button
        self.serverButton = Button(self.mainFrame, text="Start server on port :5000", command=self.startServer)
        self.serverButton.grid(column=0, row=6, columnspan=3, sticky=W)    
    
    def sendEmail(self, receiverEmail, messageText):
        senderEmail = self.userName
        senderPassword = self.userPassword

        msg = EmailMessage()
        msg['Subject'] = f"Messege from {senderEmail}"
        msg['From'] = senderEmail
        msg['To'] = receiverEmail
        msg.set_content(messageText)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(senderEmail, senderPassword)
            smtp.send_message(msg)

    def setUserName(self, event=None):
        if self.tcp.startServerInfo == True or self.tcp.isConnected:
            messagebox.showwarning("Warning", "You can't change username when server started or when connected")
            return
        self.userName = self.userName_entry.get().strip()
        if not self.userName:
            return
        if self.protocol.get() == "email":
            self.setName.config(text="Your email:")
            self.sendMessage(f"Email set: {self.userName}")
        else:
            self.setName.config(text="Your Username:")
            self.sendMessage(f"Username set: {self.userName}")
    def setUserPassword(self, event=None):
        self.userPassword = self.userPasswordEntry.get().strip()
        if not self.userPassword:
            return
        self.sendMessage(self.userPassword)
    
    def protocolChanged(self, *args):
        if self.protocol.get() == "tcp":
            self.protocolExample.config(text="192.168.1.x:xxxx")
            self.setName.config(text="Insert username")
            self.setPassword.grid_remove()
            self.userPasswordEntry.grid_remove()
            self.userName_entry.grid(column=0, row=2, columnspan=4, sticky=W)

        elif self.protocol.get() == 'email':
            self.protocolExample.config(text="example@gmail.com")
            self.setName.config(text="Insert email")
            self.userName_entry.grid(column=0, row=2, columnspan=2, sticky=W)

            self.setPassword.grid(column=2, row=1, sticky=W)
            self.userPasswordEntry.grid(column=2, row=2, columnspan=2, sticky=W)
    
    def setAddress(self, event=None):
        addressName = self.addressEntry.get().strip()
        self.yourAddress.config(text=addressName)
            
    def sendMessage(self, message):
        self.chatBox.config(state=NORMAL)
        self.chatBox.insert(END, message + "\n")
        self.chatBox.config(state=DISABLED)
        self.chatBox.see(END)

    def addMessage(self, event=None):
        message = self.textToSend.get().strip()
        if not message:
            messagebox.showwarning("Warning", "You can't send nothing")
            return
        if not self.userName:
            messagebox.showwarning("Warning", "Set username first.")
            return
        if self.protocol.get() == "tcp":
            fullMessage = f"{self.userName}: {message}"
            try:
                self.tcp.sendMessage(fullMessage)
                self.sendMessage(f"You: {message}")
                self.textToSend.delete(0, END)

            except Exception as e:
                messagebox.showerror("Send error", str(e))
        elif self.protocol.get() == "email":
            receiverEmail = self.addressEntry.get().strip()
            if not receiverEmail:
                messagebox.showwarning("Warning", "Set reciver email first")
                return
            try:
                senderEmail = self.userName
                fullMessage = f"{senderEmail}: {message}"
                self.sendEmail(receiverEmail, fullMessage)
                self.sendMessage(f"You by email: {message}")
                self.textToSend.delete(0, END)

            except Exception as e:
                messagebox.showerror("Email error", str(e))

    def safeDisplayMessage(self, message):
        self.root.after(0, lambda: self.sendMessage(message))
    
    def showError(self, error, message):
        messagebox.showerror(error, message)
    def startServer(self):
        if not self.userName:
            messagebox.showerror("Warning", "Set username first.")
            return
        self.tcp.startServer()
    def connectToServer(self):
        address = self.addressEntry.get().strip()
        if not self.userName:
            messagebox.showwarning("Warning", "Set username first.")
            return
        if ":" not in address:
            messagebox.showerror("Error", "Use format: IP:PORT")
            return
        ip, port = address.split(":")
        try:
            self.tcp.connectToServer(ip, port)
            self.yourAddress.config(text=address)

        except Exception as e:
            messagebox.showerror("Connection error", str(e))

    
def main_fun():
    root = Tk()
    mainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main_fun()