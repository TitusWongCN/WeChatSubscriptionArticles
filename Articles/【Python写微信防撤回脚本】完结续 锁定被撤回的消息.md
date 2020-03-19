> 这个系列文章里曾经说过，如果好友短时间发送多条消息然后撤回会难以判断究竟撤回的是哪条信息，只能靠猜。后来我觉得“猜”这个事情特别不`Pythonic`，研究一段时间后找到了解决方案，不得不惊叹`ItChat`真的好强大。

### 之前的解决方案

之前的不能确定的情况大概是这样：短时间内同一位好友发送了多条消息，当他随便撤回一条消息时，我们不能确定他到底撤回的到底是哪一条消息。只能猜他可能是撤回了最近的一条消息，然后将其他消息贴出来作为备选。代码如下：

```python
target_msg_pattern = '"{}" 撤回了一条消息'.format(sender_name)
if content == target_msg_pattern:
    return_msg = '【{}】撤回了一条消息：\n'.format(sender_name)
    if len(log[sender_name].items()) == 0:
        return_msg = '缓存信息列表为空！'
    else:
        return_msg += log[sender_name].items()[-1][-1] + '\n'
        if len(log[sender_name].items()) > 1:
            msgs = [msg for timestamp, msg in log[sender_name].items()[:-1]]
            return_msg += '也有可能是下列信息中的某一条：\n' + '\n'.join(msgs)
```

实际效果是这样：

![](https://user-gold-cdn.xitu.io/2020/1/4/16f6c34d31965240?w=470&h=211&f=png&s=65861)

我这个强迫症简直受不了这么不确定的说法。

### 分析`msg`信息

要想确定撤回了哪一条信息，就必须先熟悉普通`msg`和撤回的`msg`里面都有哪些信息，他们的相同点和不同点。下面就来看看这两种情况下`msg`都是怎么样的，不需要仔细的看每一行，后面会作具体分析。

先是用机器人“小帮帮”发送过来的信息得到的`msg`信息：

```python
{
	'MsgId': '2018511155698964390',
	'FromUserName': '@**********f511363f8200853d724137bb31236a7ea81e5183cc06cb4ec978e3',
	'ToUserName': '@**********c2e61fdb47b5c241553a2f',
	'MsgType': 1,
	'Content': 'msg里面到底有什么？',
	'Status': 3,
	'ImgStatus': 1,
	'CreateTime': 1578069291,
	'VoiceLength': 0,
	'PlayLength': 0,
	'FileName': '',
	'FileSize': '',
	'MediaId': '',
	'Url': '',
	'AppMsgType': 0,
	'StatusNotifyCode': 0,
	'StatusNotifyUserName': '',
	'RecommendInfo': {
		'UserName': '',
		'NickName': '',
		'QQNum': 0,
		'Province': '',
		'City': '',
		'Content': '',
		'Signature': '',
		'Alias': '',
		'Scene': 0,
		'VerifyFlag': 0,
		'AttrStatus': 0,
		'Sex': 0,
		'Ticket': '',
		'OpCode': 0
	},
	'ForwardFlag': 0,
	'AppInfo': {
		'AppID': '',
		'Type': 0
	},
	'HasProductId': 0,
	'Ticket': '',
	'ImgHeight': 0,
	'ImgWidth': 0,
	'SubMsgType': 0,
	'NewMsgId': 2018511155698964390,
	'OriContent': '',
	'EncryFileName': '',
	'User': < User: {
		'MemberList': < ContactList: [] > ,
		'Uin': 0,
		'UserName': '@**********f511363f8200853d724137bb31236a7ea81e5183cc06cb4ec978e3',
		'NickName': '小帮帮',
		'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=699837854&username=@**********f511363f8200853d724137bb31236a7ea81e5183cc06cb4ec978e3&skey=@crypt_****c00c_92668c8ba7d285c221a85e**********',
		'ContactFlag': 2049,
		'MemberCount': 0,
		'RemarkName': '小帮帮',
		'HideInputBarFlag': 0,
		'Sex': 2,
		'Signature': '',
		'VerifyFlag': 0,
		'OwnerUin': 0,
		'PYInitial': 'XBB',
		'PYQuanPin': 'xiaobangbang',
		'RemarkPYInitial': 'XBB',
		'RemarkPYQuanPin': 'xiaobangbang',
		'StarFriend': 0,
		'AppAccountFlag': 0,
		'Statues': 0,
		'AttrStatus': 33658937,
		'Province': '浙江',
		'City': '台州',
		'Alias': '',
		'SnsFlag': 17,
		'UniFriend': 0,
		'DisplayName': '',
		'ChatRoomId': 0,
		'KeyWord': '',
		'EncryChatRoomId': '',
		'IsOwner': 0
	} > ,
	'Type': 'Text',
	'Text': 'msg里面到底有什么？'
}
```

下面是机器人撤回刚才的信息得到的msg信息：

```python
{
	'MsgId': '4056955577161654067',
	'FromUserName': '@**********f511363f8200853d724137bb31236a7ea81e5183cc06cb4ec978e3',
	'ToUserName': '@**********c2e61fdb47b5c241553a2f',
	'MsgType': 10002,
	'Content': '<sysmsg type="revokemsg"><revokemsg><session>wxid_4gngrr04aqjn21</session><oldmsgid>1123721956</oldmsgid><msgid>2018511155698964390</msgid><replacemsg><![CDATA["小帮帮" 撤回了一条消息]]></replacemsg></revokemsg></sysmsg>',
	'Status': 4,
	'ImgStatus': 1,
	'CreateTime': 1578069381,
	'VoiceLength': 0,
	'PlayLength': 0,
	'FileName': '',
	'FileSize': '',
	'MediaId': '',
	'Url': '',
	'AppMsgType': 0,
	'StatusNotifyCode': 0,
	'StatusNotifyUserName': '',
	'RecommendInfo': {
		'UserName': '',
		'NickName': '',
		'QQNum': 0,
		'Province': '',
		'City': '',
		'Content': '',
		'Signature': '',
		'Alias': '',
		'Scene': 0,
		'VerifyFlag': 0,
		'AttrStatus': 0,
		'Sex': 0,
		'Ticket': '',
		'OpCode': 0
	},
	'ForwardFlag': 0,
	'AppInfo': {
		'AppID': '',
		'Type': 0
	},
	'HasProductId': 0,
	'Ticket': '',
	'ImgHeight': 0,
	'ImgWidth': 0,
	'SubMsgType': 0,
	'NewMsgId': 4056955577161654067,
	'OriContent': '',
	'EncryFileName': '',
	'User': < User: {
		'MemberList': < ContactList: [] > ,
		'Uin': 0,
		'UserName': '@**********f511363f8200853d724137bb31236a7ea81e5183cc06cb4ec978e3',
		'NickName': '小帮帮',
		'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=699837854&username=@**********f511363f8200853d724137bb31236a7ea81e5183cc06cb4ec978e3&skey=@crypt_****c00c_92668c8ba7d285c221a85e**********',
		'ContactFlag': 2049,
		'MemberCount': 0,
		'RemarkName': '小帮帮',
		'HideInputBarFlag': 0,
		'Sex': 2,
		'Signature': '',
		'VerifyFlag': 0,
		'OwnerUin': 0,
		'PYInitial': 'XBB',
		'PYQuanPin': 'xiaobangbang',
		'RemarkPYInitial': 'XBB',
		'RemarkPYQuanPin': 'xiaobangbang',
		'StarFriend': 0,
		'AppAccountFlag': 0,
		'Statues': 0,
		'AttrStatus': 33658937,
		'Province': '浙江',
		'City': '台州',
		'Alias': '',
		'SnsFlag': 17,
		'UniFriend': 0,
		'DisplayName': '',
		'ChatRoomId': 0,
		'KeyWord': '',
		'EncryChatRoomId': '',
		'IsOwner': 0
	} > ,
	'Type': 'Note',
	'Text': '"小帮帮" 撤回了一条消息'
}
```

得到了两种类型的`msg`，下面是对比（高亮的部分是不同处，省略了部分相同内容。可以点击放大查看大图）：

![](https://user-gold-cdn.xitu.io/2020/1/4/16f6e6338a761d4d?w=821&h=727&f=png&s=79437)

现在来分析几条关键信息：

- MsgId（与下面的NewMsgId同）

    消息编号。这个很好理解，每条消息都是通过一个独一无二的编号来与其他消息区分，所以这两条消息的编号不同很正常。如果我们能拿到好友撤回消息的编号，也就能锁定这条消息了。

- MsgType（与下面的Type同）

    消息类型。如下图，左边是普通的对话消息，右边类似于系统提示消息。是不是可以根据这条信息来判断是不是有好友撤回了消息？
    
    ![](https://user-gold-cdn.xitu.io/2020/1/4/16f6e70257a48b33?w=960&h=464&f=png&s=203436)
    
    ![](https://user-gold-cdn.xitu.io/2020/1/4/16f6e719e2de0048?w=959&h=377&f=png&s=159728)

- Content

    消息内容，注意与下面的`Text`区分，这两种消息类型在内容上最大的区别可能就在这里了。
    
    来看一下撤回消息的`Content`是怎么样的（为了便于查看，已经经过格式化）：
    
    ```xml
    <sysmsg type="revokemsg">
        <revokemsg>
            <session>wxid_4gngrr04aqjn21</session>
            <oldmsgid>1123721956</oldmsgid>
            <msgid>2018511155698964390</msgid>
            <replacemsg><![CDATA["小帮帮" 撤回了一条消息]]></replacemsg>
        </revokemsg>
    </sysmsg>
    ```
    
    一眼就能发现关键点：撤回的那条消息属于系统消息（`sysmsg`），类型是撤回消息（`revokemsg`），对应的消息编号是`2018511155698964390`。
    
    细心的读者已经发现，这个消息编号正好就是左边那条消息的编号。
    
    通过这个推理，猜测`Content`字段是系统内部传输的内容，而`Text`字段则是用户看到的内容。

### 确定消息类型

根据上述分析，有三个地方帮助确定收到的某条信息是否是撤回的消息：

1. MsgType

    是`1`就是普通消息，是`10002`则可能为撤回消息。

2. Content

    如果Content里有包含`type="revokemsg"`则可能为撤回消息，否则不是撤回消息。

3. Type

    是`Text`就是普通消息，是`Note`则可能为撤回消息。

精确起见，消息还要同时满足上面三种情况才可认定为撤回消息。

### 锁定撤回的消息

由于要锁定撤回消息必须要`MsgId`才能确定，所以在存储临时消息时需要加上这一字段。

```python
log[sender_name][cur_timestamp] = msg['MsgId'] + '|||' + content
```

为了简化数据复杂度，我通过分隔符`|||`直接把`MsgId`加在前面。

于是，锁定并发送撤回消息的代码就时这样：

```python
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
```

测试一下，为便于查看，将撤回提醒直接发给机器人“小帮帮”（掘金上不会上传动图，需要看动图版本的可以到[这里](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000197&idx=1&sn=842927099123460085c3e49e12c38a3d&chksm=6a4bda055d3c5313dc586d8558670c9d1bfe2486c8abaf2885dffede502c7811c3259281a732#rd)）：

![](https://user-gold-cdn.xitu.io/2020/1/4/16f6ece89ee41c98?w=544&h=960&f=png&s=600799)

一个完美的微信防撤回脚本大功告成！

### 结语

Python有很多好用好玩的库，可以慢慢发掘。本期我们利用ItChat库编写了一个微信防撤回脚本。其实ItChat功能远远不止这些，它还可以处理微信群消息以及各种其他类型的消息，我们讲到的只是九牛一毛，更多的还要大家自己去探索。

这个系列就到此为止了，如果有想要了解交流的可以在公众号主页联系我，这个系列的代码在这里：

```html
https://github.com/TitusWongCN/AntiInfoWithdrawal
```

大家有什么想了解的，或者有什么想做的也可以在文章后面留言，后面说不定就会做了哦~

### 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

---

【Python写微信防撤回脚本】往期推荐：

第一期：[【Python写微信防撤回脚本】01 熟悉ItChat库](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000174&idx=1&sn=89f0ab38943b35dac7cca07823562542&chksm=6a4bda6e5d3c5378c04d513cc25a26af95c14cade2bdd64967d2099229594fb9a10b5a9b2343#rd)

第二期：[【Python写微信防撤回脚本】02 接收记录聊天信息](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000182&idx=1&sn=41940b0310d7037f9315082972f4ebae&chksm=6a4bda765d3c53601193bf365c528cd4ad56293db400f7b0e6daf61a7b120e09d53949b967ee#rd)

第三期：[【Python写微信防撤回脚本】03 获取撤回信息并整理](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000187&idx=1&sn=0cd773ac90c382eb0f96ec3b6dcb06da&chksm=6a4bda7b5d3c536de94f20228a6702b1d5faf472920978f50a1e9921ac9d3d2ec7f6a1b86bdf#rd)

第四期：[【Python写微信防撤回脚本】04完结 发送被撤回消息](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000190&idx=1&sn=774e19ce3a288d152ef26e30525face7&chksm=6a4bda7e5d3c53681ff7f59b39fbef4af9477196d7ba717e27faf26334f4059d6b23221aeec6#rd)

下面是我的公众号，有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2020/1/4/16f6eafbafc6ce1a?w=304&h=112&f=png&s=41105)
![](https://user-gold-cdn.xitu.io/2020/1/4/16f6eaffd55288e9?w=258&h=258&f=png&s=20814)