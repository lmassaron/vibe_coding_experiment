import os
import random
import wandb
import numpy as np
from PIL import Image

# Initialize W&B run
run = wandb.init(project="VibeCoding", job_type="art-generation")

# --- Art Generation Parameters ---
width, height = 512, 512
max_iter = 100 # Max iterations for fractal calculation

table = wandb.Table(columns=["image", "art_type", "seed", "vibe_score", "tags"])

def generate_mandelbrot(c, max_iter):
    z = c
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

def generate_julia(c, z, max_iter):
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

def generate_fractal(art_type, seed):
    """Generates a Mandelbrot or Julia set fractal."""
    random.seed(seed)
    
    # --- Fractal Parameters ---
    c_real = random.uniform(-2, 1)
    c_imag = random.uniform(-1.5, 1.5)
    z_real = random.uniform(-1, 1)
    z_imag = random.uniform(-1, 1)
    
    img = Image.new('RGB', (width, height), color = 'black')
    pixels = img.load()

    for x in range(width):
        for y in range(height):
            # Scale and translate pixel coordinates to complex plane
            real = (x - width / 2) * 4 / width
            imag = (y - height / 2) * 4 / height

            if art_type == 'mandelbrot':
                m = generate_mandelbrot(complex(real, imag), max_iter)
                color = (m % 256, (m * 5) % 256, (m * 10) % 256)
            elif art_type == 'julia':
                c = complex(c_real, c_imag)
                z = complex(real, imag)
                m = generate_julia(c, z, max_iter)
                color = ((m*2) % 256, (m*7) % 256, (m*13) % 256)
            
            pixels[x, y] = color
            
    return img

def main():
    print("Press 'g' to generate new art, or 'q' to quit.")
    
    while True:
        user_input = input()
        if user_input.lower() == 'g':
            seed = random.randint(0, 1000000)
            art_type = random.choice(['mandelbrot', 'julia'])
            
            art = generate_fractal(art_type, seed)
            
            # Log to W&B Table
            img_path = f"art_{art_type}_{seed}.png"
            art.save(img_path)
            
            table.add_data(wandb.Image(img_path), art_type, seed, None, None)
            
            print(f"Generated and logged {art_type} art with seed: {seed}")
            
        elif user_input.lower() == 'q':
            break

    # Log the final table to W&B
    run.log({"art_generations": table})
    run.finish()
    print("Art generation session finished. Check your W&B dashboard!")

if __name__ == "__main__":
    main()