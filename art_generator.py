import os
import random
import wandb
from PIL import Image, ImageDraw

# Initialize W&B run
run = wandb.init(project="VibeCoding", job_type="art-generation")

# --- Art Generation Parameters ---
width, height = 512, 512
# Every time a new piece of art is generated, log the image to a W&B Table
# Also, log the parameters that created it
table = wandb.Table(columns=["image", "seed", "num_shapes", "vibe_score", "tags"])

def generate_art(seed):
    """Generates a unique piece of abstract art based on a seed."""
    random.seed(seed)
    img = Image.new('RGB', (width, height), color = 'black')
    draw = ImageDraw.Draw(img)

    num_shapes = random.randint(5, 50)

    for _ in range(num_shapes):
        shape_type = random.choice(['rectangle', 'ellipse', 'line'])
        
        # Random color
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = (r, g, b)

        # Random position and size
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        if shape_type == 'rectangle':
            draw.rectangle([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], fill=color)
        elif shape_type == 'ellipse':
            draw.ellipse([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], fill=color)
        elif shape_type == 'line':
            draw.line([x1, y1, x2, y2], fill=color, width=random.randint(1, 5))
            
    return img, num_shapes

def main():
    print("Press 'g' to generate new art, or 'q' to quit.")
    
    while True:
        user_input = input()
        if user_input.lower() == 'g':
            seed = random.randint(0, 1000000)
            art, num_shapes = generate_art(seed)
            
            # Log to W&B Table
            img_path = f"art_{seed}.png"
            art.save(img_path)
            
            # Add data to the table
            # In your Weave dashboard, view the table of generated images
            # Use Weave's tools to "score" your own creations
            # Add a column to your table for a "vibe_score" (a rating from 1-10)
            # or subjective tags like "chaotic," "calm," or "colorful."
            table.add_data(wandb.Image(img_path), seed, num_shapes, None, None)
            
            print(f"Generated and logged art with seed: {seed}")
            
        elif user_input.lower() == 'q':
            break

    # Log the final table to W&B
    run.log({"art_generations": table})
    run.finish()
    print("Art generation session finished. Check your W&B dashboard!")

if __name__ == "__main__":
    main()