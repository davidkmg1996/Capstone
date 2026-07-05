import cv2
import numpy as np

image = cv2.imread("test.JPG")  # BGR

# Split channels
b, g, r = cv2.split(image)

def sobel_channel(channel):
    sx = cv2.Sobel(channel, cv2.CV_64F, 1, 0, ksize=3)
    sy = cv2.Sobel(channel, cv2.CV_64F, 0, 1, ksize=3)
    return np.sqrt(sx**2 + sy**2)

# Apply Sobel to each channel
edges_b = sobel_channel(b)
edges_g = sobel_channel(g)
edges_r = sobel_channel(r)

# Combine (take max response)
edges = np.maximum.reduce([edges_b, edges_g, edges_r])

#edges = np.uint8(255 * edges / np.max(edges))
#edges_b = np.uint8(255 * edges_b / np.max(edges_b))
#edges_g = np.uint8(255 * edges_g / np.max(edges_g))
#edges_r = np.uint8(255 * edges_r / np.max(edges_r))

#cv2.imwrite("edges_color.jpg", edges)
cv2.imwrite("edges_b.jpg", edges)
cv2.imwrite("edges_g.jpg", edges)
cv2.imwrite("edges_r.jpg", edges)
