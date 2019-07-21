from PIL import Image
import pytesseract
import time
import pygetwindow as gw

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


class IncorrectTextError(Exception):
    """Raised when the data has been read incorrectly from the screen grab"""
    pass


def analyze_screen():
    active = gw.getActiveWindow()
    while True:
        active = gw.getActiveWindow()
        if active is not None and (active.title == 'ApowerMirror'):
            x = 1


def read_question(src_img):
    """
    Given an image of an HQ question, this will use Tesseract to analyze the text in the image
    and convert it to a mapping of the question to the answer choices.
    :param src_img: the url of an image
    :return: a dictionary with the question mapped to a list of the answer choices
    """
    try:
        img_data = pytesseract.image_to_string(Image.open(src_img))
        split = img_data.split('\n\n')
        question_loc = None
        for line_num in range(len(split)):
            if '?' in split[line_num]:
                question_loc = line_num
        if question_loc is None:
            raise IncorrectTextError

        split = split[question_loc:question_loc+4]
        if len(split) != 4:
            raise IncorrectTextError

        mapping = {}
        question = split.pop(0).replace('\n', ' ')
        answers = []
        for line in split:
            answers.append(line)
        mapping[question] = answers
        return mapping
    except IncorrectTextError:
        print("There was an error reading this image: There was not a clear question and 3 answers.")


if __name__ == '__main__':
    # start = time.time()
    # mapping = read_question('img/question_screenshot3.png')
    # print(time.time() - start)
    # print(mapping)
    analyze_screen()
