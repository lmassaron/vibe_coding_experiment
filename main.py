import os
import random
import wandb
import time
import argparse
import threading
from PIL import Image

# Import modularized components
from fractal_core import generate_fractal, calculate_complexity, JULIA_C_VALUES
from palettes import palettes
from web_utils import start_server, clean_previous_images, generate_html_index, PORT

def main():
    parser = argparse.ArgumentParser(description="Generate Julia fractals with various palettes and log to W&B.")
    parser.add_argument("--width", type=int, default=512, help="Width of the generated image.")
    parser.add_argument("--height", type=int, default=512, help="Height of the generated image.")
    parser.add_argument("--max_iter", type=int, default=150, help="Maximum iterations for fractal calculation.")
    parser.add_argument("--num_images", type=int, default=100, help="Number of fractals to generate in a batch.")
    parser.add_argument("--image_dir", type=str, default="generated_images", help="Directory to save generated images.")
    parser.add_argument("--port", type=int, default=PORT, help="Port for the local web server.")
    parser.add_argument("--julia_c_idx", type=int, default=-1, 
                        help="Index of the Julia c-value to use from the curated list. -1 for random.")
    
    args = parser.parse_args()

    # Conditional W&B Initialization
    use_wandb = os.environ.get("WANDB_API_KEY") is not None
    if use_wandb:
        run = wandb.init(project="VibeCoding", job_type="julia-fractal-generation-full-features")
        table = wandb.Table(columns=["image", "palette_name", "seed", "complexity_score", "originality_score", "julia_c_value"])
    else:
        print("WANDB_API_KEY not found. Skipping W&B logging.")

    # Define paths
    current_cwd = os.getcwd()
    image_full_path = os.path.join(current_cwd, args.image_dir)
    index_html_path = os.path.join(current_cwd, "index.html")

    # Start the web server in a separate thread
    # The server_thread will now return the httpd object
    httpd_instance = None
    server_thread = threading.Thread(target=lambda: globals().update(httpd_instance=start_server(current_cwd)))
    server_thread.start()
    
    # Give the server a moment to start up
    time.sleep(1)

    clean_previous_images(image_full_path, index_html_path)
    os.makedirs(image_full_path, exist_ok=True)

    print(f"Generating a batch of {args.num_images} Julia fractals...")

    generated_image_data = [] # Store (img_path, metadata_tuple) for HTML generation
    for i in range(args.num_images):
        seed = random.randint(0, 1000000)
        random.seed(seed) # Seed random for reproducible fractal parameters

        # Select Julia c-value
        if args.julia_c_idx != -1 and args.julia_c_idx < len(JULIA_C_VALUES):
            julia_c_value = JULIA_C_VALUES[args.julia_c_idx]
        else:
            julia_c_value = random.choice(JULIA_C_VALUES)
        
        palette_name, palette_func = random.choice(list(palettes.items()))
        
        art_array, iteration_data = generate_fractal(args.width, args.height, args.max_iter, julia_c_value, palette_func)
        art_image = Image.fromarray(art_array)
        
        # Score the generation
        complexity_score = calculate_complexity(iteration_data)
        originality_score = seed # Using the seed as a direct originality metric

        # Log to W&B Table
        img_filename = f"julia_art_{seed}_{palette_name}.png"
        img_path = os.path.join(image_full_path, img_filename)
        art_image.save(img_path)
        
        metadata = (palette_name, seed, complexity_score, originality_score, str(julia_c_value))
        generated_image_data.append((img_path, metadata))
        
        if use_wandb:
            table.add_data(wandb.Image(img_path), *metadata)
        
        print(f"Generated and logged Julia art with seed: {seed}, Palette: {palette_name}, Complexity: {complexity_score:.2f}")

    # Generate HTML index in the original directory
    generate_html_index(generated_image_data, args.image_dir, index_html_path)

    # Log the final table to W&B
    if use_wandb:
        run.log({"art_generations": table})
        run.finish()
    
    print("\nBatch generation complete. Check your W&B dashboard to see the scored fractals! (if API key was set)")
    print(f"You can also view the generated images locally at http://localhost:{args.port}")
    print("To rank by 'beauty', you can add a custom column in the W&B UI and manually assign scores.")
    print("Press Ctrl+C to stop the web server and exit.")

    try:
        # Keep the main thread alive to allow the server thread to continue running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server and exiting.")
        if httpd_instance:
            httpd_instance.shutdown()
            httpd_instance.server_close()

if __name__ == "__main__":
    main()