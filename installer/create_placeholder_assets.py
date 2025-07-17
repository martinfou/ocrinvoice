#!/usr/bin/env python3
"""
Create placeholder assets for the NSIS installer.
This generates basic icon and image files to prevent NSIS build failures.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_application_icon():
    """Create a simple application icon."""
    size = (32, 32)
    image = Image.new('RGBA', size, (0, 120, 215, 255))  # Windows blue background
    
    draw = ImageDraw.Draw(image)
    
    # Draw a simple document icon
    draw.rectangle([4, 4, 28, 28], fill=(255, 255, 255, 255), outline=(200, 200, 200, 255))
    
    # Draw some lines to represent text
    for i in range(3):
        y = 8 + i * 6
        draw.line([(8, y), (24, y)], fill=(100, 100, 100, 255), width=1)
    
    # Draw a fold corner
    draw.polygon([(20, 4), (28, 4), (28, 12), (20, 4)], fill=(220, 220, 220, 255))
    
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    image.save(icon_path, format='ICO', sizes=[(32, 32)])
    print(f"Created application icon: {icon_path}")

def create_welcome_image():
    """Create a simple welcome page image."""
    size = (164, 314)
    image = Image.new('RGB', size, (255, 255, 255))  # White background
    
    draw = ImageDraw.Draw(image)
    
    # Draw a border
    draw.rectangle([0, 0, 163, 313], outline=(200, 200, 200), width=2)
    
    # Draw a simple logo area
    draw.rectangle([20, 20, 144, 80], fill=(0, 120, 215), outline=(0, 100, 180), width=2)
    
    # Add some text
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw title
    draw.text((82, 35), "OCR", fill=(255, 255, 255), anchor="mm", font=font)
    draw.text((82, 55), "Invoice", fill=(255, 255, 255), anchor="mm", font=font)
    draw.text((82, 75), "Parser", fill=(255, 255, 255), anchor="mm", font=font)
    
    # Draw some descriptive text
    draw.text((82, 120), "Welcome to", fill=(0, 0, 0), anchor="mm", font=font)
    draw.text((82, 140), "OCR Invoice Parser", fill=(0, 0, 0), anchor="mm", font=font)
    draw.text((82, 160), "Professional PDF", fill=(0, 0, 0), anchor="mm", font=font)
    draw.text((82, 180), "Invoice Processing", fill=(0, 0, 0), anchor="mm", font=font)
    
    # Draw some features
    features = [
        "• Extract invoice data",
        "• Business name mapping", 
        "• PDF metadata storage",
        "• Batch processing",
        "• Professional GUI"
    ]
    
    y_start = 220
    for i, feature in enumerate(features):
        y = y_start + i * 20
        draw.text((20, y), feature, fill=(0, 0, 0), font=font)
    
    image_path = os.path.join(os.path.dirname(__file__), 'welcome.bmp')
    image.save(image_path, format='BMP')
    print(f"Created welcome image: {image_path}")

def main():
    """Create all placeholder assets."""
    print("Creating placeholder assets for NSIS installer...")
    
    create_application_icon()
    create_welcome_image()
    
    print("All placeholder assets created successfully!")

if __name__ == "__main__":
    main() 