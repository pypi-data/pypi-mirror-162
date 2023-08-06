from abc import ABCMeta


class ConnectionConfig(metaclass=ABCMeta):
    pass


class MessageBody(metaclass=ABCMeta):
    pass


# ----------------------------connection config----------------------------
class MailConnectionConfig(ConnectionConfig):

    def __init__(self, user_name, auth_code, host='smtp.163.com', port=25, **kwargs):
        self.host = host
        self.port = port
        self.user_name = user_name
        self.auth_code = auth_code


class ComWechatConnectionConfig(ConnectionConfig):

    def __init__(self, corpid, corp_secret, get_token_url=None, send_message_url=None):
        if not get_token_url:
            self.get_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        if not send_message_url:
            self.send_message_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        self.corpid = corpid
        self.corp_secret = corp_secret


# ----------------------------message config----------------------------
class MailMessageBody(MessageBody):
    pass


class ComWechatBody(MessageBody):
    pass
