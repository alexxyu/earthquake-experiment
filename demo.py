import os
import csv
import time
import random
import numpy as np
import pandas as pd
from psychopy import core, visual, data, event, gui, sound

# PARAMETERS / SETTINGS
'''
Columns in the .csv file containing raw experiment data:
Image:          image filename shown
Response:       user key input to prompt ('y' for yes and 'n' for no)
Actual:         actual/expected answer to prompt
Pres Time:      how long the image was shown
Response Time:  response time (in seconds) defined as time between image display and user response
'''
data_columns = ['Image', 'Response', 'Actual', 'Pres Time', 'Response Time']

# Graphical options
bg_color = "#827F7B"
text_color = "white"
img_dims = [1.0, 1.0]                         # how much image is resized onto window (set to None if full-window)
full_screen = True                            # whether to have display be full-screen
msg_display_time = 3.0                        # how long instructions/messages are displayed on screen

# Experimental options
key_list = ['z', 'n']                         # options for user response (first is the response for yes)
num_each = 200                                # how many of each type of image (damaged and undamaged)
feedback_rounds = 20                          # number of rounds to provide feedback

# File paths
img_dir = r"images/"                          # directory containing images to display
damage_subdir = "Damage"                      # subdirectory name to images of damaged buildings
nodamage_subdir = "NoDamage"                  # subdirectory name to images of undamged buildings
data_dir = r"demo_data"                       # directory to data output path

# UTILITY FUNCTIONS
def get_imgs(img_dir, damage_subdir, num_each, nodamage_subdir):
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
    window = visual.Window(color=bg_color, monitor='monitor', fullscr=full_screen)
    frame_rate = window.getActualFrameRate()

    instruction_msg = visual.TextStim(window, color=text_color, text=f"You will be asked whether the building shown is damaged. Each image will be shown briefly.\n\nPlease press {key_list[0]} for yes and {key_list[1]} for no.\n\nPress any key to continue.")
    instruction_msg.draw()
    window.flip()
    event.waitKeys()

    instruction_msg.text = f"We will start with a demo experiment in which the images will be shown for different amounts of time depending on your accuracy.\n\nYou will hear a beep if you are correct.\n\nPress any key to continue."
    instruction_msg.draw()
    window.flip()
    event.waitKeys()

    img = visual.ImageStim(window, size=img_dims)
    user_data = pd.DataFrame(columns=data_columns)

    conds = data.importConditions('demo_params.csv')
    staircases = []
    for cond in conds:
        staircases.append(data.QuestHandler(startVal=cond['startVal'], startValSd=cond['startValSd'], 
                                        pThreshold=cond['pThreshold'], nTrials=cond['nTrials'],
                                        beta=cond['beta'], delta=cond['delta'], gamma=cond['gamma'], 
                                        minVal=cond['minVal'], maxVal=cond['maxVal']))

    img_list = get_imgs(img_dir, damage_subdir, num_each, nodamage_subdir)
    print(f"{len(img_list)} images loaded.")

    key_list.append('escape')

    # Run through image list with participant
    rounds = 1
    while len(img_list) > 0:

        staircase = random.choice(staircases)
        curr_time = next(staircase)

        curr_time = float(format(curr_time, '.3f'))
        print(f"Will display image for {curr_time} seconds.")

        # Get and parse random image's information
        subdir, img_name = get_random_img(img_list)
        truth = 'y' if subdir == damage_subdir else 'n'
        img.setImage(img_dir + subdir + '/' + img_name)

        # Display the image for set number of frames
        frames_to_show = get_frames_to_show(curr_time, frame_rate)
        keypress = None
        start_time, end_time = time.time(), 0
        for _ in range(frames_to_show):
            img.draw()
            window.flip()

            keypress = event.getKeys(keyList=key_list)
            if 'escape' in keypress:
                instruction_msg.text = 'Experiment aborted. Quitting...'
                instruction_msg.draw()
                window.flip()
                core.wait(3.0)
                core.quit()
            if len(keypress) > 0:
                end_time = time.time()
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
                core.quit()
            end_time = time.time()
        reaction_time = float(format(end_time - start_time, '.3f'))
        
        answer = 'y' if keypress[0] == key_list[0] else 'n'
        event.clearEvents()
        if answer == truth:
            if rounds <= feedback_rounds:
                beep = sound.Sound('A', secs=0.25)
                beep.play()
            staircase.addResponse(1)
        else:
            staircase.addResponse(0)

        user_data.loc[len(user_data)] = ([img_name, answer, truth, curr_time, reaction_time])    
        rounds += 1

        if rounds == feedback_rounds + 1:
            instruction_msg.text = 'From now on, feedback will no longer be provided.'
            instruction_msg.draw()
            window.flip()
            core.wait(3.0)        

    avg = 0
    for staircase in staircases:
        avg += next(staircase)
    avg /= len(staircases)
    with open('demo_result.txt', 'w') as f:
        f.write(f"The experiment's presentation time will be {avg} seconds.\n")

    user_data['Correct'] = (user_data['Actual']==user_data['Response']).astype(int)

    # Output individual participant data to .csv file
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    user_data.to_csv(f"{data_dir}/data_{id}.csv")

    instruction_msg.text = "Test completed. Closing window..."
    instruction_msg.draw()
    window.flip()
    core.wait(3.0)

    core.quit()

if __name__ == "__main__":
    main()
