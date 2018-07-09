#-------------------------------------------------------------------------------
# Name:        BackupControl
# Purpose:
#
# Author:      anvar
#
# Created:     09.07.2018
# Copyright:   (c) anvar 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import smtplib
from email.mime.text import MIMEText
from email.header import Header

def SendEmail(host, from_addr, pas, to_addr, subject, body_text):
    msg = MIMEText(body_text, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr

    server = smtplib.SMTP_SSL(host, 465, 10)
    server.login(from_addr, pas)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def main():

    pathBackup = ''

    SendEmail(
        'smtp.yandex.ru',
        '',
        '',
        'apxi2@yandex.ru',
        'Тест',
        'Тело письма'
    )

if __name__ == '__main__':
    main()
