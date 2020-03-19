
> 前面我们的预约脚本已经自动将姓名填入了网页，现在来处理剩下的部分

### 自动输入其他固定信息

前面提到过自动输入姓名信息，其实证件号码、手机号码、2020年贺岁币（第一批）这三条信息也是可以自动输入的。

输入的方式其实是一样的，下面是代码：

```python
ele_identNo = driver.find_element_by_xpath('//*[@id="identNo"]')
ele_identNo.send_keys(paras['identNo'])
ele_mobile = driver.find_element_by_xpath('//*[@id="mobile"]')
ele_mobile.send_keys(paras['mobile'])
ele_cardvalue0 = driver.find_element_by_xpath('//*[@id="cardvalue0"]')
ele_cardvalue0.send_keys(paras['cardvalue0'])
```

### 自动输入验证码

前文有提到过，网页上验证码的源是一条链接而不是一张固定的图片：

![](https://user-gold-cdn.xitu.io/2019/12/21/16f28c540aed2ffc?w=460&h=143&f=png&s=89951)

基于这种情况，我们不能通过链接直接读取当前的验证码。退而求其次，我们采取的方式是对当前验证码截图。不过这样做有一个缺点，就是每次运行时需要存储一个临时的验证码图片。考虑到脚本的使用环境不会有太多的验证码被缓存，而且每次缓存时保持临时图片的文件名不变则一直只会有一张图片，所以这个策略是可以被接受的。

那怎样对当前验证码截图呢？

`selenium`已经为我们想到了这一点：

```python
# 先找到验证码对应的网页元素
ele_piccaptcha = driver.find_element_by_xpath('//*[@id="piccaptcha"]')
# 然后直接调用这个元素的screenshot方法，参数是保存的路径即可实现截图
ele_piccaptcha.screenshot('./temp_capchar.jpg')
```

我们将验证码图片保存为了当前目录下的`temp_capchar.jpg`文件。但有时由于元素选择的不准确或者其他的原因会导致图片偏大，所以在识别验证码之前需要对它进行“瘦身”（前文代码中有体现）：

```python
# 先读取图片
image = cv2.imread(capchar, 0)
# 将图片上下左右各切割一个像素
image = image[1:-1, 1:-1]
```

上述代码是默认封装在`recognize_capchar`方法中的，要识别验证码，我们只需要将验证码图片的路径以及我们训练好的模型传递给这个方法即可。
需要注意的是，由于初始化神经网络的耗时相对其他代码来说会长很多，所以最好的做法是在程序一开始就初始化一个模型对象，后面只要需要自动识别验证码，都用这个对象来做。整个过程只需要初始化模型一次，能大大的提高效率，毕竟这是抢钱的时候。

```python
# 用已经提前初始化好的模型和标签对象来对temp_capchar.jpg进行自动识别
capchar = recognize_capchar('./temp_capchar.jpg', model, lb)
# 将识别结果输入到对应的框中
ele_capchar = driver.find_element_by_xpath('//*[@id="piccode"]')
ele_capchar.send_keys(capchar)
```

### 自动选择下拉框

前面都是静态的网页元素，像这种需要选择的元素应该怎么处理呢？

![](https://user-gold-cdn.xitu.io/2019/12/21/16f290e8c11ba390?w=386&h=272&f=png&s=26410)

![](https://user-gold-cdn.xitu.io/2019/12/21/16f291078d24c67b?w=480&h=272&f=png&s=26744)

其实也还是一步步的来，首先获取到这个下拉框对象：

```python
ele_orglevel = driver.find_element_by_xpath('//*[@id="orglevel1"]')
```

然后可以通过这个下拉框对象的`text`属性已经预先配置好的`location`信息获取到下拉列表的下标：

```python
for org_index, org in enumerate(ele_orglevel.text.split('\n')):
    if loca in org:
        ele_org = driver.find_element_by_xpath(xpath + '/option[{}]'.format(str(org_index + 1)))
        ele_org.click()
        break
```

这样一级一级的做下来就可以选中预先配置的选项了。我把这些重复的动作做到一个`for`循环中，然后将下拉框的选择做成了一个独立的方法，这样代码是不是看起来精简了许多：

```python
def choose_bank(driver, location, top_xpath):
    locations = location.split(',')
    for index, loca in enumerate(locations):
        level = str(index + 1)
        xpath = top_xpath.replace('1', level)
        ele_orglevel = driver.find_element_by_xpath(xpath)
        for org_index, org in enumerate(ele_orglevel.text.split('\n')):
            if loca in org:
                ele_org = driver.find_element_by_xpath(xpath + '/option[{}]'.format(str(org_index + 1)))
                ele_org.click()
                break
    xpath = top_xpath.replace('1', str(len(locations) + 1))
    try:
        ele_bottom = driver.find_element_by_xpath(xpath)
    except:
        return
    else:
        org_index = random.choice(list(range(len(ele_bottom.text.split('\n'))))[1:])
        ele_org = driver.find_element_by_xpath(xpath + '/option[{}]'.format(str(org_index + 1)))
        ele_org.click()
```

然后这样调用就可以了：

```python
choose_bank(driver, paras['location'], '//*[@id="orglevel1"]')
```

### 手机验证码的处理

由于手机验证码不是程序能直接拿到的东西，所以这个脚本也无能为力，这也是这个脚本只能叫做半自动脚本的原因。

但这里还是能简单讲讲业务流程的。

要获取手机验证码，我们首先得点击“获取验证码”按钮：

```python
btn_sms = driver.find_element_by_xpath('//*[@id="sendValidate"]')
btn_sms.click()
```

然后，我们需要输入手机验证码，然后程序会自动的输入到网页中：

```python
phoneCaptchaNo = input('请输入手机验证码, 按回车键确认（如果还未收到短信，请等到短信之后再输入）：\n')
ele_phoneCaptchaNo = driver.find_element_by_xpath('//*[@id="phoneCaptchaNo"]')
ele_phoneCaptchaNo.send_keys(phoneCaptchaNo)
```

### 提交预约单

至此，整个表单的信息全部填写完成，现在就差提交了：

```python
ele_infosubmit = driver.find_element_by_xpath('//*[@id="infosubmit"]')
ele_infosubmit.click()
```

### 后记

到这里，整个预约过程就结束了。

我们的“Python盘纪念币系列”也基本结束。

本系列的所有源代码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/AutoTokenAppointment
```

> 后面会有一篇文章对“Python盘纪念币系列”做一个总结，同时开始下一个系列，敬请期待！

---

[第一期：Python盘纪念币系列之一：简介](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483772&idx=1&sn=d578c80bbb0216c5bf528a8cc4a3a89a&chksm=ea4bdabcdd3c53aa46796d7b96a5292361223b1f96a1a0579f9bd2c3a80886a27ca4d57a6d68&scene=21#wechat_redirect)

[第二期：Python盘纪念币系列之二：识别验证码 01](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483781&idx=1&sn=0bff3d3410b55f25a5528cfcd9454a41&chksm=ea4bda45dd3c5353ba6b6cc67ebe84cebabc06b53a39391e2d49be45a6e5b763ab4bd60b3979&scene=21#wechat_redirect)

[第三期：Python盘纪念币系列之二：识别验证码 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000138&idx=1&sn=442469c6418af28deedd24dbf4fa033b&chksm=6a4bda4a5d3c535ca5e7d46fdf4c837eabba8691fad6a881c56781e037a530952a6fd42e92c7#rd)

[第四期：Python盘纪念币系列之二：识别验证码 03](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000144&idx=1&sn=4541cf9fb5dfdf0df5b69193845ebb9a&chksm=6a4bda505d3c5346ae5fee707c6a6221d66b3ecd8f8ea70e31793140d83499925d3cfe3c2542#rd)

[第五期：Python盘纪念币系列之二：识别验证码 04](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000149&idx=1&sn=395d1ff104dfe1a2d5791e308ed81008&chksm=6a4bda555d3c53431f3632f976af24dc768b4be46ae73f3d67397ad7763f56aaf81b9ec52ddf#rd)

[第六期：Python盘纪念币系列之三：自动预约脚本编写 01](https://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000160&idx=1&sn=8a378d166a717a7844152f02813314e4&chksm=6a4bda605d3c5376936307ff2dea68be3d20e2dc6ecb57d4fc5fee75fde21bd1bf47b28fc81d#rd)

