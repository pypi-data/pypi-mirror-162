"""
The aurori project

Copyright (C) 2022  Marcus Drobisch,

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Marcus Drobisch"]
__contact__ = "aurori@fabba.space"
__credits__ = []
__license__ = "AGPLv3+"

import smtplib
from email.mime.text import MIMEText
from jinja2 import Template
from aurori.jobs.job import Job
import ssl


class MailFromFileTemplateJob(Job):

    description = "Send a mail from a local template file with data"

    def defineArguments(self):
        self.addListArgument('recipients',
                             label="Recipients",
                             description="List of recipients email adresses")
        self.addStringArgument('subject',
                               label="Subject",
                               description="Subject of the mail")
        self.addStringArgument('template_path',
                               label="Template path",
                               description="File path to the template")
        self.addDictArgument('data',
                             label="Template data",
                             description="Data for the template")

    def run(self, **kwargs):
        config = kwargs['mail_config']
        subject = kwargs['subject']
        recipients = kwargs['recipients']
        template_path = kwargs['template_path']
        data = kwargs['data']

        sender = config.get('sender')

        # Get File Content in String
        jinja2_template_string = open(template_path, 'r').read()

        # Create Template Object
        template = Template(jinja2_template_string)

        # Render HTML Template String
        content = template.render(**data)

        # try to send message
        try:
            msg = MIMEText(content)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ','.join(recipients)

            host = config.get('server')
            port = config.get('port')
            username = config.get('username')
            password = config.get('password')
            try:
                s = smtplib.SMTP_SSL(host, port)
            except Exception:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                s = smtplib.SMTP(host, port)
                s.starttls(context=context)
            s.login(username, password)

            #print(sender, recipients, host, port, username, password)
            s.send_message(msg)
            s.quit()
        except Exception as e:
            print(e)
            raise e
