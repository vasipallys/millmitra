#!/usr/bin/env python3

"""
Generate base64-encoded PNG icons for PWA
Creates simple colored icons that can be used immediately
"""

import base64
from io import BytesIO

def create_simple_png_icon(size, color='#1976d2'):
    """Create a simple PNG icon using base64 encoding"""
    
    # Simple SVG icon
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1976d2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#42a5f5;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="{size}" height="{size}" fill="url(#grad1)" rx="20"/>
  
  <!-- Rice grain icon -->
  <g transform="translate({size//2},{size//2})">
    <!-- Main grain -->
    <ellipse cx="0" cy="0" rx="{size//8}" ry="{size//4}" fill="white" opacity="0.9"/>
    
    <!-- Side grains -->
    <ellipse cx="-{size//6}" cy="-{size//8}" rx="{size//12}" ry="{size//6}" fill="white" opacity="0.7" transform="rotate(-20)"/>
    <ellipse cx="{size//6}" cy="-{size//8}" rx="{size//12}" ry="{size//6}" fill="white" opacity="0.7" transform="rotate(20)"/>
    
    <!-- Text for larger icons -->
    {f'<text x="0" y="{size//4}" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="{size//12}" font-weight="bold">MILL</text>' if size >= 192 else ''}
  </g>
  
  <!-- Border -->
  <rect width="{size-4}" height="{size-4}" x="2" y="2" fill="none" stroke="#1565c0" stroke-width="2" rx="18"/>
</svg>'''
    
    return svg_content

def svg_to_base64_data_url(svg_content):
    """Convert SVG to base64 data URL"""
    svg_bytes = svg_content.encode('utf-8')
    base64_string = base64.b64encode(svg_bytes).decode('utf-8')
    return f"data:image/svg+xml;base64,{base64_string}"

def create_png_placeholder(size):
    """Create a simple PNG placeholder using a minimal approach"""
    
    # Create a simple PNG header and data for a solid color square
    # This is a minimal PNG implementation for demonstration
    
    # For now, let's create SVG-based icons which are more reliable
    svg_content = create_simple_png_icon(size)
    return svg_content

def generate_icon_files():
    """Generate icon files for PWA"""
    
    print("🎨 Generating PWA Icons...")
    print("=" * 40)
    
    # Generate different sizes
    sizes = [64, 192, 512]
    
    for size in sizes:
        print(f"📱 Creating {size}x{size} icon...")
        
        svg_content = create_simple_png_icon(size)
        
        # Save as SVG file (which can be used as icon)
        filename = f"logo{size}.svg"
        if size == 64:
            filename = "favicon.svg"
            
        with open(f"frontend/public/{filename}", 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"✅ Created: frontend/public/{filename}")
    
    # Create a simple HTML file to convert SVG to PNG
    html_converter = '''<!DOCTYPE html>
<html>
<head>
    <title>SVG to PNG Converter</title>
</head>
<body>
    <h2>SVG to PNG Converter</h2>
    <canvas id="canvas192" width="192" height="192" style="border:1px solid #ccc; margin:10px;"></canvas>
    <canvas id="canvas512" width="512" height="512" style="border:1px solid #ccc; margin:10px;"></canvas>
    <br>
    <button onclick="convertToPNG(192)">Download 192x192 PNG</button>
    <button onclick="convertToPNG(512)">Download 512x512 PNG</button>
    
    <script>
        function convertToPNG(size) {
            const canvas = document.getElementById('canvas' + size);
            const ctx = canvas.getContext('2d');
            
            // Create gradient background
            const gradient = ctx.createLinearGradient(0, 0, size, size);
            gradient.addColorStop(0, '#1976d2');
            gradient.addColorStop(1, '#42a5f5');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, size, size);
            
            // Draw rice icon
            ctx.fillStyle = 'white';
            const centerX = size / 2;
            const centerY = size / 2;
            const scale = size / 192;
            
            // Main grain
            ctx.beginPath();
            ctx.ellipse(centerX, centerY, 24 * scale, 48 * scale, 0, 0, 2 * Math.PI);
            ctx.fill();
            
            // Side grains
            ctx.globalAlpha = 0.7;
            ctx.beginPath();
            ctx.ellipse(centerX - 32 * scale, centerY - 16 * scale, 16 * scale, 32 * scale, -0.3, 0, 2 * Math.PI);
            ctx.fill();
            
            ctx.beginPath();
            ctx.ellipse(centerX + 32 * scale, centerY - 16 * scale, 16 * scale, 32 * scale, 0.3, 0, 2 * Math.PI);
            ctx.fill();
            
            ctx.globalAlpha = 1;
            
            // Add text for larger icons
            if (size >= 192) {
                ctx.font = `bold ${16 * scale}px Arial`;
                ctx.textAlign = 'center';
                ctx.fillText('MILL', centerX, centerY + 70 * scale);
            }
            
            // Download
            const link = document.createElement('a');
            link.download = 'logo' + size + '.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }
        
        // Auto-generate on load
        window.onload = function() {
            convertToPNG(192);
            convertToPNG(512);
        };
    </script>
</body>
</html>'''
    
    with open("png_icon_generator.html", 'w', encoding='utf-8') as f:
        f.write(html_converter)
    
    print(f"✅ Created: png_icon_generator.html")
    print("\n🔗 Next Steps:")
    print("1. Open png_icon_generator.html in your browser")
    print("2. It will auto-download PNG versions of the icons")
    print("3. Copy the PNG files to frontend/public/")
    print("4. Restart the frontend server")

if __name__ == "__main__":
    generate_icon_files()
