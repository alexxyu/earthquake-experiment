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
full_screen = True                            # whether to have display be full-screen

# Experimental options
key_list = ['z', 'n']                         # options for user response (first is the response for yes)
time_to_show = 2                              # time for image to be displayed in seconds
#countdown_time = 1.5                          # countdown duration (from 3 to 1) in seconds

# File paths
img_dir = r"images/"                          # directory containing images to display
damage_subdir = "Damage"                      # subdirectory name to images of damaged buildings
nodamage_subdir = "NoDamage"                  # subdirectory name to images of undamged buildings
data_dir = r"data"                            # directory to data output path
csv_filename = "summary.csv"                  # filename of summary data file

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

def main():
    img_list = get_imgs(img_dir, damage_subdir, nodamage_subdir)
    print(f"{len(img_list)} images loaded.")

    # Sets system time as the random seed
    np.random.seed(seed=None)

    # Prompt GUI for participant ID
    dlg = gui.Dlg(title="Enter participant ID:")
    dlg.addField('Participant ID:')
    id = dlg.show()
    if not dlg.OK:
        print('Program aborted.')
        exit()
    id = id[0]

    # Set up window and how many frames image should be displayed depending on refresh rate of monitor
    window = visual.Window(size=window_dims, color=bg_color, monitor='monitor', fullscr=full_screen)
    frame_rate = window.getActualFrameRate()
    frames_to_show = (int) (round(time_to_show * frame_rate))

    instruction_msg = visual.TextStim(window, color=text_color, text=f"You will be asked whether the building shown is damaged.\n\nEach image will be shown briefly.\n\nPlease press {key_list[0]} for yes and {key_list[1]} for no.")
    instruction_msg.draw()
    window.flip()
    event.waitKeys()

    img = visual.ImageStim(window, size=img_dims)
    data = pd.DataFrame(columns=data_columns)

    key_list.append('escape')

    # Run through image list with participant
    while len(img_list) > 0:

        # Get and parse random image's information
        subdir, img_name = get_random_img(img_list)
        truth = 'y' if subdir == damage_subdir else 'n'
        img.setImage(img_dir + subdir + '/' + img_name)

        # Display the image for set number of frames
        start_time = time.time()
        keypress = None
        for _ in range(frames_to_show):
            img.draw()
            window.flip()

            keypress = event.getKeys(keyList=key_list)

            if 'escape' in keypress:
                instruction_msg.text = 'Experiment aborted. Quitting...'
                instruction_msg.draw()
                window.flip()
                core.wait(3.0)
                window.close()
                return 0
            if len(keypress) > 0:
                break

        window.flip()

        # Track reaction time for user response
        if keypress is None or len(keypress) == 0:
            keypress = event.waitKeys(keyList=key_list)
            if 'escape' in keypress:
                instruction_msg.text = 'Experiment aborted. Quitting...'
                instruction_msg.draw()
                window.flip()
                core.wait(3.0)
                window.close()
                return 0
            
        end_time = time.time()

        reaction_time = float(format(end_time - start_time, '.3f'))
        event.clearEvents()

        answer = 'y' if keypress[0] == key_list[0] else 'n'

        data.loc[len(data)] = ([img_name, answer, truth, reaction_time])

    # Output individual participant data to .csv file
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data.to_csv(f"{data_dir}/data_{id}.csv")

    # Create summary file if it doesn't already exist
    if not os.path.exists(csv_filename):
        summary = pd.DataFrame(columns=['ID', 'Accuracy'])
        summary.to_csv(csv_filename)

    # Output summarized participant data to summary file
    accuracy = len(data.query('Response == Actual')) / len(data)

    index = 0
    with open(csv_filename) as file:
        index = sum(1 for line in file)

    with open(csv_filename, 'a') as file:
        file.write(f"{index},{id},{accuracy}")
        file.write("\n")

    instruction_msg.text = "Test completed. Press any key to close experiment window."
    instruction_msg.draw()
    window.flip()
    event.waitKeys()
    window.close()

if __name__ == "__main__":
    main()
