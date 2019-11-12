import os
import time
import random
import numpy as np
import pandas as pd
from psychopy import visual, event, core, logging, gui

# PARAMETERS / SETTINGS
data_columns = ['Image', 'Response', 'Time']

# Graphical options
window_dims = [600,600]                       # dimensions of window display (if not full-screen)
bg_color = "#827F7B"
text_color = "white"
img_dims = [1.0, 1.0]                         # how much image is resized onto window (set to None if full-window)
full_screen = True                            # whether to have display be full-screen

# File paths
img_dir = r"images/Damage/"                   # directory containing images to display
output_filename = "truth.csv"

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
        quadrant.lineWidth = 1.0
        quadrant.draw()

    window.flip()

def get_response(mouse, quadrants, window, img):

    def select_quadrant(quadrants, quadrants_selected, window, img):
        img.draw()

        for q in quadrants:
            q.lineColor = "red"
            q.lineWidth = 1.0
            q.draw()
        for qn in quadrants_selected:
            quadrants[qn-1].lineColor = "blue"
            quadrants[qn-1].lineWidth = 4.0
            quadrants[qn-1].draw()

        window.flip()

    quads_pressed = []

    while len(quads_pressed) == 0 or len(event.getKeys(keyList=['space'])) == 0:

        if len(event.getKeys(keyList=['escape'])) > 0:
            return None

        if mouse.isPressedIn(quadrants[0]):
            event.clearEvents()
            if 1 in quads_pressed:
                quads_pressed.remove(1)
            else:
                quads_pressed.append(1)
            select_quadrant(quadrants, quads_pressed, window, img)
        elif mouse.isPressedIn(quadrants[1]):
            event.clearEvents()
            if 2 in quads_pressed:
                quads_pressed.remove(2)
            else:
                quads_pressed.append(2)
            select_quadrant(quadrants, quads_pressed, window, img)
        elif mouse.isPressedIn(quadrants[2]):
            event.clearEvents()
            if 3 in quads_pressed:
                quads_pressed.remove(3)
            else:
                quads_pressed.append(3)
            select_quadrant(quadrants, quads_pressed, window, img)
        elif mouse.isPressedIn(quadrants[3]):
            event.clearEvents()
            if 4 in quads_pressed:
                quads_pressed.remove(4)
            else:
                quads_pressed.append(4)
            select_quadrant(quadrants, quads_pressed, window, img)

        core.wait(0.001)

    event.clearEvents()
    quads_pressed.sort()
    return quads_pressed

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

    data = pd.DataFrame(columns=data_columns)

    # Run through image list with participant
    mouse = event.Mouse()
    while len(img_list) > 0:

        # Get and parse random image's information
        img_name = get_random_img(img_list)
        img.setImage(img_dir + img_name)

        draw_quadrants(window, img, quadrants)
        start_time = time.time()
        response = get_response(mouse, quadrants, window, img)
        if response is None:
            break
        end_time = time.time()
        response_time = end_time - start_time

        data.loc[len(data)] = ([img_name, response, format(response_time, '.3f')])
        data.to_csv(output_filename)

    instruction_msg.text = "Test is over. Press any key to close experiment window."
    instruction_msg.draw()
    window.flip()
    event.waitKeys()
    window.close()

if __name__ == "__main__":
    main()
