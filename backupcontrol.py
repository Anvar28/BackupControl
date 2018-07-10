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
import os
import pathlib
import time
from email.mime.text import MIMEText
from email.header import Header

def SendEmailLong(host, from_addr, pas, to_addr, subject, body_text):
    msg = MIMEText(body_text, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr

    server = smtplib.SMTP_SSL(host, 465, 10)
    server.login(from_addr, pas)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def SendEmail(body_text):
    SendEmailLong('smtp.yandex.ru', 'test@pioner-plus.ru', 'Test2808', 'apxi2@yandex.ru', 'Тест', body_text)

def main():

    pathBackup = r'D:\projects\python\BackupControl\test'

    if not os.path.exists(pathBackup):
        SendEmail('Не найден каталог с архивными копиями: '+pathBackup)
    else:
        # Перебираем файлы, сортируем по уменьшению даты
        # если размер предыдущего архива меньше, то отправляем письмо
        # если дата создания меньше текущей даты, то отправляем письмо

        allFiles = {}
        currentDirectory = pathlib.Path(pathBackup)
        for f in currentDirectory.iterdir():
            timeFile = time.gmtime(os.path.getctime(str(f)))
            strTimeFile = time.strftime('%Y-%m-%d-%H-%M-%S', timeFile)
            allFiles[strTimeFile] = {'path':str(f), 'date':timeFile}

        first = True
        for k in sorted(allFiles.keys(), reverse=True):
            print (k, ':', allFiles[k])
            if first:
                first = False


        #SendEmail('Дата последнего архива 11.11.11')


if __name__ == '__main__':
    main()
