# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс для работы с почтой
# P.S: - Говорят, русские — очень опасные, а этот вообще со всех сторон ненормальный.
#
#--------------------------------------------------------------------
import base64
import email
from imaplib import IMAP4_SSL
import quopri
from support import service_log
from support.utils import common_utils
from tests.MainClass import MainClass

__author__ = 'm.senchuk'


class Inbox(MainClass):

    #Имя и пароль для соединения с электронной почтой
    HOST = MainClass.ENV_MAIL_HOST
    LOGIN = MainClass.ENV_MAIL_LOGIN
    PASSWORD = MainClass.ENV_MAIL_PASS

    def get_email(self, get_emails='(UNSEEN)', to_email=None):
        """
        Получить сообщение из почтового ящика
        :param get_emails:
        :param to_email:
        :return:
        """
        emails = list()
        server = IMAP4_SSL(self.HOST)
        server.login(self.LOGIN, self.PASSWORD)
        server.select()
        result, data = server.search(None, get_emails)
        ids = data[0].split()
        for id in ids:
            result, unseen = server.fetch(id, "(RFC822)")
            raw_email = quopri.decodestring(unseen[0][1].encode('utf-8'))
            emails.append(self.parse_email(raw_email))
        if to_email is not None:
            tmp = [e_mail for e_mail in emails if e_mail["To"] == to_email]
            emails = tmp
        return emails

    @staticmethod
    def parse_email(raw_email):
        """
        Распарсить тело сообщения
        :param raw_email:
        :return:
        """
        tags = [
            'Date',
            'From',
            'To',
            'Message-ID',
            #'Subject',
            'Content-Type',
            'Content-Transfer-Encoding',
        ]
        parsed_email = dict()
        msg = email.message_from_string(raw_email)
        for tag in tags:
            service_log.put("Parsing '%s' ..." % tag)
            p = msg[tag]
            parsed_email.update({tag: p})
            service_log.put("Parsed '%s'" % tag)
        parsed_email.update({'Body': msg._payload})
        return parsed_email

    @staticmethod
    def build_subject(row_subject):
        """
        Собрать заголовок письма
        """
        service_log.put("Decoding 'Subject' ...")
        service_log.put("Subject value [%s]" % row_subject)
        subject = ''
        if '=?UTF-8?Q?' in row_subject.upper():
            subject = row_subject.upper().replace('=?UTF-8?Q?', '').replace('\r', '').replace('\n', '').\
                replace('?', '').replace('_', ' ').replace('/', '').replace('MIME-VERSION: 1.0', '')
        else:
            row_subject = row_subject.upper().replace('=?UTF-8?B?', '').replace('MIME-VERSION: 1.0', '')
            list_subj = row_subject.split(' ')
            for tmp in list_subj:
                service_log.put("Decoding [%s]" % tmp)
                try:
                    tmp = base64.b64decode(tmp)
                except Exception:
                    tmp = base64.b64decode(tmp+"=")
                subject += tmp
            subject = subject.replace('?', '')
        service_log.put("Decoded [%s]" % subject)
        return subject

    @staticmethod
    def decode_base64(data):
        """Decode base64, padding being optional.
        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.
        """
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += b'='* missing_padding
        return base64.decodestring(data)