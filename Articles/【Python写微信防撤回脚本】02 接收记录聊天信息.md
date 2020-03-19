> 上一期我们安装好了`ItChat`，并且学会用它登录微信。想知道它还能做什么？往下滑吧~

### 接收好友信息

利用`ItChat`登录微信之后，我们就可以自动记录好友发来的信息。

话不多说，直接上代码：

```python
import itchat
from itchat.content import TEXT

@itchat.msg_register([TEXT])
def text_reply(msg):
    # 谁, 发了什么消息
    sender_name = msg['User']['NickName']
    content = str(msg['Text'])
    print('{} 发给你一条消息: {}'.format(sender_name, content))
```

运行之后，如果有好友发送信息，控制台会输出类似下面的信息：

![](https://user-gold-cdn.xitu.io/2019/12/30/16f5738328709682?w=309&h=27&f=png&s=1909)

想要自动记录好友发来的信息，就必须先注册一个方法，并用`itchat.msg_register()`装饰它。注意，要接收文本信息，必须给这个装饰器传入`[TEXT]`这样的参数。

当好友发来消息会自动进入`text_reply`方法，这条消息的所有信息都在`msg`对象里。如代码所示，发送者的昵称、发送的内容都可以从这个对象中取出。最后程序会在命令提示符中打印出格式为“谁给你发了一条什么样的信息”的信息。

但是当好友发来的消息不是纯文本，上面的代码是无法捕获的。好在强大的`ItChat`不只是支持接收文本信息，还能接收图片、分享的链接、位置等各种消息类型。只需要像下面一样声明，就可以自动接收其他种类的信息：

```python
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    pass
```

当然，如果要支持其他类型的消息，还要提前把这些消息类型引入：

```python
from itchat.content import TEXT, MAP, CARD, NOTE, SHARING
```

或者想偷懒也可以像我这样不管三七二十一，一股脑儿全部导入：

```python
from itchat.content import *
```

这样，好友发的大多数种类的消息都能进入我们的代码。进入代码之后，我们能做的就多了。比如这时好友分享给我一篇文章，代码就能捕获并在控制台输出：

![](https://user-gold-cdn.xitu.io/2019/12/30/16f573d8fb52ac36?w=474&h=27&f=png&s=2954)

当然，`msg`对象里面还有对应的网址信息，有兴趣的同学可以自己去探索。

### 缓存好友信息

由于我们的需求只是缓存近几分钟好友发过来的信息，没有必要用到那些专业的数据库，甚至没必要存储到本地文件中，反而一个简单的字典就能满足要求。

有时候我们会利用“文件传输助手”传输信息，这部分信息我们是不关心的，代码要能处理这种例外。代码如下：

```python
import itchat
from itchat.content import *
import time

log = {}

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    timestamp = time.time()
    formatted_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    # 为了程序的鲁棒性，避免因msg['User']没有'NickName'键而出错
    if 'NickName' in msg['User']:
        sender_name = msg['User']['NickName']
        if sender_name != 'filehelper':
            content = str(msg['Text'])
            print('{}, {} 发来消息: {}'.format(formatted_timestamp, sender_name, content))
            if sender_name not in log:
                log[sender_name] = {}
            log[sender_name][timestamp] = content
```

简单的讲解一下上面的代码。

1. 首先需要初始化一个全局的消息日志字典——`log`。字典的每一个键都是发来信息的好友的昵称，它的值也是一个字典。这个字典则是以接收到消息那一刻的时间戳为键，以该时间戳对应的信息内容为值。这样设计便于后面找到撤回的消息。
2. 有的消息可能没有`NickName`键的，为了增加程序的鲁棒性，要提前对`msg['User']`进行判断。
3. 判断是否是`文件传输助手(filehelper)`，如果不判断，会报下面的错：

![](https://user-gold-cdn.xitu.io/2019/12/30/16f5741cb03097f4?w=889&h=126&f=png&s=17008)

4. 如果某个好友第一次发信息过来，日志字典里面是没有这个键的。直接插入字典会出错，所以要先判断键是否已存在。

这时我们来测试一下。先用一个账号给自己发一条消息：

![](https://user-gold-cdn.xitu.io/2019/12/30/16f5747562f84e52?w=1242&h=2208&f=png&s=978480)

然后撤回：

![](https://user-gold-cdn.xitu.io/2019/12/30/16f5747a6e5492e5?w=1242&h=2208&f=png&s=945921)

同时，控制台输出：

![](https://user-gold-cdn.xitu.io/2019/12/30/16f5748457fcf17f?w=501&h=44&f=png&s=5165)

### 下期预告

在上面举的例子中，我们很容易就能知道被撤回的消息的内容是什么。但是这样需要我们一条一条的看，这也太累了吧。

作为一名程序员，怎么能允许自己活的那么累呢！所以下期我们就来看看如何自动判断是否是撤回的消息，并将撤回的消息自动发送给“文件传输助手”上。

### 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```python
https://github.com/TitusWongCN/
```

---

【Python写微信防撤回脚本】往期推荐：

第一期： [【Python写微信防撤回脚本】01 熟悉ItChat库](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000174&idx=1&sn=89f0ab38943b35dac7cca07823562542&chksm=6a4bda6e5d3c5378c04d513cc25a26af95c14cade2bdd64967d2099229594fb9a10b5a9b2343#rd)


下面是我的公众号，有兴趣可以扫一下：


![](https://user-gold-cdn.xitu.io/2019/12/30/16f574d3f958c41d?w=304&h=112&f=png&s=41105)


![](https://user-gold-cdn.xitu.io/2019/12/30/16f574ea458c11d7?w=258&h=258&f=png&s=20814)