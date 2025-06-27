import os
import random
import wandb
import numpy as np
from PIL import Image

# Initialize W&B run
run = wandb.init(project="VibeCoding", job_type="julia-fractal-generation-guaranteed-blue-hues")

# --- Art Generation Parameters ---
width, height = 512, 512
max_iter = 150 # Max iterations for fractal calculation

# Updated table with scoring columns
table = wandb.Table(columns=["image", "palette_name", "seed", "complexity_score", "originality_score"])

def generate_julia(c, z, max_iter):
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

# --- Guaranteed Blue-Hue Palette ---
def palette_guaranteed_blue(m):
    # Define key blue colors
    dark_blue = np.array([0, 0, 50])
    medium_blue = np.array([0, 50, 150])
    azure = np.array([0, 127, 255])
    light_blue = np.array([100, 200, 255])

    # Interpolate based on iteration count
    if m < max_iter / 4:
        # Dark to medium blue
        ratio = m / (max_iter / 4)
        color = dark_blue * (1 - ratio) + medium_blue * ratio
    elif m < max_iter / 2:
        # Medium blue to azure
        ratio = (m - max_iter / 4) / (max_iter / 4)
        color = medium_blue * (1 - ratio) + azure * ratio
    elif m < max_iter * 3 / 4:
        # Azure to light blue
        ratio = (m - max_iter / 2) / (max_iter / 4)
        color = azure * (1 - ratio) + light_blue * ratio
    else:
        # Light blue to white-ish blue
        ratio = (m - max_iter * 3 / 4) / (max_iter / 4)
        color = light_blue * (1 - ratio) + np.array([200, 230, 255]) * ratio

    return tuple(color.astype(int))

palettes = {
    "guaranteed_blue": palette_guaranteed_blue,
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
            
            # Set color to black if the point does not escape (background)
            if m == max_iter:
                color = (0, 0, 0) 
            else:
                color = palette_func(m)
            
            pixels[x, y] = color
            iteration_data[x, y] = m
            
    return img, iteration_data

def calculate_complexity(iteration_data):
    """Calculates a complexity score based on the average iteration count."""
    return np.mean(iteration_data)

def main():
    num_images = 50 # Fixed batch size
    print(f"Generating a batch of {num_images} Julia fractals with guaranteed blue-hue palettes and black backgrounds...")

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
    print("To rank by 'beauty', you can add a custom column in the W&B UI and manually assign scores.")

if __name__ == "__main__":
    main()