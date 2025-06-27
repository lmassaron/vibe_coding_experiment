
import numpy as np
import cmath

def generate_julia(z_initial, c, max_iter):
    z = z_initial
    for n in range(max_iter):
        if abs(z) > 2:
            # Smooth coloring algorithm:
            # m = n + 1 - log(log(|z|)) / log(2)
            # This formula provides a "fractional" iteration count for smoother gradients.
            return n + 1 - cmath.log(cmath.log(abs(z))) / cmath.log(2)
        z = z*z + c
    return max_iter # Point did not escape

def calculate_complexity(iteration_data):
    """Calculates a complexity score based on the average iteration count."""
    return np.mean(iteration_data)

def generate_fractal(width, height, max_iter, c_value, palette_func):
    """Generates a Julia set fractal and returns the image and its iteration data for scoring."""
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    iteration_data = np.zeros((height, width))

    for x in range(width):
        for y in range(height):
            # Scale and translate pixel coordinates to complex plane
            real = (x - width / 2) * 4 / width
            imag = (y - height / 2) * 4 / height
            z_initial = complex(real, imag)

            m = generate_julia(z_initial, c_value, max_iter)
            
            # Set color to white if the point does not escape (background)
            if m == max_iter:
                color = (255, 255, 255) 
            else:
                # Apply logarithmic scaling to the iteration count for better detail
                # A small constant (1e-6) is added to avoid log(0) if m is very small
                log_m = cmath.log(m + 1e-6).real 
                color = palette_func(log_m, cmath.log(max_iter + 1e-6).real)
            
            # Clamp color values to 0-255
            color = np.clip(color, 0, 255).astype(int)
            
            img_array[y, x] = color
            iteration_data[y, x] = m.real
            
    return img_array, iteration_data

# Curated list of interesting Julia set 'c' values
# These are known to produce visually appealing and complex fractals
JULIA_C_VALUES = [
    complex(-0.7, 0.27015),
    complex(-0.8, 0.156),
    complex(0.285, 0.01),
    complex(-0.4, 0.6),
    complex(-0.74543, 0.11301),
    complex(-0.1, 0.651),
    complex(-0.79, 0.15),
    complex(0, 0.8),
    complex(-0.12, 0.77),
    complex(-0.7269, 0.1889),
]
