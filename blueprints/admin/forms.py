from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length

from wtforms.widgets import ListWidget, CheckboxInput



class MultipleCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class InstagramLoginForm(FlaskForm):
    username = StringField(label='Username', name='username', validators=[DataRequired()])
    password = PasswordField(label='Password', name='password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField(label='Login')


class InstagramVerifyFrom(FlaskForm):
    verification_code = StringField(label='Verification Code', name='verification_code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField(label='Verify')


class InstagramLogoutForm(FlaskForm):
    submit = SubmitField(label='Logout')

class InstagramCookieSet(FlaskForm):
    cookie = StringField(label='Cookies', name='cookie', validators=[DataRequired()])
    submit = SubmitField(label='Set')

class LoginForm(FlaskForm):
    username = StringField(label='Username', name='username', validators=[DataRequired()])
    password = PasswordField(label='Password', name='password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField(label='Login')


class RegisterForm(FlaskForm):
    new_username = StringField(label='New Username', name='new_username', validators=[DataRequired()])
    role = SelectField(label='Role', name='role', validators=[DataRequired()], choices=[('root', 'Root'), ('admin', 'Admin'), ('viewer', 'Viewer')], default='admin')
    new_password = PasswordField(label='New Password', name='new_password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(label='Confirm Password', name='confirm_password', validators=[DataRequired(), Length(min=8)])
    current_password = PasswordField(label='Current Password', name='current_password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField(label='Register')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(label='Current Password', name='current_password', validators=[DataRequired(), Length(min=8)])
    new_password = PasswordField(label='New Password', name='new_password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(label='Confirm Password', name='confirm_password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField(label='Change')


class EditAdminsForm(FlaskForm):
    admins_list = MultipleCheckboxField(label='Admins', name='admins_list', coerce=int)
    current_password = PasswordField(label='Current Password', name='current_password', validators=[DataRequired(), Length(min=8)])
    action = SelectField(label='Action', name='action', choices=[('root', 'Root'), ('admin', 'Admin'), ('viewer', 'Viewer'), ('banned', 'Ban'), ('delete', 'Delete')], default='viewer')
    submit = SubmitField(label='Edit')


class DeleteAccountForm(FlaskForm):
    password = PasswordField(label='Password', name='password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(label='Confirm Password', name='confirm_password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField(label='Delete')


class ConfirmDeleteAccountForm(FlaskForm):
    username = StringField(label='Username', name='username', validators=[DataRequired()])
    submit = SubmitField(label='Confirm Delete')