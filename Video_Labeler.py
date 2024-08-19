import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2

MAX_PREVIEW_FRAMES = 8

class VideoLabelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Labeler")

        self.video_path = self.load_video()
        self.video_capture = cv2.VideoCapture(self.video_path)

        if not self.video_capture.isOpened():
            messagebox.showerror("Error", "Failed to open video.")
            self.root.destroy()
            return

        self.current_frame_index = 0
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.labels = {}
        self.label_listbox = None
        self.display_frame_index = 0

        self.create_widgets()
        self.display_frame()

    def load_video(self):
        file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if not file_path:
            messagebox.showerror("Error", "No file selected.")
            self.root.destroy()
            return ""

        return file_path
    
    def get_labels(self):
        if (self.label_listbox is None) or (self.label_listbox.size() == 0):
            return None
        return [label for label in self.label_listbox.get(0, tk.END)]

    def create_widgets(self):
            # Main frame
            self.main_frame = tk.Frame(self.root)
            self.main_frame.pack(fill=tk.BOTH, expand=True)
    
            # Left frame for live labels and label adding
            self.left_frame = tk.Frame(self.main_frame)
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            self.export_labels_button = tk.Button(self.left_frame, text="Export Labels", command=self.export_labels_alone)
            self.export_labels_button.pack()

            # Right frame for video and its label editing
            self.right_frame = tk.Frame(self.main_frame)
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            self.save_labels_button = tk.Button(self.right_frame, text="Save Labels", command=self.save_labels_to_file)
            self.save_labels_button.pack()
            
            
            self.bottom_frame = tk.Frame(self.root)
            self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

            # Create a frame to hold the previews and navigation buttons
            self.preview_frame = tk.Frame(self.bottom_frame)
            self.preview_frame.pack(fill=tk.X)

            # Create labels for the previews
            self.preview_labels = []
            self.preview_numbers = []
            for i in range(MAX_PREVIEW_FRAMES):
                if self.current_frame_index + i < self.total_frames:
                    frame_image = self.get_frame_preview(self.current_frame_index + i)
                    if frame_image is None:
                        break
                    preview_label = tk.Label(self.preview_frame, image=frame_image)
                    preview_label.image = frame_image 
                    preview_label.grid(row=0, column=i, padx=5, pady=5)
                    preview_label.bind("<Button-1>", lambda event, frame_index=self.current_frame_index + i: self.on_preview_click(event, frame_index))
                    self.preview_labels.append(preview_label)
                    
                    preview_number = tk.Label(self.preview_frame, text=f"Frame: {self.current_frame_index + i + 1}")
                    preview_number.grid(row=1, column=i, padx=5, pady=5)
                    self.preview_numbers.append(preview_number)

            # Create a frame to hold the navigation buttons
            self.nav_button_frame = tk.Frame(self.bottom_frame)
            self.nav_button_frame.pack(side=tk.BOTTOM, fill=tk.X)
            # Backward button
            self.backward_10_button = tk.Button(self.nav_button_frame, text="<<", command=self.backward_10_frame)
            self.backward_10_button.pack(side=tk.LEFT, padx=10, pady=10)
          
            self.backward_button = tk.Button(self.nav_button_frame, text="<", command=self.backward_frame)
            self.backward_button.pack(side=tk.LEFT, padx=10, pady=10)
            # Forward button
            self.forward_10_button = tk.Button(self.nav_button_frame, text=">>", command=self.forward_10_frame)
            self.forward_10_button.pack(side=tk.RIGHT, padx=10, pady=10)
            
            self.forward_button = tk.Button(self.nav_button_frame, text=">", command=self.forward_frame)
            self.forward_button.pack(side=tk.RIGHT, padx=10, pady=10)
            
            
            
            
    
            # Video and its label editing (Right frame)
            self.video_label = tk.Label(self.right_frame)
            self.video_label.pack()
            
            self.frame_label = tk.Label(self.right_frame, text=f"Frame: {self.current_frame_index + 1}/{self.total_frames}")
            self.frame_label.pack()
            self.selected_label = tk.StringVar(self.right_frame)

            # OptionMenu for the dropdown
            labels = self.get_labels()
            if labels:
                self.label_dropdown = tk.OptionMenu(self.right_frame, self.selected_label, *labels)
            else:
                self.label_dropdown = tk.OptionMenu(self.right_frame, self.selected_label, "No Labels currently")
            self.label_dropdown.config(width=50)
            self.label_dropdown.pack()
            self.selected_label.trace('w', self.update_live_label)
            
            self.button_frame = tk.Frame(self.right_frame)
            self.button_frame.pack()
            self.back_30_button = tk.Button(self.button_frame, text="Previous 30 Frame", command=self.previous_30_frame)
            self.back_30_button.config(state=tk.DISABLED)
            self.back_30_button.pack(side=tk.LEFT)
            self.previous_button = tk.Button(self.button_frame, text="Previous", command=self.previous_frame)
            self.previous_button.pack(side=tk.LEFT)
            self.remove_button = tk.Button(self.button_frame, text="Remove Label", command=self.remove_image_label)
            self.remove_button.config(state=tk.DISABLED)
            self.remove_button.pack(side=tk.LEFT)
            self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_label)
            self.save_button.pack(side=tk.LEFT)  # side=tk.LEFT
            self.assign_last_label = tk.Button(self.button_frame, text="Assign Last Label", command=self.assign_previous_label)
            self.assign_last_label.config(state=tk.DISABLED)
            self.assign_last_label.pack(side=tk.LEFT)  # side=tk.LEFT
            self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_frame)
            self.next_button.pack(side=tk.LEFT)
            self.next_30_button = tk.Button(self.button_frame, text="Next 30 Frame", command=self.next_30_frame)
            self.next_30_button.config(state=tk.DISABLED)
            self.next_30_button.pack(side=tk.LEFT)
            if self.current_frame_index == 0:
                self.previous_button.config(state=tk.DISABLED)
            self.live_label = tk.Label(self.right_frame, text="", fg="blue")
            self.live_label.pack(side=tk.BOTTOM)
    
            self.label_listbox = tk.Listbox(self.left_frame)
            self.label_listbox.pack()
            self.custom_label_entry = tk.Entry(self.left_frame, width=50)
            self.custom_label_entry.insert(0, "Enter Label Here")
            self.custom_label_entry.pack()
            self.add_label_button = tk.Button(self.left_frame, text="Add Label", command=self.add_label)
            self.add_label_button.pack()
            self.remove_label_button = tk.Button(self.left_frame, text="Remove Label", command=self.remove_label)
            self.remove_label_button.pack()
            self.update_dropdown()
            
            messagebox.showinfo("Loaded the Video")
            
    def on_preview_click(self, event, frame_index):
        self.current_frame_index = frame_index
        if self.current_frame_index != 0:
            self.previous_button.config(state="normal")
        else:
            self.previous_button.config(state="disabled")
        if self.current_frame_index + 1 < self.total_frames:
            self.next_button.config(state="normal")
        else:
            self.next_button.config(state="disabled")
        print(f"Preview clicked: {self.current_frame_index}")
        
        self.display_frame()
            
    def update_dropdown(self):
        # Clear the current options in the dropdown
        self.label_dropdown["menu"].delete(0, "end")

        # Get the updated list of labels
        labels = self.get_labels()
        if labels:
            for label in labels:
                self.label_dropdown["menu"].add_command(label=label, command=lambda value=label: self.selected_label.set(value))
            self.save_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.label_dropdown.config(state="normal")
        else:
            self.label_dropdown["menu"].add_command(label="No Labels currently", command=lambda: self.selected_label.set("No Labels currently"))
            self.save_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.label_dropdown.config(state="disabled")
            self.selected_label.set("No Labels currently")
        
    def update_previews(self):
        for i in range(MAX_PREVIEW_FRAMES):
            frame_index = self.display_frame_index + i
            if frame_index < self.total_frames:
                frame_image = self.get_frame_preview(frame_index)
                if frame_image:
                    self.preview_labels[i].config(image=frame_image)
                    self.preview_labels[i].image = frame_image 
                    self.preview_labels[i].bind("<Button-1>", lambda event, frame_index=frame_index: self.on_preview_click(event, frame_index))
                    self.preview_numbers[i].config(text=f"Frame: {frame_index + 1}")
            else:
                self.preview_labels[i].config(image='', text="No Frame")
                self.preview_labels[i].unbind("<Button-1>")
                self.preview_numbers[i].config(text="")

    def backward_10_frame(self):
        if self.display_frame_index - 10 > 0:
            self.display_frame_index -= 10
        else:
            self.display_frame_index = 0
        self.update_previews()
    
    def forward_10_frame(self):
        if self.display_frame_index + MAX_PREVIEW_FRAMES + 10 <= self.total_frames:
            self.display_frame_index += 10
        else:
            self.display_frame_index = self.total_frames - MAX_PREVIEW_FRAMES
        self.update_previews()
    
    def backward_frame(self):
        if self.display_frame_index > 0:
            self.display_frame_index -= 1
            self.update_previews()
    
    def forward_frame(self):
        if self.display_frame_index + MAX_PREVIEW_FRAMES + 1 <= self.total_frames:
            self.display_frame_index += 1
            self.update_previews()
    
    def add_label(self):
        label = self.custom_label_entry.get()
        if label and label != "Enter Label Here":
            if  (self.get_labels() == None) or (label not in self.get_labels()): 
                self.label_listbox.insert(tk.END, label)
                self.custom_label_entry.delete(0, tk.END)
                self.update_dropdown()

    def remove_label(self):
        selected_label_index = self.label_listbox.curselection()
        if selected_label_index:
            value = self.label_listbox.get(selected_label_index)
            keys_to_delete = [key for key, val in self.labels.items() if val == value]
            for key in keys_to_delete:
                del self.labels[key]
            self.label_listbox.delete(selected_label_index)
            self.update_dropdown()
    
    def get_frame_preview(self, frame_index):
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (100, 75))
            return ImageTk.PhotoImage(Image.fromarray(frame))
        return None
            
    def get_frame(self, frame_index):
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape
            resized_frame = cv2.resize(frame, (width // 2, height // 2))  # Resize frame to half its original dimensions
            return ImageTk.PhotoImage(Image.fromarray(resized_frame))
        return None

    def update_buttons(self, button_state):
        self.previous_button.config(state=button_state)
        self.next_button.config(state=button_state)
        self.next_30_button.config(state=button_state)
        self.back_30_button.config(state=button_state)
        self.remove_button.config(state=button_state)
        
    def check_if_previous_label_exists(self):
        if self.current_frame_index > 0:
            previous_keys = [key for key in self.labels.keys() if key < self.current_frame_index]
            if previous_keys:
                previous_key = max(previous_keys)
                if self.labels.get(previous_key, ""):
                    self.assign_last_label.config(state=tk.NORMAL)
                else:
                    self.assign_last_label.config(state=tk.DISABLED)
            else:
                self.assign_last_label.config(state=tk.DISABLED)
        else:
            self.assign_last_label.config(state=tk.DISABLED)

    def display_frame(self):
        if self.current_frame_index < self.total_frames:
            self.update_dropdown()
            self.frame_label.config(text=f"Frame: {self.current_frame_index + 1}/{self.total_frames}")
            photo = self.get_frame(self.current_frame_index)
            self.check_if_previous_label_exists()
            if self.labels.get(self.current_frame_index, ""):
                self.selected_label.set(self.labels.get(self.current_frame_index))
                self.live_label.config(text=f"Live label: {self.labels.get(self.current_frame_index)}")
                self.update_buttons(tk.NORMAL)
            else:
                self.selected_label.set("No labels Selected")
                self.live_label.config(text="Live label: No labels Selected")
                self.update_buttons(tk.DISABLED)
                
            if photo:
                self.video_label.config(image=photo)
                self.video_label.image = photo

                label = self.labels.get(self.current_frame_index, "")
                self.live_label.config(text=f"Live label: {label}")
            else:
                messagebox.showerror("Error", "Failed to read the frame.")

    def update_live_label(self, *args):
        selected_label = self.selected_label.get()
        self.live_label.config(text="Live label: " + selected_label)
        
    def previous_30_frame(self):
        self.current_frame_index -= 30
        if self.current_frame_index < 0:
            messagebox.showerror("Error", "No previous frames.")
            self.current_frame_index = 0
        else:
            self.selected_label.set(self.labels.get(self.current_frame_index, "No labels Selected"))
            self.display_frame_index = self.current_frame_index
            if (self.current_frame_index) != 0:
                self.previous_button.config(state=tk.NORMAL)
            else:
                self.previous_button.config(state=tk.DISABLED)
        self.update_previews()
        self.display_frame()
                
    def next_30_frame(self):
        self.current_frame_index += 30
        if self.current_frame_index < self.total_frames:
            self.display_frame_index = self.current_frame_index
            self.update_previews()
            self.display_frame()
        else:
            self.current_frame_index = self.total_frames - 1
            self.update_previews()
            self.display_frame()
            messagebox.showerror("Error", "No next frames.")
    
    def assign_previous_label(self):
        if self.current_frame_index > 0:
            # Find the largest key smaller than the current frame index
            previous_keys = [key for key in self.labels.keys() if key < self.current_frame_index]
            if previous_keys:
                previous_key = max(previous_keys)
                for key in range(previous_key, self.current_frame_index + 1):
                    self.labels[key] = self.labels[previous_key]
                self.selected_label.set(self.labels.get(previous_key, "No labels Selected"))
                
                self.update_previews()
                self.display_frame()
                 
    def previous_frame(self):
        self.current_frame_index -= 1
        if self.current_frame_index < 0:
            messagebox.showerror("Error", "No previous frames.")
            self.current_frame_index = 0
        else:
            self.selected_label.set(self.labels.get(self.current_frame_index, "No labels Selected"))
            self.display_frame_index = self.current_frame_index
            self.update_previews()
            self.display_frame()
            if (self.current_frame_index) != 0:
                self.previous_button.config(state=tk.NORMAL)
            else:
                self.previous_button.config(state=tk.DISABLED)
    
    def next_frame(self):
        # Move to the next frame without saving the current label
        if self.current_frame_index in self.labels.keys():
            self.current_frame_index += 1
            if not (self.current_frame_index >= self.total_frames):
                self.selected_label.set("No labels Selected")
                self.display_frame_index = self.current_frame_index
                self.update_previews()
                self.display_frame()
        else:
            messagebox.showerror("Error", "Please save the label before moving to the next frame.")

    def save_label(self):
        if self.live_label.cget("text") == "Live label: ":  # No label entered
            messagebox.showerror("Error", "Please enter a label.")
            return
        if self.current_frame_index < self.total_frames:
            new_label = self.selected_label.get()
            self.update_buttons(tk.NORMAL)
            self.labels[self.current_frame_index] = new_label

    def remove_image_label(self):
        if self.current_frame_index in self.labels.keys():
            del self.labels[self.current_frame_index]
            self.selected_label.set("No labels Selected")
            self.update_buttons(tk.DISABLED)
            self.display_frame()
        else:
            messagebox.showerror("Error", "No label to remove.")

    def save_labels_to_file(self):
        if self.labels:
            save_path = filedialog.asksaveasfilename(title="Save Labels", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(save_path, 'w') as file:
                    for frame_index, label in self.labels.items():
                        file.write(f"{frame_index}\t{label}\n")
                messagebox.showinfo("Saved", f"Labels saved to {save_path}")
        else:
            messagebox.showerror("Error", "No labels to save.")
                
    def export_labels_alone(self):
        labels = self.label_listbox.get(0, tk.END)
        if labels:
            save_path = filedialog.asksaveasfilename(title="Save Mapping Labels", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(save_path, 'w') as file:
                    for index, label in enumerate(labels):
                        file.write(f"{index}\t{label}\n")
                messagebox.showinfo("Saved", f"Labels saved to {save_path}")
        else:
            messagebox.showerror("Error", "No labels to export.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoLabelApp(root)
    root.mainloop()
