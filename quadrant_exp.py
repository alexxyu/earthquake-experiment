import os
import time
import random
import numpy as np
import pandas as pd
from psychopy import visual, event, core, logging, gui

# PARAMETERS / SETTINGS
data_columns = ['Image', 'Response', 'Time', 'Q1 Label', 'Q2 Label', 'Q3 Label', 'Q4 Label']

# Graphical options
window_dims = [600,600]                       # dimensions of window display (if not full-screen)
bg_color = "#827F7B"
text_color = "white"
img_dims = [1.0, 1.0]                         # how much image is resized onto window (set to None if full-window)
full_screen = True                            # whether to have display be full-screen

# File paths
img_dir = r"images/Damage/"                   # directory containing images to display
truth_filepath = "DamagedQuadrants.csv"
output_dir = r"QuadrantData/"

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

    def redraw_quadrants(quadrants, quadrants_selected, window, img):
        img.draw()

        # Draws thick blue border around the selected quadrants
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
        for qn in range(len(quadrants)):
            # Update GUI and quadrants pressed if mouse clicked in one of them
            if mouse.isPressedIn(quadrants[qn]):
                event.clearEvents()
                if qn+1 in quads_pressed:
                    # Deselect quadrant
                    quads_pressed.remove(qn+1)
                else:
                    # Select quadrant
                    quads_pressed.append(qn+1)
                redraw_quadrants(quadrants, quads_pressed, window, img)
                break

        core.wait(0.001)

    event.clearEvents()
    quads_pressed.sort()
    return quads_pressed

def get_label(user_response, truth, quadrant):
    if quadrant in user_response and str(quadrant) in truth:
        # Subject responds "Damage" + Ground truth "Damage" => "Hit"
        return "Hit"
    elif quadrant not in user_response and str(quadrant) in truth:
        # Subject responds "No damage" + Ground truth "Damage" => "Miss"
        return "Miss"
    elif quadrant in user_response and str(quadrant) not in truth:
        # Subject responds "Damage" + Ground truth "No damage" => "False alarm"
        return "False alarm"
    else:
        # Subject responds "No damage" + Ground truth "No damage" => "Correct rejection"
        return "Correct rejection"

def main():

    # Prompt GUI for participant ID
    dlg = gui.Dlg(title="Enter participant ID:")
    dlg.addField('Participant ID:')
    id = dlg.show()
    if not dlg.OK:
        print('Program aborted.')
        exit()
    id = id[0]
    output_filename = output_dir + f"data_{id}.csv"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img_list = get_imgs(img_dir)
    print(f"{len(img_list)} images loaded.")

    # Set system time as the random seed
    np.random.seed(seed=None)

    # Set up graphical components of experimental frame
    window = visual.Window(size=window_dims, color=bg_color, monitor='monitor', fullscr=full_screen)

    img = visual.ImageStim(window, size=img_dims)
    quadrant1 = visual.ShapeStim(window, lineColor="red")
    quadrant2 = visual.ShapeStim(window, lineColor="red")
    quadrant3 = visual.ShapeStim(window, lineColor="red")
    quadrant4 = visual.ShapeStim(window, lineColor="red")

    quadrants = [quadrant1, quadrant2, quadrant3, quadrant4]

    # Display instructional imformation for user
    instruction_msg = visual.TextStim(window, color=text_color, text=f"You will be asked in which quadrant the building shown is damaged.\n\nChoose the quadrant with the mouse, and press the spacebar to move on.\n\nPress any key to continue.")
    instruction_msg.draw()
    window.flip()
    event.waitKeys()

    data = pd.DataFrame(columns=data_columns)
    ground_truth = pd.read_csv(truth_filepath, index_col=1).dropna(how='any')

    # Run through image list with participant
    mouse = event.Mouse()
    while len(img_list) > 0:

        # Get and parse random image's information
        img_name = get_random_img(img_list)
        img_truth = ground_truth.at[img_name, "Response"]
        img.setImage(img_dir + img_name)

        # Draw image and quadrants, wait for user response
        draw_quadrants(window, img, quadrants)
        start_time = time.time()
        response = get_response(mouse, quadrants, window, img)
        if response is None:
            break               # Quit experiment early if escape key pressed

        # Measure the user's reaction time
        end_time = time.time()
        response_time = end_time - start_time

        data.loc[len(data)] = ([img_name, response, format(response_time, '.3f'), get_label(response, img_truth, 1), get_label(response, img_truth, 2), get_label(response, img_truth, 3), get_label(response, img_truth, 4)])
        data.to_csv(output_filename)

    instruction_msg.text = "Test is over. Press any key to close experiment window."
    instruction_msg.draw()
    window.flip()
    event.waitKeys()
    window.close()

if __name__ == "__main__":
    main()
