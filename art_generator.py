

import os
import random
import wandb
import numpy as np
from PIL import Image
import glob
import http.server
import socketserver
import threading
import time
import shutil

# Conditional W&B Initialization
use_wandb = os.environ.get("WANDB_API_KEY") is not None
if use_wandb:
    run = wandb.init(project="VibeCoding", job_type="julia-fractal-generation-psychedelic-only")
    # Updated table with scoring columns
    table = wandb.Table(columns=["image", "palette_name", "seed", "complexity_score", "originality_score"])

# --- Art Generation Parameters ---
width, height = 512, 512
max_iter = 150 # Max iterations for fractal calculation
IMAGE_DIR = "generated_images"

def generate_julia(c, z, max_iter):
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

# --- Color Palettes ---
def palette_viridis_like(m, max_iter):
    # Simple approximation of Viridis-like, focusing on smooth progression
    colors = [
        np.array([68, 1, 84]),   # Dark Purple-Blue
        np.array([59, 82, 139]), # Blue
        np.array([33, 145, 140]),# Teal
        np.array([129, 199, 124]),# Light Green
        np.array([253, 231, 37]) # Bright Yellow
    ]
    
    idx = int(m / max_iter * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (m / max_iter * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_grayscale(m, max_iter):
    val = int(m / max_iter * 255)
    return (val, val, val)

def palette_single_blue_hue(m, max_iter):
    # Gradient from very dark blue to light blue
    intensity = m / max_iter
    r = int(intensity * 50)
    g = int(intensity * 100)
    b = int(intensity * 200)
    return (r, g, b)

# 2. Aesthetic Beauty and Artistic Expression
def palette_analogous_blue_purple(m, max_iter):
    # Blue to purple gradient
    colors = [
        np.array([0, 0, 100]),   # Dark Blue
        np.array([50, 0, 150]),  # Medium Purple
        np.array([100, 0, 200]), # Bright Purple
        np.array([150, 50, 250]) # Light Purple
    ]
    idx = int(m / max_iter * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (m / max_iter * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_fire(m, max_iter):
    # Red, Orange, Yellow
    colors = [
        np.array([0, 0, 0]),     # Black
        np.array([100, 0, 0]),   # Dark Red
        np.array([200, 50, 0]),  # Orange
        np.array([255, 150, 0]), # Bright Orange
        np.array([255, 255, 0])  # Yellow
    ]
    idx = int(m / max_iter * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (m / max_iter * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_ocean(m, max_iter):
    # Deep blue to cyan/white
    colors = [
        np.array([0, 0, 50]),    # Deep Navy
        np.array([0, 50, 150]),  # Medium Blue
        np.array([0, 150, 200]), # Cyan
        np.array([150, 255, 255])# Light Cyan
    ]
    idx = int(m / max_iter * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (m / max_iter * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_metallic(m, max_iter):
    # Grays, silvers, and golds
    colors = [
        np.array([0, 0, 0]),     # Black
        np.array([50, 50, 50]),  # Dark Gray
        np.array([150, 150, 150]),# Silver
        np.array([200, 180, 100]),# Gold
        np.array([255, 230, 150]) # Bright Gold
    ]
    idx = int(m / max_iter * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (m / max_iter * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_nebula(m, max_iter):
    # Dark purples, blues, magentas, with bright highlights
    colors = [
        np.array([0, 0, 0]),     # Black
        np.array([20, 0, 40]),   # Dark Purple
        np.array([40, 0, 80]),   # Medium Purple
        np.array([80, 0, 160]),  # Bright Purple
        np.array([120, 0, 200]), # Magenta-Blue
        np.array([200, 100, 255]),# Light Magenta
        np.array([255, 255, 255]) # White (for stars)
    ]
    idx = int(m / max_iter * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (m / max_iter * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

# 3. Classic Psychedelic Look
def palette_psychedelic(m, max_iter):
    # Small, repeating, high-contrast palette
    psy_colors = [
        (255, 0, 0),   # Red
        (255, 127, 0), # Orange
        (255, 255, 0), # Yellow
        (0, 255, 0),   # Green
        (0, 0, 255),   # Blue
        (75, 0, 130),  # Indigo
        (148, 0, 211)  # Violet
    ]
    return psy_colors[m % len(psy_colors)]

palettes = {
    "psychedelic": palette_psychedelic,
}

def generate_fractal(seed, palette_func):
    """Generates a Julia set fractal and returns the image and its iteration data for scoring."""
    random.seed(seed)
    
    # --- Fractal Parameters ---
    c_real = random.uniform(-1, 1)
    c_imag = random.uniform(-1, 1)
    c = complex(c_real, c_imag)
    
    # Change background to white
    img = Image.new('RGB', (width, height), color = 'white')
    pixels = img.load()
    iteration_data = np.zeros((width, height))

    for x in range(width):
        for y in range(height):
            real = (x - width / 2) * 4 / width
            imag = (y - height / 2) * 4 / height
            z = complex(real, imag)

            m = generate_julia(c, z, max_iter)
            
            # Set color to white if the point does not escape (background)
            if m == max_iter:
                color = (255, 255, 255) 
            else:
                color = palette_func(m, max_iter) # Pass max_iter to palette function
            
            pixels[x, y] = color
            iteration_data[x, y] = m
            
    return img, iteration_data

def calculate_complexity(iteration_data):
    """Calculates a complexity score based on the average iteration count."""
    return np.mean(iteration_data)

def clean_previous_images():
    """Deletes all previously generated fractal images and index.html."""
    print("Cleaning up previous images and index.html...")
    if os.path.exists(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)
    if os.path.exists("index.html"):
        os.remove("index.html")
    print("Previous images and index.html cleaned.")

PORT = 5555
Handler = http.server.SimpleHTTPRequestHandler

def start_server():
    """Starts a simple HTTP server in a new thread."""
    # Change current directory to IMAGE_DIR for serving
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.chdir(IMAGE_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving images at http://localhost:{PORT}")
        httpd.serve_forever()

def generate_html_index(image_filenames):
    """Generates an HTML index file with thumbnails of the images."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Julia Fractals</title>
    <style>
        body { font-family: sans-serif; background-color: #333; color: #eee; }
        .container { display: flex; flex-wrap: wrap; gap: 10px; padding: 20px; }
        .thumbnail { border: 1px solid #555; padding: 5px; background-color: #222; }
        .thumbnail img { width: 150px; height: 150px; object-fit: cover; }
    </style>
</head>
<body>
    <h1>Generated Julia Fractals</h1>
    <div class="container">
"""
    # Image filenames are now relative to IMAGE_DIR
    for filename in image_filenames:
        html_content += f"        <div class=\"thumbnail\"><img src=\"{os.path.basename(filename)}\" alt=\"{os.path.basename(filename)}\"></div>\n"
    
    html_content += """
    </div>
</body>
</html>
"""
    # Write index.html to the parent directory, as the server changes directory
    with open(os.path.join(os.path.dirname(os.getcwd()), "index.html"), "w") as f:
        f.write(html_content)
    print("Generated index.html with thumbnails.")

def main():
    # Start the web server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start up
    time.sleep(1)

    # Change back to original directory before cleanup and image generation
    original_cwd = os.getcwd()
    os.chdir(original_cwd)
    clean_previous_images()
    os.makedirs(IMAGE_DIR, exist_ok=True)

    num_images = 100 # Fixed batch size
    print(f"Generating a batch of {num_images} Julia fractals...")

    generated_image_filenames = []
    for i in range(num_images):
        seed = random.randint(0, 1000000)
        
        palette_name, palette_func = random.choice(list(palettes.items()))
        
        art, iteration_data = generate_fractal(seed, palette_func)
        
        # Score the generation
        complexity_score = calculate_complexity(iteration_data)
        originality_score = seed # Using the seed as a direct originality metric

        # Log to W&B Table
        img_filename = f"julia_art_{seed}_{palette_name}.png"
        img_path = os.path.join(IMAGE_DIR, img_filename)
        art.save(img_path)
        generated_image_filenames.append(img_path)
        
        if use_wandb:
            table.add_data(wandb.Image(img_path), palette_name, seed, complexity_score, originality_score)
        
        print(f"Generated and logged Julia art with seed: {seed}, Palette: {palette_name}, Complexity: {complexity_score:.2f}")

    # Generate HTML index in the original directory
    os.chdir(original_cwd)
    generate_html_index(generated_image_filenames)

    # Log the final table to W&B
    if use_wandb:
        run.log({"art_generations": table})
        run.finish()
    
    print("\nBatch generation complete. Check your W&B dashboard to see the scored fractals! (if API key was set)")
    print(f"You can also view the generated images locally at http://localhost:{PORT}")
    print("To rank by 'beauty', you can add a custom column in the W&B UI and manually assign scores.")

if __name__ == "__main__":
    main()
