> 引子：疫情已经好转许多，身在湖北的我已经能看到曙光！在【`Python`开发微信助手】系列的第一期我们初试牛刀实现了一个完善的自动回复功能，这一期我们来写一个自动查询百度和微博热搜的功能。

![](https://user-gold-cdn.xitu.io/2020/3/15/170decb8e8742c19?w=750&h=385&f=png&s=116737)

### 需求背景

平常生活中，我应该属于是比较宅的，国内国际发生什么大事我也不怎么关注。但工作中我发现同事间聊天，除了工作就是聊这些新发生的热点问题，所以我有时候也会关注这些以免跟不上节奏。

一般热点问题都可以在微博或者百度里面通过查看实时热搜或者实时热点来查询。那么问题就来了。我想看微博热搜，我就得先打开微博然后切换到对应菜单栏，然后找到大家都在搜后点全部才能看到完整的榜单；百度的实时热点也是与此类似。就像下面这张微博的图片：

![](https://user-gold-cdn.xitu.io/2020/3/15/170dcd960cfa0c00?w=410&h=729&f=png&s=145098)

一个小小的需求，竟需要三个操作才能实现。前面说了，我是微信重度使用者，基本上我打开手机肯定是在微信界面。那我能不能指令我的微信小助手帮我查询热搜话题然后发送给我呢？

当然可以！实现效果如下（有想体验的朋友可以公众号后台发送“微信个人助手体验”获取助手微信号，备注“微信个人助手体验”自动通过，目前已有天气查询、实时热搜查询、翻译、在线点歌功能）：

![](https://user-gold-cdn.xitu.io/2020/3/15/170dcda80f4c5e86?w=410&h=461&f=png&s=246868)

### 获取热搜资讯

实现这个功能的第一步自然是获取我们想要的热搜资讯，由于原理都一样，这里我们就拿微博热搜举例。下面是微博热搜的网址：

```html
https://s.weibo.com/top/summary?cate=realtimehot
```

![](https://user-gold-cdn.xitu.io/2020/3/15/170de8446e46120c?w=847&h=463&f=png&s=36704)

那怎样才能把这些关键词提取出来呢？下面就涉及到爬虫的相关知识了。本公众号最初的文章中有两篇相关的文章，有兴趣的可以再去看看。

在Chrome地址栏输入上面的网址，打开开发者工具然后回车：

![](https://user-gold-cdn.xitu.io/2020/3/15/170de602239768e8?w=770&h=477&f=png&s=56417)

发现没有专门的`API`来生成热搜信息，所以这里我们采取直接解析网页源代码的方式来获取热搜资讯。

用`Python`获取网页源代码十分简单，两句话就能搞定：

```Python
import requests

page = requests.get('https://s.weibo.com/top/summary?cate=realtimehot')
page_source = page.text
```

这里引用了`requests`包，这是一个支持`HTTP`连接保持和连接池，支持使用`cookie`保持会话，支持文件上传，支持自动响应内容的编码，支持国际化的`URL`和`POST`数据自动编码的`Python`库。总之，记住这是一个处理`URL`资源特别方便的库就好。通过上面两句代码，我们拿到下面这样的信息（内容太多，这里有部分删减，且格式已经整理好）：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>微博搜索-热搜榜</title>
</head>

<body class="wbs-hotrank">
<div class="m-main">
    <!--内容 aa-->
    <div class="m-wrap" id="plc_main">
        <div class="data" id="pl_top_realtimehot">
            <table>
                <thead>
                    <tr class="thead_tr">
                        <th class="th-01">序号</th>
                        <th class="th-02">关键词</th>
                        <th class="th-03"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="">
                        <td class="td-01"><i class="icon-top"></i></td>
                        <td class="td-02">
                            <a href="">全球战疫中国式投桃报李</a>
                        </td>
                    </tr>
                    <tr class="">
                        <td class="td-01 ranktop">1</td>
                        <td class="td-02">
                            <a href="">	张文宏称疫情今夏结束基本已不可能</a>
                            <span>4855001</span>
                        </td>
                    </tr>
                    <tr class="">
                        <td class="td-01 ranktop">2</td>
                        <td class="td-02">
                            <a href="">北京小汤山医院所有医疗设备就位</a>
                            <span>2153854</span>
                        </td>
                    </tr>
```

【本文来自微信公众号`Titus的小宇宙`，`ID`为`TitusCosmos`，转载请注明！】

【为了防止网上各种爬虫一通乱爬还故意删除原作者信息，故在文章中间加入作者信息，还望各位读者理解】

可以很明显的看到每一个热搜话题以及对应的热度。这里要注意观察，每个热搜话题和它对应的热度都分别在`class`属性为`td-02`的`td`标签下的`a`标签和`span`标签中。发现了这一点后，是不是每次都需要把网页源代码格式化之后再通过某种方法筛选出来呢？当然不用，我们有更简单的工具：

```Python
from lxml import etree

tree = etree.HTML(page_source)
```

这里引用了`lxml`包中的`etree`类，它可以自动把`html`源代码转换为类似`xml`的树结构。根据前面的分析，这里通过`xpath`就能很方便的获取对应位置的信息，但要注意热搜话题中的第一条是手动置顶话题，这里需要去除掉：

```Python
news = tree.xpath('//td[@class="td-02"]/a/text()')[1:]
news_hot_index = tree.xpath('//td[@class="td-02"]/span/text()')
```

得到的内容如下：

![](https://user-gold-cdn.xitu.io/2020/3/15/170de82c0314d0da?w=1110&h=635&f=png&s=116854)

所有前期准备已经做好，接下来要做的就是根据要显示的数量把这些内容组织起来了：

```Python
# limit是默认或者设置的要显示的数量
for index in range(limit):
    topic = format.format(str(index+1), news_hot_index[index], news[index])
    topics.append(topic)
result = '\n***********************\n'.join(topics)
return result
```

这样，获取热搜话题的后台代码就编写好了。

### 微信交互

后台的功能做好了，剩下的就是前台与微信交互的部分了。

我们会根据用户的请求采集微博或者百度平台的热搜信息，两者都是默认提供50条热搜信息。所以这部分需要用户提供的信息有两个：热搜来源和显示条数。

通过设置默认的热搜平台和显示条数，用户可以只发送“热搜”即可获取信息。同时也可以通过“开启/关闭热搜”来选择启用或者停用热搜查询功能。

与上一篇“自动回复”文章一样，通过全局变量的方式实现用户的自定义设置（请注意只是演示，部分代码没有做严谨的限制）：

```python
# 在外部定义默认值
is_open_hotspot = True
custom_platform = '微博'
custom_limit = 5

# 在函数最开头声明这是一个全局变量
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    global is_open_hotspot, custom_platform, custom_limit
    sender = msg['User']['UserName'] if 'UserName' in msg['User'] else 'filehelper'
    nickname = msg['User']['NickName'] if 'NickName' in msg['User'] else 'filehelper'
    content = msg['Content']
    if nickname == 'filehelper' or nickname == 'Admin/Name/To/Fill/In':
        cmd = content.lstrip().rstrip()
        if cmd == '开启热搜':
            is_open_hotspot = True
            itchat.send_msg('已开启热搜功能！', sender)
        elif cmd == '关闭热搜':
            is_open_hotspot = False
            itchat.send_msg('已关闭热搜功能！', sender)
        elif cmd.startswith('设置热搜，'):
            custom_content = content.replace('设置热搜，', '')
            custom_platform = custom_content.split(' ')[0]
            custom_limit = custom_content.split(' ')[1]
            itchat.send_msg('热搜默认值已设置成功！', sender)
        elif cmd == '热搜':
            result = get_hotspot(custom_platform, custom_limit)
            itchat.send_msg(result, sender)
        elif cmd.startswith('热搜，'):
            custom_content = content.replace('设置热搜，', '')
            result = get_hotspot(custom_content.split(' ')[0], custom_content.split(' ')[1])
            itchat.send_msg(result, sender)
        else:
            pass
```

到这里，一个完整的热搜查询功能正式完成。

程序员的世界里不允许存在多余的操作，每一个多余的操作都是在浪费生命。

### 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

<hr>

【Python开发微信助手】往期推荐：

第一期：[【Python开发微信助手】01 自动回复功能](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000225&idx=1&sn=0d59f71434742bf8643b5d264a73a6d7&chksm=6a4bda215d3c533799d4db2964f38833b4053b7bcda6d84a4b17b85ee7e33d306614d6253626#rd)

下面是我的公众号，里面记载了一些我有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2020/3/7/170b0b521cad4cbd?w=304&h=112&f=png&s=43506)

![](https://user-gold-cdn.xitu.io/2020/3/7/170b0b5459f7f115?w=258&h=258&f=png&s=23703)