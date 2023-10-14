import cv2
import numpy as np
from scipy.ndimage import zoom

# import imgaug as ia
# import imgaug.augmenters as iaa




def brightness_img(img, value):
    # convert to HSV
    # bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img_float32 = np.float32(img)
    hsv = cv2.cvtColor(img_float32, cv2.COLOR_BGR2HSV)

    # add the value in the value channel
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, value)
    v[v > 255] = 255
    v[v < 0] = 0

    # convert image back to gray
    final_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    # img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def sharp_img(image):
    # # Create the sharpening kernel
    # # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    # kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    
    # # Sharpen the image
    # return cv2.filter2D(image, -1, kernel)
    # blur = cv2.GaussianBlur(image, (0, 0), 3)
    # sh_img = cv2.addWeighted(image, 1.5, blur, -0.5, 0)

    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    
    # Sharpen the image
    return cv2.filter2D(image, -1, kernel)

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

def contrast(img, value):
    brightness = 30
    shadow = brightness
    highlight = 255

    # add the brightness
    alpha_b = (highlight - shadow) / 255
    gamma_b = shadow
    img = cv2.addWeighted(img, alpha_b, img, 0, gamma_b)

    # add the constrast
    f = 131 * (value + 127) / (127 * (131 - value))
    alpha_c = f
    gamma_c = 127 * (1 - f)
    img = cv2.addWeighted(img, alpha_c, img, 0, gamma_c)

    return img

def img2gray(img):
    img_float32 = np.float32(img)
    im = cv2.cvtColor(img_float32, cv2.COLOR_RGB2GRAY)
    return cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)

def zoom_img(img, zoom_factor):
    # https://stackoverflow.com/questions/37119071/scipy-rotate-and-zoom-an-image-without-changing-its-dimensions
    h, w = img.shape[:2]
    zoom_tuple = (zoom_factor,) * 2 + (1,) * (img.ndim - 2)
    zh = int(np.round(h / zoom_factor))
    zw = int(np.round(w / zoom_factor))
    top = (h - zh) // 2
    left = (w - zw) // 2

    out = zoom(img[top:top + zh, left:left + zw], zoom_tuple)

    # `out` might still be slightly larger than `img` due to rounding, so
    # trim off any extra pixels at the edges
    trim_top = ((out.shape[0] - h) // 2)
    trim_left = ((out.shape[1] - w) // 2)
    out = out[trim_top:trim_top + h, trim_left:trim_left + w]

    return out

def translate(img, offsetx, offsety): 
    translation_matrix = np.float32([ [1, 0, offsetx], [0, 1, offsety] ])
    return cv2.warpAffine(img, translation_matrix, img.shape[1::-1], flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def horizontal_flip(img):
    return np.fliplr(img)


# def noise_img(img):
#     gaussian = np.random.normal(0, 20, (img.shape[0], img.shape[1]))
#     return img + gaussian

def noise_img(image, noise_typ = "gauss"):
    if noise_typ == "gauss":
        row,col,ch= image.shape
        mean = 0
        var = 0.1
        sigma = var**0.5
        gauss = np.random.normal(mean,sigma,(row,col,ch))
        gauss = gauss.reshape(row,col,ch)
        noisy = image + gauss
        return noisy
    elif noise_typ == "s&p":
        row,col,ch = image.shape
        s_vs_p = 0.5
        amount = 0.004
        out = np.copy(image)
        # Salt mode
        num_salt = np.ceil(amount * image.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))
                for i in image.shape]
        out[coords] = 1

        # Pepper mode
        num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))
                for i in image.shape]
        out[coords] = 0
        return out
    elif noise_typ == "poisson":
        vals = len(np.unique(image))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(image * vals) / float(vals)
        return noisy
    elif noise_typ == "speckle":
        row,col,ch = image.shape
        gauss = np.random.randn(row,col,ch)
        gauss = gauss.reshape(row,col,ch)        
        noisy = image + image * gauss
        return noisy

def blur_image(img):
    return cv2.GaussianBlur(img, (11, 11), 0)


def rotation(img, angle):
    # rotate image about its center
    image_center = tuple(np.array(img.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    #result = zoom_img(result, 1.2)
    return result
