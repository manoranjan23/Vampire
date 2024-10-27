import os
import re
import textwrap
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

# Path to the template thumbnail image you provided
TEMPLATE_PATH = "/mnt/data/file-A4qEDjTAjflCH5OetMOGpV8R"

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

        # Add text to the template image
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

        # Save the final thumbnail
        template_img.save(thumbnail_file)
        return thumbnail_file

    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return YOUTUBE_IMG_URL

