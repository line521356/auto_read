import sys
import random
import time
from PIL import Image

if sys.version_info.major != 3:
    print('Please run under Python3')
    exit(1)
try:
    from common import debug, config, screenshot, UnicodeStreamFilter
    from common.auto_adb import auto_adb
    from common import apiutil
    from common.compression import resize_image
except Exception as ex:
    print(ex)
    print('请将脚本放在项目根目录中运行')
    print('请检查项目根目录中的 common 文件夹是否存在')
    exit(1)

VERSION = "0.0.1"

# 我申请的 Key，随便用，嘻嘻嘻
# 申请地址 http://ai.qq.com
AppID = '1106858595'
AppKey = 'bNUNgOpY6AeeJjFu'
FACE_PATH = 'face/'
DEBUG_SWITCH = True
GIRL_MIN_AGE = 18
BEAUTY_THRESHOLD = 80
adb = auto_adb()
config = config.open_accordant_config()

def _random_bias(num):
    """
    random bias
    :param num:
    :return:
    """
    print('num = ', num)
    return random.randint(-num, num)

def follow_user(device_name):
    """
    关注用户
    :return:
    """
    cmd = 'shell -s '+device_name+' input tap {x} {y}'.format(
        x=config['follow_bottom']['x'] + _random_bias(10),
        y=config['follow_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)


def thumbs_up(device_name):
    """
    点赞
    :return:
    """
    cmd = 'shell -s '+device_name+' input tap {x} {y}'.format(
        x=config['star_bottom']['x'] + _random_bias(10),
        y=config['star_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)


def init(device_name):
    time.sleep(1)
    screenshot.pull_screenshot(device_name)
    resize_image('autojump.png', 'optimized.png', 1024 * 1024)
    with open('optimized.png', 'rb') as bin_data:
        image_data = bin_data.read()

    ai_obj = apiutil.AiPlat(AppID, AppKey)
    rsp = ai_obj.face_detectface(image_data, 0)
    major_total = 0
    minor_total = 0
    if rsp['ret'] == 0:
        beauty = 0
        for face in rsp['data']['face_list']:
            print(face)
            face_area = (face['x'], face['y'], face['x'] + face['width'], face['y'] + face['height'])
            print(face_area)
            img = Image.open("optimized.png")
            cropped_img = img.crop(face_area).convert('RGB')
            cropped_img.save(FACE_PATH + face['face_id'] + '.png')
            # 性别判断
            if face['beauty'] > beauty and face['gender'] < 50:
                beauty = face['beauty']

            if face['age'] > GIRL_MIN_AGE:
                major_total += 1
            else:
                minor_total += 1

        # 是个美人儿~关注点赞走一波
        if beauty > BEAUTY_THRESHOLD and major_total > minor_total:
            print('发现漂亮妹子！！！')
            thumbs_up(device_name)
            follow_user(device_name)