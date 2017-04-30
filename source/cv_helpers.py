import cv2
import numpy as np

# Define a function that thresholds the S-channel of HLS
def hls_select(img, thresh=(0, 255)):
    # 1) Convert to HLS color space
    hls = cv2.cvtColor( img, cv2.COLOR_RGB2HLS )
    
    # 2) Apply a threshold to the S channel
    s = hls[:,:,2]
    binary_output = np.zeros_like( s )
    binary_output[ (s>thresh[0]) & (s<=thresh[1]) ] = 255
    
    # 3) Return a binary image of threshold result
    return binary_output

# Define a function that applies Sobel x and y, then computes the direction of the gradient and applies a threshold
def dir_threshold(img, sobel_kernel=3, thresh=(0, np.pi/2)):
    # Convert to grayscale
    gray = cv2.cvtColor( img, cv2.COLOR_RGB2GRAY )
    
    # Take the gradient in x and y separately
    grad_x = cv2.Sobel( gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel )
    grad_y = cv2.Sobel( gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel )
    
    # Take the absolute value of the x and y gradients
    grad_x_abs = np.absolute( grad_x )
    grad_y_abs = np.absolute( grad_y )
    
    # Use np.arctan2(abs_sobely, abs_sobelx) to calculate the direction of the gradient 
    direction = np.arctan2( grad_y_abs, grad_x_abs )
    
    # Create a binary mask where direction thresholds are met
    binary_output = np.zeros_like( gray )
    binary_output[ (direction > thresh[0]) & (direction < thresh[1]) ] = 1
    
    # Return this mask binary_output image
    return binary_output

# Define a function that applies Sobel x and y, then computes the magnitude of the gradient and applies a threshold
def mag_thresh(img, sobel_kernel=3, mag_thresh=(0, 255)):
    
    # Convert to grayscale
    gray = cv2.cvtColor( img, cv2.COLOR_RGB2GRAY )
    
    # Take the gradient in x and y separately
    x_grad = cv2.Sobel( gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel )
    y_grad = cv2.Sobel( gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel )
    
    # Calculate the magnitude
    mag = np.sqrt( np.square( x_grad ) + np.square( y_grad ) )
    
    # Scale to 8-bit (0 - 255) and convert to type = np.uint8
    scale_factor = np.max( mag ) / 255
    scaled = (mag / scale_factor).astype( np.uint8 )

    # Create a binary mask where mag thresholds are met
    binary_output = np.zeros_like( mag )
    binary_output[ (scaled > mag_thresh[0]) & (scaled < mag_thresh[1]) ] = 1

    # Return this binary_output image
    return binary_output

# Define a function that applies Sobel x or y, then takes an absolute value and applies a threshold.
def abs_sobel_thresh(img, orient='x', sobel_kernel=3, thresh=(0, 255)):
    # Convert to grayscale
    gray = cv2.cvtColor( img, cv2.COLOR_RGB2GRAY )
    
    # Take the derivative in x or y given orient = 'x' or 'y', and absolute
    if orient == 'x':
        x = 1
        y = 0
    else:
        x = 0
        y = 1
    deriv = np.absolute( cv2.Sobel( gray, cv2.CV_64F, x, y ) )
    
    # Rescale back to 8 bit integer
    scaled_sobel = np.uint8( 255*deriv / np.max(deriv) )
    
    # Create a copy and apply the threshold
    binary_output = np.zeros_like(scaled_sobel)    
    binary_output[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1
    return binary_output

# Define our mega threshold function
def threshold(image):
    # Apply each of the thresholding functions
    ksize = 3
    gradx_binary = abs_sobel_thresh(image, orient='x', sobel_kernel=ksize, thresh=(10, 255))
    grady_binary = abs_sobel_thresh(image, orient='y', sobel_kernel=ksize, thresh=(10, 255))
    mag_binary = mag_thresh(image, sobel_kernel=ksize, mag_thresh=(30, 255)) 
    dir_binary = dir_threshold(image, sobel_kernel=ksize, thresh=(0.9, 1.2))

    # Stack each channel to view their individual contributions in green and blue respectively
    stacked_binary = np.dstack(( np.zeros_like(mag_binary), gradx_binary, mag_binary))

    # Combine them
    combined = np.zeros_like(dir_binary)
    combined[ ((gradx_binary == 1) | (grady_binary == 1) | (mag_binary == 1) ) & dir_binary == 1 ] = 1
    return combined, stacked_binary, gradx_binary, grady_binary, mag_binary, dir_binary

    
