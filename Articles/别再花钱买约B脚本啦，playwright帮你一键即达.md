> 
>
> 偷懒了近半年，每每想要写篇文章又不知道写什么好。正好前段时间看了篇`playwright`的技术文，觉得很适合小白来学习，正好来水一篇文章。

> 一月份的牛年纪念币想必大家都约到了，10元的面值近期最高涨到15元，50个点的收益率啊！如果大家自己能利用工具提高效率的话，收益还是很可观的。一如既往，本片文章只提供思路，具体实现还请各位读者自己摸索。

## 总结

本篇文章简单学习了`Python`的`playwright`包，并利用它生成了傻瓜式的自动脚本，非常适合新手学习和开发。

|    涉及概念    |        概念内容        |
| :------------: | :--------------------: |
| 主要`Python`库 |      `playwright`      |
|    主要概念    | 自动化测试、自动化脚本 |

## `playwright`安装

不像有些软件包需要自己编译才能安装，`playwright`的安装很简单，一句命令就能完成：

```cmd
pip install playwright
```

如果下载速度巨慢的话，可以考虑制定阿里或者豆瓣的源：

```cmd
pip install playwright -i https://mirrors.aliyun.com/pypi/simple/
```

上面安装好了`playwright`软件包，下面还得安装它内置的`Chromium`、`Firefox`、`WebKit`等浏览器的驱动文件，也是一句命令就能完成，不过需要等的时间可能会长一些：

```cmd
python -m playwright install
```

到这里，`playwright`就算是真正的安装完成了。

## `playwright`简单使用

`playwright`是微软开发的一款类似于`selenium`的自动化测试工具，但比`selenium`要简单得多，下面是项目主页：

```html
https://github.com/microsoft/playwright-python
```

### 桌面浏览器

`playwright`可以很方便的启动桌面浏览器，而且支持同步和异步的代码。

同步`API`：

```python
from playwright import sync_playwright

with sync_playwright() as p:
    for browser_type in [p.chromium, p.firefox, p.webkit]:
        browser = browser_type.launch()
        page = browser.newPage()
        page.goto('https://www.baidu.com/')
        page.screenshot(path=f'example-{browser_type.name}.png')
        browser.close()
```

异步`API`需要配合`asyncio`包使用：

```python
import asyncio
from playwright import async_playwright

async def main():
    async with async_playwright() as p:
        for browser_type in [p.chromium, p.firefox, p.webkit]:
            browser = await browser_type.launch()
            page = await browser.newPage()
            await page.goto('https://www.baidu.com/')
            await page.screenshot(path=f'example-{browser_type.name}.png')
            await browser.close()

asyncio.run(main())
```

上面的代码实现的功能一样，都是打开一个浏览器，然后自动导航到`https://www.baidu.com/`这个网站，最后对网页截图后保存到当前目录。如下图：

`chromium`：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/377954d6cbcd41f5a3e6df164265640a~tplv-k3u1fbpfcp-watermark.image)

`firefox`：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6c838cf587e64bfb879a6cb698d27fc9~tplv-k3u1fbpfcp-watermark.image)

`webkit`：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f0d490603ee64a26af450fa21d3e6bf6~tplv-k3u1fbpfcp-watermark.image)

三张图没什么区别，仔细观察还是可以发现字体有些区别的。这里要注意的是，上面程序运行的时候是不会出现浏览器窗口的，这也是“无头(headless)”浏览器的由来。如果想要看到浏览器，只需要在`launch`时指定`headless`参数：

```python
browser = browser_type.launch(headless=False)
```

### 手机浏览器

除了模拟桌面浏览器，`playwright`还能模拟手机模式：

```python
from playwright import sync_playwright

with sync_playwright() as p:
    iphone_x = p.devices['iPhone X']
    browser = p.webkit.launch()
    context = browser.newContext(**iphone_x)
    page = context.newPage()
    page.goto('https://www.baidu.com/')
    page.screenshot(path='example-iphone.png')
    browser.close()
```

输出图像如下（还不清楚为什么右侧有黑条，有知道的还请指导下 0.0）：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8f6847d401124a19873821467fe19002~tplv-k3u1fbpfcp-watermark.image)

### 浏览器中运行`JavaScript`

为了避免网站察觉我们是机器人，有时候需要在浏览器中运行`JS`代码，`playwright`也能轻松实现：

```python
from playwright import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False, slowMo=1000)
    page = browser.newPage()
    page.goto('https://www.baidu.com/')
    dimensions = page.evaluate('''() => {
      return {
        width: document.documentElement.clientWidth,
        height: document.documentElement.clientHeight,
        deviceScaleFactor: window.devicePixelRatio
      }
    }''')
    print(dimensions)
    browser.close()
```

上面的代码会输出：

```html
{'width': 1280, 'height': 720, 'deviceScaleFactor': 1}
```

## `playwright`自动生成代码

这个应该是`playwright`另外一个最牛逼的功能了。命令如下：

```shell
python -m playwright codegen
```

看看具体怎么使用：

```shell
~: python -m playwright codegen --help
Usage: index codegen [options] [url]

open page and generate code for user actions

Options:
  -o, --output <file name>  saves the generated script to a file
  --target <language>       language to use, one of javascript, python, python-async, csharp (default: "python")
  -h, --help                display help for command

Examples:

  $ codegen
  $ codegen --target=python
  $ -b webkit codegen https://example.com

```

由上面的帮助文档了解到，这句命令主要用三个参数：

```
-o 输出脚本的路径
–target 输出脚本的程序语言，默认为python
-b 指定浏览器驱动，以及默认网址
```

所以，如果我想要一个自动打开`chromium`浏览器并搜索`python`的脚本的话，这个命令就要这样写：

```
python -m playwright codegen --target python -o ./auto_script.py -b chromium https://www.baidu.com
```

<img src="F:\1.gif"  />

执行命令之后会自动打开浏览器并导航到百度，这时手动输入`python`并点击“百度一下”，最后关闭浏览器。动作完成之后，命令会在当前目录生成一个名为`auto_script.py`的脚本，内容如下：

```python
from playwright import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.newContext()

    # Open new page
    page = context.newPage()
    # Go to https://www.baidu.com/
    page.goto("https://www.baidu.com/")
    # Click input[name="wd"]
    page.click("input[name=\"wd\"]")
    # Fill input[name="wd"]
    page.fill("input[name=\"wd\"]", "python")
    # Go to https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=python&fenlei=256&rsv_pq=e4a6f92700029eae&rsv_t=b8545mdVOyJ8nn%2BdAb7T42XhONZny%2FRVkiL3tF5z8dKoH729P5bXjXBbnXU&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_sug3=7&rsv_sug1=5&rsv_sug7=100&rsv_btype=i&prefixsug=python&rsp=3&inputT=1975&rsv_sug4=2759
    page.goto("https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=python&fenlei=256&rsv_pq=e4a6f92700029eae&rsv_t=b8545mdVOyJ8nn%2BdAb7T42XhONZny%2FRVkiL3tF5z8dKoH729P5bXjXBbnXU&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_sug3=7&rsv_sug1=5&rsv_sug7=100&rsv_btype=i&prefixsug=python&rsp=3&inputT=1975&rsv_sug4=2759")
    # Close page
    page.close()
    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
```

运行这段代码，就能重现刚才手动执行的操作，是不是很简单？！

同样，要是用在纪念币上，会是什么样呢？给大家一个网址大家自己去尝试一下：

```html
https://eapply.abchina.com/coin/Coin/OrdinaryCoinRequest?issueid=I073&batchOrder=%202&t=1613823951232
```

## 后记

不管写什么，希望能跟更多人沟通，有问题或者需求随时欢迎交流。

我所有的项目源码都会放在下面的`github`仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/
```

下面是我的公众号，有兴趣可以扫一下：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a66ed052b3e142e6b6cb0efe0d4313be~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/00d84ee4e4bf47868f509f7206530655~tplv-k3u1fbpfcp-zoom-1.image)