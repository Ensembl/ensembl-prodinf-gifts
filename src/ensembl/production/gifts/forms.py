from wtforms import Form, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import Email, InputRequired


class GIFTsSubmissionForm(Form):
    ensembl_release = StringField('Ensembl Release', validators=[InputRequired()])
    environment = SelectField('Environment', choices=[('dev', 'Dev'), ('staging', 'Staging')],
                              validators=[InputRequired()])
    email = StringField('Email', validators=[Email(), InputRequired()])
    auth_token = TextAreaField('Authentication Token', validators=[InputRequired()])
    tag = StringField('Tag')
    update_ensembl = SubmitField('Update Ensembl')
    process_mapping = SubmitField('Process Mapping')
