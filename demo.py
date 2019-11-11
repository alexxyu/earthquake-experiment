import os
import time
import random
import numpy as np
import pandas as pd
from psychopy import visual, event, core, logging, gui, data

# PARAMETERS / SETTINGS
'''
Columns in the .csv file containing raw experiment data:
Image - image filename shown
Response - user key input to prompt ('y' for yes and 'n' for no)
Actual - actual/expected answer to prompt
Time - response time (in seconds) defined as time between image display and user response
'''
data_columns = ['Image', 'Response', 'Actual', 'Time']

# Graphical options
window_dims = [600,600]                       # dimensions of window display (if not full-screen)
bg_color = "#827F7B"
text_color = "white"
img_dims = None                               # how much image is resized onto window (set to None if full-window)
full_screen = False                           # whether to have display be full-screen
msg_display_time = 0.5                        # how long instructions/messages are displayed on screen

# Experimental options
key_list = ['z', 'n']                         # options for user response (first is the response for yes)
num_each = 12                                 # number of damaged buildings and undamaged buildings to show

'''
Staircase Procedure Handler
The values described here determine how much each answer affects the next presentation time.

startVal:       the time to begin at
stepType:       how each step is added/subtracted ('lin' for linear, 'db' for decibel, 'log' for log)
stepSizes:      the step size after each reversal
nUp:            number of incorrect guesses before staircase level increases
nDown:          number of correct guesses before staircase level decreases
minVal:         lowest presentation time that can be reached
'''
staircase = data.StairHandler(startVal = 3.0,
                        stepType = 'db', stepSizes = [4, 2, 1],
                        nUp = 2, nDown = 2, minVal = 0.200, 
                        nTrials = num_each * 2)

# File paths
img_dir = r"images/"                          # directory containing images to display
damage_subdir = "Damage"                      # subdirectory name to images of damaged buildings
nodamage_subdir = "NoDamage"                  # subdirectory name to images of undamged buildings

# UTILITY FUNCTIONS
def get_imgs(img_dir, num_each, damage_subdir, nodamage_subdir):
    imgs_list = []

    all_damage_imgs = [f"{damage_subdir}/" + f for f in os.listdir(img_dir + damage_subdir)]
    all_nodamage_imgs = [f"{nodamage_subdir}/" + f for f in os.listdir(img_dir + nodamage_subdir)]

    # Make number of images between two labels equal
    imgs_list.extend(random.sample(all_damage_imgs, num_each))
    imgs_list.extend(random.sample(all_nodamage_imgs, num_each))

    return imgs_list

def parse_img(img_file):
    slash = img_file.find('/')
    return img_file[:slash], img_file[slash+1:]

def get_random_img(img_list):
    rand_index = np.random.randint(0, len(img_list))
    img = img_list[rand_index]
    img_list.remove(img)
    return parse_img(img)

def get_frames_to_show(time_to_show, frame_rate):
    return (int) (round(time_to_show * frame_rate))

# MAIN ROUTINE
def main():
    img_list = get_imgs(img_dir, num_each, damage_subdir, nodamage_subdir)
    print(f"{len(img_list)} images loaded.")

    # Sets system time as the random seed
    np.random.seed(seed=None)

    # Set up window and how many frames image should be displayed depending on refresh rate of monitor
    window = visual.Window(size=window_dims, color=bg_color, monitor='monitor', fullscr=full_screen)
    frame_rate = window.getActualFrameRate()

    instruction_msg = visual.TextStim(window, color=text_color, text=f"You will be asked whether the building shown is damaged.\n\nEach image will be shown briefly.\n\nPlease press {key_list[0]} for yes and {key_list[1]} for no.")
    instruction_msg.draw()
    window.flip()
    core.wait(msg_display_time)

    img = visual.ImageStim(window, size=img_dims)

    # Run through image list with participant
    last_time = 0
    log = open('time_log.txt', 'a')
    log.write('======================================================================\n')
    log.write('TEST\n')
    log.write('======================================================================\n')
    for curr_time in staircase:

        if len(img_list) == 0:
            break
        print(f"Will display image for {curr_time} seconds.")
        log.write(f"Will display image for {curr_time} seconds.\n")

        # Get and parse random image's information
        subdir, img_name = get_random_img(img_list)
        truth = 'y' if subdir == damage_subdir else 'n'
        img.setImage(img_dir + subdir + '/' + img_name)

        # Display the image for set number of frames
        frames_to_show = get_frames_to_show(curr_time, frame_rate)
        keypress = None
        for _ in range(frames_to_show):
            img.draw()
            window.flip()

            keypress = event.getKeys(keyList=key_list)
            if len(keypress) > 0:
                break

        window.flip()

        # Track reaction time for user response
        if keypress is None or len(keypress) == 0:
            keypress = event.waitKeys(keyList=key_list)
        
        answer = 'y' if keypress[0] == key_list[0] else 'n'
        event.clearEvents()
        if answer == truth:
            staircase.addResponse(1)
        else:
            staircase.addResponse(0)

        last_time = curr_time

    print(f"The experiment's presentation time will be {last_time} seconds.")
    log.write(f"The experiment's presentation time will be {last_time} seconds.\n\n")
    log.close()

    instruction_msg.text = "Test completed. Closing window..."
    instruction_msg.draw()
    window.flip()
    core.wait(3.0)
    window.close()

if __name__ == "__main__":
    main()
