from wtforms import Form, StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired
from werkzeug import secure_filename


class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    category = SelectField('category')
    upload = FileField('image')
