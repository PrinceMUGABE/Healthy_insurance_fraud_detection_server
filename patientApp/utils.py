import cv2

def is_high_quality(image_data):
    # Load the image data using OpenCV
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # Check image dimensions
    height, width, _ = image.shape
    if height < 200 or width < 200:
        return False

    # Add more checks as needed (e.g., image sharpness, noise levels, etc.)
    # Example: Check for image blur using Laplacian variance
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
    if laplacian_var < 100:
        return False

    # Add more quality checks based on your requirements

    return True
