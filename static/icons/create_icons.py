"""
Script to create simple placeholder icons for PWA
Run this to generate icon files
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with text"""
    # Create image with purple background
    img = Image.new('RGB', (size, size), color='#4F46E5')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple money bag emoji or text
    try:
        # Try to use a font
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw text "💰" or "$"
    text = "💰"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='white', font=font)
    
    # Save
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

if __name__ == "__main__":
    # Create icons directory if it doesn't exist
    os.makedirs("static/icons", exist_ok=True)
    
    # Create icons
    create_icon(192, "static/icons/icon-192.png")
    create_icon(512, "static/icons/icon-512.png")
    
    print("Icons created successfully!")

