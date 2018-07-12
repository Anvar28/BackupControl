#-------------------------------------------------------------------------------
# Name:        BackupControl
# Purpose:     Программа для проверки создания архивов.
#              По переданным параметрам проверяет в каталоге архивов
#              1. Когда был создан последний архив, если дата меньше текущего дня
#              то оправляет письмо
#              2. Проверяет размер архива по сравнению с прошлым архивом,  если
#              размер меньше, то опправляет письмо
#              3. Проверяет существует ли каталог архива, если нет, то оправляет письмо
#              4. Раз в неделю отправляет письмо для проверки связи
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
import datetime
import argparse
import sys
import configparser
import traceback
from email.mime.text import MIMEText
from email.header import Header
import inspect

class cDataProg:
    def __init__(self):
        self.mailSmtpServer  = 'smtp.yandex.ru:465'
        self.mailFrom        = ''
        self.mailPass        = ''
        self.mailTo          = ''
        self.mailSubject     = ''
        self.pathBackup      = ''
        self.fileLog         = 'log.txt'
        self.strNotFoundPathBackup = 'Не найден каталог с архивными копиями: {0}'.format(self.pathBackup)
        self.strMailSend = 'Отправлено письмо на адрес {0} с текстом \n {1}'
        self.strMailError = 'Ошибка оправки почты host={0}  from_addr={1}  to_addr={2}'
        self.strBackupFileOld = 'Последний раз архивный файл \n {0} был создан <b> {1} </b> \n Необходимо проверить как создаются архивы.'
        self.strBackupFileSmall = 'Размер файла \n({0}) байт {1} \n меньше чем предыдущего файла \n ({2}) байт {3} \n Необходимо проверить как создаются архивы.'
        self.strCheck = 'Проверка связи!'

dataProg = cDataProg()

def pathScript(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(pathScript)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

def log(str):
    str = ''+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+' '+str
    print(str)
    f = open(pathScript()+'\\'+dataProg.fileLog, 'a')
    f.writelines('\r\n'+str)

def SendEmailLong(host, from_addr, pas, to_addr, subject, body_text):
    msg = MIMEText(body_text, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    try:
        server = smtplib.SMTP_SSL(host, timeout=20)
        server.login(from_addr, pas)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        log(dataProg.strMailSend.format(to_addr, body_text))
    except Exception as e:
        log('----- Ошибка -----')
        log(dataProg.strMailError.format(host, from_addr, to_addr))
        log(str(e))
        log(traceback.format_exc)


def SendEmail(body_text):
    #log(body_text)
    SendEmailLong(
        dataProg.mailSmtpServer,
        dataProg.mailFrom,
        dataProg.mailPass,
        dataProg.mailTo,
        dataProg.mailSubject,
        body_text
    )

def main():
    log('-------------------------')
    if not os.path.exists(dataProg.pathBackup):
        SendEmail(dataProg.strNotFoundPathBackup)
    else:
        # Перебираем файлы, сортируем по уменьшению даты
        # если размер предыдущего архива меньше, то отправляем письмо
        # если дата создания меньше текущей даты, то отправляем письмо

        allFiles = {}
        currentDirectory = pathlib.Path(dataProg.pathBackup)
        for f in currentDirectory.iterdir():
            fileName = str(f)
            if os.path.isfile(fileName) :
                timeFile = time.localtime(os.path.getctime(fileName))
                strTimeFile = time.strftime('%Y-%m-%d-%H-%M-%S', timeFile)
                allFiles[strTimeFile] = {'path':fileName, 'date':timeFile}

        first = True
        currentTime = time.localtime()
        dataOldFile = 0

        for k in sorted(allFiles.keys(), reverse=True):
            dataFile = allFiles[k]
            #print(dataFile)
            dateFile = dataFile.get('date')
            fileName = dataFile.get('path')

            # если дата создания меньше текущей даты, то отправляем письмо
            if first:
                # если дата создания меньше текущей даты, то отправляем письмо
                first = False
                if (currentTime.tm_year != dateFile.tm_year or
                        currentTime.tm_mon != dateFile.tm_mon or
                        currentTime.tm_mday != dateFile.tm_mday):
                    SendEmail(
                        dataProg.strBackupFileOld.format(
                            fileName,
                            time.strftime('%Y-%m-%d %H:%M:%S', dateFile)
                        )
                    )

            # если размер предыдущего архива меньше, то отправляем письмо
            if dataOldFile != 0:
                sizeCurrentFile = os.path.getsize(fileName)
                fileNameOldFile = dataOldFile.get('path')
                sizeOldFile = os.path.getsize(fileNameOldFile)
                if sizeOldFile < sizeCurrentFile :
                    SendEmail(
                        dataProg.strBackupFileSmall.format(
                            str(sizeOldFile),
                            fileNameOldFile,
                            str(sizeCurrentFile),
                            fileName
                        )
                    )
                break


            dataOldFile = dataFile

def createArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fileproperty')
    parser.add_argument('-s', '--smtpserver', default=dataProg.mailSmtpServer)
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('-t', '--mailto')
    parser.add_argument('-su', '--subject')
    parser.add_argument('-pb', '--pathbackup')
    return parser

def loadPropertyFromFile(fileName):

    fullFileName = pathScript()+'\\'+fileName

    config = configparser.ConfigParser()
    section = 'settings'

    global dataProg

    # если файл не существует, то создаем
    if not os.path.exists(fullFileName):
        config.add_section(section)
        config.set(section, 'smtpserver', dataProg.mailSmtpServer)
        config.set(section, 'username', '')
        config.set(section, 'password', '')
        config.set(section, 'mailto', '')
        config.set(section, 'subject', '')
        config.set(section, 'pathbackup', '')
        with open(fullFileName, "w") as config_file:
            config.write(config_file)

    else:
        config.read(fullFileName)
        dataProg.mailSmtpServer = config.get(section, 'smtpserver')
        dataProg.mailFrom = config.get(section, 'username')
        dataProg.mailPass = config.get(section, 'password')
        dataProg.mailTo = config.get(section, 'mailto')
        dataProg.mailSubject = config.get(section, 'subject')
        dataProg.pathBackup = config.get(section, 'pathbackup')

if __name__ == '__main__':

    try:
        argPars = createArgParser()
        namespace = argPars.parse_args()

        if namespace.fileproperty:
            #Грузим настройки из файла
            loadPropertyFromFile(namespace.fileproperty)
        else:
            dataProg.mailSmtpServer = namespace.smtpserver
            dataProg.mailFrom = namespace.username
            dataProg.mailPass = namespace.password
            dataProg.mailTo = namespace.mailto
            dataProg.mailSubject = namespace.subject
            dataProg.pathBackup = namespace.pathbackup

        if datetime.datetime.today().isoweekday() == 1:
            SendEmail(self.strCheck)

        main()
    except Exception as e:
        log('----- Ошибка -----')
        log(str(e))
        log(traceback.format_exc())
