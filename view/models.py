from view import db, ma
import json
from werkzeug.security import generate_password_hash, check_password_hash


# models for database
# schema exposes fields to expose


class Person(db.Model):
    """ users """
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    personname = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PersonSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'personname', 'password_hash')


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(255))
    score = db.Column(db.Integer)

    def get_team_name(self):
        return self.teamname


class TeamSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'teamname', 'score')


class Category(db.Model):
    """ category of question """
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class CategorySchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name')


class Type(db.Model):
    """ type of question (e.g. multiple choice) """
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class TypeSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name')


class Variant(db.Model):
    """ for some questions, multiple answers (variants) are correct """
    __tablename__ = 'variant'
    id = db.Column(db.Integer, primary_key=True)
    subanswer_id = db.Column(db.Integer, db.ForeignKey('subanswer.id'))
    answer = db.Column(db.String(255))
    isNumber = db.Column(db.Boolean)

    def get_answer(self):
        return self.answer


class VariantSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'subanswer_id', 'answer', 'isNumber')


class SubAnswer(db.Model):
    """ question can have multiple subquestions, each subquestion has a subanswer """
    __tablename__ = 'subanswer'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    variants = db.relationship('Variant')


class SubAnswerSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'question_id', 'variants')

    variants = ma.Nested(VariantSchema(many=True))


class LineSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'answersheet_id', 'image_width', 'image_height', 'image')


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    questionnumber = db.Column(db.Integer)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    createdby = db.relationship('Person')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    questioncategory = db.relationship('Category')
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    questiontype = db.relationship('Type')
    question = db.Column(db.String(255))
    subanswers = db.relationship('SubAnswer')
    active = db.Column(db.Boolean)

    def get_question(self):
        return self.question


class QuestionSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = (
            'id', 'questionnumber', 'person_id', 'category_id', 'question', 'active', 'subanswers', 'questioncategory',
            'createdby', 'type_id', 'questiontype')

    subanswers = ma.Nested(SubAnswerSchema(many=True))
    questioncategory = ma.Nested(CategorySchema)
    questiontype = ma.Nested(TypeSchema)
    createdby = ma.Nested(PersonSchema)

# mag weg
class SubAnswerGiven(db.Model):
    """ A answer can consist of multiple lines, this indicates a single line of an answer. """
    __tablename__ = 'subanswergiven'
    id = db.Column(db.Integer, primary_key=True)
    corr_answer_id = db.Column(db.Integer, db.ForeignKey('subanswer.id'), nullable=False)
    corr_answer = db.relationship('SubAnswer')
    read_answer = db.Column(db.String(255))
    probability_read_answer = db.Column(db.Float)
    correct = db.Column(db.Boolean)
    confidence = db.Column(db.Float)
    probability_read_answer = db.Column(db.Float)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    checkedby = db.relationship('Person')
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=False)
    line = db.relationship('Line')
    answergiven_id = db.Column(db.Integer, db.ForeignKey('answergiven.id'), nullable=False)


class SubAnswerGivenSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = (
            'id', 'corr_answer_id', 'corr_answer', 'read_answer', 'correct', 'person_id', 'checkedby', 'confidence',
            'line',
            'answergiven_id')

    checkedby = ma.Nested(PersonSchema)
    corr_answer = ma.Nested(SubAnswerSchema)
    line = ma.Nested(LineSchema)

# mag weg
class AnswerGiven(db.Model):
    __tablename__ = 'answergiven'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.relationship('Question')
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    answered_by = db.relationship('Team')
    subanswersgiven = db.relationship('SubAnswerGiven', lazy='dynamic')


class AnswerGivenSchema(ma.Schema):
    class Meta:
        fields = ('id', 'question_id', 'question', 'team_id', 'answered_by', 'subanswersgiven')
    question = ma.Nested(QuestionSchema)
    answered_by = ma.Nested(TeamSchema)
    subanswersgiven = ma.Nested(SubAnswerGivenSchema, many=True)

# mag weg
class Answersheet(db.Model):
    """ image of complete answersheet (handwritten) """
    __tablename__ = 'answersheet'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    answersheet_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)

    def set_team_id(self, team_id):
        self.team_id = team_id

    def get_team_id(self):
        return self.team_id

# mag weg
class AnswerSheetQuestion(db.Model):
    """ answersheet corresponding to a question """
    __tablename__ = 'answersheetquestion'
    id = db.Column(db.Integer, primary_key=True)
    answersheet_id = db.Column(db.Integer, db.ForeignKey('answersheet.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

# mag weg
class Word(db.Model):
    """ A word object, corresponding to words in a line. """
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'))
    word_recognised = db.Column(db.String(255))
    probability = db.Column(db.Float)
    word_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)

# mag weg
class Line(db.Model):
    """ A line object, corresponding to an answersheet line """
    __tablename__ = 'line'
    id = db.Column(db.Integer, primary_key=True)
    line_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)

# mag weg
class QuestionNumber(db.Model):
    """ A word object, corresponding to words in a line. """
    __tablename__ = 'questionnumber'
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.String(255))
    question_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)
