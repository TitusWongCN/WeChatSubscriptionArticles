> 上一期我们整理好了撤回消息文本，现在可以把它们转发给“文件传输助手”了。

### `ItChat`获取好友信息

前面讲过，`ItChat`能很方便的处理朋友发来的微信消息。这里要讲的是，`ItChat`还能更方便给朋友发送微信消息。

要给朋友发消息，很自然的，我们必须知道是给哪位朋友发送什么消息。

消息的内容可以自己定义。至于怎么确定是哪位朋友，就需要在接收到消息的时候从`msg`对象中分析了，这样做的缺点是只能在这位朋友发来消息之后才能给他回复消息。更高级一点的发送消息的方式是提前获取好友的`UserName`代码，然后就可以随时根据某个好友对应的代码给他发送消息了。

`ItChat`有提供一个方法，能让我们知道所有好友的具体信息，其中就包括前面提到的`UserName`和`NickName`信息：

```python
friends = itchat.get_friends(update=True)
```

加上`update`参数之后可以动态刷新朋友列表，这样也能获取到新加的朋友的信息。

获取到所有好友的信息之后就能获取对应的信息了，代码如下：

```python
def flush_friends():
    config = {}
    friends = itchat.get_friends(update=True)
    for friend in friends:
        config[friend['NickName']] = friend['UserName']
    print('Load friends done.')
    return config
```

所有好友的昵称的编码都在`config`里面了，需要给谁发信息直接从这个对象里面找即可。

### `ItChat`发送消息

我们可以通过一个例子来学习通过`ItChat`发送消息。

玩过`QQ`的同学都知道，`QQ`有一个自动回复的功能，如果状态是离开状态，好友发来消息会自动回复`您好,我现在有事不在,一会再和您联系。`。我们就在微信中实现自动回复：

```python
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    auto_reply = '您好,我现在有事不在,一会再和您联系。'
    itchat.send_msg(auto_reply, msg['User']['UserName'])
```

效果如下：

![](https://user-gold-cdn.xitu.io/2020/1/3/16f66fcd61b085ed?w=1242&h=796&f=png&s=211216)

再来试一试高级玩法：

```python
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    auto_reply = '您好,我现在有事不在,一会再和您联系。'
    # itchat.send_msg(auto_reply, msg['User']['UserName'])
    config = flush_friends()
    itchat.send_msg(auto_reply, config['小帮帮'])
```

为了便于演示，还是写在`text_reply`方法中。不同的是，给“文件传输助手”发送消息来触发事件，而我们却自动回复给机器人“小帮帮”。效果如下：

![](https://user-gold-cdn.xitu.io/2020/1/3/16f66fd1a99ea179?w=1242&h=588&f=png&s=143693)

![](https://user-gold-cdn.xitu.io/2020/1/3/16f66fd69a70efa9?w=1242&h=1159&f=png&s=389838)


### 发送被撤回消息

有了前面的基础，这一步就非常简单了。唯一跟前面不同的是，微信里“文件传输助手”默认是作为一个好友的，这位好友的代码是`filehelper`，不要改变大小写。

前面已经拿到了整理好的被撤回消息`return_msg `，现在可以发送给`filehelper`了：

```python
itchat.send_msg(return_msg, 'filehelper')
```

就一句代码，是不是非常`easy`。下面是效果：

![](https://user-gold-cdn.xitu.io/2020/1/3/16f66ff4bd5b182e?w=1242&h=1299&f=png&s=560075)

![](https://user-gold-cdn.xitu.io/2020/1/3/16f66ff7b1a6010e?w=1242&h=1262&f=png&s=511754)

![](https://user-gold-cdn.xitu.io/2020/1/3/16f66ff963578ea1?w=1242&h=971&f=png&s=289028)

### 系列结语

`Python`有很多好用好玩的库，可以慢慢发掘。本期我们利用`ItChat`库编写了一个微信防撤回脚本。其实`ItChat`功能远远不止这些，它还可以处理微信群消息以及各种其他类型的消息，我们讲到的只是九牛一毛，更多的还要大家自己去探索。

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

下面是我的公众号，有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2020/1/3/16f670612b1b7199?w=304&h=112&f=png&s=41105)

![](https://user-gold-cdn.xitu.io/2020/1/3/16f67062e5fca8e4?w=258&h=258&f=png&s=20814)