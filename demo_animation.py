import tkinter as tk
from PIL import Image, ImageTk
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
        self.update_queue_display_callback = None  # Placeholder for the callback

        # Start the processing thread
        self.process_thread = threading.Thread(target=self.process_requests)
        self.process_thread.start()

    def add_request(self, request_type):
        # Generate a unique name for the request, e.g., "Read1", "Write2", etc.
        self.request_counts[request_type] += 1
        request_name = f"{request_type.capitalize()}{self.request_counts[request_type]}"
        
        try:
            self.queue.put_nowait((request_name, request_type))
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Request '{request_name}' added to the queue.")
            if self.update_queue_display_callback:
                self.update_queue_display_callback()
        except Full:
            # Highlight "Queue is full" messages in red
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Queue is full! Request '{request_name}' blocked.")
            if self.update_queue_display_callback:
                self.update_queue_display_callback(request_name, request_type, blocked=True)

    def process_requests(self):
        while self.running:
            try:
                # Get the next request from the queue
                request_name, request_type = self.queue.get(timeout=1)
                process_time = PROCESS_TIMES.get(request_type, 1)
                
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Processing '{request_name}' (time: {process_time}s)...")
                
                # Simulate request processing time
                time.sleep(process_time)
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] '{request_name}' processed.")
                
                self.queue.task_done()
                
                # Update queue display after processing
                if self.update_queue_display_callback:
                    self.update_queue_display_callback()
            except Empty:
                continue

    def stop(self):
        self.running = False
        self.process_thread.join()

# Tkinter GUI Application
class App(tk.Tk):
    def __init__(self, server):
        super().__init__()
        self.title("Server Queue Simulation with Animation")
        self.geometry("1200x800")
        self.server = server

        # Load images
        self.client_image = ImageTk.PhotoImage(Image.open("client.png").resize((100, 100)))
        self.server_image = ImageTk.PhotoImage(Image.open("server.png").resize((100, 100)))

        # Create UI elements
        self.create_ui_elements()

        # Set flags for controlling simulation
        self.running = False
        self.paused = False
        self.thread = None

        # Update queue and log display
        self.update_display()

    def create_ui_elements(self):
        # Create a canvas for drawing
        self.canvas = tk.Canvas(self, width=1200, height=800, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw the Client and Server images
        self.canvas.create_image(150, 350, image=self.client_image)
        self.canvas.create_image(1050, 350, image=self.server_image)
        self.canvas.create_text(150, 450, text="Client", font=("Arial", 16))
        self.canvas.create_text(1050, 450, text="Server", font=("Arial", 16))

        # Draw connection line between Client and Server
        self.canvas.create_line(250, 400, 950, 400, arrow=tk.LAST, width=3)

        # Add "Request Queue" label above the queue
        self.canvas.create_text(600, 200, text="Request Queue", font=("Arial", 16, "bold"))

        # Queue slots for visualizing requests in a compact style
        self.queue_slots = []
        slot_x_start = 300  # Starting X position for the queue slots
        slot_y = 250  # Y position for all queue slots
        for i in range(QUEUE_LENGTH):
            slot = self.canvas.create_rectangle(slot_x_start + i * 40, slot_y, slot_x_start + 40 + i * 40, slot_y + 40, outline="orange", fill="white")
            self.queue_slots.append(slot)

        # Blocked Area
        #self.canvas.create_text(1050, 100, text="Blocked Area", font=("Arial", 16, "bold"))
        self.blocked_requests = []  # List to keep track of blocked request visuals

        # Status Log
        self.status_label = tk.Label(self, text="Status Log", font=("Arial", 16))
        self.status_label.place(x=50, y=500)

        # Text widget to show the status log
        self.status_display = tk.Text(self, height=10, width=130, state="disabled", font=("Arial", 10))
        self.status_display.place(x=50, y=550)

        # Control buttons
        self.start_button = tk.Button(self, text="Start", font=("Arial", 12), command=self.start_simulation)
        self.start_button.place(x=1100, y=600)

        self.pause_button = tk.Button(self, text="Pause", font=("Arial", 12), command=self.pause_simulation)
        self.pause_button.place(x=1100, y=650)

        self.end_button = tk.Button(self, text="End", font=("Arial", 12), command=self.on_closing)
        self.end_button.place(x=1100, y=700)

    def start_simulation(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self.process_sequence, daemon=True)
            self.thread.start()

    def pause_simulation(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")

    def process_sequence(self):
        for request_type in REQUEST_SEQUENCE:
            if not self.running:
                break
            while self.paused:
                time.sleep(0.1)  # Wait while paused
            # Animate request moving from client to queue
            self.animate_request_to_queue(request_type)
            self.server.add_request(request_type)
            self.update_display()
            time.sleep(TIME_DELAY)  # Delay between each request

    def animate_request_to_queue(self, request_type, blocked=False):
        # Create a small rectangle representing the request moving from Client to Queue
        request_label = self.canvas.create_rectangle(200, 370, 250, 420, fill=REQUEST_COLORS[request_type])

        # Define the animation function for moving the request label
        def move_request(x, y, final_x, final_y):
            if x < final_x:
                self.canvas.coords(request_label, x, y, x + 50, y + 50)
                self.after(50, lambda: move_request(x + 20, y, final_x, final_y))  # Move slower by incrementing x
            else:
                # When animation finishes, remove the label and update the queue if not blocked
                if blocked:
                    self.blocked_requests.append(request_label)
                else:
                    self.canvas.delete(request_label)
                    self.update_display()  # Update the queue colors only after animation completes

        # Move to Blocked Area if blocked, else move to queue end
        final_x, final_y = (1000, 80) if blocked else (900, 370)
        move_request(200, 370, final_x, final_y)

    def update_display(self, request_name=None, request_type=None, blocked=False):
        # Update queue slots with colors based on request types
        queue_items = list(self.server.queue.queue)
        for i in range(QUEUE_LENGTH):
            if i < len(queue_items):
                _, req_type = queue_items[i]
                color = REQUEST_COLORS.get(req_type, "white")
                self.canvas.itemconfig(self.queue_slots[i], fill=color)
            else:
                self.canvas.itemconfig(self.queue_slots[i], fill="white")

        # If a request is blocked, animate it moving to the Blocked Area
        if blocked and request_name and request_type:
            self.animate_request_to_queue(request_type, blocked=True)

        # Update log display with timestamps
        self.status_display.config(state="normal")
        self.status_display.delete(1.0, tk.END)
        for entry in self.server.log[-15:]:
            if "Queue is full" in entry:
                self.status_display.insert(tk.END, entry + "\n", "red")
                self.status_display.tag_config("red", foreground="red")
            else:
                self.status_display.insert(tk.END, entry + "\n")
        self.status_display.config(state="disabled")

        # Schedule the next update
        self.after(500, self.update_display)

    def on_closing(self):
        self.running = False
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
