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
import argparse
import sys
import configparser
from email.mime.text import MIMEText
from email.header import Header

progData =
mailSmtpServer  = 'smtp.yandex.ru:465'
mailFrom        = ''
mailPass        = ''
mailTo          = ''
mailSubject     = ''
pathBackup      = ''
fileLog         = 'log.txt'

strNotFoundPathBackup = 'Не найден каталог с архивными копиями: '+pathBackup

def log(str):
    str = ''+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+' '+str
    print(str)
    f = open(os.getcwd()+'\\'+fileLog, 'a')
    f.writelines('\r\n'+str)

def SendEmailLong(host, from_addr, pas, to_addr, subject, body_text):
    msg = MIMEText(body_text, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    try:
        server = smtplib.SMTP_SSL(host, 465, 10)
        server.login(from_addr, pas)
        server.sendmail(from_addr, [to_addr], msg.as_string())
    except:
        log('Ошибка оправки почты host='+host+' from_addr='+from_addr+' to_addr='+to_addr)
        log(abs[1].__doc__)
    finally:
        server.quit()

def SendEmail(body_text):
    log(body_text)
    SendEmailLong(mailSmtpServer, mailFrom, mailPass, mailTo, mailSubject, body_text)

def main():
    log('-------------------------')
    if not os.path.exists(pathBackup):
        SendEmail(strNotFoundPathBackup)
    else:
        # Перебираем файлы, сортируем по уменьшению даты
        # если размер предыдущего архива меньше, то отправляем письмо
        # если дата создания меньше текущей даты, то отправляем письмо

        allFiles = {}
        currentDirectory = pathlib.Path(pathBackup)
        for f in currentDirectory.iterdir():
            fileName = str(f)
            if os.path.isfile(fileName) :
                timeFile = time.gmtime(os.path.getctime(fileName))
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
                    SendEmail('Последний раз архивный файл \n'+
                        fileName+
                        ' был создан '+
                        time.strftime('%Y-%m-%d %H:%M:%S', dateFile)+
                        ' Необходимо проверить как создаются архивы.'
                    )

            # если размер предыдущего архива меньше, то отправляем письмо
            if dataOldFile != 0:
                sizeCurrentFile = os.path.getsize(fileName)
                fileNameOldFile = dataOldFile.get('path')
                sizeOldFile = os.path.getsize(fileNameOldFile)
                if sizeOldFile < sizeCurrentFile :
                    SendEmail('Размер файла \n'+
                        '('+str(sizeOldFile)+') байт '+fileNameOldFile +
                        '\n меньше чем предыдущего файла \n'+
                        '('+str(sizeCurrentFile)+') байт '+fileName +
                        '\nНеобходимо проверить как создаются архивы.'
                    )

            dataOldFile = dataFile

def createArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fileproperty')
    parser.add_argument('-s', '--smtpserver', default=mailSmtpServer)
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('-t', '--mailto')
    parser.add_argument('-su', '--subject')
    parser.add_argument('-pb', '--pathbackup')
    return parser

def loadPropertyFromFile(fileName):

    fullFileName = os.getcwd()+'\\'+fileName

    config = configparser.ConfigParser()
    section = 'settings'

    # если файл не существует, то создаем
    if not os.path.exists(fullFileName):
        config.set(section, 'smtpserver', mailSmtpServer)
        config.set(section, 'username', '')
        config.set(section, 'password', '')
        config.set(section, 'mailto', '')
        config.set(section, 'subject', '')
        config.set(section, 'pathbackup', '')
        with open(fullFileName, "w") as config_file:
            config.write(config_file)

    else:
        config.read(fullFileName)
        mailSmtpServer = config.get(section, 'smtpserver')
        mailFrom = config.get(section, 'username')
        mailPass = config.get(section, 'password')
        mailTo = config.get(section, 'mailto')
        mailSubject = config.get(section, 'subject')
        pathBackup = config.get(section, 'pathbackup')

if __name__ == '__main__':

    argPars = createArgParser()
    namespace = argPars.parse_args()

    if namespace.fileproperty:
        #Грузим настройки из файла
        loadPropertyFromFile(namespace.fileproperty)
    else:
        mailSmtpServer = namespace.smtpserver
        mailFrom = namespace.username
        mailPass = namespace.password
        mailTo = namespace.mailto
        mailSubject = namespace.subject
        pathBackup = namespace.pathbackup
    try:
        main()
    except:
        abs = sys.exc_info()
        log(abs[1].__doc__)
