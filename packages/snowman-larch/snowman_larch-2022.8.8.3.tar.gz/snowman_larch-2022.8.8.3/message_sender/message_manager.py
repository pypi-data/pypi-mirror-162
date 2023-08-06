from abc import ABCMeta
from message_sender.message_engine import MailMessageEngine, ComWechatMessageEngine
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MessageManager(metaclass=ABCMeta):

    def __init__(self, connection_config):
        self._receivers = []
        self.connection_config = connection_config

    def append_receiver(self, receiver):
        self._receivers.append(receiver)

    def send_message(self, receivers, msg, **kwargs):
        self._receivers = self._receivers + receivers
        raise NotImplementedError


class MailMessageManager(MessageManager):

    def send_message(self, msg_body, **kwargs):
        msg = MIMEMultipart()
        msg['Subject'] = getattr(msg_body, 'subject', '') or msg_body.get('subject', '')
        msg['from'] = getattr(msg_body, 'from', '') or msg_body.get('from', '')
        body = getattr(msg_body, 'msg', '') or msg_body.get('msg', '')
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if not msg_body:
            raise ValueError('msg_body is empty.')

        self._receivers = msg_body.get('receivers', [])

        # connect
        message_engine = MailMessageEngine()
        message_engine.connect(self.connection_config)

        # send message
        for receiver in self._receivers:
            _msg_body = {
                'receiver': receiver,
                'msg': msg
            }
            # msg['Cc'] = getattr(msg_body, 'cc', '...@163.com') or msg_body.get('cc', '')
            message_engine.send(_msg_body)

        # close
        message_engine.close()


class ComWechatMessageManager(MessageManager):

    def send_message(self, msg_body, **kwargs):

        if not msg_body:
            raise ValueError('msg_body is empty.')

        self._receivers = msg_body.get('receivers', [])

        message_engine = ComWechatMessageEngine()
        message_engine.connect(self.connection_config)
        for receiver in self._receivers:
            _msg_body = {
                'receiver': receiver,
                'content':  msg_body.get('msg', '')
            }
            message_engine.send(_msg_body)
            message_engine.close()
