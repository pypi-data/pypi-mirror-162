import smtplib
import json
import requests

from abc import ABCMeta, abstractmethod, ABC


class MessageEngine(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, connect_config, *args, **kwargs):
        pass

    @abstractmethod
    def send(self, msg_body, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def close(self, *args, **kwargs):
        pass


class MailMessageEngine(MessageEngine, ABC):
    """mail message engine, now support 163.com"""

    user_name = None

    def __init__(self):
        self.__conn = None

    def connect(self, connect_config, **kwargs):
        try:
            host = getattr(connect_config, 'host', None) or connect_config.get('host', '')
            port = getattr(connect_config, 'port', None) or connect_config.get('port', '')
            self.user_name = getattr(connect_config, 'user_name', None) or connect_config.get('user_name', '')
            auth_code = getattr(connect_config, 'auth_code', None) or connect_config.get('auth_code', '')
            self.__conn = smtplib.SMTP()
            self.__conn.connect(host, port)
            self.__conn.login(self.user_name, auth_code)
            return True
        except ConnectionRefusedError as e:
            raise ConnectionError(e)

    def send(self, msg_body, *args, **kwargs):

        try:
            from_addr = msg_body.get('from_addr', self.user_name)
            to_addr = msg_body.get('receiver')
            msg = msg_body.get('msg', '')
            msg['to'] = to_addr
            self.__conn.sendmail(from_addr, to_addr, msg.as_string())
        except ConnectionError as e:
            raise ConnectionError(e)

    def close(self, *args, **kwargs):
        try:
            self.__conn.quit()
        finally:
            self.__conn = None


class ComWechatMessageEngine(MessageEngine):
    """comWechat message engine."""
    send_message_url = None

    def connect(self, connect_config, *args, **kwargs):
        """require token"""
        corpid = getattr(connect_config, 'corpid') or connect_config.get('corpid', '')
        corp_secret = getattr(connect_config, 'corp_secret') or connect_config.get('corp_secret', '')
        get_token_url = getattr(connect_config, 'get_token_url') or connect_config.get('get_token_url', '')
        send_message_url = getattr(connect_config, 'send_message_url') or connect_config.get('send_message_url', '')
        params = {
            "corpid": corpid,
            "corpsecret": corp_secret
        }
        try:
            res = requests.get(url=get_token_url, params=params, verify=True)
            res_json = res.json()
            if res_json['errcode'] != 0:
                raise ConnectionError(f'failed to get token response, {str(res_json)}')
            token = res_json['access_token']
            self.send_message_url = f"{send_message_url}?access_token=%s" % token
        except Exception as e:
            raise ConnectionError(f'failed to get token response, {e}')

    def send(self, msg_body, *args, **kwargs):
        agentid = msg_body.get('agent_id', '')
        content = msg_body.get('content', '')
        receiver = msg_body.get('receiver', '')
        data = {
            # "toparty": "10",
            "touser": receiver,
            "msgtype": "text",
            "agentid": agentid,
            "text": {"content": content},
            "safe": "0"
        }
        res = requests.post(url=self.send_message_url, data=json.dumps(data))
        res_json = res.json()
        if res_json['errcode'] != 0:
            raise RuntimeError('failed to send message, %s' % res_json)
        return True

    def close(self, *args, **kwargs):
        pass
