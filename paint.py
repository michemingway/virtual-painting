import cv2
import numpy as np
from paint_func import *
import time
import mediapipe as mp

# # ------------------------------------ Inputs
camera_ID = 0  # webcam # change to 1 or 2 if you have virtual webcam software installed

thresh_shoot = 3. # seconds to wait before shoot screen

# palette options
width_keyboard, height_keyboard = 200, 600 # [pixels]

# colors pointer etx
box_pointer = 20
r = 2 #factor to expand box and blur / erode
color_pointer = (0, 0, 0)
# # ------------------------------------

# Initialize hands recognition
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# Initialize the camera
camera = init_camera(camera_ID = camera_ID)

# take size screen
size_screen = np.array([camera.get(cv2.CAP_PROP_FRAME_WIDTH), camera.get(cv2.CAP_PROP_FRAME_HEIGHT)]).astype(int)

# define a divisor line from size screen
divisor_screen = int(size_screen[0] / 1.4)

# define size of the drawing page
size_page = (int(size_screen[1]), divisor_screen)

# make a page (3D frame; 2D * 3 channels) to write & project
page_paint = make_white_page(size = size_page)
page_screen = make_black_page(size = size_page)
page_work = make_black_page(size = size_page)

# Initialize palette
offset_palette = (int(divisor_screen*1.15), 50) # pixel offset (x, y) of keyboard coordinates
key_points = get_palette(width_palette  = width_keyboard ,
                         height_palette = height_keyboard ,
                         offset_palette = offset_palette )

# ----------------- triggers
chek_time = False
color_brush = (0,0,255)
size_brush = 8
# --------------------------

while(True):

    ret, frame = camera.read()   # Capture frame
    frame = adjust_frame(frame)  # rotate / flip

    # init page (2D array in color space to work with)
    frame_to_work = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    put_objects_in_frame(frame, objects = [divisor_screen])
    put_objects_in_page(page_paint)

    # Display keyboards and get keys
    dysplay_palette(img = frame, keys = key_points)

    results = hands.process(frame_to_work)

    if results.multi_hand_landmarks:

        for handLms in results.multi_hand_landmarks:

            if (handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y >
                handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_PIP].y):

                # compute points to draw
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x *w), int(lm.y*h)
                    cv2.circle(frame, (cx,cy), 10, (255,0,0), cv2.FILLED)

                mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

            else:

                # compute points to draw
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x *w), int(lm.y*h)
                    cv2.circle(frame, (cx,cy), 10, (0,255,0), cv2.FILLED)

                mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

                pointer_Y, pointer_X = [int(handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x * size_screen[0]),
                                        int(handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y * size_screen[1])]

                coordinates = [pointer_X, pointer_Y]

                if (((np.array(coordinates) + size_brush*r) < size_page).sum() +
                    ((np.array(coordinates) - size_brush*r) > (0, 0)).sum()) == 4:


                        page_work  = colorize_img(img = page_work, coord = coordinates,
                                             color_to_paint = color_brush, box = size_brush)
                        page_paint  = colorize_img(img = page_paint, coord = coordinates,
                                             color_to_paint = color_brush, box = size_brush)

                else:

                        cv2.circle(frame, (pointer_Y, pointer_X), int(box_pointer), color_pointer, -1)

                        command, color_change, size_change, new_brush_color, new_size_scale = identify_key(key_points = key_points, coordinate_X = pointer_X, coordinate_Y = pointer_Y)

                        if color_change:
                            color_brush = new_brush_color

                        if size_change:
                            if new_size_scale == '+':
                                size_brush = 20
                            if new_size_scale == '-':
                                size_brush = 4
                            if new_size_scale == '//':
                                size_brush = 8

                        if command == 'screen':
                            start = time.time()
                            chek_time = True

    scale_alpha = (1, 1) # check here what it is
    frame[:,:divisor_screen, :] = cv2.addWeighted(frame[:,:divisor_screen, :],scale_alpha[0],
                                                page_work, scale_alpha[1],
                                                - np.mean(page_work))
    if chek_time:
        now = time.time()
        seconds = now - start

        if seconds > thresh_shoot:
            chek_time = False
            page_screen = frame[:,:divisor_screen, :]
            page_work= cv2.addWeighted(page_screen, 0.8, page_work, 0.5, 0)
            # page_screen = np.mean([page_work, page_screen],axis=2).astype('int')

    # visualize windows
    show_window('frame', frame)
    show_window('page', cv2.resize(page_work, (int(size_page[1]/2.),int(size_page[0]/2.))))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
