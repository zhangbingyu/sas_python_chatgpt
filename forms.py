from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from models import User

# registration form
class RegistrationForm(FlaskForm):
    """
    Form for user registration
    """
    username = StringField("UserName", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        """validate whether the user exists in the database"""
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValidationError('Email address exists.')


# login form
class LoginForm(FlaskForm):
    """Form for user log in"""
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

class ResetForm(FlaskForm):
    """Form for user log in"""
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ResetInitialForm(FlaskForm):
    """Form for user log in"""
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Send reset link')

class OpenAIForm(FlaskForm):
    """Form for SAS input"""
    sas = TextAreaField('SAS', validators=[DataRequired()])
    response = TextAreaField('Response')
    submit = SubmitField('Analyze')
