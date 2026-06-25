import cv2
import numpy as np

def preprocess_image(image):
    # Resize image if it's too large (improves API speed and reduces token usage)
    # We'll set a max width/height of 1024 while maintaining aspect ratio
    max_dim = 1024
    height, width = image.shape[:2]
    
    if max(height, width) > max_dim:
        scaling_factor = max_dim / float(max(height, width))
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    # For Gemini, keeping the image in its original color is often better
    # because it uses color to identify logos and document structure.
    # We will just apply a slight unsharp mask to make text pop.
    
    gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
    unsharp_image = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
    
    return unsharp_image
