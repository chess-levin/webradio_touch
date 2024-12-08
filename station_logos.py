import sys
import os

from dataclasses import dataclass, field
from typing import List, Dict
from PIL import Image
import customtkinter as ctk

@dataclass
class LogoDist:
    directory: str
    img_ext: List[str]
    images: Dict[str, Image.Image] = field(init=False)
    default_logo_name: str

    def __post_init__(self):
        self.images = self.load_images_from_directory(self.directory, self.img_ext)

    @staticmethod
    def load_image(directory: str, filename: str):
        image = None
        try:
            filepath = os.path.join(directory, filename)

            image = Image.open(filepath)
        except OSError as e:
            print(f"Unable to open {filename}. Setting to None. Details : {e}", file=sys.stderr)

        return image

    @staticmethod
    def load_images_from_directory(directory: str, img_ext: List[str]) -> Dict[str, Image.Image]:
        images = {}
        for filename in os.listdir(directory):
            if any(filename.lower().endswith(ext) for ext in img_ext):
                    images[os.path.basename(filename)] = LogoDist.load_image(directory, filename)
                    print(f"added new logo '{os.path.basename(filename)}'")

        print(f"Loaded {len(images)} logos")
        return images

    def get_image(self, key: str) -> Image.Image:
        return self.images.get(key, self.get_default_image())

    def get_image_as_ctk(self, key: str, _logo_size):
        return ctk.CTkImage(self.get_image(key), size=(_logo_size, _logo_size))

    def get_default_image(self):
        return self.images.get(self.default_logo_name)

# Beispielverwendung
img_ext = ['.png', '.jpg', '.jpeg']
logo_dist = LogoDist(directory='logos', img_ext=img_ext, default_logo_name='dummy.jpg')
print(logo_dist.get_image("unkjonw").filename)
#print(logo_dist.images)