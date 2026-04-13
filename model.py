import cv2
import numpy as np

def analyze_thermal_image(image_path):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not load image.")

    # Resize to 300x300
    img = cv2.resize(img, (300, 300))

    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Compute average pixel intensity (0-255)
    avg_intensity = float(round(np.mean(img), 4))

    # Map intensity to temperature (0-100 scale)
    temperature = round((avg_intensity / 255) * 100, 2)

    # Classify
    if temperature < 30:
        label = "Cold"
    elif temperature <= 60:
        label = "Normal"
    else:
        label = "Hot"

    return {
        "avg_intensity": avg_intensity,
        "temperature": temperature,
        "label": label
    }
