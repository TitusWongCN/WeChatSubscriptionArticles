> 前一篇遗漏了“预约兑换日期”的自动输入，这篇文章将介绍如何处理。另外，将会对“Python盘纪念币系列”做一个简单的总结。

### 自动输入预约兑换日期

不像文本输入框和下拉选择框，这个兑换日期元素点击之后会出现一个日期选择控件，看起来确实比前两者难以处理，不知道从何下手。

![](https://user-gold-cdn.xitu.io/2019/12/23/16f3268eaf84ea80?w=426&h=316&f=png&s=27581)

其实还是一样的，我们一步一步来处理。

在这之前，发现代码中有大量的重复语句，于是将这些语句挑出来写成独立的方法：

```python
def find_and_click(driver, xpath):
    ele = driver.find_element_by_xpath(xpath)
    ele.click()
    
def find_and_fill(driver, xpath, value):
    ele = driver.find_element_by_xpath(xpath)
    ele.send_keys(value)
```

他们的作用是什么相信读者一看就能知道，函数名写的很清楚。

那接下来肯定还是要先定位到这个文本框，定位到之后，执行点击操作，呼出日期选择器。一句话搞定：

```python
find_and_click(driver, '//*[@id="coindate"]')
```

看着上面那个日期选择器，似乎真的无从下手。但仔细想想，既然它能在网页中出现，那它肯定是有对应的网页路径的。所以，这里来查看一下：

![](https://user-gold-cdn.xitu.io/2019/12/23/16f327065913b6cd?w=329&h=336&f=png&s=20757)

对应的每一个日期也都是可以索引到的：

![](https://user-gold-cdn.xitu.io/2019/12/23/16f3319bfb058060?w=341&h=267&f=png&s=20793)


![](https://user-gold-cdn.xitu.io/2019/12/23/16f331b4966aad42?w=314&h=63&f=png&s=6694)

例如，上图中的`12`就可以用下面的`xpath`索引到：

```html
//*[@id="ui-datepicker-div"]/table/tbody/tr[3]/td[4]/span
```

熟悉`html`的同学应该知道，`<tr>`和`<td>`标签是表格符号，所以这个日期选择器其实就是一个表格，通过对`<tr>`和`<td>`标签的下标进行遍历即可找到对应的元素。如果本页遍历结束都还没有找到，则点击箭头到下一页继续：

![](https://user-gold-cdn.xitu.io/2019/12/23/16f33210eadb6ed7?w=541&h=335&f=png&s=36764)

而且是否可以选择可以直接根据上面`title`中的“不在兑换期”判断。

如果是可以兑换的日期，`title`则显示为“可选择”，如下：

![](https://user-gold-cdn.xitu.io/2019/12/23/16f331cf05efc579?w=380&h=217&f=png&s=21687)

![](https://user-gold-cdn.xitu.io/2019/12/23/16f331d46cdf6e27?w=320&h=79&f=png&s=8823)

经过上述分析，最后我们的代码大概是这样的：

```python
for tr_index in range(6):
    for td_index in range(7):
        try:
            ele_td = driver.find_element_by_xpath(
                '//*[@id="ui-datepicker-div"]/table/tbody/tr[{}]/td[{}]'.format(str(tr_index + 1), str(td_index + 1)))
        except:
            continue
        if ele_td.get_attribute('title') == '可选择':
            is_find = True
            ele_td.click()
            return
```

这样，最后一个拦路虎也解决了，我们终于可以开开心心的盘纪念币了。

说一句题外话，这个系列讲的是预约农行的纪念币，但其实其他银行也是同样的道理。我正在做工行的脚本，目前也快要完工，有需要可以公众号后台联系。

### 盘纪念币系列总结

说实话，我一开始也没想到我能坚持下来写完这一个系列。虽然不是什么很难的问题，但好歹是一步一步、一片一片、一点一点的讲完了。当然，文章有不少的缺陷，有的地方可以讲的细一些却没有精讲，有些地方比较类似却花了大量篇幅。但这些，我相信都是可以慢慢学习慢慢更正的，所以我更看重这个从`0`到`1`的质变。

题外话不多说，`Python`盘纪念币系列是一个利用`python`语言自动在网页上输入信息进行纪念币预约的系列文章。

这个系列的主要技术点有三个。

第一，利用`OpenCV`库处理验证码图片，分割出每一个字符；

第二，训练神经网络智能识别字符（当然这并不是唯一的识别验证码的方案）；

第三，利用`selenium`库自动化测试，将信息填入网页中实现自动预约。

想要详细了解可以翻翻这个系列的文章，如下所示。

[第一期：Python盘纪念币系列之一：简介](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483772&idx=1&sn=d578c80bbb0216c5bf528a8cc4a3a89a&chksm=ea4bdabcdd3c53aa46796d7b96a5292361223b1f96a1a0579f9bd2c3a80886a27ca4d57a6d68&scene=21#wechat_redirect)

[第二期：Python盘纪念币系列之二：识别验证码 01](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483781&idx=1&sn=0bff3d3410b55f25a5528cfcd9454a41&chksm=ea4bda45dd3c5353ba6b6cc67ebe84cebabc06b53a39391e2d49be45a6e5b763ab4bd60b3979&scene=21#wechat_redirect)

[第三期：Python盘纪念币系列之二：识别验证码 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000138&idx=1&sn=442469c6418af28deedd24dbf4fa033b&chksm=6a4bda4a5d3c535ca5e7d46fdf4c837eabba8691fad6a881c56781e037a530952a6fd42e92c7#rd)

[第四期：Python盘纪念币系列之二：识别验证码 03](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000144&idx=1&sn=4541cf9fb5dfdf0df5b69193845ebb9a&chksm=6a4bda505d3c5346ae5fee707c6a6221d66b3ecd8f8ea70e31793140d83499925d3cfe3c2542#rd)

[第五期：Python盘纪念币系列之二：识别验证码 04](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000149&idx=1&sn=395d1ff104dfe1a2d5791e308ed81008&chksm=6a4bda555d3c53431f3632f976af24dc768b4be46ae73f3d67397ad7763f56aaf81b9ec52ddf#rd)

[第六期：Python盘纪念币系列之三：自动预约脚本编写 01](https://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000160&idx=1&sn=8a378d166a717a7844152f02813314e4&chksm=6a4bda605d3c5376936307ff2dea68be3d20e2dc6ecb57d4fc5fee75fde21bd1bf47b28fc81d#rd)

[第七期：Python盘纪念币系列之三：自动预约脚本编写 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000160&idx=1&sn=8a378d166a717a7844152f02813314e4&chksm=6a4bda605d3c5376936307ff2dea68be3d20e2dc6ecb57d4fc5fee75fde21bd1bf47b28fc81d#rd)

[第八期：Python盘纪念币系列之三：自动预约脚本编写 03 & 系列总结](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000166&idx=1&sn=4ac00276bdfecaa1a22e8a3c083e7d48&chksm=6a4bda665d3c537098af5aaed68f6a97e522ff69f4ba7f893d294e1fe400c15dea0d2aa3aa15#rd)


---


写完这个系列，接下来会写一写跟微信有关系的文章，比如说微信群机器人、微信个人辅助之类的文章。因为平时玩微信比较多，也喜欢搞一些小`trick`。

当然了，不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的源代码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

下面是我的公众号，有兴趣可以扫一下：

![](https://user-gold-cdn.xitu.io/2019/12/23/16f333d3a3578000?w=304&h=112&f=png&s=13830)

![](https://user-gold-cdn.xitu.io/2019/12/23/16f333c33bd9bbe4?w=258&h=258&f=png&s=37181)