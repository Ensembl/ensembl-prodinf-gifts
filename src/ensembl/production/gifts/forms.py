#!/usr/bin/env python
# .. See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from wtforms import Form, StringField, SubmitField, TextAreaField
from wtforms.validators import Email, InputRequired


class GIFTsSubmissionForm(Form):
    ensembl_release = StringField('Ensembl Release', validators=[InputRequired()])
    environment = StringField("Environment", default="staging", render_kw={'readonly': True})
    email = StringField('Email', validators=[Email(), InputRequired()])
    auth_token = TextAreaField('Authentication Token', validators=[InputRequired()])
    tag = StringField('Tag')
    update_ensembl = SubmitField('Update Ensembl')
    process_mapping = SubmitField('Process Mapping')
