from PIL import Image
import os

# Paths
source_logo = r"D:\Projects\MISoft\Docs\MISoft Logo.png"
output_logo = r"D:\Projects\MISoft\frontend\src\assets\logo-new.png"

# Load the image
print(f"Loading logo from: {source_logo}")
img = Image.open(source_logo)

# Convert to RGBA if not already
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Get image data
width, height = img.size
pixels = img.load()

print(f"Image size: {width}x{height}")
print(f"Image mode: {img.mode}")

# Define the circular logo area (assuming logo is centered)
center_x, center_y = width // 2, height // 2
radius = min(width, height) // 2

# Process pixels - make corners white
for y in range(height):
    for x in range(width):
        # Calculate distance from center
        distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        
        # If pixel is outside the circle, make it white
        if distance > radius:
            pixels[x, y] = (255, 255, 255, 255)  # White with full opacity

# Save the processed logo
print(f"Saving processed logo to: {output_logo}")
img.save(output_logo, 'PNG')
print("Logo processing complete!")

# Also display some info about the result
print(f"\nProcessed logo saved successfully!")
print(f"Original: {source_logo}")
print(f"Output: {output_logo}")
