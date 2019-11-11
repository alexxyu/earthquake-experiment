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
img_dir = r"images/"                          # directory containing images to display
damage_subdir = "Damage"                      # subdirectory name to images of damaged buildings
nodamage_subdir = "NoDamage"                  # subdirectory name to images of undamged buildings

# UTILITY FUNCTIONS
def get_imgs(img_dir, damage_subdir, nodamage_subdir):
    imgs_list = []
    
    damage_imgs = [f"{damage_subdir}/" + f for f in os.listdir(img_dir + damage_subdir)]
    nodamage_imgs = [f"{nodamage_subdir}/" + f for f in os.listdir(img_dir + nodamage_subdir)]

    # Make number of images between two labels equal
    imgs_list.extend(damage_imgs)
    imgs_list.extend(random.sample(nodamage_imgs, len(imgs_list)))

    return imgs_list

def parse_img(img_file):
    slash = img_file.find('/')
    return img_file[:slash], img_file[slash+1:]

def get_random_img(img_list):
    rand_index = np.random.randint(0, len(img_list))
    img = img_list[rand_index]
    img_list.remove(img)
    return parse_img(img)

# EXPERIMENTAL ROUTINE

def draw_quadrants(img, quadrants, vert, horiz):
    quad_w, quad_h = img.size[0]/2, img.size[1]/2
    quadrants[0].vertices = [[0, 0], [0, quad_h], [quad_w, quad_h], [quad_w, 0]]
    quadrants[1].vertices = [[0, 0], [0, quad_h], [-quad_w, quad_h], [-quad_w, 0]]
    quadrants[2].vertices = [[0, 0], [-quad_w, 0], [-quad_w, -quad_h], [0, -quad_h]]
    quadrants[3].vertices = [[0, 0], [0, -quad_h], [quad_w, -quad_h], [quad_w, 0]]

    vert.start, vert.end = [0, -quad_h], [0, quad_h]
    horiz.start, horiz.end = [-quad_w, 0], [quad_w, 0]

    for quadrant in quadrants:
        quadrant.fillColor = None
        quadrant.opacity = 1
        quadrant.draw()

    vert.draw()
    horiz.draw()

def get_response(mouse, quadrants, window, img, vert, horiz):

    def make_other_quadrants_transparent(quadrants, quadrant_to_highlight, window, img):
        img.draw()
        for i in range(len(quadrants)):
            if i != quadrant_to_highlight-1:
                quadrants[i].fillColor = "white"
                quadrants[i].opacity = 0.3
                quadrants[i].draw()
            else:
                quadrants[i].fillColor = None

        vert.draw()
        horiz.draw()
        window.flip()

    quad_pressed = None

    while quad_pressed is None or len(event.getKeys(keyList=['space'])) == 0:

        if mouse.isPressedIn(quadrants[0]):
            prev = quad_pressed
            quad_pressed = 1
            make_other_quadrants_transparent(quadrants, quad_pressed, window, img)
        elif mouse.isPressedIn(quadrants[1]):
            prev = quad_pressed
            quad_pressed = 2
            make_other_quadrants_transparent(quadrants, quad_pressed, window, img)
        elif mouse.isPressedIn(quadrants[2]):
            prev = quad_pressed
            quad_pressed = 3
            make_other_quadrants_transparent(quadrants, quad_pressed, window, img)
        elif mouse.isPressedIn(quadrants[3]):
            prev = quad_pressed
            quad_pressed = 4
            make_other_quadrants_transparent(quadrants, quad_pressed, window, img)

    event.clearEvents()
    return quad_pressed

def main():
    img_list = get_imgs(img_dir, damage_subdir, nodamage_subdir)
    print(f"{len(img_list)} images loaded.")

    # Sets system time as the random seed
    np.random.seed(seed=None)

    # Set up window and how many frames image should be displayed depending on refresh rate of monitor
    window = visual.Window(size=window_dims, color=bg_color, monitor='monitor', fullscr=full_screen)

    img = visual.ImageStim(window, size=img_dims)
    quadrant1 = visual.ShapeStim(window, lineColor=None)
    quadrant2 = visual.ShapeStim(window, lineColor=None)
    quadrant3 = visual.ShapeStim(window, lineColor=None)
    quadrant4 = visual.ShapeStim(window, lineColor=None)

    vert = visual.Line(window, lineColor="red")
    horiz = visual.Line(window, lineColor="red")

    quadrants = [quadrant1, quadrant2, quadrant3, quadrant4]

    instruction_msg = visual.TextStim(window, color=text_color, text=f"You will be asked in which quadrant the building shown is damaged.\n\nChoose the quadrant with the mouse, and press the spacebar to move on.\n\nPress any key to continue.")
    instruction_msg.draw()
    window.flip()
    event.waitKeys()

    # Run through image list with participant
    mouse = event.Mouse()
    while len(img_list) > 0:

        # Get and parse random image's information
        subdir, img_name = get_random_img(img_list)
        img.setImage(img_dir + subdir + '/' + img_name)

        img.draw()
        draw_quadrants(img, quadrants, vert, horiz)
        window.flip()

        response = get_response(mouse, quadrants, window, img, vert, horiz)
        print(f"Quadrant {response} picked.")

    instruction_msg.text = "Test completed. Press any key to close experiment window."
    instruction_msg.draw()
    window.flip()
    event.waitKeys()
    window.close()

if __name__ == "__main__":
    main()
