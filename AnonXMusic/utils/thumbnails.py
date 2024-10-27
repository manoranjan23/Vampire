import os
import re
import textwrap
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

# Paths to template and images of girls
TEMPLATE_PATH = "/mnt/data/file-A4qEDjTAjflCH5OetMOGpV8R"
GIRLS_IMAGES_PATH = "AnonXMusic/assets/girls"

async def get_thumb(videoid, user_id):
    # Generate unique filename for the thumbnail
    thumbnail_file = f"cache/{videoid}_{user_id}.png"
    if os.path.isfile(thumbnail_file):
        return thumbnail_file

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        # Fetch video details
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]

        # Clean and retrieve details
        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown")

        # Open the provided template image
        template_img = Image.open(TEMPLATE_PATH).convert("RGBA")
        draw = ImageDraw.Draw(template_img)
        font = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 45)
        arial_font = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)

        # Draw title text on the thumbnail
        wrapped_title = textwrap.wrap(title, width=32)
        y_text = 500  # Adjust as needed for your template
        for line in wrapped_title:
            text_w, text_h = draw.textsize(line, font=font)
            draw.text(((template_img.width - text_w) / 2, y_text), line, fill="white", font=font)
            y_text += text_h + 5

        # Draw duration
        duration_text = f"Duration: {duration} Mins"
        text_w, _ = draw.textsize(duration_text, font=arial_font)
        draw.text(((template_img.width - text_w) / 2, y_text + 50), duration_text, fill="white", font=arial_font)

        # Draw central circle with video ID
        circle_center_x, circle_center_y = template_img.width // 2, 200  # Adjust position as needed
        outer_radius = 100
        inner_radius = 30

        # Outer circle
        draw.ellipse(
            (circle_center_x - outer_radius, circle_center_y - outer_radius,
             circle_center_x + outer_radius, circle_center_y + outer_radius),
            outline="white", width=5
        )

        # Video ID in the center of the circle
        videoid_font = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 20)
        videoid_text_w, videoid_text_h = draw.textsize(videoid, font=videoid_font)
        draw.text(
            (circle_center_x - videoid_text_w // 2, circle_center_y - videoid_text_h // 2),
            videoid, fill="white", font=videoid_font
        )

        # Inner circle for user ID
        draw.ellipse(
            (circle_center_x - inner_radius, circle_center_y - inner_radius,
             circle_center_x + inner_radius, circle_center_y + inner_radius),
            fill="white"
        )

        # User ID in the smaller circle
        userid_font = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 15)
        userid_text_w, userid_text_h = draw.textsize(str(user_id), font=userid_font)
        draw.text(
            (circle_center_x - userid_text_w // 2, circle_center_y - userid_text_h // 2),
            str(user_id), fill="black", font=userid_font
        )

        # Randomly select two images of girls
        girl_images = [img for img in os.listdir(GIRLS_IMAGES_PATH) if img.endswith(('.png', '.jpg', '.jpeg'))]
        if len(girl_images) >= 2:
            left_girl_img = Image.open(os.path.join(GIRLS_IMAGES_PATH, random.choice(girl_images))).resize((150, 150))
            right_girl_img = Image.open(os.path.join(GIRLS_IMAGES_PATH, random.choice(girl_images))).resize((150, 150))

            # Paste left girl image
            template_img.paste(left_girl_img, (circle_center_x - 300, circle_center_y - 75), left_girl_img)

            # Paste right girl image
            template_img.paste(right_girl_img, (circle_center_x + 150, circle_center_y - 75), right_girl_img)

        # Save the final thumbnail
        template_img.save(thumbnail_file)
        return thumbnail_file

    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return YOUTUBE_IMG_URL



