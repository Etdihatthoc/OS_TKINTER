# import tkinter as tk
# import json
# import time
# import threading
# from queue import Queue, Full, Empty
# from datetime import datetime

# # Load configurations from config.json
# with open("config.json", "r") as file:
#     config = json.load(file)

# TIME_DELAY = config["rq_time_arrival"]
# QUEUE_LENGTH = config["queue_length"]
# PROCESS_TIMES = {
#     "read": config["read_time"],
#     "write": config["write_time"],
#     "forward": config["forward_time"]
# }
# REQUEST_SEQUENCE = config["requests_sequence"]

# # Server class simulating request processing with a limited queue
# class ServerSimulator:
#     def __init__(self, queue_length):
#         self.queue = Queue(maxsize=queue_length)
#         self.running = True
#         self.log = []
#         self.request_counts = {"read": 0, "write": 0, "forward": 0}  # Track request counts

#         # Start the processing thread
#         self.process_thread = threading.Thread(target=self.process_requests)
#         self.process_thread.start()

#     def add_request(self, request_type):
#         # Generate a unique name for the request, e.g., "Read1", "Write2", etc.
#         self.request_counts[request_type] += 1
#         request_name = f"{request_type.capitalize()}{self.request_counts[request_type]}"
        
#         try:
#             self.queue.put_nowait(request_name)
#             self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Request '{request_name}' added to the queue.")
#         except Full:
#             #self.log.append(f"\033[91mQueue is full! Request '{request_name}' blocked.\033[0m")
#             self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Queue is full! Request '{request_name}' blocked.")

#     def process_requests(self):
#         while self.running:
#             try:
#                 # Get the next request from the queue
#                 request_name = self.queue.get(timeout=1)
                
#                 # Extract the request type (e.g., "Read" from "Read1")
#                 request_type = ''.join(filter(str.isalpha, request_name)).lower()
                
#                 # Retrieve the processing time based on request type
#                 process_time = PROCESS_TIMES.get(request_type, 1)
                
#                 self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Processing '{request_name}' (time: {process_time}s)...")
                
#                 # Simulate request processing time
#                 time.sleep(process_time)
#                 self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] '{request_name}' processed.")
                
#                 self.queue.task_done()
#             except Empty:
#                 continue

#     def stop(self):
#         self.running = False
#         self.process_thread.join()

# # Tkinter GUI Application
# class App(tk.Tk):
#     def __init__(self, server):
#         super().__init__()
#         self.title("Server Queue Simulation")
#         self.geometry("1000x600")
#         self.server = server

#         # Create UI elements
#         self.queue_label = tk.Label(self, text="Request Queue", font=("Arial", 12))
#         self.queue_label.pack(pady=5)

#         # Queue Display and Queue Size
#         queue_frame = tk.Frame(self)
#         queue_frame.pack(pady=5)

#         # Listbox to show current requests in the queue
#         self.queue_display = tk.Listbox(queue_frame, height=10, width=30)
#         self.queue_display.pack(side="left", padx=5)

#         # Label to show the number of requests in the queue
#         self.queue_count_label = tk.Label(queue_frame, text="Queue Size: 0", font=("Arial", 12))
#         self.queue_count_label.pack(side="left")

#         self.status_label = tk.Label(self, text="Status Log", font=("Arial", 12))
#         self.status_label.pack(pady=5)

#         # Text widget to show the status log
#         self.status_display = tk.Text(self, height=20, width=60, state="disabled")
#         self.status_display.pack()

#         # Automatically add requests from the sequence
#         self.process_sequence()

#         # Update queue and log display
#         self.update_display()

#     def process_sequence(self):
#         # Add requests from REQUEST_SEQUENCE one by one with delay
#         def add_requests():
#             for request_type in REQUEST_SEQUENCE:
#                 self.server.add_request(request_type)
#                 self.update_display()
#                 time.sleep(TIME_DELAY)  # Delay of 1 second between each request

#         # Start a thread to add requests without blocking the GUI
#         threading.Thread(target=add_requests, daemon=True).start()

#     def update_display(self):
#         # Update queue display
#         self.queue_display.delete(0, tk.END)
#         for i, item in enumerate(list(self.server.queue.queue)):
#             self.queue_display.insert(tk.END, item)

#         # Update the queue count label
#         queue_size = self.server.queue.qsize()
#         self.queue_count_label.config(text=f"RQ in queue: {queue_size}/{QUEUE_LENGTH}")

#         # Update log display
#         self.status_display.config(state="normal")
#         self.status_display.delete(1.0, tk.END)
#         self.status_display.insert(tk.END, "\n".join(self.server.log[-20:]))  # Show last 10 log entries
#         self.status_display.config(state="disabled")

#         # Schedule next update
#         self.after(1000, self.update_display)

#     def on_closing(self):
#         self.server.stop()
#         self.destroy()

# # Main function
# def main():
#     server = ServerSimulator(QUEUE_LENGTH)
#     app = App(server)
#     app.protocol("WM_DELETE_WINDOW", app.on_closing)
#     app.mainloop()

# if __name__ == "__main__":
#     main()


import tkinter as tk
import json
import time
import threading
from queue import Queue, Full, Empty
from datetime import datetime

# Load configurations from config.json
with open("config.json", "r") as file:
    config = json.load(file)

TIME_DELAY = config["rq_time_arrival"]
QUEUE_LENGTH = config["queue_length"]
PROCESS_TIMES = {
    "read": config["read_time"],
    "write": config["write_time"],
    "forward": config["forward_time"]
}
REQUEST_SEQUENCE = config["requests_sequence"]

# Color mapping for request types
REQUEST_COLORS = {
    "read": "red",
    "write": "green",
    "forward": "blue"
}

# Server class simulating request processing with a limited queue
class ServerSimulator:
    def __init__(self, queue_length):
        self.queue = Queue(maxsize=queue_length)
        self.running = True
        self.log = []
        self.request_counts = {"read": 0, "write": 0, "forward": 0}  # Track request counts

        # Start the processing thread
        self.process_thread = threading.Thread(target=self.process_requests)
        self.process_thread.start()

    def add_request(self, request_type):
        # Generate a unique name for the request, e.g., "Read1", "Write2", etc.
        self.request_counts[request_type] += 1
        request_name = f"{request_type.capitalize()}{self.request_counts[request_type]}"
        
        try:
            self.queue.put_nowait(request_name)
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Request '{request_name}' added to the queue.")
        except Full:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Queue is full! Request '{request_name}' blocked.")

    def process_requests(self):
        while self.running:
            try:
                # Get the next request from the queue
                request_name = self.queue.get(timeout=1)
                
                # Extract the request type (e.g., "Read" from "Read1")
                request_type = ''.join(filter(str.isalpha, request_name)).lower()
                
                # Retrieve the processing time based on request type
                process_time = PROCESS_TIMES.get(request_type, 1)
                
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Processing '{request_name}' (time: {process_time}s)...")
                
                # Simulate request processing time
                time.sleep(process_time)
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] '{request_name}' processed.")
                
                self.queue.task_done()
            except Empty:
                continue

    def stop(self):
        self.running = False
        self.process_thread.join()

# Tkinter GUI Application
class App(tk.Tk):
    def __init__(self, server):
        super().__init__()
        self.title("Server Queue Simulation")
        self.geometry("1000x600")
        self.server = server

        # Create UI elements
        self.create_ui_elements()

        # Automatically add requests from the sequence
        self.process_sequence()

        # Update queue and log display
        self.update_display()

    def create_ui_elements(self):
        # Canvas to draw server and queue layout
        self.canvas = tk.Canvas(self, width=1000, height=600, bg="white")
        self.canvas.pack()

        # Draw Server (Blue Circle)
        self.server_circle = self.canvas.create_oval(750, 200, 850, 300, fill="lightblue")
        self.canvas.create_text(800, 250, text="Server", font=("Arial", 12))

        # Queue Label
        self.canvas.create_text(400, 100, text="Request Queue", font=("Arial", 12))

        # Compact Queue slots above Server
        self.queue_slots = []
        for i in range(QUEUE_LENGTH):
            slot = self.canvas.create_rectangle(200 + i * 50, 130, 240 + i * 50, 170, outline="orange", fill="white")
            self.queue_slots.append(slot)

        # Status Log
        self.status_label = tk.Label(self, text="Status Log", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Text widget to show the status log
        self.status_display = tk.Text(self, height=15, width=100, state="disabled")
        self.status_display.pack()

    def process_sequence(self):
        # Add requests from REQUEST_SEQUENCE one by one with delay
        def add_requests():
            for request_type in REQUEST_SEQUENCE:
                self.server.add_request(request_type)
                self.update_display()
                time.sleep(TIME_DELAY)  # Delay of TIME_DELAY seconds between each request

        # Start a thread to add requests without blocking the GUI
        threading.Thread(target=add_requests, daemon=True).start()

    def update_display(self):
        # Update queue slots with colors based on request types
        queue_items = list(self.server.queue.queue)
        for i in range(QUEUE_LENGTH):
            if i < len(queue_items):
                request_name = queue_items[i]
                request_type = ''.join(filter(str.isalpha, request_name)).lower()
                color = REQUEST_COLORS.get(request_type, "white")
                self.canvas.itemconfig(self.queue_slots[i], fill=color)
            else:
                self.canvas.itemconfig(self.queue_slots[i], fill="white")

        # Update log display
        self.status_display.config(state="normal")
        self.status_display.delete(1.0, tk.END)
        self.status_display.insert(tk.END, "\n".join(self.server.log[-20:]))  # Show last 20 log entries
        self.status_display.config(state="disabled")

        # Schedule next update
        self.after(1000, self.update_display)

    def on_closing(self):
        self.server.stop()
        self.destroy()

# Main function
def main():
    server = ServerSimulator(QUEUE_LENGTH)
    app = App(server)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
