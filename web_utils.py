import os
import glob
import http.server
import socketserver
import threading
import shutil

PORT = 5555

def start_server(directory, port):
    """Starts a simple HTTP server in a new thread, serving from the specified directory."""
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    httpd = None
    try:
        httpd = socketserver.TCPServer(("", port), CustomHandler)
        print(f"Serving from '{directory}' at http://localhost:{port}")
        
        # Return the server instance so it can be shut down later
        return httpd
        
    except Exception as e:
        print(f"Error starting server: {e}")
        if httpd:
            httpd.server_close()
        return None

def clean_previous_images(image_dir, index_html_path):
    """Deletes all previously generated fractal images and index.html."""
    print("Cleaning up previous images and index.html...")
    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)
    if os.path.exists(index_html_path):
        os.remove(index_html_path)
    print("Previous images and index.html cleaned.")

def generate_html_index(image_filenames, image_dir_name, index_html_path):
    """Generates an HTML index file with thumbnails of the images."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Julia Fractals</title>
    <style>
        body { font-family: sans-serif; background-color: #333; color: #eee; margin: 0; padding: 0; }
        h1 { text-align: center; padding: 20px; color: #eee; }
        .container { display: flex; flex-wrap: wrap; gap: 15px; padding: 20px; justify-content: center; }
        .thumbnail { 
            border: 1px solid #555; 
            padding: 8px; 
            background-color: #222; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: transform 0.2s;
            border-radius: 8px;
            overflow: hidden;
            width: 180px; /* Fixed width for better layout */
            text-align: center;
        }
        .thumbnail:hover { transform: translateY(-5px); }
        .thumbnail img { 
            width: 100%; 
            height: 150px; /* Fixed height for consistent thumbnails */
            object-fit: cover; 
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .thumbnail p { margin: 0; font-size: 0.9em; color: #bbb; }
        .thumbnail p strong { color: #fff; }
    </style>
</head>
<body>
    <h1>Generated Julia Fractals</h1>
    <div class="container">
"""
    for img_path, metadata in image_filenames:
        # Use os.path.join to create the correct relative path for HTML
        # metadata is a tuple: (palette_name, seed, complexity_score, originality_score, julia_c_value)
        html_content += f"""
        <div class="thumbnail">
            <img src="{os.path.join(image_dir_name, os.path.basename(img_path))}" alt="{os.path.basename(img_path)}">
            <p><strong>Palette:</strong> {metadata[0]}</p>
            <p><strong>Seed:</strong> {metadata[1]}</p>
            <p><strong>Complexity:</strong> {metadata[2]:.2f}</p>
            <p><strong>Originality:</strong> {metadata[3]:.2f}</p>
            <p><strong>C-Value:</strong> {metadata[4]}</p>
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    # Write index.html to the main project directory
    with open(index_html_path, "w") as f:
        f.write(html_content)
    print("Generated index.html with thumbnails.")