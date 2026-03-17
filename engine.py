import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk, ImageOps
import random
import numpy as np
import os
import urllib.request
import string
import math
import json

class SyntheticJerseyEngine:
    def __init__(self):
        # Top 25 Most Common / Iconic Hockey Jersey Colors
        self.jersey_colors =[
            (17, 17, 17),    # Black
            (240, 240, 240), # White
            (0, 32, 91),     # Navy Blue
            (0, 56, 168),    # Royal Blue
            (206, 17, 38),   # Red
            (134, 38, 51),   # Crimson
            (0, 104, 71),    # Kelly Green
            (2, 73, 48),     # Forest Green
            (0, 109, 117),   # Teal
            (247, 73, 2),    # Orange
            (252, 181, 20),  # Yellow/Gold
            (185, 151, 91),  # Vegas Gold
            (162, 170, 173), # Silver
            (104, 162, 185), # Light Blue
            (0, 22, 40),     # Dark Navy
            (80, 43, 133),   # Purple
            (111, 38, 61),   # Maroon/Burgundy
            (197, 90, 17),   # Copper
            (204, 0, 0),     # Carolina Red
            (79, 46, 109),   # Eggplant
            (0, 104, 94),    # Jade Green
            (65, 143, 222),  # Columbia Blue
            (218, 165, 32),  # Mustard Yellow
            (241, 230, 178), # Vintage Cream
            (8, 112, 129),   # Deep Teal
        ]
        
        self.fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        os.makedirs(self.fonts_dir, exist_ok=True)
        self.font_paths = self._ensure_fonts_downloaded()

    def _ensure_fonts_downloaded(self):
        fonts_to_get = {
            "1_Varsity_Block.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/graduate/Graduate-Regular.ttf",
            "2_Modern_Angled.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/russoone/RussoOne-Regular.ttf",
            "3_Tall_Condensed.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf",
            "4_Heavy_Block.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf",
            "5_Spurred_NHL.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/blackopsone/BlackOpsOne-Regular.ttf"
        }
        
        paths =[]
        for name, url in fonts_to_get.items():
            path = os.path.join(self.fonts_dir, name)
            if not os.path.exists(path):
                try:
                    print(f"Downloading {name}...")
                    urllib.request.urlretrieve(url, path)
                except Exception:
                    pass
            if os.path.exists(path):
                paths.append(path)
                
        if not paths: paths =["impact.ttf", "arialbd.ttf"]
        return paths

    def get_font(self, size):
        chosen = random.choice(self.font_paths)
        try:
            return ImageFont.truetype(chosen, size)
        except IOError:
            return ImageFont.load_default()

    def get_contrasting_colors(self):
        bg_color = random.choice(self.jersey_colors)
        jr, jg, jb = bg_color
        
        luminance = 0.299 * jr + 0.587 * jg + 0.114 * jb
        
        if luminance > 128:
            text_color = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50))
            outline_color = (255, 255, 255)
        else:
            text_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            outline_color = (0, 0, 0)
            
        return bg_color, text_color, outline_color

    def draw_text_with_outline(self, draw, x, y, text, font, text_color, outline_color, thickness=3):
        for dx in range(-thickness, thickness+1):
            for dy in range(-thickness, thickness+1):
                if dx*dx + dy*dy > thickness*thickness: continue
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=text_color)

    def apply_text_style_transform(self, text_img):
        stretch_x = random.uniform(0.82, 1.24)
        stretch_y = random.uniform(0.88, 1.08)
        resized_width = max(1, int(round(text_img.width * stretch_x)))
        resized_height = max(1, int(round(text_img.height * stretch_y)))
        text_img = text_img.resize((resized_width, resized_height), resample=Image.BICUBIC)

        if random.random() > 0.2:
            shear = random.uniform(-0.22, 0.22)
            xshift = abs(shear) * text_img.height
            transformed_width = max(1, int(round(text_img.width + xshift)))
            text_img = text_img.transform(
                (transformed_width, text_img.height),
                Image.AFFINE,
                (1, shear, -xshift if shear > 0 else 0, 0, 1, 0),
                resample=Image.BICUBIC,
                fillcolor=(0, 0, 0, 0),
            )

        if random.random() > 0.6:
            blur_radius = random.uniform(0.0, 0.45)
            if blur_radius > 0.05:
                text_img = text_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        alpha_bbox = text_img.getchannel("A").getbbox()
        if alpha_bbox:
            text_img = text_img.crop(alpha_bbox)
        return text_img

    def render_number_layer(self, player_number, base_size, text_color, outline_color):
        measure_img = Image.new("L", (1, 1), 0)
        measure_draw = ImageDraw.Draw(measure_img)
        font = self.get_font(random.randint(102, 128))
        outline_thickness = random.randint(2, 6)
        glyph_margin = outline_thickness + 6
        inter_digit_spacing = random.randint(-3, 3)

        glyphs = []
        cursor_x = 0
        max_right = 0
        max_height = 0
        digit_offsets = [random.randint(-2, 2) for _ in player_number]

        for digit, digit_y_offset in zip(player_number, digit_offsets):
            bbox = measure_draw.textbbox((0, 0), digit, font=font)
            glyph_width = max(1, bbox[2] - bbox[0])
            glyph_height = max(1, bbox[3] - bbox[1])
            glyph_img = Image.new(
                "RGBA",
                (glyph_width + glyph_margin * 2, glyph_height + glyph_margin * 2),
                (0, 0, 0, 0),
            )
            glyph_draw = ImageDraw.Draw(glyph_img)
            self.draw_text_with_outline(
                glyph_draw,
                glyph_margin - bbox[0],
                glyph_margin - bbox[1],
                digit,
                font,
                text_color,
                outline_color,
                thickness=outline_thickness,
            )
            glyphs.append((glyph_img, cursor_x, digit_y_offset))
            max_right = max(max_right, cursor_x + glyph_img.width)
            max_height = max(max_height, glyph_img.height + abs(digit_y_offset))
            if len(player_number) > 1:
                advance_width = glyph_width + outline_thickness * 2 + inter_digit_spacing
            else:
                advance_width = glyph_width + glyph_margin
            cursor_x += max(1, advance_width)

        number_img = Image.new("RGBA", (max_right, max_height + 4), (0, 0, 0, 0))
        for glyph_img, glyph_x, digit_y_offset in glyphs:
            glyph_y = max(0, (number_img.height - glyph_img.height) // 2 + digit_y_offset)
            number_img.alpha_composite(glyph_img, (glyph_x, glyph_y))

        number_img = self.apply_text_style_transform(number_img)
        max_number_width = int(base_size * 0.82)
        max_number_height = int(base_size * 0.56)
        fit_scale = min(
            max_number_width / max(1, number_img.width),
            max_number_height / max(1, number_img.height),
            1.0,
        )
        if fit_scale < 1.0:
            fit_width = max(1, int(round(number_img.width * fit_scale)))
            fit_height = max(1, int(round(number_img.height * fit_scale)))
            number_img = number_img.resize((fit_width, fit_height), resample=Image.BICUBIC)

        layer = Image.new("RGBA", (base_size, base_size), (0, 0, 0, 0))
        target_center_y = int(base_size * random.uniform(0.56, 0.6))
        paste_x = max(0, (base_size - number_img.width) // 2)
        paste_y = max(0, int(round(target_center_y - number_img.height / 2)))
        paste_y = min(max(0, base_size - number_img.height), paste_y)
        layer.alpha_composite(number_img, (paste_x, paste_y))

        number_bbox = layer.getchannel("A").getbbox()
        if number_bbox is None:
            fallback_size = max(40, base_size // 3)
            fallback_left = (base_size - fallback_size) // 2
            fallback_top = (base_size - fallback_size) // 2
            number_bbox = (
                fallback_left,
                fallback_top,
                fallback_left + fallback_size,
                fallback_top + fallback_size,
            )
        return layer, number_bbox

    def apply_fabric_distortion(self, img):
        arr = np.array(img)
        h, w = arr.shape[:2]
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        fold_x_freq = random.uniform(12, 34)
        fold_x_amp = random.uniform(6, 15)
        secondary_x_freq = random.uniform(20, 52)
        secondary_x_amp = random.uniform(2, 6)
        x_phase_tilt = random.uniform(0.08, 0.22)
        shift_x = np.sin(y / fold_x_freq) * fold_x_amp
        shift_x += np.sin((y + x * x_phase_tilt) / secondary_x_freq) * secondary_x_amp
        
        fold_y_freq = random.uniform(16, 42)
        fold_y_amp = random.uniform(4, 10)
        secondary_y_freq = random.uniform(22, 60)
        secondary_y_amp = random.uniform(1.5, 4.5)
        y_phase_tilt = random.uniform(0.05, 0.18)
        shift_y = np.cos(x / fold_y_freq) * fold_y_amp
        shift_y += np.cos((x - y * y_phase_tilt) / secondary_y_freq) * secondary_y_amp
        
        new_x = np.clip(x + shift_x, 0, w - 1).astype(int)
        new_y = np.clip(y + shift_y, 0, h - 1).astype(int)
        
        distorted_arr = arr[new_y, new_x]
        return Image.fromarray(distorted_arr)

    def apply_broadcast_noise(self, img):
        arr = np.array(img).astype(np.int16)
        noise_intensity = random.uniform(3, 15) # Softened slightly to prevent color washing
        noise = np.random.normal(0, noise_intensity, arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        
        if random.random() > 0.5:
            speckle_amount = random.uniform(0.01, 0.03)
            num_salt = np.ceil(speckle_amount * arr.size * 0.5)
            
            coords =[np.random.randint(0, i - 1, int(num_salt)) for i in arr.shape[:2]]
            arr[tuple(coords)] = 255

            coords =[np.random.randint(0, i - 1, int(num_salt)) for i in arr.shape[:2]]
            arr[tuple(coords)] = 0
            
        noisy_img = Image.fromarray(arr)
        noisy_img = noisy_img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.4, 1.2)))
        return noisy_img

    def generate_image(self, player_number=None, include_metadata=False):
        bg_color, text_color, outline_color = self.get_contrasting_colors()
        
        base_size = 256
        img = Image.new('RGB', (base_size, base_size), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw Fake Name & Number
        name_font = self.get_font(random.randint(24, 34))
        
        fake_name_length = random.randint(5, 9)
        player_name = "".join(random.choices(string.ascii_uppercase, k=fake_name_length))
        if player_number is None:
            player_number = str(random.randint(0, 99))
        else:
            player_number = str(int(player_number))

        # Center fake name
        bbox_name = draw.textbbox((0, 0), player_name, font=name_font)
        nx = (base_size - (bbox_name[2] - bbox_name[0])) // 2
        self.draw_text_with_outline(
            draw,
            nx,
            random.randint(26, 34),
            player_name,
            name_font,
            text_color,
            outline_color,
            thickness=random.randint(1, 3),
        )

        number_layer, bbox_num = self.render_number_layer(player_number, base_size, text_color, outline_color)
        num_left, num_top, num_right, num_bottom = bbox_num
        num_w = num_right - num_left
        num_h = num_bottom - num_top
        num_center_x = (num_left + num_right) / 2
        num_center_y = (num_top + num_bottom) / 2
        number_corners = [
            (num_left, num_top),
            (num_right, num_top),
            (num_right, num_bottom),
            (num_left, num_bottom),
        ]
        img = Image.alpha_composite(img.convert('RGBA'), number_layer).convert('RGB')

        # Shadows/Highlights (Fabric folds)
        overlay = Image.new('RGBA', (base_size, base_size), (0, 0, 0, 0))
        draw_over = ImageDraw.Draw(overlay)
        for _ in range(random.randint(2, 5)):
            fx = random.randint(0, base_size)
            start_y = random.randint(-24, 24)
            end_y = base_size + random.randint(-24, 24)
            shadow_width = random.randint(18, 42)
            shadow_offset = random.randint(-55, 55)
            draw_over.line(
                [(fx, start_y), (fx + shadow_offset, end_y)],
                fill=(0, 0, 0, random.randint(45, 100)),
                width=shadow_width,
            )
            fx2 = fx + random.randint(8, 24)
            highlight_offset = shadow_offset + random.randint(-12, 12)
            draw_over.line(
                [(fx2, start_y), (fx2 + highlight_offset, end_y)],
                fill=(255, 255, 255, random.randint(25, 75)),
                width=max(12, shadow_width - random.randint(2, 8)),
            )

        if random.random() > 0.35:
            for _ in range(random.randint(1, 2)):
                fy = random.randint(50, base_size - 40)
                crest_height = random.randint(18, 34)
                crest_left = random.randint(-30, 30)
                crest_right = base_size + random.randint(-30, 30)
                draw_over.line(
                    [(crest_left, fy), (base_size // 2, fy + crest_height), (crest_right, fy)],
                    fill=(0, 0, 0, random.randint(30, 70)),
                    width=random.randint(12, 24),
                    joint="curve",
                )
                draw_over.line(
                    [(crest_left, fy - 8), (base_size // 2, fy + crest_height - 8), (crest_right, fy - 8)],
                    fill=(255, 255, 255, random.randint(18, 55)),
                    width=random.randint(10, 20),
                    joint="curve",
                )
                            
        overlay = overlay.filter(ImageFilter.GaussianBlur(10))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        # Fabric Distortion
        img = self.apply_fabric_distortion(img)

        # ==========================================
        # WHITE ICE BACKGROUND (Simulates Turned Body)
        # ==========================================
        # This draws the pure white ice line BEFORE the rotation, guaranteeing 
        # it rotates and perspective-squishes exactly perfectly with the player numbers.
        draw = ImageDraw.Draw(img)
        if random.random() > 0.3: # 70% chance to show ice
            ice_color = (250, 252, 255) # Pure/bright white rink color
            ice_width = random.randint(25, 65)
            
            if random.random() > 0.5:
                # Vertical white ice strip on strictly the LEFT side
                draw.rectangle([(0, 0), (ice_width, base_size)], fill=ice_color)
            else:
                # Vertical white ice strip on strictly the RIGHT side
                draw.rectangle([(base_size - ice_width, 0), (base_size, base_size)], fill=ice_color)

        # MINIMAL, EDGE-ONLY OCCLUSIONS
        if random.random() > 0.5:  
            edge = random.choice(["left", "right", "bottom"])
            blob_w = random.randint(28, 70)
            blob_h = random.randint(48, 100)
            
            if edge == "left":
                bx = random.randint(-30, 0)
                by = random.randint(80, 200)
            elif edge == "right":
                bx = base_size - random.randint(0, 30)
                by = random.randint(80, 200)
            else:
                bx = random.randint(40, 200)
                by = base_size - random.randint(0, 30)

            occlusion = Image.new("RGBA", (base_size, base_size), (0, 0, 0, 0))
            occ_draw = ImageDraw.Draw(occlusion)
            occ_draw.ellipse(
                [bx, by, bx + blob_w, by + blob_h],
                fill=(255, 255, 255, random.randint(70, 150)),
            )

            if random.random() > 0.3:
                inner_inset = random.randint(6, 14)
                occ_draw.ellipse(
                    [
                        bx + inner_inset,
                        by + inner_inset,
                        bx + blob_w - inner_inset,
                        by + blob_h - inner_inset,
                    ],
                    fill=(245, 248, 255, random.randint(45, 110)),
                )

            occlusion = occlusion.filter(ImageFilter.GaussianBlur(radius=random.uniform(8, 16)))
            img = Image.alpha_composite(img.convert("RGBA"), occlusion).convert("RGB")

        # ==========================================
        # BELL CURVE ROTATION & PERSPECTIVE SQUISH
        # ==========================================
        angle = np.random.normal(loc=0, scale=24) 
        angle = float(np.clip(angle, -60, 60)) 

        # 3D Realism
        squish_intensity = random.uniform(0.3, 0.5)
        compress_ratio = max(0.5, 1.0 - (abs(angle) / 60.0) * squish_intensity)
        
        # Apply 2D Rotation and Perspective Width Scale
        img = img.rotate(angle, resample=Image.BICUBIC, fillcolor=bg_color)
        new_w = int(base_size * compress_ratio)
        img = img.resize((new_w, base_size), resample=Image.BICUBIC)

        # ==========================================
        # ROTATION-AWARE TIGHT ZOOM CROP 
        # ==========================================
        angle_rad = math.radians(abs(angle))
        actual_angle_rad = math.radians(angle)
        current_num_w = num_w * compress_ratio
        
        rotated_w = current_num_w * math.cos(angle_rad) + num_h * math.sin(angle_rad)
        rotated_h = current_num_w * math.sin(angle_rad) + num_h * math.cos(angle_rad)
        
        view_size_x = max(60, int(rotated_w / random.uniform(0.75, 0.90)))
        view_size_y = max(60, int(rotated_h / random.uniform(0.75, 0.90)))

        image_center = base_size / 2
        dx = num_center_x - image_center
        dy = num_center_y - image_center

        rotated_center_x = image_center + dx * math.cos(actual_angle_rad) - dy * math.sin(actual_angle_rad)
        rotated_center_y = image_center + dx * math.sin(actual_angle_rad) + dy * math.cos(actual_angle_rad)

        transformed_center_x = rotated_center_x * compress_ratio
        transformed_center_y = rotated_center_y
        transformed_corners = []
        for point_x, point_y in number_corners:
            dx = point_x - image_center
            dy = point_y - image_center
            rotated_x = image_center + dx * math.cos(actual_angle_rad) - dy * math.sin(actual_angle_rad)
            rotated_y = image_center + dx * math.sin(actual_angle_rad) + dy * math.cos(actual_angle_rad)
            transformed_corners.append((rotated_x * compress_ratio, rotated_y))

        half_w = view_size_x / 2
        half_h = view_size_y / 2
        pad_left = max(0, int(math.ceil(half_w - transformed_center_x)))
        pad_right = max(0, int(math.ceil(transformed_center_x + half_w - new_w)))
        pad_top = max(0, int(math.ceil(half_h - transformed_center_y)))
        pad_bottom = max(0, int(math.ceil(transformed_center_y + half_h - base_size)))

        if pad_left or pad_right or pad_top or pad_bottom:
            img = ImageOps.expand(img, border=(pad_left, pad_top, pad_right, pad_bottom), fill=bg_color)
            transformed_center_x += pad_left
            transformed_center_y += pad_top
            transformed_corners = [(x + pad_left, y + pad_top) for x, y in transformed_corners]

        left = int(round(transformed_center_x - half_w))
        top = int(round(transformed_center_y - half_h))
        right = left + view_size_x
        bottom = top + view_size_y
        img = img.crop((left, top, right, bottom))
        transformed_corners = [(x - left, y - top) for x, y in transformed_corners]

        # Bias output sizes toward smaller low-res crops while keeping the 30-150 range.
        min_dim = 30
        max_dim = 150
        scale_min = max(min_dim / view_size_x, min_dim / view_size_y)
        scale_max = min(max_dim / view_size_x, max_dim / view_size_y)

        if scale_min <= scale_max:
            scale_bias = random.betavariate(1.3, 3.0)
            scale = scale_min + (scale_max - scale_min) * scale_bias
        else:
            scale = min(max_dim / view_size_x, max_dim / view_size_y)

        target_w = max(min_dim, min(max_dim, int(round(view_size_x * scale))))
        target_h = max(min_dim, min(max_dim, int(round(view_size_y * scale))))
        img = img.resize((target_w, target_h), resample=Image.BICUBIC)
        scale_x = target_w / view_size_x
        scale_y = target_h / view_size_y
        transformed_corners = [(x * scale_x, y * scale_y) for x, y in transformed_corners]

        # Broadcast Noise
        img = self.apply_broadcast_noise(img)

        bbox_x1 = max(0.0, min(x for x, _ in transformed_corners))
        bbox_y1 = max(0.0, min(y for _, y in transformed_corners))
        bbox_x2 = min(float(target_w), max(x for x, _ in transformed_corners))
        bbox_y2 = min(float(target_h), max(y for _, y in transformed_corners))
        bbox_w = max(1.0, bbox_x2 - bbox_x1)
        bbox_h = max(1.0, bbox_y2 - bbox_y1)
        metadata = {
            "class_id": int(player_number),
            "class_name": player_number,
            "bbox": [bbox_x1, bbox_y1, bbox_w, bbox_h],
            "image_size": [target_w, target_h],
        }

        if include_metadata:
            return img, player_number, metadata
        return img, player_number


class YoloNumberPredictor:
    def __init__(self):
        self.model = None
        self.model_path = None
        self.model_mtime = None
        self.device = "cpu"
        self._torch = None
        self._YOLO = None

    def _ensure_dependencies(self):
        if self._torch is not None:
            return

        try:
            import torch
            from ultralytics import YOLO
        except Exception as exc:
            raise RuntimeError(
                "Ultralytics and PyTorch are required for YOLO prediction. "
                "Run this viewer from your training virtual environment."
            ) from exc

        self._torch = torch
        self._YOLO = YOLO

    def load_model(self, checkpoint_path):
        self._ensure_dependencies()
        self.device = 0 if self._torch.cuda.is_available() else "cpu"
        self.model = self._YOLO(checkpoint_path)
        self.model_path = checkpoint_path
        self.model_mtime = os.path.getmtime(checkpoint_path)
        class_names = getattr(self.model, "names", {}) or {}

        return {
            "checkpoint_path": checkpoint_path,
            "device": "cuda:0" if self.device == 0 else "cpu",
            "num_classes": len(class_names),
        }

    def is_loaded(self):
        return self.model is not None

    def find_latest_best_checkpoint(self, search_root):
        if not os.path.isdir(search_root):
            return None

        candidates = []
        for root, _, files in os.walk(search_root):
            for filename in files:
                if filename.lower() == "best.pt":
                    candidates.append(os.path.join(root, filename))

        if not candidates:
            return None
        return max(candidates, key=os.path.getmtime)

    def ensure_latest_model(self, search_root):
        checkpoint_path = self.find_latest_best_checkpoint(search_root)
        if checkpoint_path is None:
            raise RuntimeError(f"No best.pt checkpoint was found under {search_root}")

        checkpoint_mtime = os.path.getmtime(checkpoint_path)
        if (
            self.model is None
            or self.model_path != checkpoint_path
            or self.model_mtime != checkpoint_mtime
        ):
            return self.load_model(checkpoint_path)

        return {
            "checkpoint_path": checkpoint_path,
            "device": "cuda:0" if self.device == 0 else "cpu",
            "num_classes": len(getattr(self.model, "names", {}) or {}),
        }

    def predict_pil_image(self, image, top_k=5):
        if self.model is None:
            raise RuntimeError("No YOLO model is loaded.")

        image = ImageOps.exif_transpose(image).convert("RGB")
        results = self.model.predict(
            source=np.array(image),
            device=self.device,
            conf=0.05,
            verbose=False,
        )

        if not results:
            return []

        boxes = getattr(results[0], "boxes", None)
        if boxes is None or len(boxes) == 0:
            return []

        confidences = boxes.conf.detach().cpu().tolist()
        class_ids = [int(class_id) for class_id in boxes.cls.detach().cpu().tolist()]
        bboxes = boxes.xyxy.detach().cpu().tolist()
        names = getattr(self.model, "names", {}) or {}

        predictions = []
        ranked = sorted(
            zip(confidences, class_ids, bboxes),
            key=lambda item: item[0],
            reverse=True,
        )
        for confidence, class_id, bbox in ranked[:top_k]:
            predictions.append(
                {
                    "class_id": class_id,
                    "label": str(names.get(class_id, class_id)),
                    "confidence": float(confidence),
                    "bbox": [float(value) for value in bbox],
                }
            )
        return predictions


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Synthetic Hockey Dataset Engine v10")
        self.root.geometry("400x600")
        self.preview_width = 250
        self.preview_height = 200
        self.predictor = None
        self.predict_window = None
        self.predict_preview_width = 320
        self.predict_preview_height = 320
        self.predict_model_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
        
        self.engine = SyntheticJerseyEngine()
        
        self.title_lbl = ttk.Label(root, text="Synthetic Number Engine", font=("Arial", 16, "bold"))
        self.title_lbl.pack(pady=10)

        # Reserve the full preview area so the controls stay anchored at the bottom.
        self.canvas_frame = tk.Frame(
            root,
            width=self.preview_width,
            height=self.preview_height,
            bg="#111111",
            bd=2,
            relief="solid",
        )
        self.canvas_frame.pack(pady=10)
        self.canvas_frame.pack_propagate(False)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.preview_width,
            height=self.preview_height,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.controls_frame = ttk.Frame(root)
        self.controls_frame.pack(side="bottom", fill="x", pady=10)

        self.info_lbl = ttk.Label(self.controls_frame, text="Number: -- | Resolution: --")
        self.info_lbl.pack(pady=5)

        self.btn_gen = ttk.Button(self.controls_frame, text="Generate Single Image", command=self.generate_single)
        self.btn_gen.pack(pady=10)

        self.btn_batch = ttk.Button(self.controls_frame, text="Batch Generate Dataset", command=self.generate_batch)
        self.btn_batch.pack(pady=5)

        self.btn_predictor = ttk.Button(self.controls_frame, text="Open YOLO Predictor", command=self.open_predictor_window)
        self.btn_predictor.pack(pady=5)

        self.generate_single()

    def generate_single(self):
        img, number = self.engine.generate_image()
        
        self.info_lbl.config(text=f"Number: {number} | Resolution: {img.size[0]}x{img.size[1]}")
        
        # Fit the preview into a fixed-height box so the button row does not move.
        display_scale = min(self.preview_width / img.size[0], self.preview_height / img.size[1])
        display_width = max(1, int(round(img.size[0] * display_scale)))
        display_height = max(1, int(round(img.size[1] * display_scale)))
        display_img = img.resize((display_width, display_height), Image.NEAREST)
        
        self.tk_img = ImageTk.PhotoImage(display_img)
        
        self.canvas.delete("all")
        offset_x = (self.preview_width - display_width) // 2
        offset_y = (self.preview_height - display_height) // 2
        self.canvas.create_image(offset_x, offset_y, anchor="nw", image=self.tk_img)

    def open_predictor_window(self):
        if self.predict_window is not None and self.predict_window.winfo_exists():
            self.predict_window.deiconify()
            self.predict_window.lift()
            self.predict_window.focus_force()
            return

        self.predict_window = tk.Toplevel(self.root)
        self.predict_window.title("YOLO Number Predictor")
        self.predict_window.geometry("520x680")
        self.predict_window.resizable(False, False)
        self.predict_window.protocol("WM_DELETE_WINDOW", self.close_predictor_window)

        self.predict_model_var = tk.StringVar(value="Model: searching for latest best.pt...")
        self.predict_image_var = tk.StringVar(value="Image: --")
        self.predict_result_var = tk.StringVar(
            value="The predictor will auto-load the newest best.pt under runs/."
        )

        title_lbl = ttk.Label(self.predict_window, text="YOLO Jersey Predictor", font=("Arial", 15, "bold"))
        title_lbl.pack(pady=(14, 8))

        status_lbl = ttk.Label(
            self.predict_window,
            textvariable=self.predict_model_var,
            justify="left",
            wraplength=460,
        )
        status_lbl.pack(pady=(0, 4))

        image_lbl = ttk.Label(
            self.predict_window,
            textvariable=self.predict_image_var,
            justify="left",
            wraplength=460,
        )
        image_lbl.pack(pady=(0, 10))

        btn_row = ttk.Frame(self.predict_window)
        btn_row.pack(pady=(0, 10))

        self.btn_reload_yolo = ttk.Button(btn_row, text="Reload Latest best.pt", command=self.reload_latest_yolo_model)
        self.btn_reload_yolo.pack(side="left", padx=6)

        self.btn_upload_predict = ttk.Button(btn_row, text="Upload Jersey Image", command=self.predict_uploaded_image)
        self.btn_upload_predict.pack(side="left", padx=6)

        preview_frame = tk.Frame(
            self.predict_window,
            width=self.predict_preview_width,
            height=self.predict_preview_height,
            bg="#111111",
            bd=2,
            relief="solid",
        )
        preview_frame.pack(pady=10)
        preview_frame.pack_propagate(False)

        self.predict_canvas = tk.Canvas(
            preview_frame,
            width=self.predict_preview_width,
            height=self.predict_preview_height,
            bg="#111111",
            highlightthickness=0,
        )
        self.predict_canvas.pack()

        result_header = ttk.Label(self.predict_window, text="Prediction", font=("Arial", 12, "bold"))
        result_header.pack(pady=(10, 4))

        result_lbl = ttk.Label(
            self.predict_window,
            textvariable=self.predict_result_var,
            justify="left",
            wraplength=460,
        )
        result_lbl.pack(padx=20, pady=(0, 14))

        self.reload_latest_yolo_model(show_success=False)

    def close_predictor_window(self):
        if self.predict_window is not None and self.predict_window.winfo_exists():
            self.predict_window.destroy()
        self.predict_window = None

    def reload_latest_yolo_model(self, show_success=True):
        if self.predictor is None:
            self.predictor = YoloNumberPredictor()

        try:
            model_info = self.predictor.ensure_latest_model(self.predict_model_root)
        except Exception as exc:
            self.predict_model_var.set("Model: latest best.pt not available")
            self.predict_result_var.set(str(exc))
            if show_success:
                messagebox.showerror("YOLO Load Failed", str(exc))
            return

        checkpoint_path = model_info["checkpoint_path"]
        run_name = os.path.basename(os.path.dirname(os.path.dirname(checkpoint_path)))
        self.predict_model_var.set(
            "Model: "
            f"{os.path.basename(checkpoint_path)} | "
            f"{run_name} | "
            f"{model_info['num_classes']} classes | "
            f"{model_info['device']}"
        )
        self.predict_result_var.set("Latest best.pt loaded. Upload a jersey image to run prediction.")
        if show_success:
            messagebox.showinfo("YOLO Loaded", f"Loaded {checkpoint_path} successfully.")

    def predict_uploaded_image(self):
        image_path = filedialog.askopenfilename(
            title="Select Jersey Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("All files", "*.*"),
            ],
        )
        if not image_path:
            return

        try:
            self.reload_latest_yolo_model(show_success=False)
            if self.predictor is None or not self.predictor.is_loaded():
                raise RuntimeError("No YOLO best.pt model is available yet.")

            with Image.open(image_path) as source_image:
                display_image = ImageOps.exif_transpose(source_image).convert("RGB")
                predictions = self.predictor.predict_pil_image(display_image, top_k=5)
        except Exception as exc:
            messagebox.showerror("Prediction Failed", str(exc))
            return

        preview_image = display_image.copy()
        if predictions:
            draw_preview = ImageDraw.Draw(preview_image)
            for rank, prediction in enumerate(predictions[:3]):
                x1, y1, x2, y2 = prediction["bbox"]
                color = "#00ff99" if rank == 0 else "#ffd166"
                draw_preview.rectangle((x1, y1, x2, y2), outline=color, width=3 if rank == 0 else 2)
                draw_preview.text(
                    (x1 + 4, max(0, y1 - 16)),
                    f"{prediction['label']} {prediction['confidence'] * 100:.1f}%",
                    fill=color,
                )

        preview_scale = min(
            self.predict_preview_width / preview_image.size[0],
            self.predict_preview_height / preview_image.size[1],
        )
        preview_width = max(1, int(round(preview_image.size[0] * preview_scale)))
        preview_height = max(1, int(round(preview_image.size[1] * preview_scale)))
        display_preview = preview_image.resize((preview_width, preview_height), Image.NEAREST)
        self.predict_tk_img = ImageTk.PhotoImage(display_preview)

        self.predict_canvas.delete("all")
        offset_x = (self.predict_preview_width - preview_width) // 2
        offset_y = (self.predict_preview_height - preview_height) // 2
        self.predict_canvas.create_image(offset_x, offset_y, anchor="nw", image=self.predict_tk_img)

        self.predict_image_var.set(f"Image: {image_path}")
        self.predict_result_var.set(self.format_prediction_text(predictions))

    def format_prediction_text(self, predictions):
        if not predictions:
            return "No detections found in the uploaded image."

        top_prediction = predictions[0]
        lines = [
            f"Predicted class: {top_prediction['label']}",
            f"Confidence: {top_prediction['confidence'] * 100:.1f}%",
            "",
            "Top detections:",
        ]
        for rank, prediction in enumerate(predictions, start=1):
            lines.append(
                f"{rank}. {prediction['label']} ({prediction['confidence'] * 100:.1f}%)"
            )
        return "\n".join(lines)

    def _write_yolo_config(self, folder):
        dataset_root = os.path.abspath(folder).replace("\\", "/")
        yaml_lines = [
            f'path: "{dataset_root}"',
            "train: images/train",
            "val: images/val",
            "names:",
        ]
        yaml_lines.extend(f'  {class_id}: "{class_id}"' for class_id in range(100))
        with open(os.path.join(folder, "dataset.yaml"), "w", encoding="utf-8") as handle:
            handle.write("\n".join(yaml_lines) + "\n")

        with open(os.path.join(folder, "classes.txt"), "w", encoding="utf-8") as handle:
            handle.write("\n".join(str(class_id) for class_id in range(100)) + "\n")

    def _write_coco_annotations(self, folder, split, images, annotations):
        payload = {
            "info": {
                "description": "Synthetic hockey jersey numbers",
                "version": "1.0",
            },
            "licenses": [],
            "images": images,
            "annotations": annotations,
            "categories": [
                {"id": class_id + 1, "name": str(class_id), "supercategory": "jersey_number"}
                for class_id in range(100)
            ],
        }
        annotations_dir = os.path.join(folder, "annotations")
        os.makedirs(annotations_dir, exist_ok=True)
        output_path = os.path.join(annotations_dir, f"instances_{split}.json")
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def _build_balanced_number_plan(self, count):
        counts_by_class = {
            class_id: count // 100 + (1 if class_id < count % 100 else 0)
            for class_id in range(100)
        }
        number_plan = []
        for class_id, class_count in counts_by_class.items():
            number_plan.extend([class_id] * class_count)
        random.shuffle(number_plan)
        return number_plan, counts_by_class

    def generate_batch(self):
        folder = filedialog.askdirectory(title="Select Folder to Save Dataset")
        if not folder:
            return

        count = simpledialog.askinteger(
            "Dataset Size",
            "How many images should be generated?",
            initialvalue=1000,
            minvalue=1,
            parent=self.root,
        )
        if count is None:
            return

        for split in ("train", "val"):
            os.makedirs(os.path.join(folder, "images", split), exist_ok=True)
            os.makedirs(os.path.join(folder, "labels", split), exist_ok=True)

        number_plan, counts_by_class = self._build_balanced_number_plan(count)
        val_targets = {}
        for class_id, class_count in counts_by_class.items():
            if class_count <= 1:
                val_targets[class_id] = 0
                continue
            proposed_val = max(1, int(round(class_count * 0.2)))
            val_targets[class_id] = min(class_count - 1, proposed_val)

        seen_by_class = {class_id: 0 for class_id in range(100)}
        coco_images = {"train": [], "val": []}
        coco_annotations = {"train": [], "val": []}
        annotation_id = 1

        for image_index, class_id in enumerate(number_plan, start=1):
            img, number, metadata = self.engine.generate_image(player_number=class_id, include_metadata=True)
            split = "val" if seen_by_class[class_id] < val_targets[class_id] else "train"
            seen_by_class[class_id] += 1

            filename = f"jersey_{int(number):02d}_{image_index:05d}_{img.size[0]}x{img.size[1]}.png"
            image_rel_path = os.path.join("images", split, filename)
            image_path = os.path.join(folder, image_rel_path)
            img.save(image_path)

            bbox_x, bbox_y, bbox_w, bbox_h = metadata["bbox"]
            image_width, image_height = img.size
            yolo_x_center = (bbox_x + bbox_w / 2) / image_width
            yolo_y_center = (bbox_y + bbox_h / 2) / image_height
            yolo_width = bbox_w / image_width
            yolo_height = bbox_h / image_height
            label_path = os.path.join(folder, "labels", split, f"{os.path.splitext(filename)[0]}.txt")
            with open(label_path, "w", encoding="utf-8") as handle:
                handle.write(
                    f"{class_id} {yolo_x_center:.6f} {yolo_y_center:.6f} {yolo_width:.6f} {yolo_height:.6f}\n"
                )

            coco_images[split].append(
                {
                    "id": image_index,
                    "width": image_width,
                    "height": image_height,
                    "file_name": image_rel_path.replace("\\", "/"),
                }
            )
            coco_annotations[split].append(
                {
                    "id": annotation_id,
                    "image_id": image_index,
                    "category_id": class_id + 1,
                    "bbox": [round(bbox_x, 2), round(bbox_y, 2), round(bbox_w, 2), round(bbox_h, 2)],
                    "area": round(bbox_w * bbox_h, 2),
                    "iscrowd": 0,
                    "segmentation": [],
                }
            )
            annotation_id += 1

        self._write_yolo_config(folder)
        self._write_coco_annotations(folder, "train", coco_images["train"], coco_annotations["train"])
        self._write_coco_annotations(folder, "val", coco_images["val"], coco_annotations["val"])

        messagebox.showinfo(
            "Success",
            (
                f"Generated {count} images in {folder}\n"
                "YOLO files: images/, labels/, dataset.yaml\n"
                "COCO files: annotations/instances_train.json and instances_val.json"
            ),
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()
