# -*- coding: utf-8 -*-  
"""
@Date     : 2025-01-06
@Author   : xwq
@Desc     : <None>

"""
import base64
import logging
import os.path
import random
import time

import requests
from DrissionPage.items import ChromiumTab
from PIL import Image
from PIL.ImageFile import ImageFile

from src import get_config
from src.config import COMMON_DOWNLOAD_PATH
from src.error.login_error import LoginVerifyError, LoginSmsError


def _location(img: str) -> list[tuple[int, int]] | None:
    """
    识别图片应点击位置
    :param img: 图片地址
    """
    with open(img, 'rb') as f:
        b = base64.b64encode(f.read()).decode()
    response = requests.post(
        url='https://api.jfbym.com/api/YmServer/customApi',
        headers={'Content-Type': 'application/json'},
        json={
            "token": get_config('ym', 'token'),
            "type": "88888",
            "image": b,
        }
    )
    jsn = response.json()
    if jsn['code'] != 10000:
        raise LoginVerifyError(f'云码平台响应错误: {jsn}')
    result = [x.split(',') for x in jsn['data']['data'].split('|')]
    result = [(int(x[0]), int(x[1])) for x in result]
    return result


def _white(img: ImageFile) -> ImageFile:
    if img.mode in ('RGBA', 'LA') or (img.mode == 'p' and 'transparency' in img.info):
        white_background = Image.new('RGB', img.size, (255, 255, 255))
        white_background.paste(img, mask=img.split()[3])
        img = white_background
    return img


def _contact(top_image_path: str, bottom_image_path: str, final_img_path: str) -> None:
    """
    纵向拼接两张图片
    :param top_image_path:
    :param bottom_image_path:
    """
    top_image = Image.open(top_image_path)
    bottom_image = Image.open(bottom_image_path)
    new_width = max(top_image.width, bottom_image.width)
    new_height = top_image.height + bottom_image.height

    bottom_image = _white(bottom_image)

    new_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))
    new_image.paste(top_image, (0, 0))
    new_image.paste(bottom_image, (0, top_image.height))
    new_image.save(final_img_path)


def _coordinate(*coordinate: tuple[int, int]) -> tuple[int, int]:
    x = 0
    y = 0
    for a, b in coordinate:
        x += a
        y += b
    return x, y


def _download(tab: ChromiumTab, loc: str, path: str):
    tab.wait.eles_loaded(loc, raise_err=True)
    tab.wait.ele_displayed(loc, raise_err=True)
    img_size = tab.ele(loc).rect.size
    img_size = (int(img_size[0]), int(img_size[1]))
    img_src = tab.ele(loc).attr('src')
    with open(path, 'wb') as f:
        f.write(requests.get(img_src).content)
    img = Image.open(path)
    img.resize(img_size, Image.ADAPTIVE)
    img.save(path)


def _verify(tab: ChromiumTab, gap: int = 5):
    """
    点选验证
    :param tab:
    """

    folder = COMMON_DOWNLOAD_PATH
    e_small_img = 'c:.vipsc_qimg'
    small_img_path = os.path.join(folder, f'small_img_{int(time.time() * 1000)}_{int(random.random() * 10000)}.png')
    _download(tab, e_small_img, small_img_path)

    e_login_button = 'c:[id="J_login_submit"]'
    tab.actions.move_to(e_login_button)
    time.sleep(1)
    tab.ele(e_small_img).click()
    e_big_img = 'c:.vipsc_code_img'
    big_img_path = os.path.join(folder, f'big_img_{int(time.time() * 1000)}_{int(random.random() * 10000)}.png')
    _download(tab, e_big_img, big_img_path)

    contact_img_path = os.path.join(folder, f'contact_img_{int(time.time())}_{int(random.random())}.png')
    _contact(big_img_path, small_img_path, contact_img_path)

    location = _location(contact_img_path)
    if len(location) != 3:
        return False

    small_img_location = tab.ele(e_small_img).rect.location
    small_img_location = (int(small_img_location[0]), int(small_img_location[1]))
    tab.actions.move_to(_coordinate(small_img_location, (-200, 0))).click()
    tab.actions.move_to(e_small_img).click()
    tab.wait.ele_displayed(e_big_img, raise_err=True)
    left_top = tab.ele('c:.vipsc_code_img').rect.location
    left_top = (int(left_top[0]) + gap, int(left_top[1]) + gap)

    tab.listen.start('https://captcha-pc.vip.com/check')
    for x, y in location:
        tab.actions.move_to(_coordinate(left_top, (x, y)), duration=random.uniform(0.3, 0.5)).click()
        time.sleep(.5)
    dp = tab.listen.wait(timeout=10, raise_err=True)
    return dp.response.body['message'] == 'SUCCESS'


def verify(tab: ChromiumTab, gap: int = 5):
    """
    点选验证
    :param tab:
    :param gap:
    """
    e_another = 'x://span[text()="换一张"]'
    tab.wait.ele_displayed(e_another, raise_err=True)
    tab.actions.move_to(e_another).click()
    time.sleep(1)
    limit = 10
    for i in range(limit):
        logging.info(f'第{i + 1}次尝试点选')
        if _verify(tab, gap):
            return
        time.sleep(1)
    raise LoginSmsError(f'限定{limit}次尝试均未能成功登录')
