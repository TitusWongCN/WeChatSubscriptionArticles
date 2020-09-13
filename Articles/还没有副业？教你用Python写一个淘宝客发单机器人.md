> 写在前面：本文只讨论技术实现原理及引导教程，不广告，不推广。文章有点长，各位看官可以各取所需。

> 说起2020年的人们讨论最多的词汇，我觉得**副业**应该可以算一个。

> 年初的疫情把大家都锁在家里，好多人的收入都没有了保障。于是，副业成了刚需。一时间，朋友圈卖各种东西的朋友如雨后春笋般冒了出来——谁谁谁又通过副业赚了几万乃至几十万的消息此起彼伏。这你能受得了？反正我是受不了！**卖东西我不会卖，但我能让你卖得更加自动化**。

## 总结

本篇文章用`Python`实现了一个淘宝客微信机器人自动获取包含大额优惠券的推广购买链接，推广者将可以获取推广佣金。具体功能如下：

1. 给机器人发送淘口令，机器人能自动获取对应的大额优惠券
2. 给机器人发送想要购买的物品名称，机器人会自动搜索对应物品，并筛选出性价比最高（当然也是佣金相对最高的啦）的商品生成推广购买链接
3. 附加功能：生成对应卖货平台（闲鱼、转转等）的商品描述，简化上架操作（把上一步拿到的信息套进模板即可）

|  涉及概念  |  概念内容  |
| :---: | :---: |
|  主要`Python`库  |  `itchat`、`Wechaty`  |
|  主要概念  |  `app`数据爬取、微信机器人  |

## `app`数据爬取

疫情在家期间除了官方淘宝客平台，还接触过一些第三方平台，对各自的佣金比例及平台信誉有一定了解。有的有网页端和`app端`，有的只有`app`端，可惜的是，我选出来我觉得最好的那个只有`app`端。

于是，怎么爬取`app`内的数据？这当然难不倒程序员啦。

### 爬取前的准备

手机上的工具有限，使用体验不佳，很直接就能想到让手机上的数据通过电脑传输，只要经过电脑了，那事情就好办了。我们使用`Fiddler`来完成这个操作：

> `Fiddler`是一个`http`协议调试代理工具，它能够记录并检查所有你的电脑和互联网之间的`http`通讯，设置断点，查看所有的“进出”`Fiddler`的数据

下面简单介绍一下这个工具的下载与配置，以下文字参考自：[Python3,x：如何进行手机APP的数据爬取](https://www.cnblogs.com/lizm166/p/8693085.html)，感谢作者的分享。

#### `Fiddler`下载与配置

首先到官网下载，根据系统选择安装包，下载地址为：[`https://www.telerik.com/download/fiddler`](https://www.telerik.com/download/fiddler)。安装过程很简单没有什么特别的，直接下一步就好。

安装好以后，需要设置以下几项：

1. 设置允许抓取`HTTPS`信息包

	菜单栏找到 `Tools -> Options`，然后在`HTTPS`的工具栏下勾选`Decrpt HTTPS traffic`，在新弹出的选项栏下勾选`Ignore server certificate errors (unsafe)`。这样，`Fiddler`就会抓取到`HTTPS`的信息包。

	![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1d4ecfa03f974e6abe319d9c93745993~tplv-k3u1fbpfcp-zoom-1.image)

2. 设置允许外部设备发送`HTTP/HTTPS`到`Fiddler`

	在`Connections`选项栏下勾选`Allow remote computers to connect`，并记住上面的端口号`8888`，端口号后面会使用到。
	
    ![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/097703996fbc4b18b7eb1ccd3ee6491e~tplv-k3u1fbpfcp-zoom-1.image)

3. 重启下`Fiddler`

#### 手机端设置

手机端的配置相对比较麻烦，不过也还好。我使用的苹果机，所以这里只介绍苹果机的配置。其他系统的手机可以直接在网上搜索教程，类似的教程非常多，这里就不细讲了。

1. 设置手机和电脑在同一网络内

	前面说到手机上的数据通过电脑来传输，基本前提就是需要手机跟电脑在同一网络内。如果家里有`WIFI`，则手机和电脑都连上这个`WIFI`，台式机没有无线网卡的话可以用网线连接到`WIFI`对应的路由器上；家里没有`WIFI`的话，可以用手机打开无线热点，电脑连上手机的热点也可以。

2. 设置手机`HTTP`代理

	先获取电脑的`IP`地址：
    
    ![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e1e83fce4aaf4799b08d50e5d4322ae6~tplv-k3u1fbpfcp-zoom-1.image)
    
    然后进入手机`WIFI`的设置界面，选择当前连接网络的更多信息，在苹果中是一个叹号。点击进入后你会在最下面看到`HTTP`代理的选项，选择点击进入，选择手动。进入后，填写上面记住的`IP`地址和端口号，确定保存：

	![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d6ca3dbdbc7e438888e15fc3591ee6e5~tplv-k3u1fbpfcp-zoom-1.image)

3. 下载并安装`Fiddler`安全证书

	手机上打开`Safari`浏览器输入一个上面`IP`地址和端口号组成的`url: http://192.168.2.107:8888`。打开后你会看到如下的界面，然后点击`FiddlerRoot certificate`并允许下载`Fiddler`证书。

	![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/cd2779edfece4041a6158ec0b4340fed~tplv-k3u1fbpfcp-zoom-1.image)

	下载完成后到设置里安装证书：
    
    ![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/180c9b8a45bb4027a7134a777603e292~tplv-k3u1fbpfcp-zoom-1.image)

至此，`Fiddler`的安装与配置就做好了。

### 开始爬取

#### 获取请求

打开手机上对应的`app`，`Fiddler`随即出来很多条请求，根据`url`可以很容易找出我们想要的内容。

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1e28b904719e4c53a5f7369b8bedbc0a~tplv-k3u1fbpfcp-zoom-1.image)

这些内容就是获取`app`上我们看到的信息的网络请求，所以只需要用代码实现这些请求即可获取`app`上的信息。

根据需求，我们依次找到了**淘口令搜索物品**、**直接搜索物品**、**特定物品生成推广购买链接及淘口令**这三种请求。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/93005a66146646108ade77618e3545b8~tplv-k3u1fbpfcp-zoom-1.image)

#### 分析请求

来看一下这些请求的具体内容吧。

点击某个请求，再点击响应栏的`JSON`选项卡看到请求返回的信息是一组`Json`字符串：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7288549cb7114cf3a32ff16f99f3e0d8~tplv-k3u1fbpfcp-zoom-1.image)

下面分别是生成淘口令和链接的请求对应的`Json`：

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/867a2b9c713c47d4a013a52f85bd206c~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a9567eaa9baf445cb28ec9b6e45c8b59~tplv-k3u1fbpfcp-zoom-1.image)

可以清晰的看到对应物品的图片、价格、佣金和简单描述等相关信息，这也正是我们想要的。

以淘口令搜索物品为例，请求栏的`Headers`选项卡也有这个请求的详细请求头信息：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d597c3c915134ed5b9b129bd40bacb29~tplv-k3u1fbpfcp-zoom-1.image)

#### 模拟请求

有了这些信息，我们可以很清晰的模拟发送请求，代码如下：

```python
from urllib.parse import urlencode
import requests
import pprint

def analysis_keyword(keyword):
    headers = {
        'Host': 'proxy.guod********.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-appid': '1911140394',
        'Accept': '*/*',
        'x-agent': 'JellyBox/2.2.4 (iOS, iPhone 8 Plus, 13.3.1)',
        'x-token': '',
        'x-devid': 'DF3D1D14-3230-497E-811E-C4425521736F',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-userid': '',
        'User-Agent': 'AffordablePig/2.2.4 (iPhone; iOS 13.3.1; Scale/3.00)',
        'Content-Length': '0',
        'x-nettype': 'WIFI',
        'x-platform': 'iOS',
        'x-devtype': 'UTDID',
        'Cookie': 'PHPSESSID={}',
        'Connection': 'keep-alive',
    }

    headers['x-token'] = ******
    headers['x-userid'] = ******
    headers['Cookie'].format('**************')

    encoded_keyword = urlencode(keyword)
    query_url = 'https://proxy.guod********.com/cate/search?q={}&sort=&coupon=false&type=2&page=1'.format(
                encoded_keyword)

    sess = requests.session()
    result = sess.post(query_url, headers=headers).json()
    pprint.pprint(result)
    return result
 
print(analysis_keyword('*****'))
```

运行以后获取的信息为：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7030d5aab5ec4c8ea6d809281f157e57~tplv-k3u1fbpfcp-zoom-1.image)

太长了，就不全部贴出来了。是不是跟`Fiddler`上面的一样？其他请求也是类似的道理。但有时候需要按步骤进行每一个请求，因为它们是一环套一环的。

## 微信机器人

到这里，我们就应该能获取到上面所说的那些信息了，那怎么才能发送给微信呢？

实现微信控制的有很多库，我用过的有代表性的就是`itchat`和`Wechaty`，他们都可以实现微信登录及收发信息等微信操作，只不过实现的方式不同。我前面的文章已经多次介绍这两个库，这里不再赘述。

实现机器人的方式也很简单，用户将要查询的物品名称或者淘口令发送给机器人，如果是在群聊中则需要用户@机器人（需要通过@确认是查询命令），机器人就会自动相对应的推广物品信息。

为了让实现机器人的代码保持功能单一，我把所有查券的代码放在一个文件中。

### 通用查券代码

上面的代码能够得到商品的详细信息，但是不可能直接把那些东西给用户吧，所以需要整理成言简意赅的短消息。代码如下（虽然少有注释，但变量名就是注释 0.0），类似的代码作了删减：

```python
# 获取关键信息
def gen_good_coupan_desc(result, uland_url):
    good_data = result['result'][0] # 这里的result就是上面得到的result
    good_name = good_data['goods_name']
    good_id = good_data['goods_id']
    good_url = 'https://detail.tmall.com/item.htm?id={}'.format(good_id)
    good_pre_price = good_data['attr_prime']
    good_cur_price = good_data['attr_price']
    attr_ratio = good_data['attr_ratio']
    coupon = good_data['coupon_explain'] if 'coupon_explain' in good_data else ''
    coupon_begin_date = good_data['coupon_begin'] if 'coupon_begin' in good_data else ''
    coupon_final_date = good_data['coupon_final'] if 'coupon_final' in good_data else ''
    coupon_start_fee = good_data['coupon_start_fee'] if 'coupon_start_fee' in good_data else ''
    coupon_saving_amount = good_data['coupon_amount'] if 'coupon_amount' in good_data \
        else '{:.2f}'.format(float(good_pre_price) - float(good_cur_price))
    price_info = '现价: {}, 实付价: {}'.format(good_pre_price, good_cur_price)
    coupon_info = ''
    if coupon_begin_date != '' and coupon_final_date != '':
        coupon_info = '优惠券有效期: {}-{}'.format(coupon_begin_date, coupon_final_date)
    good_image_url = good_data['goods_thumb']
    params = {
        'timestamp': str(time.time()).split('.')[0],
        'url': uland_url,
        'member_id': headers['x-userid'],
        'text': good_name,
        'logo': good_image_url,
        'goods_id': good_id,
        'attr_prime': str(good_pre_price),
        'attr_price': str(good_cur_price),
        'attr_ratio': str(attr_ratio)
    }
    return params, good_url, good_image_url, good_name, price_info, coupon_info

def get_uland_url(result):
    pass
    return # 返回优惠券链接

def gen_TKL(result):
    # 代码与获取商品详情类似，省去
    pass
    return # 返回推广淘口令

def gen_web_url(result):
    # 代码与获取商品详情类似，省去
    pass
    return # 返回推广链接

def get_good_desc(keyword):
    result = analysis_keyword(keyword)
    uland_url = get_uland_url(result)
    coupan_desc = gen_good_coupan_desc(result, uland_url)
    if isinstance(coupan_desc, str):
        continue
    params, good_url, good_image_url, good_name, price_info, coupon_info = coupan_desc
    my_tkl = gen_TKL(params)
    my_web = gen_web_url(params, my_tkl)
    # 生成回复文本
    reply_TKL = reply_head + '复制本信息至TB领取隐藏优惠券({})'.format(my_tkl)
    good_reply = [good_name, price_info, coupon_info, reply_TKL] if coupon_info != '' \
        else [good_name, price_info, reply_TKL]
    return '\n'.join(good_reply)
  
print(get_good_desc(result))
```

当给机器人发送淘口令`₳hr6a****ZTy₳`时，机器人的回复就会是：

```text
******医用口罩一次性医疗口罩三层防护灭菌熔喷布夏天透气非外科
现价: 18.8, 实付价: 16.8
优惠券有效期: 20200908-20200913
复制本信息至TB领取隐藏优惠券(₴C9v3c****po₰)
```

好了，现在万事俱备，只欠东风。下面就看看怎么实现机器人。

### `itchat`版本机器人代码

`itchat`我已经写过很多篇了，这里直接上代码：

```python
# -*- coding=utf8 -*-
import itchat
from itchat.content import *

# 如果是好友发送的文本消息
@itchat.msg_register([TEXT])
def text_reply(msg):
    sender_id = msg['User']['UserName'] if 'UserName' in msg['User'] else 'filehelper'
    content = msg['Content']
    # 生成回复文本
    reply = get_good_desc(keyword)
    itchat.send_msg(reply, sender_id)

# 如果是群聊发送的文本消息
@itchat.msg_register([TEXT], isGroupChat=True)
def group_reply(msg):
	content = msg['Text']
    if msg['IsAt']: # 如果被@
    	# 获取需要查询的信息（去掉消息文本中的@及@后面的符号）
    	content = '\u2005'.join(content.split('\u2005')[1:]) if '\u2005' in content \
                    else ' '.join(content.split(' ')[1:])
    	sender_id = msg['User']['UserName']
        # 生成回复文本
        reply = get_good_desc(keyword)
        itchat.send_msg(reply, sender_id)

if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    itchat.run()
```

### `Wechaty`版本机器人代码

其实代码都差不多，只不过每个库有每个库不同的使用方式，废话不多说，Show the code：

```python
from wechaty import Wechaty
from typing import Optional, Union, List
from wechaty_puppet import ScanStatus, MessageType
from wechaty.user import Message, Room
from wechaty import Friendship, FriendshipType, Contact
import asyncio

async def on_message(msg: Message):
    await msg.ready()
    from_contact = msg.talker()
    room = msg.room()
    # 如果是文本消息
    if msg.payload.type == MessageType.MESSAGE_TYPE_TEXT:
    	# 而且发单机器人被@
    	if wechaty_robot_id in msg.payload.mention_ids:
        	content = msg.text()
            if room is None:
                # 如果是好友发送的消息则直接生成回复文本
                reply = get_good_desc(content)
                await from_contact.ready()
                from_contact.say(reply)
            else:
                # 如果是群聊消息处理被@的消息
                if '\u2005' in content: # 手机发的消息会有这个特殊符号
                    content = '\u2005'.join([item for item in content.split('\u2005') if not item.startswith('@')])
                else: # 电脑发的则是空格
                    content = ' '.join([item for item in content.split(' ') if not item.startswith('@')])
                reply = get_good_desc(content)
                await room.ready()
                room.say(reply)

async def bot_start():
    bot = Wechaty()
    # 把消息处理方法绑定到"message"事件上
    bot.on('message', on_message)
    await bot.start()

asyncio.run(bot_start())
```

### 效果演示

说了这么多，该上点实在的东西了，下面就是实际运行的效果图了（图有点长，可以快点拉...）：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c02f6506fa9e47cc8e69e3f120251b1c~tplv-k3u1fbpfcp-zoom-1.image)

## 附言

就我的感受而言，之所以很多人热衷于副业，还是因为没钱或者是不够有钱，毕竟这一届社畜压力实在太大。如果这篇文章能帮到你，给你带来不一样的点子，也算让我感到欣慰了。

最后，希望所有人都不用副业就可以生活的很美满。

## 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

下面是我的公众号，有兴趣可以扫一下：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a66ed052b3e142e6b6cb0efe0d4313be~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/00d84ee4e4bf47868f509f7206530655~tplv-k3u1fbpfcp-zoom-1.image)