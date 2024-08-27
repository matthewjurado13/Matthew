import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

# Capture image from webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

ret, frame = cap.read()
cap.release()

if not ret:
    print("Error: Failed to capture image.")
    exit()

# Save the captured image
captured_image_path = 'captured_image.jpg'
cv2.imwrite(captured_image_path, frame)

# Load the saved captured image and the reference image
captured_img = cv2.imread(captured_image_path)
url = 'Socketed_part.jpg'
reference_img = cv2.imread(url)

if reference_img is None:
    print("Error: Could not load reference image")
    exit()


# Manually specify the coordinates of the green square (x, y, width, height)
# You should adjust these coordinates based on the actual location of the green square in your reference image
x, y, w, h = 150, 150, 325, 300  # Example values; replace with actual coordinates



# Crop the reference and captured images using the specified coordinates
cropped_reference_img = reference_img[y:y+h, x:x+w]
cropped_captured_img = captured_img[y:y+h, x:x+w]

# Convert both cropped images to grayscale
cropped_reference_gray = cv2.cvtColor(cropped_reference_img, cv2.COLOR_BGR2GRAY)
cropped_captured_gray = cv2.cvtColor(cropped_captured_img, cv2.COLOR_BGR2GRAY)

# Resize images to the same size if necessary (unlikely needed since we crop them to the same size)
if cropped_captured_gray.shape != cropped_reference_gray.shape:
    cropped_reference_gray = cv2.resize(cropped_reference_gray, (cropped_captured_gray.shape[1], cropped_captured_gray.shape[0]))

# Compute SSIM between the two cropped images
similarity_score, diff = ssim(cropped_captured_gray, cropped_reference_gray, full=True)
print(f"Image Similarity: {similarity_score * 100:.2f}%")

# Convert diff to a format that can be displayed
diff = (diff * 255).astype("uint8")

# Threshold the difference image
_, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

# Find contours of the differences
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw blue rectangles around the differences on the cropped captured image
for contour in contours:
    if cv2.contourArea(contour) > 40:  # Filter out small differences
        cx, cy, cw, ch = cv2.boundingRect(contour)
        cv2.rectangle(cropped_captured_img, (cx, cy), (cx + cw, cy + ch), (255, 0, 0), 2)  # Blue color in BGR

# Display the images and the highlighted differences
cv2.imshow("Cropped Captured Image with Differences", cropped_captured_img)
cv2.imshow("Cropped Reference Image", cropped_reference_img)
cv2.imshow(f"Difference {100 - (similarity_score * 100):.2f}%", diff)

cv2.waitKey(0)
cv2.destroyAllWindows()
