from tkinter import *
from tkinter import ttk, messagebox

from datetime import datetime
from emailCommunicationClass import emailCommunication
from tcpCommunicationClass import tcpCommunication



class guiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Communication application")
        self.tcp = tcpCommunication(self.safeDisplayMessage, self.showError)
        self.email = emailCommunication(self.safeDisplayMessage, self.showError)
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
        self.protocol = StringVar() 
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

        #Disconnect Button 
        self.disconnectButton = Button(self.mainFrame, text="Disconnect", command=self.disconnectFromServer)
        self.disconnectButton.grid(column=3, row=6, sticky=(W, E))
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
            self.tryStartReceivingEmail()
        else:
            self.setName.config(text="Your Username:")
            self.sendMessage(f"Username set: {self.userName}")

    def setUserPassword(self, event=None):
        self.userPassword = self.userPasswordEntry.get().strip()
        if not self.userPassword:
            return
        self.sendMessage("User password set")
        self.tryStartReceivingEmail()
    
    def protocolChanged(self, *args):
        if self.protocol.get() == "tcp":
            self.protocolExample.config(text="192.168.1.x:xxxx")
            self.setName.config(text="Insert username")
            self.setPassword.grid_remove()
            self.userPasswordEntry.grid_remove()
            self.userName_entry.grid(column=0, row=2, columnspan=4, sticky=W)
            self.email.stopReceivingEmail()

        elif self.protocol.get() == 'email':
            self.protocolExample.config(text="example@gmail.com")
            self.setName.config(text="Insert email")
            self.userName_entry.grid(column=0, row=2, columnspan=2, sticky=W)
            self.setPassword.grid(column=2, row=1, sticky=W)
            self.userPasswordEntry.grid(column=2, row=2, columnspan=2, sticky=W)
            self.tryStartReceivingEmail()

    def setAddress(self, event=None):
        addressName = self.addressEntry.get().strip()
        self.yourAddress.config(text=addressName)
        self.tryStartReceivingEmail()
            
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
                self.sendMessage(f"{self.userName}: {message}")
                self.saveToLog("TCP", fullMessage)
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
                self.email.sendEmail(self.userName, self.userPassword, receiverEmail, message)
                self.sendMessage(f"You sent message: {message}")
                self.saveToLog("EMAIL", fullMessage)
                self.textToSend.delete(0, END)

            except Exception as e:
                messagebox.showerror("Email error", str(e))

    def safeDisplayMessage(self, message):
        self.saveToLog("TCP", message)
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

    def disconnectFromServer(self):
        self.tcp.disconnectFromServer()

    def saveToLog(self, protocol, message):
        timeNow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("message_log.txt", "a", encoding="utf-8") as file:
            file.write(f"[{timeNow}] [{protocol}] [{message}]\n")

    def tryStartReceivingEmail(self):
        receiverEmail = self.addressEntry.get().strip()
        if self.protocol.get() != "email":
            return
        if not self.userName:
            return
        if not self.userPassword: 
            return
        if not receiverEmail:
            return
        
        self.email.startReceivingEmail(self.userName, self.userPassword, receiverEmail)
    