# -*- coding=utf-8 -*-
import cv2
import os


def cv_show(win_name, img):
    cv2.imshow(win_name, img)
    flag = cv2.waitKey(0)
    return flag


def get_gif_first_frame(gif_path):
    gif = cv2.VideoCapture(gif_path)
    _, frame = gif.read()
    gif.release()
    return frame


def get_patch_edge(char_patch):
    horizontal = [sum(char_patch[:, index]) for index in range(char_patch.shape[1])]
    vertical = [sum(char_patch[index, :]) for index in range(char_patch.shape[0])]
    return get_list_zero(horizontal), get_list_zero(vertical)


def get_list_zero(sums):
    item_cnt = len(sums)
    zero_vertical_index = [index for index, value in enumerate(sums) if value == 0]
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
    first_index = first_index if first_index > -1 else 0
    last_index = last_index if last_index < item_cnt else item_cnt - 1
    return first_index, last_index


def get_cutted_patches(cap):
    if len(cap.shape) > 2 and cap.shape[-1] == 3:
        cap = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(cap, 150, 255, cv2.THRESH_BINARY)
    # cv_show('thresh', thresh)
    width = thresh.shape[1]
    chars = [thresh[:, 0:int(width / 4)],
             thresh[:, int(width / 4):int(width / 2)],
             thresh[:, int(width / 2):int(3 * width / 4)],
             thresh[:, int(3 * width / 4):]]
    target_patches = []
    for index, char in enumerate(chars):
        try:
            (h_f, h_l), (v_f, v_l) = get_patch_edge(char)
            # print((h_f, h_l), (v_f, v_l))
        except:
            continue
        target_patches.append(char[v_f: v_l, h_f: h_l])
    return target_patches


if __name__ == '__main__':
    captcha_dir = './captchas/'
    char_dir = './test_chars/'
    class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
               'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    class_ords = [ord(class_name) for class_name in class_names]
    class_cnt = {class_name: 0 for class_name in class_names}
    _ = [os.system('mkdir "{}"'.format(os.path.join(char_dir, class_name))) for class_name in class_names]
    for index, captcha in enumerate(os.listdir(captcha_dir)):
        if index < 600:
            continue
        print(index, captcha)
        cap_path = os.path.join(captcha_dir, captcha)
        cap = get_gif_first_frame(cap_path)
        target_patches = get_cutted_patches(cap)
        for target_patch in target_patches:
            while True:
                flag = cv_show('patch', target_patch)
                if flag in class_ords:
                    class_name = class_names[class_ords.index(flag)]
                    class_cnt[class_name] += 1
                    cv2.imwrite(os.path.join(char_dir, class_name, '{}.jpg'.format(str(class_cnt[class_name])))
                                , target_patch)
                    break
                else:
                    continue
        cv2.destroyAllWindows()
