
> 不知道昨天大家是怎么跨年的，反正我吃的不错。看着我懒散的肚皮瘫在那里，想起`2019`年初给自己订的锻炼计划几乎没怎么执行过，我又重重的在`2020`年的计划里写下了坚持每周锻炼`4`次的宏伟目标。哈哈，往者不可谏，来者犹可追。新的一年，祝大家工作生活都顺利。

> 这篇不是总结文，题外话不多说。上一期我们知道怎么记录好友发来的信息，这里我们来看看怎么知道哪些消息是被撤回的，并且把它们转发给“文件传输助手”。

### 优化缓存机制

前面我们把好友发来的所有信息都存入到一个叫`log`的字典对象中，以免错过好友的任何一条信息。但是这么多信息都存储在里面，没有办法一条条的去分析到底是不是被撤回的信息，必须想办法把有用的信息挑选出来。

值得一提的是，微信撤回机制有一个规则，用户只能撤回`2`分钟内自己发出去的消息。所以相对每次接收到信息的时刻，`log`中`2`分钟以前的信息是不能被撤回的。这些信息属于无用信息，完全可以删除，也避免了信息内容过多无法分析和程序运行效率因信息占用过多内存而降低的问题。

删除的方法也很简单，因为好友的每一条信息的键都是接收到该信息时刻的时间戳，这也是前面这样设计的原因：

> 这个字典则是以接收到消息那一刻的时间戳为键，以该时间戳对应的信息内容为值。这样设计便于后面找到撤回的消息。

```python
import copy

def del_overdue_msg(cur_timestamp):
    log_copy = copy.deepcopy(log)
    for friend in log_copy:
        for timestamp in log_copy[friend]:
            if cur_timestamp - timestamp > 2.01 * 60:
               log[friend].pop(timestamp)
```

因为不能在循环字典的时候对其进行更改，所以先`copy`一份，然后处理，注意要引入`copy`包。代码中设计的时间间隔为`2.01`分钟，是为了留出一定的`Buffer`，避免因程序运行原因导致错过什么消息。为了简化代码，把这段代码拿出来写到一个独立的方法中，然后在每次接收到消息时调用它。

```python
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    cur_timestamp = time.time()
    del_overdue_msg(cur_timestamp)
    ...
```

### 生成撤回信息

当好友撤回已经发送的消息时，也会进入我们的程序，就像前面控制台的截图：

![](https://user-gold-cdn.xitu.io/2020/1/1/16f60da64b6c7a47?w=501&h=44&f=png&s=27085)

此时程序判断的消息发送者就是撤回消息的好友昵称，而消息的格式则是固定的：

```python
msg_pattern = '"{}" 撤回了一条消息'.format(sender_name)
```

如果接收到的消息内容符合这个格式，就能确定某个好友撤回了消息（不考虑好友故意发送同样的信息的情况，这个真处理不了）。

但是可能该好友短时间连续发了多条消息，怎么确定是哪一条呢？目前我了解到的，有多条临时存储的消息的情况是不能唯一确定被撤回的是哪一条信息的。不过从逻辑上讲，一般被撤回的消息大概率都是最新的一条。在不确定的情况下，可以先显示最新的一条，其余消息在后面作为备选。

还有一个要注意的点。好友有可能会连续撤回好几条消息，所以程序中已经作为撤回消息返回的部分还不能立即从内存中删除，避免找不到真正撤回的消息。在整个处理过程中，临时存储的消息只会在前面说的“`2`分钟”的逻辑下才会被删除。

有了策略，就可以开始撸代码了：

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

下面是实际效果：

- 机器人“小帮帮”发过来一条消息：

![](https://user-gold-cdn.xitu.io/2020/1/1/16f610cd374a6ec7?w=1242&h=615&f=png&s=159884)

- 控制台给出输出：

![](https://user-gold-cdn.xitu.io/2020/1/1/16f610bb3766ded6?w=526&h=48&f=png&s=5063)

- 机器人撤回消息：

![](https://user-gold-cdn.xitu.io/2020/1/1/16f610e4c2e35c3e?w=1242&h=586&f=png&s=109997)

- 控制台给出撤回的信息内容：

![](https://user-gold-cdn.xitu.io/2020/1/1/16f610c4407d54c0?w=470&h=111&f=png&s=9775)

如果是连续的多条消息，则是这样的：

- 收到信息
 
![](https://user-gold-cdn.xitu.io/2020/1/1/16f612136ae5ca4e?w=1242&h=913&f=png&s=336497)

- 控制台显示收到

![](https://user-gold-cdn.xitu.io/2020/1/1/16f6121b89af4bfe?w=521&h=89&f=png&s=10584) 

- 撤回第一条信息

![](https://user-gold-cdn.xitu.io/2020/1/1/16f61222abd5b2a9?w=1242&h=922&f=png&s=302826)

- 控制台显示可能撤回的信息

![](https://user-gold-cdn.xitu.io/2020/1/1/16f6122c2ccd50b8?w=470&h=211&f=png&s=19365)

- 撤回第二条信息

![](https://user-gold-cdn.xitu.io/2020/1/1/16f612352566e39f?w=1242&h=868&f=png&s=252284)

- 控制台显示可能撤回的信息

![](https://user-gold-cdn.xitu.io/2020/1/1/16f61249390ae782?w=479&h=349&f=png&s=27979)

大概就是这样。

### 下期预告

本来是打算今天写完的，但奈何这一期太长，要看完可能是个体力活。所以，下一期我们会实现将整理好的撤回消息文本发送给“文件传输助手”，以便我们及时知道又有谁撤回了什么见不得人的消息。

### 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
本文代码：
https://github.com/TitusWongCN/AntiInfoWithdrawal
所有代码：
https://github.com/TitusWongCN/
```

---

【Python写微信防撤回脚本】往期推荐：

第一期：[【Python写微信防撤回脚本】01 熟悉ItChat库](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000174&idx=1&sn=89f0ab38943b35dac7cca07823562542&chksm=6a4bda6e5d3c5378c04d513cc25a26af95c14cade2bdd64967d2099229594fb9a10b5a9b2343#rd)

第二期：[【Python写微信防撤回脚本】02 接收记录聊天信息](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000182&idx=1&sn=41940b0310d7037f9315082972f4ebae&chksm=6a4bda765d3c53601193bf365c528cd4ad56293db400f7b0e6daf61a7b120e09d53949b967ee#rd)

下面是我的公众号，有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2020/1/1/16f6129fbe804df3?w=304&h=112&f=png&s=41105)

![](https://user-gold-cdn.xitu.io/2020/1/1/16f612a3ab3cc59b?w=258&h=258&f=png&s=20814)