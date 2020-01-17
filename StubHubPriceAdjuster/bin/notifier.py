
import smtplib
import logging

from sheet import Sheet

class Notifier(object):
    
    
    distrib_list = []
    sent_from = ""
    initiated = False
    smtp_username = ""
    smtp_password = ""
    
    # navigate to https://myaccount.google.com/lesssecureapps with your account to enable less secure logins
    def __init__(self, server = "smtp.gmail.com", port = 587, username = "", password = "", auth_file = ""):
        """
        init
        """
        
        try:
            self.sheet = Sheet(auth_file_name = auth_file, sheet_name = "contacts")
            self.sheet.open_sheet()
            self.config_distrib_list()
            
            self.smtpserver = smtplib.SMTP(server, port)
            self.smtpserver.ehlo()
            self.smtpserver.starttls()
            self.smtpserver.ehlo()
            
            
            self.smtpserver.login(self.smtp_username, self.smtp_password)
            
            self.initiated = True
            
                
        except Exception as e:
    
            logging.debug(" unable to initiate email notifications ")
            logging.debug(e)
        
        
    def config_distrib_list(self):
        """
        get distirib list
        """
        
        for row in self.sheet.all_sheet_records:
            self.distrib_list.append(row['contacts'])
        
        self.sent_from = self.sheet.all_sheet_records[0]['from']
        self.smtp_username = self.sheet.all_sheet_records[0]['credentials']
        self.smtp_password = self.sheet.all_sheet_records[1]['credentials']
        
        
    def send(self, content = "", subject = ""):
        """
        send notification
        """
        
        self.sheet.login()
        
        if(self.initiated):
                   
            try:
                
                body = '\r\n'.join(['To: %s' % ", ".join(self.distrib_list),
                    'From: %s' % self.sent_from,
                    'Subject: %s' % subject,
                    '', 
                    content]
                )
                
                self.smtpserver.sendmail(self.sent_from, self.distrib_list, body)
                logging.info("\nSending notification ")
                logging.info("From: " + self.sent_from)
                logging.info("To: " + ", ".join(self.distrib_list))
                logging.info("\n")
            
            except Exception as e:
                logging.debug(e)
            
        else:
            logging.debug(" the email client was not initiated ")
            
        
        
if(__name__ == "__main__"):
    
    n = Notifier()
    
    n.send(
        content = "this is a test message",
        subject = "ticket price has been adjusted"
    )
            