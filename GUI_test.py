from tkinter import *
from tkinter import ttk, messagebox
import socket
import threading


class MainWindow:
    def __init__(self, root):
        self.root = root
        root.title("Communication application")

        self.username = ""
        self.sock = None
        self.conn = None
        self.is_connected = False

        mainFrame = ttk.Frame(root, padding=(3, 3, 6, 6))
        mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)
        mainFrame.columnconfigure(2, weight=1)
        mainFrame.columnconfigure(3, weight=1)
        mainFrame.rowconfigure(6, weight=1)

        # USERNAME
        Label(mainFrame, text="Insert username").grid(row=0, column=0, sticky=W)

        self.userNameEntry = Entry(mainFrame)
        self.userNameEntry.grid(row=1, column=0, columnspan=4, sticky=(W, E))
        self.userNameEntry.bind("<Return>", self.set_username)

        self.usernameLabel = Label(mainFrame, text="")
        self.usernameLabel.grid(row=0, column=1, columnspan=3, sticky=W)

        # RADIOBUTTONS
        self.protocol = StringVar(value="tcp")

        ttk.Radiobutton(
            mainFrame,
            text="TCP",
            variable=self.protocol,
            value="tcp",
            command=self.protocol_changed
        ).grid(row=2, column=0)

        ttk.Radiobutton(
            mainFrame,
            text="EMAIL",
            variable=self.protocol,
            value="email",
            command=self.protocol_changed
        ).grid(row=2, column=2)

        Label(mainFrame, text="Address format:").grid(column=0, row=3, sticky=W)

        self.protocolExample = Label(mainFrame, text="192.168.1.x:5000")
        self.protocolExample.grid(column=1, row=3, columnspan=3, sticky=W)

        # ADDRESS
        self.addressEntry = Entry(mainFrame)
        self.addressEntry.grid(row=4, column=0, columnspan=3, sticky=(W, E))

        self.connectButton = Button(mainFrame, text="Connect", command=self.connect_to_server)
        self.connectButton.grid(row=4, column=3, sticky=(W, E))

        Label(mainFrame, text="Address to send to:").grid(column=0, row=5, sticky=W)

        self.yourAddress = Label(mainFrame, text="")
        self.yourAddress.grid(column=1, row=5, columnspan=3, sticky=W)

        # CHAT TEXT AREA
        self.chatBox = Text(mainFrame, width=50, height=20, state=DISABLED)
        self.chatBox.grid(column=0, row=6, columnspan=4, sticky=(N, W, E, S))

        # MESSAGE ENTRY
        self.textToSend = Entry(mainFrame)
        self.textToSend.grid(row=7, column=0, columnspan=3, sticky=(W, E))
        self.textToSend.bind("<Return>", self.send_message)

        self.sendButton = Button(mainFrame, text="Send", command=self.send_message)
        self.sendButton.grid(row=7, column=3, sticky=(W, E))

        # SERVER BUTTON
        self.serverButton = Button(mainFrame, text="Start server", command=self.start_server)
        self.serverButton.grid(row=8, column=0, columnspan=4, sticky=(W, E))

    def set_username(self, event=None):
        name = self.userNameEntry.get().strip()

        if name:
            self.username = name
            self.userNameEntry.destroy()
            self.usernameLabel.config(text=f"Your username: {self.username}")

    def protocol_changed(self):
        if self.protocol.get() == "tcp":
            self.protocolExample.config(text="192.168.1.x:5000")
        elif self.protocol.get() == "email":
            self.protocolExample.config(text="example@gmail.com")

    def add_message(self, message):
        self.chatBox.config(state=NORMAL)
        self.chatBox.insert(END, message + "\n")
        self.chatBox.config(state=DISABLED)
        self.chatBox.see(END)

    def start_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(("0.0.0.0", 5000))
            self.sock.listen(1)

            self.add_message("Server started on port 5000. Waiting for connection...")

            thread = threading.Thread(target=self.accept_client, daemon=True)
            thread.start()

        except OSError:
            messagebox.showerror("Error", "Server is already running or port 5000 is busy.")

    def accept_client(self):
        self.conn, address = self.sock.accept()
        self.is_connected = True

        self.root.after(0, lambda: self.add_message(f"Connected with {address}"))

        thread = threading.Thread(target=self.receive_messages, daemon=True)
        thread.start()

    def connect_to_server(self):
        address = self.addressEntry.get().strip()

        if ":" not in address:
            messagebox.showerror("Error", "Use format: IP:PORT")
            return

        ip, port = address.split(":")

        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((ip, int(port)))
            self.is_connected = True

            self.yourAddress.config(text=address)
            self.add_message(f"Connected to {address}")

            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()

        except Exception as e:
            messagebox.showerror("Connection error", str(e))

    def send_message(self, event=None):
        message = self.textToSend.get().strip()

        if not message:
            return

        if not self.username:
            messagebox.showwarning("Warning", "Set username first.")
            return

        if not self.is_connected or self.conn is None:
            messagebox.showwarning("Warning", "You are not connected.")
            return

        full_message = f"{self.username}: {message}"

        try:
            self.conn.sendall(full_message.encode("utf-8"))
            self.add_message("You: " + message)
            self.textToSend.delete(0, END)

        except Exception as e:
            messagebox.showerror("Send error", str(e))

    def receive_messages(self):
        while True:
            try:
                data = self.conn.recv(1024)

                if not data:
                    break

                message = data.decode("utf-8")
                self.root.after(0, lambda msg=message: self.add_message(msg))

            except:
                break

        self.is_connected = False
        self.root.after(0, lambda: self.add_message("Connection closed."))


def main_fun():
    root = Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main_fun()