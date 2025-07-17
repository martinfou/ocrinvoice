#!/usr/bin/env python3
"""
Create a simple placeholder icon for the NSIS installer.
This generates a basic 32x32 icon file to prevent NSIS build failures.
"""

from PIL import Image, ImageDraw
import os

def create_placeholder_icon():
    """Create a simple placeholder icon file."""
    
    # Create a 32x32 image with a simple design
    size = (32, 32)
    image = Image.new('RGBA', size, (0, 120, 215, 255))  # Windows blue background
    
    # Create a simple document icon design
    draw = ImageDraw.Draw(image)
    
    # Draw a white document shape
    draw.rectangle([4, 4, 28, 28], fill=(255, 255, 255, 255), outline=(200, 200, 200, 255))
    
    # Draw some lines to represent text
    for i in range(3):
        y = 8 + i * 6
        draw.line([(8, y), (24, y)], fill=(100, 100, 100, 255), width=1)
    
    # Draw a fold corner
    draw.polygon([(20, 4), (28, 4), (28, 12), (20, 4)], fill=(220, 220, 220, 255))
    
    # Save as ICO file
    icon_path = os.path.join(os.path.dirname(__file__), 'setup.ico')
    image.save(icon_path, format='ICO', sizes=[(32, 32)])
    
    print(f"Created placeholder icon: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_placeholder_icon() 