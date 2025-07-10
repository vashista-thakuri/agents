import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smolagents.tools import Tool

import re

class OutlookEmailTool(Tool):
    name = "outlook_email"
    description = "Send an email using Outlook SMTP."
    inputs = {
        "to_email": {"type": "string", "description": "Recipient email address", "nullable": True},
        "subject": {"type": "string", "description": "Subject of the email", "nullable": True},
        "body": {"type": "string", "description": "Body of the email", "nullable": True},
        "from_email": {"type": "string", "description": "Sender's Outlook email address", "nullable": True},
        "password": {"type": "string", "description": "Sender's Outlook app password", "nullable": True}
    }
    output_type = "string"

    def is_valid_email(self, email):
        return isinstance(email, str) and re.match(r"[^@]+@[^@]+\\.[^@]+", email)

    def forward(
        self,
        to_email=None,
        subject=None,
        body=None,
        from_email=None,
        password=None
    ):
        # Use default if not a valid email
        if not self.is_valid_email(to_email):
            to_email = "vashista.thakuri@gmail.com"
        if not self.is_valid_email(from_email):
            from_email = "vashista.thakuri@gmail.com"
        if subject is None:
            subject = ""
        if body is None:
            body = ""
        if password is None:
            password = ""
        try:
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            return f"Email sent to {to_email} successfully."
        except Exception as e:
            return f"Failed to send email: {str(e)}"
