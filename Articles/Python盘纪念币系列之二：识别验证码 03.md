
> 上一期的分割方法以失败告终（[Python盘纪念币系列之二：识别验证码 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000138&idx=1&sn=442469c6418af28deedd24dbf4fa033b&chksm=6a4bda4a5d3c535ca5e7d46fdf4c837eabba8691fad6a881c56781e037a530952a6fd42e92c7#rd)）。问题摆在这里总要解决，所以我想了另外一个方法

### 字符分割

第一种方法宣告失败。重新仔细观察图片，发现所有验证码图片中的字符大概都占据了原始图片`1/4`的位置。那是否可以将原始图片均匀切割成四等份，刚好每个字符都在独立的块中呢？下面是算法步骤：

1. 图片转换为灰度图

    ```python
    cap = get_gif_first_frame('1.jpg')
    cap = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
    ```
    
    ![](https://user-gold-cdn.xitu.io/2019/12/14/16f04a26773eb116?w=122&h=66&f=png&s=2060)

2. 将图片中像素值小于某个数的像素像素值全部置零，有效降低干扰

    ```python
    _, thresh = cv2.threshold(cap, 150, 255, cv2.THRESH_BINARY)
    ```

    ![](https://user-gold-cdn.xitu.io/2019/12/14/16f04a2f55425e09?w=123&h=67&f=png&s=1494)

3. 图片切为四份

    ```python
    width = thresh.shape[1]
    chars = [thresh[:, 0:int(width / 4)],
             thresh[:, int(width / 4):int(width / 2)],
             thresh[:, int(width / 2):int(3 * width / 4)],
             thresh[:, int(3 * width / 4):]]
    ```

    ![](https://user-gold-cdn.xitu.io/2019/12/14/16f04a42f981c72f?w=124&h=275&f=png&s=5523)

4. 在水平和垂直方向上去掉字符块上下左右侧的黑边，以第一个字符块在垂直方向的处理方法为例，以下是的具体算法步骤：

    1. 将每一行的像素值相加
    
        ```python
        vertical = [sum(char_patch[index, :]) for index in range(char_patch.shape[0])]
        ```
    
    2. 取出非零元素的下标，按照三种情况来取得字符块的边界。为了能完整切分字符，边界上下界下标特意各放宽了一个像素
    
        ```python
        item_cnt = len(vertical)
        zero_vertical_index = [index for index, value in enumerate(vertical) if value == 0]
        if 0 not in zero_vertical_index:
            first_index = 0
            last_index = zero_vertical_index[0] + 1
        elif item_cnt - 1 not in zero_vertical_index:
            first_index = zero_vertical_index[0] - 1
            last_index = item_cnt - 1
        else:
            target = [index for index, value in enumerate(zero_vertical_index[:-1])
        				if zero_vertical_index[index + 1] - zero_vertical_index[index] != 1]
            first_index = zero_vertical_index[target[0]] - 1
            last_index = zero_vertical_index[target[-1] + 1] + 1
        ```
    
    3. 切分字符
    
        ```python
        (v_f, v_l) = first_index, last_index
        target_char = char[v_f: v_l]
        ```
    
        ![](https://user-gold-cdn.xitu.io/2019/12/14/16f04d49075e5115?w=265&h=318&f=png&s=13227)
        
    4. 保存字符。由于前期并没有专门对验证码图片打标，所以在保存的时候需要告诉计算机要保存的字符是什么。另外，观察发现验证码字符的字体和大小基本没有什么变化，所以在这个问题中其实不需要太多的数据集，于是在实际操作中，我只解析了100张验证码（算是偷懒了~）。
    
        ```python
        class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
        'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T','U', 'V', 'W', 'X', 'Y',
        'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        class_ords = [ord(class_name) for class_name in class_names]
        class_cnt = {class_name: 0 for class_name in class_names}
        cv2.imshow('target_char', target_char)
        flag = cv2.waitKey(0)
        if flag in class_ords:
            class_name = class_names[class_ords.index(flag)]
            class_cnt[class_name] += 1
            cv2.imwrite(os.path.join(char_dir, '{}_{}.jpg'.format(class_name, str(class_cnt[class_name])))
                        , target_patch)
        ```
    
        ![](https://user-gold-cdn.xitu.io/2019/12/14/16f04fa5cebb7027?w=311&h=55&f=png&s=2723)
        
    
### 后记

至此，整个数据集的预处理到构建基本上就讲完了。

本系列的所有源代码都会放在下面的github仓库里面，有需要可以参考，有问题欢迎指正，谢谢！

```html
https://github.com/TitusWongCN/AutoTokenAppointment
```


> 下一步就是激动人心的模型设计与训练啦，敬请期待。


----
第一期：[Python盘纪念币系列之一：简介](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483772&idx=1&sn=d578c80bbb0216c5bf528a8cc4a3a89a&chksm=ea4bdabcdd3c53aa46796d7b96a5292361223b1f96a1a0579f9bd2c3a80886a27ca4d57a6d68&scene=21#wechat_redirect)

第二期：[Python盘纪念币系列之二：识别验证码 01](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=2247483781&idx=1&sn=0bff3d3410b55f25a5528cfcd9454a41&chksm=ea4bda45dd3c5353ba6b6cc67ebe84cebabc06b53a39391e2d49be45a6e5b763ab4bd60b3979&scene=21#wechat_redirect)

第三期：[Python盘纪念币系列之二：识别验证码 02](http://mp.weixin.qq.com/s?__biz=MzI2MjQ3NTQzOQ==&mid=100000138&idx=1&sn=442469c6418af28deedd24dbf4fa033b&chksm=6a4bda4a5d3c535ca5e7d46fdf4c837eabba8691fad6a881c56781e037a530952a6fd42e92c7#rd)