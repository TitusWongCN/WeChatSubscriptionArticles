> 据说震惊体很吸引眼球，今天我也来试一试🤪

> 本系列所有文章的开头都会用一两句话总结一下对应文章的内容。对这个话题感兴趣的话可以继续往下读，不感兴趣可以直接关掉，绝不浪费读者的时间。

## 总结

本篇文章用`Python`实现了一个简单的自动交易脚本，产生交易时会自动通过微信通知。

|  涉及概念  |  概念内容  |
| :---: | :---: |
|  `Python`库  |  `Wechaty`  |
|  主要概念  |  量化交易、微信机器人  |

## 量化交易

### 简介

`7`月份大`A`股的好行情想必大家都印象深刻，甚至有人预言`A`股五六年一个周期的大牛市即将开启。

结果大家已经看到了，但且不论开启没开启，反正当时大多数人的脑子都挺热的，这当然也包括我。不过，回顾我悲惨的投资经历，“追涨杀跌”这四个字是一个很好的总结😂。

这就难办了，眼睁睁看着别人赚钱翻倍，我不赚钱都相当于是亏钱。

我深知我每次的交易决策都是自身情绪的反映，而往往情绪化交易的后果就是追涨杀跌亏钱。那么问题来了，怎么才能管得住我这双亏钱的手？其中一个答案可能是**量化交易**。

量化交易其实不是很高深的概念。

一个量化交易软件会严格按照已经定义好的交易策略进行买入卖出操作，这些操作完完全全由策略触发，不受人为控制。

最简单的交易策略有双均值策略、网格交易策略等。

这简直就是为我设计的交易方式啊，妈妈再也不用担心我的臭手了。

### 网格交易策略

网上现成的量化交易框架很多，但学习这些框架可能需要比较长的时间。反正我就是想简单测试一下，顺便熟悉一下策略的机制，于是直接徒手写一个吧。

到底啥叫网格交易？网格交易可以简单地理解为：

> 把价格的波动区间放到以一个设定好的网格里，资金分成多份，价格每跌一格就买一份，每涨一格就卖一份。一份买入对应一份卖出，买卖交易之间只赚一格网格的差价。

看起来这正是我需要的。网格交易比较适用于震荡频率较高幅度较大的标的；一次只赚一格的钱，积少成多；把钱分为若干份，虽然利用率变低了，但也降低了风险。

说干就干，我决定测试一下网格交易策略效果如何。

首先需要预先定义一个震荡区间和网格数，我把这些需要预先定义的参数都放置到专门的配置文件里：

```python
lowest = 2.5  # 网格最低价格
highest = 3.5  # 网格最高价格
parts = 20  # 网格数
start_value = 300.0  # 账户初始资金 
timespan = 15  # 每15秒检测一次标的价格
wechat_reminder = 1  # 是否通过微信通知（1：是，0：否）
mail_reminder = 0  # 是否通过邮件通知（1：是，0：否）
mail_list = ['mailbox1', ]  # 需要通知的邮箱列表
```

初始化时，脚本会根据配置来设置当前的网格：

```python
# 每一格的高度
price_part_value = (highest - lowest) / parts
# 每变动一格对应的持仓百分比
percent_part_value = 1 / parts
# 所有网格的标记价格
price_levels = [round(highest - index * price_part_value, 4) for index in range(parts + 1)]
price_levels[-1] = lowest
# 每一格对应的整体持仓百分比
percent_levels = [round(0 + index * percent_part_value, 4) for index in range(parts + 1)]
percent_levels[-1] = 1.0000
```

配置完成后需要根据标的当前价格建底仓：

```python
# 如果当前价格比网格最低价格高则按照网格计算建仓层数，反之直接全仓
# order_target_percent根据target的符号及数值判断买入还是卖出，并下单交易
if float(close) > price_levels[0]:
    pos = [close > level for level in price_levels]
    i = pos.index(False) - 1
    last_price_index = i
    target = percent_levels[last_price_index] - last_percent
    if target != 0.0:
        return True, order_target_percent(float(close), depth, target, date=date)
else:
    return True, order_target_percent(float(close), depth, 1.0, date=date)
```

然后每次标的价格穿越网格时执行对应的操作：

```python
signal = False
while True:
    upper = None
    lower = None
    if last_price_index > 0:
        upper = price_levels[last_price_index - 1]
    if last_price_index < len(price_levels) - 1:
        lower = price_levels[last_price_index + 1]
    # 还不是最轻仓，继续涨，就再卖一档
    if upper and float(close) > upper:
        last_price_index = last_price_index - 1
        signal = True
        continue
    # 还不是最重仓，继续跌，再买一档
    if lower and float(close) < lower:
        last_price_index = last_price_index + 1
        signal = True
        continue
    break
if signal:
    target = percent_levels[last_price_index] - last_percent
    if target != 0.0:
        return True, order_target_percent(float(close), depth, target, date=date)
else:
    return False, []
```

到这里一个最简单但很完整的网格交易策略就写好了。当然了，实时价格的获取以及交易操作的实现需要读者自己去实现了。

## 微信机器人

### 简介

看过我之前文章的读者都知道，我写的所有关于微信机器人的文章全都是用的`ItChat`。这个库只支持能登录网页版微信的微信号，`2017`年之前没有登陆过网页版微信的微信号和`2017`年之后申请的新微信号基本上都不能用，局限性太大！读者可以打开网页版微信官网[`https://wx.qq.com/`](https://wx.qq.com/)查看自己是否可以使用网页版微信。

经过我不懈的寻找，终于找到一款不限于网页版微信的库：`Wechaty`：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d46d316ceddd4c868ecff1ddf43045bf~tplv-k3u1fbpfcp-zoom-1.image)

`Wechaty`原本是用`TypeScript`开发的，但开发团队正在进行多语言的移植，目前已经有可以用的`Python`版本，不过功能可能暂时没有原版那么强大。`Wechaty`开发团队励志把它开发成一款支持全平台微信协议的库，目前已经支持`Web`、`Ipad`、`Windows`以及`Mac`等协议。虽然需要付费获取`token`，但是可以申请参与开源激励计划来获取免费甚至长期有效的`token`。在这里也要感谢`Wechaty`团队提供微信机器人`SDK`🙏🙏🙏。

### Demo

下面来实现一个最简单的机器人：收到任意消息后回复`收到`。

```python
import asyncio
from typing import Optional, Union
from wechaty import Wechaty, Contact
from wechaty.user import Message, Room

async def wechat():
    bot = Wechaty()
    # 将on_message方法绑定到bot对象的message事件上
    bot.on('message', on_message)
    await bot.start()
    
async def on_message(msg: Message):
    from_contact = msg.talker()
    text = msg.text()
    room = msg.room()
    conversation: Union[
        Room, Contact] = from_contact if room is None else room
    await conversation.ready()
    await conversation.say('收到')
    
asyncio.run(wechat())
```

上面的代码只用到了`message`事件，`Wechaty`还提供很多事件接口，例如`scan`、`login`、`room-join`、`room-leave`、`logout`、`error`等，想了解的读者可以联系交流。

### 脚本中的使用

上面的demo代码很简单，一看就懂，在本案例中的使用其实也很简单。

当前价格触发网格策略进行交易时，只需要在交易后总结当次交易的信息，然后利用类似上面的方法发送出来即可。实际操作中，我会把相应消息发送到我专门建的“量化动态播报”群里（目前在运行的有两个网格）：

```python
async def on_message(msg: Message):
    from_contact = msg.talker()
    text = msg.text()
    room = msg.room()
    conversation: Union[
        Room, Contact] = from_contact if room is None else room
    if from_contact.payload.name.upper() == AdminWechatName and from_contact.contact_id.upper() == AdminWechatContactId:
        # 发送#GRIDSTATUS时回复当前网格仓位状态等
        if text.upper() == '#GRIDSTATUS':
            await conversation.ready()
            await conversation.say(str(grid))
        # 发送#SETGRID:格式信息时动态修改网格参数
        elif text.upper().startswith('#SETGRID:'):
            paras = {('grid.' + item.split('=')[0]): item.split('=')[1] for item in text[9:].lower().split(';')}
            cfg.set_paras(paras)
            await run_grid()

async def run_grid():
    flag, content = grid.run_data(data)
    if flag:
        if int(grid.mail_reminder):
        	for mail_box in grid.mail_list:
              	mail_helper.sendmail(mail_box, 'GRID SCRIPT NEW TRADE', content)
        if int(grid.wechat_reminder):
            await trade_reminder(bot, content)
            
async def trade_reminder(bot, mail_content, target=None):
    for id in target:
        room = bot.Room.load(id)
        await room.ready()
        conversation: Union[Room, Contact] = room
        await conversation.ready()
        await conversation.say(mail_content)
```

下面是实际效果：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/468ace5ba7eb4667a3cf911a6888608c~tplv-k3u1fbpfcp-zoom-1.image)

### 微信机器人的替代方案

肯定会有读者觉得上面的机器人还是太麻烦，这里在推荐一个小工具，同时也感谢开发者的努力与奉献！

这个工具的名字叫`Server酱`，英文名为`ServerChan`，是一款程序员和服务器之间的通信软件，也就是从服务器推报警和日志到手机的工具。官网是[http://sc.ftqq.com/3.version](http://sc.ftqq.com/3.version)，读者可以自行了解，总之很好用就是了。

开通并使用上它，只需要一分钟：

- 登入：用`GitHub`账号登入网站，就能获得一个`SCKEY`。

- 绑定：点击“微信推送”，扫码关注同时即可完成绑定。

- 发消息：往`http://sc.ftqq.com/SCKEY.send`发`GET`请求，就可以在微信里收到消息了。

收到的消息类似于这种：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/cae87660c219431aa8cada5a664246cd~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/884b99355e334522945dcde76edfd6ea~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e90a17b142b94f5c9aff52c0ef2a0665~tplv-k3u1fbpfcp-zoom-1.image)

是不是很简单方便？

## 附言

由于网格交易策略更适用于震荡市，所以目前策略是在数字货币上实施的，正在运行的包括一个实盘币种和一个测试币种，玩过数字货币的读者应该对它的震荡行情有所了解。

有兴趣的读者也可以联系我进量化动态播报群，网格交易触发的时候机器人会把操作动态实时发到群里。

## 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

下面是我的公众号，我有兴趣可以扫一下：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a66ed052b3e142e6b6cb0efe0d4313be~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/00d84ee4e4bf47868f509f7206530655~tplv-k3u1fbpfcp-zoom-1.image)