#!/usr/bin/env python
# -*- coding: latin-1 -*-
import atexit
import codecs
import csv
import os
import random
from os.path import join
from statistics import mean
import yaml
from psychopy import visual, event, logging, gui, core

from misc.screen_misc import get_screen_res, get_frame_rate
from itertools import combinations_with_replacement, product

"""
    @TODO:
    1. Refactor third instruction - first phrase is wrong
    2. Fixation cross?
    3. How to measure frame rate
    4. Is wait for key should be in for loop? 
    5. Change amount of repeats
"""

def get_participant_id():
    participant_info = dict()
    participant_info['Participant ID'] = ''
    dlg = gui.DlgFromDict(participant_info)
    if not dlg.OK:
        core.quit()
    return participant_info['Participant ID']


@atexit.register
def save_beh_results():
    """
    Save results of experiment. Decorated with @atexit in order to make sure, that intermediate
    results will be saved even if interpreter will broke.
    """
    with open(join('results', PART_ID + '_' + str(random.choice(range(100, 1000))) + '_beh.csv'), 'w',
              encoding='utf-8') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()


def show_image(win, file_name, key='f7'):
    """
    Show instructions in a form of an image.
    """
    image = visual.ImageStim(win=win, image=file_name,
                             interpolate=True)
    image.pos = (0, 0)
    image.autoDraw = False
    image.draw()
    win.flip()
    clicked = event.waitKeys(keyList=[key, 'space'])
    if clicked == [key]:
        logging.critical(
            'Experiment finished by user! {} pressed.'.format(key[0]))
        exit(0)


def read_text_from_file(file_name, insert=''):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert:
    :return: message
    """
    if not isinstance(file_name, str):
        logging.error('Problem with file reading, filename must be a string')
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):  # if not commented line
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def check_exit(key='f7'):
    """
    Check (during procedure) if experimentator doesn't want to terminate.
    """
    stop = event.getKeys(keyList=[key])
    if stop:
        abort_with_error(
            'Experiment finished by user! {} pressed.'.format(key))


def show_info(win, file_name, insert=''):
    """
    Clear way to show info message into screen.
    :param win:
    :return:
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color='black', text=msg,
                          height=20, wrapWidth=SCREEN_RES['width'])
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space', 'left', 'right'])
    if key == ['f7']:
        abort_with_error(
            'Experiment finished by user on info screen! F7 pressed.')
    win.flip()


def abort_with_error(err):
    """
    Call if an error occured.
    """
    logging.critical(err)
    raise Exception(err)


# GLOBALS

RESULTS = list()  # list in which data will be colected
RESULTS.append(['PART_ID', 'Trial_no', 'RT', 'Correctness', 'Trial'])  # ... Results header


def main():
    global PART_ID  # PART_ID is used in case of error on @atexit, that's why it must be global

    # === Dialog popup ===
    info = {'IDENTYFIKATOR': '', u'P\u0141EC': ['M', "K"], 'WIEK': '20'}
    dict_dlg = gui.DlgFromDict(
        dictionary=info, title='Multilanguage Stroop')
    if not dict_dlg.OK:
        abort_with_error('Info dialog terminated.')

    clock = core.Clock()
    # load config, all params are there
    conf = yaml.load(open('config.yaml', encoding='utf-8'))

    # === Scene init ===
    win = visual.Window(list(SCREEN_RES.values()), fullscr=False,
                        monitor='testMonitor', units='pix', screen=0, color=conf['BACKGROUND_COLOR'])
    event.Mouse(visible=False, newPos=None, win=win)  # Make mouse invisible

    # have to figure out how to measure framerate because now it is not working
    # frame_rate = get_frame_rate(win)
    # print(frame_rate)
    # # check if a detected frame rate is consistent with a frame rate for witch experiment was designed
    # # important only if miliseconds precision design is used
    # if FRAME_RATE != conf['FRAME_RATE']:
    #     dlg=gui.Dlg(title="Critical error")
    #     dlg.addText(
    #         'Wrong no of frames detected: {}. Experiment terminated.'.format(FRAME_RATE))
    #     dlg.show()
    #     return None

    PART_ID = info['IDENTYFIKATOR'] + info[u'P\u0141EC'] + info['WIEK']
    logging.LogFile(join('results', PART_ID + '.log'),
                    level=logging.INFO)  # errors logging
    # logging.info('FRAME RATE: {}'.format(FRAME_RATE))
    logging.info('SCREEN RES: {}'.format(SCREEN_RES.values()))

    show_info(win, join('.', 'messages', 'hello.txt'))

    show_image(win, 'images/InstrukcjaTrening.png')

    # Run trainee session
    win.flip()
    #run_trainee(win, conf, lang=0)

    # time for break
    show_image(win, 'images/break.jpg')

    # Run experiment session
    win.flip()
    run_experiment(win, conf, random.randint(0, 1))

    save_beh_results()
    logging.flush()
    show_info(win, join('.', 'messages', 'end.txt'))
    win.close()


def draw_hints(win, conf, lang):
    if lang == 0:
        red_pl = visual.TextStim(win, text='d = czerwony', color="#" + conf["RED"], pos=(-300, 200))
        green_pl = visual.TextStim(win, text='f = zielony', color="#" + conf["GREEN"], pos=(-100, 200))
        blue_pl = visual.TextStim(win, text='j = niebieski', color="#" + conf["BLUE"], pos=(100, 200))
        pink_pl = visual.TextStim(win, text="k = ró\u017Cowy", color="#" + conf["PINK"], pos=(300, 200))
        red_pl.draw()
        green_pl.draw()
        blue_pl.draw()
        pink_pl.draw()
    elif lang == 1:
        red_rus = visual.TextStim(win, text='d = \u043A\u0440\u0430\u0441\u043D\u044B\u0439',
                                  color="#" + conf["RED"], pos=(-300, 200))
        green_rus = visual.TextStim(win, text='f = \u0437\u0435\u043B\u0455\u043D\u044B\u0439',
                                    color="#" + conf["GREEN"], pos=(-100, 200))
        # seventh char crashing program (\u0301) so i deleted it
        blue_rus = visual.TextStim(win, text='j = \u0433\u043e\u043b\u0443\u0431\u043e\u0439',
                                   color="#" + conf["BLUE"], pos=(100, 200))
        # as above, \u0301 should be third in row
        pink_rus = visual.TextStim(win, text='k = \u0440\u043e\u0437\u043e\u0432\u044b\u0439',
                                   color="#" + conf["PINK"], pos=(300, 200))
        red_rus.draw()
        green_rus.draw()
        blue_rus.draw()
        pink_rus.draw()


def run_trainee(win, conf, lang):
    clock = core.Clock()
    colors = conf['COLORS_ARRAY_HEX']
    # Start loop for certain amount of trials
    for i in range(conf['TRAINEE_SESSIONS_TRIALS_INT']):
        win.flip()
        # display hints in polish
        draw_hints(win, conf, lang)
        win.callOnFlip(clock.reset)
        # get random word from adjectives array
        text = random.choice(conf['ADJECTIVES'])
        color = random.choice(colors)
        # draw word in the screen
        adjective = visual.TextStim(win, text=text, color="#" + color)
        adjective.autoDraw = False
        adjective.draw()
        win.flip()
        # wait for the button press
        key = event.waitKeys(keyList=list(
            conf['REACTION_KEYS']), timeStamped=clock, maxWait=conf['WAIT_FOR_KEY_S'])
        # check if the button was pressed
        if (key is not None) and str(conf["MAPPING"][key[0][0]]) == str("#" + color):
            win.flip()
            correct = visual.TextStim(win, text="\u2713", color='green')
            for frames in range(int(conf['FRAME_RATE'] * conf['SHOW_RESULTS_S'])):
                correct.draw()
            correctness = 1
            win.flip()
        else:
            win.flip()
            error = visual.TextStim(win, text='\u26A0', color='red')
            error.autoDraw = False
            error.draw()
            print(conf['FRAME_RATE'] * conf['SHOW_RESULTS_S'])
            for frames in range(int(conf['FRAME_RATE'] * conf['SHOW_RESULTS_S'])):
                error.draw()
            correctness = 0
            win.flip()
        # add results to the file
        RESULTS.append([PART_ID, 'trainee', round(key[0][1],
                                                  conf['DIGIT_AFTER_COMA_RESULTS_INT']) if key else 0,
                        correctness, i + 1])
        # wait certain amount of time to go back to next trial
        for frames in range(int(conf['FRAME_RATE'] * conf['WAIT_TO_NEXT_TRIALS_S'])):
            win.flip()


def run_experiment(win, conf, first):
    win.flip()
    if first == 0:
        db = create_color_db(conf, first)
        show_image(win, 'images/Instrukcja1.png')
        engine(win, conf, db, first)
        show_image(win, 'images/break.jpg')
        db = create_color_db(conf, first + 1)
        engine(win, conf, db, first + 1)
    else:
        db = create_color_db(conf, first)
        show_image(win, 'images/Instrukcja2.png')
        engine(win, conf, db, first)
        show_image(win, 'images/break.jpg')
        db = create_color_db(conf, first - 1)
        engine(win, conf, db, first - 1)


def create_color_db(conf, first):
    """
    This function get colors from config and the HEX signs and makes array for colors
    REPEATS_OF_COLOR_IN_TRIALS_INT set how many times one color can repeat
    Second 'for' add control conditional for test
    At the end db get randomized
    """
    db = []
    for k in range(conf['REPEATS_OF_COLOR_IN_TRIALS_INT']):
       # for l in range(len(conf['COLORS_ARRAY_HEX'])):
            #db.append([conf['COLORS_ARRAY_HEX'][l], conf['COLORS_PL_ARRAY'][l]])
        if first == 0:
            for i in range(len(conf['COLORS_PL_ARRAY'])):
                for j in range(len(conf['COLORS_ARRAY_HEX'])):
                    db.append([conf['COLORS_ARRAY_HEX'][i], conf['COLORS_PL_ARRAY'][j]])
        else:
            for i in range(len(conf['COLORS_RUS_ARRAY'])):
                for j in range(len(conf['COLORS_ARRAY_HEX'])):
                    db.append([conf['COLORS_ARRAY_HEX'][i], conf['COLORS_RUS_ARRAY'][j]])

    for i in range(conf['HOW_MANY_CONTROLS_INT']):
        text = random.choice(conf['ADJECTIVES'])
        color = random.choice(conf['COLORS_ARRAY_HEX'])
        db.append([color, text])
    randomized = random.sample(db, len(db))
    return randomized


def engine(win, conf, db, first):
    clock = core.Clock()
    for i in range(len(db)):
        win.flip()
        win.callOnFlip(clock.reset)
        draw_hints(win, conf, first)
        word = visual.TextStim(win, text=db[i][1], color="#" + db[i][0])
        word.autoDraw = False
        word.draw()
        win.flip()
        key = event.waitKeys(keyList=list(
            conf['REACTION_KEYS']), timeStamped=clock, maxWait=conf['WAIT_FOR_KEY_S'])
        if (key is not None) and str(conf["MAPPING"][key[0][0]]) == str("#" + db[i][0]):
            win.flip()
            correct = visual.TextStim(win, text="\u2713", color='green')
            for frames in range(int(conf['FRAME_RATE'] * conf['SHOW_RESULTS_S'])):
                correct.draw()
            correctness = 1
            win.flip()
        else:
            win.flip()
            error = visual.TextStim(win, text='\u26A0', color='red')
            error.autoDraw = False
            for frames in range(int(conf['FRAME_RATE'] * conf['SHOW_RESULTS_S'])):
                error.draw()
            correctness = 0
            win.flip()
        RESULTS.append([PART_ID, 'PL' if first == 0 else 'RUS',
                        round(key[0][1], conf['DIGIT_AFTER_COMA_RESULTS_INT']) if key else 0,
                        correctness, i + 1])
        # wait certain amount of time to go back to next trial
        for frames in range(int(conf['FRAME_RATE'] * conf['WAIT_TO_NEXT_TRIALS_S'])):
            win.flip()


if __name__ == '__main__':
    PART_ID = ''
    SCREEN_RES = get_screen_res()
    main()