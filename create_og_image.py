#!/usr/bin/env python3
"""Generate Open Graph social sharing image for JustAButton"""

from PIL import Image, ImageDraw, ImageFont
import os

# Image dimensions (recommended for OG and Twitter)
WIDTH = 1200
HEIGHT = 630

# Create image with gradient background
img = Image.new('RGB', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(img)

# Create purple gradient (matching website: #667eea to #764ba2)
for y in range(HEIGHT):
    # Interpolate between the two colors
    ratio = y / HEIGHT
    r = int(102 + (118 - 102) * ratio)
    g = int(126 + (75 - 126) * ratio)
    b = int(234 + (162 - 234) * ratio)
    draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

# Draw large circular button in center
button_size = 300
button_x = (WIDTH - button_size) // 2
button_y = (HEIGHT - button_size) // 2 - 40

# Button shadow
shadow_offset = 15
draw.ellipse(
    [button_x + shadow_offset, button_y + shadow_offset,
     button_x + button_size + shadow_offset, button_y + button_size + shadow_offset],
    fill=(0, 0, 0, 100)
)

# Main button (gradient from #ff6b6b to #ee5a6f)
for i in range(button_size // 2):
    ratio = i / (button_size // 2)
    r = int(255 + (238 - 255) * ratio)
    g = int(107 + (90 - 107) * ratio)
    b = int(107 + (111 - 107) * ratio)
    draw.ellipse(
        [button_x + i, button_y + i,
         button_x + button_size - i, button_y + button_size - i],
        fill=(r, g, b)
    )

# Try to use system fonts, fall back to default
try:
    # Try common system fonts
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    button_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
except:
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 80)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 36)
        button_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 48)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        button_font = ImageFont.load_default()

# Draw "JustAButton" title at top
title_text = "JustAButton"
title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
title_width = title_bbox[2] - title_bbox[0]
title_x = (WIDTH - title_width) // 2
title_y = 60
# Text shadow
draw.text((title_x + 3, title_y + 3), title_text, font=title_font, fill=(0, 0, 0, 150))
draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))

# Draw "Click Me!" on button
button_text = "Click Me!"
button_text_bbox = draw.textbbox((0, 0), button_text, font=button_font)
button_text_width = button_text_bbox[2] - button_text_bbox[0]
button_text_height = button_text_bbox[3] - button_text_bbox[1]
button_text_x = (WIDTH - button_text_width) // 2
button_text_y = button_y + (button_size - button_text_height) // 2 - 10
draw.text((button_text_x, button_text_y), button_text, font=button_font, fill=(255, 255, 255))

# Draw tagline at bottom
tagline = "One Button. One Chance. Forever."
tagline_bbox = draw.textbbox((0, 0), tagline, font=subtitle_font)
tagline_width = tagline_bbox[2] - tagline_bbox[0]
tagline_x = (WIDTH - tagline_width) // 2
tagline_y = HEIGHT - 80
# Text shadow
draw.text((tagline_x + 2, tagline_y + 2), tagline, font=subtitle_font, fill=(0, 0, 0, 150))
draw.text((tagline_x, tagline_y), tagline, font=subtitle_font, fill=(255, 255, 255, 230))

# Save the image
output_path = 'button/static/button/og-image.png'
img.save(output_path, 'PNG', optimize=True)
print(f"✓ Created social sharing image: {output_path}")
print(f"  Dimensions: {WIDTH}x{HEIGHT}px")
print(f"  Size: {os.path.getsize(output_path) / 1024:.1f}KB")
