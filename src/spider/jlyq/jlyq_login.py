import os
import random
import time

import cv2
from DrissionPage.items import ChromiumFrame, ChromiumTab
from PIL import Image, ImageDraw

from src.config import COMMON_DOWNLOAD_PATH
from src.utils.logintools import Login
from src.utils.tabtools import EasyTab


def _draw_black(path: str, w: float, h: float) -> None:
    image = Image.open(path)
    draw = ImageDraw.Draw(image)
    color = (255, 0, 0)
    draw.rectangle(((.0, .0), (w, h)), fill=color)
    image.save(path)


def _find_all_template(im_source, im_search, threshold=0.5, maxcnt=0, rgb=False, bgremove=False):
    """
    Locate image position with cv2.templateFind

    Use pixel match to find pictures.

    Args:
        im_source(string): 图像、素材
        im_search(string): 需要查找的图片
        threshold: 阈值，当相识度小于该阈值的时候，就忽略掉

    Returns:
        A tuple of found [(point, score), ...]

    Raises:
        IOError: when file read error
    """
    # method = cv2.TM_CCORR_NORMED
    # method = cv2.TM_SQDIFF_NORMED
    method = cv2.TM_CCOEFF_NORMED
    DEBUG = False
    if rgb:
        s_bgr = cv2.split(im_search)  # Blue Green Red
        i_bgr = cv2.split(im_source)
        weight = (0.3, 0.3, 0.4)
        resbgr = [0, 0, 0]
        for i in range(3):  # bgr
            resbgr[i] = cv2.matchTemplate(i_bgr[i], s_bgr[i], method)
        res = resbgr[0] * weight[0] + resbgr[1] * weight[1] + resbgr[2] * weight[2]
    else:
        s_gray = cv2.cvtColor(im_search, cv2.COLOR_BGR2GRAY)
        i_gray = cv2.cvtColor(im_source, cv2.COLOR_BGR2GRAY)
        # 边界提取(来实现背景去除的功能)
        if bgremove:
            s_gray = cv2.Canny(s_gray, 100, 200)
            i_gray = cv2.Canny(i_gray, 100, 200)
            # cv2.imshow("s_gray", s_gray)
            # cv2.imshow("i_gray", i_gray)
            # cv2.waitKey(0)

        res = cv2.matchTemplate(i_gray, s_gray, method)
    w, h = im_search.shape[1], im_search.shape[0]

    result = []
    while True:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        if DEBUG:
            print('templmatch_value(thresh:%.1f) = %.3f' % (threshold, max_val))  # not show debug
        if max_val < threshold:
            break
        # calculator middle point
        middle_point = (top_left[0] + w / 2, top_left[1] + h / 2)
        result.append(dict(
            result=middle_point,
            rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]),
                       (top_left[0] + w, top_left[1] + h)),
            confidence=max_val
        ))
        if maxcnt and len(result) >= maxcnt:
            break
        # floodfill the already found area
        cv2.floodFill(res, None, max_loc, (-1000,), max_val - threshold + 0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)
    return result


def _get_img_location(big_img_path, small_img_path) -> tuple | None:
    big_img = cv2.imread(big_img_path)
    small_img = cv2.imread(small_img_path)
    result = _find_all_template(im_source=big_img, im_search=small_img, threshold=0.1, maxcnt=1, rgb=False,
                                bgremove=True)
    if result:
        return (
            result[0]["result"][0], result[0]["result"][1]
        )
    return None


def _try_slide(folder: str, tab: ChromiumTab):
    big_img_path: str = os.path.join(folder, f'[dyslide][bg][{int(time.time())}].png')
    small_img_path: str = os.path.join(folder, f'[dyslide][sg][{int(time.time())}].png')
    e_iframe = 'x://iframe'
    tab.wait.eles_loaded(e_iframe)
    time.sleep(1)
    iframe: ChromiumFrame = tab.get_frame(e_iframe)
    iframe.wait.doc_loaded()
    iframe.wait.displayed()
    time.sleep(1)
    e_big_img = 'c:[id="captcha_verify_image"]'
    iframe.wait.ele_displayed(e_big_img)
    big_img = iframe.ele(e_big_img)
    big_img.get_screenshot(big_img_path)
    big_img_size: tuple[float, float] = big_img.rect.size
    e_small_img = 'c:[id="captcha-verify_img_slide"]'
    small_img = iframe.ele(e_small_img)
    small_img.get_screenshot(small_img_path)
    small_img_size: tuple[float, float] = small_img.rect.size
    _draw_black(big_img_path, small_img_size[0], big_img_size[1])
    location: tuple | None = _get_img_location(big_img_path, small_img_path)
    if location is None:
        return False
    small_img_left_top: tuple[float, float] = small_img.rect.location
    tab.listen.start()
    small_img.drag_to(
        (int(small_img_left_top[0] + location[0]), int(small_img_left_top[1] + location[1])),
        random.randint(1, 2)
    )
    for dp in tab.listen.steps(timeout=15):
        if (dp.request.url.startswith('https://business.oceanengine.com/nbs/api/bm/user/global_var')
                and dp.response.status == 200
                and isinstance(dp.response.body, dict)
                and dp.response.body['code'] == 0):
            return True
    return False


def _is_logined(tab: ChromiumTab) -> bool:
    tab.listen.start('https://business.oceanengine.com/nbs/api/bm/user/global_var')
    tab.get('https://business.oceanengine.com/site/account-center/account/security/level')
    dp = tab.listen.wait(timeout=10, raise_err=True)
    return dp.response.status == 200 and isinstance(dp.response.body, dict) and dp.response.body['code'] == 0


def _nap():
    time.sleep(random.uniform(0.2, 0.3))


def _login(username: str, password: str, tab: ChromiumTab):
    et = EasyTab(tab)

    # 初始化
    et.get('https://business.oceanengine.com/login')

    # 账密
    et.click('c:.email.account-center-switch-button')
    et.input('c:[title="请输入邮箱"]', username)
    et.input('c:[title="密码"]', password)
    et.click('c:.account-center-agreement-check')

    # 滑块
    # tab.listen.start('https://sso.oceanengine.com/account_login/v2')
    tab.listen.start()
    et.click('c:.account-center-action-button')
    for dp in tab.listen.steps(timeout=10):
        if (dp.request.url.startswith('https://business.oceanengine.com/nbs/api/bm/user/global_var')
                and dp.response.status == 200
                and isinstance(dp.response.body, dict)
                and dp.response.body['code'] == 0):
            return
        if dp.request.url.startswith('https://sso.oceanengine.com/account_login/v2'):
            break
    tab.listen.stop()
    limit = 15
    for i in range(limit):
        if _try_slide(COMMON_DOWNLOAD_PATH, tab):
            tab.wait.eles_loaded('c:[id="header-user"]', raise_err=True)
            tab.wait.ele_displayed('c:[id="header-user"]', raise_err=True)
            time.sleep(1)
            return
        tab.get_frame('x://iframe').refresh()
        time.sleep(1)
    raise TimeoutError(f'未能在规定次数内({limit})验证成功')


class JlyqLogin(Login):

    def __init__(self, port: int, username: str, password: str):
        super().__init__(port, username)
        self._password = password

    def _login(self, tab: ChromiumTab) -> None:
        if _is_logined(tab):
            time.sleep(.5)
            return
        _login(self._username, self._password, tab)
        time.sleep(.5)
