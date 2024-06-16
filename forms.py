from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import EmailField, StringField, PasswordField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Your Password', validators=[DataRequired()])
    conf_password = PasswordField('Confirm the Password', validators=[DataRequired()])
    submit = SubmitField('Create Account')

class UploadForm(FlaskForm):
    file = FileField('File', validators=[FileRequired(), FileAllowed(['pdf', 'doc', 'docx', 'txt', 'mp3', 'mp4', 'jpeg', 'jpg', 'png'], 'Only PDF, DOC, DOCX, TXT or Image files allowed')])
    group_name = StringField('File Group Name')
    submit = SubmitField('Upload')

class ShareForm(FlaskForm):
    file_group = SelectField('File Group', validators=[DataRequired()])
    user = SelectField('User', validators=[DataRequired()])
    submit = SubmitField('Share')

class DownloadForm(FlaskForm):
    file = SelectField('File', choices=[])
    submit = SubmitField('Download')

class AdminCommandForm(FlaskForm):
    command = StringField('Command', validators=[DataRequired()])
    submit = SubmitField('Execute')

class CommentForm(FlaskForm):
    file = SelectField('File', validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')