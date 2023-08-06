import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ShynaMailClient:
    """
    Make sure define a default path of image file. it will use that image or any other file instead of that image.
    Below value need to be defined:
    path = ""
    sender_gmail_account_id = ""
    sender_gmail_account_pass = ""
    master_email_address_is = ""
    email_subject = ""
    email_body = ""

    method
    send_email_with_attachment_subject_and_body: Need email_subject and email_body
    """
    msg = MIMEMultipart()
    path = ""
    sender_gmail_account_id = ""
    sender_gmail_account_pass = ""
    master_email_address_is = ""
    email_subject = ""
    email_body = ""

    def send_email_with_attachment_subject_and_body(self):
        try:
            from_password = self.sender_gmail_account_pass
            self.msg = MIMEMultipart()
            self.msg['From'] = self.sender_gmail_account_id
            self.msg['To'] = self.master_email_address_is
            self.msg['Subject'] = self.email_subject
            body = self.email_body
            self.msg.attach(MIMEText(body, 'plain'))
            filename = self.path
            attachment = open(filename, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            self.msg.attach(p)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(self.sender_gmail_account_id, from_password)
            text = self.msg.as_string()
            s.sendmail(self.sender_gmail_account_id, self.master_email_address_is, text)
            s.quit()
            print("I have sent you the details check your email now")
        except Exception as ex:
            print("Exception from functionality sys \n", str(ex))
