import cv2 # OpenCV for image processing
import tkinter as tk # GUI framework
from tkinter import filedialog, messagebox, Frame, Label, Button, Scale
from PIL import Image, ImageTk #  for handling images
import numpy as np # for numerical operations


class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Chitra Image Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#ADD8E6') # this sets the background color

        # this Handles window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Image Attributes
        self.original_image = None # Stores original image
        self.modified_image = None # Stores edited image
        self.history = [] # Stores edit history for undo
        self.redo_stack = [] # Stores redo actions
        self.crop_mode = False # Crop mode flag
        self.start_x = self.start_y = self.end_x = self.end_y = 0 # Crop coordinates

        # Scaling factors for the resizing
        self.scale_x = 1.0  # Horizontal scaling factor
        self.scale_y = 1.0  # Vertical scaling factor

        # This creates the UI Elements
        self.create_gui()
        self.bind_shortcuts()

        # This creates Footer Label with credit 
        Label(self.root, text="Made with ❤️ by Hadi, Akhil, Athira, Susan", fg='white', bg='#2D2D2D',
              font=('Segoe UI', 10)).pack(side=tk.BOTTOM, pady=10)

    def create_gui(self):
        """Creates the main GUI layout."""
        main_frame = Frame(self.root, bg='#ADD8E6')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # This creates the Canvas Frame for images 
        canvas_frame = Frame(main_frame, bg='#B0E0E6')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # for creating the left frame (Original Image)
        left_frame = Frame(canvas_frame, bg='black', bd=3, relief='solid')
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.original_canvas = tk.Canvas(left_frame, width=500, height=500, bg='white')
        self.original_canvas.pack()
        Label(left_frame, text="Original", bg='black', fg='white', font=('Segoe UI', 12, 'bold')).pack()

        # for creating the right frame (Modified Image)
        right_frame = Frame(canvas_frame, bg='black', bd=3, relief='solid')
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        self.modified_canvas = tk.Canvas(right_frame, width=500, height=500, bg='white')
        self.modified_canvas.pack()
        Label(right_frame, text="Edited", bg='black', fg='white', font=('Segoe UI', 12, 'bold')).pack()
        self.modified_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.modified_canvas.bind("<B1-Motion>", self.draw_crop_rectangle)
        self.modified_canvas.bind("<ButtonRelease-1>", self.end_crop)

        # Control Frame
        control_frame = Frame(main_frame, bg='#B0E0E6', pady=10)
        control_frame.pack(fill=tk.X)

        button_container = Frame(control_frame, bg='#B0E0E6')
        button_container.pack(expand=True)

        # definining the button styles 
        btn_style = {'font': ('Segoe UI', 10, 'bold'), 'bg': '#4A90E2', 'fg': 'black', 'bd': 0, 'padx': 15, 'pady': 8,
                     'relief': 'flat'}

        # This creates buttons for various functions i.e. load, save, undo, redo, grayscale, rotate and crop the image
        buttons = [
            Button(button_container, text="Load Image", command=self.load_image, **btn_style),
            Button(button_container, text="Save Image", command=self.save_image, **btn_style),
            Button(button_container, text="Undo", command=self.undo, **btn_style),
            Button(button_container, text="Redo", command=self.redo, **btn_style),
            Button(button_container, text="Grayscale", command=self.apply_grayscale, **btn_style),
            Button(button_container, text="Rotate 90°", command=self.rotate_image, **btn_style),
            Button(button_container, text="Crop", command=self.enable_crop_mode, **btn_style)
        ]
        # this packs buttons horizontally
        for btn in buttons:
            btn.pack(side=tk.LEFT, padx=5)

        # For resizing the image
        self.resize_scale = Scale(control_frame, from_=10, to=200, orient=tk.HORIZONTAL, label="Resize (%) ",
                                  bg='#B0E0E6')
        self.resize_scale.set(100)
        self.resize_scale.pack(pady=10)
        self.resize_scale.bind("<Motion>", self.preview_resize)

    def bind_shortcuts(self):
        """This binds keyboard shortcuts for quick access."""
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-s>", lambda e: self.save_image())

    def load_image(self):
        """This will load an image from the file system."""
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        try:
            self.original_image = cv2.imread(file_path)
            if self.original_image is None:
                raise ValueError("Failed to load image.")
            self.modified_image = self.original_image.copy()
            self.history = [self.modified_image.copy()]
            self.redo_stack = []
            self.show_images()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_images(self):
        """This displays the loaded images on the canvas."""
        if self.original_image is not None:
            self.display_image(self.original_image, self.original_canvas)
        if self.modified_image is not None:
            self.display_image(self.modified_image, self.modified_canvas)

    def display_image(self, image, canvas):
        """Displays an image on the given canvas after resizing it."""
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # for converting the color format
        img = Image.fromarray(img)
        original_width, original_height = img.size

        # Resize image to fit within 500x500 while maintaining aspect ratio to fit canvas
        img.thumbnail((500, 500)) 
        resized_width, resized_height = img.size

        # Calculate scaling factors
        self.scale_x = original_width / resized_width
        self.scale_y = original_height / resized_height

        img_tk = ImageTk.PhotoImage(img)
        canvas.config(width=resized_width, height=resized_height)  # Adjust canvas size dynamically
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk

    def save_image(self):
        """Saves the modified image to a file."""
        if self.modified_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                cv2.imwrite(file_path, self.modified_image)
                messagebox.showinfo("Success", "Image saved successfully!")

    def undo(self): #jumps into the previous action
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.modified_image = self.history[-1].copy()
            self.show_images()

    def redo(self): #redo the action
        if self.redo_stack:
            self.history.append(self.modified_image.copy())  # Save current state before redoing
            self.modified_image = self.redo_stack.pop()
            self.show_images()

    def apply_grayscale(self): #for applying grayscale effect in the image
        if self.modified_image is not None:
            self.history.append(self.modified_image.copy())
            gray = cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2GRAY)
            self.modified_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            self.show_images()

    def rotate_image(self): # for rotating the image by 90 degree
        if self.modified_image is not None:
            self.history.append(self.modified_image.copy())
            self.modified_image = cv2.rotate(self.modified_image, cv2.ROTATE_90_CLOCKWISE)
            self.show_images()

    def enable_crop_mode(self): # for cropping the image 
        self.crop_mode = True

    def start_crop(self, event):
        if self.crop_mode:
            self.start_x, self.start_y = event.x, event.y

    def draw_crop_rectangle(self, event):
        if self.crop_mode:
            self.modified_canvas.delete("crop_rect")
            self.end_x, self.end_y = event.x, event.y
            self.modified_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red",
                                                  tags="crop_rect")

            #This displays temporary thumbnail of the cropped area
            try:
                x1, y1 = int(self.start_x * self.scale_x), int(self.start_y * self.scale_y)
                x2, y2 = int(self.end_x * self.scale_x), int(self.end_y * self.scale_y)
                x1, x2 = sorted([x1, x2])
                y1, y2 = sorted([y1, y2])

                if x1 != x2 and y1 != y2:  # Ensure valid crop area
                    cropped = self.modified_image[y1:y2, x1:x2]
                    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                    cropped = Image.fromarray(cropped)
                    cropped.thumbnail((100, 100))  # Create a small thumbnail
                    cropped_tk = ImageTk.PhotoImage(cropped)

                    # Displays the thumbnail in a popup or overlay
                    if not hasattr(self, "thumbnail_label"):
                        self.thumbnail_label = Label(self.root, bg="white")
                        self.thumbnail_label.place(x=10, y=10)  # Position the thumbnail
                    self.thumbnail_label.config(image=cropped_tk)
                    self.thumbnail_label.image = cropped_tk
            except Exception as e:
                pass  #This ignores errors during thumbnail creation

    def end_crop(self, event):
        if self.crop_mode:
            self.crop_mode = False
            x1, y1 = int(self.start_x * self.scale_x), int(self.start_y * self.scale_y)
            x2, y2 = int(self.end_x * self.scale_x), int(self.end_y * self.scale_y)

            # Ensure valid crop area
            if x1 == x2 or y1 == y2:
                messagebox.showwarning("Invalid Crop", "Crop area is too small.")
                return

            # Sort coordinates to handle reverse dragging
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])

            # Crop the image
            try:
                self.history.append(self.modified_image.copy())
                self.modified_image = self.modified_image[y1:y2, x1:x2]
                self.modified_canvas.delete("crop_rect")  # Remove selection box
                self.show_images()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to crop image: {str(e)}")
    #For the resizing of image
    def preview_resize(self, event):
        if self.modified_image is not None:
            scale = self.resize_scale.get() / 100.0
            h, w = self.modified_image.shape[:2]
            new_size = (int(w * scale), int(h * scale))
            resized = cv2.resize(self.modified_image, new_size)
            self.display_image(resized, self.modified_canvas)

    def confirm_resize(self):
        if self.modified_image is not None:
            scale = self.resize_scale.get() / 100.0
            h, w = self.modified_image.shape[:2]
            new_size = (int(w * scale), int(h * scale))

            # Use different interpolation methods based on scale
            if scale < 0.5:
                resized = cv2.resize(self.modified_image, new_size, interpolation=cv2.INTER_NEAREST)  # Low-quality
            else:
                resized = cv2.resize(self.modified_image, new_size, interpolation=cv2.INTER_LINEAR)  # Higher-quality

            self.history.append(self.modified_image.copy())
            self.modified_image = resized
            self.show_images()

    def on_closing(self):
        """Intercept the close event and show a feedback popup."""
        self.show_satisfaction_popup()

    def show_satisfaction_popup(self): # Satisfaction window will appear
        satisfaction_popup = tk.Toplevel(self.root)
        satisfaction_popup.title("Feedback")
        satisfaction_popup.geometry("300x150")
        satisfaction_popup.resizable(False, False)
        satisfaction_popup.grab_set()  # Make it modal (block interaction with the main window)

        Label(satisfaction_popup, text="How was your experience?", font=('Segoe UI', 12)).pack(pady=10)

        def close_app(): 
            satisfaction_popup.destroy()
            self.root.quit()

        Button(satisfaction_popup, text="😊 Happy", font=('Segoe UI', 12),
               command=lambda: [messagebox.showinfo("Feedback", "Thank you for your positive feedback!"), close_app()]).pack(pady=5)
        Button(satisfaction_popup, text="😡 Angry", font=('Segoe UI', 12),
               command=lambda: [messagebox.showinfo("Feedback", "We’re sorry to hear that!"), close_app()]).pack(pady=5)
        Button(satisfaction_popup, text="😕 Confused", font=('Segoe UI', 12),
               command=lambda: [messagebox.showinfo("Feedback", "Let us know what’s unclear!"), close_app()]).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop() # Starts the application
