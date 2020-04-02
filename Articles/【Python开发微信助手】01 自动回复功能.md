> 引子：全国疫情已经好转了很多，可我还是困在老家无法复工，只得在家看些东西，码点代码保持状态。【`Python`开发微信助手】会是一个长期更新的系列，既然叫个人助手，那就需要满足不同的人的不同的需求。每个需求都会是一个独立的功能模块，代码中也会是模块化的开发。

### 需求背景

作为微信深度用户的我，经常会在认真工作的时候收到各种人发来的微信消息。关键是我这人吧，记性还不太好，处理完这些消息就忘了我要干啥了。

所以，模仿`QQ`的自动回复功能，我打算也做一个微信自动回复功能。一来不影响我的工作，二来也不会因为长时间没有回复或者匆匆回复让人家觉得不礼貌。

### 实现自动回复

公众号前面的文章讲了很多关于`Python`利用`ItChat`登录微信发送信息的例子，也有对应的代码，这篇文章就不再介绍`ItChat`这个库了。

首先新建一个主程序`main.py`，然后登录微信咯：

```Python
import itchat

itchat.auto_login(hotReload=True)
itchat.run()
```

登录微信之后就要开始监听微信消息了，通过监听可以获取发信人的`ID`，发信人的昵称以及发信的内容等：

```Python
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    sender = msg['User']['UserName'] if 'UserName' in msg['User'] else 'filehelper'
    nickname = msg['User']['NickName'] if 'NickName' in msg['User'] else 'filehelper'
    content = msg['Content']
```

再来分析一下自动回复这个功能。顾名思义，自动回复自然是要在别人发来消息之后自动回复给他一段固定的或者自定义的话，前面已经知道了发信人的`ID`，如果要回复固定的话就是这样：

```Python
itchat.send_msg('【自动回复】工作中，有事请留言！', sender)
```

或者自定义的：

```Python
itchat.send_msg('您的信息<{}>已收到，现在忙，稍后回复！'.format(content), sender)
```

个人比较倾向于后一种，把他发送的消息发回给他会让他知道我确实收到信息，只不过现在没时间处理。

下图中右侧为开启自动回复功能的测试账号（谢谢某位掘友提供的壁纸）：

![](https://user-gold-cdn.xitu.io/2020/3/6/170b04e3cd4978ea?w=1242&h=665&f=png&s=1026939)

### 自动回复升级

到这里，基本的自动回复就完成了，是不是很简单？

这时候就有人要说了：我也不是一直要工作啊，我要是没事的时候跟别人聊天一直弹出这个`【自动回复】工作中，有事请留言！`，即使我不烦，人家也要烦啊。

所以这个时候，除了关闭个人助手，还有一个方法就是给个人助手加一个**开关**。忙碌的时候打开开关，闲暇的时候关闭开关，让自己能方便地控制个人助手。

怎么做呢？只需要在主程序中增加一个全局变量，用这个全局变量控制自动回复功能的开启或关闭：

```Python
is_auto_reply = False

# 还需要在函数最开头声明这是一个全局变量
...
    global is_auto_reply
    ...
```

上面的代码表示自动回复功能默认是关闭的。那么，怎么改变它的状态呢？我们只需要给文件传输助手发送对应的命令。接着最上面的代码，在自动回复之前加入判断：

```Python
cmd = content.lstrip().rstrip()
if cmd == '开启自动回复':
    is_auto_reply = True
elif cmd == '关闭自动回复':
    is_auto_reply = False
```

通过两个指令`开启自动回复`和`关闭自动回复`，就能控制自动回复功能的开启和关闭。有时候可能发送的指令不太标准，所以在第一句中作了简单的预处理。

【本文来自微信公众号`Titus的小宇宙`，`ID`为`TitusCosmos`，转载请注明！】

【为了防止网上各种爬虫一通乱爬还故意删除原作者信息，故在文章中间加入作者信息，还望各位读者理解】

同时，像这样的控制指令，控制者往往希望个人助手执行命令之后有一些反馈，所以在更改功能开启状态之后，需要返回给控制者状态信息：

```Python
if cmd == '开启自动回复':
    is_auto_reply = True
    itchat.send_msg('已开启自动回复！', sender)
elif cmd == '关闭自动回复':
    is_auto_reply = False
    itchat.send_msg('已关闭自动回复！', sender)
```

最后，如果收到的信息不是控制指令，就要先判断自动回复功能是否开启，再决定是不是要自动回复：

```Python
# 接前面的代码
else:
    if is_auto_reply:
        itchat.send_msg('【自动回复】工作中，有事请留言！', sender)
        # 或者
        itchat.send_msg('您的信息<{}>已收到，现在忙，稍后回复！'.format(content), sender)
    else:
        pass
```

到这里，我们就成功地为自动回复功能加上了开关。

下图中右侧为开启自动回复功能的测试账号：

![](https://user-gold-cdn.xitu.io/2020/3/6/170b04f81f848b59?w=1242&h=1289&f=png&s=2409192)

### 自动回复再升级

可能有人觉得我这个自动回复的内容太古板了，能不能俏皮一些，或者说能不能在使用时自己自定义自动回复的内容呢？

当然可以！

与上面一样，增加一个全局变量，并声明：

```Python
custom_reply_content = '【自动回复】工作中，有事请留言！'

# 还需要在函数最开头声明这是一个全局变量
...
    global is_auto_reply, custom_reply_content
    ...
```

与前面一样，需要增加一个判断设置自动回复内容指令的语句。不同的是现在需要多输入一个自定义自动回复的内容，中间默认用中文逗号隔开：

```Python
# 假如收到的是：设置自动回复，现在在忙哦，可以的话稍后给你回复哟！
...
elif cmd.startswith('设置自动回复，'):
    custom_reply_content = content.replace('设置自动回复，', '')
    itchat.send_msg('自动回复内容已设置成功！', sender)
...
```

然后在自动回复中直接回复这个`custom_reply_content`就可以了。

同样，下图中右侧为开启自动回复功能的测试账号：

![](https://user-gold-cdn.xitu.io/2020/3/7/170b0bb5a45a094e?w=620&h=564&f=png&s=576847)

### 自动回复终极版

但是现在的版本还有一个致命的`bug`，那就是无论谁给你发上面那些控制指令都能生效，因为我们没有判断是不是你本人发来的信息。所以还需要在代码中限制，必须是文件传输助手或者你自己的微信发来的信息才判断是不是指令，代码如下：

```Python
if nickname == 'filehelper' or nickname == 'AdminNameToFillIn':
    cmd = content.lstrip().rstrip()
    if cmd == '开启自动回复':
        is_auto_reply = True
        itchat.send_msg('已开启自动回复！', sender)
    elif cmd == '关闭自动回复':
        is_auto_reply = False
        itchat.send_msg('已关闭自动回复！', sender)
    elif cmd.startswith('设置自动回复，'):
        custom_reply_content = content.replace('设置自动回复，', '')
        itchat.send_msg('自动回复内容已设置成功！', sender)
else:
    if is_auto_reply:
        itchat.send_msg('【自动回复】工作中，有事请留言！', sender)
        # 或者
        itchat.send_msg('您的信息<{}>已收到，现在忙，稍后回复！'.format(content), sender)
    else:
        pass
```

到这里，小助手才算是有了一个完整的自动回复功能。

### 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

下面是我的公众号，里面记载了一些我有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2020/3/7/170b0b521cad4cbd?w=304&h=112&f=png&s=43506)

![](https://user-gold-cdn.xitu.io/2020/3/7/170b0b5459f7f115?w=258&h=258&f=png&s=23703)
