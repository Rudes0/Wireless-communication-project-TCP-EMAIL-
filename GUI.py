from tkinter import *
from tkinter import ttk, messagebox
import socket
import threading

class mainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Communication application")
        self.conn = None
        self.sock = None
        self.isConnected = False
        self.username = ""

        
        self.mainFrame = ttk.Frame(root, padding=(3, 3, 6, 6))
        self.mainFrame.grid(column=0, row=0, sticky=(N, W, E, S), columnspan=4, rowspan=8)
        

        #Info 1 Label
        self.setName = Label(self.mainFrame, text="Insert username")
        self.setName.grid(column=0, row=0, sticky=W)

        #Pick Username Entry
        self.userName_entry = Entry(self.mainFrame)
        self.userName_entry.grid(column=0, row=1, columnspan=4, sticky=W)

        self.userName_entry.bind("<Return>", self.set_userName)
        
        #Radio button
        self.protocol = StringVar() 
        home = ttk.Radiobutton(self.mainFrame, text='TCP', variable=self.protocol, value="tcp").grid(row=2, column=0, columnspan=1)
        office = ttk.Radiobutton(self.mainFrame, text='EMAIL', variable=self.protocol, value="email").grid(row=2, column=2, columnspan=1)

        self.protocolFormat = Label(self.mainFrame, text="Address format:")
        self.protocolFormat.grid(column=0, row=3, sticky=W)
        
        
        self.protocolExample = Label(self.mainFrame, text="")
        self.protocolExample.grid(column=1, row=3, columnspan=3, sticky=W)

        self.protocol.trace_add("write", self.protocol_changed)
        
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
        
        self.addressEntry.bind("<Return>", self.set_address)

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
    
    def set_userName(self, event=None):
        self.userName = self.userName_entry.get().strip()
            
        if self.userName:
            self.userName_entry.destroy()
            #Info 2 Label
            username_label = Label(self.mainFrame, text=self.userName)
            username_label.grid(column=0, row=1, columnspan=4, sticky=W)
                
            #Picked Username Label
            setName = Label(self.mainFrame, text="Your Username:")
            setName.grid(column=0, row=0, sticky=W)
    
    def protocol_changed(self, *args):
        if self.protocol.get() == "tcp":
                self.protocolExample.config(text="192.168.1.x:xxxx")
        elif self.protocol.get() == 'email':
                self.protocolExample.config(text="example@gmail.com")
    
    def set_address(self, event=None):
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
              return
         
        if not self.userName:
            messagebox.showwarning("Warning", "Set username first.")
            return
        
        if not self.isConnected or self.conn is None:
            messagebox.showwarning("Warning", "You are not connected.")
            return
        
        fullMessage = f"{self.userName}: {message}"

        try:
            self.conn.sendall(fullMessage.encode("utf-8"))
            self.sendMessage(f"You: {message}")
            self.textToSend.delete(0, END)

        except Exception as e:
            messagebox.showerror("Send error", str(e))
    def reciveMessages(self):
        while True:
            try:
                data = self.conn.recv(1024)
                if not data:
                    break
                message = data.decode("utf-8")
                self.root.after(0, lambda msg=message: self.sendMessage(msg))
            except:
                 break
            
        self.isConnected = False
        self.root.after(0, lambda: self.sendMessage("Connection closed."))

    def startServer(self):
            try:    
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind(("0.0.0.0", 5000))
                self.sock.listen(1)
                
                self.sendMessage("Server started on port 5000. Waiting for connection...")

                thread = threading.Thread(target=self.acceptClient, daemon=True)
                thread.start()

            except OSError:
                 messagebox.showerror("Error", "Server is already running or port 5000 is busy.")

    def acceptClient(self):
        self.conn, address = self.sock.accept()
        self.isConnected = True
         
        self.root.after(0, lambda: self.sendMessage(f"Connected with {address}"))

        thread = threading.Thread(target=self.reciveMessages, daemon=True)
        thread.start()

    def connectToServer(self):
        address = self.addressEntry.get().strip()

        if ":" not in address:
            messagebox.showerror("Error", "Use format: IP:PORT")
            return

        ip, port = address.split(":")

        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((ip, int(port)))
            self.isConnected = True

            self.yourAddress.config(text=address)
            self.sendMessage(f"Connected to {address}")

            thread = threading.Thread(target=self.reciveMessages, daemon=True)
            thread.start()

        except Exception as e:
            messagebox.showerror("Connection error", str(e))

    
def main_fun():
    root = Tk()
    mainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main_fun()