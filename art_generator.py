import os
import random
import wandb
import numpy as np
from PIL import Image

# Initialize W&B run
run = wandb.init(project="VibeCoding", job_type="art-generation-scored")

# --- Art Generation Parameters ---
width, height = 512, 512
max_iter = 150 # Increased for more complexity potential

# Updated table with scoring columns
table = wandb.Table(columns=["image", "art_type", "seed", "complexity_score", "originality_score"])

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
    """Generates a fractal and returns the image and its iteration data for scoring."""
    random.seed(seed)
    
    # --- Fractal Parameters ---
    c_real = random.uniform(-1, 1)
    c_imag = random.uniform(-1, 1)
    
    img = Image.new('RGB', (width, height), color = 'black')
    pixels = img.load()
    iteration_data = np.zeros((width, height))

    for x in range(width):
        for y in range(height):
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
            iteration_data[x, y] = m
            
    return img, iteration_data

def calculate_complexity(iteration_data):
    """Calculates a complexity score based on the average iteration count."""
    return np.mean(iteration_data)

def main():
    num_images = random.randint(10, 20)
    print(f"Generating a batch of {num_images} fractals...")

    for i in range(num_images):
        seed = random.randint(0, 1000000)
        art_type = random.choice(['mandelbrot', 'julia'])
        
        art, iteration_data = generate_fractal(art_type, seed)
        
        # Score the generation
        complexity_score = calculate_complexity(iteration_data)
        originality_score = seed # Using the seed as a direct originality metric

        # Log to W&B Table
        img_path = f"art_{art_type}_{seed}.png"
        art.save(img_path)
        
        table.add_data(wandb.Image(img_path), art_type, seed, complexity_score, originality_score)
        
        print(f"Generated and logged {art_type} art with seed: {seed}, Complexity: {complexity_score:.2f}")

    # Log the final table to W&B
    run.log({"art_generations": table})
    run.finish()
    print("\nBatch generation complete. Check your W&B dashboard to see the scored fractals!")

if __name__ == "__main__":
    main()
