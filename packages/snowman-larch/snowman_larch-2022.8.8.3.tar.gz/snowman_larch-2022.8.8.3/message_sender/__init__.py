from message_sender.message_config import MailConnectionConfig, ComWechatConnectionConfig
from message_sender.message_manager import MailMessageManager, ComWechatMessageManager

'''
from snowman_larch import MailMessageManager, MailConnectionConfig

msg_manager = MailMessageManager(MailConnectionConfig('18048587325@163.com', '********'))
_msg = {
    'subject': 'Snowman Larch 2022.8.8',
    'from': '18048587325@163.com',
    'receivers': ['1039614309@qq.com', '18048587325@163.com'],
    'msg': 'Snowman Notes has released Snowman Larch 2022.8.8!'
}
msg_manager.send_message(_msg)
'''