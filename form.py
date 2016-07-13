from wtforms import Form, StringField, TextAreaField, SubmitField, validators, ValidationError


class ContactFormFr(Form):
    name = StringField("Nom", [validators.Length(min=4, max=35)])
    email = StringField("Email", [validators.Length(min=4, max=35), validators.Email()])
    subject = StringField("Sujet", [validators.Length(min=4, max=40)])
    message = TextAreaField("Message", [validators.Length(min=4, max=200)])
    submit = SubmitField("Envoyer")


class ContactFormEn(Form):
    name = StringField("Name", [validators.Length(min=4, max=35)])
    email = StringField("Email", [validators.Length(min=4, max=35), validators.Email()])
    subject = StringField("Subject", [validators.Length(min=4, max=40)])
    message = TextAreaField("Message", [validators.Length(min=4, max=200)])
    submit = SubmitField("Send")
