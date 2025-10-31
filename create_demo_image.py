#!/usr/bin/env python3
"""
Create a demo image for testing Rhinovate AI
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_demo_image():
    """Create a simple demo face image for testing"""
    
    # Create a 400x400 image with a light background
    img = Image.new('RGB', (400, 400), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face
    # Face outline
    face_bbox = [50, 50, 350, 350]
    draw.ellipse(face_bbox, fill='#fdbcb4', outline='#000000', width=2)
    
    # Eyes
    left_eye_bbox = [120, 150, 160, 190]
    right_eye_bbox = [240, 150, 280, 190]
    draw.ellipse(left_eye_bbox, fill='white', outline='#000000', width=2)
    draw.ellipse(right_eye_bbox, fill='white', outline='#000000', width=2)
    
    # Eye pupils
    draw.ellipse([135, 165, 145, 175], fill='#000000')
    draw.ellipse([255, 165, 265, 175], fill='#000000')
    
    # Nose
    nose_points = [(200, 200), (190, 250), (210, 250)]
    draw.polygon(nose_points, fill='#fdbcb4', outline='#000000', width=2)
    
    # Mouth
    mouth_bbox = [170, 280, 230, 300]
    draw.ellipse(mouth_bbox, fill='#ff6b6b', outline='#000000', width=2)
    
    # Add some text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add title
    title_text = "Demo Face for Testing"
    if font:
        bbox = draw.textbbox((0, 0), title_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (400 - text_width) // 2
        draw.text((text_x, 20), title_text, fill='#333333', font=font)
    
    # Save the image
    demo_path = 'demo_face.jpg'
    img.save(demo_path, 'JPEG', quality=95)
    
    print(f"✅ Demo image created: {demo_path}")
    print(f"   Size: {img.size}")
    print(f"   Location: {os.path.abspath(demo_path)}")
    
    return demo_path

if __name__ == "__main__":
    create_demo_image()
