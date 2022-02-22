from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class StoryTextForm(FlaskForm):
    text = TextAreaField(name='story_text', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField(label='Submit')
