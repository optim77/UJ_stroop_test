#!/usr/bin/env python
# -*- coding: latin-1 -*-
import atexit
import codecs
import csv
import os
import random
import time
from os.path import join
from statistics import mean
import yaml
from datetime import datetime
from psychopy import visual, event, logging, gui, core

from misc.screen_misc import get_screen_res, get_frame_rate
from itertools import combinations_with_replacement, product

"""AGATKA"""
def get_participant_id():
    participant_info = dict()
    participant_info['Participant ID'] = ''
    dlg = gui.DlgFromDict(participant_info)
    if not dlg.OK:
        core.quit()
    return participant_info['Participant ID']


def get_now_data():
    now = datetime.now()
    return str(now.strftime("___%m-%d-%Y___%H-%M-%S"))


@atexit.register
def save_beh_results():
    """
    Save results of experiment. Decorated with @atexit in order to make sure, that intermediate
    results will be saved even if interpreter will broke.
    """
    with open(join('results', PART_ID + get_now_data() + '.csv'), 'w',
              encoding='utf-8') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()


def show_image(win, file_name, key='f7'):
    """
    AGATKA:Show instructions in a form of an image.
    """
    image = visual.ImageStim(win=win, image=file_name,
                             interpolate=True)
    image.pos = (0, 0)
    image.autoDraw = False
    image.draw()
    win.flip()
    clicked = event.waitKeys(keyList=[key, 'space'])
    win.flip()
    if clicked == [key]:
        logging.critical(
            'Experiment finished by user! {} pressed.'.format(key[0]))
        exit(0)


def read_text_from_file(file_name, insert=''):
    """
    KOSZ
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
    KOSZ
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


def check_framerate(win, conf):
    frame_rate = get_frame_rate(win)
    if frame_rate != conf['FRAME_RATE']:
        logging.info('FRAME RATE: {}'.format(frame_rate))
        dlg = gui.Dlg(title="Critical error")
        dlg.addText(
            'Wrong no of frames detected: {}. Experiment terminated.'.format(frame_rate))
        dlg.show()
        return None

"""AGATKA"""
RESULTS = list()  # list in which data will be collected
# Results header
RESULTS.append(['PART_ID', 'Trial', 'RT', 'Correctness', 'Trial_no', 'Stimuli', 'Congruency', 'Key'])


def main():
    global PART_ID  # PART_ID is used in case of error on @atexit, that's why it must be global

    # === Dialog popup ===
    info = {'IDENTYFIKATOR': ''}

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

    # calling this function sometimes crash app
    #check_framerate(win, conf)

    PART_ID = info['IDENTYFIKATOR']
    logging.LogFile(join('results', PART_ID + '.log'),
                    level=logging.INFO)  # errors logging

    logging.info('SCREEN RES: {}'.format(SCREEN_RES.values()))

    # showing start message
    show_info(win, join('.', 'messages', 'hello.txt'))

    # showing instruction

    show_image(win, 'images/InstrukcjaTrening.png')

    # Run trainee session
    run_trainee(win, conf, lang=0)
    win.flip()
    # time for break
    draw_hints(win, conf, 'refresh')
    show_image(win, 'images/break.png')
    # Run experiment session, random between russian and polish session
    win.flip()
    run_experiment(win, conf, random.randint(0, 1))
    save_beh_results()
    logging.flush()
    show_info(win, join('.', 'messages', 'end.txt'))
    win.close()


def draw_hints(win, conf, lang):
    """
       AGATKA:
        Hints in txt for any reason
        There is some problems with autoDraw in text so we use image hints which replace hints in second language
    """
    red_pl = visual.TextStim(win, text='d = czerwony', color="#" + conf["RED"],
                             pos=(-450, 400), height=conf['FONT_SIZE_INT'])
    green_pl = visual.TextStim(win, text='f = zielony', color="#" + conf["GREEN"],
                               pos=(-150, 400), height=conf['FONT_SIZE_INT'])
    blue_pl = visual.TextStim(win, text='j = niebieski', color="#" + conf["BLUE"],
                              pos=(150, 400), height=conf['FONT_SIZE_INT'])
    pink_pl = visual.TextStim(win, text="k = r�\u017Cowy", color="#" + conf["PINK"],
                              pos=(450, 400), height=conf['FONT_SIZE_INT'])
    red_rus = visual.TextStim(win, text='d = \u043A\u0440\u0430\u0441\u043D\u044B\u0439',
                              color="#" + conf["RED"], pos=(-450, 400), height=conf['FONT_SIZE_INT'])
    green_rus = visual.TextStim(win, text='f = \u0437\u0435\u043B\u0455\u043D\u044B\u0439',
                                color="#" + conf["GREEN"], pos=(-150, 400), height=conf['FONT_SIZE_INT'])
    # seventh char is crashing the program (\u0301) so i deleted it
    blue_rus = visual.TextStim(win, text='j = \u0433\u043e\u043b\u0443\u0431\u043e\u0439',
                               color="#" + conf["BLUE"], pos=(150, 400), height=conf['FONT_SIZE_INT'])
    # as above, \u0301 should be the third one in a row
    pink_rus = visual.TextStim(win, text='k = \u0440\u043e\u0437\u043e\u0432\u044b\u0439',
                               color="#" + conf["PINK"], pos=(450, 400), height=conf['FONT_SIZE_INT'])

    hints_pl = visual.ImageStim(win=win, image='images/hints_pl.png',
                                interpolate=True, pos=(conf['HINTS_PLACE_X'], conf['HINTS_PLACE_Y']))
    hints_rus = visual.ImageStim(win=win, image='images/hints_rus.png',
                                 interpolate=True, pos=(conf['HINTS_PLACE_X'], conf['HINTS_PLACE_Y']))
    grey_bar = visual.ImageStim(win=win, image='images/grey_bar.png',
                                 interpolate=True, pos=(conf['HINTS_PLACE_X'], conf['HINTS_PLACE_Y']))
    if lang == 'refresh':
        grey_bar.autoDraw = True
        grey_bar.draw()
    if lang == 0:
        hints_pl.autoDraw = True
        hints_pl.draw()

    if lang == 1:
        hints_rus.autoDraw = True
        hints_rus.draw()

"""AGATKA"""
def draw_cross(win, conf):
    cross = visual.TextStim(win, text='+', height=conf['CROSS_SIZE_INT'], color='black')
    cross.autoDraw = True
    win.flip()
    cross.draw()
    timer(1, conf['FIX_CROSS_TIME'])
    win.flip()
    cross.autoDraw = False


def run_trainee(win, conf, lang):
    clock = core.Clock()
    colors = conf['COLORS_ARRAY_HEX']
    # Start loop for certain amount of trials
    draw_hints(win, conf, lang)
    for i in range(conf['TRAINEE_SESSIONS_TRIALS_INT']):
        # get random word from adjectives array
        text = random.choice(conf['ADJECTIVES'])
        color = random.choice(colors)
        # draw word in the screen
        win.callOnFlip(clock.reset)
        # because of winflip we repeat draw_hints in every loop, which is not optimal
        draw_cross(win, conf)
        adjective = visual.TextStim(win, text=text, color="#" + color, height=conf['FONT_SIZE_STIM_INT'])
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
            correct.autoDraw = True
            win.flip()
            correct.draw()
            timer(1, conf['SHOW_RESULTS_S'])
            win.flip()
            correctness = 1
            correct.autoDraw = False
            win.flip()
        else:
            win.flip()
            error = visual.TextStim(win, text='X', color='red')
            error.autoDraw = True
            win.flip()
            error.draw()
            timer(1, conf['SHOW_RESULTS_S'])
            correctness = 0
            error.autoDraw = False
            win.flip()
        # add results to the file
        RESULTS.append([PART_ID, 'trainee', round(key[0][1],
                        conf['DIGIT_AFTER_COMA_RESULTS_INT']) if key else 0,
                        correctness, i + 1, color,
                       'true' if (key is not None) and str(conf["MAPPING"][key[0][0]]) == str("#" + color) else 'false',
                        key[0][0] if key is not None else 'not pressed'])
        # wait certain amount of time to go back to next trial
        timer(1, conf['WAIT_TO_NEXT_TRIALS_S'])
        win.flip()


def run_experiment(win, conf, first):
    win.flip()
    if first == 0:
        db = create_color_db(conf, first)
        draw_hints(win, conf, 'refresh')
        show_image(win, 'images/Instrukcja1.png')
        engine(win, conf, db, first)
        win.flip()
        show_image(win, 'images/break.png')
        db = create_color_db(conf, first + 1)
        engine(win, conf, db, first + 1)
    else:
        db = create_color_db(conf, first)
        draw_hints(win, conf, 'refresh')
        show_image(win, 'images/Instrukcja2.png')
        engine(win, conf, db, first)
        win.flip()
        show_image(win, 'images/break.png')
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
    # Clearing clock just in case
    win.flip()
    clock = core.Clock()
    draw_hints(win, conf, lang=first)
    win.flip()
    for i in range(len(db)):
        win.flip()
        win.callOnFlip(clock.reset)
        draw_cross(win, conf)
        word = visual.TextStim(win, text=db[i][1], color="#" + db[i][0], height=conf['FONT_SIZE_STIM_INT'])
        word.autoDraw = False
        word.draw()
        win.flip()
        key = event.waitKeys(keyList=list(
            conf['REACTION_KEYS']), timeStamped=clock, maxWait=conf['WAIT_FOR_KEY_S'])
        if (key is not None) and str(conf["MAPPING"][key[0][0]]) == str("#" + db[i][0]):
            correctness = 1
        else:
            correctness = 0
        RESULTS.append([PART_ID, 'PL' if first == 0 else 'RUS',
                        round(key[0][1], conf['DIGIT_AFTER_COMA_RESULTS_INT']) if key else 0,
                        correctness, i + 1])
        # wait certain amount of time to go back to next trial
        timer(1, conf['WAIT_TO_NEXT_TRIALS_S'])
    draw_hints(win, conf, lang='refresh')


def timer(counter, seconds, command='pass'):
    """
        There is two types of time counter
        Type zero is the most correct but on some computers in this way time is not counted well
        Therefore, you can choose type one which is not as accurate as zero however does not cause as many problems
        """

    if counter == 0:
        for frames in range(int(60 * seconds)):
            exec(command)
    elif counter == 1:
        clock = core.Clock()
        clock.add(seconds)
        while clock.getTime() < 0:
            pass


if __name__ == '__main__':
    PART_ID = ''
    SCREEN_RES = get_screen_res()
    main()