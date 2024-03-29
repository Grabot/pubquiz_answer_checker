from view import view, db
from view.models import Answersheet
from view.models import Line
from view.models import Word
from view.models import SubAnswerGiven
from view.models import QuestionNumber
from view.models import Team
from flask import request
from flask import make_response
from flask import render_template
from flask import url_for
from flask import send_file
import numpy as np
import cv2
from app import docs
import zipfile
import io
import os
import pathlib
import shutil


@view.route('/answersheets/nuke', methods=['GET'])
def nuke_all_answersheets():
    Answersheet.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence answersheet_id_seq RESTART with 1')
    return 'ok'


@view.route("/load_answersheet/<int:question_id>", methods=['GET', 'POST'])
def load_answersheet(question_id):
    answersheet = Answersheet.query.filter_by(id=question_id).first()
    if answersheet is None:
        return "answersheet with id " + str(question_id) + " does not exist in the database."
    image_data = answersheet.answersheet_image
    # I need to know the exact shape it had in order to load it from the database
    width = answersheet.image_width
    height = answersheet.image_height
    np_answersheet = np.fromstring(image_data, np.uint8).reshape(width, height, 3)

    ret, png = cv2.imencode('.png', np_answersheet)
    response = make_response(png.tobytes())
    response.headers['Content-Type'] = 'image/png'
    return response


@view.route("/answersheets/load", methods=['GET', 'POST'])
def answersheet_all():
    # TODO With large number of answersheets saved in the database make a 'next', 'previous' button functionality.
    page = request.args.get('page', 1, type=int)
    answersheets = Answersheet.query.paginate(page, view.config['ANSWERSHEETS_PER_PAGE'], False)

    next_url = None
    if answersheets.has_next:
        next_url = url_for('answersheet_all', page=answersheets.next_num)

    prev_url = None
    if answersheets.has_prev:
        prev_url = url_for('answersheet_all', page=answersheets.prev_num)

    return render_template("answersheet.html", answersheets=answersheets.items, next_url=next_url, prev_url=prev_url)


@view.route('/nuke/all', methods=['GET'])
def nuke_all():
    SubAnswerGiven.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence subanswergiven_id_seq RESTART with 1')

    Word.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence word_id_seq RESTART with 1')

    Line.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence line_id_seq RESTART with 1')

    Answersheet.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence answersheet_id_seq RESTART with 1')

    QuestionNumber.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence questionnumber_id_seq RESTART with 1')
    return 'database images cleared'


@view.route('/api/v1.0/createdoc', methods=['POST'])
def create_doc():
    # First we remove the folder 'pubquiz_sheets' because we want to create that folder with new content
    if os.path.exists('pubquiz_sheets'):
        shutil.rmtree('pubquiz_sheets')
    post = request.get_json()
    print("ER IS POST %s" % post)
    message = docs.create_doc(post)
    return message


@view.route('/api/v1.0/download/templates', methods=['GET'])
def request_answersheet_templates():
    # After the document is created we want to send it to the user.
    base_path = pathlib.Path('pubquiz_sheets')
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            print("folder %s" % str(f_name))
            for doc_file in f_name.iterdir():
                print("file %s" % str(doc_file))
                z.write(doc_file)
    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='templates.zip'
    )

