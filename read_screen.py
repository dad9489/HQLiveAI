from PIL import Image
import pytesseract
import time
import pygetwindow as gw
import pyautogui
from search import google_search
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


class IncorrectTextError(Exception):
    """Raised when the data has been read incorrectly from the screen grab"""
    pass


def analyze_screen():
    active = gw.getActiveWindow()
    print('Please run ApowerMirror and mirror your phone, and make sure the main window is selected on your computer.')
    was_selected = False
    searched = []
    while True:
        active = gw.getActiveWindow()
        if active is not None and (active.title == 'ApowerMirror Main'):
            if not was_selected:
                was_selected = True
                print('The correct window is active. Please do not click away.')
            img = pyautogui.screenshot()
            left = active.left
            top = active.top
            right = active.left + active.width
            bottom = active.top + active.height
            img = img.crop((left, top, right, bottom))

            if round(img.width/img.height, 1) == round(16.0/9.0, 1):
                # the phone is horizontal with a 16:9 ration, so we need to crop it
                # this happens when a screen recoded video of a vertical screen is played
                left = round(img.width*0.34)
                right = round(img.width - (img.width*0.34))
                img = img.crop((left, 0, right, img.height))

            # crop to the size of the game window TODO are these the correct dimensions in an actual game?
            game_left = img.width * 0.0375
            # game_top = img.height * 0.0375
            game_top = img.height * 0.1786
            game_right = img.width * 0.9595
            game_bottom = img.height * 0.6851
            img = img.crop((round(game_left), round(game_top), round(game_right), round(game_bottom)))
            img.save('img/screenshot.png')

            q_and_a = read_question(img)
            if q_and_a is not None and q_and_a[0] not in searched:
                question = q_and_a[0]
                searched.append(question)
                answers = q_and_a[1]
                results = google_search(question)
                results = re.sub('[^a-zA-Z0-9]', '', results).lower()

                answer_counts = []
                total = 0
                for answer in answers:
                    answer_clean = re.sub('[^a-zA-Z0-9]', '', answer).lower()
                    count = results.count(answer_clean)
                    total += count
                    answer_counts.append((answer, count))

                for answer_count in answer_counts:
                    if total == 0:
                        percent = 0
                    else:
                        percent = round(answer_count[1]/total, 2)*100
                    print(answer_count[0]+': '+str(percent)+'%')

        else:
            if was_selected:
                print('You have clicked away from the main window of ApowerMirror. Please reselect that window.')
            was_selected = False


def read_question(img):
    """
    Given an image of an HQ question, this will use Tesseract to analyze the text in the image
    and convert it to a tuple of the question to the answer choices.
    :param img: an image object with the game window in focus
    :return: a tuple of the question and a list of the answer choices
    """
    try:
        img_data = pytesseract.image_to_string(img)
        split = img_data.split('\n')
        split = list(filter(lambda a: a != '' and not a.isspace(), split))
        question_loc = None
        for line_num in range(len(split)):
            if '?' in split[line_num]:
                question_loc = line_num
                break
        if question_loc is None:
            raise IncorrectTextError

        question = ' '.join(split[0:question_loc+1])
        split = split[question_loc+1:]
        # split = split[question_loc:question_loc+4]
        # if len(split) != 4:
        if len(split) != 3:
            raise IncorrectTextError

        # question = split.pop(0).replace('\n', ' ')
        answers = []
        for line in split:
            answers.append(line)
        return question, answers
    except IncorrectTextError:
        # print("There was an error reading this image: There was not a clear question and 3 answers.")
        return None


if __name__ == '__main__':
    # start = time.time()
    # mapping = read_question('img/question_screenshot3.png')
    # print(time.time() - start)
    # print(mapping)
    analyze_screen()
