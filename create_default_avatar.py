#!/usr/bin/env python3
"""
Script tạo avatar mặc định cho Tarot AI Oracle Hub
Chạy script này trước khi deploy
"""

import os

def create_avatar_svg():
    """Tạo SVG avatar đơn giản"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <radialGradient id="gradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#00ffff;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#9d00ff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ff00ff;stop-opacity:1" />
        </radialGradient>
    </defs>
    
    <!-- Background circle -->
    <circle cx="100" cy="100" r="90" fill="url(#gradient)" opacity="0.9"/>
    
    <!-- Inner circle -->
    <circle cx="100" cy="100" r="70" fill="#0a0a0f" opacity="0.3"/>
    
    <!-- Oracle symbol -->
    <text x="100" y="120" font-family="Arial, sans-serif" font-size="80" 
          text-anchor="middle" fill="white" opacity="0.9">🔮</text>
</svg>'''
    
    # Tạo thư mục nếu chưa có
    os.makedirs('static/avatar', exist_ok=True)
    
    # Lưu file SVG
    with open('static/avatar/default.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print("✓ Đã tạo default.svg")
    
    # Nếu có PIL, tạo PNG
    try:
        from PIL import Image, ImageDraw, ImageFont
        import cairosvg
        
        # Convert SVG to PNG
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to='static/avatar/default.png',
            output_width=200,
            output_height=200
        )
        print("✓ Đã tạo default.png")
        
    except ImportError:
        print("! PIL/cairosvg không có, chỉ tạo SVG")
        print("! Bạn có thể dùng default.svg hoặc cài: pip install Pillow cairosvg")
        
        # Fallback: Tạo PNG đơn giản bằng PIL nếu có
        try:
            from PIL import Image, ImageDraw
            
            # Tạo background gradient
            img = Image.new('RGB', (200, 200), color='#0a0a0f')
            draw = ImageDraw.Draw(img)
            
            # Vẽ circles với gradient effect
            for i in range(90, 0, -1):
                # Gradient từ cyan -> purple -> pink
                if i > 60:
                    r = int((i - 60) / 30 * 255)
                    g = int(255 - (i - 60) / 30 * 255)
                    b = 255
                elif i > 30:
                    r = int(157 + (60 - i) / 30 * (255 - 157))
                    g = 0
                    b = 255
                else:
                    r = 157
                    g = 0
                    b = int(255 - (30 - i) / 30 * 255)
                
                opacity = int(255 * (90 - i) / 90 * 0.9)
                draw.ellipse(
                    [(100 - i, 100 - i), (100 + i, 100 + i)],
                    fill=(r, g, b, opacity)
                )
            
            # Vẽ text
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
                except:
                    font = None
            
            text = "🔮"
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((200 - text_width) // 2, (200 - text_height) // 2)
                draw.text(position, text, font=font, fill='white')
            
            img.save('static/avatar/default.png')
            print("✓ Đã tạo default.png (fallback)")
            
        except ImportError:
            print("! Không thể tạo PNG, chỉ có SVG")

def main():
    print("🔮 Tarot AI Oracle - Tạo Avatar Mặc Định")
    print("=" * 50)
    
    create_avatar_svg()
    
    print("\n✅ Hoàn thành! Avatar mặc định đã được tạo.")
    print("\nFiles được tạo:")
    
    if os.path.exists('static/avatar/default.svg'):
        print("  ✓ static/avatar/default.svg")
    
    if os.path.exists('static/avatar/default.png'):
        print("  ✓ static/avatar/default.png")
    
    print("\n💡 Bạn có thể thay thế bằng avatar tùy chỉnh.")

if __name__ == '__main__':
    main()
