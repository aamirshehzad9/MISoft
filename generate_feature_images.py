import requests
import os
import time
from pathlib import Path

# Load HuggingFace API key from .env.local
env_path = Path(r"D:\Projects\MISoft\Docs\.env.local")
hf_api_key = None

with open(env_path, 'r') as f:
    for line in f:
        if 'HuggingFace_API_Key=' in line or 'VITE_HF_API_KEY=' in line:
            hf_api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
            if hf_api_key:
                break

if not hf_api_key:
    print("ERROR: HuggingFace API key not found")
    exit(1)

print("✓ API key loaded securely")

# Use Stable Diffusion 2.1 (reliable model)
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
headers = {"Authorization": f"Bearer {hf_api_key}"}

# Simplified prompts for better generation
prompts = {
    "ifrs_compliance": "professional 3D holographic IFRS compliance dashboard, financial reporting standards, purple and cyan glow, dark background, glass effect, modern enterprise software, high quality",
    
    "multi_currency": "professional 3D holographic globe with currency symbols USD EUR GBP JPY, exchange rates, purple and cyan colors, dark background, glass effect, financial technology, high quality",
    
    "manufacturing_erp": "professional 3D holographic factory with production lines, inventory tracking, purple and cyan data streams, dark background, glass effect, enterprise software, high quality",
    
    "ai_engine": "professional 3D holographic AI brain analyzing financial data, neural network, purple and cyan glow, dark background, glass effect, enterprise AI software, high quality"
}

# Output directory
output_dir = Path(r"d:\Projects\MISoft\frontend\src\assets\features")
output_dir.mkdir(parents=True, exist_ok=True)

# Generate each image
success_count = 0
for name, prompt in prompts.items():
    print(f"\nGenerating {name}...")
    
    try:
        response = requests.post(
            API_URL, 
            headers=headers, 
            json={"inputs": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            output_path = output_dir / f"{name}.png"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Saved: {name}.png ({len(response.content)} bytes)")
            success_count += 1
        elif response.status_code == 503:
            print(f"⏳ Model loading, waiting 20 seconds...")
            time.sleep(20)
            # Retry once
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            if response.status_code == 200:
                output_path = output_dir / f"{name}.png"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Saved: {name}.png ({len(response.content)} bytes)")
                success_count += 1
            else:
                print(f"✗ Error {response.status_code}: {response.text[:200]}")
        else:
            print(f"✗ Error {response.status_code}: {response.text[:200]}")
    
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    # Small delay between requests
    time.sleep(2)

print(f"\n{'='*50}")
print(f"Generation complete! {success_count}/4 images created")
print(f"{'='*50}")
