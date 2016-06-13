from wtforms import Form, StringField, TextAreaField, SubmitField, validators, ValidationError, PasswordField


class ChatForm(Form):
    pseudo = StringField("Pseudo", [validators.Length(min=4, max=35)])
    message = TextAreaField("Message", [validators.Length(min=4, max=500)])
    submit = SubmitField("Submit")


class ConnForm(Form):
    pseudo = StringField("Pseudo", [validators.Length(min=4, max=35)])
    password = PasswordField("Password", [validators.Length(min=4, max=100)])
    submit = SubmitField("Log in")


class SignUpForm(Form):
    pseudo = StringField("Pseudo", [validators.Length(min=4, max=35)])
    password = PasswordField("Password", [validators.Length(min=4, max=50),
                                          validators.DataRequired(),
                                          validators.EqualTo('conf_password', message='Passwords must match')])

    conf_password = PasswordField("confirmation password", [validators.Length(min=4, max=50)])
    mail = StringField("mail", [validators.Email(message="Should be an email")])
    submit = SubmitField("Submit")
