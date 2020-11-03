#!usr/bin/python3
from PIL import Image, ImageDraw
import random
import numpy

def find_most_common_color(image: Image):
    """Return the most common RBG or RGBA color of a Image object
    
    Arguments:
        image {Image} -- Image object of a picture
    
    Raises:
        TypeError: raise if pass an non Image object
    
    Returns:
        tuple -- a tuple represents a RGB or RGBA color
    """

    if not isinstance(image, Image.Image):
        raise TypeError('image argument must be a PIL.Image object')

    pixels = image.getdata()
    pixel_dict = {}
    for pixel in pixels:
        if pixel not in pixel_dict:
            pixel_dict[pixel] = 1
        else:
            pixel_dict[pixel] += 1
    
    return max(pixel_dict)

class Sprite:
    """Sprite figure to instantiate a sprite object

    Arguments:
        label {int} -- label of a Sprite object
        x1 {int} -- x-axis value of top_left point of a Sprite object
        y1 {int} -- y-axis value of top_left point of a Sprite object
        x2 {int} -- x-axis value of bottom_right point of a Sprite object
        y2 {int} -- y-axis value of bottom_right point of a Sprite object

    Attributes:
        label {int} -- label of a Sprite object
        __top_left {int} -- top_left point of a Sprite object
        __bottom_right {int} -- bottom_right point of a Sprite object
        __width {int} -- number of horizontal pixels of a Sprite object
        __height {int} -- number of vertical pixels of a Sprite object

    Raises:
        ValueError: raise if arguments are not a positive integer
    
    Returns:
        obj -- An object which is instantiated from Sprite class
    """
    def __init__(self, label, x1, y1, x2, y2):
        if not all([isinstance(_, int) for _ in [label, x1, y1, x2, y2]])\
            or not all([_ >= 0 for _ in [label, x1, x2, y1, y2]])\
            or not (x2 > x1 and y2 > y1):
            raise ValueError('Invalid coordinates')

        self.__label = label
        self.__top_left = (x1, y1)
        self.__bottom_right = (x2, y2)
        self.__width = x2 - x1
        self.__height = y2 - y1 

    @property
    def label(self):
        return self.__label

    @property
    def top_left(self):
        return self.__top_left
    
    @property
    def bottom_right(self):
        return self.__bottom_right

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

def find_sprites(image, background_color=None):
    """Return a label bit map and a dictionary of sprites and its label
    
    Arguments:
        image {obj} -- a PIL.Image.Image object
    
    Keyword Arguments:
        background_color {list} -- argument that define the background color of the Image (default: {[]})
    
    Raises:
        TypeError: raise if not pass a Image object
        ValueError: raise if not pass a proper background color into background color argument
    
    Returns:
        list, dict -- a bit map and a dictionary of sprites
    """
    if not isinstance(image, Image.Image):
        raise TypeError('image argument must be a PIL.Image object')

    if background_color != None:
        if image.mode == 'L':
            if not isinstance(background_color, int):
                raise ValueError('background_color of a grayscale format image must be a integer')
            elif background_color <= 0:
                raise ValueError('background_color of a grayscale format image must be a integer')

        if image.mode in ['RGB', 'RGBA']:
            if not isinstance(background_color, tuple):
                raise ValueError('background_color of a RGB or RGBA format image must be a tuple')
            
            elif ((len(background_color) != 3 and image.mode == 'RGB') \
                or (len(background_color) != 4 and image.mode =='RGBA'))\
                or not all([isinstance(_, int) and _ >= 0 and _ <= 255 for _ in background_color]):
                raise ValueError('background_color of a RGB or RGBA format image must be a tuple of \
                    three integers between 0-255')

    # Set background pixel or pixel that will be ignore in the process 
    if background_color == None:
        ignore_pixel = find_most_common_color(image)
    else:
        ignore_pixel = background_color

    pixel_map = list(image.getdata())
    image_size = image.size
    bit_map = []
    _1d_bit_map = []

    # create one dimesional bit map
    for i in range(image_size[0]*image_size[1]):
        if image.mode == 'RGBA'\
            and background_color == None\
            and pixel_map[i][3] == 0:
                _1d_bit_map.append(0)
        elif pixel_map[i] == background_color\
            and background_color != None:
            _1d_bit_map.append(0)
        else:
            _1d_bit_map.append(1)

    del pixel_map
    clone_bit_map = []

    # Create two dimensional bit map and its clone
    for _ in range(image_size[1]):
        bit_map.append(_1d_bit_map[_*image_size[0]:_*image_size[0]+image_size[0]])
        clone_bit_map.append(_1d_bit_map[_*image_size[0]:_*image_size[0]+image_size[0]])

    del _1d_bit_map
    i,j = 0,0 
    sprite = [] # contain the axis of pixel of the current sprite
    in_a_sprite_area = False # identify the scan session
    sprite_areas = [] # contain sprite areas that found
    connect_pixels = []

    # scaning sprite areas in the bit map
    while True:
        if clone_bit_map[i][j] == 1: # if current position pixel is 1
            connect_pixels = [(i,j+1), (i,j-1), (i+1,j+1), (i+1,j),\
                 (i+1,j-1), (i-1,j+1), (i-1,j-1), (i-1,j)]
            clone_bit_map[i][j] = 0
        
        # start a new sprite scan
        if connect_pixels != [] and sprite == []:
            sprite.append((i,j))

        # if is scaning a sprite area
        if connect_pixels != [] and sprite != []:
            for pixel in connect_pixels:
                try:
                    clone_bit_map[pixel[0]][pixel[1]]
                except:
                    continue

                if clone_bit_map[pixel[0]][pixel[1]] == 1:
                    sprite.append(pixel)
                    i,j = pixel[0], pixel[1]
                    in_a_sprite_area = True
                    break

        connect_pixels = []

        # if not in a sprite scan session
        if not in_a_sprite_area and sprite != []: 
            sprite_areas.append(sprite)
            sprite = []
            i,j = 0,0
        
        if in_a_sprite_area: # skip to another step
            in_a_sprite_area = False
            continue

        j += 1
        if j == image_size[0]:
            i += 1
            j = 0
        
        if i == image_size[1]:
            break
    
    del clone_bit_map, in_a_sprite_area, sprite
    pixel_coordinates_of_sprites = []
    sprite_container = []

    # combine sprite areas into the proper sprite
    while True:
        sprite_container.extend(sprite_areas.pop(0))
        i,j,i_sc,i_sa,indice = -1,-1,0,0,0
        while True:
            # if current point changed
            if sprite_container[i_sc] != (i,j):
                i,j = sprite_container[i_sc][0], sprite_container[i_sc][1]
                connect_pixels = [(i,j+1), (i,j-1), (i+1,j+1), (i+1,j),(i+1,j-1),\
                     (i-1,j+1), (i-1,j-1), (i-1,j)]

            # if prite area connect sprite in container
            if sprite_areas[indice][i_sa] in connect_pixels:
                sprite_container.extend(sprite_areas.pop(indice))
                i_sa -= 1

            i_sa += 1
            # if sprite area indice run over the index 
            if indice < len(sprite_areas):
                if i_sa >= len(sprite_areas[indice]): 
                    indice += 1
                    i_sa = 0 
            
            if indice >= len(sprite_areas):
                indice = 0
                i_sa = 0
                i_sc += 1
            
            if i_sc >= len(sprite_container) or sprite_areas == []:
                break

        pixel_coordinates_of_sprites.append(sprite_container)
        sprite_container = []
        
        if sprite_areas == []:
            break

    label = 1
    sprites = {}

    #find bottom-right and top-left and set label for bit map sprite
    for sprite in pixel_coordinates_of_sprites:
        max_x_axis, min_x_axis, max_y_axis, min_y_axis\
             = sprite[0][0], sprite[0][0], sprite[0][1], sprite[0][1]
        for axis in sprite:
            bit_map[axis[0]][axis[1]] = label
            if max_x_axis < axis[0]:
                max_x_axis = axis[0]
            if min_x_axis > axis[0]:
                min_x_axis = axis[0]
            if max_y_axis < axis[1]:
                max_y_axis = axis[1]
            if min_y_axis > axis[1]:
                min_y_axis = axis[1]

        sprites[label] = Sprite(label, min_x_axis, min_y_axis, max_x_axis, max_y_axis)
        label += 1

    del label, pixel_coordinates_of_sprites

    return sprites, bit_map

def create_sprite_labels_image(sprites, label_map, background_color=(255, 255, 255)):
    """Return a sprite labels image
    
    Arguments:
        sprites {dict} -- a dict contains label and its Sprite object that can get from find_sprites function
        label_map {list} -- two dimesional array of contains label of the pixel that can get from find_sprites function
    
    Keyword Arguments:
        background_color {tuple} -- background color of the output image (default: {(255, 255, 255)})
    
    Raises:
        TypeError: raise if background_color parameter is not a tuple
        ValueError: raise if background_color parameter is not a tuple of three or four integers between 0 and 255
    
    Returns:
        obj -- Image instance of sprite labels image
    """
    if not isinstance(background_color, tuple):
        raise TypeError('background_color argument must be a tuple')
    if (len(background_color) < 3 and len(background_color) > 4)\
        or not all([_>=0 and _<=255 for _ in background_color]):
        raise ValueError('background_color argument must be a tuple contains (0-255,0-255,0-255,0-255)')
    
    if len(background_color) == 4:
        mode = 'RGBA'
    else:
        mode = 'RGB'

    sprite_color = {}
    for label in range(1,len(sprites)+1):
        if mode == 'RGB':
            sprite_color[label] = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        else:
            sprite_color[label] = (random.randint(0,255),random.randint(0,255),random.randint(0,255),background_color[3])
    
    #get sprite's coordinates point
    sprite_coordinate = {}
    for i in range(len(label_map)):
        for j in range(len(label_map[0])):
            if label_map[i][j] != 0:
                try:
                    sprite_coordinate[label_map[i][j]]                
                except:
                    sprite_coordinate[label_map[i][j]] = [(j,i)]
                sprite_coordinate[label_map[i][j]].append((j,i))
    
    #Create a new image, draw sprite and its bounding box
    image = Image.new(mode, (len(label_map[0]),len(label_map)), background_color)
    draw_im = ImageDraw.Draw(image, mode)
    for label in sprite_coordinate:
        draw_im.point(sprite_coordinate[label], sprite_color[label])
        draw_im.rectangle([(sprites[label].top_left[1],sprites[label].top_left[0]),\
            (sprites[label].bottom_right[1],sprites[label].bottom_right[0])],\
                 outline=sprite_color[label])

    return image

class SpriteSheet:
    """This class implements image's sprite and generates spritesheet
    
    Arguments:
        fd -- accept imformation of source image, which can be either:
                * the name and path (a string) that references an image file in the local file system;
                * a pathlib.Path object that references an image file in the local file system ;
                * a file object that MUST implement read(), seek(), and tell() methods, and be opened 
                  in binary mode;
                * a Image object.
        background_color -- accept as an optional argument, which can be either:
                * an integer if the mode is grayscale;
                * a tuple (red, green, blue) of integers if the mode is RGB;
                * a tuple (red, green, blue, alpha) of integers if the mode is RGBA. 
                  The alpha element is optional. If not defined, while the image mode 
                  is RGBA, the constructor considers the alpha element to be 255.
    Attributes:
        __background_color: background color of the source image
        image: Image.Image object source in the instance

    Raises:
        ValueError: raise if fd, which is not a Image.Image object, 
                    does not implements with Image.Image constructor
    """
    def __init__(self, fd, background_color=None):
        if not isinstance(fd, Image.Image):
            try:
                Image.open(fd)
            except:
                raise ValueError("fd argument must implement with Image class constructor")
            image = Image.open(fd)
        else:
            image = fd
        
        self.__background_color = background_color
        self.image = image

    @property
    def background_color(self):
        """Return background color of the source image"""
        return self.__background_color

    def find_sprites(self):
        """Return a label bit map and a dictionary of sprites and its label"""
        return find_sprites(self.image, self.__background_color)

    def create_sprite_labels_image(self):
        """Return a sprite labels image and its bounding box"""
        sprites, label_map = self.find_sprites()
        return create_sprite_labels_image(sprites, label_map)
