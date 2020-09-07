---
title: Python虚拟环境更换pip源
date: 2018-03-20 20:31:59
tags: [原创, Python, 更换pip源]
categories: Python配置
---

> 前两天重新安装了Debian, 把电脑里面的Python环境重新配置了一下。但是，重新通过pip安装Python各种包的时候，实在是太慢了受不了，于是有了这篇博文。

<!--more-->

### 背景

测试显示，通过pip默认地址安装Django包，平均速度在46KB/s左右，实在等不了让它下载完。

![默认pip地址下载速度太慢](1速度太慢.png "默认pip地址下载速度太慢")

### 问题解决

经过一番网上搜索，发现可以通过配置pip的方法来更换pip安装的源。我测试了一下，豆瓣的源就已经达到1.6MB/s了，于是一顿操作：

![更换豆瓣源之后的速度飞快](2速度真快.png "更换豆瓣源之后的速度飞快")

速度果然飞起来了！棒棒哒！

### 解决方法

关子卖完，该放干货了: 

- 在我们新建的虚拟环境的根目录，新建一个pip.conf文件

![新建pip配置文件](3新建config文件.png "新建pip配置文件")

- 打开配置档，加入如下内容

```Python
[global]
index-url=http://pypi.doubanio.com/simple/
[install]
trusted-host=pypi.doubanio.com
```

![编辑配置档](4编辑配置档.png "编辑配置档")

当然，如果你对速度有极致的追求，那你可以选择别的源～
