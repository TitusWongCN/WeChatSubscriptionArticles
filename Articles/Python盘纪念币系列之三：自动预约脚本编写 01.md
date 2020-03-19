
> 前面我们通过神经网络成功的识别了验证码，这一期我们就可以开始编写自动预约脚本了。

### 页面观察

趁着近期可以预约鼠年纪念币，我们可以拿现成的预约界面来观察：

![](https://user-gold-cdn.xitu.io/2019/12/20/16f23a6e856df13e?w=774&h=619&f=png&s=71474)

与前面给出过的一个页面相比，现在的页面不一样的是可以填写预约数量：

![](https://user-gold-cdn.xitu.io/2019/12/20/16f23aa29b0e4590?w=719&h=73&f=png&s=7166)

其他一些之前没有反应的UI也都有了该有的反应。

在这个基础上，我们就可以开始编写脚本了。

### 配置文件设计

既然要写脚本，必然是要做大量的重复性工作。在这里，就是要快速的输入多组信息来预约纪念币。所以，我们要提前把需要的数据按照一定的格式准备好，这样便于脚本运行时自动读取。下面是一个例子：

```python
users = {
    'name_1': {
        'identNo': 'identNo_1',
        'mobile': 'mobile_1',
        'location': 'location_1',
        'cardvalue0': 'cardvalue0_1'
    },
    'name_2': {
        'identNo': 'identNo_2',
        'mobile': 'mobile_2',
        'location': 'location_2',
        'cardvalue0': 'cardvalue0_2'
    },
    'name_3': {
        'identNo': 'identNo_3',
        'mobile': 'mobile_3',
        'location': 'location_3',
        'cardvalue0': 'cardvalue0_3'
    }
    ...
}
```

配置文件中包含了姓名、身份证号码、手机号码、地点信息以及预约数量。这些都是固定信息，是可以提前配置好的，程序会在启动之后将这些信息自动填入对应的位置。

### 预约脚本编写

在编写正式脚本之前，我们需要根据前文先将验证码识别写成一个独立的功能块，以免造成代码混乱：

```python
def recognize_capchar(capchar, model, lb):
    result = ''
    image = cv2.imread(capchar, 0)
    image = image[1:-1, 1:-1]
    target_patches = get_cutted_patches(image)
    for target_patch in target_patches:
        image = cv2.resize(target_patch, (16, 16))
        # scale图像数据
        image = image.astype("float") / 255.0
        image = np.expand_dims(image, axis=-1)
        # 对图像进行拉平操作
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        # 预测
        preds = model.predict(image)
        # 得到预测结果以及其对应的标签
        i = preds.argmax(axis=1)[0]
        label = lb.classes_[i]
        result += label
    return result
```

尝试自己填写信息，然后点击提交之后发现，这个网页并没有可以直接提交预约信息的api，所以目前来看最好的做法，还是利用`selenium`通过自动化测试的方式进行。

#### 建立浏览器对象

为了能演示的清楚，这里采用`Chrome`来测试。

想要能运行此代码，需要安装`selenium`，安装方法很简单：

```python
pip install selenium
```

另外，我们还需要`Chrome`驱动。驱动大家可以在网上搜索下载，官网需要科学上网。要注意的是下载的驱动要跟`Chrome`的版本匹配，然后将可执行文件存放在`Path`可以访问到的位置。

准备工作做好后，建立浏览器对象就很简单了，只需要引入对应的包，然后新建对象即可：

```python
from selenium import webdriver
driver = webdriver.Chrome()
```

效果如下：

![](https://user-gold-cdn.xitu.io/2019/12/20/16f23d1c2655c0b4?w=533&h=527&f=png&s=20034)

#### 访问对应的网址

由于每次预约的网址都不一样，所以需要提前定义好本次预约的网址。然后利用浏览器对象去访问它，代码还是一样的简单：

```python
url = 'https://eapply.abchina.com/coin/coin/*******'
driver.get(url)
```

效果如下：

![](https://user-gold-cdn.xitu.io/2019/12/20/16f23d270b455492?w=532&h=527&f=png&s=49389)

#### 填入信息

到这一步，网页其实跟我们自己访问时没有什么区别，只是需要把对应的信息一一填入对应的格子里，那我们接下来就来做这件事。

首先，我们需要让程序知道下一个信息要填写到哪里：

```python
ele_name = driver.find_element_by_xpath('//*[@id="name"]')
```

这个`//*[@id="name"]`可能不知道是怎么来的，其实很简单。打开网页之后，先按照[Python盘纪念币系列之二：识别验证码 01](https://juejin.im/post/5dee487751882512513529b8#heading-1)中的第二点找到小箭头，然后点击对应的输入框，在右侧源代码窗口对应位置右键，选择`Copy -> Copy XPath`即可获得。

获取到位置之后自然就是要把信息填写进去，也是相当简单：

```python
ele_name.send_keys('姓名')
```

这样就实现自动把“姓名”填写到对应的位置了，其他固定信息（证件号码、手机号码、
2020年贺岁币（第一批））也是同样的道理。


#### ToDo

1. 验证码处理
2. 下拉框处理
3. 日期处理

### 后记

限于篇幅，这里就先只写到这里，接下来的 **验证码处理**、**下拉框处理**、**日期处理** 会在下一期继续介绍，敬请期待。



本系列的所有源代码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/AutoTokenAppointment
```

> 接下来的会是本系列的最后一篇，主要内容包括验证码处理、下拉框处理、日期处理 ，敬请期待。

---

[第一期：Python盘纪念币系列之一：简介](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483772&idx=1&sn=d578c80bbb0216c5bf528a8cc4a3a89a&chksm=ea4bdabcdd3c53aa46796d7b96a5292361223b1f96a1a0579f9bd2c3a80886a27ca4d57a6d68&scene=21#wechat_redirect)

[第二期：Python盘纪念币系列之二：识别验证码 01](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483781&idx=1&sn=0bff3d3410b55f25a5528cfcd9454a41&chksm=ea4bda45dd3c5353ba6b6cc67ebe84cebabc06b53a39391e2d49be45a6e5b763ab4bd60b3979&scene=21#wechat_redirect)

[第三期：Python盘纪念币系列之二：识别验证码 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000138&idx=1&sn=442469c6418af28deedd24dbf4fa033b&chksm=6a4bda4a5d3c535ca5e7d46fdf4c837eabba8691fad6a881c56781e037a530952a6fd42e92c7#rd)

[第四期：Python盘纪念币系列之二：识别验证码 03](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000144&idx=1&sn=4541cf9fb5dfdf0df5b69193845ebb9a&chksm=6a4bda505d3c5346ae5fee707c6a6221d66b3ecd8f8ea70e31793140d83499925d3cfe3c2542#rd)

[第五期：Python盘纪念币系列之二：识别验证码 04](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000149&idx=1&sn=395d1ff104dfe1a2d5791e308ed81008&chksm=6a4bda555d3c53431f3632f976af24dc768b4be46ae73f3d67397ad7763f56aaf81b9ec52ddf#rd)
