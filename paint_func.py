import cv2
import numpy as np
import random
import time


# # ------------------------------------ Inputs
trace_pointer_area_min = 100
get_pointer_position_area_min = 400
r = 2 #factor to expand box and blur / erode
dict_color = {'green': (0,255,0),
              'blue':(255,0,0),
              'red': (0,0,255),
              'yellow': (0,255,255),
              'white': (255, 255, 255),
              'black': (0,0,0)}
# # ------------------------------------



# -----   Initialize camera
def init_camera(camera_ID):
    camera = cv2.VideoCapture(0)
    # x_len = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    # y_len = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return camera
# --------------------------------------------------
# ----- Make page
def make_white_page(size):

    page = (np.zeros((int(size[0]), int(size[1]), 3)) + 255).astype('uint8')
    return page
# --------------------------------------------------
# ----- Make page
def make_black_page(size):

    page = (np.zeros((int(size[0]), int(size[1]), 3))).astype('uint8')
    return page
# --------------------------------------------------
# -----   Rotate / flip / everything else (depends on camera conf)
def adjust_frame(frame):
    # frame = cv2.rotate(frame, cv2.ROTATE_180)
    frame = cv2.flip(frame, 1)
    return frame
# --------------------------------------------------
# ----- Show a window
def show_window(title_window, window):
    cv2.namedWindow(title_window)
    cv2.imshow(title_window,window)
# --------------------------------------------------
# ----- decorate frame
def put_objects_in_frame(img, objects):
    divisor_screen = objects[0]

    cv2.line(img, (divisor_screen, 0), (divisor_screen, int(img.shape[0])), (255,182,193), thickness=5)

    # cv2.putText(img, 'palette',
                # (int(divisor_screen * 1.1), int(img.shape[0]/10)), cv2.FONT_HERSHEY_SIMPLEX,
                # 2,(255, 255, 255),5)
# --------------------------------------------------
# ----- decorate page
def put_objects_in_page(img):
    cv2.putText(img, 'text',
                (15, 50), cv2.FONT_HERSHEY_SIMPLEX,
                2,(255, 255, 255),5)
# --------------------------------------------------



# -----   colorize
def colorize_img(img, coord, color_to_paint, box):
    """
    r is an input here
    """
    box_to_paint = (np.zeros((box*2, box*2))).astype('uint8')


    if color_to_paint == dict_color['black']:

        img[coord[0]- box: coord[0]+ box,
            coord[1]- box: coord[1]+ box, 0] = box_to_paint + color_to_paint[0]
        img[coord[0]- box: coord[0]+ box,
            coord[1]- box: coord[1]+ box, 1] = box_to_paint + color_to_paint[1]
        img[coord[0]- box: coord[0]+ box,
            coord[1]- box: coord[1]+ box, 2] = box_to_paint + color_to_paint[2]
    else:

        img[coord[0]- box: coord[0]+ box,
            coord[1]- box: coord[1]+ box, 0] = box_to_paint + color_to_paint[0]
        img[coord[0]- box: coord[0]+ box,
            coord[1]- box: coord[1]+ box, 1] = box_to_paint + color_to_paint[1]
        img[coord[0]- box: coord[0]+ box,
            coord[1]- box: coord[1]+ box, 2] = box_to_paint + color_to_paint[2]

        img[coord[0]- r*box: coord[0]+ r*box,
            coord[1]- r*box: coord[1]+ r*box, :] = cv2.GaussianBlur(img[coord[0]- r*box: coord[0]+ r*box,
                                                                        coord[1]- r*box: coord[1]+ r*box, :],
                                                                                    (5,5),0)
        kernel = np.ones((int(np.max([box/2, 10])), int(np.max([box/2, 10]))), np.uint8)
        img[coord[0]- r*box: coord[0]+ r*box,
            coord[1]- r*box: coord[1]+ r*box, :]  = cv2.dilate(img[coord[0]- r*box: coord[0]+ r*box,
                                                                   coord[1]- r*box: coord[1]+ r*box, :], kernel)




    return img
# --------------------------------------------------


# -----   display keys piano on frame, frame by frame
def dysplay_palette(img, keys):

    for key in keys:

        if key[0] == 'black':
            cv2.rectangle(img, key[3], key[4], dict_color[key[1]], thickness = -1)
            cv2.putText(img, 'canc', (key[2][0]-30, key[2][1]) , cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), thickness=2)

        else:
            cv2.rectangle(img, key[3], key[4], dict_color[key[1]], thickness = -1)

        if key[0] == '+':
            cv2.putText(img, '+', key[2], cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), thickness=3)
        if key[0] == '-':
            cv2.putText(img, '-', key[2], cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), thickness=3)
        if key[0] == '//':
            cv2.putText(img, '/', key[2], cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), thickness=3)

        if key[0] == 'screen':
            cv2.putText(img, ':-)', (key[2][0]-20, key[2][1]) , cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), thickness=3)
            cv2.rectangle(img, key[3], key[4], (0,255,0), thickness = 6)


# --------------------------------------------------



# -----   check keyboard
def identify_key(key_points, coordinate_X, coordinate_Y):
    command = False
    color_change, size_change = False, False
    new_color, new_size_scale = None, None


    for key in range(0, len(key_points)):
        condition_1 = np.mean(np.array([coordinate_Y, coordinate_X]) > np.array(key_points[key][3]))
        condition_2 = np.mean(np.array([coordinate_Y, coordinate_X]) < np.array(key_points[key][4]))
        # print condition_1 + condition_2
        if (int(condition_1 + condition_2) == 2):
            command = key_points[key][0]

            if command in dict_color.keys():
                color_change = True
                new_color =  dict_color[command]

            if command == '+':
                size_change = True
                new_size_scale = '+'
            if command == '-':
                size_change = True
                new_size_scale = '-'
            if command == '//':
                size_change = True
                new_size_scale = '-'


            break

    return command, color_change,size_change, new_color, new_size_scale
# --------------------------------------------------


# -----   get keys palette (img ratios etc)
def get_palette(width_palette , height_palette, offset_palette):
    """
    draw a color palette qwerty 2 x 5
    offset_palette = (int, int) is the spatial offset on x, y of the palette
    """
    column = np.arange(0, width_palette, width_palette/2 , dtype=int) + offset_palette[0]
    row = np.arange(0, height_palette, height_palette/ 6, dtype=int) + offset_palette[1]

    box = (int((width_palette/4.)/2.),   int((height_palette/10.)/2.))

    key_points = []
                      # key    color center               upper-left                      bottom-right
    key_points.append(['red', 'red', (column[0], row[0]), (column[0]-box[0], row[0]-box[1]), (column[0]+box[0], row[0]+box[1])])
    key_points.append(['yellow','yellow', (column[1], row[0]), (column[1]-box[0], row[0]-box[1]), (column[1]+box[0], row[0]+box[1])])

    key_points.append(['green','green', (column[0], row[1]), (column[0]-box[0], row[1]-box[1]), (column[0]+box[0], row[1]+box[1])])
    key_points.append(['blue','blue', (column[1], row[1]), (column[1]-box[0], row[1]-box[1]), (column[1]+box[0], row[1]+box[1])])

    key_points.append(['white','white',(column[0], row[2]), (column[0]-box[0], row[2]-box[1]), (column[0]+box[0], row[2]+box[1])])
    key_points.append([ 'black','black', (column[1], row[2]), (column[1]-box[0], row[2]-box[1]), (column[1]+box[0], row[2]+box[1])])

    key_points.append(['+','white', (column[0], row[3]), (column[0]-box[0], row[3]-box[1]), (column[0]+box[0], row[3]+box[1])])
    key_points.append(['-','white',(column[1], row[3]), (column[1]-box[0], row[3]-box[1]), (column[1]+box[0], row[3]+box[1])])

    key_points.append(['//', 'white', (column[0], row[4]), (column[0]-box[0], row[4]-box[1]), (column[0]+box[0], row[4]+box[1])])
    key_points.append(['screen', 'white',(column[1], row[4]), (column[1]-box[0], row[4]-box[1]), (column[1]+box[0], row[4]+box[1])])

    # key_points.append(['screen_back', 'white', (column[0], row[4]), (column[0]-box[0], row[4]-box[1]), (column[0]+box[0], row[4]+box[1])])
    # key_points.append(['page_back', 'white',(column[1], row[4]), (column[1]-box[0], row[4]-box[1]), (column[1]+box[0], row[4]+box[1])])

    return key_points
# --------------------------------------------------
