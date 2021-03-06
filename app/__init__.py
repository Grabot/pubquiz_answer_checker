"""
A neural network that reads handwriting from given images.
Based on the project :
'build a handwritten text recognition system'
https://towardsdatascience.com/build-a-handwritten-text-recognition-system-using-tensorflow-2326a3487cd5
"""
import sys
from app.Model import Model
from app.Model import DecoderType
from app.pdf_to_image import convert_pdf_to_image
from app.line_segmentation import line_segmentation, crop_and_warp
from app.word_segmentation import word_segmentation, prepare_image, find_rect, show_image, save_word_image, save_word_details
import os
import cv2
import argparse
from view.models import Team
from view.models import SubAnswerGiven
from view.models import SubAnswer
from view.models import Question
from view.models import QuestionNumber
from view.models import Variant
from view.config import InputConfig
import numpy as np
import pytesseract
import re
import app.save_to_database
from view import db
from app.process_team import read_team
from app.process_question_number import read_question_number


def process_sheet(answer_sheet_image, model):
    problem = False
    sub_answer_number = 0
    previous_question = -1
    team_id = -1
    read_team_name = True
    resized_height = 50
    # After the resizing, the size of the number box will always be around this value.
    number_box_size = 66
    print("processing lines")
    for line_result in line_segmentation(answer_sheet_image):
        if line_result is None:
            print("It did not correctly read the lines from this answhersheet image!")
            problem = True
        else:
            line = line_result[0]
            # The first line of each answersheet will include the team name.
            if read_team_name:
                print("reading the team name")
                read_team_name = False
                team_id = read_team(line)
                # We remove the line after the team is determined since we don't need this for anything anymore.
                save_to_database.remove_line_in_database(line_result[2])
            else:
                print("processing normal line")
                # Here we define some parameters of the line used for the processing.
                original_height = line.shape[0]
                multiply_factor = original_height / resized_height
                # TODO @Sander: maybe update the line with the new image, which is smaller and easier to load
                line, question_image = prepare_image(line, resized_height, number_box_size)
                question_number = read_question_number(question_image, previous_question)

                if question_number != "":
                    # We will update the line image with the new one without the question number.
                    # The line id is taken from the result and the new line is the one without the question number
                    save_to_database.update_line_in_database(line, line_result[2])

                    question_id = int(question_number)
                    if question_id == previous_question:
                        # If this question has the same number as before we should find a variant, because it will have
                        # several sub_answers associated with it
                        sub_answer_number += 1
                    else:
                        sub_answer_number = 0
                    previous_question = question_id
                else:
                    # We turn the question_id to 0. This means it will be ignored.
                    question_id = 0
                    save_to_database.remove_line_in_database(line_result[2])
                print("the question number that is read: " + str(question_id))

                res = word_segmentation(line, kernel_size=25, sigma=11, theta=7, min_area=100)
                save_word_details(line_result, multiply_factor, res, number_box_size, db, model, team_id, question_id, sub_answer_number)
    return problem


def run_pubquiz_program(answer_sheets):
    print("De officiele Ordina pub-quiz antwoord vinder")
    model = Model(open('model/charList.txt').read())

    # Not the cleanest way to detect an error, but the fastest to implement
    problem = False
    for p in convert_pdf_to_image(answer_sheets):
        if p is not None:
            try:
                print("start processing answersheet")
                if process_sheet(p, model):
                    problem = True
            except:
                return "Bestand uploaden mislukt. Het bestand kan niet uitgelezen worden."
    if problem:
        return "Bestand uploaden mislukt. Het bestand kan niet uitgelezen worden."



def save_answersheet():
    pubquiz_answer_sheets = 'scan.pdf'
    pages = convert_pdf_to_image(pubquiz_answer_sheets)
    return pages

