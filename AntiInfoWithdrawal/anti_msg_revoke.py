import itchat
from itchat.content import *
import time
import copy

log = {}

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    # auto_reply = '您好,我现在有事不在,一会再和您联系。'
    # itchat.send_msg(auto_reply, msg['User']['UserName'])
    config = flush_friends()
    # itchat.send_msg(auto_reply, config['小帮帮'])
    cur_timestamp = time.time()
    del_overdue_msg(cur_timestamp)
    formatted_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cur_timestamp))
    # 为了程序的鲁棒性，避免因msg['User']没有'NickName'键而出错
    if 'NickName' in msg['User']:
        sender_name = msg['User']['NickName']
        if sender_name != 'filehelper':
            if sender_name not in log:
                log[sender_name] = {}
            content = str(msg['Text'])
            revoke_info = msg['Content']
            print('{}, {} 发来消息: {}'.format(formatted_timestamp, sender_name, content))
            target_msg_pattern = '"{}" 撤回了一条消息'.format(sender_name)
            if target_msg_pattern == content and msg['Type'] == 'Note' and str(msg['MsgType']) == '10002' and 'type="revokemsg"' in revoke_info:
                return_msg = ''
                return_msg_head = '{}，【{}】撤回了一条消息：\n'.format(formatted_timestamp, sender_name)
                revoke_msg_id = revoke_info.split('<msgid>')[-1].split('</msgid>')[0]
                for _, value in log[sender_name].items():
                    if value.split('|||')[0] == revoke_msg_id:
                        return_msg = value.split('|||')[1]
                if return_msg == '':
                    return_msg = '缓存信息列表为空！'
                return_msg = return_msg_head + return_msg
                print(return_msg)
                itchat.send_msg(return_msg, 'filehelper')
                # itchat.send_msg(return_msg, config['小帮帮'])
            else:
                log[sender_name][cur_timestamp] = msg['MsgId'] + '|||' + content


def del_overdue_msg(cur_timestamp):
    log_copy = copy.deepcopy(log)
    for friend in log_copy:
        for timestamp in log_copy[friend]:
            if cur_timestamp - timestamp > 2.01 * 60:
               log[friend].pop(timestamp)


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def file_reply(msg):
    is_group=False
    target = msg['User']['UserName']
    msg.download('./FileCache/' + msg.fileName)
    if is_group:
        sender_name = msg['ActualNickName'] if msg['ActualNickName'] != '' else msg['User']['Self']['NickName']
        # 消息来自于哪个群聊
        group_name = msg['User']['NickName']
        sender_name = '{} {}'.format(group_name, sender_name)
    else:
        sender_name = msg['User']['NickName'] if 'NickName' in msg['User'] else 'filehelper'
    if msg['Type'] == 'Picture':
        itchat.send_msg('{} send picture: '.format(sender_name), target)
        itchat.send_image('./FileCache/' + msg.fileName, target)
    elif msg['Type'] == 'Recording':
        msg.user.send('%s : %s' % (msg.type, msg.text))
        itchat.send_msg('{} send recording: '.format(sender_name), target)
        itchat.send_file('./FileCache/' + msg.fileName, target)
    elif msg['Type'] == 'Video':
        itchat.send_msg('{} send recording: '.format(sender_name), target)
        itchat.send_video('./FileCache/' + msg.fileName, target)
    else:
        itchat.send_msg('{} send file: '.format(sender_name), target)
        itchat.send_file('./FileCache/' + msg.fileName, target)


def flush_friends():
    config = {}
    friends = itchat.get_friends(update=True)
    for friend in friends:
        config[friend['NickName']] = friend['UserName']
    print('Load friends done.')
    return config


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    itchat.run()