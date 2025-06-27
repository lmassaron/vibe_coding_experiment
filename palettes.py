
import numpy as np

# Palettes now take 'm' (iteration count, potentially smoothed/log-scaled) and 'max_m' (max_iter, also log-scaled)

# 1. Maximum Detail and Scientific Analysis
def palette_viridis_like(m, max_m):
    # Simple approximation of Viridis-like, focusing on smooth progression
    # Interpolate based on normalized m
    norm_m = m / max_m
    colors = [
        np.array([68, 1, 84]),   # Dark Purple-Blue
        np.array([59, 82, 139]), # Blue
        np.array([33, 145, 140]),# Teal
        np.array([129, 199, 124]),# Light Green
        np.array([253, 231, 37]) # Bright Yellow
    ]
    
    idx = int(norm_m * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (norm_m * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_grayscale(m, max_m):
    val = int(m / max_m * 255)
    return (val, val, val)

def palette_single_blue_hue(m, max_m):
    # Gradient from very dark blue to light blue
    intensity = m / max_m
    r = int(intensity * 50)
    g = int(intensity * 100)
    b = int(intensity * 200)
    return (r, g, b)

# 2. Aesthetic Beauty and Artistic Expression
def palette_analogous_blue_purple(m, max_m):
    # Blue to purple gradient
    norm_m = m / max_m
    colors = [
        np.array([0, 0, 100]),   # Dark Blue
        np.array([50, 0, 150]),  # Medium Purple
        np.array([100, 0, 200]), # Bright Purple
        np.array([150, 50, 250]) # Light Purple
    ]
    idx = int(norm_m * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (norm_m * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_fire(m, max_m):
    # Red, Orange, Yellow
    norm_m = m / max_m
    colors = [
        np.array([0, 0, 0]),     # Black
        np.array([100, 0, 0]),   # Dark Red
        np.array([200, 50, 0]),  # Orange
        np.array([255, 150, 0]), # Bright Orange
        np.array([255, 255, 0])  # Yellow
    ]
    idx = int(norm_m * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (norm_m * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_ocean(m, max_m):
    # Deep blue to cyan/white
    norm_m = m / max_m
    colors = [
        np.array([0, 0, 50]),    # Deep Navy
        np.array([0, 50, 150]),  # Medium Blue
        np.array([0, 150, 200]), # Cyan
        np.array([150, 255, 255])# Light Cyan
    ]
    idx = int(norm_m * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (norm_m * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_metallic(m, max_m):
    # Grays, silvers, and golds
    norm_m = m / max_m
    colors = [
        np.array([0, 0, 0]),     # Black
        np.array([50, 50, 50]),  # Dark Gray
        np.array([150, 150, 150]),# Silver
        np.array([200, 180, 100]),# Gold
        np.array([255, 230, 150]) # Bright Gold
    ]
    idx = int(norm_m * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (norm_m * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

def palette_nebula(m, max_m):
    # Dark purples, blues, magentas, with bright highlights
    norm_m = m / max_m
    colors = [
        np.array([0, 0, 0]),     # Black
        np.array([20, 0, 40]),   # Dark Purple
        np.array([40, 0, 80]),   # Medium Purple
        np.array([80, 0, 160]),  # Bright Purple
        np.array([120, 0, 200]), # Magenta-Blue
        np.array([200, 100, 255]),# Light Magenta
        np.array([255, 255, 255]) # White (for stars)
    ]
    idx = int(norm_m * (len(colors) - 1))
    if idx >= len(colors) - 1:
        return tuple(colors[-1])
    
    ratio = (norm_m * (len(colors) - 1)) - idx
    color = colors[idx] * (1 - ratio) + colors[idx+1] * ratio
    return tuple(color.astype(int))

# 3. Classic Psychedelic Look
def palette_psychedelic(m, max_m):
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
    return psy_colors[int(m) % len(psy_colors)] # Cast m to int for modulo operation

palettes = {
    "viridis_like": palette_viridis_like,
    "grayscale": palette_grayscale,
    "single_blue_hue": palette_single_blue_hue,
    "analogous_blue_purple": palette_analogous_blue_purple,
    "fire": palette_fire,
    "ocean": palette_ocean,
    "metallic": palette_metallic,
    "nebula": palette_nebula,
    "psychedelic": palette_psychedelic,
}
