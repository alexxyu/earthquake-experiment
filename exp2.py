import os
import time
import random
import numpy as np
import pandas as pd
from psychopy import visual, event, core, logging, gui

# PARAMETERS / SETTINGS
'''
Columns in the .csv file containing raw experiment data:
Image:          image filename shown
Response:       user key input to prompt ('y' for yes and 'n' for no)
Actual:         actual/expected answer to prompt
Time:           response time (in seconds) defined as time between image display and user response
'''
data_columns = ['Image', 'Response', 'Actual', 'Time']

# Graphical options
window_dims = [600,600]                       # dimensions of window display (if not full-screen)
bg_color = "#827F7B"
text_color = "white"
img_dims = [1.0, 1.0]                         # how much image is resized onto window (set to None if full-window)
full_screen = False                            # whether to have display be full-screen

# File paths
img_dir = r"images/Damage/"                   # directory containing images to display

# UTILITY FUNCTIONS
def get_imgs(img_dir):
    imgs_list = []
    imgs_list.extend([f for f in os.listdir(img_dir)])

    return imgs_list

def get_random_img(img_list):
    rand_index = np.random.randint(0, len(img_list))
    img = img_list[rand_index]
    img_list.remove(img)
    return img

# EXPERIMENTAL ROUTINE

def draw_quadrants(window, img, quadrants):
    img.draw()

    quad_w, quad_h = img.size[0]/2, img.size[1]/2
    quadrants[0].vertices = [[0, 0], [0, quad_h], [quad_w, quad_h], [quad_w, 0]]
    quadrants[1].vertices = [[0, 0], [0, quad_h], [-quad_w, quad_h], [-quad_w, 0]]
    quadrants[2].vertices = [[0, 0], [-quad_w, 0], [-quad_w, -quad_h], [0, -quad_h]]
    quadrants[3].vertices = [[0, 0], [0, -quad_h], [quad_w, -quad_h], [quad_w, 0]]

    for quadrant in quadrants:
        quadrant.lineColor = "red"
        quadrant.draw()

    window.flip()

def get_response(mouse, quadrants, window, img):

    def select_quadrant(quadrants, quadrant_to_highlight, window, img):
        img.draw()
        for quadrant in quadrants:
            if quadrant != quadrant_to_highlight:
                quadrant.lineColor = "red"
                quadrant.draw()

        quadrant_to_highlight.lineColor = "white"
        quadrant_to_highlight.draw()
        window.flip()

    quad_pressed = None

    while quad_pressed is None or len(event.getKeys(keyList=['space'])) == 0:

        if len(event.getKeys(keyList=['escape'])) > 0:
            return None

        if mouse.isPressedIn(quadrants[0]):
            event.clearEvents()
            if quad_pressed == 1:
                draw_quadrants(window, img, quadrants)
                quad_pressed = None
            else:
                quad_pressed = 1
                select_quadrant(quadrants, quadrants[0], window, img)
        elif mouse.isPressedIn(quadrants[1]):
            event.clearEvents()
            if quad_pressed == 2:
                draw_quadrants(window, img, quadrants)
                quad_pressed = None
            else:
                quad_pressed = 2
                select_quadrant(quadrants, quadrants[1], window, img)
        elif mouse.isPressedIn(quadrants[2]):
            event.clearEvents()
            if quad_pressed == 3:
                draw_quadrants(window, img, quadrants)
                quad_pressed = None
            else:
                quad_pressed = 3
                select_quadrant(quadrants, quadrants[2], window, img)
        elif mouse.isPressedIn(quadrants[3]):
            event.clearEvents()
            if quad_pressed == 4:
                draw_quadrants(window, img, quadrants)
                quad_pressed = None
            else:
                quad_pressed = 4
                select_quadrant(quadrants, quadrants[3], window, img)

    event.clearEvents()
    return quad_pressed

def main():
    img_list = get_imgs(img_dir)
    print(f"{len(img_list)} images loaded.")

    # Sets system time as the random seed
    np.random.seed(seed=None)

    # Set up window and how many frames image should be displayed depending on refresh rate of monitor
    window = visual.Window(size=window_dims, color=bg_color, monitor='monitor', fullscr=full_screen)

    img = visual.ImageStim(window, size=img_dims)
    quadrant1 = visual.ShapeStim(window, lineColor="red")
    quadrant2 = visual.ShapeStim(window, lineColor="red")
    quadrant3 = visual.ShapeStim(window, lineColor="red")
    quadrant4 = visual.ShapeStim(window, lineColor="red")

    quadrants = [quadrant1, quadrant2, quadrant3, quadrant4]

    instruction_msg = visual.TextStim(window, color=text_color, text=f"You will be asked in which quadrant the building shown is damaged.\n\nChoose the quadrant with the mouse, and press the spacebar to move on.\n\nPress any key to continue.")
    instruction_msg.draw()
    window.flip()
    event.waitKeys()

    # Run through image list with participant
    mouse = event.Mouse()
    while len(img_list) > 0:

        # Get and parse random image's information
        img_name = get_random_img(img_list)
        img.setImage(img_dir + img_name)

        draw_quadrants(window, img, quadrants)
        response = get_response(mouse, quadrants, window, img)
        if response is None:
            break
        print(f"Quadrant {response} picked.")

    instruction_msg.text = "Test is over. Press any key to close experiment window."
    instruction_msg.draw()
    window.flip()
    event.waitKeys()
    window.close()

if __name__ == "__main__":
    main()
