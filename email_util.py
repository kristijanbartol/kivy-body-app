import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# https://stackoverflow.com/questions/3362600/how-to-send-email-attachments


def send_email(_):
    
    try: 
        # Create your SMTP session 
        smtp = smtplib.SMTP('smtp.gmail.com', 587) 

        # Use TLS to add security 
        smtp.starttls() 

        # User authentication 
        smtp.login('kivy.body.app', '61346704rs')

        # Defining the message 
        msg = MIMEMultipart()
        msg.attach(MIMEText('Message body'))
        
        # Add an attachment
        '''
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
        '''

        # Send an email
        smtp.sendmail('kivy.body.app', 'kristijan.bartol@gmail.com', msg.as_string()) 

        # Terminate the session 
        #smtp.quit() 
        smtp.close()
        print ('Email sent successfully!') 

    except Exception as ex: 
        print('Something went wrong....', ex)
