from psychopy import visual, event, core, logging, gui
import os
import numpy as np
import pandas as pd
import time

def get_random_img(img_list):
    rand_index = np.random.randint(0, len(img_list))
    img = img_list[rand_index]
    img_list.remove(img)
    return img

window_dims = [600,600]                                 # dimensions of window display
key_list = ['y', 'n']                                   # options for user response
time_to_show = 0.200                                    # time for image to be displayed in seconds

'''
Columns in the .csv file containing raw experiment data:
Image - image filename shown
Response - user key input to prompt
Actual - actual/expected answer to prompt
Time - response time (in seconds) defined as time between image display and user response
'''
data_columns = ['Image', 'Response', 'Actual', 'Time']

img_dir = r"images/"                                    # directory containing images to display
img_list = [f for f in os.listdir(img_dir)]

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
window = visual.Window(size=window_dims, monitor='monitor')
frame_rate = window.getActualFrameRate()
frames_to_show = (int) (round(time_to_show * frame_rate))

instruction_msg = visual.TextStim(window, text="Each image will be shown briefly after a 3 second countdown.")
instruction_msg.draw()
window.flip()
core.wait(3)

instruction_msg = visual.TextStim(window, text="Is the building damaged?\n\nPlease press 'y' for yes and 'n' for no.")
countdown_msg = visual.TextStim(window, text=None)
img = visual.ImageStim(window)

data = pd.DataFrame(columns=data_columns)

# Run through image list with participant
while len(img_list) > 0:

    # Shows 3 second countdown to image display
    for n in range(3, 0, -1):
        countdown_msg.text = "%i" % n
        countdown_msg.draw()
        window.flip()
        core.wait(1.0)

    img_name = get_random_img(img_list)
    img.setImage(img_dir + img_name)

    start_time = time.time()
    for frame in range(frames_to_show):
        img.draw()
        window.flip()

    instruction_msg.draw()
    window.flip()

    # Track reaction time for user response
    answer = event.waitKeys(keyList=key_list)
    end_time = time.time()
    reaction_time = end_time - start_time

    data.loc[len(data)] = ([img_name, answer[0], '', reaction_time])
    # logging.log(level=logging.DATA, msg="The key pressed for the picture %s was %s." % (img_name, answer[0]))

instruction_msg.text = "Test completed. Closing window..."
instruction_msg.draw()
window.flip()
core.wait(3.0)
window.close()

# Output individual participant data to .csv file
if not os.path.exists('data'):
    os.makedirs('data')
data.to_csv('data/data_%s.csv' % id)

# Output summarized participant data to summary file
accuracy = len(data.query('Response == Actual')) / len(data)

if not os.path.exists('summary.csv'):
    summary = pd.DataFrame(columns=['ID', 'Accuracy'])
    summary.to_csv('summary.csv')

index = 0
with open('summary.csv') as file:
    index = sum(1 for line in file)

with open('summary.csv', 'a') as file:
    file.write("%i,%s,%f" % (index, id, accuracy))
    file.write("\n")
