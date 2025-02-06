import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, Frame, Label, Button, Scale
from PIL import Image, ImageTk
import numpy as np

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#ADD8E6')
        
        
        # Image Attributes
        self.original_image = None
        self.modified_image = None
        self.history = []
        self.redo_stack = []
        self.crop_mode = False
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        
        # UI Elements
        self.create_gui()
        self.bind_shortcuts()
        
        # Footer Label
        Label(self.root, text="Made with ❤️ by Hadi, Akhil, Athira, Susan", fg='white', bg='#2D2D2D',
              font=('Segoe UI', 10)).pack(side=tk.BOTTOM, pady=10)


    def create_gui(self):
        main_frame = Frame(self.root, bg='#ADD8E6')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.canvas_frame = Frame(main_frame, bg='#B0E0E6')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.left_frame = Frame(self.canvas_frame, bg='black', bd=3, relief='solid')
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.right_frame = Frame(self.canvas_frame, bg='black', bd=3, relief='solid')
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.original_canvas = tk.Canvas(self.left_frame, width=500, height=500, bg='white')
        self.original_canvas.pack()
        
        self.modified_canvas = tk.Canvas(self.right_frame, width=500, height=500, bg='white')
        self.modified_canvas.pack()
        self.modified_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.modified_canvas.bind("<B1-Motion>", self.draw_crop_rectangle)
        self.modified_canvas.bind("<ButtonRelease-1>", self.end_crop)
        
        control_frame = Frame(main_frame, bg='#B0E0E6', pady=10)
        control_frame.pack(fill=tk.X)
        
        button_container = Frame(control_frame, bg='#B0E0E6')
        button_container.pack(expand=True)
        
        btn_style = {'font': ('Segoe UI', 10, 'bold'), 'bg': '#4A90E2', 'fg': 'black', 'bd': 0, 'padx': 15, 'pady': 8, 'relief': 'flat'}
        
        buttons = [
            Button(button_container, text="Load Image", command=self.load_image, **btn_style),
            Button(button_container, text="Save Image", command=self.save_image, **btn_style),
            Button(button_container, text="Undo", command=self.undo, **btn_style),
            Button(button_container, text="Redo", command=self.redo, **btn_style),
            Button(button_container, text="Grayscale", command=self.apply_grayscale, **btn_style),
            Button(button_container, text="Rotate 90°", command=self.rotate_image, **btn_style),
            Button(button_container, text="Crop", command=self.enable_crop_mode, **btn_style)
        ]
        
        for btn in buttons:
            btn.pack(side=tk.LEFT, padx=5)
        
        self.resize_scale = Scale(control_frame, from_=10, to=200, orient=tk.HORIZONTAL, label="Quality Scale (%)", bg='#B0E0E6')
        self.resize_scale.set(100)
        self.resize_scale.pack(pady=10)
        self.resize_scale.bind("<Motion>", self.preview_resize)


    def bind_shortcuts(self):
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-s>", lambda e: self.save_image())
    
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.original_image = cv2.imread(file_path)
        self.modified_image = self.original_image.copy()
        self.history = [self.modified_image.copy()]
        self.redo_stack = []
        self.show_images()
    
    def show_images(self):
        if self.original_image is not None:
            self.display_image(self.original_image, self.original_canvas)
        if self.modified_image is not None:
            self.display_image(self.modified_image, self.modified_canvas)
    
    def display_image(self, image, canvas):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.thumbnail((500, 500))
        img_tk = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk
    
    def save_image(self):
        if self.modified_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                cv2.imwrite(file_path, self.modified_image)
                messagebox.showinfo("Success", "Image saved successfully!")
    
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.modified_image = self.history[-1].copy()
            self.show_images()
    
    def redo(self):
       if self.redo_stack:
           self.history.append(self.modified_image.copy())  # Save current state before redoing
           self.modified_image = self.redo_stack.pop()
           self.show_images()

    
    def apply_grayscale(self):
        if self.modified_image is not None:
            self.history.append(self.modified_image.copy())
            gray = cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2GRAY)
            self.modified_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            self.show_images()
    
    def rotate_image(self):
        if self.modified_image is not None:
            self.history.append(self.modified_image.copy())
            self.modified_image = cv2.rotate(self.modified_image, cv2.ROTATE_90_CLOCKWISE)
            self.show_images()
    
    def enable_crop_mode(self):
        self.crop_mode = True
    
    def start_crop(self, event):
        if self.crop_mode:
            self.start_x, self.start_y = event.x, event.y
    
    def draw_crop_rectangle(self, event):
        if self.crop_mode:
            self.modified_canvas.delete("crop_rect")
            self.end_x, self.end_y = event.x, event.y
            self.modified_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red", tags="crop_rect")
    
    def end_crop(self, event):
        if self.crop_mode:
            self.crop_mode = False
            x1, y1, x2, y2 = self.start_x, self.start_y, self.end_x, self.end_y
            if x1 != x2 and y1 != y2:
                self.history.append(self.modified_image.copy())
                self.modified_image = self.modified_image[y1:y2, x1:x2]
                self.modified_canvas.delete("crop_rect")  # Remove selection box
                self.show_images()
    
    def preview_resize(self, event):
        if self.modified_image is not None:
            scale = self.resize_scale.get() / 100.0
            h, w = self.modified_image.shape[:2]
            new_size = (int(w * scale), int(h * scale))
            resized = cv2.resize(self.modified_image, new_size)
            self.display_image(resized, self.modified_canvas)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()