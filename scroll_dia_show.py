import os
import tkinter as tk
from PIL import Image, ImageTk


_img_timeout_ms = 5000
_aspect_ratio_tolerance = 0.1

class ImageApp:
    def __init__(self, root, folder, canvas_width, canvas_height):
        self.tk_img = None
        self.root = root
        self.folder = folder
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
        self.canvas.pack()
        self.images = self.load_images()
        self.current_image_index = 0
        self.animation_tid = None
        self.animate_step = 0
        self.show_image()

    def load_images(self):
        images = []
        for filename in os.listdir(self.folder):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img = Image.open(os.path.join(self.folder, filename))
                if (img.width >= self.canvas_width) and (img.height >= self.canvas_height):
                    images.append(img)
                else:
                    print(f"Skipping img '{os.path.join(self.folder, filename)}', because resolution is too low. Minimum resolution is {self.canvas_width}x{self.canvas_height}")
        return images

    def show_image(self):
        img = self.images[self.current_image_index]
        img = self.resize_image(img)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.animate_step = 0
        self.animate(img)
        self.root.after(_img_timeout_ms, self.next_image)

    def resize_image(self, img):
        img_aspect_ratio = img.width / img.height
        canvas_aspect_ratio = self.canvas_width / self.canvas_height
        normalized_img_aspect_ratio = img_aspect_ratio

        if normalized_img_aspect_ratio < 1:
            normalized_img_aspect_ratio = 1/normalized_img_aspect_ratio

        # already has canvas dimensions
        if (img.width == self.canvas_width) and (img.height == self.canvas_height):
            print(f"{img.filename}: already has canvas dim of {img.width}x{img.height}")
            return img

        # img aspect ratio is within tolerable limits for rescaling to aspect ratio of canvas
        if (normalized_img_aspect_ratio < canvas_aspect_ratio * (1+_aspect_ratio_tolerance)) and (normalized_img_aspect_ratio > canvas_aspect_ratio * (1-_aspect_ratio_tolerance)):
            print(f"{img.filename}: aspect_ratio {normalized_img_aspect_ratio:.1f} of {img.width}x{img.height} is in tolerance. resize to canvas dim {self.canvas_width}x{self.canvas_height}")
            return img.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)

        fy = img.height / self.canvas_height
        fx = img.width / self.canvas_width

        # rescale so that one dimension matches canvas size
        if fx < fy:
            print(f"{img.filename}: {img.width}x{img.height} resize to {self.canvas_width}x{int(img.height / fx)}")
            img = img.resize((self.canvas_width, int(img.height / fx)), Image.Resampling.LANCZOS)
        else:
            print(f"{img.filename}: {img.width}x{img.height} resize to {int(img.width/fy)}x{self.canvas_height}")
            img = img.resize((int(img.width / fy), self.canvas_height), Image.Resampling.LANCZOS)

        return img

    def animate(self, img):
        img_width, img_height = img.size
        crop_width = self.canvas_width
        crop_height = self.canvas_height
        total_steps = 150
        delay = _img_timeout_ms / total_steps

        if img.width > img.height:  # Querformat
            x_step = (img_width - crop_width) / total_steps
            left = int(self.animate_step * x_step)
            top = 0
            right = left + crop_width
            bottom = crop_height
        else:  # Hochformat
            y_step = (img_height - crop_height) / total_steps
            left = 0
            top = img_height - crop_height - int(self.animate_step * y_step)
            right = crop_width
            bottom = top + crop_height

        cropped_img = img.crop((left, top, right, bottom))
        self.tk_img = ImageTk.PhotoImage(cropped_img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

        self.animate_step += 1
        if self.animate_step < total_steps:
            self.animation_tid = self.root.after(int(delay), self.animate, img)

    def next_image(self):
        if self.animation_tid:
            self.root.after_cancel(self.animation_tid)
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root, "gallery/test", 1280, 400)
    root.mainloop()