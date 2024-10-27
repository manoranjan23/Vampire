import os
import re
import textwrap
import aiofiles
import aiohttp
import numpy as np
import random
from PIL import Image, ImageChops, ImageOps, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from AnonXMusic.assets import thumbs, colors
from config import YOUTUBE_IMG_URL

# Existing utility functions (no changes needed)
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

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

        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown")
        thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]

        # Download the main thumbnail image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumbnail_file, mode="wb") as f:
                        await f.write(await resp.read())

        # Fetch user profile or app profile picture for overlay
        try:
            wxyz = await app.get_profile_photos(user_id)
            wxy = await app.download_media(wxyz[0]['file_id'], file_name=f'{user_id}.jpg')
        except:
            abc = await app.get_profile_photos(app.id)
            wxy = await app.download_media(abc[0]['file_id'], file_name=f'{app.id}.jpg')

        # Open profile photo and add circular mask
        profile_img = Image.open(wxy)
        mask = Image.new('L', profile_img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, profile_img.size[0], profile_img.size[1]), fill=255)
        profile_img.putalpha(mask)

        # Choose background and border dynamically
        bg_image = random.choice(thumbs)
        border_color = random.choice(colors)

        # Process the thumbnail image
        youtube_img = Image.open(thumbnail_file)
        bg_img = Image.open(f"AnonXMusic/assets/{bg_image}.png")
        youtube_resized = youtube_img.resize((1280, 720)).convert("RGBA")
        bg_resized = bg_img.resize((1280, 720)).convert("RGBA")

        # Blend and overlay images
        blended_bg = Image.blend(youtube_resized, bg_resized, alpha=0.5)
        result_img = ImageOps.expand(blended_bg, border=10, fill=border_color)

        # Add text
        draw = ImageDraw.Draw(result_img)
        font = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 45)
        arial_font = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)
        draw.text((450, 35), "STARTED PLAYING", fill="white", font=font)

        # Wrap and position song title
        wrapped_title = textwrap.wrap(title, width=32)
        y_text = 560
        for line in wrapped_title:
            text_w, text_h = draw.textsize(line, font=font)
            draw.text(((1280 - text_w) / 2, y_text), line, fill="white", font=font)
            y_text += text_h + 5

        # Duration
        text_w, _ = draw.textsize(f"Duration: {duration} Mins", font=arial_font)
        draw.text(((1280 - text_w) / 2, 665), f"Duration: {duration} Mins", fill="white", font=arial_font)

        # Save final thumbnail
        result_img.save(thumbnail_file)
        return thumbnail_file

    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return YOUTUBE_IMG_URL