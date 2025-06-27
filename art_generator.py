

import os
import random
import wandb
import numpy as np
from PIL import Image

# Initialize W&B run
run = wandb.init(project="VibeCoding", job_type="julia-fractal-generation-vibrant")

# --- Art Generation Parameters ---
width, height = 512, 512
max_iter = 150 # Increased for more complexity potential

# Updated table with scoring columns
table = wandb.Table(columns=["image", "palette_name", "seed", "complexity_score", "originality_score"])

def generate_julia(c, z, max_iter):
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

# --- Vibrant Color Palettes ---
def palette_rainbow(m):
    # Cycles through hues based on iteration count
    hue = (m * 7) % 256
    r = int(np.sin(0.024 * hue + 0) * 127 + 128)
    g = int(np.sin(0.024 * hue + 2) * 127 + 128)
    b = int(np.sin(0.024 * hue + 4) * 127 + 128)
    return (r, g, b)

def palette_deep_ocean(m):
    # Blues and greens with some darker tones
    r = int(np.sin(0.05 * m) * 60 + 60)
    g = int(np.sin(0.05 * m + 2) * 80 + 100)
    b = int(np.sin(0.05 * m + 4) * 100 + 150)
    return (r, g, b)

def palette_sunset(m):
    # Oranges, reds, and purples
    r = int(np.sin(0.03 * m + 0) * 100 + 150)
    g = int(np.sin(0.03 * m + 2) * 50 + 70)
    b = int(np.sin(0.03 * m + 4) * 80 + 100)
    return (r, g, b)

# Keeping some of the previous ones if they were not considered dull
def palette_fire(m):
    return (m % 256, (m * 2) % 256, (m * 3) % 256)

palettes = {
    "rainbow": palette_rainbow,
    "deep_ocean": palette_deep_ocean,
    "sunset": palette_sunset,
    "fire": palette_fire,
}

def generate_fractal(seed, palette_func):
    """Generates a Julia set fractal and returns the image and its iteration data for scoring."""
    random.seed(seed)
    
    # --- Fractal Parameters ---
    c_real = random.uniform(-1, 1)
    c_imag = random.uniform(-1, 1)
    c = complex(c_real, c_imag)
    
    img = Image.new('RGB', (width, height), color = 'black')
    pixels = img.load()
    iteration_data = np.zeros((width, height))

    for x in range(width):
        for y in range(height):
            real = (x - width / 2) * 4 / width
            imag = (y - height / 2) * 4 / height
            z = complex(real, imag)

            m = generate_julia(c, z, max_iter)
            color = palette_func(m)
            
            pixels[x, y] = color
            iteration_data[x, y] = m
            
    return img, iteration_data

def calculate_complexity(iteration_data):
    """Calculates a complexity score based on the average iteration count."""
    return np.mean(iteration_data)

def main():
    num_images = random.randint(10, 20)
    print(f"Generating a batch of {num_images} Julia fractals with vibrant palettes...")

    for i in range(num_images):
        seed = random.randint(0, 1000000)
        
        palette_name, palette_func = random.choice(list(palettes.items()))
        
        art, iteration_data = generate_fractal(seed, palette_func)
        
        # Score the generation
        complexity_score = calculate_complexity(iteration_data)
        originality_score = seed # Using the seed as a direct originality metric

        # Log to W&B Table
        img_path = f"julia_art_{seed}_{palette_name}.png"
        art.save(img_path)
        
        table.add_data(wandb.Image(img_path), palette_name, seed, complexity_score, originality_score)
        
        print(f"Generated and logged Julia art with seed: {seed}, Palette: {palette_name}, Complexity: {complexity_score:.2f}")

    # Log the final table to W&B
    run.log({"art_generations": table})
    run.finish()
    print("\nBatch generation complete. Check your W&B dashboard to see the scored fractals!")

if __name__ == "__main__":
    main()

