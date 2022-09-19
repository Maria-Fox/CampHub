from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, URLField, TextAreaField
from wtforms.validators import InputRequired, Optional, Length 

class Signup_Form (FlaskForm):
    '''Form for rendering signup form and creating a new account.'''

    username = StringField("Create a username", validators = [InputRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5)])
    school_name = StringField("Bootcamp Name", validators = [InputRequired()])
    field_of_study = StringField("Field of Study", validators = [InputRequired()])

class Login_Form (FlaskForm):
    '''Form to authenticate existing user.'''

    username = StringField("Create a username", validators = [InputRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5)])

class Edit_Profile_form(FlaskForm):
    '''Allow authroize duser to edit profile details.'''

    username = StringField("Update Username", validators = [InputRequired(), Length(max=20)])
    school_name = StringField("Bootcamp Name", validators = [InputRequired()])
    field_of_study = StringField("Field of Study", validators = [InputRequired()])
    

class Camphub_User_Post_Form(FlaskForm):
    '''Form for user to create a new page/article.'''

    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Content", validators=[InputRequired()])

class Camphub_Comment_Form(FlaskForm):
    '''Create a comment for an article/page.'''

    content = TextAreaField("Comment", validators = [InputRequired()])

class Suggest_Topic_Form(FlaskForm):
      '''Form to allow users to suggest'''

      topic = StringField("Title", validators= [InputRequired()])
      details = TextAreaField("Details", validators = [InputRequired()])