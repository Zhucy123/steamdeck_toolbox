#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
try:
    gi.require_version('Vte', '2.91')
    from gi.repository import Vte
    VTE_AVAILABLE = True
except (ValueError, ImportError):
    VTE_AVAILABLE = False

from gi.repository import Gtk, GLib, GdkPixbuf, Gdk, Pango
import subprocess
import os
import sys
import re
import json
import tempfile
import shutil
import threading
import time
import urllib.request
import atexit
import base64
import signal

# ============================================================================
# 版本定义
# ============================================================================
VERSION = "1.8.0"
REPO_RAW_URL = "https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_gui.py"
REPO_URL = "https://gitee.com/Zhucy2100/steamdeck_toolbox"
VERSION_CHECK_TIMEOUT = 10

# ============================================================================
# 内嵌图标（base64，脚本自包含，无需外部文件夹）
# 图标数据来自仓库 emoji_icons/，运行时优先使用脚本旁 emoji_icons/ 的自定义文件
# ============================================================================
EMBEDDED_ICONS = {
    "clipboard_twemoji.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAPFBMVEVHcEzM1t3M1t3M1t3M1t3M1t2Zoqg9REgpLzPM1t3M1t3M1t3BaU/BaU/BaU/CcFjgtKf////M1dqZqrWLZiLOAAAADnRSTlMAIJ/v/zD///8QUN9Q360w504AAADiSURBVHgB7dhVgoUwEERRIIVrw/7XOoI7HRl9fRdwgKS+8J7yAwWowPcsCxX6VGjn+ApRnCRxBOVbQQGipC9CYAUpxAMUQ9k4KZCMAZ52WY6lBZrLM6aDVcunreNJOVYth70uZ57Luun6t90BRVn11WBUDZXFiVNNcaG+o1SaQeUBqsyg6s9ADRGBERE1txDxIfprELPfBgnUdie1BlB3mjPoxz6Nn+zovtbw+o99I2T/abKjv78j2ZHsSHYkUOvqsLvT3EPmnyY7aohdcwMZ9Beg0swpD1BhBhWnP1m0KxfnHV+T0IbfZ3ihAAAAAElFTkSuQmCC",
    "game_controller.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEwpLjQxNz0xNz0jJywjJywUFxoVGBsnLDEUFxorMTYwNjwbHyMmKzAUFxoxNz0VGBsUFxoxNz0UFxopLjMxNz0bHiAUFxpMVl0jKS4pLzMuNDoeIyY+Rk1fa3VndX9SXmZWYmtETVSImaY0O0EjO01OHSY8VjLwwUp0YC40YofdLkRfjUeBkZ13slVEiL3/zE1QpeY1HiHEn0BGZTijJzh1Ii5SeD++Kj1upE+KcjSniDpreYNygYwfMkBdUCo3DEEFAAAAFXRSTlMAgL+kMCCfv0HnXOhwEI/Pz2CPr++5YFXqAAAC8ElEQVR4Xu2W2ZKbMBBFBQZj8DYepyV2vG+z72uS//+rSAJstWUSM/MYnyfXpfpUq1uUIYITJ06csDpDlx3B2bBjk2oGZ6wGzqBC03JZTRzrkKfHvkBH9zTZl2hWe8D3/QmtFryvbldr3aSf62rKmVR61reC3xWnaykFU4FfKXqQogclUSfufkd0tvMY7HjRhxR9qNEANXSs6H7FPSvKDrXkoYKUe67CQ475ZjNnjK7f19yzeH5ebKeEVxZOBT9pyj2J/D1Gns0dZ1METxecxd7iijcMpoVpzD2ST9UT3EmC/IAXknsmcQoRQ6JpJnrTRfNcNJfBs/SULblE0sWiq3BG03+JFqgjhm8jFJ5EzEkXsRvhuckD+io8r0wTSUAQJHJO+W8k+sVNN2V0z6f9RLHIZqzGPWKP19dvjwxDcmqJlteCJcrcQuTWEV1K0SXKHHyPvi8K6ohepOgFZW0isQCl408OciPiN9EQVSMKxfohYDWgy8clRUkALSkyIGLfgUbgSVEDIDjwNElmMc7iWZJEuigEMKTIBICYYWZpJphQRe3LKN1XxQDQkCLgRBR7soLxzjMusxluHTh94emCZgqyLUmZTbZRGuMBCfKlaSZ/J0rLgmzHRDlX7gGbizyQqBNPlaoiDZVopMy5oCW3XxKVPWcKYbUoiKDEkEtTCKQrPUIUB6BwzkV9QFA8o6wchhL5clkIk4sAI1oKcZHr8myEmwwA0SbEBkyI1jYWDfaaoqUULS0CjNw+hiq3ZiQ8rm3L0Y6VmxXDHhbpgNaSIE5GIz8q/0d7Mpv5o1ESM70huX8DMNob3NQ/DGmoFRmkARo/XMXT0z8x3R9wQGRqWd+2t2VOixR4W3uza7U1kUm0rN/lZfag6ThDwyIKljF0nN5APO72ddF+0iDH0DU1UQ0PovH3o3nkaM6xCJnbHqmBh9/aluKxSC085TS20mLfIjXZXYOOclizS2pj98vrKGk1TLPhkS/hmbzWJv85J/4AvtAeEDjvcnoAAAAASUVORK5CYII=",
    "globe.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAM1BMVEVHcEw7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMM7iMMRH0i/AAAAEHRSTlMAgL8Q32AgQO+fj1CvzzBw4ZaNVwAAAg5JREFUeF7lmMtyhiAMhaPcUX59/6ftAOoBp6At6apZZQb4cggRAeqYVn6W+2Fy9krTL2xxFwMm3fIzivZ2b5j173WZde/aat6pcZUAt0Vnc5VE90LVVI6QShBFh0goWfKnJzmhDDwJohNEJKayLXRFLaUca4gAimaq5s4CHiGDTJwP3UH0SSR5yG5Oz+VI2wYOQCVp27I01+OEj7bgAFSSrP6ETGpznKA5Ooq+B5GKgJmEa5GmzDl6rtQC0XrEcd/nabkCyKhdtEEiTk5eU7itnbYnR+WATRB6ZJKt6ylkziFIUgeELpkU6gQN2FRNbMCKybkBTFkDZh80U1WGiSZzDbWTjRHzIQIjdPLhqi4IFZBTM8P1SR06iGeQSAEhySfXXjrJwe2Bsg4H114fh0KpTW9AE8pWnR+KS0QoNm9ApsiBLT5SVzf3QfeQLqvThzIIfgQhCdg4dLVQHrlug5BiXy2hhwq09kGICXU+odcCNL0DTRmEOq9WHOnqgZCYqhbyBAEy70AGoJxmDP4dCP7OYP8B9Jxsc7ctAkqfbfnZCpLtE2H7aNm2EbaNjWurZdv82X5HXD9Itl827yGCVkgK7481AYJWtoMW19GP7TDKdTxuH9hDf4eM+mV00qjAdoXgutRwXbO4Ln5cV1HGyzH/dZ3/AeH5ScPXTxpMjyxczz5cD1H8T2P8j3Vsz4dfTyiMV5arauoAAAAASUVORK5CYII=",
    "hammer_wrench.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAjVBMVEVHcEyImaaImaaImaaImaZmdX9mdX+ImaaImaZmdX/0kAyImab0kAyImaZmdX+ImaaImaaImab0kAxmdX9mdX9mdX9mdX9mdX9mdX+Imab0kAyImaaImaZmdX/0kAxmdX9mdX9mdX/0kAz0kAz0kAyTmJdmdX/0kAyImaZmdX/0kAzgkim/hjePmJzMk0bf6kn5AAAAKHRSTlMAQIDvz+8wnxCfECCfYL+P37+A32CAj0DPUM8wr1DvcBCvUGBwnyAguBawEwAAAiJJREFUeNrd1+uSmkAQhuFvQARBDp511dXd7CbD5nD/lxedStkjkPm2zb+8F/AUzTQ1BUKNV1XSXkuq1QZSmTbW2niHz7VctH7J+oxrWRTbP2UA7+iYu064ZBp7qwDt/NJjkmoMoLRSCtp46xOTzRkuvZN4TPUVrn911pCK+HFnCa/0cecEr+Jxp4JffXMapdNu4CcbVCudBf4yWYT7iizotC/wMwIdgM4h7EJOu4JfJFCcdRwbDzkcslFvKUJOu+5C0r7j2IDTPf2dD8V7cVwhp01yeO3tXVHmOw2ubcbi+P14ynvvQooPUd34qz5eXIYYdD4+RBJnsFJmGnJEIk5MHCdxx63DNuCIRJwmA4jjJOZYA4A4TnonTolL666xWK+2zpG+/+QOMLnfwRMuTQWhUuycnrQBdFJaAEPSBBqpqYXpSAk+I6X7XRRFRpS+tEVA4neISEcwyTlUWgJEcg6ROg7SX0NSCtKyqo7du6EvicMTZ0B6f8zpS0+53iGSyuESd4ikd7jEHS5xh0t6h0vckdJpQNI4QEBSOURSOERSOFziDpHUDpe4wyXuMEnjcIk7SqkOOBrJBByVNLOumDhUyuy1UYFiRBwimdsPTxZ7jkaaCjSTIfsOl77doBGujcTRSW/yjkoApThKae4NdIhScTSSQIadO5fe4KqJQ6XnHF2pBh6QvshXMnPMzEDV/Nk9z8WRMmNMBm3563z+muO/7je+6nfRvPo7kwAAAABJRU5ErkJggg==",
    "inbox.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAYFBMVEVHcEzBaU/BaU/BaU/ZnoLBaU/ZnoJ3slV3slV3slXZnoLBaU93slV3slV3slV3slV3slV3slV3slV3slV3slXBaU/ZnoJmIRNtKRrSlnuKSDaRUD21d1+nZ1GYWER3slVIZBYuAAAAFXRSTlMAv88g72Cfn2BAIO+AEN9Q778wr3AL/u/gAAABHklEQVR42u3R2U7DMBCF4ckKTZM2ZRnsLPX7vyWFSj0KtevY4wsQ+R/g0+gMPeytN7cOO4quNYteYp2uX0KvsdDO/GiDNmiDfiF0MqtqfU5n1nUiX0/roCOlkZ6JZBIcmQRHJsGRSXBkEhyZBEcmwZFJcGQSHJkERybBkUlwZBIcmQRHKMER1vbGHI6Uoo7+e01d8l0fD+K7yrq5OGDCIVAN1WxLuR3Ftmoq2dbghga2VRJbm93QzNYckHZDOgji0eWMHAZp5ZhaB0I82aGJQyE+25wzeyCPBCcG4kktGTVxHMR6XPxLczAEah7U9zHDDMYDedugDfpL0Hui0kFZGiejKg1UEeUpnJyIir3c2Rf0JeXiewq6VmWinSu69AktjxkykvjpqwAAAABJRU5ErkJggg==",
    "package.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEzBaU/ZnoLBaU/ZnoJmIRPZtKTSjnPZnoLYn4RmIRPZnoJmIRNmIRPZnoLZnoLBaU/BaU9mIRPBaU9mIRNmIRPZnoLBaU/X3+XT3OPZnoLBaU/X3+XX3+VmIRPZnoLBaU/M1t1mIRPh6O2ZqrXf5OnCbVTFd17EhW3Zo4jY4ObTlHnM0tfbrpnMy83RwbrYqJHfzcXR2uHPim+im553NCPdv7GhsbyuvMaDQC++joFtKRrUtKXg3Nuub1iXVkI382ntAAAAH3RSTlMA0iCmhDcwEMjv79/JEKJG70ZgaKuIYDBgGHCAn88gug289wAAAlFJREFUeF6t04la2zAQBGBjnMMkEJISSgutJN+5T47e7/9WDcTNJF25WsmdB/g/73jkGRN0hGj3vLpptcVbgppOsyPKtFt1nNtQHNJpujuBOMltzXqQK6fzmqEgafv2zl2czqgUWu/gId7liUC2O/jwKX7LjxEElx00VRqXEs5z2MGdUmpcSjjPfgcPSh1LK5zH2gHqUfusY5znsINeOFVlDkWlT/Y7+CjEcl46OC9dWe6gdSV2GS2UwnkuO/D/PK7vkA7nWeygh8c1Q1EWO0A9yAhF2e4gEKfRFTXTSAQCgaI4O/i7cV+QLDVFrYyQt4GAojTnLU+dCTntcSJoFqYdTDICRd8KALQo/Q42maRQFP0UrKKwg0JKLRT9EoyisINcVkFRdVF0B5NMVkPsotLVrp4KqJT0RZHzxlL+CzIUhR2slRmKvhiKGsfpWnGg6LGqKMQEsYp6eTZDjKKmL0nCh/RFjRY75znhQKaiFvMkKaGMCemLKpIDVPAgfVG5TOy/iBY1ySWgKa8jWtT+kQL6yoRoURspAU1Lhw2hqFweQfNC8iEU9epk8gjaZtIFil4heQThrBrQNtnm8n9AElfVhKQRunGDzgnUcIP6HsnABXoHAGlc2ELXfU+by64ddNbyqjJkQ+hZn8EFF7pGPdo0ujzo7L1nyOWNAUI9pgzN0D2DwQ4ohL/OzOcuhfj10KL00Dnq4WRAIPoo+EUBsqqHPhhA+OsuGQJiPArDgwFkeBSmBwNI/9f5Oygh/HXXDPfQvVc7jVCIsA/APX4Q+GbgN8dXd0WtHL/wAAAAAElFTkSuQmCC",
    "pushpin.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAllBMVEVHcEzdLkTdLkSZqrXdLkSZqrXdLkTdLkTdLkSZqrXdLkTdLkSZqrXdLkTdLkSZqrWZqrWZqrXdLkSZqrW+GTHFHjXdLkS+GTGZqrW+GTG+GTHdLkSZqrW+GTGZqrW+GTG+GTHdLkSqi5m+GTGZqrXaLEKZqrXdLkS+GTGZqrXVKT/KITjXKkDRJj3ZK0LAGjKdoq7QRVknDsMFAAAAJ3RSTlMAv+/vgBBwnxDP38+PMCAwUL9gYJ/fUDCf78+vcBDfUHBAQN8gr4BIwjJqAAAB4klEQVR42q3X2XLCMAxAUcVx9rAFChRogW62u9D2/3+u60RpgyOBcl+ZOTORIwNwWmkc5CZfVynI0sr8pGIJkwYGSwRQgoxIqhCRSbnpRxqgIJNi05OkjVRCSC4hJJcWF6YXaXtpD31IO2vtk5FLM/vVo1S6WtnvXp9l0uLWWkqKeWO2pKQ8N91w/2fMDKmCdtXafJYnQxwzLa3bS17UH+p6zLSUtxxlsPt6zLT0z0mVafZiuVLevpbPk4J/p2XMmVJM3IJcSaWdT8aXNPwtMOdJAXghWnps7Gzqv05pyT4dfk9+Dq3mhiFhF1rreADHUqdIlwviW5ArbaGjgC/toKu04EozwCTSCjCJdHsFcgkPTC5tAcQSHphcmgG7m/cOacV3ous3v4QHRpc555fu+c7SuS5Jc52Nc93SkOeMnSOkhOWMQkdJOevAMudIiQNNXKPrm+IotKedsulkEaTFedOeNp2ld1voQTedjXfv1uSgQ2TCsX+DK3oz6rKR/y4o6M2om0T+W0UN+IMuPf+v0eENegqtYoU/GKgrqB7zCI4110GQxEP+G51FIKnEt1DUGMcj6i78XdIRyMrw7eljQCUIG+NykdGrmt2BtAk+lqgpPpbwwfC0RD24cAN9VD5EvTgfMdE81SP5ZWQAAAAASUVORK5CYII=",
    "refresh.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAARVBMVEVHcEw7iMM7iMM7iMM7iMM7iMP///9sptLO4fC20ulUl8udxOFgns7a6fQ7iMPz+PuFtdrC2uypy+VHj8eRvN3n8Ph4rdZhf4NlAAAABnRSTlMAv+9gIM+kpfmZAAAB20lEQVR4Xt3Y227DIAyA4XRtbXMmPb3/o04Lm1hmiK3C1f7r5FMkBAGWr86nONDpvJQu1zjY9bI5H3G4jy/pGid0XZZznNJ5Oc2BTkuclAa621HIZkNQSmSyfQ+ytyf86XmzGsj/ZpCgGaEMkakmQTfyIgQ/koPDnAAFKJIPIBT8IQSwSZhALKEEgcmgKvch2wLS6nDLrYlJHQg5Y3ZjjWYnoRoybGbY31TyHeghj8x+REMHcjvHxE6mSk4BPSKPf7lvQsQ+SJRIgCSpjh62oACSxB9dWxCAWvLwkxUgSTJ84JbuDCHKDGAPBw7h99urcxnxXgD5kyyD7uVtZS82d5f4XglKt1FohRKNQg5KqQlZxIfVQQjfMYgCbOEoBPA/oECjkM2ItrlCJjYNVXGIoLSOQjcopVEow3cvDcAnOl+PjPx2dm4lqmPTWbNt18hE8CfLIadcYvcd7ka8IAlQXNlCLEuhBaH671ijHcT/tQ9BEiCv30Q0/2s1p9vWyFAMuo1W7dGBfFJt/WrYgSIKm1E1FLN2e8x3I0xSlcvnxS6kP0IYAdIeajYpHEH6Y5YBEiDtwc8IkP4o6ucfjuXjelIf1+UqIEPjTbtkmXbtM+siatrV2LzLumnXh58fkO/Lo6a6oQAAAABJRU5ErkJggg==",
    "trash.png": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAP1BMVEVHcExndX9ndX9ndX+aqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrSaqrRndX8VtlsmAAAAFXRSTlMAUN//v/9gQM+fMK+AIBDvcI/fUBDdJcf4AAADVElEQVR4AazRAQ0AMBCDQNr697xMw3MOCJDurIFMETpFmYRJvLRMEW//9xgto3VJQRgGc4EoKoD4/u+6Z/XHbc7Xi+3NGIcGJ4ll4vJT6blcF2oLitcXb4rT38sYnoIImJdZu+L8wH2xmM7jIzqfr8rPVW2y0uBWLS+4PJfnR9QffPGo30rFyfKCr+eqBwoh2ifByUrwJxq854fblIsq7IEEuS6IBs6I9kqyVPDDiybUQmdmh4MF4PXlY8MjgOFdwr8aGPU86gjhfkWrE49XtFeSe2IsHIYIahSazC1NjGjwglluYjTVp8p3o01cDLwQlXpvSJCoA/kFH2YfwRIjNKGSvArgZFJgMZpJkKgWdCW46T5gTDalv5gMg0XFVgWL+0q0cycr3uVdBTtEUSTg1wpGtFWxuC8u5F8h7ebFlvBlcdXxvyrR+a1Qouq4z35U10QM4cVrp0EUkc4DvOqCQ3nVfU3yrjfyL0mK8HLD9T97oqkk8Ir7KgGRE9xVkiFxBWuQZiV99KG8y6qvmsaIyF9kkEenVnipTBpZfgkNmpTxyo0krdMJb2+Itr+PWiVGNjbr7OQTvlphgG/yBhssCVJiEiLJTkdK8O+IxuQsNkbi/0kMMw1os21oxQbZHibBI8oyKrtxC/e6DMZkicT/KJOvmlyiapVJeuK+1vFuevmHgA59bL+ESPy3nbcElY7b8kZ1n+q8sJtGP8nQRzRSuyGk4/9Kp0ksojXgZXjp+FUFoyqdRUdqNst4syu/wQ0SnQx9jgtp2CaviZHWQNGo0yGJRFOkiPAs84JUjGncplNsK16MjIx8ECM0sZodEiOkc4JUQ9POc8JTeZsTIxkkSUcskqAGaUO0DQHcIN1RRyySIBq8iObHCP91xCLJFE1H7s6L7RM1Gc5IQhUd5VFjpP5TOFeROkbkrvK1676MiEZ8O5KkhGid0DchkhKnLzrGqsN/HfBfmglvkMhxtGxyHAE5juB0CkvkgISXTj0gXfcltUnzI0c2eUrfHm7x7f/8iQAEv4b7t6bwtKJvhtSvyO+WzkOzIX+0fPeZIMOyIgmi2d7Bw7t12mgkHfozhMlbq/VnjEzkDxwgANnjSJgmMZE7uIIGRJjJBDQyiHKvUR7YVI9+ALq4Sv5opt7bAAAAAElFTkSuQmCC",
}

# ============================================================================
# 全局样式与工具函数
# ============================================================================
# ============================================================================
# 主题（深色 / 浅色）
# ============================================================================
# 配色表：键名相同，两套值不同，CSS 模板通过 {key} 占位符注入。
THEME_DARK = {
    "bg": "#0d1219", "bg_alt": "#101720", "panel": "#151d26", "panel_hi": "#1b2531",
    "border": "#26313e", "accent": "#1a9fff", "accent_dark": "#0f6cbd",
    "text": "#e6edf4", "dim": "#8b98a6",
    "header_top": "#1c2733", "header_bottom": "#131a22", "header_border": "#070a0e",
    "header_backdrop_top": "#161e28", "header_backdrop_bottom": "#11171e",
    "title": "#ffffff", "search_bg": "#0a0f15",
    "sidebar_header_top": "#16202a", "sidebar_header_bottom": "#111820",
    "bottom_top": "#131a22", "bottom_bottom": "#0e141b",
    "hover": "rgba(255, 255, 255, 0.06)",
    "scrollbar": "rgba(255, 255, 255, 0.16)",
    "btn_ghost": "rgba(255, 255, 255, 0.07)", "btn_ghost_border": "rgba(255, 255, 255, 0.09)",
    "titlebtn": "rgba(255, 255, 255, 0.10)", "titlebtn_border": "rgba(255, 255, 255, 0.16)",
    "titlebtn_hover": "rgba(255, 255, 255, 0.24)",
    "shadow": "rgba(0, 0, 0, 0.45)",
    "sel_text": "#ffffff",
    "suggested_hover": "#3aaeff",
    "destructive": "#a63d3c", "destructive_border": "#c95352",
    "destructive_hover": "#c14948", "destructive_hover_border": "#e06766",
    "close_hover": "#c0392b", "close_hover_border": "#e05a4a",
    "alpha_accent_hover": "0.14", "alpha_accent_btn": "0.28", "alpha_accent_head": "0.30",
}

THEME_LIGHT = {
    "bg": "#f2f5f9", "bg_alt": "#e8eef5", "panel": "#ffffff", "panel_hi": "#eef3f9",
    "border": "#c9d5e3", "accent": "#0a7ddb", "accent_dark": "#085fa8",
    "text": "#1a2531", "dim": "#5d6b7a",
    "header_top": "#ffffff", "header_bottom": "#e9eff6", "header_border": "#c2cfdd",
    "header_backdrop_top": "#f7fafd", "header_backdrop_bottom": "#eef4fa",
    "title": "#10202e", "search_bg": "#ffffff",
    "sidebar_header_top": "#eef4fa", "sidebar_header_bottom": "#e3ebf4",
    "bottom_top": "#e9eff6", "bottom_bottom": "#dde6ef",
    "hover": "rgba(10, 125, 219, 0.10)",
    "scrollbar": "rgba(26, 37, 49, 0.22)",
    "btn_ghost": "rgba(0, 0, 0, 0.05)", "btn_ghost_border": "rgba(0, 0, 0, 0.10)",
    "titlebtn": "rgba(0, 0, 0, 0.06)", "titlebtn_border": "rgba(0, 0, 0, 0.12)",
    "titlebtn_hover": "rgba(0, 0, 0, 0.14)",
    "shadow": "rgba(30, 50, 70, 0.18)",
    "sel_text": "#ffffff",
    "suggested_hover": "#1a8fe8",
    "destructive": "#c0392b", "destructive_border": "#a93226",
    "destructive_hover": "#d0453a", "destructive_hover_border": "#c0392b",
    "close_hover": "#c0392b", "close_hover_border": "#e05a4a",
    "alpha_accent_hover": "0.12", "alpha_accent_btn": "0.20", "alpha_accent_head": "0.22",
}

# CSS 模板：所有颜色来自上面的主题字典，深浅模式共用同一份样式结构
APP_CSS_TEMPLATE = """
/* =====================================================================
   Steam Deck 风格主题（深色 / 浅色可切换）
   圆角卡片 + 触控友好行高
   ===================================================================== */
@define-color sd_bg {bg};
@define-color sd_bg_alt {bg_alt};
@define-color sd_panel {panel};
@define-color sd_panel_hi {panel_hi};
@define-color sd_border {border};
@define-color sd_accent {accent};
@define-color sd_accent_dark {accent_dark};
@define-color sd_text {text};
@define-color sd_dim {dim};

window {{ background-color: @sd_bg; color: @sd_text; }}
.background {{ background-color: @sd_bg; }}

/* ---------- 顶部标题栏 ---------- */
headerbar {{
    min-height: 46px;
    padding: 0 10px;
    background-image: linear-gradient(to bottom, {header_top}, {header_bottom});
    border-bottom: 1px solid {header_border};
    color: @sd_text;
    box-shadow: 0 2px 6px {shadow};
}}
headerbar:backdrop {{ background-image: linear-gradient(to bottom, {header_backdrop_top}, {header_backdrop_bottom}); }}
headerbar .title {{ font-weight: 700; font-size: 15px; color: {title}; }}
headerbar .subtitle {{ font-size: 11px; color: @sd_dim; }}
headerbar button {{
    background-image: none;
    background-color: {btn_ghost};
    border: 1px solid {btn_ghost_border};
    border-radius: 9px;
    color: @sd_text;
    min-height: 26px;
    padding: 0 10px;
    box-shadow: none;
    text-shadow: none;
}}
headerbar button:hover {{ background-color: alpha(@sd_accent, {alpha_accent_head}); border-color: @sd_accent; }}
headerbar button:active, headerbar button:checked {{ background-color: @sd_accent_dark; color: {sel_text}; }}
headerbar button.titlebutton {{
    background-image: none;
    background-color: {titlebtn};
    border: 1px solid {titlebtn_border};
    border-radius: 8px;
    color: {title};
    -gtk-icon-shadow: none;
    min-width: 24px;
    min-height: 24px;
    padding: 0;
    box-shadow: none;
}}
headerbar button.titlebutton:hover {{ background-color: {titlebtn_hover}; }}
headerbar button.titlebutton:active {{ background-color: @sd_accent_dark; }}
headerbar button.titlebutton.close:hover {{ background-color: {close_hover}; border-color: {close_hover_border}; }}
headerbar button.titlebutton image {{ color: {title}; }}

/* ---------- 搜索框 ---------- */
entry.search, entry.search-entry, searchentry {{
    background-image: none;
    background-color: {search_bg};
    border: 1px solid @sd_border;
    border-radius: 10px;
    color: @sd_text;
    min-height: 30px;
    padding: 0 10px;
    box-shadow: none;
    caret-color: @sd_accent;
}}
entry.search:focus, entry.search-entry:focus, searchentry:focus {{ border-color: @sd_accent; }}
entry.search image, entry.search-entry image, searchentry image {{ color: @sd_dim; }}
/* 深色模式下防止默认主题把搜索框画成白底 */
headerbar entry, headerbar entry.search {{ color: @sd_text; }}
headerbar entry text, headerbar entry.search text {{
    background-color: transparent;
    color: @sd_text;
}}

/* ---------- 左侧分类栏 ---------- */
#sidebar {{ background-color: @sd_bg_alt; border-right: 1px solid @sd_border; }}
#sidebar.view {{ background-color: transparent; color: @sd_text; -GtkTreeView-vertical-separator: 3px; }}
#sidebar.view:hover {{ background-color: {hover}; }}
#sidebar.view:selected {{
    background-image: linear-gradient(to right, @sd_accent, @sd_accent_dark);
    color: {sel_text};
}}
#sidebar-header {{
    background-image: linear-gradient(to bottom, {sidebar_header_top}, {sidebar_header_bottom});
    border-bottom: 1px solid @sd_border;
    padding: 10px 12px;
}}
#sidebar-header label {{ font-weight: 700; color: {title}; font-size: 14px; }}

/* ---------- 功能列表 / 搜索结果列表 ---------- */
#func-list {{ background-color: transparent; color: @sd_text; -GtkTreeView-vertical-separator: 2px; }}
#func-list.view:hover {{ background-color: alpha(@sd_accent, {alpha_accent_hover}); }}
#func-list.view:selected {{
    background-image: linear-gradient(to right, @sd_accent, @sd_accent_dark);
    color: {sel_text};
}}
treeview button {{
    background-image: none;
    background-color: @sd_panel_hi;
    border: none;
    border-bottom: 1px solid @sd_border;
    border-radius: 0;
    color: @sd_dim;
    min-height: 26px;
    box-shadow: none;
    text-shadow: none;
    font-weight: 600;
}}

/* ---------- 圆角卡片容器 ---------- */
.card {{
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 12px;
}}

/* ---------- 页面标题 ---------- */
#page-title {{ color: {title}; }}

/* ---------- 底部状态栏 ---------- */
#bottom-bar {{
    background-image: linear-gradient(to bottom, {bottom_top}, {bottom_bottom});
    border-top: 1px solid @sd_border;
    padding: 6px 10px;
}}
#status-label {{ font-size: 11px; color: @sd_dim; }}
#task-timer {{ font-size: 11px; font-weight: bold; color: @sd_accent; }}

/* ---------- 普通按钮 ---------- */
button {{
    background-image: none;
    background-color: @sd_panel_hi;
    border: 1px solid @sd_border;
    border-radius: 9px;
    color: @sd_text;
    min-height: 30px;
    padding: 2px 14px;
    box-shadow: none;
    text-shadow: none;
}}
button:hover {{ background-color: alpha(@sd_accent, {alpha_accent_btn}); border-color: @sd_accent; }}
button:active {{ background-color: @sd_accent_dark; color: {sel_text}; }}
button:disabled {{ color: @sd_dim; background-color: @sd_panel; border-color: @sd_border; }}
button.suggested-action {{
    background-image: linear-gradient(to bottom, @sd_accent, @sd_accent_dark);
    border-color: @sd_accent;
    color: {sel_text};
}}
button.suggested-action:hover {{ background-image: linear-gradient(to bottom, {suggested_hover}, @sd_accent_dark); }}
button.destructive-action {{ background-color: {destructive}; border-color: {destructive_border}; color: #ffffff; }}
button.destructive-action:hover {{ background-color: {destructive_hover}; border-color: {destructive_hover_border}; }}

/* ---------- 文本框 ---------- */
textview, textview text {{ background-color: @sd_panel; color: @sd_text; caret-color: @sd_accent; }}
textview {{ border-radius: 10px; }}

/* ---------- 滚动条 ---------- */
scrollbar {{ background-color: transparent; border: none; }}
scrollbar slider {{
    background-color: {scrollbar};
    border-radius: 6px;
    min-width: 8px;
    min-height: 8px;
}}
scrollbar slider:hover {{ background-color: alpha(@sd_accent, 0.6); }}

/* ---------- 主题切换弹出菜单（Popover 才能跟随主题着色） ---------- */
popover, popover.background {{
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 10px;
    box-shadow: 0 6px 18px {shadow};
}}
popover > box, popover.background > box {{ background-color: transparent; }}
/* 主题行按钮 */
.theme-row, button.theme-row {{
    background-image: none;
    background-color: transparent;
    border: none;
    border-radius: 7px;
    box-shadow: none;
    padding: 8px 14px;
    min-height: 24px;
    color: @sd_text;
}}
.theme-row:hover, button.theme-row:hover {{
    background-image: none;
    background-color: alpha(@sd_accent, {alpha_accent_btn});
    border: none;
    color: @sd_text;
}}
.theme-row:active, button.theme-row:active {{
    background-image: none;
    background-color: alpha(@sd_accent, {alpha_accent_btn});
    color: @sd_text;
}}
.theme-row label {{ color: @sd_text; }}
.theme-row image {{ color: @sd_accent; }}

/* ---------- 对话框（危险操作确认等原生 MessageDialog） ---------- */
/* 原生 Adwaita 对话框纸面是浅色，而它继承的是深色主题的文字色，
   切到浅色模式后就会出现"白底浅字"。这里显式指定对话框的底色与文字色。 */
dialog, dialog.background, messagedialog, messagedialog.background {{
    background-color: @sd_panel;
    color: @sd_text;
}}
dialog .dialog-action-area, messagedialog .dialog-action-area {{
    background-color: @sd_bg_alt;
    border-top: 1px solid @sd_border;
}}
dialog label, messagedialog label,
dialog .label, messagedialog .label {{
    color: @sd_text;
}}
dialog .dim-label, messagedialog .dim-label,
dialog .subtitle, messagedialog .subtitle {{
    color: @sd_dim;
}}
dialog .title, messagedialog .title {{ color: @sd_text; font-weight: 700; }}
dialog image, messagedialog image {{ color: @sd_accent; }}
dialog button, messagedialog button {{ color: @sd_text; }}
dialog button:active, messagedialog button:active,
dialog button.suggested-action, messagedialog button.suggested-action {{ color: {sel_text}; }}

/* ---------- 下拉菜单 / 工具提示 / 输入法候选窗等原生浮层 ---------- */
menu, .menu, .context-menu, menuitem, tooltip, tooltip.background {{
    color: @sd_text;
}}
menu, .menu, .context-menu {{ background-color: @sd_panel; border: 1px solid @sd_border; }}
menuitem {{ background-color: transparent; }}
menuitem:hover {{ background-color: alpha(@sd_accent, {alpha_accent_btn}); }}
tooltip.background {{ background-color: {panel_hi}; border: 1px solid @sd_border; }}
tooltip label {{ color: @sd_text; }}

/* ---------- 终端 ---------- */
vte-terminal {{ padding: 6px; }}
"""

def build_css(theme_name):
    """根据主题名生成对应的 CSS 文本。"""
    palette = THEME_LIGHT if theme_name == "light" else THEME_DARK
    return APP_CSS_TEMPLATE.format(**palette)

# 向后兼容：旧代码中若有引用 APP_CSS 的地方，默认使用深色
APP_CSS = build_css("dark")

# ---------------------------------------------------------------------------
# 主题配置：深色 / 浅色 / 跟随系统，持久化到 ~/.config/steamdeck_toolbox/config.json
# ---------------------------------------------------------------------------
THEME_MODES = ("dark", "light", "system")
THEME_LABELS = {"dark": "深色", "light": "浅色", "system": "跟随系统"}

_css_provider = None

def _config_path():
    return os.path.join(os.path.expanduser("~"), ".config", "steamdeck_toolbox", "config.json")

def load_theme_pref():
    """读取用户偏好，默认跟随系统。"""
    try:
        with open(_config_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        mode = data.get("theme", "system")
        return mode if mode in THEME_MODES else "system"
    except Exception:
        return "system"

def save_theme_pref(mode):
    """保存主题偏好，失败不影响使用。"""
    if mode not in THEME_MODES:
        return False
    try:
        path = _config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {}
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f) or {}
            except Exception:
                data = {}
        data["theme"] = mode
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存主题设置失败: {e}")
        return False

# 系统真实配色方案的快照。
# 注意：apply_app_css 会去改 GTK 的 prefer-dark 让原生控件跟着变，
# 如果不先记录系统原始值，选“跟随系统”时读到的就是自己被改写过的值（自我污染）。
_system_theme = None

def _detect_system_theme():
    """探测系统真实配色，返回 dark 或 light。只应在程序启动、修改 GTK 之前调用一次。"""
    # 1) 优先读桌面环境的颜色方案设置（这是用户真正设置的“系统主题”）
    for cmd, key, dark_pat in (
        (["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"], None, "dark"),
        (["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"], None, None),
    ):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            val = (out.stdout or "").strip().lower()
            if not val or out.returncode != 0:
                continue
            if dark_pat is not None:
                # color-scheme 为 'prefer-dark' / 'default' 等
                return "dark" if dark_pat in val else "light"
            # gtk-theme 名称里含 dark 视为深色主题
            return "dark" if "dark" in val else "light"
        except Exception:
            continue
    # 2) 退化：读 GTK 的 prefer-dark
    try:
        settings = Gtk.Settings.get_default()
        if settings is not None:
            return "dark" if settings.get_property("gtk-application-prefer-dark-theme") else "light"
    except Exception:
        pass
    return "light"

def reset_system_theme_cache():
    """重新探测系统配色（用户可能在系统里改了主题）。"""
    global _system_theme
    _system_theme = _detect_system_theme()
    return _system_theme

def resolve_theme_mode(mode):
    """把 system 解析成实际生效的 dark/light。使用启动时记录的系统快照，避免自我污染。"""
    if mode in ("dark", "light"):
        return mode
    global _system_theme
    if _system_theme is None:
        reset_system_theme_cache()
    return _system_theme or "light"

def apply_app_css(mode=None):
    """应用主题样式；mode 为 dark/light/system，None 表示使用已保存的偏好。"""
    global _css_provider
    try:
        if mode is None:
            mode = load_theme_pref()
        resolved = resolve_theme_mode(mode)
        css = build_css(resolved)

        # 同步 GTK 自身的深色偏好，让对话框、下拉菜单等原生控件配色一致
        try:
            settings = Gtk.Settings.get_default()
            if settings is not None:
                settings.set_property("gtk-application-prefer-dark-theme", resolved == "dark")
        except Exception:
            pass

        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode('utf-8'))
        screen = Gdk.Screen.get_default()
        if screen is None:
            return
        # 先移除旧 provider，避免重复叠加导致样式错乱
        if _css_provider is not None:
            try:
                Gtk.StyleContext.remove_provider_for_screen(screen, _css_provider)
            except Exception:
                pass
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        _css_provider = provider
    except Exception as e:
        print(f"应用样式失败: {e}")

def load_icon_pixbuf(name, size=24):
    """优先加载脚本目录 emoji_icons/ 下的本地图标，其次使用内嵌图标。"""
    if not name:
        return None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "emoji_icons", name)
    if os.path.exists(icon_path):
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, size, size)
        except Exception as e:
            print(f"加载本地图标失败 {icon_path}: {e}")
    data = EMBEDDED_ICONS.get(name)
    if data:
        try:
            loader = GdkPixbuf.PixbufLoader.new_with_mime_type("image/png")
            loader.write(base64.b64decode(data))
            loader.close()
            pb = loader.get_pixbuf()
            if pb and (pb.get_width() != size or pb.get_height() != size):
                pb = pb.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
            return pb
        except Exception as e:
            print(f"解码内嵌图标失败 {name}: {e}")
    return None

def version_tuple(v):
    out = []
    for part in str(v).split('.'):
        digits = re.sub(r'\D', '', part)
        out.append(int(digits) if digits else 0)
    # 去掉末尾的 0，让 "1.7" 与 "1.7.0" 视为同一版本
    # （未对齐时 (1,7) < (1,7,0) 会把同版本误判为"有新版本"，反复提示更新/降级）
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)

def compare_versions(a, b):
    ta, tb = version_tuple(a), version_tuple(b)
    # 补零对齐后再比较，避免元组长度不同导致的误判
    width = max(len(ta), len(tb))
    ta = ta + (0,) * (width - len(ta))
    tb = tb + (0,) * (width - len(tb))
    return (ta > tb) - (ta < tb)

def find_terminal():
    for t in ("konsole", "xterm", "gnome-terminal", "xfce4-terminal", "lxterminal"):
        if shutil.which(t):
            return t
    return None

def launch_terminal(command_str):
    """在可用的终端模拟器中执行命令，返回是否成功启动。"""
    term = find_terminal()
    if not term:
        return False
    try:
        if term == "gnome-terminal":
            subprocess.Popen([term, "--", "bash", "-c", command_str],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        else:
            subprocess.Popen([term, "-e", "bash", "-c", command_str],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        return True
    except Exception:
        return False

# GUI 层二次确认的危险操作（对应 bash 内部提示较弱的系统级修改）
# clover_install_or_reinstall 会往 EFI 分区写文件、替换 BOOTX64.EFI、改 efibootmgr
# 启动项，一旦出错可能导致机器无法启动，必须走确认框。
DANGEROUS_FUNCS = {"fix_boot", "fix_shared_disk", "uninstall_plugin_store", "clear_hosts_cache",
                   "clover_install_or_reinstall", "health_check"}

# 每个危险功能的额外风险说明（缺省用通用文案）
DANGEROUS_HINTS = {
    "clover_install_or_reinstall": "该功能会向 EFI 系统分区写入 Clover 引导文件，"
                                   "替换 BOOTX64.EFI 并修改 EFI 启动项。\n"
                                   "操作不当可能导致设备无法开机，请确认已了解风险并做好备份。",
    "fix_boot": "该功能会修改 EFI 启动顺序，把 Clover 设为第一启动项。",
    "fix_shared_disk": "该功能会修改 /etc/fstab 与 UDisks2 策略文件，用于自动挂载 Windows 分区。",
    "uninstall_plugin_store": "该功能会删除已安装的插件商店及其插件数据。",
    "clear_hosts_cache": "该功能会修改系统 /etc/hosts 文件（会自动备份）。",
    "health_check": "该功能会检查 ESP 分区、UEFI 启动项、Clover 引导文件与 /etc/fstab。\n"
                    "检查过程为只读，仅在你确认修复后才会修改系统（fstab 修改前会自动备份）。",
}
DEFAULT_DANGEROUS_HINT = "该功能会修改系统引导、挂载或系统文件，请确认已了解风险。"

# ============================================================================
# 内嵌 Bash 脚本
# ============================================================================
BASH_SCRIPT = r'''#!/bin/bash
set -uo pipefail
TEMP_DIR="/tmp/steamdeck_toolbox"
cleanup_temp() { rm -rf "$TEMP_DIR" 2>/dev/null; }
# SteamOS 只读模式：脚本退出时自动恢复（sudo -n 非交互，避免卡在密码提示）
# 关键：只有脚本自己 disable 过只读，退出时才恢复。
# 否则用户手动把系统设为可写（disabled）时，跑任何功能都会在退出时被强行改回
# enabled，覆盖掉用户自己的设置。
RO_READONLY_DISABLED_BY_US=0
restore_readonly() {
    command -v steamos-readonly &>/dev/null || return 0
    # 脚本没动过只读开关 → 保持用户原状，绝不擅自 enable
    [ "${RO_READONLY_DISABLED_BY_US:-0}" -eq 1 ] || return 0
    if sudo -n steamos-readonly status 2>/dev/null | grep -q "disabled"; then
        if sudo -n steamos-readonly enable 2>/dev/null; then
            echo -e "${GREEN}✓ 已恢复只读模式${NC}"
        else
            echo -e "${YELLOW}⚠ 无法自动恢复只读模式，请手动执行: sudo steamos-readonly enable${NC}"
        fi
    fi
    return 0
}
trap 'restore_readonly; cleanup_temp; exit 0' EXIT
trap 'echo -e "\n${YELLOW}用户取消操作，关闭窗口。${NC}"; cleanup_temp; exit 0' INT TERM

PYTHON_CMD="python3"
command -v python3 &>/dev/null || PYTHON_CMD="python"
# 当前用户名/组：不能硬编码 deck，非 deck 用户名的设备会把文件属主改错
CURRENT_USER="${USER:-$(id -un)}"
CURRENT_GROUP="$(id -gn "$CURRENT_USER" 2>/dev/null || echo "$CURRENT_USER")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'; NC='\033[0m'

# 全局下载镜像源（GitHub 加速）
# 2026-10 实测：各跑 5 轮小文件 + 33MB 二进制（sha256 校验）+ 大文件 range，
#   旧列表里的 gh.ddlc.top 已 429 限流、mirror.ghproxy.com 域名失效，仅 ghproxy.net 仍可用但很慢。
# 顺序按「速度 + 稳定性」排列。
# 用法：${镜像前缀}${完整 GitHub URL}，例如 https://gh-proxy.com/https://github.com/a/b/releases/download/v1/x.zip
# 官方源的前缀是空串（完整 URL 本身就能直接用），不能写成 https://github.com/ 否则会拼成
# https://github.com/https://github.com/...
MIRRORS=(
    "https://gh-proxy.com/"     # 国内镜像，速度快
    "https://gh.3w.pm/"         # 国内镜像，稳定
    "https://cors.isteed.cc/"   # 国内镜像，稳定
    "https://ghproxy.net/"      # 国内镜像，慢速备用
    ""                          # 官方源（空前缀 = 直接用原始 GitHub URL）
)
# 给用户选择菜单用的人类可读名称，与 MIRRORS 一一对应
MIRROR_LABELS=(
    "gh-proxy.com (国内镜像，速度快)"
    "gh.3w.pm (国内镜像，稳定)"
    "cors.isteed.cc (国内镜像，稳定)"
    "ghproxy.net (国内镜像，慢速备用)"
    "GitHub (官方源)"
)


# 安全解析 lsblk -P 输出（避免 eval 注入），变量名与 lsblk 字段一致
parse_line() {
    local line="$1" key val
    local pat='([A-Z]+)="([^"]*)"(.*)'
    NAME=""; TYPE=""; LABEL=""; FSTYPE=""; MOUNTPOINT=""; UUID=""; PARTTYPE=""; SIZE=""
    while [[ "$line" =~ $pat ]]; do
        key="${BASH_REMATCH[1]}"; val="${BASH_REMATCH[2]}"; line="${BASH_REMATCH[3]}"
        case "$key" in
            NAME) NAME="$val";; TYPE) TYPE="$val";; LABEL) LABEL="$val";;
            FSTYPE) FSTYPE="$val";; MOUNTPOINT) MOUNTPOINT="$val";; UUID) UUID="$val";;
            PARTTYPE) PARTTYPE="$val";; SIZE) SIZE="$val";;
        esac
    done
}

# 带 zip 完整性校验的镜像下载（复用全局 MIRRORS）
download_zip_with_mirrors() {
    local url="$1" output="$2" desc="${3:-ZIP文件}"
    while true; do
        clear
        echo -e "${CYAN}下载 ${desc}${NC}\n"
        echo "请选择下载镜像源（输入编号，0取消）："
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRROR_LABELS[$i]:-${MIRRORS[$i]}}"
        done
        read -p "请输入选择: " choice < /dev/tty
        [[ -z "$choice" ]] && echo -e "${RED}输入无效${NC}" && sleep 1 && continue
        [[ "$choice" == "0" ]] && echo "操作已取消。" && return 1
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            local mirror="${MIRRORS[$((choice-1))]}"
            local full_url="${mirror}${url}"
            echo -e "尝试从 ${MIRROR_LABELS[$((choice-1))]:-${mirror}} 下载..."
            if curl -L --progress-bar -f -o "$output" "$full_url" && [ -s "$output" ] && unzip -t "$output" &>/dev/null; then
                echo -e "${GREEN}下载成功，文件完整。${NC}"
                return 0
            fi
            echo -e "${RED}下载失败或文件不完整，请重新选择镜像源。${NC}"
            rm -f "$output"; sleep 1
        else
            echo -e "${RED}无效编号。${NC}"; sleep 1
        fi
    done
}

mk_temp_dir() { mkdir -p "$TEMP_DIR"; }

confirm_action() {
    read -n1 -p "按回车键或 A 键确认，其他键取消: " confirm < /dev/tty
    echo
    [[ -z "$confirm" || "$confirm" =~ [Aa] ]]
}

disable_readonly() {
    if command -v steamos-readonly &>/dev/null; then
        if sudo steamos-readonly disable 2>/dev/null; then
            # 记下“只读是脚本关掉的”，退出时 trap 才会恢复，避免覆盖用户自己的设置
            RO_READONLY_DISABLED_BY_US=1
            echo -e "${GREEN}✓ 已禁用只读模式${NC}"
        else
            echo -e "${RED}✗ 禁用只读模式失败，操作中止。${NC}"
            return 1
        fi
    fi
    return 0
}

download_with_mirrors() {
    local url="$1" output="$2" desc="${3:-文件}"
    while true; do
        clear
        echo -e "${CYAN}下载 ${desc}${NC}\n"
        echo "请选择下载镜像源（输入编号，0取消）："
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRROR_LABELS[$i]:-${MIRRORS[$i]}}"
        done
        read -p "请输入选择: " choice < /dev/tty
        [[ -z "$choice" ]] && echo -e "${RED}输入无效${NC}" && sleep 1 && continue
        [[ "$choice" == "0" ]] && echo "操作已取消。" && return 1
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            local mirror="${MIRRORS[$((choice-1))]}"
            local full_url="${mirror}${url}"
            echo -e "尝试从 ${MIRROR_LABELS[$((choice-1))]:-${mirror}} 下载..."
            if curl -L --progress-bar -f -o "$output" "$full_url" && [ -s "$output" ]; then
                echo -e "${GREEN}下载成功。${NC}"
                return 0
            fi
            echo -e "${RED}下载失败，请重新选择镜像源。${NC}"
            rm -f "$output"; sleep 1
        else
            echo -e "${RED}无效编号。${NC}"; sleep 1
        fi
    done
}

install_flatpak_app() {
    local app_title="$1" desktop_name="$2" categories="$3"; shift 3
    local app_ids=("$@")
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装 ${app_title} ════════════════${NC}"

    local already_installed=""
    for app_id in "${app_ids[@]}"; do
        flatpak info "$app_id" &>/dev/null && already_installed="$app_id" && break
    done
    if [ -n "$already_installed" ]; then
        echo -e "${GREEN}✓ ${app_title} 已安装 (${already_installed})，无需重复安装。${NC}"
        return 0
    fi

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    local available_id=""
    for app_id in "${app_ids[@]}"; do
        if timeout 10 flatpak remote-info flathub "$app_id" &>/dev/null; then
            available_id="$app_id"; break
        else
            echo -e "${YELLOW}${app_id} 不存在或查询超时，尝试下一个...${NC}"
        fi
    done
    [ -z "$available_id" ] && echo -e "${RED}✗ 未找到可安装的 ${app_title} 包。${NC}" && return 1

    echo "正在安装 ${available_id} ..."
    if flatpak install flathub "$available_id" -y 2>/dev/null; then
        echo -e "${GREEN}✓ ${app_title} 安装成功${NC}"
        cat > "$HOME/Desktop/${desktop_name}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=${desktop_name}
Exec=flatpak run ${available_id}
Icon=${available_id}
Terminal=false
Categories=${categories};
EOF
        chmod +x "$HOME/Desktop/${desktop_name}.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ 安装失败，请检查网络或手动安装。${NC}"
    fi
}

uninstall_flatpak_app() {
    local app_title="$1" desktop_name="$2"; shift 2
    local app_ids=("$@")
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 卸载 ${app_title} ════════════════${NC}"
    local installed=""
    for pkg in "${app_ids[@]}"; do flatpak info "$pkg" &>/dev/null && installed="$pkg" && break; done
    [ -z "$installed" ] && echo -e "${YELLOW}未检测到已安装的 ${app_title}。${NC}" && return 0

    confirm_action || { echo "取消卸载。"; return 0; }
    if flatpak uninstall "$installed" -y; then
        echo -e "${GREEN}✓ ${app_title} 卸载完成${NC}"
        local desktop_dir="$HOME/Desktop"
        if [ -d "$desktop_dir" ]; then
            local deleted_any=false
            for f in "$desktop_dir"/*.desktop; do
                # Desktop 目录为空时 glob 不展开，跳过字面量，避免 basename 得到 "*.desktop"
                [ -e "$f" ] || continue
                local base=$(basename "$f")
                # 只认两件事：①与显示名/应用 ID 完全同名的 .desktop
                #           ②文件名里带完整应用 ID（点或下划线写法都算，如 com_qq_QQ.desktop）
                # 不能只用 ${installed//./_} 做子串匹配：com.qq.QQ 会把
                # com_qq_QQ_something.desktop 这类无关快捷方式一起删掉。
                local id_us="${installed//./_}"
                if [ "$base" = "${desktop_name}.desktop" ] || [ "$base" = "${installed}.desktop" ] \
                   || [ "$base" = "${id_us}.desktop" ] || [ "$base" = "${installed//./-}.desktop" ]; then
                    rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ 桌面快捷方式已删除: $base${NC}" && deleted_any=true
                fi
            done
            $deleted_any || echo -e "${YELLOW}未找到匹配的桌面快捷方式。${NC}"
        fi

        local data_dir="$HOME/.var/app/$installed"
        if [ -d "$data_dir" ]; then
            echo ""
            echo -e "${CYAN}是否删除该应用的所有设置和用户数据？${NC}"
            confirm_action && rm -rf "$data_dir" && echo -e "${GREEN}✓ 用户数据已删除${NC}" || echo -e "${YELLOW}已保留用户数据。${NC}"
        fi
        echo ""
        echo -e "${GREEN}${app_title} 卸载流程结束。${NC}"
    else
        echo -e "${RED}✗ 卸载失败${NC}"
    fi
}

install_chinese_source() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装国内源 ════════════════${NC}"
    echo "正在配置国内源..."
    echo ""
    # 不需要禁用 SteamOS 只读模式：flatpak remote 配置在 /var/lib/flatpak（可写分区），
    # 与只读的根分区无关。原实现先 disable_readonly 属于多余操作，还会顺手改掉系统只读状态。
    echo -e "${CYAN}步骤1: 检查 flatpak 环境${NC}"
    if ! command -v flatpak &>/dev/null; then
        echo -e "${RED}✗ 未找到 flatpak 命令，无法配置镜像源。${NC}"
        return 1
    fi
    if ! flatpak remotes --columns=name 2>/dev/null | grep -qx "flathub"; then
        echo -e "${YELLOW}⚠ 未检测到 flathub 远程仓库，正在按官方地址添加...${NC}"
        if ! sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null; then
            echo -e "${RED}✗ 添加 flathub 失败，已中止。${NC}"
            return 1
        fi
    fi
    echo -e "${GREEN}✓ flatpak 环境正常${NC}"
    echo ""
    echo -e "${CYAN}步骤2: 配置Flatpak国内源${NC}"

    # 实测（2026-10）：
    #   mirror.sjtu.edu.cn/flathub  → 已改为 301 跳回官方 dl.flathub.org，等于没加速
    #   mirrors.tuna / nju / bfsu / iscas / aliyun 的 flathub → 404，没有这个镜像
    #   mirrors.ustc.edu.cn/flathub → 真实镜像（yadex 增量方案），实测可正常查询与安装，
    #                                 且需要先导入 flathub 公钥才能校验签名
    local FP_MIRROR="https://mirrors.ustc.edu.cn/flathub/"
    local FP_KEY_TMP="${TEMP_DIR}/flathub.gpg"
    local FP_OLD_URL
    # 注意：flatpak 没有 remote-get-url 这个子命令，要从 remotes 列表里取
    FP_OLD_URL=$(flatpak remotes --columns=name,url 2>/dev/null | awk '$1 == "flathub" {print $2; exit}')

    # 先确认 sudo 可用：系统级 flatpak remote 配置需要 root，
    # 若这里不先验证，后面 remote-modify 会卡在密码提示上（输出被 2>/dev/null 吞掉，看起来像无响应）
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}✗ 需要 sudo 权限才能修改 Flatpak 源，已中止。${NC}"
        return 1
    fi

    # 1) 导入 flathub 官方公钥（UESTC 镜像的摘要带 flathub 签名，缺公钥会被拒绝）
    echo "正在获取 flathub 签名公钥..."
    if curl -fsSL --connect-timeout 15 --max-time 60 -o "$FP_KEY_TMP" \
        https://dl.flathub.org/repo/flathub.gpg 2>/dev/null && [ -s "$FP_KEY_TMP" ]; then
        if sudo flatpak remote-modify --gpg-import="$FP_KEY_TMP" flathub 2>/dev/null; then
            echo -e "${GREEN}✓ 已导入 flathub 签名公钥${NC}"
        else
            echo -e "${YELLOW}⚠ 导入公钥失败（源可能已存在该公钥，继续）${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ 无法下载 flathub 公钥，跳过导入（若安装报签名错误，请先联网执行一次官方安装）${NC}"
    fi
    rm -f "$FP_KEY_TMP"

    # 2) 切换 flathub 地址到镜像
    if ! sudo flatpak remote-modify flathub --url="$FP_MIRROR" 2>/dev/null; then
        echo -e "${RED}✗ Flatpak国内源配置失败${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Flatpak 源已切换为 $FP_MIRROR${NC}"

    # 3) 实际拉一次元数据验证，不只看命令返回值
    #    remote-info 必须指定分支，否则会因"多个可用分支"直接报错，被误判为镜像不可用
    echo "正在验证镜像可用性..."
    if timeout 90 flatpak remote-info flathub org.freedesktop.Platform/x86_64/24.08 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ 镜像验证通过（可正常查询软件包）${NC}"
    else
        echo -e "${RED}✗ 镜像验证失败，正在回滚到官方源...${NC}"
        if [ -n "$FP_OLD_URL" ]; then
            sudo flatpak remote-modify flathub --url="$FP_OLD_URL" 2>/dev/null \
                && echo -e "${YELLOW}已回滚到原地址: $FP_OLD_URL${NC}" \
                || echo -e "${RED}回滚失败，请手动执行: sudo flatpak remote-modify flathub --url=$FP_OLD_URL${NC}"
        else
            echo -e "${RED}未获取到原地址，请手动恢复: sudo flatpak remote-modify flathub --url=https://dl.flathub.org/repo/${NC}"
        fi
        return 1
    fi
    echo ""
    echo -e "${GREEN}✓ 国内源配置已生效。${NC}"
    echo -e "${CYAN}  如需恢复官方源，请在 Konsole 中执行（需要 sudo）：${NC}"
    echo -e "${CYAN}    sudo flatpak remote-modify flathub --url=https://dl.flathub.org/repo/${NC}"
}

adjust_swap() {
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}════════════════ 调整虚拟内存大小 ════════════════${NC}"
        echo ""
        echo -e "${CYAN}当前系统状态${NC}"
        echo "--------------------------------------------"
        if command -v free &> /dev/null; then
            mem_line=$(LANG=C free -h | grep '^Mem:')
            swap_line=$(LANG=C free -h | grep '^Swap:')
            [ -n "$mem_line" ] && echo -e "物理内存: ${GREEN}$(echo "$mem_line" | awk '{print $2}')${NC} | 已用: ${YELLOW}$(echo "$mem_line" | awk '{print $3}')${NC}"
            [ -n "$swap_line" ] && echo -e "交换空间: ${GREEN}$(echo "$swap_line" | awk '{print $2}')${NC} | 已用: ${YELLOW}$(echo "$swap_line" | awk '{print $3}')${NC}"
        fi
        echo ""
        echo -e "${CYAN}请选择要执行的操作${NC}"
        echo "============================================"
        echo -e "${GREEN}[1] 一键应用CryoByte33推荐方案${NC}"
        echo -e "${GREEN}[2] 调整传统Swap文件大小${NC}"
        echo -e "${GREEN}[3] 配置ZRAM (内存压缩交换)${NC}"
        echo -e "${GREEN}[4] 清理所有虚拟内存配置并重新开始${NC}"
        echo "============================================"
        echo ""
        read -p "请输入选项 [1-4]: " main_choice < /dev/tty
        case $main_choice in
            1) apply_cryo_recommendation ;;
            2) adjust_swapfile ;;
            3) configure_zram ;;
            4) cleanup_swap ;;
            *) echo -e "${RED}无效选择，请重新输入。${NC}"; sleep 1; continue ;;
        esac
        echo ""
        read -p "按回车键继续..." < /dev/tty
    done
}

# 检查 /home 剩余空间是否足够创建指定大小（GB）的交换文件
check_swap_space() {
    local need_gb="$1"
    local avail_kb=$(df --block-size=1K --output=avail /home 2>/dev/null | tail -1 | tr -d ' ')
    if [ -z "$avail_kb" ] || [ "$avail_kb" -lt $((need_gb * 1024 * 1024)) ]; then
        echo -e "${RED}✗ /home 剩余空间不足：需要约 ${need_gb}GB，当前可用约 $((avail_kb / 1024 / 1024))GB。${NC}"
        return 1
    fi
    echo -e "${CYAN}✓ /home 剩余空间充足（约 $((avail_kb / 1024 / 1024))GB）。${NC}"
    return 0
}

apply_cryo_recommendation() {
    mk_temp_dir
    echo -e "${YELLOW}═══════════════ 应用CryoByte33推荐方案 ═══════════════${NC}"
    confirm_action || { echo "取消操作。"; return; }
    local swap_size_gb=16; local block_count=$((swap_size_gb*1024))
    check_swap_space "$swap_size_gb" || return 1
    sudo swapoff /home/swapfile 2>/dev/null; sudo swapoff -a 2>/dev/null
    sudo rm -f /home/swapfile
    sudo touch /home/swapfile; sudo chattr +C /home/swapfile 2>/dev/null || true
    if ! sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$block_count conv=fsync status=progress 2>/dev/null; then
        echo -e "${RED}✗ 创建交换文件失败（dd 出错，可能磁盘空间不足）。${NC}"
        return 1
    fi
    sudo chmod 600 /home/swapfile
    if ! sudo mkswap /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ mkswap 格式化失败。${NC}"
        return 1
    fi
    if ! sudo swapon /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ swapon 启用失败。${NC}"
        return 1
    fi
    sudo sed -i '\|/home/swapfile|d' /etc/fstab 2>/dev/null
    echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null
    echo -e "${GREEN}✓ 16GB交换文件创建完成${NC}"
    sudo tee /etc/sysctl.d/99-cryo-optimizations.conf > /dev/null <<'EOF'
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.page-cluster=0
vm.dirty_background_ratio=3
vm.dirty_ratio=50
EOF
    sudo sysctl --system --load=/etc/sysctl.d/99-cryo-optimizations.conf >/dev/null 2>&1
    if [ -f /etc/sysctl.d/99-cryo-optimizations.conf ]; then
        echo -e "${GREEN}✓ 内核参数优化完成${NC}"
    else
        echo -e "${YELLOW}⚠ 内核参数配置文件写入失败，本次优化未持久化${NC}"
    fi
    # 停用 ZRAM 要以实际结果为准，不能无条件打印成功
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    if ! systemctl is-active systemd-zram-setup@zram0 &>/dev/null \
       && ! systemctl is-enabled systemd-zram-setup@zram0 &>/dev/null 2>&1; then
        echo -e "${GREEN}✓ ZRAM已停用${NC}"
    else
        echo -e "${YELLOW}⚠ ZRAM 未能完全停用，如需彻底禁用请手动执行:"
        echo -e "   sudo systemctl disable --now systemd-zram-setup@zram0${NC}"
    fi
    echo -e "${GREEN}✅ CryoByte33推荐方案已成功应用！${NC}"
}

adjust_swapfile() {
    mk_temp_dir
    while true; do
        clear; echo -e "${YELLOW}调整传统Swap文件大小${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        [ -f "/home/swapfile" ] && echo -e "现有文件大小: ${GREEN}$(sudo du -h /home/swapfile 2>/dev/null | cut -f1)${NC}" || echo -e "现有文件: ${YELLOW}未找到${NC}"
        echo -n "/home 剩余空间: "; df -h /home | tail -1
        echo "选择新的大小: 1)1G 2)4G 3)8G 4)16G 5)32G 6)自定义"
        local swap_size_gb=""
        read -p "请选择 [1-6]: " size_choice < /dev/tty
        case $size_choice in
            1) swap_size_gb=1;; 2) swap_size_gb=4;; 3) swap_size_gb=8;; 4) swap_size_gb=16;; 5) swap_size_gb=32;;
            6) read -p "请输入大小 (GB): " custom_size < /dev/tty
               [[ "$custom_size" =~ ^[0-9]+$ ]] && swap_size_gb=$custom_size || { echo -e "${RED}无效数字。${NC}"; sleep 1; continue; };;
            *) echo -e "${RED}无效选项。${NC}"; sleep 1; continue;;
        esac
        break
    done
    check_swap_space "$swap_size_gb" || return 1
    # 替换前必须先停用旧 swapfile，否则 rm/mkswap 会碰到 device busy，
    # 而且在内存吃紧时直接删掉唯一交换分区有 OOM 风险。
    if swapon --show=NAME --noheadings 2>/dev/null | awk '$1 == "/home/swapfile" {found=1} END {exit !found}'; then
        echo -e "${CYAN}正在停用旧的 /home/swapfile ...${NC}"
        if ! sudo swapoff /home/swapfile 2>/dev/null; then
            echo -e "${RED}✗ 无法停用正在使用的 /home/swapfile，已中止（请检查内存占用后重试）。${NC}"
            return 1
        fi
        # 二次确认确实已释放，避免残留在 swap 表里继续 rm 出错
        if swapon --show=NAME --noheadings 2>/dev/null | awk '$1 == "/home/swapfile" {found=1} END {exit !found}'; then
            echo -e "${RED}✗ /home/swapfile 仍在使用中，已中止，未做任何修改。${NC}"
            return 1
        fi
    fi
    sudo rm -f /home/swapfile
    sudo touch /home/swapfile
    if mount | grep " /home " | grep -q btrfs; then sudo chattr +C /home/swapfile 2>/dev/null || echo -e "${YELLOW}⚠ chattr +C 失败，继续${NC}"; fi
    if ! sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$((swap_size_gb*1024)) status=progress conv=fsync 2>/dev/null; then
        echo -e "${RED}✗ 创建交换文件失败（dd 出错，可能磁盘空间不足）。${NC}"
        return 1
    fi
    sudo chmod 600 /home/swapfile
    if ! sudo mkswap /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ mkswap 格式化失败。${NC}"
        return 1
    fi
    if ! sudo swapon /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ swapon 启用失败。${NC}"
        return 1
    fi
    # 按第一字段精确匹配才判断"已存在"：原来的 grep -q "/home/swapfile" 会命中
    # 注释行（#/home/swapfile ...）或 /home/swapfile2，导致该加的条目没加上/加重复。
    if ! awk '$1 == "/home/swapfile" {found=1} END {exit !found}' /etc/fstab 2>/dev/null; then
        echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null
    fi
    echo -e "${GREEN}✅ Swap文件创建成功${NC}"
}

configure_zram() {
    mk_temp_dir
    while true; do
        clear; echo -e "${YELLOW}配置ZRAM (内存压缩交换)${NC}"
        echo -e "${CYAN}设置会写入持久化配置，重启后依然生效。${NC}"
        echo "选择ZRAM大小: 1)2G 2)4G 3)8G"
        local zram_size_gb=""
        read -p "请选择 [1-3]: " zram_choice < /dev/tty
        case $zram_choice in 1) zram_size_gb=2;; 2) zram_size_gb=4;; 3) zram_size_gb=8;; *) echo -e "${RED}无效选项。${NC}"; sleep 1; continue;; esac
        break
    done
    if ! command -v zramctl &>/dev/null; then
        echo -e "${RED}❌ 未找到 zramctl，无法配置 ZRAM。${NC}"
        return 1
    fi
    sudo modprobe zram 2>/dev/null

    # 持久化：写 zram-generator 的覆盖配置。/etc/systemd/zram-generator.conf 的优先级
    # 高于 SteamOS 自带的 /usr/lib/systemd/zram-generator.conf（默认 ram/2 + zstd）；
    # 不写这个文件，重启后 zram-generator 会按厂商默认重建，本次选择必然丢失。
    # 原代码结尾还 rm -f 了同一个文件，等于把设置又删掉，这里一并修正。
    local zram_conf_tmp="${TEMP_DIR}/zram-generator.conf.$$"
    cat > "$zram_conf_tmp" <<EOF
[zram0]
zram-size = ${zram_size_gb}G
compression-algorithm = lz4
swap-priority = 100
fs-type = swap
EOF
    local persist_ok=1
    if sudo install -D -m 644 "$zram_conf_tmp" /etc/systemd/zram-generator.conf 2>/dev/null; then
        sudo systemctl daemon-reload 2>/dev/null
        echo -e "${GREEN}✓ 已写入持久化配置 /etc/systemd/zram-generator.conf（重启后仍生效）${NC}"
    else
        persist_ok=0
        echo -e "${RED}❌ 写入持久化配置失败：本次设置重启后会丢失。${NC}"
    fi
    rm -f "$zram_conf_tmp"

    # 立即生效：先停用旧 zram 交换区，再按所选大小重建
    if swapon --show=NAME --noheadings 2>/dev/null | awk '$1 == "/dev/zram0" {found=1} END {exit !found}'; then
        sudo swapoff /dev/zram0 2>/dev/null || echo -e "${YELLOW}⚠️ 无法停用现有 /dev/zram0，将尝试直接调整大小。${NC}"
    fi
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo zramctl /dev/zram0 --reset 2>/dev/null
    local zram_dev="/dev/zram0" applied=0
    if sudo zramctl /dev/zram0 --size ${zram_size_gb}G --algorithm lz4 2>/dev/null; then
        applied=1
    else
        zram_dev=$(sudo zramctl --find --size ${zram_size_gb}G --algorithm lz4 2>/dev/null)
        [ -n "$zram_dev" ] && applied=1
    fi
    if [ "$applied" -ne 1 ] || [ -z "$zram_dev" ]; then
        echo -e "${RED}❌ 无法创建 ZRAM 设备。${NC}"
        [ "$persist_ok" -eq 1 ] && echo -e "${CYAN}   持久化配置已写入，重启后会按 ${zram_size_gb}G 自动创建。${NC}"
        return 1
    fi
    sudo mkswap "$zram_dev" >/dev/null 2>&1
    if ! sudo swapon "$zram_dev" -p 100 2>/dev/null; then
        echo -e "${RED}❌ ZRAM 启用失败（swapon 出错）。${NC}"
        return 1
    fi
    # 以实际结果为准，不按命令返回值猜成功
    if swapon --show=NAME --noheadings 2>/dev/null | awk -v d="$zram_dev" '$1 == d {found=1} END {exit !found}'; then
        local real_size=$(zramctl "$zram_dev" --noheadings --output DISKSIZE 2>/dev/null | tr -d ' ')
        echo -e "${GREEN}✅ ZRAM 已成功启用：$zram_dev（设定 ${zram_size_gb}G，实际 ${real_size:-未知}，lz4，优先级 100）${NC}"
        [ "$zram_dev" != "/dev/zram0" ] && echo -e "${YELLOW}⚠️ 本次实际设备为 $zram_dev；持久化配置使用 zram0，重启后以 zram0 为准。${NC}"
        [ "$persist_ok" -eq 1 ] && echo -e "${GREEN}✓ 重启后会自动恢复该配置。${NC}" \
            || echo -e "${YELLOW}⚠️ 持久化配置写入失败，重启后将恢复厂商默认 ZRAM。${NC}"
    else
        echo -e "${RED}❌ ZRAM 启用后未出现在 swap 列表中。${NC}"
        return 1
    fi
}

cleanup_swap() {
    mk_temp_dir
    confirm_action || { echo "操作已取消。"; return; }
    sudo swapoff -a 2>/dev/null
    # 只有在真正存在 /dev/zram0 时才重置它；不存在属于"当前没启用 ZRAM"，不是失败。
    # 原写法 `[ -b ... ] && reset || echo 失败` 在设备不存在时会误报"ZRAM 重置失败"。
    if [ -b /dev/zram0 ]; then
        if sudo zramctl /dev/zram0 --reset 2>/dev/null; then
            echo -e "${GREEN}✓ ZRAM 已重置${NC}"
        else
            echo -e "${YELLOW}⚠️ ZRAM 重置失败（设备可能仍被占用），可重启后再试。${NC}"
        fi
    else
        echo -e "${CYAN}ℹ 未发现 ZRAM 设备，跳过重置。${NC}"
    fi
    sudo rm -f /home/swapfile 2>/dev/null
    # 按第一字段精确匹配删除，避免把注释行/前缀相近的条目一起删掉
    if awk '$1 == "/home/swapfile" {found=1} END {exit !found}' /etc/fstab 2>/dev/null; then
        local fstab_tmp="${TEMP_DIR}/fstab.$$"
        if awk '$1 != "/home/swapfile"' /etc/fstab > "$fstab_tmp" 2>/dev/null; then
            sudo cp "$fstab_tmp" /etc/fstab && echo -e "${GREEN}✓ 已移除 fstab 中的 swapfile 条目${NC}"
        else
            echo -e "${YELLOW}⚠️ 写入临时 fstab 失败，/etc/fstab 中的 swapfile 条目未删除。${NC}"
        fi
        rm -f "$fstab_tmp"
    fi
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    # 清理 swap 后不应再让 zram-generator 按上次选择的尺寸重建 ZRAM，
    # 所以这里删掉「配置ZRAM」写入的持久化文件才是正确行为。
    if [ -f /etc/systemd/zram-generator.conf ]; then
        if sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null; then
            echo -e "${GREEN}✓ 已移除 ZRAM 持久化配置${NC}"
        else
            echo -e "${YELLOW}⚠️ 无法删除 /etc/systemd/zram-generator.conf，重启后 ZRAM 可能仍会按旧配置重建。${NC}"
        fi
    fi
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ 所有虚拟内存配置已清理完成（重启后生效）。${NC}"
}

fix_single_ntfs() {
    local device="$1" mountpoint="$2"
    echo ""
    echo -e "${CYAN}正在修复分区: $device${NC}"
    if [ -n "$mountpoint" ] && mountpoint -q "$mountpoint" 2>/dev/null; then
        echo "  分区当前挂载于 $mountpoint，正在卸载..."
        if sudo umount "$device" 2>/dev/null || sudo umount -f "$device" 2>/dev/null; then echo -e "${GREEN}  ✓ 卸载成功${NC}"; else echo -e "${RED}  ✗ 卸载失败，无法继续修复${NC}"; return 1; fi
    fi
    echo "  正在运行 ntfsfix ..."
    if sudo ntfsfix "$device" 2>/dev/null; then echo -e "${GREEN}  ✓ 修复成功${NC}"; else echo -e "${RED}  ✗ 修复失败，请检查 dmesg 输出${NC}"; sudo dmesg | grep -i ntfs | tail -5; fi
    if [ -n "$mountpoint" ] && [ -d "$mountpoint" ]; then
        echo "  尝试重新挂载到 $mountpoint ..."
        if sudo mount "$device" "$mountpoint" 2>/dev/null; then echo -e "${GREEN}  ✓ 重新挂载成功${NC}"; else echo -e "${YELLOW}  ⚠️ 自动挂载失败，请稍后手动挂载${NC}"; fi
    fi
}

fix_disk_write_error() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 修复磁盘写入错误 ════════════════${NC}"
    echo -e "${CYAN}正在扫描 NTFS 分区并检查是否存在错误...${NC}"

    # ------------------------------------------------------------------
    # 先扫描，再决定是否需要 sudo：
    # 单系统 SteamOS 通常没有任何 NTFS 分区，此时不应打扰用户输密码。
    # ------------------------------------------------------------------
    echo ""
    echo "步骤1: 扫描 NTFS 分区..."
    local ntfs_devices=()
    local ntfs_labels=()
    local ntfs_mountpoints=()
    local ntfs_uuids=()
    local ntfs_count=0

    while IFS= read -r line; do
        parse_line "$line"

        [ "$TYPE" != "part" ] && continue
        [[ "$FSTYPE" =~ ^(ntfs|fuseblk|ntfs3)$ ]] || continue

        dev="/dev/$NAME"
        ntfs_devices+=("$dev")
        ntfs_labels+=("${LABEL:-无标签}")
        ntfs_uuids+=("${UUID:-}")

        if [ -z "$MOUNTPOINT" ] || [ "$MOUNTPOINT" = "None" ]; then
            ntfs_mountpoints+=("")
        else
            ntfs_mountpoints+=("$MOUNTPOINT")
        fi
        ((ntfs_count++))
    done < <(lsblk -P -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID --noheadings 2>/dev/null)

    # lsblk 没有任何 NTFS 时，blkid 也几乎不可能有，但保留兜底探测
    # （注意：blkid 需要 root 才能读到全部信息，所以这里用 sudo -n，拿不到就跳过）
    if [ $ntfs_count -eq 0 ] && sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}⚠️  lsblk 未找到 NTFS 分区，尝试使用 blkid ...${NC}"
        while IFS= read -r line; do
            [ -z "$line" ] && continue
            dev=$(echo "$line" | cut -d: -f1)
            fstype=$(echo "$line" | sed -n 's/.* TYPE="\([^"]*\)".*/\1/p')
            label=$(echo "$line" | sed -n 's/.* LABEL="\([^"]*\)".*/\1/p')
            uuid=$(echo "$line" | sed -n 's/.* UUID="\([^"]*\)".*/\1/p')

            if [[ "$fstype" == "ntfs" || "$fstype" == "fuseblk" || "$fstype" == "ntfs3" ]]; then
                ntfs_devices+=("$dev")
                ntfs_labels+=("${label:-无标签}")
                ntfs_uuids+=("${uuid:-}")
                ntfs_mountpoints+=("")
                ((ntfs_count++))
            fi
        done < <(sudo -n blkid 2>/dev/null)
    fi

    # 没有 NTFS 分区：直接给出明确结论，不索要密码、不改动只读模式
    if [ $ntfs_count -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ 未检测到 NTFS 分区，无需修复。${NC}"
        echo -e "${CYAN}   本功能用于修复「Windows 双系统 / NTFS 存储卡」在卸载或断电后"
        echo -e "${CYAN}   残留的脏标志（Volume dirty），单系统 SteamOS 不会出现该问题。${NC}"
        echo ""
        echo -e "${CYAN}   如果您确实遇到了磁盘写入错误，可能属于以下情况：${NC}"
        echo "     · 文件系统错误（btrfs/ext4）→ 运行 sudo btrfs check 或 sudo fsck"
        echo "     · 空间不足          → 运行 df -h 检查可用空间"
        echo "     · 硬件/IO 报错      → 运行 sudo dmesg | grep -i error 查看"
        echo ""
        echo -e "${YELLOW}   提示：如已插入 NTFS 存储卡或移动硬盘，请确认已插紧后重试。${NC}"
        return 0
    fi

    # ------------------------------------------------------------------
    # 确认存在 NTFS 分区后，才需要 root 权限
    # ------------------------------------------------------------------
    if ! command -v ntfsfix &> /dev/null; then
        echo ""
        echo -e "${RED}错误: 未安装 ntfsfix 工具。${NC}"
        echo "请安装 ntfs-3g 包："
        echo "  sudo pacman -S ntfs-3g   (Arch/SteamOS)"
        echo "  sudo apt install ntfs-3g (Debian/Ubuntu)"
        return 1
    fi

    echo ""
    echo -e "${CYAN}发现 $ntfs_count 个 NTFS 分区，需要 root 权限进行检查。${NC}"
    echo -e "${CYAN}请输入您的 sudo 密码以继续操作（输入时不会显示）${NC}"
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}密码验证失败或已取消，操作终止。${NC}"
        return 1
    fi
    echo -e "${GREEN}密码已验证，继续执行。${NC}"

    # 记录进入时的只读状态，退出时按需恢复，避免把系统永久留在可写状态
    local readonly_was_enabled=0
    if command -v steamos-readonly &> /dev/null; then
        echo ""
        echo "步骤2: 检查并禁用 SteamOS 只读模式"
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            readonly_was_enabled=1
            if sudo steamos-readonly disable 2>/dev/null; then
                RO_READONLY_DISABLED_BY_US=1
                echo -e "${GREEN}✓ 已禁用只读模式${NC}"
            else
                echo -e "${YELLOW}⚠️  禁用只读模式失败，尝试继续...${NC}"
            fi
        else
            echo -e "${GREEN}✓ 系统已处于读写模式${NC}"
        fi
    else
        echo ""
        echo "步骤2: 跳过 SteamOS 只读检查（非 SteamOS）"
    fi

    echo ""
    echo -e "${CYAN}正在检查 $ntfs_count 个 NTFS 分区的错误状态...${NC}"
    local dirty_indices=()
    local skipped_count=0
    for ((i=0; i<ntfs_count; i++)); do
        echo -n "  检查 ${ntfs_devices[$i]} ... "
        # 注意：ntfsinfo / ntfsfix 都需要独占打开设备，已挂载的卷会报
        #      “Access is denied because the NTFS volume is already exclusively opened”。
        #      而用户真正关心的 Windows 分区通常正挂载着，所以必须先临时卸载再检查，
        #      检查完立即按原挂载点挂回。
        local dev="${ntfs_devices[$i]}"
        local mp="${ntfs_mountpoints[$i]}"
        local was_mounted=0
        if [ -n "$mp" ] && mountpoint -q "$mp" 2>/dev/null; then
            was_mounted=1
            # 卸载/挂载的输出全部丢弃，避免打断 “检查 xxx ...” 这一行的显示
            if ! sudo umount "$dev" >/dev/null 2>&1 && ! sudo umount -f "$dev" >/dev/null 2>&1; then
                echo -e "${YELLOW}跳过（分区正被占用，无法卸载）${NC}"
                skipped_count=$((skipped_count + 1))
                continue
            fi
        fi

        # 读取 $Volume 的 Volume Flags 判断 DIRTY 位（0x0001）。
        # 不能靠 `ntfsfix -n` 输出里找 "Volume is dirty" —— ntfsfix 并不打印这句话。
        local vol_out dirty=0 check_err=""
        vol_out=$(sudo ntfsinfo -m "$dev" 2>&1)
        local rc=$?
        if echo "$vol_out" | grep -q "DIRTY"; then
            dirty=1
        else
            local flags_hex
            flags_hex=$(echo "$vol_out" | sed -n 's/.*Volume Flags:[[:space:]]*0x\([0-9a-fA-F]\+\).*/\1/p' | head -1)
            if [ -n "$flags_hex" ]; then
                local flags_dec=$((16#$flags_hex))
                [ $((flags_dec & 1)) -eq 1 ] && dirty=1
            elif [ $rc -ne 0 ]; then
                check_err="读取失败"
            fi
        fi

        # 无论检查结果如何，先把卷挂回原位，避免影响用户正常使用
        if [ "$was_mounted" -eq 1 ] && [ -n "$mp" ]; then
            if ! sudo mount "$mp" >/dev/null 2>&1 && ! sudo mount "$dev" "$mp" >/dev/null 2>&1; then
                echo -e "${YELLOW}⚠ 检查后无法自动挂回 $mp，请手动挂载${NC}"
            fi
        fi

        if [ "$dirty" -eq 1 ]; then
            echo -e "${RED}有错误（脏）${NC}"
            dirty_indices+=("$i")
        elif [ -n "$check_err" ]; then
            echo -e "${YELLOW}跳过（$check_err）${NC}"
            skipped_count=$((skipped_count + 1))
        else
            echo -e "${GREEN}正常${NC}"
        fi
    done

    # 无论走哪条分支，退出前都尝试恢复只读
    _restore_readonly_after_fix() {
        if [ "$readonly_was_enabled" -eq 1 ] && command -v steamos-readonly &> /dev/null; then
            echo ""
            echo "正在恢复 SteamOS 只读模式..."
            if sudo -n steamos-readonly enable 2>/dev/null; then
                echo -e "${GREEN}✓ 只读模式已恢复${NC}"
            else
                echo -e "${YELLOW}⚠️  无法自动恢复只读模式，请手动执行: sudo steamos-readonly enable${NC}"
            fi
        fi
    }

    if [ ${#dirty_indices[@]} -eq 0 ]; then
        echo ""
        if [ "$skipped_count" -gt 0 ]; then
            # 有分区没能检查，就不能声称“全部正常”
            echo -e "${YELLOW}⚠️  ${skipped_count} 个分区未能检查（被占用或读取失败），其余 $((ntfs_count - skipped_count)) 个分区状态正常。${NC}"
            echo -e "${CYAN}   建议关闭正在使用这些分区的程序（Steam 库、文件管理器）后重试。${NC}"
        else
            echo -e "${GREEN}✅ 所有 NTFS 分区状态正常，无磁盘写入错误。${NC}"
        fi
        _restore_readonly_after_fix
        return 0
    fi

    echo ""
    echo -e "${YELLOW}发现 ${#dirty_indices[@]} 个分区存在写入错误（脏标志）：${NC}"
    # 编号采用“脏分区列表内的连续序号”（1,2,3...），与下方选项 2 的输入一致
    local n=0
    for idx in "${dirty_indices[@]}"; do
        n=$((n + 1))
        local mp_display="${ntfs_mountpoints[$idx]:-未挂载}"
        echo "  ${n}. ${ntfs_devices[$idx]}  标签:${ntfs_labels[$idx]}  挂载点:${mp_display}"
    done

    echo ""
    echo "请选择修复方式："
    echo "  1) 修复所有有错误的分区"
    echo "  2) 选择特定分区修复"
    echo "  3) 取消修复"

    local fix_choice
    while true; do
        # 读取失败（无 tty / EOF）时退出循环，避免无限重试刷屏
        if ! read -p "请输入选项 [1-3]: " fix_choice < /dev/tty; then
            echo -e "${YELLOW}无法读取输入，操作取消。${NC}"
            _restore_readonly_after_fix
            return 1
        fi
        case $fix_choice in
            1|2|3) break ;;
            *) echo -e "${RED}无效选项，请重新选择。${NC}" ;;
        esac
    done

    case $fix_choice in
        1)
            for idx in "${dirty_indices[@]}"; do
                fix_single_ntfs "${ntfs_devices[$idx]}" "${ntfs_mountpoints[$idx]}"
            done
            ;;
        2)
            echo "请输入要修复的分区编号（多个编号用空格分隔，如 1 3）："
            while true; do
                if ! read -p "编号: " -a indices < /dev/tty; then
                    echo -e "${YELLOW}无法读取输入，操作取消。${NC}"
                    _restore_readonly_after_fix
                    return 1
                fi
                local valid=true
                for num in "${indices[@]}"; do
                    # 编号范围 1..脏分区个数
                    if [[ ! "$num" =~ ^[0-9]+$ ]] || [ "$num" -lt 1 ] || [ "$num" -gt ${#dirty_indices[@]} ]; then
                        valid=false; break
                    fi
                done
                if $valid; then
                    break
                else
                    echo -e "${RED}无效编号，请输入 1 到 ${#dirty_indices[@]} 之间的数字。${NC}"
                fi
            done
            for num in "${indices[@]}"; do
                # 由“脏分区列表序号”映射回真实分区下标
                local target_idx="${dirty_indices[$((num-1))]}"
                fix_single_ntfs "${ntfs_devices[$target_idx]}" "${ntfs_mountpoints[$target_idx]}"
            done
            ;;
        3|*)
            echo "操作取消。"
            ;;
    esac

    _restore_readonly_after_fix
    echo ""
    echo -e "${GREEN}✅ 修复流程完成。${NC}"
}

clear_hosts_cache() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 清理 hosts 缓存 ════════════════${NC}"
    echo -e "${CYAN}仅移除 Steam 相关 hosts 条目，保留系统条目，并自动备份。${NC}"
    # /etc/hosts 位于 SteamOS 只读根分区：只读模式下 sudo sed 会静默失败，
    # 原代码不检查返回值、照样打印"清理完成"。这里先确保可写，失败就明确中止。
    if command -v steamos-readonly &>/dev/null; then
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            echo -e "${CYAN}正在临时禁用只读模式以修改 /etc/hosts（退出时自动恢复）...${NC}"
            disable_readonly || { echo -e "${RED}✗ 无法禁用只读模式，/etc/hosts 未做任何修改。${NC}"; return 1; }
        fi
    fi
    local backup="/etc/hosts.backup.$(date +%Y%m%d_%H%M%S)"
    if ! sudo cp /etc/hosts "$backup" 2>/dev/null; then
        echo -e "${RED}✗ 备份 /etc/hosts 失败（或目标只读），已中止，未做任何修改。${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ 已备份原 hosts 到 $backup${NC}"
    local steam_hosts_re='^\s*([0-9a-fA-F:.]+|\*)\s+(steamcommunity\.com|steamstatic\.com|steamcontent\.com|steamusercontent\.com|api\.steampowered\.com|store\.steampowered\.com|s\.team|steamcdn-a\.akamaihd\.net)(\s|$)'
    if ! sudo sed -i -E "/${steam_hosts_re}/d" /etc/hosts 2>/dev/null; then
        echo -e "${RED}✗ 写入 /etc/hosts 失败（磁盘只读或权限不足），原文件未被修改。${NC}"
        echo -e "${YELLOW}   如需回滚：sudo cp $backup /etc/hosts${NC}"
        return 1
    fi
    # 以实际内容校验结果，不能只依赖命令返回值
    if grep -qE "$steam_hosts_re" /etc/hosts 2>/dev/null; then
        echo -e "${RED}✗ 仍有 Steam 相关条目未能移除，请检查 /etc/hosts。${NC}"
        echo -e "${YELLOW}   备份文件：$backup（可用 sudo cp $backup /etc/hosts 回滚）${NC}"
        return 1
    fi
    # localhost 判断要锚定到完整主机名，否则 127.0.0.1 localhost.localdomain
    # 会被误判为"已有 localhost 条目"，真正的 localhost 条目就补不上了
    grep -qE '^\s*127\.0\.0\.1\s+localhost([[:space:]]|$)' /etc/hosts 2>/dev/null \
        || echo "127.0.0.1 localhost" | sudo tee -a /etc/hosts > /dev/null
    grep -qE '^\s*::1\s+localhost([[:space:]]|$)' /etc/hosts 2>/dev/null \
        || echo "::1 localhost ip6-localhost ip6-loopback" | sudo tee -a /etc/hosts > /dev/null
    echo -e "${GREEN}✓ hosts 已清理完成（备份: $backup）${NC}"
}

calibrate_joystick_stick() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 校准摇杆 ════════════════${NC}"
    if thumbstick_cal; then echo -e "${GREEN}✓ 摇杆校准完成${NC}"; else echo -e "${RED}✗ 摇杆校准失败${NC}"; echo "请确保系统中已安装摇杆校准工具 (thumbstick_cal)"; fi
}

calibrate_joystick_trigger() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 校准扳机 ════════════════${NC}"
    if trigger_cal; then echo -e "${GREEN}✓ 扳机校准完成${NC}"; else echo -e "${RED}✗ 扳机校准失败${NC}"; echo "请确保系统中已安装扳机校准工具 (trigger_cal)"; fi
}

steamdeck_cache_manager() {
    # 没有 zenity 时原来还去调 zenity 报错，等于什么都不显示；改为写到标准输出
    if ! command -v zenity &>/dev/null; then
        echo -e "${RED}✗ 未找到 zenity，无法打开缓存管理器。请先安装：sudo pacman -S zenity${NC}"
        return 1
    fi
    mk_temp_dir

    # 收集所有 Steam 库的 steamapps 目录：默认库 + libraryfolders.vdf 里的其它库。
    # 原实现只写死 $HOME/.local/share/Steam/steamapps，装在 SD 卡/第二块盘的库
    # 根本不会出现在列表里（实测本机 VDF 就有 /run/media/deck/Game/SteamLibrary）。
    local steam_root="$HOME/.local/share/Steam"
    local -a steamapps_dirs=()
    [ -d "$steam_root/steamapps" ] && steamapps_dirs+=("$steam_root/steamapps")
    local vdf="$steam_root/steamapps/libraryfolders.vdf"
    if [ -f "$vdf" ]; then
        local lib_path
        while IFS= read -r lib_path; do
            [ -n "$lib_path" ] || continue
            [ -d "$lib_path/steamapps" ] || continue
            local dup=0 d
            for d in "${steamapps_dirs[@]}"; do
                [ "$d" = "$lib_path/steamapps" ] && { dup=1; break; }
            done
            [ "$dup" -eq 0 ] && steamapps_dirs+=("$lib_path/steamapps")
        done < <(awk -F'"' '/"path"/ {print $4}' "$vdf" 2>/dev/null)
    fi
    if [ ${#steamapps_dirs[@]} -eq 0 ]; then
        zenity --error --text="未找到 Steam 库目录，请确认 Steam 已安装并至少登录过一次。"
        return 1
    fi

    # 删除 compatdata/着色器缓存前提醒退出 Steam，否则可能损坏正在使用的数据
    local steam_running=0
    if pgrep -x steam >/dev/null 2>&1 || pgrep -x steamwebhelper >/dev/null 2>&1; then
        steam_running=1
        if ! zenity --question --title="Steam 正在运行" \
            --text="检测到 Steam 正在运行。删除兼容数据时可能损坏正在使用的 Proton 前缀。建议先退出 Steam 再清理。仍要继续吗？" \
            --ok-label="继续" --cancel-label="取消"; then
            return 0
        fi
    fi

    while true; do
        local choice
        # 单选列表第一列必须有一个 TRUE，否则直接点确定返回空、用户以为没反应
        choice=$(zenity --list --radiolist \
            --title="Steam 缓存管理器" \
            --text="请选择要清理的缓存类型" \
            --column="选择" --column="类型" --column="说明" \
            TRUE  "着色器缓存" "shadercache，删掉后会自动重建" \
            FALSE "兼容数据" "compatdata，含各游戏的 Proton 前缀" \
            --width=600 --height=240) || break
        [ -z "$choice" ] && break

        local cache_type title
        if [ "$choice" = "着色器缓存" ]; then
            cache_type="shadercache"; title="着色器缓存"
        else
            cache_type="compatdata"; title="兼容数据"
        fi

        # 用平行数组保存，避免把游戏名拼进 | 分隔字符串（名字里带 | 会解析错位）
        local -a app_ids=() app_names=() app_sizes=() app_dirs=()
        local sa dir app_id size manifest game_name
        for sa in "${steamapps_dirs[@]}"; do
            [ -d "$sa/$cache_type" ] || continue
            for dir in "$sa/$cache_type"/*; do
                [ -d "$dir" ] || continue
                app_id=$(basename "$dir")
                [[ "$app_id" =~ ^[0-9]+$ ]] || continue
                size=$(du -sm "$dir" 2>/dev/null | cut -f1)
                if [ -z "$size" ] || [ "$size" -le 0 ] 2>/dev/null; then
                    continue
                fi
                game_name=""
                manifest="$sa/appmanifest_${app_id}.acf"
                [ -f "$manifest" ] && game_name=$(grep -m1 '"name"' "$manifest" 2>/dev/null | cut -d'"' -f4)
                [ -z "$game_name" ] && game_name="未知应用"
                app_ids+=("$app_id"); app_names+=("$game_name")
                app_sizes+=("$size"); app_dirs+=("$dir")
            done
        done

        if [ ${#app_ids[@]} -eq 0 ]; then
            zenity --info --text="没有找到可清理的$title。"
            continue
        fi

        local -a list_data=()
        local i
        for i in "${!app_ids[@]}"; do
            list_data+=("FALSE" "${app_ids[$i]}" "${app_names[$i]}" "${app_sizes[$i]}MB")
        done

        local selections
        # ID 列隐藏但用它回传匹配：避免按"显示名"匹配（重名/名字带 | 时都会错）
        selections=$(zenity --list --checklist \
            --title="选择要删除的$title" \
            --text="共 ${#app_ids[@]} 项，可勾选多项后点确定。" \
            --column="选择" --column="ID" --column="应用名" --column="大小" \
            --hide-column=2 --print-column=2 --separator=$'\n' \
            "${list_data[@]}" \
            --width=720 --height=460) || continue
        [ -z "$selections" ] && continue

        local -a sel_dirs=() sel_labels=()
        local sel_line
        while IFS= read -r sel_line; do
            [ -n "$sel_line" ] || continue
            for i in "${!app_ids[@]}"; do
                if [ "${app_ids[$i]}" = "$sel_line" ]; then
                    sel_dirs+=("${app_dirs[$i]}")
                    sel_labels+=("${app_names[$i]} (${app_sizes[$i]}MB)")
                    break
                fi
            done
        done <<< "$selections"

        if [ ${#sel_dirs[@]} -eq 0 ]; then
            zenity --info --text="未选择任何有效项目。"
            continue
        fi

        # 确认框里列出具体条目和总大小，删除前让用户看清楚删的是什么
        local total_mb=0 label one_mb
        for i in "${!sel_dirs[@]}"; do
            label="${sel_labels[$i]}"
            # du 失败时输出为空，直接参与 $(( )) 会算术语法报错，先兜底成 0
            one_mb=$(du -sm "${sel_dirs[$i]}" 2>/dev/null | cut -f1)
            [[ "$one_mb" =~ ^[0-9]+$ ]] || one_mb=0
            total_mb=$((total_mb + one_mb))
        done
        local confirm_text="将永久删除以下 $title："
        for label in "${sel_labels[@]}"; do
            confirm_text+=$'\n'"  • $label"
        done
        confirm_text+=$'\n\n'"共 ${#sel_dirs[@]} 项，约 ${total_mb}MB，删除后无法恢复。"
        zenity --question --title="确认删除" --text="$confirm_text" \
            --ok-label="删除" --cancel-label="取消" || continue

        local deleted=0 failed=0
        for i in "${!sel_dirs[@]}"; do
            if rm -rf -- "${sel_dirs[$i]}" 2>/dev/null; then
                deleted=$((deleted + 1))
            else
                failed=$((failed + 1))
            fi
        done

        local result_text="删除完成。"
        result_text+=$'\n'"成功: $deleted 项"
        result_text+=$'\n'"失败: $failed 项"
        [ "$failed" -gt 0 ] && result_text+=$'\n\n'"失败项可能正被占用，请退出 Steam 后重试。"
        [ "$steam_running" -eq 1 ] && result_text+=$'\n'"建议重启 Steam 让缓存重新生成。"
        zenity --info --text="$result_text"
    done
}

fix_boot() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 修复引导 ════════════════${NC}"
    echo -e "${CYAN}正在运行引导修复脚本...${NC}"

    cat > "$TEMP_DIR/fix_boot.sh" << 'EOF'
#!/bin/bash

echo "========================================"
echo "  Clover启动顺序自动设置脚本"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "⚠️ 检测到需要管理员权限，正在提升权限..."
    echo "   如需修改启动顺序，请输入您的用户密码（输入时不会显示）"
    echo ""
    sudo "$0" "$@"
    exit $?
fi

if ! command -v efibootmgr &> /dev/null; then
    echo "❌ 错误：未找到efibootmgr命令。"
    echo "   请确保系统已安装efibootmgr工具。"
    exit 1
fi

echo "1. 正在扫描UEFI启动项..."
echo "----------------------------------------"

BACKUP_FILE="/tmp/boot_backup_$(date +%Y%m%d_%H%M%S).txt"
CURRENT_BOOT_ORDER=$(efibootmgr | grep "BootOrder")
echo "当前启动顺序: $CURRENT_BOOT_ORDER"
efibootmgr -v > "$BACKUP_FILE"
echo "启动项备份已保存到: $BACKUP_FILE"

echo ""
echo "2. 正在查找Clover启动项..."
echo "----------------------------------------"

CLOVER_ENTRY=$(efibootmgr -v | grep -i "CLOVER" | head -1)

if [ -z "$CLOVER_ENTRY" ]; then
    echo "❌ 未找到Clover启动项！可能的原因："
    echo "   • Clover尚未安装或安装不正确"
    echo "   • Clover的EFI文件不在标准位置"
    echo "   • 启动项名称不包含'CLOVER'关键字"
    echo ""
    echo "当前所有启动项列表："
    efibootmgr | grep "Boot[0-9A-F][0-9A-F][0-9A-F][0-9A-F]"
    echo ""
    echo "⚠️ 建议：请确保Clover已正确安装到ESP分区，然后重试。"
    exit 1
fi

CLOVER_BOOTNUM=$(echo "$CLOVER_ENTRY" | grep -o 'Boot[0-9A-F]\{4\}' | head -1 | sed 's/Boot//')

echo "✅ 找到Clover启动项："
echo "   启动编号: Boot$CLOVER_BOOTNUM"
echo "   描述: $CLOVER_ENTRY"

echo ""
echo "3. 正在分析当前启动顺序..."
echo "----------------------------------------"

CURRENT_ORDER=$(efibootmgr | grep "BootOrder" | cut -d: -f2 | tr -d ' ')

if [ -z "$CURRENT_ORDER" ]; then
    echo "⚠️  无法获取当前启动顺序，将创建新顺序。"
    NEW_ORDER="$CLOVER_BOOTNUM"
else
    if [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM,"* ]] || [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM" ]]; then
        echo "✅ Clover已在启动顺序的首位，无需修改。"
        echo "   当前顺序: $CURRENT_ORDER"
        exit 0
    fi

    NEW_ORDER="$CLOVER_BOOTNUM,$(echo "$CURRENT_ORDER" | tr ',' '\n' | grep -v "^$CLOVER_BOOTNUM$" | tr '\n' ',' | sed 's/,$//')"
fi

echo "当前顺序: $CURRENT_ORDER"
echo "新顺序: $NEW_ORDER"

echo ""
echo "4. 确认设置"
echo "----------------------------------------"
echo "脚本将执行以下操作："
echo "  • 将Clover (Boot$CLOVER_BOOTNUM) 设为第一启动项"
echo "  • 其他启动项顺序保持不变"
echo ""

read -n1 -p "按回车键或 A 键确认，其他键取消: " confirm_boot < /dev/tty
echo

if [[ -z "$confirm_boot" || "$confirm_boot" =~ [Aa] ]]; then
    echo "继续执行..."
else
    echo "❌ 操作已取消。"
    exit 0
fi

echo ""
echo "5. 正在设置启动顺序..."
echo "----------------------------------------"

efibootmgr -o "$NEW_ORDER"

echo ""
echo "6. 验证设置结果"
echo "----------------------------------------"

RESULT=$(efibootmgr | grep "BootOrder")
echo "最终启动顺序: $RESULT"

if echo "$RESULT" | grep -q "^BootOrder: $CLOVER_BOOTNUM,"; then
    echo ""
    echo "✅ 设置成功！Clover (Boot$CLOVER_BOOTNUM) 现在是第一启动项。"
    echo ""
    echo "下次重启时将首先进入Clover引导菜单。"
    echo "要测试设置，请重启Steam Deck。"
else
    echo ""
    echo "⚠️  设置可能未完全生效。"
    echo "   请手动运行 'efibootmgr -v' 检查设置。"
fi

echo ""
echo "========================================"
echo "脚本执行完成"
echo "========================================"
echo "提示：如需恢复原设置，可参考备份文件: $BACKUP_FILE"
EOF

    chmod +x "$TEMP_DIR/fix_boot.sh"
    "$TEMP_DIR/fix_boot.sh"
}

# 安全地从 fstab 移除指定条目（按第一字段精确比对，不用正则，避免特殊字符/前缀误伤）
fstab_remove_entry() {
    local key="$1"
    [ -z "$key" ] && return 1
    [ -f /etc/fstab ] || return 1
    # 先比对该 key 是否存在，避免无谓写入
    awk -v k="$key" '$1 == k {found=1} END {exit !found}' /etc/fstab 2>/dev/null || return 1
    # 备份后用 awk 过滤写回（临时文件放在 /tmp 并显式给读权限，避免权限问题）
    local tmp="${TEMP_DIR:-/tmp}/fstab.$$"
    mkdir -p "$(dirname "$tmp")" 2>/dev/null
    awk -v k="$key" '$1 != k' /etc/fstab > "$tmp" 2>/dev/null || { rm -f "$tmp"; return 1; }
    chmod 644 "$tmp" 2>/dev/null
    sudo cp "$tmp" /etc/fstab && rm -f "$tmp"
}

fix_shared_disk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 自动挂载 Windows 分区 ════════════════${NC}"
    echo ""

    echo "步骤1: 检查 SteamOS 只读模式"
    if command -v steamos-readonly &>/dev/null; then
        # 记录进入时状态，退出时由全局 trap 统一恢复（仅当是脚本关掉的）
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            if sudo steamos-readonly disable 2>/dev/null; then
                RO_READONLY_DISABLED_BY_US=1
                echo -e "${GREEN}✓ 已临时禁用只读模式${NC}"
            else
                echo -e "${YELLOW}⚠️  禁用只读模式失败，后续写入 fstab 可能失败${NC}"
            fi
        else
            echo -e "${GREEN}✓ 系统已处于可写模式${NC}"
        fi
    else
        echo -e "${GREEN}✓ 非 SteamOS 系统，跳过${NC}"
    fi
    echo ""

    echo "步骤2: 修改 UDisks2 权限文件"
    UDISKS2_FILE="/usr/share/polkit-1/actions/org.freedesktop.UDisks2.policy"
    if [ -f "$UDISKS2_FILE" ]; then
        sudo cp "$UDISKS2_FILE" "$UDISKS2_FILE.backup.$(date +%Y%m%d)" 2>/dev/null
        sudo sed -i '/<action id="org.freedesktop.udisks2.filesystem-mount-system">/,/<\/action>/ {
            s|<allow_active>[^<]*</allow_active>|<allow_active>yes</allow_active>|
        }' "$UDISKS2_FILE" 2>/dev/null
        # 校验是否真的改成功，而不是无条件报“已修改”
        if awk '/<action id="org.freedesktop.udisks2.filesystem-mount-system">/,/<\/action>/' "$UDISKS2_FILE" 2>/dev/null | grep -q '<allow_active>yes</allow_active>'; then
            echo -e "${GREEN}✓ 已修改${NC}"
        else
            echo -e "${YELLOW}⚠️  未能确认修改结果，请检查 $UDISKS2_FILE${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  未找到 UDisks2 文件，跳过${NC}"
    fi
    echo ""

    echo "步骤3: 扫描 Windows (NTFS) 分区（忽略恢复分区）..."
    local sys_mounts=("/" "/home" "/var" "/efi" "/esp" "/boot" "/boot/efi")
    local recovery_guid="de94bba4-06d1-4d40-a16a-bfd50179d6ac"

    local part_devices=()
    local part_labels=()
    local part_mountpoints=()
    local part_uuids=()
    local part_sizes=()
    local part_count=0
    # 互通盘的核心目标是“重启后依然自动挂载”，靠的是 fstab 持久化。
    # 因此不能只看分区当前是否已挂载——udisks 自动挂载的分区重启后就会消失。
    # 这里改为：只有当「已挂载 且 fstab 中已有对应条目 且 挂载点一致」才算真正就绪。
    local all_ready=true
    local fail_count=0

    echo "  清理无效的 fstab 条目..."
    local bad_entries=()
    while IFS= read -r line; do
        if echo "$line" | grep -qE '^\s*UUID=[^\s]+\s+(\S+)\s+ntfs'; then
            mp=$(echo "$line" | awk '{print $2}')
            if [[ -z "$mp" || "$mp" != /* || "$mp" =~ ^[A-F0-9]{8,} ]]; then
                bad_entries+=("$line")
            fi
        fi
    done < /etc/fstab
    if [ ${#bad_entries[@]} -gt 0 ]; then
        echo "  检测到 ${#bad_entries[@]} 条无效条目，正在删除..."
        sudo cp /etc/fstab "/etc/fstab.toolbox.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null
        for entry in "${bad_entries[@]}"; do
            # 按第一字段精确删除，不用正则，避免特殊字符导致误删
            fstab_remove_entry "$(echo "$entry" | awk '{print $1}')"
        done
        echo -e "${GREEN}✓ 无效条目已清除${NC}"
    fi

    while IFS= read -r line; do
        parse_line "$line"

        name="$NAME"
        type="$TYPE"
        label="$LABEL"
        fstype="$FSTYPE"
        mountpoint="$MOUNTPOINT"
        uuid="$UUID"
        parttype="$PARTTYPE"
        size="$SIZE"

        [[ "$type" != "part" ]] && continue
        [[ ! "$fstype" =~ ^(ntfs|fuseblk|ntfs3)$ ]] && continue

        local skip=0
        for sysmp in "${sys_mounts[@]}"; do
            if [[ "$mountpoint" == "$sysmp" ]]; then
                skip=1
                break
            fi
        done
        [ $skip -eq 1 ] && continue

        if [ -n "$parttype" ] && [[ "${parttype,,}" == "$recovery_guid" ]]; then
            if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ] && mountpoint -q "$mountpoint" 2>/dev/null; then
                echo "  恢复分区 $name 已挂载，正在卸载..."
                sudo umount "$mountpoint" 2>/dev/null
            fi
            if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ] && [ -d "$mountpoint" ]; then
                if [ -z "$(ls -A "$mountpoint" 2>/dev/null)" ]; then
                    sudo rmdir "$mountpoint" 2>/dev/null && echo "  已删除空挂载点 $mountpoint"
                fi
            fi
            continue
        fi

        part_devices+=("/dev/$name")
        part_labels+=("${label:-}")
        if [ "$mountpoint" = "None" ] || [ -z "$mountpoint" ]; then
            part_mountpoints+=("")
        else
            part_mountpoints+=("$mountpoint")
        fi
        part_uuids+=("$uuid")
        part_sizes+=("${size:-}")
        ((part_count++))

        if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ] && mountpoint -q "$mountpoint" 2>/dev/null; then
            # 已挂载，还要确认 fstab 里有精确匹配该 UUID 的条目（子串匹配会误判，用锚定正则）
            if [ -n "$uuid" ] && grep -qE "^[[:space:]]*UUID=${uuid}[[:space:]]" /etc/fstab 2>/dev/null; then
                :
            else
                all_ready=false
            fi
        else
            all_ready=false
        fi
    done < <(lsblk -P -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID,PARTTYPE,SIZE --noheadings 2>/dev/null)

    if [ $part_count -eq 0 ]; then
        while IFS= read -r source fstype mountpoint; do
            if [[ "$source" =~ ^/dev/ ]]; then
                dev="$source"
                label=$(lsblk -n -o LABEL "$dev" 2>/dev/null)
                uuid=$(lsblk -n -o UUID "$dev" 2>/dev/null)
                size=$(lsblk -n -o SIZE "$dev" 2>/dev/null)
                part_devices+=("$dev")
                part_labels+=("${label:-无标签}")
                part_mountpoints+=("$mountpoint")
                part_uuids+=("${uuid:-}")
                part_sizes+=("${size:-}")
                ((part_count++))
            fi
        done < <(findmnt -t ntfs,fuseblk,ntfs3 -o SOURCE,FSTYPE,TARGET -n 2>/dev/null)
    fi

    if [ $part_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  未检测到任何符合条件的 Windows (NTFS) 分区。${NC}"
        return
    fi

    echo -e "${CYAN}检测到以下 Windows 分区：${NC}"
    for ((i=0; i<part_count; i++)); do
        local mp_display="${part_mountpoints[$i]:-未挂载}"
        echo "  $((i+1)). ${part_devices[$i]}  标签:${part_labels[$i]:-无}  大小:${part_sizes[$i]}  挂载点:${mp_display}"
    done
    echo ""

    echo "步骤4: 清理 /run/media/deck/ 下非 Windows 分区的挂载和 fstab 条目..."
    local cleaned=0

    # 注意：这里曾经会强制卸载 /run/media/deck/ 下所有非 NTFS 分区并删除其 fstab 条目，
    # 会误伤用户的 ext4 移动硬盘 / U 盘 / Btrfs 外置盘。互通盘功能没有理由动它们，
    # 因此改为：只清理「fstab 中引用了已不存在设备」的残留条目，绝不主动卸载任何分区。
    while IFS= read -r mp; do
        [ -z "$mp" ] && continue
        dev=$(findmnt -n -o SOURCE "$mp" 2>/dev/null)
        fstype=$(findmnt -n -o FSTYPE "$mp" 2>/dev/null)
        if [[ ! "$fstype" =~ ^(ntfs|fuseblk|ntfs3|ntfs-3g)$ ]]; then
            if [ -n "$dev" ] && [ ! -b "$dev" ]; then
                echo "  清理失效的挂载记录: $mp ($fstype)"
                if [ -n "$dev" ]; then
                    local _u
                    _u=$(lsblk -n -o UUID "$dev" 2>/dev/null)
                    [ -n "$_u" ] && fstab_remove_entry "UUID=$_u"
                    fstab_remove_entry "$dev"
                fi
                ((cleaned++))
            else
                echo -e "${YELLOW}  保留挂载中的非 NTFS 分区: $mp ($fstype)${NC}"
            fi
        fi
    done < <(findmnt -o TARGET -n -l 2>/dev/null | grep '^/run/media/deck/')

    # 只删除「fstab 中已无引用」的残留空目录，避免误删用户自建的空文件夹
    for d in /run/media/deck/*; do
        [ -d "$d" ] || continue
        mountpoint -q "$d" 2>/dev/null && continue
        [ -z "$(ls -A "$d" 2>/dev/null)" ] || continue
        if grep -qE "^[[:space:]]*(UUID=|/dev/)[^[:space:]]+[[:space:]]+${d}[[:space:]]" /etc/fstab 2>/dev/null; then
            continue
        fi
        echo "  删除残留空目录 $d"
        sudo rmdir "$d" 2>/dev/null && ((cleaned++))
    done

    while IFS= read -r line; do
        if echo "$line" | grep -qE '^\s*(UUID=|/dev/)\S+\s+/run/media/deck/'; then
            mp=$(echo "$line" | awk '{print $2}')
            fs=$(echo "$line" | awk '{print $3}')
            if [[ ! "$fs" =~ ^(ntfs|fuseblk|ntfs3|ntfs-3g)$ ]]; then
                # 安全限制：这里只处理「设备已不存在」的残留条目。
                # 绝不主动卸载/删除仍真实存在的非 NTFS 分区（如用户的 ext4 移动硬盘、
                # U 盘、Btrfs 外置盘），否则会误伤用户数据盘。
                local src
                src=$(echo "$line" | awk '{print $1}')
                local dev_exists=1
                if [[ "$src" =~ ^UUID= ]]; then
                    if [ -e "/dev/disk/by-uuid/${src#UUID=}" ]; then dev_exists=0; fi
                elif [[ "$src" =~ ^/dev/ ]]; then
                    if [ -b "$src" ]; then dev_exists=0; fi
                fi
                if [ $dev_exists -eq 1 ]; then
                    echo "  清理失效的设备条目: $mp ($fs)"
                    fstab_remove_entry "$src"
                    ((cleaned++))
                    if [ -d "$mp" ] && [ -z "$(ls -A "$mp" 2>/dev/null)" ]; then
                        sudo rmdir "$mp" 2>/dev/null
                    fi
                else
                    echo -e "${YELLOW}  保留非 NTFS 分区条目（设备仍存在）: $mp ($fs)${NC}"
                fi
            fi
        fi
    done < /etc/fstab

    if [ $cleaned -gt 0 ]; then
        echo -e "${GREEN}✓ 清理完成${NC}"
    else
        echo "  无需清理。"
    fi
    echo ""

    if $all_ready; then
        echo -e "${GREEN}✅ 所有 Windows 分区均已挂载且已写入 fstab，重启后仍会自动挂载，无需操作。${NC}"
        return
    fi

    echo "步骤5: 开始挂载并写入 fstab..."
    for ((i=0; i<part_count; i++)); do
        device="${part_devices[$i]}"
        label="${part_labels[$i]}"
        mountpoint="${part_mountpoints[$i]}"
        uuid="${part_uuids[$i]}"

        echo -e "\n${CYAN}处理分区 $device${NC}"

        # 关键：先确定这个分区最终应该用哪个挂载点，再处理 fstab。
        # 优先沿用 fstab 里已有的挂载点（避免同一分区出现两个挂载点），
        # 其次沿用当前实际挂载点，最后才按标签/设备名新建。
        local fstab_mp=""
        if [ -n "$uuid" ] && grep -qE "^[[:space:]]*UUID=${uuid}[[:space:]]" /etc/fstab 2>/dev/null; then
            fstab_mp=$(awk -v u="UUID=$uuid" '$1==u {print $2; exit}' /etc/fstab)
        fi

        if [ -n "$fstab_mp" ]; then
            mount_point="$fstab_mp"
            echo "  fstab 中已有条目，挂载点: $mount_point"
        elif [ -n "$mountpoint" ]; then
            mount_point="$mountpoint"
            echo "  当前已挂载到 $mount_point"
        else
            if [ -n "$label" ] && [ "$label" != "None" ]; then
                clean_label=$(echo "$label" | sed 's/ /_/g; s|[/\\]|_|g')
                mount_point="/run/media/deck/$clean_label"
            else
                devname=$(basename "$device")
                mount_point="/run/media/deck/$devname"
            fi
            local suffix=1
            while [ -d "$mount_point" ] && [ -n "$(ls -A "$mount_point" 2>/dev/null)" ]; do
                mount_point="${mount_point%%_*}_$suffix"
                ((suffix++))
            done
            echo "  计划挂载点: $mount_point"
        fi
        sudo mkdir -p "$mount_point"
        sudo chown "${CURRENT_USER}:${CURRENT_GROUP}" "$mount_point" 2>/dev/null

        # 写入/更新 fstab：使用锚定正则精确匹配 UUID，避免子串误判
        if [ -n "$fstab_mp" ]; then
            if [ "$fstab_mp" != "$mount_point" ]; then
                # 已存在但挂载点不同（例如旧路径无效）。
                # 注意：不能「先删除再追加」，万一大写入失败会让条目彻底丢失。
                # 这里用一次性生成完整新文件 + mv 原子替换，保证 fstab 不会出现中间态。
                sudo cp /etc/fstab "/etc/fstab.toolbox.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null
                local _tmp="${TEMP_DIR:-/tmp}/fstab_upd.$$"
                mkdir -p "$(dirname "$_tmp")" 2>/dev/null
                {
                    awk -v k="UUID=$uuid" '$1 != k' /etc/fstab 2>/dev/null
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g rw,exec,uid=1000,gid=1000,windows_names,nofail 0 0"
                } > "$_tmp" 2>/dev/null && chmod 644 "$_tmp" 2>/dev/null \
                    && sudo cp "$_tmp" /etc/fstab && rm -f "$_tmp" \
                    && echo "  已更新 fstab 挂载点 → $mount_point" \
                    || { rm -f "$_tmp"; echo -e "${RED}  ✗ 更新 fstab 失败（原条目未改动）${NC}"; ((fail_count++)); continue; }
            else
                echo "  fstab 条目已正确，无需修改。"
            fi
        else
            if [ -z "$uuid" ]; then
                echo -e "${YELLOW}  ⚠ 该分区没有 UUID，跳过 fstab 写入（重启后可能不会自动挂载）${NC}"
            else
                sudo cp /etc/fstab "/etc/fstab.toolbox.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null
                local _tmp2="${TEMP_DIR:-/tmp}/fstab_add.$$"
                mkdir -p "$(dirname "$_tmp2")" 2>/dev/null
                {
                    cat /etc/fstab 2>/dev/null
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g rw,exec,uid=1000,gid=1000,windows_names,nofail 0 0"
                } > "$_tmp2" 2>/dev/null && chmod 644 "$_tmp2" 2>/dev/null \
                    && sudo cp "$_tmp2" /etc/fstab && rm -f "$_tmp2" \
                    && echo "  已添加 fstab 条目。" \
                    || { rm -f "$_tmp2"; echo -e "${RED}  ✗ 写入 fstab 失败${NC}"; ((fail_count++)); }
            fi
        fi

        if mountpoint -q "$mount_point" 2>/dev/null; then
            echo "  分区已挂载到 $mount_point"
        else
            if sudo systemctl daemon-reload 2>/dev/null; then :; fi
            if sudo mount "$mount_point" 2>/dev/null || sudo mount -U "$uuid" "$mount_point" 2>/dev/null; then
                echo -e "${GREEN}  ✓ 挂载成功到 $mount_point${NC}"
            else
                echo -e "${RED}  ✗ 挂载失败，请检查 dmesg 输出。${NC}"
                echo "  最近的 dmesg NTFS 相关错误："
                sudo dmesg 2>/dev/null | grep -i ntfs | tail -5
                ((fail_count++))
            fi
        fi
    done
    echo ""
    if [ $fail_count -gt 0 ]; then
        echo -e "${YELLOW}⚠️  完成，但有 $fail_count 个分区挂载失败，请查看上面的错误信息。${NC}"
    else
        echo -e "${GREEN}════════════════ 全部完成 ════════════════${NC}"
    fi
}

# ============================================================================
# 系统体检：SteamOS 更新后可排查「掉盘 / 掉引导 / 挂载失效」
# 只读检查，除非用户明确选择修复项，否则不修改任何系统配置
# ============================================================================
# 动态探测 ESP 分区（不能硬编码 /dev/nvme0n1p1：eMMC 是 mmcblk0，分区号也可能不是 1）
detect_esp_partition() {
    local dev="" line
    ESP_DEV=""; ESP_DISK=""; ESP_PARTN=""; ESP_MOUNT=""
    # 1) 已挂载的 /esp（SteamOS）或 /boot/efi（Bazzite）
    #    注意：findmnt -M 也会返回 systemd autofs 的 "systemd-1"，必须过滤出 /dev/ 开头的真实设备
    for mp in /esp /boot/efi; do
        dev=$(findmnt -n -o SOURCE -M "$mp" 2>/dev/null | grep '^/dev/' | head -1 || true)
        if [ -z "$dev" ]; then
            # 兜底：从 mount 输出里找该挂载点对应的设备
            dev=$(mount 2>/dev/null | awk -v m="$mp" '$3 == m {print $1; exit}')
        fi
        if [ -n "$dev" ] && [ -b "$dev" ]; then
            ESP_DEV="$dev"; ESP_MOUNT="$mp"; break
        fi
    done
    # 2) 按 EFI 分区类型 GUID 查找（c12a7328-f81f-11d2-ba4b-00a0c93ec93b）
    if [ -z "$ESP_DEV" ]; then
        dev=$(lsblk -P -n -o PATH,PARTTYPE 2>/dev/null \
            | awk -F'"' '/PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b"/{print $2; exit}' || true)
        [ -n "$dev" ] && [ -b "$dev" ] && ESP_DEV="$dev"
    fi
    [ -n "$ESP_DEV" ] || return 1
    # 注意：lsblk 输出可能带前后空格，必须清理，否则 efibootmgr -p " 1" 会失败
    ESP_DISK="/dev/$(lsblk -n -o PKNAME "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')"
    ESP_PARTN=$(lsblk -n -o PARTN "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')
    [ -n "$ESP_PARTN" ] || ESP_PARTN=1
    return 0
}

# 检查结果累加器
HC_TOTAL=0; HC_OK=0; HC_WARN=0; HC_FAIL=0
HC_FIXABLE=()      # 可自动修复的问题编号
hc_result() {
    # $1=状态 ok/warn/fail  $2=标题  $3=说明  $4=可修复(1/0)  $5=修复函数名
    HC_TOTAL=$((HC_TOTAL + 1))
    case "$1" in
        ok)   HC_OK=$((HC_OK + 1));   echo -e "  ${GREEN}[正常]${NC} $2";;
        warn) HC_WARN=$((HC_WARN + 1)); echo -e "  ${YELLOW}[注意]${NC} $2";;
        fail) HC_FAIL=$((HC_FAIL + 1)); echo -e "  ${RED}[异常]${NC} $2";;
    esac
    [ -n "$3" ] && echo -e "         $3"
    if [ "${4:-0}" -eq 1 ] && [ -n "${5:-}" ]; then
        HC_FIXABLE+=("$1|$2|$5")
        echo -e "         ${CYAN}→ 可通过下方「修复」选项处理${NC}"
    fi
}

# ---------- 单项检查 ----------
hc_check_esp() {
    echo -e "${CYAN}【1/6】ESP（EFI 系统分区）${NC}"
    if detect_esp_partition; then
        hc_result ok "ESP 分区已识别" "$ESP_DEV 挂载于 $ESP_MOUNT"
        # 剩余空间检查（Clover 需要约 15MB）
        local avail
        avail=$(df --output=avail "$ESP_DEV" 2>/dev/null | tail -1 | tr -d ' ')
        if [[ "$avail" =~ ^[0-9]+$ ]]; then
            if [ "$avail" -ge 15000 ]; then
                hc_result ok "ESP 剩余空间充足" "约 $((avail / 1024))MB 可用"
            else
                hc_result warn "ESP 剩余空间偏小" "仅约 $((avail / 1024))MB，安装 Clover 需要约 15MB"
            fi
        fi
        # EFI 目录可读性（需 root 才能列 /esp/efi/EFI）
        if sudo -n ls "$ESP_MOUNT/efi/EFI" &>/dev/null || sudo -n ls "$ESP_MOUNT/EFI" &>/dev/null; then
            hc_result ok "ESP 可正常读取" ""
        else
            hc_result warn "无法读取 ESP 内容（需要 sudo）" "请确认 sudo 可用后重试"
        fi
    else
        hc_result fail "无法识别 ESP 分区" "未找到已挂载的 /esp，也未能按 EFI 分区类型定位"
    fi
    echo ""
}

hc_check_efi_entries() {
    echo -e "${CYAN}【2/6】UEFI 启动项${NC}"
    if ! command -v efibootmgr &>/dev/null; then
        hc_result fail "未找到 efibootmgr" "请安装：sudo pacman -S efibootmgr"
        echo ""; return
    fi
    local efi_out
    efi_out=$(sudo -n efibootmgr 2>/dev/null || efibootmgr 2>/dev/null || true)
    if [ -z "$efi_out" ]; then
        hc_result fail "无法读取 UEFI 启动项" "efibootmgr 执行失败"
        echo ""; return
    fi
    # Clover 启动项
    if echo "$efi_out" | grep -qi "clover"; then
        local cl_num
        cl_num=$(echo "$efi_out" | grep -i "clover" | head -1 | grep -o 'Boot[0-9A-Fa-f]\{4\}' | head -1)
        hc_result ok "Clover 启动项存在" "$cl_num"
    else
        hc_result fail "Clover 启动项缺失" "SteamOS 更新或固件重置后常见，将从 ESP 重新注册" 1 "hc_fix_clover_entry"
    fi
    # SteamOS 启动项
    if echo "$efi_out" | grep -qi "steamos\|steamcl"; then
        hc_result ok "SteamOS 启动项存在" ""
    else
        hc_result fail "SteamOS 启动项缺失" "将从 ESP 重新注册" 1 "hc_fix_steamos_entry"
    fi
    # Windows 启动项（不是必需：Clover 会接管）
    if echo "$efi_out" | grep -qi "windows"; then
        hc_result ok "Windows 启动项存在" ""
    else
        hc_result warn "Windows 启动项缺失（Clover 会接管，通常正常）" "若要在固件菜单直接启动 Windows 才需要"
    fi
    # 启动顺序
    local order first
    order=$(echo "$efi_out" | grep "BootOrder" | cut -d: -f2 | tr -d ' ')
    first=$(echo "$order" | cut -d, -f1)
    if [ -n "$first" ] && echo "$efi_out" | grep -i "clover" | grep -q "Boot$first"; then
        hc_result ok "Clover 为第一启动项" "BootOrder: $order"
    else
        hc_result warn "Clover 不是第一启动项" "当前顺序: ${order:-未知}" 1 "hc_fix_boot_order"
    fi
    echo ""
}

hc_check_clover_files() {
    echo -e "${CYAN}【3/6】Clover 引导文件完整性${NC}"
    if [ -z "${ESP_DEV:-}" ]; then
        hc_result warn "跳过：ESP 未识别" ""
        echo ""; return
    fi
    # 若 ESP 未挂载，临时挂到一个只读目录来检查内容
    local tmp_mount="" efi_root=""
    if [ -z "${ESP_MOUNT:-}" ]; then
        tmp_mount=$(mktemp -d 2>/dev/null) || tmp_mount=""
        if [ -n "$tmp_mount" ] && sudo -n mount -o ro "$ESP_DEV" "$tmp_mount" 2>/dev/null; then
            ESP_MOUNT="$tmp_mount"
        else
            rmdir "$tmp_mount" 2>/dev/null
            hc_result warn "ESP 未挂载，且无法临时挂载检查" "请先挂载：sudo mount $ESP_DEV /mnt"
            echo ""; return
        fi
    fi
    efi_root="$ESP_MOUNT/efi/EFI"
    [ -d "$ESP_MOUNT/EFI" ] && efi_root="$ESP_MOUNT/EFI"

    # 关键：必须区分「文件真的不存在」和「没有 sudo 权限看不到」，
    # 否则 sudo -n 失效时会把每个文件都误报成缺失。
    # 用 sudo -n ls 探测一次读权限，成功才继续逐文件判断。
    if ! sudo -n ls "$efi_root" &>/dev/null; then
        hc_result warn "无法读取 ESP 上的 EFI 目录（需要 sudo 密码）" \
            "本次跳过 Clover 文件检查；请在体检时输入密码，或手动执行：sudo ls $efi_root"
        [ -n "$tmp_mount" ] && { sudo -n umount "$tmp_mount" 2>/dev/null; rmdir "$tmp_mount" 2>/dev/null; }
        echo ""; return
    fi

    # 列出实际内容，用于更准确的判断
    local efi_list
    efi_list=$(sudo -n ls "$efi_root" 2>/dev/null || true)

    # Clover 主程序
    if sudo -n test -f "$efi_root/clover/cloverx64.efi" 2>/dev/null; then
        hc_result ok "Clover EFI 主程序存在" "$efi_root/clover/cloverx64.efi"
    elif echo "$efi_list" | grep -qx "clover"; then
        hc_result fail "Clover 目录存在但缺少 cloverx64.efi" "引导文件不完整，需要重装 Clover"
    else
        hc_result fail "Clover EFI 主程序缺失" "需要重装 Clover（引导管理 → 安装/重装 Clover）"
    fi
    # Clover 配置
    if sudo -n test -f "$efi_root/clover/config.plist" 2>/dev/null; then
        hc_result ok "Clover 配置文件存在" ""
    elif echo "$efi_list" | grep -qx "clover"; then
        hc_result warn "Clover 配置文件缺失" "重装 Clover 可恢复默认配置"
    fi
    # BOOTX64.EFI 是否为 Clover（原始文件应已备份为 .orig）
    local boot_dir=""
    for cand in BOOT boot; do
        if echo "$efi_list" | grep -qx "$cand"; then boot_dir="$cand"; break; fi
    done
    if [ -n "$boot_dir" ]; then
        if sudo -n test -f "$efi_root/$boot_dir/BOOTX64.EFI" 2>/dev/null \
            || sudo -n test -f "$efi_root/$boot_dir/bootx64.efi" 2>/dev/null; then
            if sudo -n test -f "$efi_root/$boot_dir/BOOTX64.EFI.orig" 2>/dev/null \
                || sudo -n test -f "$efi_root/$boot_dir/bootx64.efi.orig" 2>/dev/null; then
                hc_result ok "BOOTX64.EFI 已被 Clover 接管" "原文件已备份为 .orig"
            else
                hc_result warn "未找到 BOOTX64.EFI 备份（.orig）" "若 Clover 仍能启动则通常无妨"
            fi
        else
            hc_result warn "BOOT 目录下未找到 bootx64.efi" ""
        fi
    fi
    # 卸载临时挂载点
    if [ -n "$tmp_mount" ]; then
        sudo -n umount "$tmp_mount" 2>/dev/null
        rmdir "$tmp_mount" 2>/dev/null
    fi
    echo ""
}

hc_check_windows_partition() {
    echo -e "${CYAN}【4/6】Windows 分区${NC}"
    local found=0 win_dev="" win_mp=""
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        local nm fs lb mp
        nm=$(echo "$line" | sed -n 's/.*NAME="\([^"]*\)".*/\1/p')
        fs=$(echo "$line" | sed -n 's/.*FSTYPE="\([^"]*\)".*/\1/p')
        lb=$(echo "$line" | sed -n 's/.*LABEL="\([^"]*\)".*/\1/p')
        mp=$(echo "$line" | sed -n 's/.*MOUNTPOINT="\([^"]*\)".*/\1/p')
        case "$fs" in
            ntfs|fuseblk|ntfs3)
                found=1
                if [ "$lb" = "Windows" ]; then
                    win_dev="/dev/$nm"; win_mp="$mp"
                fi
                ;;
        esac
    done < <(lsblk -P -n -o NAME,FSTYPE,LABEL,MOUNTPOINT 2>/dev/null)

    if [ "$found" -eq 0 ]; then
        hc_result warn "未发现 NTFS 分区" "若确为 Windows 双系统，请检查硬盘是否松动或分区表异常"
        echo ""; return
    fi
    if [ -n "$win_dev" ]; then
        hc_result ok "Windows 分区存在" "$win_dev${win_mp:+ 挂载于 $win_mp}"
        if [ -n "$win_mp" ] && [ -d "$win_mp" ]; then
            hc_result ok "Windows 分区已挂载" "$win_mp"
        else
            hc_result warn "Windows 分区未挂载" "可通过「修复互通盘」设置自动挂载" 1 "fix_shared_disk"
        fi
        # 检查 Windows 实际文件结构（确认不是空分区）
        local check_mp="$win_mp"
        if [ -z "$check_mp" ] || [ ! -d "$check_mp" ]; then
            for base in /run/media/*/"$nm" /media/*/"$nm"; do
                [ -d "$base" ] && check_mp="$base" && break
            done
        fi
        if [ -n "$check_mp" ] && [ -d "$check_mp" ]; then
            if [ -d "$check_mp/Windows" ] && { [ -d "$check_mp/Program Files" ] || [ -d "$check_mp/Users" ]; }; then
                hc_result ok "Windows 系统文件完整" "检测到 Windows/Program Files/Users"
            else
                hc_result warn "分区内未见 Windows 系统文件" "可能是纯数据盘，或 Windows 已被删除"
            fi
        fi
    else
        hc_result warn "未找到标签为 Windows 的 NTFS 分区" "可能是纯数据盘；如确认有 Windows 请检查分区标签"
    fi
    echo ""
}

hc_check_fstab() {
    echo -e "${CYAN}【5/6】/etc/fstab 挂载配置${NC}"
    if [ ! -f /etc/fstab ]; then
        hc_result fail "找不到 /etc/fstab" ""
        echo ""; return
    fi
    local bad=0 total=0
    while IFS= read -r line; do
        # 跳过注释与空行
        case "$line" in ''|\#*) continue;; esac
        local dev mp rest uuid
        dev=$(echo "$line" | awk '{print $1}')
        mp=$(echo "$line" | awk '{print $2}')
        [ -z "$dev" ] && continue
        total=$((total + 1))
        # UUID= 形式：验证能否在 blkid 中找到
        case "$dev" in
            UUID=*)
                uuid="${dev#UUID=}"
                if ! lsblk -P -n -o UUID 2>/dev/null | grep -q "UUID=\"$uuid\""; then
                    # /home/swapfile 这类不是分区，单独判断
                    if [ "$dev" = "/home/swapfile" ] || echo "$dev" | grep -q "/"; then
                        :
                    else
                        echo -e "  ${RED}[异常]${NC} fstab 条目指向不存在的分区: $dev → $mp"
                        bad=$((bad + 1))
                    fi
                fi
                ;;
            /home/swapfile)
                if [ ! -f /home/swapfile ]; then
                    echo -e "  ${RED}[异常]${NC} fstab 引用 /home/swapfile 但文件不存在"
                    bad=$((bad + 1))
                fi
                ;;
        esac
    done < /etc/fstab
    if [ "$bad" -eq 0 ]; then
        hc_result ok "fstab 条目有效" "共 $total 条有效配置"
    else
        hc_result fail "fstab 有 $bad 条失效条目" "失效条目可能导致开机变慢或进入救援模式" 1 "hc_fix_fstab_invalid"
    fi
    # 检查 systemd 是否报告挂载失败
    local failed_units
    failed_units=$(systemctl list-units --state=failed --no-legend --plain 2>/dev/null | grep -cE '\.mount|\.swap' || true)
    if [ "${failed_units:-0}" -gt 0 ]; then
        hc_result fail "有 $failed_units 个挂载单元失败" "systemctl --failed 可查看详情"
    else
        hc_result ok "无失败的挂载单元" ""
    fi
    echo ""
}

hc_check_system() {
    echo -e "${CYAN}【6/6】系统与引导服务${NC}"
    # SteamOS 只读模式
    if command -v steamos-readonly &>/dev/null; then
        local ro
        ro=$(steamos-readonly status 2>/dev/null || true)
        if echo "$ro" | grep -q "enabled"; then
            hc_result ok "SteamOS 只读模式正常（enabled）" ""
        else
            hc_result warn "SteamOS 只读模式为 disabled" "通常不改文件时会自动恢复；长期保持可写有被更新覆盖的风险"
        fi
    fi
    # clover-bootmanager 服务（这是掉引导后能自愈的关键）
    local has_clover_svc=0
    if systemctl list-unit-files --no-legend --plain 2>/dev/null \
        | awk '$1 == "clover-bootmanager.service" {found=1} END {exit !found}'; then
        has_clover_svc=1
    fi
    if [ "$has_clover_svc" -eq 1 ]; then
        if systemctl is-enabled clover-bootmanager.service &>/dev/null; then
            hc_result ok "Clover 引导守护服务已启用" "开机自动重建丢失的启动项"
        else
            hc_result fail "Clover 引导守护服务未启用" "启用后可在更新后自动重建启动项" 1 "hc_fix_enable_service"
        fi
        if systemctl is-active clover-bootmanager.service &>/dev/null; then
            hc_result ok "Clover 引导守护服务运行中" ""
        else
            hc_result warn "Clover 引导守护服务未运行" "可手动启动"
        fi
    else
        hc_result warn "未安装 Clover 引导守护服务" "安装 Clover 时会一并安装"
    fi
    # 内核与系统版本（供排查更新是否刚发生）
    hc_result ok "当前内核版本: $(uname -r)" ""
    local os_pretty
    os_pretty=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')
    hc_result ok "系统版本: ${os_pretty:-未知}" ""
    echo ""
}

# ---------- 修复动作 ----------
hc_fix_clover_entry() {
    detect_esp_partition || { echo -e "${RED}✗ 无法识别 ESP，修复中止${NC}"; return 1; }
    echo -e "${CYAN}正在重新注册 Clover 启动项（$ESP_DISK 分区 $ESP_PARTN）...${NC}"
    # 先删旧的同名条目，避免重复
    local old
    old=$(efibootmgr 2>/dev/null | grep -i "clover" | grep -o 'Boot[0-9A-Fa-f]\{4\}' | sed 's/Boot//' | head -1)
    [ -n "$old" ] && sudo efibootmgr -b "$old" -B &>/dev/null
    if sudo efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
        -L "Clover - GUI Boot Manager" -l '\EFI\clover\cloverx64.efi'; then
        echo -e "${GREEN}✓ Clover 启动项已重新注册${NC}"
        return 0
    fi
    echo -e "${RED}✗ 注册失败。ESP 上可能缺少 cloverx64.efi，请重装 Clover。${NC}"
    return 1
}

hc_fix_steamos_entry() {
    detect_esp_partition || { echo -e "${RED}✗ 无法识别 ESP，修复中止${NC}"; return 1; }
    echo -e "${CYAN}正在重新注册 SteamOS 启动项...${NC}"
    local old
    old=$(efibootmgr 2>/dev/null | grep -i "steamos" | grep -o 'Boot[0-9A-Fa-f]\{4\}' | sed 's/Boot//' | head -1)
    [ -n "$old" ] && sudo efibootmgr -b "$old" -B &>/dev/null
    if sudo efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
        -L "SteamOS" -l '\EFI\steamos\steamcl.efi'; then
        echo -e "${GREEN}✓ SteamOS 启动项已重新注册${NC}"
        return 0
    fi
    echo -e "${RED}✗ 注册失败，ESP 上可能缺少 steamcl.efi${NC}"
    return 1
}

hc_fix_boot_order() {
    local cl
    cl=$(efibootmgr 2>/dev/null | grep -i "clover" | grep -o 'Boot[0-9A-Fa-f]\{4\}' | head -1 | sed 's/Boot//')
    if [ -z "$cl" ]; then
        echo -e "${RED}✗ 未找到 Clover 启动项，请先修复启动项${NC}"
        return 1
    fi
    local cur new
    cur=$(efibootmgr 2>/dev/null | grep "BootOrder" | cut -d: -f2 | tr -d ' ')
    new="$cl"
    if [ -n "$cur" ]; then
        new="$cl,$(echo "$cur" | tr ',' '\n' | grep -vx "$cl" | tr '\n' ',' | sed 's/,$//')"
    fi
    echo -e "${CYAN}启动顺序: ${cur:-空} → $new${NC}"
    if sudo efibootmgr -o "$new"; then
        echo -e "${GREEN}✓ Clover 已设为第一启动项${NC}"
        return 0
    fi
    echo -e "${RED}✗ 设置启动顺序失败${NC}"
    return 1
}

hc_fix_enable_service() {
    if sudo systemctl enable --now clover-bootmanager.service 2>/dev/null; then
        echo -e "${GREEN}✓ Clover 引导守护服务已启用${NC}"
        return 0
    fi
    echo -e "${RED}✗ 启用失败，请手动执行: sudo systemctl enable --now clover-bootmanager.service${NC}"
    return 1
}

hc_fix_fstab_invalid() {
    echo -e "${CYAN}备份 /etc/fstab 并注释掉失效条目...${NC}"
    local backup="/etc/fstab.backup.$(date +%Y%m%d_%H%M%S)"
    if ! sudo cp /etc/fstab "$backup" 2>/dev/null; then
        echo -e "${RED}✗ 备份失败，为保证安全已中止${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ 已备份到 $backup${NC}"
    local tmp="${TEMP_DIR}/fstab.hc.$$"
    local changed=0
    while IFS= read -r line; do
        case "$line" in
            ''|\#*) echo "$line"; continue;;
        esac
        local dev
        dev=$(echo "$line" | awk '{print $1}')
        case "$dev" in
            UUID=*)
                local uuid="${dev#UUID=}"
                if lsblk -P -n -o UUID 2>/dev/null | grep -q "UUID=\"$uuid\""; then
                    echo "$line"
                elif [ "$dev" = "UUID=/home/swapfile" ]; then
                    echo "$line"
                else
                    echo "# [体检] 分区不存在，已注释: $line"
                    changed=$((changed + 1))
                fi
                ;;
            *)
                echo "$line"
                ;;
        esac
    done < /etc/fstab > "$tmp" 2>/dev/null
    if [ "$changed" -eq 0 ]; then
        rm -f "$tmp"
        echo -e "${YELLOW}未发现需要注释的条目${NC}"
        return 0
    fi
    if sudo cp "$tmp" /etc/fstab; then
        rm -f "$tmp"
        sudo systemctl daemon-reload 2>/dev/null
        echo -e "${GREEN}✓ 已注释 $changed 条失效条目（原文件备份在 $backup）${NC}"
        return 0
    fi
    rm -f "$tmp"
    echo -e "${RED}✗ 写入失败，/etc/fstab 未被修改${NC}"
    return 1
}

# 交互式修复入口
hc_run_fixes() {
    if [ ${#HC_FIXABLE[@]} -eq 0 ]; then
        echo -e "${GREEN}没有发现可自动修复的问题。${NC}"
        return 0
    fi
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}✗ 修复需要 sudo 权限，已跳过${NC}"
        return 1
    fi
    echo -e "${YELLOW}════════════════ 开始修复 ════════════════${NC}"
    local item state title fn
    for item in "${HC_FIXABLE[@]}"; do
        state="${item%%|*}"
        title="${item#*|}"; title="${title%%|*}"
        fn="${item##*|}"
        echo ""
        echo -e "${CYAN}修复: $title${NC}"
        if declare -f "$fn" >/dev/null; then
            "$fn"
            if [ $? -ne 0 ]; then
                echo -e "${YELLOW}该项修复未成功，请查看上方提示${NC}"
            fi
        else
            echo -e "${RED}内部错误：修复函数 $fn 不存在${NC}"
        fi
    done
    echo ""
    echo -e "${YELLOW}提示：建议修复后重新运行一次体检确认结果。${NC}"
}

health_check() {
    mk_temp_dir
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         SteamOS 系统体检（更新后排障）        ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo "用于排查 SteamOS 更新后常见的：掉盘、掉引导、挂载失效。"
    echo "检查过程为只读，仅在您确认后才执行修复。"
    echo ""
    echo "正在检查，需要 sudo 权限读取 EFI 分区内容..."
    if ! sudo -v 2>/dev/null; then
        echo -e "${YELLOW}⚠ 未获取 sudo 权限：部分检查（ESP 内容、启动项）将无法完成${NC}"
    fi
    echo ""
    echo -e "${CYAN}──────────────── 检查结果 ────────────────${NC}"
    echo ""
    hc_check_esp
    hc_check_efi_entries
    hc_check_clover_files
    hc_check_windows_partition
    hc_check_fstab
    hc_check_system
    echo -e "${CYAN}──────────────── 汇总 ────────────────${NC}"
    echo -e "  共检查 $HC_TOTAL 项：${GREEN}正常 $HC_OK${NC} ｜ ${YELLOW}注意 $HC_WARN${NC} ｜ ${RED}异常 $HC_FAIL${NC}"
    echo ""

    if [ "$HC_FAIL" -eq 0 ] && [ "$HC_WARN" -eq 0 ]; then
        echo -e "${GREEN}✅ 系统状态良好，未发现问题。${NC}"
        return 0
    fi
    if [ ${#HC_FIXABLE[@]} -gt 0 ]; then
        echo -e "${YELLOW}发现 ${#HC_FIXABLE[@]} 个可自动修复的问题。${NC}"
        local ans
        if read -p "是否现在修复？(y/N): " -n 1 -r ans < /dev/tty 2>/dev/null; then
            echo ""
            if [[ "$ans" =~ ^[Yy]$ ]]; then
                hc_run_fixes
            else
                echo "已跳过修复。可稍后重新运行体检并选择修复。"
            fi
        else
            echo -e "${YELLOW}无法读取输入（非交互环境），已跳过修复。${NC}"
            echo "如需修复，请按上方「可自动修复」提示手动处理。"
        fi
    else
        echo -e "${YELLOW}以上问题需要手动处理，请按提示操作。${NC}"
    fi
    echo ""
    echo -e "${CYAN}常见原因与建议：${NC}"
    echo "  · SteamOS 更新后 Clover 启动项消失 → 用本功能「修复」重建，或重装 Clover"
    echo "  · Windows 分区不再自动挂载 → 运行「修复互通盘」"
    echo "  · ESP 上 Clover 文件被覆盖 → 需要重装 Clover（引导管理 → 安装/重装 Clover）"
    echo "  · 完全无法开机 / 进不了系统 → 需要用 SteamOS 恢复 U 盘救援，本工具无法覆盖"
}

install_uu_accelerator() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装UU加速器插件 ════════════════${NC}"
    if curl -s uudeck.com | sudo sh; then
        echo -e "${GREEN}✓ UU加速器插件安装完成。${NC}"
    else
        echo -e "${RED}✗ 安装失败（脚本返回错误码），请检查网络后重试。${NC}"
        return 1
    fi
}

install_xunyou_accelerator() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装迅游加速器插件 ════════════════${NC}"
    if curl -s sd.xunyou.com | sudo sh; then
        echo -e "${GREEN}✓ 迅游加速器插件安装完成。${NC}"
    else
        echo -e "${RED}✗ 安装失败（脚本返回错误码），请检查网络后重试。${NC}"
        return 1
    fi
}

install_qiyou_accelerator() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装奇游联机宝加速插件 ════════════════${NC}"
    if curl -s sd.qiyou.cn | sudo sh; then
        echo -e "${GREEN}✓ 奇游联机宝加速插件安装完成。${NC}"
    else
        echo -e "${RED}✗ 安装失败（脚本返回错误码），请检查网络后重试。${NC}"
        return 1
    fi
}

install_asklink() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ AskLink 远程 ════════════════${NC}"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}AskLink 已安装。${NC}"
        echo -e "${YELLOW}按 回车键/A键 卸载，按其他键保持安装并退出。${NC}"
        read -p "请选择: " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY == "" ]]; then
            echo -e "${CYAN}正在卸载 AskLink...${NC}"
            sudo rm -rf /opt/AskLink
            rm -f "$HOME/Desktop/AskLink.desktop"
            sudo rm -f /usr/share/applications/AskLink.desktop
            rm -f "$HOME/.local/share/applications/AskLink.desktop"
            if [ -d "$HOME/Documents/AskLink" ]; then
                rm -rf "$HOME/Documents/AskLink"
                echo -e "${CYAN}已删除配置文件目录 $HOME/Documents/AskLink${NC}"
            fi
            echo -e "${GREEN}✅ AskLink 已卸载。${NC}"
        else
            echo -e "${GREEN}保持 AskLink 安装。${NC}"
        fi
        return 0
    fi

    echo -e "${CYAN}检查 SteamOS 只读状态...${NC}"
    if command -v steamos-readonly &>/dev/null; then
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            echo -e "${CYAN}正在禁用只读模式...${NC}"
            if ! sudo steamos-readonly disable; then
                echo -e "${RED}禁用只读模式失败，请手动执行 sudo steamos-readonly disable${NC}"
                return 1
            fi
            RO_READONLY_DISABLED_BY_US=1
        else
            echo -e "${GREEN}只读模式已禁用${NC}"
        fi
    fi

    if ! command -v dpkg &>/dev/null; then
        echo -e "${CYAN}未检测到 dpkg，正在安装...${NC}"
        if command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm dpkg
            if [ $? -ne 0 ]; then
                echo -e "${RED}安装 dpkg 失败，请手动执行 sudo pacman -S dpkg${NC}"
                return 1
            fi
            echo -e "${GREEN}dpkg 安装完成${NC}"
        else
            echo -e "${RED}未找到包管理器，无法安装 dpkg。请手动安装 dpkg。${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}dpkg 已存在${NC}"
    fi

    local ASKLINK_URL="https://dl.asklink.com/linux/4.0.33.0/AskLink-4.0.33.0-x86_64.deb"
    local FILENAME="AskLink-4.0.33.0-x86_64.deb"

    echo -e "${CYAN}下载地址: ${ASKLINK_URL}${NC}"
    echo -e "${CYAN}正在下载 ${FILENAME} ...${NC}"

    cd "$TEMP_DIR" || return
    if command -v wget &>/dev/null; then
        wget --show-progress "$ASKLINK_URL" -O "$FILENAME"
    else
        curl -L --fail --progress-bar "$ASKLINK_URL" -o "$FILENAME"
    fi
    if [ $? -ne 0 ] || [ ! -f "$FILENAME" ]; then
        echo -e "${RED}下载失败。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在安装...${NC}"
    sudo dpkg --force-depends -i "$FILENAME" 2>/dev/null

    rm -f "$FILENAME"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}✅ AskLink 安装成功！${NC}"
        local DESKTOP_FILE="$HOME/Desktop/AskLink.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=AskLink
Comment=远程协助工具
Exec=/opt/AskLink/AskLink
Icon=AskLink
Terminal=false
Categories=Network;RemoteAccess;
EOF
        chmod +x "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已创建。${NC}"
    else
        echo -e "${RED}安装失败，请手动检查。${NC}"
        return 1
    fi

    echo -e "${GREEN}AskLink 安装流程结束。${NC}"
}

watt_toolkit_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}═══════安装/更新 Watt Toolkit (Steam++) ═══════${NC}"
    echo ""

    local INSTALL_DIR="$HOME/Watt Toolkit"
    local DESKTOP_DIR="$HOME/Desktop"
    local DOWNLOAD_URL="https://gitee.com/rmbgame/SteamTools/releases/download/3.1.0/Steam%20%20_v3.1.0_linux_x64.tgz"
    local VERSION="3.1.0"

    for cmd in curl sudo unzip tar; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    local installed_version=""
    local has_install=false
    if [ -d "$INSTALL_DIR" ]; then
        has_install=true
        if [ -f "$INSTALL_DIR/.version" ]; then
            installed_version=$(cat "$INSTALL_DIR/.version")
            echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
        else
            echo -e "${YELLOW}检测到已安装目录，但无法读取版本号。${NC}"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 Watt Toolkit。${NC}"
    fi

    if $has_install; then
        if [ -n "$installed_version" ] && [ "$installed_version" = "$VERSION" ]; then
            echo -e "${GREEN}✅ 已是最新版本 ${installed_version}，无需操作。${NC}"
            return 0
        fi
        # 已安装但版本不同或无法读取 → 先询问再下载，避免静默覆盖
        if [ -n "$installed_version" ]; then
            echo -e "${YELLOW}检测到新版本 ${VERSION}（当前已安装: ${installed_version}）。${NC}"
        else
            echo -e "${YELLOW}将重新下载安装版本 ${VERSION}。${NC}"
        fi
        read -n1 -p "按回车键或 A 键继续下载安装，其他键取消: " confirm < /dev/tty
        echo
        if [[ -n "$confirm" && ! "$confirm" =~ [Aa] ]]; then
            echo "取消操作。"
            return 0
        fi
    fi

    echo -e "${GREEN}将安装版本: ${VERSION}${NC}"
    echo "正在下载 ${DOWNLOAD_URL} ..."

    local temp_dir="/tmp/watt_toolkit_install"
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    cd "$temp_dir" || return 1

    local filename="Steam_v${VERSION}_linux_x64.tgz"
    curl -L --progress-bar -o "$filename" "$DOWNLOAD_URL"
    if [ $? -ne 0 ] || [ ! -f "$filename" ]; then
        echo -e "${RED}下载失败，请检查网络后重试。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在解压...${NC}"
    local temp_extract="$temp_dir/extracted"
    mkdir -p "$temp_extract"
    if ! tar -xzf "$filename" -C "$temp_extract"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$temp_dir"
        return 1
    fi

    local content_count=$(ls -1 "$temp_extract" | wc -l)
    local first_item=$(ls -1 "$temp_extract" | head -1)

    if [ -d "$INSTALL_DIR" ]; then
        echo "检测到旧安装目录，正在删除..."
        rm -rf "$INSTALL_DIR"
    fi
    mkdir -p "$INSTALL_DIR"

    if [ $content_count -eq 1 ] && [ -d "$temp_extract/$first_item" ]; then
        echo -e "${CYAN}检测到顶层目录，移动内容到 $INSTALL_DIR ...${NC}"
        shopt -s dotglob
        mv "$temp_extract/$first_item"/* "$INSTALL_DIR/"
        shopt -u dotglob
        find "$temp_extract/$first_item" -maxdepth 1 -name ".*" ! -name "." ! -name ".." -exec mv {} "$INSTALL_DIR/" \;
        rm -rf "$temp_extract/$first_item"
    else
        echo -e "${CYAN}移动所有内容到 $INSTALL_DIR ...${NC}"
        shopt -s dotglob
        mv "$temp_extract"/* "$INSTALL_DIR/"
        shopt -u dotglob
        find "$temp_extract" -maxdepth 1 -name ".*" ! -name "." ! -name ".." -exec mv {} "$INSTALL_DIR/" \;
    fi

    rm -rf "$temp_dir"


    echo "$VERSION" > "$INSTALL_DIR/.version"

    local desktop_file="$DESKTOP_DIR/Watt_Toolkit.desktop"
    local dotnet_root="$INSTALL_DIR/dotnet"
    local dll_path="$INSTALL_DIR/assemblies/Steam++.dll"
    local icon_path="$INSTALL_DIR/Icons/Watt-Toolkit.png"

    if [ ! -f "$dll_path" ] || [ ! -f "$dotnet_root/dotnet" ]; then
        echo -e "${RED}错误: 关键文件缺失，安装可能不完整。${NC}"
        echo "请检查 $INSTALL_DIR 目录内容。"
        return 1
    fi

    cat > "$desktop_file" << EOF
[Desktop Entry]
Categories=Network;Game;
Comment[zh_CN]=Steam 工具箱
Comment=Steam 工具箱
Exec=env 'DOTNET_ROOT=${dotnet_root}' '${dotnet_root}/dotnet' '${dll_path}'
GenericName[zh_CN]=
GenericName=
Icon=${icon_path}
MimeType=
Name[zh_CN]=Watt Toolkit (Steam++)
Name=Watt Toolkit (Steam++)
Path=
StartupNotify=true
Terminal=false
TerminalOptions=
Type=Application
X-KDE-SubstituteUID=false
X-KDE-Username=
EOF
    chmod +x "$desktop_file"
    echo -e "${GREEN}✓ 桌面快捷方式已创建: ${desktop_file}${NC}"

    echo ""
    echo -e "${GREEN}✅ Watt Toolkit ${VERSION} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${INSTALL_DIR}${NC}"
    echo ""
    echo -e "${YELLOW}使用提示：${NC}"
    echo "如果加速报错，请按照下面步骤操作："
    echo "  网络加速 → 加速设置 → 安装证书"
    echo ""
    echo "请在桌面启动 Watt Toolkit。"
}

watt_toolkit_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}══════════════ 卸载 Watt Toolkit ══════════════${NC}"
    local INSTALL_DIR="$HOME/Watt Toolkit"
    local DESKTOP_DIR="$HOME/Desktop"

    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}未检测到已安装的 Watt Toolkit。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在卸载 Watt Toolkit...${NC}"
    echo "将删除以下目录: ${INSTALL_DIR}"
    echo "将删除桌面快捷方式: ${DESKTOP_DIR}/Watt_Toolkit.desktop"
    echo ""

    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    if rm -rf "$INSTALL_DIR"; then
        echo -e "${GREEN}✓ 已删除安装目录${NC}"
    else
        echo -e "${RED}✗ 删除安装目录失败${NC}"
    fi

    if rm -f "${DESKTOP_DIR}/Watt_Toolkit.desktop"; then
        echo -e "${GREEN}✓ 已删除桌面快捷方式${NC}"
    else
        echo -e "${RED}✗ 删除桌面快捷方式失败${NC}"
    fi

    echo ""
    echo -e "${GREEN}✅ Watt Toolkit 已卸载完成。${NC}"
}

install_github_plugin() {
    local GITHUB_REPO="$1"
    local PLUGIN_DIR="$2"
    local DISPLAY_NAME="$3"
    local PLUGIN_PATH="$HOME/homebrew/plugins/${PLUGIN_DIR}"
    local VERSION_FILE="$PLUGIN_PATH/package.json"
    local TEMP_DIR="/tmp/${DISPLAY_NAME}_install"
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 ${DISPLAY_NAME} ════════════════${NC}"
    echo ""

    for cmd in curl sudo unzip python3; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
    local releases_json=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases")
    if [ -z "$releases_json" ]; then
        echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
        return 1
    fi
    if ! [[ "$releases_json" == \[* ]]; then
        echo -e "${RED}错误: GitHub API 返回异常（仓库可能没有 Release，或网络被限）。${NC}"
        return 1
    fi

    local versions_info=$(echo "$releases_json" | $PYTHON_CMD -c "
import sys, json
try:
    data = json.load(sys.stdin)
    stable = []
    prerelease = []
    for rel in data:
        tag = rel.get('tag_name', '')
        if tag and rel.get('assets') and any(ch.isdigit() for ch in tag):
            if rel.get('prerelease', False):
                prerelease.append(tag)
            else:
                stable.append(tag)
    print('STABLE:' + ','.join(stable) if stable else 'STABLE:')
    print('PRERELEASE:' + ','.join(prerelease) if prerelease else 'PRERELEASE:')
except:
    print('STABLE:')
    print('PRERELEASE:')
")
    if [ -z "$versions_info" ]; then
        echo -e "${RED}错误: 无法解析版本信息。${NC}"
        return 1
    fi

    local stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
    local prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

    local latest_stable=""
    if [ -n "$stable_list" ]; then
        # GitHub API 按发布时间倒序返回，第一个稳定版即最新
        latest_stable=$(echo "$stable_list" | cut -d, -f1)
    fi

    local latest_prerelease=""
    if [ -n "$prerelease_list" ]; then
        latest_prerelease=$(echo "$prerelease_list" | cut -d, -f1)
    fi

    local local_version=""
    if [ -f "$VERSION_FILE" ]; then
        local_version=$(grep -o '"version": *"[^"]*"' "$VERSION_FILE" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$local_version" ]; then
            local_version="v${local_version}"
            echo -e "${CYAN}当前已安装版本: ${local_version}${NC}"
        else
            echo -e "${YELLOW}已安装但无法读取版本号。${NC}"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 ${DISPLAY_NAME}。${NC}"
    fi

    local options=()
    local labels=()
    local show_prerelease=false
    if [ -n "$latest_prerelease" ]; then
        if [ -z "$latest_stable" ]; then
            show_prerelease=true
        else
            local opt_stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local opt_pre_num=$(echo "$latest_prerelease" | sed 's/^v//')
            local opt_higher=$(printf '%s\n' "$opt_stable_num" "$opt_pre_num" | sort -V | tail -1)
            if [ "$opt_higher" = "$opt_pre_num" ]; then
                show_prerelease=true
            fi
        fi
    fi
    if [ -n "$latest_stable" ]; then
        options+=("$latest_stable")
        labels+=("正式版 $latest_stable")
    fi
    if [ "$show_prerelease" = true ]; then
        options+=("$latest_prerelease")
        labels+=("预发布版 $latest_prerelease")
    fi

    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}错误: 未找到任何版本。${NC}"
        return 1
    fi

    local target_version=""

    if [ -z "$local_version" ]; then
        while true; do
            clear
            echo -e "${YELLOW}════════════════ 安装/更新 ${DISPLAY_NAME} ════════════════${NC}"
            echo ""
            echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
            echo -e "${YELLOW}未检测到已安装的 ${DISPLAY_NAME}。${NC}"
            echo ""
            if [ ${#options[@]} -eq 1 ]; then
                target_version="${options[0]}"
                echo -e "${GREEN}将安装唯一版本: ${target_version}${NC}"
                break
            else
                echo "请选择要安装的版本："
                for i in "${!options[@]}"; do
                    echo "$((i+1))) ${labels[$i]}"
                done
                read -p "请输入选择 [1-${#options[@]}]: " choice < /dev/tty
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#options[@]} ]; then
                    target_version="${options[$((choice-1))]}"
                    break
                else
                    echo -e "${RED}无效选择，请重新输入。${NC}"
                    sleep 1
                fi
            fi
        done
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
    else
        local is_prerelease=false
        if [ -n "$prerelease_list" ]; then
            local inst_ver_clean=$(echo "$local_version" | sed 's/^v//')
            for tag in $(echo "$prerelease_list" | tr ',' '\n'); do
                local tag_clean=$(echo "$tag" | sed 's/^v//')
                if [ "$tag_clean" = "$inst_ver_clean" ]; then
                    is_prerelease=true
                    break
                fi
            done
        fi

        if [ "$is_prerelease" = true ]; then
            local new_prerelease=""
            if [ -n "$latest_prerelease" ]; then
                local local_clean=$(echo "$local_version" | sed 's/^v//')
                local pre_clean=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher_pre=$(printf '%s\n' "$local_clean" "$pre_clean" | sort -V | tail -1)
                if [ "$higher_pre" = "$pre_clean" ] && [ "$local_clean" != "$pre_clean" ]; then
                    new_prerelease="$latest_prerelease"
                fi
            fi

            if [ -n "$new_prerelease" ]; then
                echo -e "${YELLOW}当前已安装预发布版 ${local_version}。${NC}"
                echo -e "${YELLOW}检测到更新：预发布版 ${new_prerelease}。${NC}"
                echo "请选择操作："
                echo "1) 更新到最新预发布版 ${new_prerelease}"
                if [ -n "$latest_stable" ]; then
                    echo "2) 切换到正式版 ${latest_stable}"
                    echo "3) 保持当前版本"
                else
                    echo "2) 保持当前版本"
                fi
                while true; do
                    read -p "请输入选择: " choice < /dev/tty
                    if [ "$choice" = "1" ]; then
                        target_version="$new_prerelease"
                        echo -e "${GREEN}将更新至预发布版: ${target_version}${NC}"
                        break
                    elif [ "$choice" = "2" ]; then
                        if [ -n "$latest_stable" ]; then
                            target_version="$latest_stable"
                            echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
                            break
                        else
                            echo "保持当前版本。"
                            return 0
                        fi
                    elif [ -n "$latest_stable" ] && [ "$choice" = "3" ]; then
                        echo "保持当前版本。"
                        return 0
                    else
                        echo -e "${RED}无效选择，请重新输入。${NC}"
                    fi
                done
            elif [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}当前已安装预发布版 ${local_version}。${NC}"
                echo -e "${YELLOW}是否切换为正式版 ${latest_stable}？${NC}"
                read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice < /dev/tty
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新预发布版 ${local_version}，且没有正式版可切换。${NC}"
                return 0
            fi
        else
            # 先比较本地与最新正式版（无预发布时也必须检测正式版更新）
            local stable_num=$(echo "$local_version" | sed 's/^v//')
            local latest_stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local higher_stable=$(printf '%s\n' "$stable_num" "$latest_stable_num" | sort -V | tail -1)
            if [ -n "$latest_stable" ] && [ "$higher_stable" = "$latest_stable_num" ] && [ "$stable_num" != "$latest_stable_num" ]; then
                echo -e "${YELLOW}检测到新版本：正式版 ${latest_stable}（当前 ${local_version}）。${NC}"
                read -n1 -p "按回车键或 A 键更新，其他键保持: " up_choice < /dev/tty
                echo
                if [[ -z "$up_choice" || "$up_choice" == "a" || "$up_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}将更新至: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            elif [ -n "$latest_prerelease" ]; then
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
                if [ "$higher" = "$prerelease_num" ]; then
                    echo -e "${YELLOW}当前已安装正式版 ${local_version}。${NC}"
                    echo -e "${YELLOW}发现更高或相等的预发布版 ${latest_prerelease}，是否切换？${NC}"
                    read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice < /dev/tty
                    echo
                    if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                        target_version="$latest_prerelease"
                        echo -e "${GREEN}将切换至预发布版: ${target_version}${NC}"
                    else
                        echo "保持当前版本。"
                        return 0
                    fi
                else
                    echo -e "${GREEN}已是最新正式版 ${local_version}，且没有更高的预发布版。${NC}"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新正式版 ${local_version}，且没有预发布版。${NC}"
                return 0
            fi
        fi
    fi

    if [ -z "$target_version" ]; then
        echo -e "${RED}错误: 未确定目标版本。${NC}"
        return 1
    fi

    local download_url=$(echo "$releases_json" | $PYTHON_CMD -c "
import sys, json
try:
    data = json.load(sys.stdin)
    def norm(t):
        t = str(t).strip()
        while t[:1] in 'vV':
            t = t[1:]
        return t
    target_tag = norm('$target_version')
    plugin_dir = norm('$PLUGIN_DIR').lower()
    display = norm('$DISPLAY_NAME').lower()
    def is_source(name):
        n = name.lower()
        return any(k in n for k in ('source', 'yuanma', 'src', '\u6e90\u7801'))
    def pick(assets):
        # 1. 优先选名称含插件目录名且非源码包的
        for a in assets:
            n = a.get('name', '')
            if plugin_dir in n.lower() and not is_source(n):
                return a
        # 2. 其次选名称含显示名的
        for a in assets:
            n = a.get('name', '')
            if display in n.lower() and not is_source(n):
                return a
        # 3. 再其次选任意非源码 .zip
        for a in assets:
            n = a.get('name', '')
            if n.endswith('.zip') and not is_source(n):
                return a
        # 4. 退路：第一个 .zip
        for a in assets:
            if a.get('name', '').endswith('.zip'):
                return a
        return None
    for rel in data:
        if norm(rel.get('tag_name', '')) == target_tag:
            asset = pick(rel.get('assets', []))
            if asset:
                print(asset.get('browser_download_url', ''))
            break
except:
    pass
")
    if [ -z "$download_url" ]; then
        echo -e "${RED}错误: 无法获取 ${target_version} 的下载链接。${NC}"
        return 1
    fi

    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return

    local zip_filename="${DISPLAY_NAME}.zip"

    if ! download_zip_with_mirrors "$download_url" "$zip_filename" "${DISPLAY_NAME} ${target_version}"; then
        echo -e "${RED}下载失败，安装中止。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在解压并安装到 ${PLUGIN_PATH}...${NC}"

    local EXTRACT_DIR="$TEMP_DIR/extract"
    mkdir -p "$EXTRACT_DIR"

    if ! sudo unzip -q "$zip_filename" -d "$EXTRACT_DIR"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$TEMP_DIR"
        return 1
    fi

    local extracted_dir=""
    extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 2 -type f -name "package.json" -exec dirname {} \; | head -1)
    if [ -z "$extracted_dir" ]; then
        extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 2 -type f -name "tomoon" -exec dirname {} \; | head -1)
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 1 -type d ! -path "$EXTRACT_DIR" | head -1)
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir="$EXTRACT_DIR"
    fi

    sudo rm -rf "$PLUGIN_PATH"
    sudo mkdir -p "$HOME/homebrew/plugins"
    sudo mv "$extracted_dir" "$PLUGIN_PATH"
    sudo chown -R "${CURRENT_USER}:${CURRENT_GROUP}" "$PLUGIN_PATH"

    rm -rf "$TEMP_DIR"

    echo -e "${GREEN}✅ ${DISPLAY_NAME} 插件 ${target_version} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${PLUGIN_PATH}${NC}"
}

install_decky_lsfg_vk_install() { install_github_plugin "xXJSONDeruloXx/decky-lsfg-vk" "Decky-LSFG-VK" "LSFG-VK"; }
install_decky_framegen_install() { install_github_plugin "xXJSONDeruloXx/Decky-Framegen" "Decky-Framegen" "Framegen"; }
install_tomoon_install() { install_github_plugin "YukiCoco/ToMoon" "tomoon" "ToMoon"; }
install_freedeck_install() { install_github_plugin "panyiwei-home/Freedeck" "Freedeck" "Freedeck"; }

uninstall_plugin_generic() {
    local plugin_dir="$1" display_name="$2"
    local plugin_path="$HOME/homebrew/plugins/${plugin_dir}"
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 卸载 ${display_name} ════════════════${NC}"
    [ -d "$plugin_path" ] || { echo -e "${YELLOW}未检测到已安装的 ${display_name}。${NC}"; return 0; }
    confirm_action || { echo "取消卸载。"; return 0; }
    sudo rm -rf "$plugin_path"
    # 删除结果要以目录是否真的消失为准，不能无条件报成功
    if [ -d "$plugin_path" ]; then
        echo -e "${RED}✗ ${display_name} 卸载失败，目录仍存在: $plugin_path${NC}"
        echo -e "${YELLOW}  请手动删除：sudo rm -rf \"$plugin_path\"${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ ${display_name} 已卸载。${NC}"
}
install_tomoon_uninstall() { uninstall_plugin_generic "tomoon" "ToMoon"; }
install_freedeck_uninstall() { uninstall_plugin_generic "Freedeck" "Freedeck"; }
install_decky_lsfg_vk_uninstall() { uninstall_plugin_generic "Decky-LSFG-VK" "LSFG-VK"; }
install_decky_framegen_uninstall() { uninstall_plugin_generic "Decky-Framegen" "Framegen"; }

install_plugin_store() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 插件商店 (Decky Loader) ════════════════${NC}"
    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"

    local releases_json=$(curl -s "https://api.github.com/repos/SteamDeckHomebrew/decky-loader/releases")
    if [ -z "$releases_json" ]; then
        echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
        return 1
    fi
    if ! [[ "$releases_json" == \[* ]]; then
        echo -e "${RED}错误: GitHub API 返回异常（仓库可能没有 Release，或网络被限）。${NC}"
        return 1
    fi

    local versions_info=$(echo "$releases_json" | $PYTHON_CMD -c "
import sys, json
try:
    data = json.load(sys.stdin)
    stable = []
    prerelease = []
    for rel in data:
        tag = rel.get('tag_name', '')
        if tag and rel.get('assets') and any(ch.isdigit() for ch in tag):
            if rel.get('prerelease', False):
                prerelease.append(tag)
            else:
                stable.append(tag)
    print('STABLE:' + ','.join(stable) if stable else 'STABLE:')
    print('PRERELEASE:' + ','.join(prerelease) if prerelease else 'PRERELEASE:')
except:
    print('STABLE:')
    print('PRERELEASE:')
")
    if [ -z "$versions_info" ]; then
        echo -e "${RED}错误: 无法解析版本信息。${NC}"
        return 1
    fi

    local stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
    local prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

    local latest_stable=""
    if [ -n "$stable_list" ]; then
        # GitHub API 按发布时间倒序返回，第一个稳定版即最新
        latest_stable=$(echo "$stable_list" | cut -d, -f1)
    fi

    local latest_prerelease=""
    if [ -n "$prerelease_list" ]; then
        latest_prerelease=$(echo "$prerelease_list" | cut -d, -f1)
    fi

    local PLUGIN_LOADER="$HOME/homebrew/services/PluginLoader"
    local installed_version=""
    if [[ -f "$PLUGIN_LOADER" && -x "$PLUGIN_LOADER" ]]; then
        installed_version=$(sudo journalctl -u plugin_loader --no-pager 2>/dev/null | grep -i "Starting Decky version" | tail -1 | grep -oP 'version v?\K[0-9.]+(-pre[0-9]+)?')
        if [[ -z "$installed_version" ]]; then
            installed_version=$("$PLUGIN_LOADER" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+(-pre\d+)?')
        fi
        if [[ -n "$installed_version" ]]; then
            installed_version="v${installed_version}"
            echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
        else
            echo -e "${YELLOW}已安装但无法获取版本。${NC}"
        fi
    else
        echo "未检测到现有安装。"
    fi

    local options=()
    local labels=()
    local show_prerelease=false
    if [ -n "$latest_prerelease" ]; then
        if [ -z "$latest_stable" ]; then
            show_prerelease=true
        else
            local opt_stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local opt_pre_num=$(echo "$latest_prerelease" | sed 's/^v//')
            local opt_higher=$(printf '%s\n' "$opt_stable_num" "$opt_pre_num" | sort -V | tail -1)
            if [ "$opt_higher" = "$opt_pre_num" ]; then
                show_prerelease=true
            fi
        fi
    fi
    if [ -n "$latest_stable" ]; then
        options+=("$latest_stable")
        labels+=("正式版 $latest_stable")
    fi
    if [ "$show_prerelease" = true ]; then
        options+=("$latest_prerelease")
        labels+=("预发布版 $latest_prerelease")
    fi

    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}错误: 未找到任何版本。${NC}"
        return 1
    fi

    local target_version=""

    if [ -z "$installed_version" ]; then
        while true; do
            clear
            echo -e "${YELLOW}════════════════ 安装/更新 插件商店 ════════════════${NC}"
            echo ""
            echo -e "${YELLOW}未检测到现有安装。${NC}"
            echo ""
            if [ ${#options[@]} -eq 1 ]; then
                target_version="${options[0]}"
                echo -e "${GREEN}将安装唯一版本: ${target_version}${NC}"
                break
            else
                echo "请选择要安装的版本："
                for i in "${!options[@]}"; do
                    echo "$((i+1))) ${labels[$i]}"
                done
                read -p "请输入选择 [1-${#options[@]}]: " choice < /dev/tty
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#options[@]} ]; then
                    target_version="${options[$((choice-1))]}"
                    break
                else
                    echo -e "${RED}无效选择，请重新输入。${NC}"
                    sleep 1
                fi
            fi
        done
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
    else
        local is_prerelease=false
        if [ -n "$prerelease_list" ]; then
            local inst_ver_clean=$(echo "$installed_version" | sed 's/^v//')
            for tag in $(echo "$prerelease_list" | tr ',' '\n'); do
                local tag_clean=$(echo "$tag" | sed 's/^v//')
                if [ "$tag_clean" = "$inst_ver_clean" ]; then
                    is_prerelease=true
                    break
                fi
            done
        fi

        if [ "$is_prerelease" = true ]; then
            local new_prerelease=""
            if [ -n "$latest_prerelease" ]; then
                local local_clean=$(echo "$installed_version" | sed 's/^v//')
                local pre_clean=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher_pre=$(printf '%s\n' "$local_clean" "$pre_clean" | sort -V | tail -1)
                if [ "$higher_pre" = "$pre_clean" ] && [ "$local_clean" != "$pre_clean" ]; then
                    new_prerelease="$latest_prerelease"
                fi
            fi

            if [ -n "$new_prerelease" ]; then
                echo -e "${YELLOW}当前已安装预发布版 ${installed_version}。${NC}"
                echo -e "${YELLOW}检测到更新：预发布版 ${new_prerelease}。${NC}"
                echo "请选择操作："
                echo "1) 更新到最新预发布版 ${new_prerelease}"
                if [ -n "$latest_stable" ]; then
                    echo "2) 切换到正式版 ${latest_stable}"
                    echo "3) 保持当前版本"
                else
                    echo "2) 保持当前版本"
                fi
                while true; do
                    read -p "请输入选择: " choice < /dev/tty
                    if [ "$choice" = "1" ]; then
                        target_version="$new_prerelease"
                        echo -e "${GREEN}将更新至预发布版: ${target_version}${NC}"
                        break
                    elif [ "$choice" = "2" ]; then
                        if [ -n "$latest_stable" ]; then
                            target_version="$latest_stable"
                            echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
                            break
                        else
                            echo "保持当前版本。"
                            return 0
                        fi
                    elif [ -n "$latest_stable" ] && [ "$choice" = "3" ]; then
                        echo "保持当前版本。"
                        return 0
                    else
                        echo -e "${RED}无效选择，请重新输入。${NC}"
                    fi
                done
            elif [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}当前已安装预发布版 ${installed_version}。${NC}"
                echo -e "${YELLOW}是否切换为正式版 ${latest_stable}？${NC}"
                read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice < /dev/tty
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新预发布版 ${installed_version}，且没有正式版可切换。${NC}"
                return 0
            fi
        else
            # 先比较本地与最新正式版（无预发布时也必须检测正式版更新）
            local stable_num=$(echo "$installed_version" | sed 's/^v//')
            local latest_stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local higher_stable=$(printf '%s\n' "$stable_num" "$latest_stable_num" | sort -V | tail -1)
            if [ -n "$latest_stable" ] && [ "$higher_stable" = "$latest_stable_num" ] && [ "$stable_num" != "$latest_stable_num" ]; then
                echo -e "${YELLOW}检测到新版本：正式版 ${latest_stable}（当前 ${installed_version}）。${NC}"
                read -n1 -p "按回车键或 A 键更新，其他键保持: " up_choice < /dev/tty
                echo
                if [[ -z "$up_choice" || "$up_choice" == "a" || "$up_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}将更新至: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            elif [ -n "$latest_prerelease" ]; then
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
                if [ "$higher" = "$prerelease_num" ]; then
                    echo -e "${YELLOW}当前已安装正式版 ${installed_version}。${NC}"
                    echo -e "${YELLOW}发现更高或相等的预发布版 ${latest_prerelease}，是否切换？${NC}"
                    read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice < /dev/tty
                    echo
                    if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                        target_version="$latest_prerelease"
                        echo -e "${GREEN}将切换至预发布版: ${target_version}${NC}"
                    else
                        echo "保持当前版本。"
                        return 0
                    fi
                else
                    echo -e "${GREEN}已是最新正式版 ${installed_version}，且没有更高的预发布版。${NC}"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新正式版 ${installed_version}，且没有预发布版。${NC}"
                return 0
            fi
        fi
    fi

    if [ -z "$target_version" ]; then
        echo -e "${RED}错误: 未确定目标版本。${NC}"
        return 1
    fi

    HOME_DIR="$HOME"
    HOMEBREW_DIR="${HOME_DIR}/homebrew"
    SERVICE_DIR="${HOMEBREW_DIR}/services"
    PLUGIN_DIR="${HOMEBREW_DIR}/plugins"
    PLUGIN_LOADER="${SERVICE_DIR}/PluginLoader"
    SERVICE_FILE="${SERVICE_DIR}/plugin_loader.service"
    SERVICE_DEST="/etc/systemd/system/plugin_loader.service"
    CURRENT_USER=$(whoami)

    DOWNLOAD_URL="https://github.com/SteamDeckHomebrew/decky-loader/releases/download/${target_version}/PluginLoader"
    TMP_FILE="${PLUGIN_LOADER}.tmp"

    mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR"
    sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "$HOMEBREW_DIR" 2>/dev/null || true

    echo -e "${CYAN}正在下载 PluginLoader...${NC}"
    if ! download_with_mirrors "$DOWNLOAD_URL" "$TMP_FILE" "PluginLoader"; then
        echo -e "${RED}下载失败，安装中止。${NC}"
        return 1
    fi

    FILE_SIZE=$(stat -c%s "$TMP_FILE" 2>/dev/null || stat -f%z "$TMP_FILE" 2>/dev/null)
    if [[ -z "$FILE_SIZE" || "$FILE_SIZE" -lt 1000000 ]]; then
        echo -e "${RED}下载文件无效 (大小: ${FILE_SIZE:-0} 字节)。${NC}"
        rm -f "$TMP_FILE"
        return 1
    fi
    echo -e "\n${GREEN}下载成功 (大小: $((FILE_SIZE/1024/1024)) MB)${NC}"

    for cmd in curl "$PYTHON_CMD" systemctl sudo journalctl stat; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            rm -f "$TMP_FILE"
            return 1
        fi
    done

    if [[ -f "$PLUGIN_LOADER" ]]; then
        sudo rm -f "$PLUGIN_LOADER"
    fi
    mv "$TMP_FILE" "$PLUGIN_LOADER"
    chmod +x "$PLUGIN_LOADER"

    touch "${HOME_DIR}/.steam/steam/.cef-enable-remote-debugging"
    if [[ -d "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/" ]]; then
        touch "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/.cef-enable-remote-debugging"
    fi

    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=SteamDeck Plugin Loader
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=deck
Environment="HOMEBREW_FOLDER=${HOMEBREW_DIR}"
ExecStart=${PLUGIN_LOADER}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo cp "$SERVICE_FILE" "$SERVICE_DEST"
    sudo systemctl daemon-reload
    sudo systemctl enable plugin_loader
    sudo systemctl restart plugin_loader

    echo ""
    echo -e "${GREEN}✅ Decky Loader ${target_version} 安装/更新完成！${NC}"
    echo "请切换回游戏模式，按 '...' 键打开侧边栏检查。"
}

uninstall_plugin_store() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载插件商店 ════════════════${NC}"
    if [ ! -d "$HOME/homebrew" ]; then
        echo -e "${YELLOW}未检测到已安装的插件商店。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到已安装插件商店。${NC}"
    echo "警告：这将删除整个 $HOME/homebrew 目录，包括所有插件。"
    echo ""
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    echo "正在执行卸载..."
    sudo rm -rf "$HOME/homebrew"
    # 以目录是否真的消失为准（rm 在部分失败时也可能返回 0）
    if [ -d "$HOME/homebrew" ]; then
        echo -e "${RED}✗ 插件商店卸载失败，目录仍存在: $HOME/homebrew${NC}"
        echo -e "${YELLOW}  请手动删除：sudo rm -rf \"$HOME/homebrew\"${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ 插件商店卸载完成${NC}"
    echo "如需重新安装，请使用 '安装插件商店' 功能。"
}

get_ge_proton_versions() {
    curl -s "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases?per_page=100" | \
        python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tags = []
    for rel in data:
        tag = rel.get('tag_name', '')
        if tag.startswith('GE-Proton'):
            tags.append(tag)
    print('\n'.join(tags))
except:
    pass
"
}

get_installed_ge_proton() {
    local install_dir="$HOME/.local/share/Steam/compatibilitytools.d"
    [ -d "$install_dir" ] || return
    for dir in "$install_dir"/GE-Proton*; do
        [ -d "$dir" ] && basename "$dir"
    done
}

ge_proton_manager() {
    while true; do
        local choice=$(zenity --list --radiolist \
            --title="GE-Proton 兼容层管理" \
            --text="请选择要执行的操作" \
            --column="选择" --column="操作" \
            FALSE "安装 GE-Proton" \
            FALSE "卸载 GE-Proton" \
            --width=400 --height=200 2>/dev/null)
        [ $? -eq 1 ] && return 0
        case "$choice" in
            "安装 GE-Proton") ge_proton_install ;;
            "卸载 GE-Proton") ge_proton_uninstall ;;
            *) return 0 ;;
        esac
    done
}

ge_proton_install() {
    (
        echo "10"; echo "# 正在获取版本列表，请稍候..."
        sleep 0.5
        echo "50"; echo "# 正在连接 GitHub API..."
        sleep 0.5
        echo "100"
    ) | zenity --progress --pulsate --title="加载中" --text="正在获取版本列表..." --width=400 2>/dev/null &
    ZENITY_PID=$!

    local all_versions=$(get_ge_proton_versions)

    kill $ZENITY_PID 2>/dev/null
    wait $ZENITY_PID 2>/dev/null

    [ -z "$all_versions" ] && {
        zenity --error --text="无法获取版本列表，请检查网络。" --width=400 2>/dev/null
        return 1
    }
    mapfile -t version_array <<< "$all_versions"

    local installed_list=$(get_installed_ge_proton)
    local installed_array=()
    [ -n "$installed_list" ] && mapfile -t installed_array <<< "$installed_list"

    local available_versions=()
    for ver in "${version_array[@]}"; do
        local already=false
        for inst in "${installed_array[@]}"; do
            [ "$ver" = "$inst" ] && { already=true; break; }
        done
        [ "$already" = false ] && available_versions+=("$ver")
    done

    [ ${#available_versions[@]} -eq 0 ] && {
        zenity --info --text="所有 GE-Proton 版本已安装！" --width=400 2>/dev/null
        return 0
    }

    local list_args=(
        --list --checklist
        --title="安装 GE-Proton 兼容层"
        --text="请选择要安装的版本（可多选）\n共 ${#available_versions[@]} 个版本可用，已排除已安装版本"
        --column="选择" --column="版本"
        --width=600 --height=500
        --ok-label="安装"
        --cancel-label="返回"
    )
    for ver in "${available_versions[@]}"; do
        list_args+=("FALSE" "$ver")
    done

    local selection
    selection=$(zenity "${list_args[@]}" 2>/dev/null)
    local ret=$?

    if [ $ret -eq 1 ] || [ $ret -eq -1 ]; then
        return 0
    elif [ $ret -eq 0 ]; then
        [ -z "$selection" ] && {
            zenity --warning --text="请至少选择一个版本。" --width=300 2>/dev/null
            return 0
        }
        IFS='|' read -r -a selected <<< "$selection"
        ge_proton_do_install "${selected[@]}"
    fi
}

ge_proton_do_install() {
    local versions=("$@")
    local total=${#versions[@]}
    local install_dir="$HOME/.local/share/Steam/compatibilitytools.d"
    mkdir -p "$install_dir"

    local success_count=0
    local failed_count=0
    local failed_list=""

    local mirror_choice=$(zenity --list --radiolist \
        --title="选择下载镜像源" \
        --text="所有版本将使用同一镜像源" \
        --column="选择" --column="镜像源" \
        FALSE "gh-proxy.com (国内镜像，速度快)" \
        FALSE "gh.3w.pm (国内镜像，稳定)" \
        FALSE "cors.isteed.cc (国内镜像，稳定)" \
        FALSE "ghproxy.net (国内镜像，慢速备用)" \
        FALSE "GitHub (官方源)" \
        --width=560 --height=280 2>/dev/null)
    [ -z "$mirror_choice" ] && return 0

    local mirror=""
    case "$mirror_choice" in
        "gh-proxy.com (国内镜像，速度快)") mirror="https://gh-proxy.com/" ;;
        "gh.3w.pm (国内镜像，稳定)") mirror="https://gh.3w.pm/" ;;
        "cors.isteed.cc (国内镜像，稳定)") mirror="https://cors.isteed.cc/" ;;
        "ghproxy.net (国内镜像，慢速备用)") mirror="https://ghproxy.net/" ;;
        # 官方源用空前缀：download_url 本身已是完整的 https://github.com/... 地址，
        # 若这里也写 https://github.com/ 会拼成 .../https://github.com/... 导致 404
        "GitHub (官方源)") mirror="" ;;
    esac

    local pipe="/tmp/zenity_pipe_$$"
    mkfifo "$pipe"
    zenity --progress --pulsate --title="安装 GE-Proton" --text="准备开始..." --width=500 < "$pipe" &
    local zenity_pid=$!
    exec 3> "$pipe"

    for i in "${!versions[@]}"; do
        if ! kill -0 $zenity_pid 2>/dev/null; then
            echo "用户取消安装" >&2
            break
        fi

        local version="${versions[$i]}"
        local idx=$((i+1))
        echo "# 正在处理第 $idx/$total 个: $version (准备下载...)" >&3

        local download_url=$(curl -s "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/tags/${version}" | \
            python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for asset in data.get('assets', []):
        name = asset.get('name', '')
        if name.endswith('.tar.gz') and 'aarch64' not in name:
            print(asset.get('browser_download_url', ''))
            break
except:
    pass
")
        if [ -z "$download_url" ]; then
            echo "# 错误：无法获取 $version 的下载链接，跳过" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (无法获取下载链接)"
            continue
        fi

        local full_url="${mirror}${download_url}"
        local temp_dir="/tmp/ge_proton_$$"
        mkdir -p "$temp_dir"
        cd "$temp_dir" || continue
        local filename="${version}.tar.gz"

        echo "# 正在处理第 $idx/$total 个: $version (下载中...)" >&3
        curl -L -f -S --connect-timeout 30 --max-time 600 -o "$filename" "$full_url" 2> /tmp/curl_err_$$.log
        local curl_ret=$?
        if [ $curl_ret -ne 0 ]; then
            echo "# 下载失败，错误信息：" >&3
            tail -n 5 /tmp/curl_err_$$.log >&3
            rm -f /tmp/curl_err_$$.log
            rm -f "$filename"
            cd /tmp && rm -rf "$temp_dir"
            ((failed_count++))
            failed_list="${failed_list}\n  $version (下载失败)"
            continue
        fi
        rm -f /tmp/curl_err_$$.log

        # 先解压到临时目录校验完整性，成功后再移入 compatibilitytools.d。
        # 直接解到 install_dir 的问题是：下载包被截断/损坏时，tar 会留下
        # 半套目录，而 Steam 会把这个残缺版本当成可用的兼容层加载。
        echo "# 正在处理第 $idx/$total 个: $version (解压中...)" >&3
        local STAGE_DIR
        STAGE_DIR=$(mktemp -d "$install_dir/.stage.XXXXXX" 2>/dev/null) || STAGE_DIR=""
        if [ -z "$STAGE_DIR" ]; then
            echo "# 第 $idx/$total 个: $version 安装失败（无法创建临时目录）" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (无法创建临时目录)"
            rm -f "$filename"
            cd /tmp && rm -rf "$temp_dir"
            continue
        fi
        tar -xzf "$filename" -C "$STAGE_DIR"
        local tar_ret=$?

        rm -f "$filename"
        cd /tmp && rm -rf "$temp_dir"

        if [ $tar_ret -ne 0 ] || [ ! -d "$STAGE_DIR/$version" ]; then
            # 解压失败：清掉半成品，绝不留到 compatibilitytools.d
            rm -rf "$STAGE_DIR"
            echo "# 第 $idx/$total 个: $version 安装失败（压缩包损坏或解压中断）" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (解压失败)"
            continue
        fi

        # 解压成功：删旧版本目录后原子移入，避免残留上一次的混合内容
        rm -rf "${install_dir:?}/$version"
        if ! mv "$STAGE_DIR/$version" "$install_dir/$version"; then
            rm -rf "$STAGE_DIR"
            echo "# 第 $idx/$total 个: $version 安装失败（移动到目标目录失败）" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (移动失败)"
            continue
        fi
        rm -rf "$STAGE_DIR"

        if [ -d "$install_dir/$version" ]; then
            echo "# 第 $idx/$total 个: $version 安装成功" >&3
            ((success_count++))
        else
            echo "# 第 $idx/$total 个: $version 安装失败" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (安装校验失败)"
        fi
    done

    if kill -0 $zenity_pid 2>/dev/null; then
        local result_msg="\n========== 安装完成 ==========\n成功: $success_count 个"
        if [ $failed_count -gt 0 ]; then
            result_msg+="\n失败: $failed_count 个\n失败的版本:${failed_list}"
        fi
        if [ $success_count -gt 0 ]; then
            result_msg+="\n\n建议重启 Steam 以刷新兼容层列表。"
        fi
        echo "# $result_msg" >&3
        exec 3>&-
        wait $zenity_pid 2>/dev/null
    fi

    rm -f "$pipe"
}

ge_proton_uninstall() {
    local installed_list=$(get_installed_ge_proton)
    [ -z "$installed_list" ] && {
        zenity --info --text="未检测到已安装的 GE-Proton。" --ok-label="返回" --width=400 2>/dev/null
        return 0
    }
    mapfile -t installed_array <<< "$installed_list"

    local list_args=(
        --list --checklist
        --title="卸载 GE-Proton 兼容层"
        --text="请选择要卸载的版本（可多选）"
        --column="选择" --column="版本"
        --width=500 --height=350
        --ok-label="卸载"
        --cancel-label="返回"
    )
    for ver in "${installed_array[@]}"; do
        list_args+=("FALSE" "$ver")
    done

    local selection=$(zenity "${list_args[@]}" 2>/dev/null)
    [ -z "$selection" ] && return 0
    IFS='|' read -r -a selected <<< "$selection"

    local install_dir="$HOME/.local/share/Steam/compatibilitytools.d"
    local total=${#selected[@]}
    local success=0 fail=0
    local failed_list=""

    local pipe="/tmp/zenity_pipe_$$"
    mkfifo "$pipe"
    zenity --progress --pulsate --title="卸载 GE-Proton" --text="准备开始..." --width=500 < "$pipe" &
    local zenity_pid=$!
    exec 3> "$pipe"

    for i in "${!selected[@]}"; do
        if ! kill -0 $zenity_pid 2>/dev/null; then
            echo "用户取消卸载" >&2
            break
        fi

        local version="${selected[$i]}"
        local idx=$((i+1))

        echo "# 正在处理第 $idx/$total 个: $version ..." >&3

        if [ -d "$install_dir/$version" ]; then
            rm -rf "$install_dir/$version"
            if [ ! -d "$install_dir/$version" ]; then
                ((success++))
                echo "# 第 $idx/$total 个: $version 已卸载" >&3
            else
                ((fail++))
                failed_list="${failed_list}\n  $version (删除失败)"
                echo "# 第 $idx/$total 个: $version 卸载失败" >&3
            fi
        else
            ((success++))
            echo "# 第 $idx/$total 个: $version (目录不存在，跳过)" >&3
        fi
        sleep 0.3
    done

    if kill -0 $zenity_pid 2>/dev/null; then
        local result_msg="\n========== 卸载完成 ==========\n成功: $success 个"
        if [ $fail -gt 0 ]; then
            result_msg+="\n失败: $fail 个\n失败的版本:${failed_list}"
        fi
        result_msg+="\n\n建议重启 Steam 以使更改生效。"
        echo "# $result_msg" >&3
        exec 3>&-
        wait $zenity_pid 2>/dev/null
    fi

    rm -f "$pipe"
}

clover_install_or_reinstall() {
    clear
    echo -e "${YELLOW}════════════════ 安装/重装 Clover 引导 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}此操作将安装或重新安装 Clover 图形化引导管理器。${NC}"
    echo -e "${YELLOW}重要：请先在 Windows 中进行以下配置（如已有 Windows且初次安装引导）（如果是重装引导则忽略此步骤）：${NC}"
    echo "  1. 以管理员身份打开命令提示符或 PowerShell"
    echo "  2. 执行命令：bcdedit.exe -set \"{globalsettings}\" highestmode on"
    echo "  3. 执行命令：reg add \"HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\TimeZoneInformation\" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f"
    echo ""

    echo "========================================="
    echo "   Steam Deck Clover 安装助手"
    echo "========================================="
    # 注意：这里克隆走的是 git 协议，不是普通 HTTP 下载。
    # 2026-10 实测：gh-proxy.com / cors.isteed.cc / ghproxy.net 都**不支持** git clone
    # （只有 gh.3w.pm 和官方源可用），所以克隆镜像单独列，不套用下载镜像列表。
    echo "请选择克隆镜像源："
    echo "  1) gh.3w.pm        （国内镜像，推荐）"
    echo "  2) GitHub 官方     （国内可能较慢）"
    read -p "请输入数字 [1-2]: " choice < /dev/tty

    case "$choice" in
        1) BASE_URL="https://gh.3w.pm/https://github.com" ;;
        2) BASE_URL="https://github.com" ;;
        *) echo "操作已取消。"; return 0 ;;
    esac

    REPO_FULL_PATH="ryanrudolfoba/SteamDeck-Clover-dualboot"
    REPO_URL="${BASE_URL}/${REPO_FULL_PATH}"
    TARGET_DIR="$HOME/SteamDeck-Clover-dualboot"

    if [ -d "$TARGET_DIR" ]; then
        echo -e "${YELLOW}目录 $TARGET_DIR 已存在。${NC}"
        read -p "是否删除旧文件夹并重新克隆？(y/N): " -n 1 -r < /dev/tty
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$TARGET_DIR"
        else
            echo "操作已取消。"
            read -p "按回车键返回主菜单..." < /dev/tty
            return 0
        fi
    fi

    echo -e "${CYAN}正在克隆仓库...${NC}"
    if ! git clone --progress --depth=1 "$REPO_URL" "$TARGET_DIR" 2>&1 | tee /tmp/clone_log.txt; then
        echo -e "${RED}克隆失败，请检查网络或更换镜像源。${NC}"
        rm -rf "$TARGET_DIR"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    fi

    echo -e "${GREEN}克隆完成。${NC}"
    cd "$TARGET_DIR" || { echo -e "${RED}无法进入目录${NC}"; return 1; }

    echo -e "${CYAN}正在生成优化版 install-Clover.sh...${NC}"
    cat > install-Clover.sh << 'CLOVER_SCRIPT_EOF'
#!/bin/bash
# 失败即中止：原脚本没有 set -e，中间任何一步失败（cp/挂载/efibootmgr）都会继续
# 往下执行，可能在 ESP 上写出半套 Clover，最后还打印“安装完成”。
# 这里加 -euo pipefail，并对“允许失败”的命令（grep 探测、efibootmgr -B、umount）
# 显式写 `|| true` 或放进 if 里，见下方逐处注释。
set -euo pipefail

clear

echo "Clover 双系统启动安装脚本 - Steam Deck 专用"
echo "项目地址: https://github.com/ryanrudolfoba/SteamDeck-Clover-dualboot"
echo "作者 YT: 10MinuteSteamDeckGamer"
echo "正在进行初步检查..."

CLOVER=$(efibootmgr | grep -i Clover | colrm 9 | colrm 1 4 || true)
REFIND=$(efibootmgr | grep -i rEFInd | colrm 9 | colrm 1 4 || true)

# 动态识别 ESP，替代硬编码 /dev/nvme0n1p1：
#   Steam Deck 有 NVMe / eMMC(/dev/mmcblk0) / SATA(/dev/sda) 多种型号，
#   分区号也不保证是 1（Windows 装在 SteamOS 之前的机器 ESP 可能是 p2/p3）。
# 顺序：① 已挂载的 /esp（SteamOS）或 /boot/efi（Bazzite）→ ② 按 EFI 分区类型 GUID 找。
detect_esp() {
    local dev=""
    dev=$(findmnt -n -o SOURCE -M /esp 2>/dev/null | grep '^/dev/' | head -1 || true)
    [ -n "$dev" ] || dev=$(findmnt -n -o SOURCE -M /boot/efi 2>/dev/null | grep '^/dev/' | head -1 || true)
    if [ -z "$dev" ] || [ ! -b "$dev" ]; then
        dev=$(lsblk -P -n -o PATH,PARTTYPE 2>/dev/null \
            | awk -F'"' '/PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b"/{print $2; exit}' || true)
    fi
    [ -n "$dev" ] && [ -b "$dev" ] || return 1
    ESP_DEV="$dev"
    ESP_PARENT=$(lsblk -n -o PKNAME "$dev" 2>/dev/null | head -1 || true)
    ESP_DISK="/dev/${ESP_PARENT}"
    ESP_PARTN=$(lsblk -n -o PARTN "$dev" 2>/dev/null | head -1 || true)
    [ -n "$ESP_PARTN" ] || ESP_PARTN=1
    return 0
}

if ! detect_esp; then
    echo "❌ 无法识别 EFI 系统分区（ESP），已中止，未对系统做任何修改。"
    exit 1
fi
echo "检测到 ESP 分区: $ESP_DEV （磁盘 $ESP_DISK，分区号 $ESP_PARTN）"

# 用已识别的 ESP 设备计算剩余空间；ESP 变量单位是 KB
ESP=$(df --output=avail "$ESP_DEV" 2>/dev/null | tail -n1 | tr -d ' ' || true)
if ! [[ "$ESP" =~ ^[0-9]+$ ]]; then
    echo "❌ 无法读取 ESP 分区剩余空间，已中止。"
    exit 1
fi

# ===== SteamOS 只读模式守护 =====
# 原脚本在 rEFInd 分支里 disable 后若中途 exit，系统会一直停在可写状态。
# 用 EXIT trap 统一恢复：只有本脚本确实 disable 成功过才恢复。
# 注意：trap 必须在任何 disable 之前就装好（rEFInd 分支比原来的安装点更早）。
RO_DISABLED_BY_US=0
restore_readonly() {
    if [ "${RO_DISABLED_BY_US:-0}" -eq 1 ]; then
        if sudo -n steamos-readonly enable 2>/dev/null; then
            echo "已恢复 SteamOS 只读模式。"
        else
            echo "⚠️ 无法自动恢复只读模式，请手动执行: sudo steamos-readonly enable"
        fi
        RO_DISABLED_BY_US=0
    fi
    return 0
}
enable_readonly_mode() {
    sudo -n steamos-readonly enable 2>/dev/null || true
    RO_DISABLED_BY_US=0
}
# ISO/临时目录清理标志，与只读恢复合并在同一个 EXIT 钩子里
# （两者各自 trap EXIT 会互相覆盖，只保留最后装的那个）。
ISO_CLEANED=0
cleanup_iso() {
    [ "${ISO_CLEANED:-0}" -eq 1 ] && return 0
    ISO_CLEANED=1
    if [ "${ISO_MOUNTED:-0}" -eq 1 ]; then
        sudo -n umount ~/temp-clover &> /dev/null || true
        rmdir ~/temp-clover 2>/dev/null || true
        ISO_MOUNTED=0
    fi
    rm -f "${CLOVER_FILE:-}" "${CLOVER_BASE:-}"
}
clover_exit_hook() {
    local rc=$?
    cleanup_iso
    restore_readonly
    exit "$rc"
}
trap clover_exit_hook EXIT
CLOVER_VERSION=5172
CLOVER_EFI=\\EFI\\clover\\cloverx64.efi
BOARD_NAME=$(cat /sys/class/dmi/id/board_name)
PRODUCT_NAME=$(cat /sys/class/dmi/id/product_name)

if [ "$BOARD_NAME" = "Jupiter" ] || [ "$BOARD_NAME" = "Galileo" ]; then
    echo "检测到支持的设备 - Steam Deck $BOARD_NAME，无需修改 config.plist。"
elif [ "$PRODUCT_NAME" = "83L3" ] || [ "$PRODUCT_NAME" = "83Q2" ] || [ "$PRODUCT_NAME" = "83Q3" ]; then
    echo "检测到 Legion Go S，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1200<\/string>' custom/config.plist
elif [ "$PRODUCT_NAME" = "83N6" ]; then
    echo "不支持的设备 - Legion Go S 83N6，退出。"
    exit
elif [ "$PRODUCT_NAME" = "83E1" ]; then
    echo "检测到 Legion Go，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>2560x1600<\/string>' custom/config.plist
elif [ "$BOARD_NAME" = "RC71L" ]; then
    echo "检测到 ROG Ally，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' custom/config.plist
elif [ "$BOARD_NAME" = "RC72LA" ]; then
    echo "检测到 ROG Ally X，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' custom/config.plist
elif [ "$PRODUCT_NAME" = "ONEXPLAYER 2 PRO ARP23P" ]; then
    echo "检测到 Onexplayer 2 Pro，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>2560x1600<\/string>' custom/config.plist
else
    echo "⚠️ 警告：设备不在官方支持列表，强制继续安装（风险自负）！"
fi

if grep -qi bazzite /etc/os-release; then
    OS=bazzite
    EFI_PATH=/boot/efi/EFI
    BOOTX64=$EFI_PATH/BOOT/BOOTX64.EFI
    echo "检测到操作系统: Bazzite"
else
    grep -qi SteamOS /etc/os-release || { echo "既不是 SteamOS 也不是 Bazzite！退出。"; exit; }
    OS=SteamOS
    EFI_PATH=/esp/efi
    BOOTX64=$EFI_PATH/boot/bootx64.efi
    echo "检测到操作系统: SteamOS"
fi

if blkid "$ESP_DEV" 2>/dev/null | grep -qi microsoft; then
    echo "检测到不支持的双系统配置（Windows 安装在 SteamOS 之前）。请确保 SteamOS 安装在 Windows 之前！"
    exit 1
else
    echo "双系统配置检查通过。"
fi

# 密码处理：
#  - 原写法把密码经 `echo -e "$pw\n"` 放进管道。密码是 shell 变量而非外部命令参数，
#    实测 ps 里看不到明文；但 `echo -e` 会解释反斜杠，密码里含 `\` 时会被改写/截断
#    （实测 'p\cw' → 'p'），导致 sudo 认证失败。改用 printf '%s\n' 原样输出。
#  - 验证成功后立刻 `sudo -v` 取到时间戳，后续统一 `sudo -n`，不再反复喂密码。
if [ "$(passwd --status "$(whoami)" | tr -s " " | cut -d " " -f 2)" == "P" ]; then
    read -s -p "请输入当前 sudo 密码: " current_password < /dev/tty; echo
    echo "正在验证 sudo 密码..."
    if ! printf '%s\n' "$current_password" | sudo -S -v &> /dev/null; then
        echo "sudo 密码错误！请重新运行脚本并输入正确密码。"
        exit 1
    fi
    echo "sudo 密码正确。"
else
    echo "未设置 sudo 密码！请先设置密码再运行脚本。"
    passwd || true
    exit 1
fi

# 后续统一走 sudo -n（密码已由上面的 sudo -v 缓存）；失败直接中止而不是继续写 EFI。
mkdir -p ~/temp-ESP
if ! sudo -n mount "$ESP_DEV" ~/temp-ESP; then
    echo "挂载 ESP 分区失败！已中止，未修改系统。"
    rmdir ~/temp-ESP 2>/dev/null || true
    exit 1
fi
echo "ESP 分区已挂载。"
if [ "$ESP" -ge 15000 ]; then
    echo "ESP 分区剩余空间: $ESP KB，空间充足。"
    sudo -n umount ~/temp-ESP || true
    rmdir ~/temp-ESP 2>/dev/null || true
else
    echo "ESP 分区剩余空间: $ESP KB，空间不足！请清理后重试。"
    # 注意：这里输出“空间不足”，外层成功判定已同步匹配该关键字
    sudo -n du -hd2 /esp || true
    sudo -n umount ~/temp-ESP || true
    rmdir ~/temp-ESP 2>/dev/null || true
    exit 1
fi

if efibootmgr | grep -qi refind; then
    echo "检测到 rEFInd，正在尽力卸载..."
    for rEFInd_boot in $REFIND; do
        sudo -n efibootmgr -b "$rEFInd_boot" -B &> /dev/null || true
    done
    sudo -n systemctl disable bootnext-refind.service &> /dev/null || true
    sudo -n systemctl disable rEFInd_bg_randomizer.service &> /dev/null || true
    sudo -n rm -rf "$EFI_PATH/refind" &> /dev/null || true
    if sudo -n steamos-readonly disable; then
        RO_DISABLED_BY_US=1
    else
        echo "⚠️ 无法禁用只读模式，rEFInd 卸载可能失败。"
    fi
    sudo -n rm -f /etc/systemd/system/bootnext-refind.service &> /dev/null || true
    sudo -n rm -f /etc/systemd/system/rEFInd_bg_randomizer.service &> /dev/null || true
    sudo -n pacman-key --init || true
    sudo -n pacman-key --populate archlinux || true
    sudo -n pacman -R --noconfirm SteamDeck_rEFInd || true
    enable_readonly_mode
    rm -rf ~/.local/SteamDeck_rEFInd ~/.SteamDeck_rEFInd ~/Desktop/SteamDeck_rEFInd.desktop
    if efibootmgr | grep -qi refind; then
        echo "rEFInd 卸载失败，请手动卸载后重试。"
        exit 1
    fi
    echo "rEFInd 已成功卸载。"
else
    echo "未检测到 rEFInd，继续安装 Clover。"
fi

CLOVER_FILE="Clover-${CLOVER_VERSION}-X64.iso.7z"
CLOVER_BASE=$(basename -s .7z "${CLOVER_FILE}")

# Clover ISO 是普通 HTTP 下载（非 git），可用全部下载镜像。
# 前缀只到「镜像主机/」，后面接完整的 GitHub URL；官方源前缀为空。
# 注意：此处覆盖了全局 MIRRORS 变量（仅在此内层脚本作用域内）。
CLOVER_GH_BASE="https://github.com/CloverHackyColor/CloverBootloader"
MIRRORS=(
    "https://gh-proxy.com/"
    "https://gh.3w.pm/"
    "https://cors.isteed.cc/"
    "https://ghproxy.net/"
    ""                            # 官方源：前缀为空，直接用完整 GitHub URL
)
MIRROR_LABELS=(
    "gh-proxy.com (国内镜像，速度快)"
    "gh.3w.pm (国内镜像，稳定)"
    "cors.isteed.cc (国内镜像，稳定)"
    "ghproxy.net (国内镜像，慢速备用)"
    "GitHub (官方源)"
)

DOWNLOAD_SUCCESS=0
while true; do
    echo ""
    echo "请选择下载镜像源（输入编号，0取消）："
    for i in "${!MIRRORS[@]}"; do
        echo "  $((i+1)). ${MIRROR_LABELS[$i]:-${MIRRORS[$i]}}"
    done
    read -p "请输入选择: " choice < /dev/tty

    if [[ -z "$choice" ]]; then
        echo "输入无效，请重新选择。"
        continue
    fi
    if [[ "$choice" == "0" ]]; then
        echo "操作已取消。"
        exit 0
    fi
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
        mirror="${MIRRORS[$((choice-1))]}"
        CLOVER_URL="${mirror}${CLOVER_GH_BASE}/releases/download/${CLOVER_VERSION}/${CLOVER_FILE}"
        echo "尝试从 ${MIRROR_LABELS[$((choice-1))]:-${mirror}} 下载..."
        if curl -# -L --fail --connect-timeout 10 --max-time 120 -o "${CLOVER_FILE}" "${CLOVER_URL}"; then
            echo "✅ 下载成功！"
            DOWNLOAD_SUCCESS=1
            break
        else
            echo "⚠️ 下载失败，请重新选择镜像源。"
            rm -f "${CLOVER_FILE}"
        fi
    else
        echo "无效编号，请重新选择。"
    fi
done

if [ ${DOWNLOAD_SUCCESS} -eq 0 ]; then
    echo "❌ 下载 Clover 失败！所有镜像源均不可用，请检查网络后重试。"
    exit 1
fi

# 解压失败时清理下载的 7z 与可能残留的 ISO，避免占满 /home
if ! 7z x "${CLOVER_FILE}" -aoa "${CLOVER_BASE}" &> /dev/null; then
    echo "解压 Clover ISO 失败！"
    rm -f "${CLOVER_FILE}" "${CLOVER_BASE}"
    exit 1
fi
if [ ! -f "${CLOVER_BASE}" ]; then
    echo "解压后未找到 ISO 文件 ${CLOVER_BASE}，已中止。"
    rm -f "${CLOVER_FILE}"
    exit 1
fi
echo "Clover ISO 解压成功。"

# 挂载失败时把临时目录、ISO、7z 一并清理干净
mkdir -p ~/temp-clover
if ! sudo -n mount "${CLOVER_BASE}" ~/temp-clover &> /dev/null; then
    echo "挂载 Clover ISO 失败！已清理临时文件。"
    sudo -n umount ~/temp-clover &> /dev/null || true
    rmdir ~/temp-clover 2>/dev/null || true
    rm -f "${CLOVER_FILE}" "${CLOVER_BASE}"
    exit 1
fi
ISO_MOUNTED=1
echo "Clover ISO 已挂载。"

# 安装中途任何一步失败都要卸载 ISO、清理临时文件，不留半套环境。
# 注意：trap ... ERR 在脚本里 `exit 1` 触发的路径上**不会**执行（实测残留 ISO），
# 所以清理挂在上面已装好的 EXIT 钩子里，用 ISO_MOUNTED 标志决定是否卸载。
if ! sudo -n cp -Rf ~/temp-clover/efi/clover "$EFI_PATH"; then
    echo "❌ 复制 Clover EFI 文件到 ESP 失败（可能是 ESP 空间不足）。已中止。"
    exit 1
fi
sudo -n cp custom/config.plist "$EFI_PATH/clover/config.plist"
sudo -n cp -Rf custom/themes/. "$EFI_PATH/clover/themes/" \
    || { echo "❌ 复制主题文件失败，已中止。"; exit 1; }
sudo -n rm -rf "$EFI_PATH/clover/themes/bgm" "$EFI_PATH/clover/themes/cesium" \
    "$EFI_PATH/clover/themes/christmas" "$EFI_PATH/clover/themes/glass" \
    "$EFI_PATH/clover/themes/purple_swirl" "$EFI_PATH/clover/themes/theme-sample.plist" \
    || true

if [ "$PRODUCT_NAME" = "83N6" ] || [ "$PRODUCT_NAME" = "83L3" ] || [ "$PRODUCT_NAME" = "83Q2" ] || [ "$PRODUCT_NAME" = "83Q3" ] || [ "$PRODUCT_NAME" = "83E1" ] || [ "$BOARD_NAME" = "RC71L" ] || [ "$BOARD_NAME" = "RC72LA" ] || [ "$PRODUCT_NAME" = "ONEXPLAYER 2 PRO ARP23P" ]; then
    echo "非 Steam Deck 设备，正在安装 Xbox 360 UEFI 驱动..."
    if sudo -n cp custom/UsbXbox360Dxe.efi "$EFI_PATH/clover/drivers/uefi"; then
        echo "Xbox 360 驱动安装成功。"
    else
        echo "Xbox 360 驱动安装失败！"
        exit 1
    fi
else
    echo "Steam Deck 无需安装 Xbox 360 驱动。"
fi

cleanup_iso
echo "临时文件已清理。"

for entry in $CLOVER; do
    sudo -n efibootmgr -b "$entry" -B &> /dev/null || true
done

# 修复：原来 efibootmgr -c 硬编码 /dev/nvme0n1 -p 1。eMMC 机型是 /dev/mmcblk0，
# SATA 机型是 /dev/sda，且 ESP 分区号不一定是 1。改用上面动态探测的 ESP_DISK/ESP_PARTN，
# 并且把输出留出来（不再 &>/dev/null 丢弃），失败时能中止并回滚。
if ! sudo -n efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" -L "Clover - GUI Boot Manager" -l "$CLOVER_EFI"; then
    echo "❌ 创建 Clover EFI 启动项失败（磁盘 $ESP_DISK 分区 $ESP_PARTN）。安装中止。"
    exit 1
fi
CLOVER=$(efibootmgr | grep -i "Clover - GUI" | colrm 9 | colrm 1 4 || true)
if [ -z "$CLOVER" ]; then
    echo "❌ 写入 EFI 后仍找不到 Clover 启动项，安装中止。"
    exit 1
fi
echo "已创建 Clover 启动项: $CLOVER"

# BOOTX64 替换：必须先备份成功再覆盖；任何一步失败立刻回滚到备份。
if [ ! -e "$BOOTX64" ]; then
    echo "❌ 未找到 $BOOTX64，无法备份/替换。已中止（EFI 启动项将回滚）。"
    sudo -n efibootmgr -b "$CLOVER" -B &> /dev/null || true
    exit 1
fi
if [ -e "$BOOTX64.orig" ]; then
    echo "$BOOTX64.orig 已存在，无需备份。"
else
    echo "备份 $BOOTX64 为 $BOOTX64.orig"
    if ! sudo -n cp "$BOOTX64" "$BOOTX64.orig"; then
        echo "❌ 备份 $BOOTX64 失败，已中止，未覆盖原文件。"
        sudo -n efibootmgr -b "$CLOVER" -B &> /dev/null || true
        exit 1
    fi
fi
if ! sudo -n cp "$EFI_PATH/clover/cloverx64.efi" "$BOOTX64"; then
    echo "❌ 替换 bootx64.efi 为 Clover EFI 失败！正在回滚..."
    if sudo -n cp "$BOOTX64.orig" "$BOOTX64"; then
        echo "已回滚 BOOTX64.EFI 到原始版本。"
    else
        echo "⚠️ 回滚也失败了！请手动执行: sudo cp $BOOTX64.orig $BOOTX64"
    fi
    sudo -n efibootmgr -b "$CLOVER" -B &> /dev/null || true
    exit 1
fi
echo "已替换 bootx64.efi 为 Clover EFI。"

if [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" ]; then
    if [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" ]; then
        sudo -n mv "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/bootmgfw.efi"
        echo "已禁用 Windows EFI 直接启动。"
    else
        echo "Windows EFI 已禁用。"
    fi
else
    sudo -n cp "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig"
    sudo -n mv "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/bootmgfw.efi"
    echo "已禁用 Windows EFI 直接启动。"
fi

sudo -n efibootmgr -n "$CLOVER" || true
sudo -n efibootmgr -o "$CLOVER" || true

if efibootmgr | grep -q "Clover - GUI"; then
    echo "Clover 已成功安装到 EFI 系统分区！"
else
    echo "哎呀，出错了，Clover 未安装成功。"
    exit 1
fi

# 以下属于“EFI 已经写好之后”的附加组件。失败时只警告不中止：
# 此时 Clover 已可引导，若因工具/SYSTEMD 失败而整体报错，反而会让用户以为没装上。
mkdir -p ~/1Clover-tools
rm -f ~/1Clover-tools/* 2>/dev/null || true
cp custom/Clover-Toolbox.sh ~/1Clover-tools || echo "⚠️ 复制 Clover-Toolbox.sh 失败，桌面工具箱可能不可用。"
sudo -n cp custom/clover-bootmanager.service custom/clover-bootmanager.sh /etc/systemd/system \
    || echo "⚠️ 安装 clover-bootmanager 服务文件失败。"
cp -R custom/logos ~/1Clover-tools 2>/dev/null || true
cp -R custom/efi ~/1Clover-tools 2>/dev/null || true

chmod +x ~/1Clover-tools/Clover-Toolbox.sh 2>/dev/null || true
sudo -n chmod +x /etc/systemd/system/clover-bootmanager.sh 2>/dev/null || true

sudo -n systemctl daemon-reload || echo "⚠️ systemctl daemon-reload 失败。"
sudo -n systemctl enable --now clover-bootmanager.service \
    || echo "⚠️ 启用 clover-bootmanager.service 失败，下次开机会直接进 Clover 而不是上次系统。"
sudo -n /etc/systemd/system/clover-bootmanager.sh \
    || echo "⚠️ 执行 clover-bootmanager.sh 失败，BootNext 可能未设置。"

if [ "$OS" = "SteamOS" ]; then
    mkdir -p ~/.local/share/kservices5/ServiceMenus
    cp custom/open_as_root.desktop ~/.local/share/kservices5/ServiceMenus 2>/dev/null || true
    sudo -n cp custom/clover-whitelist.conf /etc/atomic-update.conf.d \
        || echo "⚠️ 安装 clover-whitelist.conf 失败，系统更新后 Clover 配置可能被还原。"
else
    if ! blkid "$ESP_DEV" 2>/dev/null | grep -qi esp; then
        sudo -n fatlabel "$ESP_DEV" esp || true
        echo "ESP 分区标签已设置。"
    fi
    sudo -n sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\fedora\\shimx64\.efi<\/string>' $EFI_PATH/clover/config.plist
fi

echo "Clover 安装完成于 $OS！"
CLOVER_SCRIPT_EOF

    chmod +x install-Clover.sh || {
        echo -e "${RED}无法设置 install-Clover.sh 执行权限。${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    }

    echo -e "${CYAN}即将运行 Clover 安装脚本，请根据提示输入 sudo 密码（如果需要）...${NC}"
    sleep 1

    LOG_FILE="/tmp/clover_install.log"
    # 修复：管道后直接取 $? 拿到的是 tee 的退出码，不是 install-Clover.sh 的
    # （实测 `false | tee x.log; echo $?` 输出 0）。这里显式取 PIPESTATUS[0]，
    # 并临时打开 pipefail 兜底，避免将来外层 set 选项被改动后判定静默失效。
    set -o pipefail
    ./install-Clover.sh 2>&1 | tee "$LOG_FILE"
    INSTALL_EXIT=${PIPESTATUS[0]}

    # 修复：原判定 grep 的 "Not enough space on the ESP partition!" 在本脚本里
    # 根本不存在（内层实际输出的是中文“空间不足”），属于永远不命中的死代码。
    if grep -q "Not enough space on the ESP partition" "$LOG_FILE" \
        || grep -q "空间不足" "$LOG_FILE"; then
        echo -e "${RED}安装失败：ESP分区空间不足，请清理后重试。${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    elif [ $INSTALL_EXIT -eq 0 ] && grep -q "Clover 安装完成" "$LOG_FILE"; then
        echo -e "${GREEN}Clover 安装/重装成功！${NC}"
    else
        echo -e "${RED}安装/重装失败，请检查上方输出。${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    fi

    SHORTCUT="$HOME/Desktop/引导文件配置.desktop"
    if [ -f "$SHORTCUT" ]; then
        echo -e "${GREEN}桌面快捷方式“引导文件配置”已存在，无需创建。${NC}"
    else
        # 修复：原 heredoc 带引号（<< 'EOF'）不会展开变量，Exec 里写死 /home/deck，
        # 用户名不是 deck 的机器上快捷方式直接失效。这里去掉引号让 $HOME 展开；
        # 已确认该 heredoc 除路径外没有其它 $ 或反引号。
        cat > "$SHORTCUT" << EOF
[Desktop Entry]
Type=Application
Name=引导文件配置
Exec=konsole -e bash -c '$HOME/1Clover-tools/Clover-Toolbox.sh; read -p "按回车键关闭..." -n1'
Icon=kdiamond
Terminal=false
Categories=Utility;
EOF
        chmod +x "$SHORTCUT"
        echo -e "${GREEN}已创建桌面快捷方式“引导文件配置”。${NC}"
    fi

    cat > ~/1Clover-tools/Clover-Toolbox.sh << 'TOOLBOX_EOF'
#!/bin/bash

grep -i bazzite /etc/os-release &> /dev/null
if [ $? -eq 0 ]
then
	OS=bazzite
	EFI_PATH=/boot/efi/EFI
	BOOTX64=$EFI_PATH/BOOT/BOOTX64.EFI
else
	grep -i SteamOS /etc/os-release &> /dev/null
	if [ $? -eq 0 ]
	then
		OS=SteamOS
		EFI_PATH=/esp/efi
		BOOTX64=$EFI_PATH/boot/bootx64.efi
	else
		exit
	fi
fi

current_password=$(zenity --password --title "sudo 密码验证")
printf '%s\n' "$current_password" | sudo -S ls &> /dev/null
if [ $? -ne 0 ]
then
	echo "sudo 密码错误！" | \
		zenity --text-info --title "Clover 工具箱" --width 400 --height 200
	exit
fi

while true
do
Choice=$(zenity --width 750 --height 450 --list --radiolist --multiple \
	--title "Clover 工具箱 - https://github.com/ryanrudolfoba/SteamDeck-clover-dualboot" \
	--column "选择" \
	--column "选项" \
	--column "说明 - 请仔细阅读" \
	FALSE 状态 "提交错误报告时请选用此项" \
	FALSE Batocera "选择 Batocera v39 (及更新) 或 v38 (及更旧) 的配置" \
	FALSE 主题 "选择固定主题或随机主题" \
	FALSE 超时 "设置默认超时时间 (1/5/10/15 秒) 后自动启动默认系统" \
	FALSE 服务 "禁用/启用 Clover EFI 条目和 systemd 服务" \
	FALSE 默认启动 "设置默认启动的操作系统" \
	FALSE 新Logo "替换 BGRT 启动标志" \
	FALSE 恢复Logo "恢复默认的 BGRT 启动标志" \
	FALSE 分辨率 "设置屏幕分辨率 (DeckHD 或 DeckSight 屏幕改装)" \
	FALSE 自定义 "替换 Clover EFI 为隐藏 OPTIONS 按钮的自定义版本" \
	FALSE 卸载 "卸载 Clover 并恢复所有更改" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

if [ $? -eq 1 ] || [ "$Choice" == "退出" ]
then
	echo "用户按下了取消/退出。"
	exit

elif [ "$Choice" == "状态" ]
then
	zenity --warning --title "Clover 工具箱" --text "$(fold -w 120 -s ~/1Clover-tools/status.txt)" --width 1000 --height 400

elif [ "$Choice" == "Batocera" ]
then
Batocera_Choice=$(zenity --width 550 --height 220 --list --radiolist --multiple --title "Clover 工具箱" --column "选择" \
	--column "选项" --column "说明 - 请仔细阅读" \
	FALSE v39 "为 Batocera v39 及更新版本设置 Clover 配置" \
	FALSE v38 "为 Batocera v38 及更旧版本设置 Clover 配置" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Batocera_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Batocera_Choice" == "v39" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<string>os_batocera<\/string>/!b;n;n;c\\t\t\t\t\t<string>\\efi\\batocera\\grubx64\.efi<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "已为 Batocera v39 及更新版本更新 Clover 配置！" --width 450 --height 75

	elif [ "$Batocera_Choice" == "v38" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<string>os_batocera<\/string>/!b;n;n;c\\t\t\t\t\t<string>\\efi\\boot\\bootx64\.efi<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "已为 Batocera v38 及更旧版本更新 Clover 配置！" --width 450 --height 75

	fi

elif [ "$Choice" == "主题" ]
then
Theme_Choice=$(zenity --title "Clover 工具箱"	--width 200 --height 325 --list \
	--column "主题名称" $(printf '%s\n' "$current_password" | sudo -S ls $EFI_PATH/clover/themes) )

	if [ $? -eq 1 ]
	then
		echo "用户按了取消。返回主菜单。"
	else
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>Theme<\/key>/!b;n;c\\t\t<string>'$Theme_Choice'<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "主题已更改为 $Theme_Choice！" --width 400 --height 75
	fi

elif [ "$Choice" == "超时" ]
then
Timeout_Choice=$(zenity --width 500 --height 300 --list --radiolist --multiple \
	--title "Clover 工具箱" --column "选择" --column "选项" --column "说明 - 请仔细阅读" \
	FALSE 1 "设置默认超时时间为 1 秒" \
	FALSE 5 "设置默认超时时间为 5 秒" \
	FALSE 10 "设置默认超时时间为 10 秒" \
	FALSE 15 "设置默认超时时间为 15 秒" \
 	FALSE 60 "设置默认超时时间为 60 秒" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Timeout_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"
	else
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>Timeout<\/key>/!b;n;c\\t\t<integer>'$Timeout_Choice'<\/integer>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "默认超时时间已设置为 $Timeout_Choice 秒！" --width 400 --height 75
	fi

elif [ "$Choice" == "服务" ]
then
Service_Choice=$(zenity --width 650 --height 250 --list --radiolist --multiple --title "Clover 工具箱" \
	--column "选择" --column "选项" --column "说明 - 请仔细阅读" \
	FALSE 禁用 "禁用 Clover EFI 条目和 systemd 服务" \
	FALSE 启用 "启用 Clover EFI 条目和 systemd 服务" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Service_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Service_Choice" == "禁用" ]
	then
		printf '%s\n' "$current_password" | sudo -S cp $EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig $EFI_PATH/Microsoft/Boot/bootmgfw.efi

		Windows=$(efibootmgr | grep -i Windows | colrm 9 | colrm 1 4)
		printf '%s\n' "$current_password" | sudo -S efibootmgr -n $Windows &> /dev/null

		printf '%s\n' "$current_password" | sudo -S systemctl disable --now clover-bootmanager
		zenity --warning --title "Clover 工具箱" --text "Clover systemd 服务已禁用。Windows 现已激活！" --width 500 --height 75

	elif [ "$Service_Choice" == "启用" ]
	then
		sudo systemctl enable --now clover-bootmanager
		printf '%s\n' "$current_password" | sudo -S /etc/systemd/system/clover-bootmanager.sh
		zenity --warning --title "Clover 工具箱" --text "Clover systemd 服务已启用。Windows 已禁用！" --width 500 --height 75
	fi

elif [ "$Choice" == "默认启动" ]
then
Boot_Choice=$(zenity --width 550 --height 300 --list --radiolist --multiple --title "Clover 工具箱" --column "选择" \
	--column "选项" --column "说明 - 请仔细阅读" \
	FALSE Windows "将 Windows 设为默认启动系统" \
	FALSE SteamOS "将 SteamOS 设为默认启动系统" \
	FALSE Bazzite "将 Bazzite 设为默认启动系统" \
	FALSE 上次系统 "将上一次启动的系统设为默认" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Boot_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Boot_Choice" == "Windows" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\microsoft\\bootmgfw\.efi<\/string>' $EFI_PATH/clover/config.plist
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "Windows 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "SteamOS" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\steamos\\steamcl\.efi<\/string>' $EFI_PATH/clover/config.plist
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "SteamOS 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "Bazzite" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\EFI\\FEDORA\\shimx64\.efi<\/string>' $EFI_PATH/clover/config.plist
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "Bazzite 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "上次系统" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>LastBootedVolume<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "上一次使用的系统现在是 Clover 中的默认启动项！" --width 425 --height 75
	fi

elif [ "$Choice" == "新Logo" ]
then
Logo_Choice=$(zenity --title "Clover 工具箱" --width 200 --height 350 --list \
	--column "Logo 名称" $(ls -l ~/1Clover-tools/logos/*.png | sed s/^.*\\/\//) )
	if [ $? -eq 1 ]
	then
		echo "用户按了取消。返回主菜单。"
	else
		printf '%s\n' "$current_password" | sudo -S cp ~/1Clover-tools/logos/$Logo_Choice $EFI_PATH/steamos/steamos.png
		zenity --warning --title "Clover 工具箱" --text "BGRT 标志已更改为 $Logo_Choice！" --width 400 --height 75
	fi

elif [ "$Choice" == "恢复Logo" ]
then
	printf '%s\n' "$current_password" | sudo -S rm $EFI_PATH/steamos/steamos.png &> /dev/null
	zenity --warning --title "Clover 工具箱" --text "BGRT 标志已恢复为默认！" --width 400 --height 75

elif [ "$Choice" == "分辨率" ]
then
Resolution_Choice=$(zenity --width 550 --height 250 --list --radiolist --multiple --title "Clover 工具箱" \
	--column "选择" --column "选项" --column "说明 - 请仔细阅读" \
	FALSE 默认 "使用默认屏幕分辨率 1280x800" \
	FALSE DeckHD "使用 DeckHD 屏幕分辨率 1920x1200" \
	FALSE DeckSight "使用 DeckSight 屏幕分辨率 1920x1080" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Resolution_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Resolution_Choice" == "默认" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1280x800<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1280x800。" --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckHD" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1200<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1920x1200。" --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckSight" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1920x1080。" --width 400 --height 75

	fi

elif [ "$Choice" == "自定义" ]
then
	printf '%s\n' "$current_password" | sudo -S cp ~/1Clover-tools/efi/custom_clover_5157.efi $EFI_PATH/clover/cloverx64.efi
	zenity --warning --title "Clover 工具箱" --text "自定义 Clover EFI 已安装！" --width 400 --height 75

elif [ "$Choice" == "卸载" ]
then
	# 修复：卸载前先确认要恢复的文件都存在。原来 .orig 不存在时 mv 失败后
	# 不做任何检查就继续 rm -rf $EFI_PATH/clover，会留下“Clover 文件删了、
	# Windows/BOOTX64 又没恢复”的半卸载状态，可能直接无法开机。
	UNINSTALL_OK=1
	if [ ! -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" ] \
		&& [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" ]; then
		echo "⚠️ 未找到 bootmgfw.efi.orig，跳过 Windows EFI 恢复（保持现状）。"
	elif [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" ]; then
		if ! sudo -n mv -f "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" "$EFI_PATH/Microsoft/Boot/bootmgfw.efi"; then
			echo "❌ 恢复 Windows bootmgfw.efi 失败，卸载中止，未做其它修改。"
			UNINSTALL_OK=0
		fi
	fi
	if [ "$UNINSTALL_OK" -eq 1 ] && [ ! -e "$BOOTX64.orig" ]; then
		echo "⚠️ 未找到 $BOOTX64.orig，跳过 BOOTX64.EFI 恢复（保持现状）。"
	elif [ "$UNINSTALL_OK" -eq 1 ]; then
		if ! sudo -n mv -f "$BOOTX64.orig" "$BOOTX64"; then
			echo "❌ 恢复 BOOTX64.EFI 失败，卸载中止，未做其它修改。"
			UNINSTALL_OK=0
		fi
	fi
	if [ "$UNINSTALL_OK" -ne 1 ]; then
		zenity --error --title "Clover 工具箱" --text "卸载中止：关键引导文件恢复失败。\n请手动检查 EFI 分区后再试。" --width 500 --height 100
		exit 1
	fi

	printf '%s\n' "$current_password" | sudo -S rm -rf $EFI_PATH/clover

	for entry in $(efibootmgr | grep "Clover - GUI" | colrm 9 | colrm 1 4)
	do
		printf '%s\n' "$current_password" | sudo -S efibootmgr -b $entry -B &> /dev/null
	done

	printf '%s\n' "$current_password" | sudo -S rm $EFI_PATH/steamos/steamos.png &> /dev/null

	# 修复：原逻辑 disable 后若中间任一步失败退出，系统会一直停在可写状态。
	# 这里用 EXIT trap 保证无论怎么退出都恢复只读。
	TB_RO_DISABLED=0
	tb_restore_readonly() {
		if [ "${TB_RO_DISABLED:-0}" -eq 1 ]; then
			printf '%s\n' "$current_password" | sudo -S steamos-readonly enable 2>/dev/null \
				&& echo "已恢复只读模式。" \
				|| echo "⚠️ 无法恢复只读模式，请手动执行: sudo steamos-readonly enable"
		fi
	}
	trap tb_restore_readonly EXIT
	if printf '%s\n' "$current_password" | sudo -S steamos-readonly disable; then
		TB_RO_DISABLED=1
	fi

	printf '%s\n' "$current_password" | sudo -S systemctl stop clover-bootmanager.service
	printf '%s\n' "$current_password" | sudo -S rm -f /etc/systemd/system/clover-bootmanager*
	printf '%s\n' "$current_password" | sudo -S systemctl daemon-reload

	printf '%s\n' "$current_password" | sudo -S rm -f /etc/atomic-update.conf.d/clover-whitelist.conf

	printf '%s\n' "$current_password" | sudo -S steamos-readonly enable
	TB_RO_DISABLED=0

	rm -f ~/.local/share/kservices5/ServiceMenus/open_as_root.desktop

	rm -rf ~/SteamDeck-Clover-dualboot
	rm -rf ~/1Clover-tools/

	rm -f ~/Desktop/引导文件配置.desktop

	zenity --warning --title "Clover 工具箱" --text "Clover 已卸载，Windows EFI 条目已激活！" --width 600 --height 75
	exit
fi
done
TOOLBOX_EOF

    chmod +x ~/1Clover-tools/Clover-Toolbox.sh
    echo -e "${GREEN}✓ 已更新 Clover-Toolbox.sh 为汉化版。${NC}"

    echo -e "${YELLOW}建议重启设备以使引导生效。${NC}"
    echo ""
}

install_anydesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 AnyDesk ════════════════${NC}"

    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    local ANYDESK_BIN="$ANYDESK_INSTALL_DIR/anydesk"
    local DESKTOP_FILE="$HOME/Desktop/AnyDesk.desktop"

    echo "正在检查最新版本..."
    local REMOTE_VERSION=$(curl -s https://anydesk.com.cn/zhs/downloads/linux | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/^v//')
    if [ -z "$REMOTE_VERSION" ]; then
        echo -e "${YELLOW}无法自动获取版本，尝试使用默认版本 8.0.4${NC}"
        REMOTE_VERSION="8.0.4"
    fi
    echo "最新版本: $REMOTE_VERSION"

    local LOCAL_VERSION=""
    if [ -f "$ANYDESK_BIN" ] && [ -x "$ANYDESK_BIN" ]; then
        LOCAL_VERSION=$("$ANYDESK_BIN" --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [ -n "$LOCAL_VERSION" ]; then
            echo -e "${CYAN}当前已安装版本: ${LOCAL_VERSION}${NC}"
        else
            echo -e "${YELLOW}已安装但无法读取版本号，将重新安装。${NC}"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 AnyDesk。${NC}"
    fi

    local TARGET_VERSION=""
    if [ -n "$LOCAL_VERSION" ]; then
        if [ "$LOCAL_VERSION" = "$REMOTE_VERSION" ]; then
            echo -e "${GREEN}✅ 已是最新版本 ${LOCAL_VERSION}，无需操作。${NC}"
            return 0
        else
            echo -e "${YELLOW}发现新版本 ${REMOTE_VERSION}（当前: ${LOCAL_VERSION}）${NC}"
            read -n1 -p "按回车键或 A 键更新，其他键取消: " confirm < /dev/tty
            echo
            if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
                TARGET_VERSION="$REMOTE_VERSION"
            else
                echo "取消更新。"
                return 0
            fi
        fi
    else
        TARGET_VERSION="$REMOTE_VERSION"
    fi

    if [ -z "$TARGET_VERSION" ]; then
        echo "未指定目标版本，操作取消。"
        return 0
    fi

    echo "正在安装 AnyDesk ${TARGET_VERSION}..."
    cd /tmp || return

    local URL="https://download.anydesk.com/linux/anydesk-${TARGET_VERSION}-amd64.tar.gz"
    local TARBALL="/tmp/anydesk-${TARGET_VERSION}.tar.gz"
    local EXTRACT_DIR="/tmp/anydesk-extract.$$"
    echo "下载中..."

    # 先把包下载并解压到临时目录，全部成功后再替换旧安装。
    # 原逻辑是先 rm -rf 旧目录再下载，网络一失败用户的可用 AnyDesk 就没了。
    rm -f "$TARBALL"
    if ! wget -q --show-progress "$URL" -O "$TARBALL"; then
        echo -e "${RED}下载失败，请检查网络后重试。${NC}"
        echo -e "${YELLOW}已保留原有的 AnyDesk 安装（如有）。${NC}"
        rm -f "$TARBALL"
        return 1
    fi
    rm -rf "$EXTRACT_DIR"; mkdir -p "$EXTRACT_DIR"
    if ! tar -xzf "$TARBALL" -C "$EXTRACT_DIR" --strip-components=1; then
        echo -e "${RED}✗ 解压失败，安装中止。${NC}"
        rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
        echo -e "${YELLOW}已保留原有的 AnyDesk 安装（如有）。${NC}"
        return 1
    fi
    if [ ! -x "$EXTRACT_DIR/anydesk" ]; then
        echo -e "${RED}✗ 安装包内容不完整（未找到 anydesk 可执行文件），安装中止。${NC}"
        rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
        echo -e "${YELLOW}已保留原有的 AnyDesk 安装（如有）。${NC}"
        return 1
    fi

    rm -rf "$ANYDESK_INSTALL_DIR"
    mkdir -p "$ANYDESK_INSTALL_DIR"
    if ! cp -a "$EXTRACT_DIR"/. "$ANYDESK_INSTALL_DIR"/; then
        echo -e "${RED}✗ 安装文件复制失败。${NC}"
        rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
        return 1
    fi
    rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
    chmod +x "$ANYDESK_BIN" 2>/dev/null
    if [ ! -x "$ANYDESK_BIN" ]; then
        echo -e "${RED}✗ 安装文件不完整（未找到可执行文件）。${NC}"
        rm -rf "$ANYDESK_INSTALL_DIR"
        return 1
    fi
    mkdir -p "$HOME/.local/bin"
    ln -sf "$ANYDESK_BIN" "$HOME/.local/bin/anydesk"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AnyDesk
Exec=$ANYDESK_BIN
Icon=$ANYDESK_INSTALL_DIR/icons/hicolor/256x256/apps/anydesk.png
Type=Application
Categories=Network;RemoteAccess;
EOF
    chmod +x "$DESKTOP_FILE"

    echo ""
    echo -e "${GREEN}✅ AnyDesk ${TARGET_VERSION} 安装完成！桌面快捷方式已创建。${NC}"
}

uninstall_anydesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 AnyDesk ════════════════${NC}"

    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    local DESKTOP_FILE="$HOME/Desktop/AnyDesk.desktop"
    local BIN_LINK="$HOME/.local/bin/anydesk"
    local flatpak_id="com.anydesk.Anydesk"

    local local_found=false
    local flatpak_found=false
    [ -d "$ANYDESK_INSTALL_DIR" ] && local_found=true
    flatpak info "$flatpak_id" &>/dev/null && flatpak_found=true

    if ! $local_found && ! $flatpak_found; then
        echo -e "${YELLOW}未检测到已安装的 AnyDesk。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到 AnyDesk 安装：${NC}"
    $local_found && echo "  • 本地安装 ($ANYDESK_INSTALL_DIR)"
    $flatpak_found && echo "  • Flatpak 安装 ($flatpak_id)"

    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    if $local_found; then
        rm -rf "$ANYDESK_INSTALL_DIR" && echo -e "${GREEN}✓ 已删除本地安装目录${NC}"
        rm -f "$DESKTOP_FILE" && echo -e "${GREEN}✓ 已删除本地桌面快捷方式${NC}"
        rm -f "$BIN_LINK" && echo -e "${GREEN}✓ 已删除命令链接${NC}"
    fi

    if $flatpak_found; then
        echo "正在卸载 Flatpak 版本的 AnyDesk..."
        if flatpak uninstall "$flatpak_id" -y &>/dev/null; then
            echo -e "${GREEN}✓ Flatpak 版本已卸载${NC}"
            local desktop_dir="$HOME/Desktop"
            if [ -d "$desktop_dir" ]; then
                for f in "$desktop_dir"/*.desktop; do
                    local base=$(basename "$f")
                    if [ "$base" = "AnyDesk.desktop" ] || \
                       [ "$base" = "${flatpak_id}.desktop" ] || \
                       [[ "$base" == *"${flatpak_id//./_}"* ]]; then
                        rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ 已删除桌面快捷方式 $base${NC}"
                    fi
                done
            fi

            local data_dir="$HOME/.var/app/$flatpak_id"
            if [ -d "$data_dir" ]; then
                echo ""
                echo -e "${CYAN}是否删除 AnyDesk 的所有设置和用户数据？${NC}"
                read -n1 -p "按回车键或 A 键确认删除，其他键保留: " del_data < /dev/tty
                echo
                if [[ -z "$del_data" || "$del_data" =~ [Aa] ]]; then
                    rm -rf "$data_dir" && echo -e "${GREEN}✓ 用户数据已删除${NC}"
                else
                    echo -e "${YELLOW}已保留用户数据。${NC}"
                fi
            else
                echo -e "${YELLOW}未找到用户数据目录，跳过。${NC}"
            fi

        else
            echo -e "${RED}✗ Flatpak 版本卸载失败${NC}"
        fi
    fi

    echo ""
    echo -e "${GREEN}✅ AnyDesk 卸载完成。${NC}"
}

install_todesk() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装ToDesk ════════════════${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  重要提示${NC}"
    echo "  官方未提供可直接安装的 ToDesk 包，现有方案依赖第三方维护的安装脚本"
    echo "  （todesk.lanbai.top → gitee.com/mclanbai/archtodesk）。"
    echo "  该第三方脚本会执行以下系统级改动："
    echo "    · sudo steamos-readonly disable  （解除 SteamOS 只读保护）"
    echo "    · sudo pacman-key --init / --populate  （重建 pacman 钥匙环）"
    echo "    · sudo pacman -S base-devel --noconfirm  （安装整个编译工具链，体积大）"
    echo "    · 卸载并重装 todesk / todesk-bin 包"
    echo "  另外该脚本内部把用户名硬编码为 /home/deck，非 deck 用户名的设备会出错。"
    echo ""
    echo -e "${CYAN}本工具不再自动执行该第三方脚本。${NC}"
    echo "  请二选一："
    echo "    A. 手动安装：先自行审阅脚本内容，再执行"
    echo "       curl -L todesk.lanbai.top | less     # 先看内容"
    echo "    B. 打开终端手动运行安装（执行前请确认已了解上述改动）"
    echo ""

    local ans
    if ! read -p "输入 y 在终端中打开第三方脚本（需自行确认风险），其他键取消: " -n 1 -r ans < /dev/tty; then
        echo ""
        echo "操作已取消。"
        return 0
    fi
    echo ""
    if [[ ! "$ans" =~ ^[Yy]$ ]]; then
        echo "操作已取消。"
        return 0
    fi

    # 用户明确确认后：先把脚本下载到本地供查看，再在可见的情况下执行
    local script_path="/tmp/steamdeck_toolbox_todesk_install.sh"
    if ! curl -fL --connect-timeout 20 --max-time 60 -o "$script_path" todesk.lanbai.top; then
        echo -e "${RED}✗ 下载安装脚本失败，请检查网络后重试。${NC}"
        rm -f "$script_path"
        return 1
    fi
    if [ ! -s "$script_path" ]; then
        echo -e "${RED}✗ 下载内容为空，已中止。${NC}"
        rm -f "$script_path"
        return 1
    fi
    if ! bash -n "$script_path" 2>/dev/null; then
        echo -e "${RED}✗ 下载的脚本存在语法错误，已中止执行。${NC}"
        echo -e "${YELLOW}  脚本已保留在 $script_path 供检查。${NC}"
        return 1
    fi

    echo -e "${CYAN}脚本已下载到 $script_path，内容如下（请确认无误后继续）：${NC}"
    echo "----------------------------------------"
    sed -n '1,80p' "$script_path"
    echo "----------------------------------------"
    local go
    if ! read -p "按回车键或 A 键执行该脚本，其他键取消: " -n 1 -r go < /dev/tty; then
        echo ""
        echo "操作已取消（脚本保留在 $script_path）。"
        return 0
    fi
    echo ""
    if [[ ! "$go" =~ ^[Aa]$ && -n "$go" ]]; then
        echo "操作已取消（脚本保留在 $script_path）。"
        return 0
    fi

    if bash "$script_path"; then
        echo -e "${GREEN}✓ ToDesk 安装脚本已执行完成${NC}"
    else
        echo -e "${RED}✗ ToDesk 安装脚本执行失败，请检查上方输出。${NC}"
        echo -e "${YELLOW}  脚本位置: $script_path${NC}"
        return 1
    fi
}

install_wps_office() { install_flatpak_app "WPS Office" "WPS Office" "Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"; }
install_qq() { install_flatpak_app "QQ" "QQ" "Network;Chat" "com.qq.QQ" "com.tencent.qq"; }
install_wechat() { install_flatpak_app "微信" "微信" "Network;Chat" "com.tencent.WeChat" "com.qq.weixin"; }
install_qqmusic() { install_flatpak_app "QQ音乐" "QQ音乐" "Audio" "com.qq.QQmusic" "com.tencent.QQmusic"; }
install_baidunetdisk() { install_flatpak_app "百度网盘" "百度网盘" "Network;FileTransfer" "com.baidu.NetDisk" "com.baidu.pan"; }
install_edge() { install_flatpak_app "Edge浏览器" "Microsoft Edge" "Network;WebBrowser" "com.microsoft.Edge"; }
install_chrome() { install_flatpak_app "Google浏览器" "Google Chrome" "Network;WebBrowser" "com.google.Chrome"; }

install_fcitx5() {
    if ! flatpak info org.fcitx.Fcitx5 &>/dev/null; then
        install_flatpak_app "Fcitx 5" "Fcitx 5" "Utility;Settings" "org.fcitx.Fcitx5"
    else
        echo -e "${GREEN}✓ Fcitx 5 主程序已安装${NC}"
    fi
    if ! flatpak info org.fcitx.Fcitx5.Addon.ChineseAddons &>/dev/null; then
        echo "正在安装中文输入法插件..."
        if flatpak install flathub org.fcitx.Fcitx5.Addon.ChineseAddons -y; then
            echo -e "${GREEN}✓ 中文插件安装完成${NC}"
        else
            echo -e "${RED}✗ 中文插件安装失败${NC}"
        fi
    else
        echo -e "${GREEN}✓ 中文插件已安装${NC}"
    fi
}
update_installed_apps() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 更新全部应用 ════════════════${NC}"
    if flatpak update -y; then
        echo -e "${GREEN}✓ 所有应用更新完成${NC}"
    else
        echo -e "${RED}✗ 更新失败，请检查网络或 flatpak 状态。${NC}"
        return 1
    fi
}

uninstall_wps_office() { uninstall_flatpak_app "WPS Office" "WPS Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"; }
uninstall_qq() { uninstall_flatpak_app "QQ" "QQ" "com.qq.QQ" "com.tencent.qq"; }
uninstall_wechat() { uninstall_flatpak_app "微信" "微信" "com.tencent.WeChat" "com.qq.weixin"; }
uninstall_qqmusic() { uninstall_flatpak_app "QQ音乐" "QQ音乐" "com.qq.QQmusic" "com.tencent.QQmusic"; }
uninstall_baidunetdisk() { uninstall_flatpak_app "百度网盘" "百度网盘" "com.baidu.NetDisk" "com.baidu.pan"; }
uninstall_edge() { uninstall_flatpak_app "Edge浏览器" "Microsoft Edge" "com.microsoft.Edge"; }
uninstall_chrome() { uninstall_flatpak_app "Google浏览器" "Google Chrome" "com.google.Chrome" "org.chromium.Chromium"; }
uninstall_fcitx5() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Fcitx 5 ════════════════${NC}"

    local MAIN_APP="org.fcitx.Fcitx5"
    local ADDON_APP="org.fcitx.Fcitx5.Addon.ChineseAddons"
    local DESKTOP_NAME="Fcitx 5"

    if ! flatpak info "$MAIN_APP" &>/dev/null; then
        echo -e "${YELLOW}未检测到已安装的 Fcitx 5 主程序。${NC}"
        if flatpak info "$ADDON_APP" &>/dev/null; then
            echo -e "${CYAN}检测到中文插件已安装但主程序缺失，是否只卸载插件？${NC}"
            read -n1 -p "按回车键或 A 键确认卸载插件，其他键取消: " confirm < /dev/tty
            echo
            if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
                flatpak uninstall "$ADDON_APP" -y 2>/dev/null && echo -e "${GREEN}✓ 中文插件已卸载${NC}"
            else
                echo "取消操作。"
            fi
        fi
        return 0
    fi

    echo -e "${CYAN}检测到 Fcitx 5 主程序已安装。${NC}"
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "开始卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    if flatpak info "$ADDON_APP" &>/dev/null; then
        echo "正在卸载中文插件..."
        flatpak uninstall "$ADDON_APP" -y 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 中文插件已卸载${NC}"
        else
            echo -e "${YELLOW}⚠️  中文插件卸载失败（可能已被移除）${NC}"
        fi
    else
        echo -e "${YELLOW}中文插件未安装，跳过。${NC}"
    fi

    echo "正在卸载 Fcitx 5 主程序..."
    flatpak uninstall "$MAIN_APP" -y 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Fcitx 5 主程序已卸载${NC}"
    else
        echo -e "${RED}✗ 主程序卸载失败，请检查 flatpak 状态。${NC}"
        return 1
    fi

    local desktop_dir="$HOME/Desktop"
    if [ -d "$desktop_dir" ]; then
        for f in "$desktop_dir/Fcitx 5.desktop" "$desktop_dir/org.fcitx.Fcitx5.desktop"; do
            if [ -f "$f" ]; then
                rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ 已删除桌面快捷方式 $(basename "$f")${NC}"
            fi
        done
        find "$desktop_dir" -maxdepth 1 -name "*Fcitx*" -name "*.desktop" -exec rm -f {} \; 2>/dev/null
    fi

    echo ""
    echo -e "${GREEN}✅ Fcitx 5 及其相关组件已卸载完成。${NC}"
}

uninstall_other_flatpak_apps() {
    if ! command -v zenity &>/dev/null; then
        echo "未找到 zenity，请在桌面环境运行。"
        return 1
    fi

    local exclude_ids=(
        "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"
        "com.qq.QQ" "com.tencent.qq"
        "com.tencent.WeChat" "com.qq.weixin"
        "com.qq.QQmusic" "com.tencent.QQmusic"
        "com.baidu.NetDisk" "com.baidu.pan"
        "com.microsoft.Edge"
        "com.google.Chrome" "org.chromium.Chromium"
        "org.fcitx.Fcitx5" "org.fcitx.Fcitx5.Addon.ChineseAddons"
    )

    _remove_shortcut() {
        local app_id="$1"
        local desktop_dir="$HOME/Desktop"
        [ -d "$desktop_dir" ] || return
        local id_us="${app_id//./_}"
        for f in "$desktop_dir"/*.desktop; do
            [ -e "$f" ] || continue
            local base=$(basename "$f")
            # 只匹配文件名恰好等于应用 ID 的快捷方式（点/下划线两种写法），
            # 不做子串匹配，避免误删无关 .desktop
            if [ "$base" = "${app_id}.desktop" ] || [ "$base" = "${id_us}.desktop" ]; then
                rm -f "$f" 2>/dev/null && echo "已删除桌面快捷方式 $base"
            fi
        done
    }

    while true; do
        local installed_apps=()
        while IFS=$'\t' read -r app_id app_name; do
            local skip=0
            for exclude in "${exclude_ids[@]}"; do
                if [[ "$app_id" == "$exclude" ]]; then
                    skip=1
                    break
                fi
            done
            if [ $skip -eq 0 ]; then
                installed_apps+=("$app_id|$app_name")
            fi
        done < <(flatpak list --app --columns=application,name 2>/dev/null)

        if [ ${#installed_apps[@]} -eq 0 ]; then
            zenity --info --text="没有其他已安装的 Flatpak 应用可卸载。" --width=400
            break
        fi

        local list_data=()
        for entry in "${installed_apps[@]}"; do
            IFS='|' read -r app_id app_name <<< "$entry"
            list_data+=("FALSE" "$app_name ($app_id)")
        done

        local selections
        selections=$(zenity --list --checklist \
            --title="卸载其他 Flatpak 应用" \
            --text="请选择要卸载的应用（可多选）：" \
            --column="选择" --column="应用" \
            "${list_data[@]}" \
            --width=700 --height=400 \
            --multiple 2>/dev/null)

        if [ $? -ne 0 ] || [ -z "$selections" ]; then
            break
        fi

        IFS='|' read -r -a selected_names <<< "$selections"
        local selected_ids=()
        for selected in "${selected_names[@]}"; do
            for entry in "${installed_apps[@]}"; do
                IFS='|' read -r app_id app_name <<< "$entry"
                if [ "$app_name ($app_id)" = "$selected" ]; then
                    selected_ids+=("$app_id")
                    break
                fi
            done
        done

        [ ${#selected_ids[@]} -eq 0 ] && continue

        zenity --question \
            --text="确定要卸载选中的应用吗？\n共 ${#selected_ids[@]} 项。" \
            --ok-label="卸载" --cancel-label="取消" 2>/dev/null || continue

        local total=${#selected_ids[@]}
        local success=0
        local fail=0
        local failed_list=""
        local data_dirs=()

        local pipe="/tmp/zenity_pipe_$$"
        mkfifo "$pipe"
        zenity --progress --pulsate --no-cancel --auto-close \
            --title="卸载应用" --text="准备开始..." --width=500 < "$pipe" &
        local zenity_pid=$!
        exec 3> "$pipe"

        for i in "${!selected_ids[@]}"; do
            local app_id="${selected_ids[$i]}"
            local idx=$((i+1))

            echo "# 正在处理第 $idx/$total 个: $app_id (卸载中...)" >&3

            if flatpak uninstall "$app_id" -y &>/dev/null; then
                ((success++))
                _remove_shortcut "$app_id"
                local data_dir="$HOME/.var/app/$app_id"
                if [ -d "$data_dir" ]; then
                    data_dirs+=("$data_dir")
                fi
                echo "# 第 $idx/$total 个: $app_id 卸载成功" >&3
            else
                ((fail++))
                failed_list+=" $app_id"
                echo "# 第 $idx/$total 个: $app_id 卸载失败" >&3
            fi
            sleep 0.2
        done

        exec 3>&-
        wait $zenity_pid 2>/dev/null
        rm -f "$pipe"

        sleep 1.0

        local result_msg="卸载结果：\n成功: $success 个"
        if [ $fail -gt 0 ]; then
            result_msg+="\n失败: $fail 个\n失败的 ID:${failed_list}"
        fi

        if [ ${#data_dirs[@]} -gt 0 ]; then
            local question_msg="$result_msg\n\n以下应用的用户数据目录仍然存在："
            for d in "${data_dirs[@]}"; do
                question_msg+="\n  $d"
            done
            question_msg+="\n\n是否删除这些数据目录？"

            if zenity --question --text="$question_msg" --width=600 \
                --ok-label="删除数据" --cancel-label="保留" 2>/dev/null; then
                for d in "${data_dirs[@]}"; do
                    rm -rf "$d" && echo "已删除 $d"
                done
            else
                :
            fi
            continue
        else
            zenity --info --text="$result_msg" --width=400 2>/dev/null
            continue
        fi
    done
}

install_yellow_duck_software() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装小黄鸭软件 ════════════════${NC}"
    echo ""
    local LOSS_DIR="$HOME/.local/share/Steam/steamapps/common/Lossless Scaling"
    if [[ -d "$LOSS_DIR" ]]; then
        echo -e "${CYAN}检测到已安装小黄鸭软件。${NC}"
        echo "   安装目录: $LOSS_DIR"
        echo ""
        read -p "是否要卸载已安装的小黄鸭软件？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "开始卸载小黄鸭软件..."
            if sudo rm -rf "$LOSS_DIR"; then
                echo -e "${GREEN}✅ 小黄鸭软件已成功卸载。${NC}"
                echo "如需重新安装，请再次运行此功能。"
            else
                echo -e "${RED}❌ 卸载失败，请检查权限。${NC}"
            fi
            return
        else
            echo "取消操作。"
            return
        fi
    fi

    echo -e "${CYAN}未检测到小黄鸭软件，开始从 Gitee 下载分卷文件...${NC}"
    local DOWNLOAD_DIR="/tmp/lossless_scaling_download"
    rm -rf "$DOWNLOAD_DIR"
    mkdir -p "$DOWNLOAD_DIR"
    cd "$DOWNLOAD_DIR" || return

    local BASE_URL="https://gitee.com/Zhucy2100/app-backup/raw/master/Lossless%20Scaling/Lossless%20Scaling.zip"
    local failed=0
    for i in 001 002 003 004 005 006 007; do
        echo "正在下载 Lossless Scaling.zip.${i} ..."
        if ! curl -L --fail -o "Lossless Scaling.zip.${i}" "${BASE_URL}.${i}"; then
            echo -e "${RED}下载 Lossless Scaling.zip.${i} 失败。${NC}"
            failed=1
            break
        fi
    done

    if [ $failed -ne 0 ]; then
        echo -e "${RED}下载失败，请检查网络。${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return
    fi

    echo "合并分卷文件并解压..."
    cat "Lossless Scaling.zip".* > Lossless-Scaling-Combined.zip
    unzip -o Lossless-Scaling-Combined.zip -d "$HOME/.local/share/Steam/steamapps/common/"
    if [ $? -ne 0 ]; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return
    fi

    sudo chown -R "${CURRENT_USER}:${CURRENT_GROUP}" "$HOME/.local/share/Steam/steamapps/common/Lossless Scaling"
    rm -rf "$DOWNLOAD_DIR"
    echo -e "${GREEN}✅ 小黄鸭软件安装完成！${NC}"
}

extract_exe_icon() {
    local exe_path="$1"
    local out_dir stem
    out_dir="$(dirname "$exe_path")"
    stem="$(basename "$exe_path")"
    stem="${stem%.*}"

    python3 - "$exe_path" "$out_dir" "$stem" <<'PYEOF'
import struct, sys, os

RT_ICON = 3
RT_GROUP_ICON = 14

def u16(b, o): return struct.unpack_from('<H', b, o)[0]
def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def parse_pe(data):
    if data[:2] != b'MZ':
        raise ValueError('not a PE file')
    pe_off = u32(data, 0x3C)
    if data[pe_off:pe_off+4] != b'PE\0\0':
        raise ValueError('bad PE signature')
    num_sections = u16(data, pe_off + 6)
    opt_off = pe_off + 24
    magic = u16(data, opt_off)
    if magic == 0x10B:
        dd_off = opt_off + 96
        sec_off = opt_off + 224
    elif magic == 0x20B:
        dd_off = opt_off + 112
        sec_off = opt_off + 240
    else:
        raise ValueError('bad magic')
    res_rva = u32(data, dd_off + 16)
    sections = []
    for i in range(num_sections):
        s = sec_off + i * 40
        vaddr = u32(data, s + 12)
        vsize = u32(data, s + 8)
        roff = u32(data, s + 20)
        rsize = u32(data, s + 16)
        sections.append((vaddr, vsize, roff, rsize))
    return res_rva, sections

def rva_to_off(rva, sections):
    for vaddr, vsize, roff, rsize in sections:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return roff + (rva - vaddr)
    raise ValueError('rva not found')

def read_res_dir(data, base_off, off, depth=0):
    if depth > 5:
        return []
    n_named = u16(data, off + 12)
    n_id = u16(data, off + 14)
    entries = []
    for i in range(n_named + n_id):
        e = off + 16 + i * 8
        name_id = u32(data, e)
        offset_to_data = u32(data, e + 4)
        if name_id & 0x80000000:
            name_off = base_off + (name_id & 0x7FFFFFFF)
            nchars = u16(data, name_off)
            name = data[name_off+2:name_off+2+nchars*2].decode('utf-16-le', 'replace')
        else:
            name = str(name_id)
        if offset_to_data & 0x80000000:
            sub = base_off + (offset_to_data & 0x7FFFFFFF)
            entries.append((name, read_res_dir(data, base_off, sub, depth+1)))
        else:
            de = base_off + offset_to_data
            entries.append((name, (u32(data, de), u32(data, de+4))))
    return entries

def read_blob(rva, size, data, sections):
    off = rva_to_off(rva, sections)
    return data[off:off+size]

def collect(tree, type_id, data, sections):
    out = {}
    for t, children in tree:
        if t != str(type_id):
            continue
        for name, val in children:
            if isinstance(val, tuple):
                rva, size = val
                out[name] = read_blob(rva, size, data, sections)
            else:
                for name2, val2 in val:
                    if isinstance(val2, tuple):
                        rva, size = val2
                        out[name + '/' + name2] = read_blob(rva, size, data, sections)
    return out

def main():
    path, out_dir, stem = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(path, 'rb') as f:
        data = f.read()
    res_rva, sections = parse_pe(data)
    base_off = rva_to_off(res_rva, sections)
    tree = read_res_dir(data, base_off, base_off)
    icons = collect(tree, RT_ICON, data, sections)
    groups = collect(tree, RT_GROUP_ICON, data, sections)
    if not groups:
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    gkey = sorted(groups)[0]
    g = groups[gkey]
    count = u16(g, 4)
    entries = []
    for i in range(count):
        e = 6 + i * 14
        w = g[e] or 256
        h = g[e+1] or 256
        colors = g[e+2]
        planes = u16(g, e+4)
        bpp = u16(g, e+6)
        icon_id = u16(g, e+12)
        blob = None
        for k, v in icons.items():
            if k == str(icon_id) or k.startswith(str(icon_id) + '/') or k.endswith('/' + str(icon_id)):
                blob = v
                break
        if blob is None:
            continue
        entries.append((w, h, colors, planes, bpp, blob))
    if not entries:
        sys.exit(1)
    n = len(entries)
    header = struct.pack('<HHH', 0, 1, n)
    dir_entries = b''
    blobs = b''
    offset = 6 + 16 * n
    for w, h, colors, planes, bpp, blob in entries:
        dir_entries += struct.pack('<BBBBHHII',
                                   w if w < 256 else 0,
                                   h if h < 256 else 0,
                                   colors, 0, planes, bpp, len(blob), offset)
        blobs += blob
        offset += len(blob)
    ico_path = os.path.join(out_dir, stem + '.ico')
    with open(ico_path, 'wb') as f:
        f.write(header + dir_entries + blobs)
    png_icons = [(k, v) for k, v in icons.items() if v[:8] == b'\x89PNG\r\n\x1a\n']
    if png_icons:
        best = max(png_icons, key=lambda kv: len(kv[1]))
        png_path = os.path.join(out_dir, stem + '.png')
        with open(png_path, 'wb') as f:
            f.write(best[1])
        print(png_path)
    else:
        print(ico_path)

try:
    main()
except Exception as e:
    print('图标提取失败: %s' % e, file=sys.stderr)
    sys.exit(1)
PYEOF

}

install_third_party_platform() {
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}═══════════ 安装第三方游戏平台 ═══════════${NC}"
        echo ""

        local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
        local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
        local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
        local ubisoft_installed=false
        local epic_installed=false
        local battle_installed=false
        [ -d "$UBISOFT_DIR" ] && ubisoft_installed=true
        [ -d "$EPIC_DIR" ] && epic_installed=true
        [ -d "$BATTLE_DIR" ] && battle_installed=true

        echo "当前状态："
        if $ubisoft_installed; then
            echo -e "  ${GREEN}✓ 育碧平台已安装${NC}"
        else
            echo -e "  ${YELLOW}✗ 育碧平台未安装${NC}"
        fi
        if $epic_installed; then
            echo -e "  ${GREEN}✓ Epic平台已安装${NC}"
        else
            echo -e "  ${YELLOW}✗ Epic平台未安装${NC}"
        fi
        if $battle_installed; then
            echo -e "  ${GREEN}✓ 战网平台已安装${NC}"
        else
            echo -e "  ${YELLOW}✗ 战网平台未安装${NC}"
        fi
        echo ""

        echo "请选择要安装的平台："
        echo "  1) 安装育碧平台"
        echo "  2) 安装Epic平台"
        echo "  3) 安装战网平台"
        read -p "请输入 [1-3]: " choice < /dev/tty
        case $choice in
            1) install_ubisoft; break ;;
            2) install_epic; break ;;
            3) install_battle_net; break ;;
            *) echo -e "${RED}无效选项 请重新输入${NC}"; sleep 0.5 ;;
        esac
    done
}

install_ubisoft() {
    local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
    if [ -d "$UBISOFT_DIR" ]; then
        echo -e "${GREEN}✓ 育碧平台已安装，无需重复操作。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在下载育碧安装程序...${NC}"
    cd "$HOME" || return
    rm -f UbisoftConnectInstaller.exe
    curl -# -L -o UbisoftConnectInstaller.exe "https://ubistatic3-a.akamaihd.net/orbit/launcher_installer/UbisoftConnectInstaller.exe"
    if [ $? -ne 0 ] || [ ! -f "UbisoftConnectInstaller.exe" ]; then
        echo -e "${RED}下载失败，请检查网络。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在通过 Proton Experimental 静默安装...${NC}"
    mkdir -p "$HOME/Applications/third-party-game-platform"

    export STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform"
    export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"

    local PROTON_BIN="$HOME/.steam/root/steamapps/common/Proton - Experimental/proton"
    if [ ! -x "$PROTON_BIN" ]; then
        echo -e "${RED}✗ 未找到 Proton Experimental 兼容层。${NC}"
        echo "   请先在 Steam 库 → 工具 中安装 Proton Experimental，然后重试。"
        return 1
    fi
    "$PROTON_BIN" waitforexitandrun \
        "$HOME/UbisoftConnectInstaller.exe" /S

    echo -e "${CYAN}等待安装完成...${NC}"
    local WAIT_TIME=0
    local MAX_WAIT=60
    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
        if [ -d "$UBISOFT_DIR" ]; then
            break
        fi
        sleep 2
        WAIT_TIME=$((WAIT_TIME + 2))
        echo -n "."
    done
    echo ""

    if [ -d "$UBISOFT_DIR" ]; then
        echo -e "${GREEN}✓ 育碧平台安装成功！${NC}"
        local EXE_PATH="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/UbisoftConnect.exe"

        echo -e "${CYAN}正在添加到 Steam 库...${NC}"
        steamos-add-to-steam "$EXE_PATH"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 已添加 Steam 快捷方式。${NC}"
            echo -e "${YELLOW}请手动在 Steam 库中为该快捷方式设置兼容层为 Proton Experimental。${NC}"
            echo -e "${YELLOW}或者点击桌面快捷方式运行。${NC}"
        else
            echo -e "${YELLOW}⚠️ 自动添加到 Steam 失败，请手动添加该 exe 文件。${NC}"
        fi

        local ICON_PATH=""
        echo -e "${CYAN}正在从 exe 提取图标...${NC}"
        ICON_PATH=$(extract_exe_icon "$EXE_PATH")
        if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
            echo -e "${GREEN}✓ 图标已提取: $ICON_PATH${NC}"
        else
            ICON_PATH="applications-games"
            echo -e "${YELLOW}⚠️ 图标提取失败，使用系统游戏图标。${NC}"
        fi

        local DESKTOP_FILE="$HOME/Desktop/Ubisoft Connect.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Ubisoft Connect
Comment=Ubisoft Game Launcher
Exec=env STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform" STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam" "$HOME/.steam/root/steamapps/common/Proton - Experimental/proton" waitforexitandrun "$EXE_PATH"
Icon=${ICON_PATH}
Terminal=false
Categories=Game;
EOF
        chmod +x "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已创建：~/Desktop/Ubisoft Connect.desktop${NC}"

        rm -f "$HOME/UbisoftConnectInstaller.exe"
    else
        echo -e "${RED}✗ 安装失败（超时），请检查 Proton 环境或日志。${NC}"
        echo -e "${YELLOW}安装程序保留在 $HOME/UbisoftConnectInstaller.exe，可手动运行。${NC}"
    fi
}

install_epic() {
    local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
    if [ -d "$EPIC_DIR" ]; then
        echo -e "${GREEN}✓ Epic平台已安装，无需重复操作。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在下载 Epic 安装程序...${NC}"
    cd "$HOME" || return
    rm -f EpicGamesLauncherInstaller.msi
    wget -O EpicGamesLauncherInstaller.msi "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi"
    if [ $? -ne 0 ] || [ ! -f "EpicGamesLauncherInstaller.msi" ]; then
        echo -e "${RED}下载失败，请检查网络。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在通过 Proton Experimental 静默安装...${NC}"
    mkdir -p "$HOME/Applications/third-party-game-platform"

    export STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform"
    export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"

    MSI_LOG="/tmp/epic_install_msi_$(date +%Y%m%d_%H%M%S).log"
    echo "安装日志将保存到: $MSI_LOG"

    local PROTON_BIN="$HOME/.steam/root/steamapps/common/Proton - Experimental/proton"
    if [ ! -x "$PROTON_BIN" ]; then
        echo -e "${RED}✗ 未找到 Proton Experimental 兼容层。${NC}"
        echo "   请先在 Steam 库 → 工具 中安装 Proton Experimental，然后重试。"
        return 1
    fi
    "$PROTON_BIN" waitforexitandrun \
        "$HOME/EpicGamesLauncherInstaller.msi" /quiet /log "$MSI_LOG"

    echo -e "${CYAN}等待安装完成...${NC}"
    local WAIT_TIME=0
    local MAX_WAIT=60
    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
        if [ -d "$EPIC_DIR" ]; then
            break
        fi
        sleep 2
        WAIT_TIME=$((WAIT_TIME + 2))
        echo -n "."
    done
    echo ""

    if [ -d "$EPIC_DIR" ]; then
        echo -e "${GREEN}✓ Epic平台安装成功！${NC}"
        local EXE_PATH="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games/Launcher/Portal/Binaries/Win64/EpicGamesLauncher.exe"

        echo -e "${CYAN}正在添加到 Steam 库...${NC}"
        steamos-add-to-steam "$EXE_PATH"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 已添加 Steam 快捷方式。${NC}"
            echo -e "${YELLOW}请手动在 Steam 库中为该快捷方式设置兼容层为 Proton Experimental。${NC}"
            echo -e "${YELLOW}或者点击桌面快捷方式运行。${NC}"
        else
            echo -e "${YELLOW}⚠️ 自动添加到 Steam 失败，请手动添加该 exe 文件。${NC}"
        fi

        local ICON_PATH=""
        echo -e "${CYAN}正在从 exe 提取图标...${NC}"
        ICON_PATH=$(extract_exe_icon "$EXE_PATH")
        if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
            echo -e "${GREEN}✓ 图标已提取: $ICON_PATH${NC}"
        else
            ICON_PATH="applications-games"
            echo -e "${YELLOW}⚠️ 图标提取失败，使用系统游戏图标。${NC}"
        fi

        local DESKTOP_FILE="$HOME/Desktop/Epic Games Launcher.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Epic Games Launcher
Comment=Epic Games Launcher
Exec=env STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform" STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam" "$HOME/.steam/root/steamapps/common/Proton - Experimental/proton" waitforexitandrun "$EXE_PATH"
Icon=${ICON_PATH}
Terminal=false
Categories=Game;
EOF
        chmod +x "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已创建：~/Desktop/Epic Games Launcher.desktop${NC}"

        rm -f "$HOME/EpicGamesLauncherInstaller.msi"
        rm -f "$MSI_LOG"
    else
        echo -e "${RED}✗ 安装失败（超时），请检查日志：${MSI_LOG}${NC}"
        echo -e "${YELLOW}安装程序保留在 $HOME/EpicGamesLauncherInstaller.msi，可手动运行。${NC}"
    fi
}

install_battle_net() {
    local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
    if [ -d "$BATTLE_DIR" ]; then
        echo -e "${GREEN}✓ 战网平台已安装，无需重复操作。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在从 Gitee Release 下载战网备份文件...${NC}"
    local DOWNLOAD_DIR="/tmp/battlenet_download"
    rm -rf "$DOWNLOAD_DIR"
    mkdir -p "$DOWNLOAD_DIR"
    cd "$DOWNLOAD_DIR" || return

    local BASE_URL="https://gitee.com/Zhucy2100/app-backup/releases/download/v1.0.0/Battle.net_backup.part"
    local files=("aa" "ab" "ac" "ad")
    local failed=0
    local CURL_UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    local CURL_REFERER="https://gitee.com/Zhucy2100/app-backup/releases"

    for part in "${files[@]}"; do
        echo "正在下载 Battle.net_backup.part_${part} ..."
        if ! curl -L --fail --retry 2 \
             -H "User-Agent: ${CURL_UA}" \
             -H "Referer: ${CURL_REFERER}" \
             -o "Battle.net_backup.part_${part}" "${BASE_URL}_${part}"; then
            echo -e "${RED}下载 Battle.net_backup.part_${part} 失败。${NC}"
            failed=1
            break
        fi
    done

    if [ $failed -ne 0 ]; then
        echo -e "${RED}下载失败，请检查网络。${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    echo "合并分卷文件..."
    cat Battle.net_backup.part_* > Battle.net_backup.tar.xz

    echo -e "${CYAN}正在解压到目标目录...${NC}"
    mkdir -p "$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)"
    if ! tar -xJf Battle.net_backup.tar.xz -C "$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    local EXE_PATH="$BATTLE_DIR/Battle.net Launcher.exe"
    if [ ! -f "$EXE_PATH" ]; then
        echo -e "${RED}错误: 解压后未找到 Battle.net Launcher.exe，安装失败。${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    echo -e "${CYAN}正在添加到 Steam 库...${NC}"
    steamos-add-to-steam "$EXE_PATH"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 已添加 Steam 快捷方式。${NC}"
        echo -e "${YELLOW}请手动在 Steam 库中为该快捷方式设置兼容层为 Proton Experimental。${NC}"
        echo -e "${YELLOW}或者点击桌面快捷方式运行。${NC}"
    else
        echo -e "${YELLOW}⚠️ 自动添加到 Steam 失败，请手动添加该 exe 文件。${NC}"
    fi

    local ICON_PATH=""
    echo -e "${CYAN}正在从 exe 提取图标...${NC}"
    ICON_PATH=$(extract_exe_icon "$EXE_PATH")
    if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
        echo -e "${GREEN}✓ 图标已提取: $ICON_PATH${NC}"
    else
        ICON_PATH="applications-games"
        echo -e "${YELLOW}⚠️ 图标提取失败，使用系统游戏图标。${NC}"
    fi

    local DESKTOP_FILE="$HOME/Desktop/Battle.net.desktop"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Battle.net
Comment=Blizzard Battle.net Launcher
Exec=env STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform" STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam" "$HOME/.steam/root/steamapps/common/Proton - Experimental/proton" waitforexitandrun "$EXE_PATH"
Icon=${ICON_PATH}
Terminal=false
Categories=Game;
EOF
        chmod +x "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已创建：~/Desktop/Battle.net.desktop${NC}"

    rm -rf "$DOWNLOAD_DIR"
    echo -e "${GREEN}✅ 战网平台安装完成！${NC}"
}

uninstall_third_party_platform() {
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}═══════════ 卸载第三方游戏平台 ═══════════${NC}"
        echo ""

        local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
        local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
        local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
        local ubisoft_installed=false
        local epic_installed=false
        local battle_installed=false
        [ -d "$UBISOFT_DIR" ] && ubisoft_installed=true
        [ -d "$EPIC_DIR" ] && epic_installed=true
        [ -d "$BATTLE_DIR" ] && battle_installed=true

        if ! $ubisoft_installed && ! $epic_installed && ! $battle_installed; then
            echo -e "${YELLOW}未检测到通过本程序安装的第三方游戏平台。${NC}"
            sleep 2
            return 0
        fi

        echo "当前已安装的平台："
        $ubisoft_installed && echo -e "  ${GREEN}✓ 育碧平台${NC}"
        $epic_installed && echo -e "  ${GREEN}✓ Epic平台${NC}"
        $battle_installed && echo -e "  ${GREEN}✓ 战网平台${NC}"
        echo ""

        echo "请选择要卸载的平台："
        echo "  1) 卸载育碧平台"
        echo "  2) 卸载Epic平台"
        echo "  3) 卸载战网平台"
        read -p "请输入 [1-3]: " choice < /dev/tty
        case $choice in
            1) uninstall_ubisoft; break ;;
            2) uninstall_epic; break ;;
            3) uninstall_battle_net; break ;;
            *) echo -e "${RED}无效选项 请重新输入${NC}"; sleep 0.5 ;;
        esac
    done
}

uninstall_ubisoft() {
    local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
    if [ ! -d "$UBISOFT_DIR" ]; then
        echo -e "${YELLOW}未检测到育碧平台，无需卸载。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在执行育碧官方卸载程序...${NC}"
    export STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform"
    export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"
    ~/.steam/root/steamapps/common/Proton\ -\ Experimental/proton waitforexitandrun \
        "$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/Uninstall.exe" /S
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 卸载程序执行成功，正在删除残留目录...${NC}"
        rm -rf "$UBISOFT_DIR"
        if [ ! -d "$UBISOFT_DIR" ]; then
            echo -e "${GREEN}✓ 育碧平台已成功卸载。${NC}"
        else
            echo -e "${YELLOW}⚠️ 残留目录删除失败，请手动删除：$UBISOFT_DIR${NC}"
        fi
    else
        echo -e "${RED}✗ 卸载程序执行失败，请尝试手动删除目录。${NC}"
    fi

    local DESKTOP_FILE="$HOME/Desktop/Ubisoft Connect.desktop"
    if [ -f "$DESKTOP_FILE" ]; then
        rm -f "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已删除：Ubisoft Connect.desktop${NC}"
    else
        echo -e "${YELLOW}未找到桌面快捷方式，跳过。${NC}"
    fi

    echo ""
    echo -e "${YELLOW}请手动在 Steam 库中删除对应的非 Steam 游戏快捷方式（右键→管理→从您的库中删除非 Steam 游戏）。${NC}"
}

uninstall_epic() {
    local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
    local EPIC_DIR_X86="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Epic Games"
    if [ ! -d "$EPIC_DIR" ] && [ ! -d "$EPIC_DIR_X86" ]; then
        echo -e "${YELLOW}未检测到 Epic 平台，无需卸载。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在删除 Epic 平台目录...${NC}"
    if [ -d "$EPIC_DIR" ]; then
        rm -rf "$EPIC_DIR"
        if [ ! -d "$EPIC_DIR" ]; then
            echo -e "${GREEN}✓ Epic 平台目录已删除: $EPIC_DIR${NC}"
        else
            echo -e "${RED}✗ 删除失败，请手动删除：$EPIC_DIR${NC}"
        fi
    fi

    if [ -d "$EPIC_DIR_X86" ]; then
        rm -rf "$EPIC_DIR_X86"
        if [ ! -d "$EPIC_DIR_X86" ]; then
            echo -e "${GREEN}✓ Epic 平台目录已删除: $EPIC_DIR_X86${NC}"
        else
            echo -e "${RED}✗ 删除失败，请手动删除：$EPIC_DIR_X86${NC}"
        fi
    fi

    local DESKTOP_FILE="$HOME/Desktop/Epic Games Launcher.desktop"
    if [ -f "$DESKTOP_FILE" ]; then
        rm -f "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已删除：Epic Games Launcher.desktop${NC}"
    else
        echo -e "${YELLOW}未找到桌面快捷方式，跳过。${NC}"
    fi

    echo ""
    echo -e "${YELLOW}请手动在 Steam 库中删除对应的非 Steam 游戏快捷方式（右键→管理→从您的库中删除非 Steam 游戏）。${NC}"
}

uninstall_battle_net() {
    local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
    if [ ! -d "$BATTLE_DIR" ]; then
        echo -e "${YELLOW}未检测到战网平台，无需卸载。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在删除战网平台目录...${NC}"
    rm -rf "$BATTLE_DIR"
    if [ ! -d "$BATTLE_DIR" ]; then
        echo -e "${GREEN}✓ 战网平台已成功卸载。${NC}"
    else
        echo -e "${RED}✗ 删除失败，请手动删除：$BATTLE_DIR${NC}"
    fi

    local DESKTOP_FILE="$HOME/Desktop/Battle.net.desktop"
    if [ -f "$DESKTOP_FILE" ]; then
        rm -f "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已删除：Battle.net.desktop${NC}"
    else
        echo -e "${YELLOW}未找到桌面快捷方式，跳过。${NC}"
    fi

    echo ""
    echo -e "${YELLOW}请手动在 Steam 库中删除对应的非 Steam 游戏快捷方式（右键→管理→从您的库中删除非 Steam 游戏）。${NC}"
}

if [ -n "${1:-}" ] && declare -f "$1" > /dev/null; then
    "$@"
else
    echo "此脚本为内嵌库，请通过参数调用具体功能。"
fi
'''

# ============================================================================
# Python GUI
# ============================================================================
def create_temp_script(extra_content=''):
    fd, path = tempfile.mkstemp(suffix='.sh')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(BASH_SCRIPT)
        if extra_content:
            f.write('\n' + extra_content + '\n')
    os.chmod(path, 0o755)
    atexit.register(lambda: os.path.exists(path) and os.unlink(path))
    return path

class TaskWindow(Gtk.Window):
    def __init__(self, parent, func_key, display_name):
        super().__init__(title=f"执行任务: {display_name}")
        self.set_default_size(760, 520)
        task_header = Gtk.HeaderBar()
        task_header.set_show_close_button(True)
        task_header.props.title = display_name
        task_header.props.subtitle = "任务运行中"
        # HeaderBar 默认只画「关闭」一个按钮，最小化/最大化按钮要自己加
        # （gtk-decoration-layout 只对系统原生装饰生效，对自定义 HeaderBar 无效）
        self._max_btn = Gtk.Button()
        self._max_btn.set_relief(Gtk.ReliefStyle.NONE)
        self._max_btn.set_tooltip_text("最大化 / 还原")
        self._max_btn_image = Gtk.Image.new_from_icon_name(
            "window-maximize-symbolic", Gtk.IconSize.BUTTON)
        self._max_btn.add(self._max_btn_image)
        self._max_btn.connect("clicked", self._on_maximize_clicked)
        task_header.pack_end(self._max_btn)
        self.set_titlebar(task_header)
        self._task_header = task_header
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_transient_for(parent)
        # 不再设 modal：模态窗口在部分窗口管理器下会被限制尺寸/无法最大化，
        # 而任务窗口本质是独立终端，用户需要能自由缩放、切到别的窗口复制内容。
        self.set_modal(False)
        self.set_resizable(True)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.terminal = None
        self.completed = False
        self.temp_script = None
        self._force_closing = False
        self.use_external_terminal = not VTE_AVAILABLE
        self.child_pid = None
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)
        if self.use_external_terminal:
            label = Gtk.Label(label="任务已在外部终端中运行，请查看弹出的终端窗口。")
            label.set_margin_top(20)
            label.set_margin_bottom(20)
            vbox.pack_start(label, True, True, 0)
            self.action_btn = Gtk.Button(label="关闭")
            self.action_btn.connect("clicked", lambda btn: self.destroy())
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_margin_bottom(5)
            button_box.pack_start(Gtk.Label(), True, True, 0)
            button_box.pack_start(self.action_btn, False, False, 0)
            vbox.pack_start(button_box, False, False, 0)
            self.show_all()
            self.run_external(func_key)
        else:
            self.terminal = Vte.Terminal()
            self.terminal.set_vexpand(True)
            self.terminal.set_hexpand(True)
            self.terminal.set_scrollback_lines(10000)
            try:
                self.terminal.set_font(Pango.FontDescription("Monospace 11"))
            except Exception:
                pass
            try:
                fg = Gdk.RGBA(); fg.parse("#e6edf4")
                bg = Gdk.RGBA(); bg.parse("#0b1016")
                palette = []
                for hex_color in ("#1b2531", "#e05c5c", "#5cd07a", "#e0c05c",
                                  "#1a9fff", "#b48cff", "#5cc8d0", "#c7d5e0",
                                  "#3a4a5a", "#ff7a7a", "#7be89a", "#ffd97a",
                                  "#4fb8ff", "#c9a8ff", "#7fe0e8", "#ffffff"):
                    c = Gdk.RGBA(); c.parse(hex_color); palette.append(c)
                self.terminal.set_colors(fg, bg, palette)
            except Exception:
                pass
            term_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            term_frame.get_style_context().add_class("card")
            term_frame.set_margin_top(10); term_frame.set_margin_bottom(0); term_frame.set_margin_start(10); term_frame.set_margin_end(10)
            term_frame.pack_start(self.terminal, True, True, 0)
            vbox.pack_start(term_frame, True, True, 0)

            # 终端右键菜单：复制选中 / 复制全部输出 / 粘贴 / 全选
            self.terminal.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            self.terminal.connect("button-press-event", self._on_terminal_button_press)
            # 键盘快捷键：Ctrl+Shift+C 复制、Ctrl+Shift+V 粘贴、Ctrl+Shift+A 全选
            self.terminal.connect("key-press-event", self._on_terminal_key_press)

            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_margin_top(5)
            button_box.set_margin_bottom(5)
            button_box.set_margin_start(10)
            button_box.set_margin_end(10)
            self.timer_label = Gtk.Label(label="已运行 0:00")
            self.timer_label.set_name("task-timer")
            button_box.pack_start(self.timer_label, False, False, 0)
            button_box.pack_start(Gtk.Label(), True, True, 0)

            # 复制按钮：有选中内容时复制选中，否则复制全部输出
            self.copy_btn = Gtk.Button(label="复制")
            self.copy_btn.set_tooltip_text("复制选中的终端内容；未选中时复制全部输出")
            self.copy_btn.connect("clicked", self.on_copy_clicked)
            button_box.pack_start(self.copy_btn, False, False, 0)

            self.action_btn = Gtk.Button(label="取消")
            self.action_btn.connect("clicked", self.on_action_button_clicked)
            button_box.pack_start(self.action_btn, False, False, 0)
            vbox.pack_start(button_box, False, False, 0)
            self.temp_script = create_temp_script()
            self.start_time = time.time()
            self.connect("destroy", self.on_window_destroy)
            self.start_command(func_key)
            self.show_all()
            GLib.timeout_add_seconds(1, self._tick)

    # ------------------------------------------------------------------
    # 复制按钮 / 右键菜单入口
    # ------------------------------------------------------------------
    def _on_terminal_button_press(self, widget, event):
        # 右键（button 3）弹菜单
        if event.button == 3:
            return self._show_terminal_menu(widget, event)
        return False

    def on_copy_clicked(self, button):
        """有选中内容时复制选中，否则复制全部输出，并给出短时反馈。"""
        if self._terminal_has_selection():
            ok = self._copy_selection()
            msg = "已复制选中内容" if ok else "复制失败"
        else:
            ok = self._copy_all_output()
            msg = "已复制全部输出" if ok else "没有可复制的内容"
        self._flash_copy_button(msg)

    def _on_terminal_key_press(self, widget, event):
        """终端键盘快捷键。Ctrl+C 留给中断进程，复制用 Ctrl+Shift+C。"""
        try:
            state = event.state & Gtk.accelerator_get_default_mod_mask()
            ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
            shift = bool(state & Gdk.ModifierType.SHIFT_MASK)
            if not ctrl:
                return False
            key = Gdk.keyval_name(event.keyval) or ""
            key = key.lower()
            if shift and key == "c":
                self.on_copy_clicked(self.copy_btn)
                return True
            if shift and key == "v":
                self._paste_to_terminal()
                return True
            if shift and key == "a":
                if self.terminal:
                    self.terminal.select_all()
                return True
        except Exception as e:
            print(f"快捷键处理失败: {e}")
        return False

    def _flash_copy_button(self, msg):
        try:
            old = self.copy_btn.get_label()
            self.copy_btn.set_label(msg)
            def restore():
                try:
                    self.copy_btn.set_label(old if old else "复制")
                except Exception:
                    pass
                return False
            GLib.timeout_add(1500, restore)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 窗口最大化 / 还原
    # ------------------------------------------------------------------
    def _on_maximize_clicked(self, button):
        self.toggle_maximize()

    def toggle_maximize(self):
        """最大化 / 还原窗口，并同步按钮图标。"""
        try:
            if self.is_maximized():
                self.unmaximize()
                icon = "window-maximize-symbolic"
            else:
                self.maximize()
                icon = "window-restore-symbolic"
            self._max_btn_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)
        except Exception as e:
            print(f"窗口最大化切换失败: {e}")

    # ------------------------------------------------------------------
    # 终端复制 / 粘贴
    # ------------------------------------------------------------------
    def _terminal_has_selection(self):
        try:
            return bool(self.terminal and self.terminal.get_has_selection())
        except Exception:
            return False

    def _copy_selection(self):
        """复制终端中选中的文本到剪贴板。"""
        if not self.terminal:
            return False
        try:
            if not self.terminal.get_has_selection():
                return False
            self.terminal.copy_clipboard_format(Vte.Format.TEXT)
            return True
        except Exception:
            try:
                self.terminal.copy_clipboard()
                return True
            except Exception as e:
                print(f"复制失败: {e}")
                return False

    def _copy_all_output(self):
        """复制终端全部内容（含滚动回看）到剪贴板。"""
        if not self.terminal:
            return False
        text = ""
        # get_text_range_format 返回 (文本, 属性数组) 元组，不是字符串，要取第 0 项
        try:
            if hasattr(self.terminal, "get_text_range_format"):
                result = self.terminal.get_text_range_format(Vte.Format.TEXT, 0, 0, -1, -1)
                if isinstance(result, (tuple, list)) and result:
                    text = result[0] or ""
                elif isinstance(result, str):
                    text = result
        except Exception as e:
            print(f"get_text_range_format 失败: {e}")
            text = ""
        if not text:
            # 兜底：全选后取选中文本
            try:
                self.terminal.select_all()
                text = self.terminal.get_text_selected(Vte.Format.TEXT) or ""
            except Exception as e:
                print(f"读取终端内容失败: {e}")
                text = ""
        if not text:
            return False
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text, -1)
            clipboard.store()
            return True
        except Exception as e:
            print(f"写入剪贴板失败: {e}")
            return False

    def _paste_to_terminal(self):
        if not self.terminal:
            return
        try:
            self.terminal.paste_clipboard()
        except Exception as e:
            print(f"粘贴失败: {e}")

    def _show_terminal_menu(self, terminal, event):
        """终端右键菜单：复制选中 / 复制全部输出 / 粘贴 / 全选。"""
        menu = Gtk.Menu()
        has_sel = self._terminal_has_selection()

        item_copy = Gtk.MenuItem(label="复制选中内容")
        item_copy.set_sensitive(has_sel)
        item_copy.connect("activate", lambda *_: self._copy_selection())
        menu.append(item_copy)

        item_copy_all = Gtk.MenuItem(label="复制全部输出")
        item_copy_all.connect("activate", lambda *_: self._copy_all_output())
        menu.append(item_copy_all)

        item_paste = Gtk.MenuItem(label="粘贴")
        item_paste.connect("activate", lambda *_: self._paste_to_terminal())
        menu.append(item_paste)

        menu.append(Gtk.SeparatorMenuItem())

        item_sel_all = Gtk.MenuItem(label="全选")
        item_sel_all.connect("activate", lambda *_: self.terminal.select_all())
        menu.append(item_sel_all)

        menu.show_all()
        # popup_at_pointer 需要真实的事件窗口；用 GTK3.22+ 时优先用它，
        # 失败则退回传统 popup（部分 WM/合成事件下事件窗口为空会触发断言）
        try:
            menu.popup_at_pointer(event)
        except Exception:
            try:
                menu.popup(None, None, None, None, event.button if event else 0,
                           Gtk.get_current_event_time())
            except Exception as e:
                print(f"右键菜单弹出失败: {e}")
                return False
        return True

    def run_external(self, func_key):
        tmp_path = create_temp_script()
        cmd = f"bash {tmp_path} {func_key}; read -p '按回车键关闭...' -n1"
        if not launch_terminal(cmd):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                                    text="未找到可用的终端模拟器")
            dlg.format_secondary_text("请安装 konsole 或 xterm 后重试。")
            dlg.run(); dlg.destroy()

    def start_command(self, func_key):
        ok, self.child_pid = self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.path.expanduser("~"),
            ["/bin/bash", self.temp_script, func_key],
            None,
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            None
        )
        if not ok or not self.child_pid:
            self.action_btn.set_label("启动失败")
            self.action_btn.set_sensitive(True)
            return
        self.terminal.connect("child-exited", self.on_child_exited)

    def on_child_exited(self, terminal, status):
        GLib.idle_add(self.set_completed)

    def set_completed(self):
        self.completed = True
        self.action_btn.set_sensitive(True)
        self.action_btn.set_label("完成")
        try:
            self._task_header.props.subtitle = "任务已完成"
        except Exception:
            pass

    def _tick(self):
        if self.completed:
            return False
        elapsed = int(time.time() - self.start_time)
        m, s = divmod(elapsed, 60)
        self.timer_label.set_text(f"已运行 {m}:{s:02d}")
        return True

    def _kill_task(self):
        pid = getattr(self, 'child_pid', None)
        if not pid:
            return
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def on_action_button_clicked(self, button):
        if self.completed:
            self.destroy()
            return
        self._kill_task()
        self.action_btn.set_sensitive(False)
        self.action_btn.set_label("正在取消...")
        GLib.timeout_add(500, self.destroy)

    def force_kill(self):
        if not self.completed:
            self._kill_task()
        self.destroy()
        return False

    def on_window_destroy(self, widget):
        if self._force_closing:
            return
        if not self.completed:
            self._kill_task()
            GLib.timeout_add(500, self._force_close)

    def _force_close(self):
        self._force_closing = True
        self.destroy()
        return False

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Steam Deck 工具箱")
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(950, 620)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.system_type = self.detect_system_type()
        self.task_window = None

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Steam Deck 工具箱"
        header.props.subtitle = f"v{VERSION}  ·  {self.system_type}"
        self.set_titlebar(header)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("全局搜索功能...")
        self.search_entry.set_width_chars(20)
        self.search_entry.connect("search-changed", self.on_search_changed)
        header.pack_end(self.search_entry)

        # 主题切换按钮（深色 / 浅色 / 跟随系统）
        self.theme_button = Gtk.MenuButton()
        self.theme_button.set_tooltip_text("切换深色 / 浅色模式")
        self.theme_button.set_relief(Gtk.ReliefStyle.NONE)
        self._theme_icon = Gtk.Image.new_from_icon_name("weather-clear-night-symbolic",
                                                        Gtk.IconSize.BUTTON)
        self.theme_button.add(self._theme_icon)
        header.pack_end(self.theme_button)
        self._build_theme_menu()

        self._current_page = "func"

        self.icon_map = {
            "支持和维护": "pushpin.png", "更新日志": "clipboard_twemoji.png",
            "系统优化": "hammer_wrench.png", "软件安装": "package.png",
            "网络工具": "globe.png", "插件相关": "game_controller.png",
            "引导管理": "refresh.png", "更新和卸载软件": "inbox.png", "其他": "trash.png"
        }

        self.category_tree = {
            "支持和维护": [],
            "更新日志": [],
            "系统优化": [
                ("安装国内源", "install_chinese_source"),
                ("调整虚拟内存", "adjust_swap"),
                ("修复磁盘写入错误", "fix_disk_write_error"),
                ("清理hosts缓存", "clear_hosts_cache"),
                ("校准设备", [
                    ("校准摇杆", "calibrate_joystick_stick"),
                    ("校准扳机", "calibrate_joystick_trigger")
                ]),
                ("Steam缓存管理", "steamdeck_cache_manager"),
                ("GE-Proton 管理", "ge_proton_manager")
            ],
            "软件安装": [
                ("AnyDesk", "install_anydesk"),
                ("ToDesk", "install_todesk"),
                ("AskLink远程", "install_asklink"),
                ("WPS Office", "install_wps_office"),
                ("QQ", "install_qq"),
                ("微信", "install_wechat"),
                ("QQ音乐", "install_qqmusic"),
                ("百度网盘", "install_baidunetdisk"),
                ("Edge浏览器", "install_edge"),
                ("Google浏览器", "install_chrome"),
                ("Fcitx 5", "install_fcitx5")
            ],
            "网络工具": [
                ("UU加速器插件", "install_uu_accelerator"),
                ("迅游加速器插件", "install_xunyou_accelerator"),
                ("奇游联机宝加速插件", "install_qiyou_accelerator"),
                ("Watt Toolkit (Steam++)", [
                    ("安装", "watt_toolkit_install"),
                    ("卸载", "watt_toolkit_uninstall")
                ])
            ],
            "插件相关": [
                ("安装/卸载插件商店", [
                    ("安装插件商店", "install_plugin_store"),
                    ("卸载插件商店", "uninstall_plugin_store")
                ]),
                ("ToMoon 插件", [
                    ("安装/更新 ToMoon", "install_tomoon_install"),
                    ("卸载 ToMoon", "install_tomoon_uninstall")
                ]),
                ("Freedeck 插件", [
                    ("安装/更新 Freedeck", "install_freedeck_install"),
                    ("卸载 Freedeck", "install_freedeck_uninstall")
                ]),
                ("LSFG-VK插件", [
                    ("安装/更新 LSFG-VK", "install_decky_lsfg_vk_install"),
                    ("卸载 LSFG-VK", "install_decky_lsfg_vk_uninstall")
                ]),
                ("Framegen插件", [
                    ("安装/更新 Framegen", "install_decky_framegen_install"),
                    ("卸载 Framegen", "install_decky_framegen_uninstall")
                ])
            ],
            "引导管理": [
                ("安装/重装 Clover", "clover_install_or_reinstall")
            ],
            "更新和卸载软件": [
                ("更新已安装应用", "update_installed_apps"),
                ("卸载已安装应用", [
                    ("卸载 WPS Office", "uninstall_wps_office"),
                    ("卸载 QQ", "uninstall_qq"),
                    ("卸载微信", "uninstall_wechat"),
                    ("卸载 QQ音乐", "uninstall_qqmusic"),
                    ("卸载百度网盘", "uninstall_baidunetdisk"),
                    ("卸载 Edge浏览器", "uninstall_edge"),
                    ("卸载 Google浏览器", "uninstall_chrome"),
                    ("卸载 AnyDesk", "uninstall_anydesk"),
                    ("卸载Fcitx 5", "uninstall_fcitx5"),
                    ("卸载其他已安装应用", "uninstall_other_flatpak_apps")
                ])
            ],
            "其他": [
                ("小黄鸭软件", "install_yellow_duck_software"),
                ("安装/卸载第三方游戏平台", [
                    ("安装第三方游戏平台", "install_third_party_platform"),
                    ("卸载第三方游戏平台", "uninstall_third_party_platform")
                ])
            ]
        }

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.set_vexpand(True)
        main_vbox.pack_start(hbox, True, True, 0)

        self.list_store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.category_icons = {}
        for cat in self.category_tree.keys():
            icon_file = self.icon_map.get(cat)
            pixbuf = load_icon_pixbuf(icon_file, 28) if icon_file else None
            self.list_store.append([pixbuf, cat])
            self.category_icons[cat] = pixbuf

        self.cat_view = Gtk.TreeView(model=self.list_store)
        self.cat_view.set_name("sidebar")
        col = Gtk.TreeViewColumn()
        col.set_spacing(10)
        renderer_icon = Gtk.CellRendererPixbuf(); col.pack_start(renderer_icon, False); col.add_attribute(renderer_icon, "pixbuf", 0)
        renderer_text = Gtk.CellRendererText(); renderer_text.set_property("ypad", 9); col.pack_start(renderer_text, True); col.add_attribute(renderer_text, "text", 1)
        self.cat_view.append_column(col)
        self.cat_view.set_activate_on_single_click(True)
        self.cat_view.connect("row-activated", self.on_category_activated)
        scrolled_left = Gtk.ScrolledWindow(); scrolled_left.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC); scrolled_left.set_vexpand(True); scrolled_left.set_valign(Gtk.Align.FILL); scrolled_left.add(self.cat_view)

        sidebar_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        sidebar_header.set_name("sidebar-header")
        sidebar_icon = Gtk.Image.new_from_icon_name("input-gamepad-symbolic", Gtk.IconSize.BUTTON)
        sidebar_title = Gtk.Label(label="功能分类"); sidebar_title.set_halign(Gtk.Align.START)
        sidebar_header.pack_start(sidebar_icon, False, False, 0)
        sidebar_header.pack_start(sidebar_title, False, False, 0)

        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        left_panel.set_size_request(258, -1)
        left_panel.pack_start(sidebar_header, False, False, 0)
        left_panel.pack_start(scrolled_left, True, True, 0)
        hbox.pack_start(left_panel, False, True, 0)

        self.stack = Gtk.Stack(); self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE); self.stack.set_vexpand(True); self.stack.set_valign(Gtk.Align.FILL)
        hbox.pack_start(self.stack, True, True, 0)

        # About page
        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        about_box.set_margin_top(20); about_box.set_margin_bottom(20); about_box.set_margin_start(20); about_box.set_margin_end(20)
        about_title = Gtk.Label(); about_title.set_name("page-title"); about_title.set_markup("<big><b>关于本工具</b></big>"); about_title.set_halign(Gtk.Align.START)
        about_box.pack_start(about_title, False, False, 0)
        about_textview = Gtk.TextView(); about_textview.set_editable(False); about_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        about_textview.set_left_margin(16); about_textview.set_right_margin(16); about_textview.set_top_margin(14); about_textview.set_bottom_margin(14)
        about_textview.get_style_context().add_class("card")
        about_text = f"""
steamdeck工具箱 v{VERSION}
制作人：薯条 & DeepSeek
发布日期：2026年1月1日
工具箱介绍：这是一个专为 Steam Deck 设计的工具箱，集成了系统优化、软件安装、网络工具等多种功能。
使用说明：点击左侧分类查看功能；顶部搜索框可跨分类查找；点击功能将弹出独立任务窗口。
https://gitee.com/Zhucy2100/steamdeck_toolbox
"""
        about_textview.get_buffer().set_text(about_text)
        scrolled_about = Gtk.ScrolledWindow(); scrolled_about.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC); scrolled_about.set_vexpand(True); scrolled_about.add(about_textview)
        about_box.pack_start(scrolled_about, True, True, 0)
        self.stack.add_named(about_box, "about")

        changelog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        changelog_box.set_margin_top(20); changelog_box.set_margin_bottom(20); changelog_box.set_margin_start(20); changelog_box.set_margin_end(20)
        changelog_title = Gtk.Label(); changelog_title.set_name("page-title"); changelog_title.set_markup("<big><b>更新日志</b></big>"); changelog_title.set_halign(Gtk.Align.START)
        changelog_box.pack_start(changelog_title, False, False, 0)
        self.changelog_textview = Gtk.TextView(); self.changelog_textview.set_editable(False); self.changelog_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.changelog_textview.set_cursor_visible(False)
        self.changelog_textview.set_left_margin(16); self.changelog_textview.set_right_margin(16); self.changelog_textview.set_top_margin(14); self.changelog_textview.set_bottom_margin(14)
        self.changelog_textview.get_style_context().add_class("card")
        css_provider = Gtk.CssProvider(); css_provider.load_from_data(b'textview { font: 10pt Monospace; }')
        self.changelog_textview.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        scrolled_changelog = Gtk.ScrolledWindow(); scrolled_changelog.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC); scrolled_changelog.set_vexpand(True); scrolled_changelog.add(self.changelog_textview)
        changelog_box.pack_start(scrolled_changelog, True, True, 0)
        self.stack.add_named(changelog_box, "changelog")

        func_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        func_page.set_margin_top(20); func_page.set_margin_bottom(20); func_page.set_margin_start(20); func_page.set_margin_end(20)
        func_page.set_vexpand(True); func_page.set_valign(Gtk.Align.FILL)
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); title_box.set_halign(Gtk.Align.START)
        self.title_icon = Gtk.Image(); self.title_icon.set_visible(False); title_box.pack_start(self.title_icon, False, False, 0)
        self.category_title = Gtk.Label(); self.category_title.set_name("page-title"); self.category_title.set_visible(False); title_box.pack_start(self.category_title, False, False, 0)
        func_page.pack_start(title_box, False, False, 0)

        self.func_store = Gtk.TreeStore(str)
        self.func_view = Gtk.TreeView(model=self.func_store)
        self.func_view.set_name("func-list")
        func_col = Gtk.TreeViewColumn(); renderer_func = Gtk.CellRendererText(); renderer_func.set_property("ypad", 10); func_col.pack_start(renderer_func, True); func_col.add_attribute(renderer_func, "text", 0)
        self.func_view.append_column(func_col); self.func_view.set_headers_visible(False); self.func_view.set_activate_on_single_click(True); self.func_view.connect("row-activated", self.on_func_row_activated); self.func_view.set_expander_column(func_col)
        scrolled_func = Gtk.ScrolledWindow(); scrolled_func.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); scrolled_func.set_vexpand(True); scrolled_func.set_valign(Gtk.Align.FILL); scrolled_func.add(self.func_view)
        scrolled_func.get_style_context().add_class("card")
        func_page.pack_start(scrolled_func, True, True, 0)
        self.stack.add_named(func_page, "func")

        # 全局搜索结果页
        search_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        search_page.set_margin_top(20); search_page.set_margin_bottom(20); search_page.set_margin_start(20); search_page.set_margin_end(20)
        search_page.set_vexpand(True); search_page.set_valign(Gtk.Align.FILL)
        self.search_title = Gtk.Label(label=""); self.search_title.set_name("page-title"); self.search_title.set_halign(Gtk.Align.START)
        search_page.pack_start(self.search_title, False, False, 0)
        self.search_store = Gtk.ListStore(str, str, str)
        self.search_view = Gtk.TreeView(model=self.search_store)
        self.search_view.set_name("func-list")
        col_name = Gtk.TreeViewColumn("功能"); r_name = Gtk.CellRendererText(); r_name.set_property("ypad", 9); col_name.pack_start(r_name, True); col_name.add_attribute(r_name, "text", 0)
        col_cat = Gtk.TreeViewColumn("分类"); r_cat = Gtk.CellRendererText(); r_cat.set_property("ypad", 9); col_cat.pack_start(r_cat, True); col_cat.add_attribute(r_cat, "text", 1)
        self.search_view.append_column(col_name); self.search_view.append_column(col_cat)
        self.search_view.set_headers_visible(True)
        self.search_view.set_activate_on_single_click(True)
        self.search_view.connect("row-activated", self.on_search_row_activated)
        scrolled_search = Gtk.ScrolledWindow(); scrolled_search.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); scrolled_search.set_vexpand(True); scrolled_search.set_valign(Gtk.Align.FILL); scrolled_search.add(self.search_view)
        scrolled_search.get_style_context().add_class("card")
        search_page.pack_start(scrolled_search, True, True, 0)
        self.stack.add_named(search_page, "search")

        selection = self.cat_view.get_selection()
        first_path = Gtk.TreePath.new_first(); selection.select_path(first_path)
        self.on_category_activated(self.cat_view, first_path, None)

        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10); bottom_bar.set_name("bottom-bar")
        self.status_label = Gtk.Label(label="")
        self.status_label.set_name("status-label")
        bottom_bar.pack_start(self.status_label, False, False, 0)
        bottom_bar.pack_start(Gtk.Label(), True, True, 0)
        help_btn = Gtk.Button(label="帮助"); help_btn.get_style_context().add_class("suggested-action"); help_btn.connect("clicked", self.on_help_clicked); bottom_bar.pack_start(help_btn, False, False, 0)
        quit_btn = Gtk.Button(label="退出"); quit_btn.get_style_context().add_class("destructive-action"); quit_btn.connect("clicked", lambda b: self.destroy()); bottom_bar.pack_start(quit_btn, False, False, 0)
        main_vbox.pack_start(bottom_bar, False, False, 0)
        self.update_status()

        self.func_map = {}
        self.build_func_map()

    # ------------------------------------------------------------------
    # 主题切换
    # ------------------------------------------------------------------
    def _build_theme_menu(self):
        """构建主题下拉菜单（用 Popover，这样能跟随深色/浅色样式，原生 Gtk.Menu 无法着色）。"""
        current = load_theme_pref()
        popover = Gtk.Popover()
        popover.set_relative_to(self.theme_button)
        popover.set_position(Gtk.PositionType.BOTTOM)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_border_width(6)
        box.get_style_context().add_class("theme-popover")
        self._theme_items = {}
        # 不用 RadioMenuItem：原生单选圆点会和文字重叠。
        # 改为「图标 + 文字」的普通按钮行，选中项加 check 图标，样式完全可控。
        for mode in THEME_MODES:
            row = Gtk.Button()
            row.set_relief(Gtk.ReliefStyle.NONE)
            row.get_style_context().add_class("theme-row")
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            check = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.MENU)
            check.set_opacity(1.0 if mode == current else 0.0)
            hbox.pack_start(check, False, False, 0)
            lbl = Gtk.Label(label=THEME_LABELS[mode])
            hbox.pack_start(lbl, False, False, 0)
            row.add(hbox)
            row.connect("clicked", self.on_theme_row_clicked, mode)
            self._theme_items[mode] = (row, check)
            box.pack_start(row, False, False, 0)
        popover.add(box)
        box.show_all()
        self.theme_button.set_popover(popover)
        self._theme_menu = popover
        self._refresh_theme_icon(current)

    def _refresh_theme_icon(self, mode):
        """根据当前模式切换按钮图标。
        图标反映“点击后切换到的目标”更符合直觉，这里显示当前生效主题的图标。
        """
        resolved = resolve_theme_mode(mode)
        icons = {
            "dark": "weather-clear-night-symbolic",   # 深色 → 月亮
            "light": "weather-clear-symbolic",        # 浅色 → 太阳
        }
        name = icons.get(resolved, "weather-clear-night-symbolic")
        try:
            if self._theme_icon is not None:
                self._theme_icon.set_from_icon_name(name, Gtk.IconSize.BUTTON)
        except Exception:
            pass

    def on_theme_row_clicked(self, button, mode):
        """用户点击主题行：立即应用并保存。"""
        apply_app_css(mode)
        save_theme_pref(mode)
        self._refresh_theme_icon(mode)
        # 更新选中标记
        for m, (_row, chk) in self._theme_items.items():
            try:
                chk.set_opacity(1.0 if m == mode else 0.0)
            except Exception:
                pass
        # 收起弹出菜单
        try:
            popover = self.theme_button.get_popover()
            if popover is not None:
                popover.popdown()
        except Exception:
            pass

    def on_theme_selected(self, item, mode):
        """兼容旧接口：用户选择主题。"""
        if not item.get_active():
            return
        apply_app_css(mode)
        save_theme_pref(mode)
        self._refresh_theme_icon(mode)
        # 收起弹出菜单
        try:
            popover = self.theme_button.get_popover()
            if popover is not None:
                popover.popdown()
        except Exception:
            pass

    def build_func_map(self):
        for items in self.category_tree.values():
            def walk(items):
                for item in items:
                    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], str):
                        self.func_map[item[0]] = item[1]
                    elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list):
                        walk(item[1])
            walk(items)

    def detect_system_type(self):
        """探测当前是否为「SteamOS + Windows」双系统。

        为什么需要多层判据：
        1) EFI 启动项里有 Windows —— 最直接，但 Clover 安装时会移除/改名 Windows
           的 EFI 启动项（改为从 Clover 菜单引导），装了 Clover 的双系统机器上
           这里往往看不到 Windows 字样，只看这一项会误判成「单系统」。
        2) 存在 NTFS 分区且标签为 Windows —— 无需 root，稳定可靠。
        3) NTFS 分区里存在 Windows 目录结构（Windows/Program Files/Users）——
           即使标签被改也能识别。
        4) 已挂载的 NTFS 分区里有上述结构同上。
        注意：不能只凭「Clover 启动项」判断双系统 —— 单系统装了 Clover 也会命中。
        只要 2/3/4 任一成立即可判定为双系统。
        """
        # ---- 判据 1：EFI 启动项里有 Windows ----
        if shutil.which("efibootmgr"):
            for cmd in (["sudo", "-n", "efibootmgr"], ["efibootmgr"]):
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        if re.search(r'(?i)windows', result.stdout):
                            return "双系统"
                        break  # 拿到有效输出即可，不必再试下一种方式
                except Exception:
                    continue

        # ---- 判据 2/3：扫描 NTFS 分区（lsblk 无需 root）----
        try:
            result = subprocess.run(
                ["lsblk", "-P", "-n", "-o", "NAME,TYPE,FSTYPE,LABEL,MOUNTPOINT"],
                capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                ntfs_entries = []
                for line in result.stdout.splitlines():
                    fields = dict(re.findall(r'([A-Z]+)="([^"]*)"', line))
                    fstype = (fields.get("FSTYPE") or "").lower()
                    if fstype not in ("ntfs", "fuseblk", "ntfs3"):
                        continue
                    label = (fields.get("LABEL") or "").strip()
                    # 判据 2：分区标签直接就是 Windows
                    if label.lower() == "windows":
                        return "双系统"
                    ntfs_entries.append(fields)

                # 判据 3/4：看分区内容里有没有 Windows 目录结构
                for fields in ntfs_entries:
                    name = fields.get("NAME") or ""
                    mountpoint = (fields.get("MOUNTPOINT") or "").strip()
                    candidates = []
                    if mountpoint and os.path.isdir(mountpoint):
                        candidates.append(mountpoint)
                    # 未挂载的尝试常见 udisks 挂载路径
                    if name:
                        for base in ("/run/media", "/media"):
                            try:
                                for user_dir in os.listdir(base):
                                    p = os.path.join(base, user_dir, name)
                                    if os.path.isdir(p):
                                        candidates.append(p)
                            except OSError:
                                pass
                    for path in candidates:
                        # Windows 根目录下有 Windows/ 且（Program Files 或 Users）
                        has_win_dir = os.path.isdir(os.path.join(path, "Windows"))
                        has_pf = os.path.isdir(os.path.join(path, "Program Files"))
                        has_users = os.path.isdir(os.path.join(path, "Users"))
                        if has_win_dir and (has_pf or has_users):
                            return "双系统"
        except Exception:
            pass

        return "单系统"

    def on_category_activated(self, treeview, path, column):
        model = treeview.get_model(); iter_ = model.get_iter(path); category = model.get_value(iter_, 1)
        if self.search_entry.get_text().strip():
            self.search_entry.set_text("")
        if category == "支持和维护":
            self._current_page = "about"
            self.stack.set_visible_child_name("about"); self.title_icon.set_visible(False); self.category_title.set_visible(False); return
        if category == "更新日志":
            self._current_page = "changelog"
            self.stack.set_visible_child_name("changelog")
            icon_pixbuf = self.category_icons.get(category)
            if icon_pixbuf: self.title_icon.set_from_pixbuf(icon_pixbuf); self.title_icon.set_visible(True)
            else: self.title_icon.set_visible(False)
            self.category_title.set_markup(f"<big><b>{category}</b></big>"); self.category_title.set_visible(True)
            self.display_changelog(); return

        self._current_page = "func"
        self.stack.set_visible_child_name("func")
        icon_pixbuf = self.category_icons.get(category)
        if icon_pixbuf: self.title_icon.set_from_pixbuf(icon_pixbuf); self.title_icon.set_visible(True)
        else: self.title_icon.set_visible(False)
        if category == "系统优化": title_text = f"<big><b>{category} [{self.system_type}]</b></big>"
        else: title_text = f"<big><b>{category}</b></big>"
        self.category_title.set_markup(title_text); self.category_title.set_visible(True)

        self.func_store.clear()
        items = list(self.category_tree.get(category, []))
        if category == "系统优化" and self.system_type == "双系统":
            items = items[:] + [("系统体检", "health_check"),
                                ("修复引导", "fix_boot"),
                                ("修复互通盘", "fix_shared_disk")]
            self.func_map["系统体检"] = "health_check"
            self.func_map["修复引导"] = "fix_boot"
            self.func_map["修复互通盘"] = "fix_shared_disk"

        for item in items:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], str):
                self.func_store.append(None, [item[0]])
            elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list):
                parent_iter = self.func_store.append(None, [item[0]])
                for child in item[1]:
                    self.func_store.append(parent_iter, [child[0]])

    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()
        if not query:
            self.stack.set_visible_child_name(self._current_page)
            return
        matches = []
        for cat, items in self.category_tree.items():
            def walk(items, cat):
                for item in items:
                    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], str):
                        if query in item[0].lower():
                            matches.append((item[0], cat, item[1]))
                    elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list):
                        walk(item[1], cat)
            walk(items, cat)
        if self.system_type == "双系统":
            for name, key in (("系统体检", "health_check"),
                              ("修复引导", "fix_boot"),
                              ("修复互通盘", "fix_shared_disk")):
                if query in name.lower():
                    matches.append((name, "系统优化", key))
        self.search_store.clear()
        for name, cat, key in matches:
            self.search_store.append([name, cat, key])
        if matches:
            self.search_title.set_markup(f"<big><b>搜索结果（{len(matches)} 项）</b></big>")
        else:
            self.search_title.set_markup("<big><b>搜索结果（无匹配）</b></big>")
        self.stack.set_visible_child_name("search")

    def on_search_row_activated(self, treeview, path, column):
        model = treeview.get_model(); iter_ = model.get_iter(path)
        func_name = model.get_value(iter_, 0)
        func_key = model.get_value(iter_, 2)
        self.run_function(func_name, func_key)

    def run_function(self, func_name, func_key):
        if func_key in DANGEROUS_FUNCS:
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                                    text=f"危险操作确认：{func_name}")
            dlg.format_secondary_text(DANGEROUS_HINTS.get(func_key, DEFAULT_DANGEROUS_HINT))
            # 危险操作默认焦点放在「否」上，避免误按回车直接执行
            try:
                dlg.set_default_response(Gtk.ResponseType.NO)
            except Exception:
                pass
            response = dlg.run()
            dlg.destroy()
            if response != Gtk.ResponseType.YES:
                return

        if func_name in ("Steam缓存管理", "GE-Proton 管理", "卸载其他已安装应用"):
            self._run_standalone_script(func_key); return
        if func_name == "UU加速器插件":
            self.run_external_terminal(func_key); return

        if self.task_window: self.task_window.destroy()
        self.task_window = TaskWindow(self, func_key, func_name)

    def update_status(self):
        term = "内嵌终端" if VTE_AVAILABLE else "外部终端"
        self.status_label.set_text(f"系统: {self.system_type} ｜ 终端: {term} ｜ 版本: v{VERSION}")

    def display_changelog(self):
        changelog_content = """2026-10-19（v1.8.0）
【新增功能】
- 新增「系统体检」功能（双系统用户可见）：专用于 SteamOS 更新后排查掉盘、掉引导、挂载失效，覆盖 6 大类共 18 项检查
  · ESP 分区：是否识别、挂载状态、剩余空间（Clover 需约 15MB）
  · UEFI 启动项：Clover / SteamOS / Windows 启动项是否存在，Clover 是否为第一启动项
  · Clover 引导文件：cloverx64.efi、config.plist、BOOTX64.EFI 及其 .orig 备份是否完整
  · Windows 分区：是否存在、是否挂载、Windows 系统文件结构是否完整
  · /etc/fstab：条目是否指向仍存在的分区，有无失败的挂载单元
  · 系统与引导服务：SteamOS 只读模式、Clover 引导守护服务（clover-bootmanager）启用与运行状态
- 体检为只读检查，发现问题后列出「可自动修复」项，经确认才执行修复
- 可一键修复：重建丢失的 Clover / SteamOS 启动项、把 Clover 设为第一启动项、启用 Clover 引导守护服务、注释掉 fstab 中的失效条目（修改前自动备份）

【问题修复】
- 体检中的 ESP 探测不再硬编码 /dev/nvme0n1p1：改用 findmnt + EFI 分区类型 GUID 动态定位，兼容 eMMC/SATA 机型与不同分区号
- 区分「文件确实缺失」与「无 sudo 权限无法读取」：无权限时明确提示跳过，不再把每个文件都误报为缺失

2026-10-19（v1.7.7）
【问题修复】
- 修复双系统被误判为单系统：Clover 安装后会移除/隐藏 Windows 的 EFI 启动项，只看 efibootmgr 里有没有 "Windows" 字样会漏判，导致「修复引导」「修复互通盘」等双系统功能不显示
- 系统类型检测改为多重判据：① EFI 启动项含 Windows ② 存在标签为 Windows 的 NTFS 分区 ③ NTFS 分区内存在 Windows\\Program Files 或 Windows\\Users 目录结构（即使分区标签被改也能识别）；任一成立即判定为双系统
- 确保只有 Clover 启动项、没有 Windows 的单系统机器仍正确显示为「单系统」，不会误暴露双系统危险功能

2026-10-19（v1.7.6）
【界面优化】
- 内嵌终端窗口新增「复制」按钮：有选中内容时复制选中，未选中时复制全部输出，并有短时状态反馈
- 内嵌终端新增右键菜单：复制选中内容 / 复制全部输出 / 粘贴 / 全选
- 内嵌终端新增键盘快捷键：Ctrl+Shift+C 复制、Ctrl+Shift+V 粘贴、Ctrl+Shift+A 全选（Ctrl+C 仍保留用于中断进程）
- 任务窗口标题栏新增「最大化 / 还原」按钮，可把终端铺满屏幕；窗口不再强制模态，可自由缩放并切换到其他窗口

【问题修复】
- 修复「安装国内源」完成后提示的恢复官方源命令缺少 sudo、直接复制执行会失败的问题，并注明需在 Konsole 中执行

2026-10-19（v1.7.5）
【问题修复】
- 统一全部 GitHub 下载镜像源：原 3 个镜像中 gh.ddlc.top 已 429 限流、mirror.ghproxy.com 域名失效，仅 ghproxy.net 仍可用但很慢，导致插件 / GE-Proton / Clover 下载经常失败
- 新镜像列表（均经 5 轮稳定性 + 33MB 文件 sha256 完整性 + 实速实测）：gh-proxy.com（速度快）、gh.3w.pm（稳定）、cors.isteed.cc（稳定）、ghproxy.net（慢速备用）、GitHub 官方源
- 修复下载镜像选择菜单显示空条目：官方源在内部用空前缀（避免 URL 拼成 https://github.com/https://github.com/...），菜单改为显示可读名称
- 修复 Clover 克隆镜像选择：实测 gh-proxy.com / cors.isteed.cc / ghproxy.net 均不支持 git clone，改为仅提供 gh.3w.pm 与官方源
- 修复 Flatpak 国内源：原配置的 mirror.sjtu.edu.cn/flathub 已改为 301 跳回官方、实际无效；改用 mirrors.ustc.edu.cn/flathub（实测可正常查询与安装），并自动导入 flathub 签名公钥、切换后验证可用性、失败自动回滚
- 修复 Flatpak 源配置使用不存在的 `flatpak remote-get-url` 命令获取原地址，改为从 remotes 列表解析
- 修复 Flatpak 源验证因未指定分支必然失败，以及系统级 remote-modify 缺少 sudo 会卡在密码提示的问题
- 修复「安装国内源」多余的禁用 SteamOS 只读模式操作：flatpak 配置位于可写的 /var 分区，与只读根分区无关

2026-10-19（v1.7.4）
【问题修复】
- 修复「一键应用 CryoByte33 推荐方案」重复执行会在 /etc/fstab 写入重复 swap 条目的问题（sed 分隔符转义错误导致删除失败）
- 修复退出时无条件把 SteamOS 只读模式改回 enabled：现在只有脚本自己解除过只读才会恢复，不再覆盖用户手动设置的可写状态
- 修复「调整虚拟内存」替换正在使用的 swapfile 前未先 swapoff（可能导致 device busy 或在内存紧张时 OOM），改为先停用并校验
- 修复「调整虚拟内存」显示 / 剩余空间、实际预检 /home 的不一致；fstab 判断改为按第一字段精确匹配（不再误判注释行与 swapfile2）
- 修复「配置ZRAM」设置无法持久化：现写入 /etc/systemd/zram-generator.conf，重启后仍生效，并修正原代码误删该配置的问题
- 修复「清理虚拟内存配置」在未启用 ZRAM 时误报"ZRAM 重置失败"，且 fstab 改用精确匹配删除
- 修复「清理hosts缓存」在只读模式下静默失败却仍提示成功，改为先确保可写、失败即中止并给出回滚方法
- 修复「Steam缓存管理」只扫描默认库（SD 卡/第二块盘的库看不到）、游戏名含分隔符会解析错位、删除前缺少明细确认
- 修复「安装/重装 Clover」缺少危险操作二次确认；并改为动态探测 ESP 分区（原硬编码 /dev/nvme0n1p1，eMMC/SATA 机型会失败）
- 修复 Clover 安装中途失败会在 EFI 分区留下半套文件：备份/替换 BOOTX64.EFI 失败现在会中止并回滚，安装脚本失败即停
- 修复 Clover 安装脚本用 echo -e 传递含反斜杠的 sudo 密码会被截断导致认证失败，改用 printf 原样传递
- 修复 Clover 相关脚本退出时可能把系统停在可写状态，以及 ISO/7z 临时文件残留
- 修复自更新先截断自身再写入、中途失败会导致程序损坏：改为写临时文件后原子替换，并增加语法校验
- 修复版本比较把 1.7 与 1.7.0 判为不同版本，可能反复提示更新
- 修复「安装/卸载插件」结果只看命令返回值，现在以目录实际状态为准，避免假成功
- 修复非 deck 用户名的设备上安装插件/小黄鸭后文件属主被改成 deck 的问题
- 修复「安装ToDesk」直接执行第三方远程脚本：现改为下载到本地、展示内容、语法校验后再询问是否执行，并明确列出该脚本对系统的改动
- 修复检测系统类型时把 Clover 启动项当成双系统依据（单系统装了 Clover 会误显示"双系统"并暴露危险功能），改为仅以 Windows 启动项判断
- 修复「安装/更新 GE-Proton」解压中断会在 compatibilitytools.d 留下残缺版本，改为先解压到临时目录校验后再移入
- 危险操作确认框默认焦点改为「否」，避免误按回车直接执行

2026-10-19（v1.7.3）
【问题修复】
- 修复浅色模式下危险操作确认窗口文字看不清：原生对话框底色是浅色而文字仍沿用深色主题配色，出现"白底浅字"；现为对话框显式指定底色与文字色，标题、正文、按钮均随主题正确切换
- 修复浅色模式下下拉菜单、右键菜单、工具提示等原生浮层的文字配色不随主题变化的问题

2026-10-19（v1.7.2）
【新增功能】
- 新增深色 / 浅色主题切换：标题栏图标按钮可切换深色、浅色、跟随系统三种模式，选择自动保存，重启后保持
- 浅色主题为独立配色的完整主题，并同步 GTK 原生控件（对话框、菜单）配色

【问题修复】
- 修复 vte3 安装失败（"889B5EBD… 无法在本地签署"）：SteamOS 的 holo 密钥环与 Arch 官方钥匙环相互独立，只执行 pacman-key --populate archlinux 时该密钥不会被导入，导致后续签名必然失败；现同时导入 archlinux 与 holo 两个钥匙环
- 修复「修复磁盘写入错误」功能检测失效：原逻辑靠 ntfsfix 输出中的 "Volume is dirty" 判断，但 ntfsfix 并不打印该文字，导致所有分区恒显示"正常"；现改为读取 $Volume 的 Volume Flags 脏标志位
- 修复已挂载 NTFS 分区无法检测：ntfsinfo/ntfsfix 需要独占打开设备，挂载中的分区会报占用；现检查前临时卸载、检查后自动挂回原处
- 修复「修复磁盘写入错误」的无意义密码提示：单系统无 NTFS 分区时不再索要 sudo 密码，直接给出结论与排查建议
- 修复有分区被跳过时仍显示"所有 NTFS 分区状态正常"的误导性结论，改为明确提示未检查数量
- 修复 NTFS 分区编号与实际输入不一致的问题
- 修复「修复互通盘」重启后失效：原逻辑只要分区当前已挂载就跳过，但 udisks 自动挂载重启后不会保留；现要求"已挂载且已写入 fstab"才算就绪，确保重启后仍自动挂载
- 修复「修复互通盘」误删用户数据盘：不再强制卸载并删除 /run/media/deck/ 下非 NTFS 分区（ext4/U盘/Btrfs 外置盘）的 fstab 条目
- 修复 fstab 条目匹配使用子串导致误判（UUID 前缀相同会被当成已存在），改为锚定精确匹配
- 修复 fstab 写入可能丢失条目：改为原子替换，失败时保留原条目
- 修复 fstab 删除使用 sed 正则转义不全导致删不掉条目，改用按字段精确比对
- 修复「修复互通盘」挂载失败时仍显示"全部完成"，现改为显示失败数量
- 修复「修复互通盘」、UDisks2 修改的假成功提示，改为真实结果反馈
- 修复主题"跟随系统"读取的是被自己改写过的值（自我污染），现改为启动时记录系统真实配色快照

2026-09-09（v1.7.1）
【界面优化】
- 全新 Steam Deck 风格主题：深蓝黑底 + Steam 蓝高亮，圆角卡片与加高的触控友好列表行
- 左侧分类栏新增面板标题，功能列表与搜索结果改为圆角卡片容器，帮助/退出按钮使用强调色
- 顶部标题栏副标题显示系统类型，窗口按钮与搜索框统一为圆角样式
- 任务窗口新增标题栏与深色终端配色，运行时显示计时、完成后显示"任务已完成"
- 更新日志页补充页面标题，关于/更新日志正文改为圆角卡片

2026-09-06（v1.7.0包含 v1.6.9 的调整）
【界面优化】
- 新增顶部标题栏（HeaderBar），显示版本号
- 新增全局功能搜索：顶部搜索框跨分类查找功能，结果页显示所属分类
- 任务窗口新增运行计时器，任务状态一目了然
- 危险操作二次确认：修复引导/修复互通盘/卸载插件商店/清理hosts 执行前弹出确认
- 底部状态栏显示系统类型、终端模式、版本
- 全局样式优化：更舒适的列表间距与选中高亮

【问题修复】
- 修复取消任务无效：任务进程现在会被真正终止（此前点"取消"只是关窗口，进程仍在后台运行）
- 修复 SteamOS 只读模式禁用后未恢复：所有功能执行完毕自动恢复，避免系统更新异常
- 修复清理 hosts 误删系统条目：现在只移除 Steam 相关域名并自动备份
- 修复自更新无内容校验：更新前校验下载内容，防止错误页覆盖脚本
- 修复版本比较逻辑：数字逐段比较，本地版本更新时不再提示降级
- 修复 ToMoon/Freedeck 等插件版本获取：排除 build 类无效标签、兼容无 v 前缀标签、智能选择下载资产（跳过源码包）、已装正式版时正确检测更新
- 修复 GitHub API 检查在管道下误报异常
- 修复 Watt Toolkit 已安装时静默重复下载：现在会先确认再覆盖

【功能强化】
- 交换文件创建增加空间预检与 dd/mkswap/swapon 逐级校验，失败时明确报错
- 加速器/ToDesk/AnyDesk/应用更新增加失败提示
- 安装育碧/Epic 前置检查 Proton Experimental 是否存在，缺失时给出指引
- 插件安装器统一为通用逻辑，镜像源全局统一，zip 下载带完整性校验
- 图标资源内嵌到脚本，离线自包含，无需外部文件夹

【其他】
- 全面改用 $HOME 变量，减少硬编码路径
- 桌面快捷方式改用 sys.executable，兼容性更好
- 终端模拟器缺失时自动回退（konsole → xterm 等）
2026-08-07（v1.6.8） 调整了从github上安装的部分功能的版本对比逻辑
2026-08-05（v1.6.7） 修复了部分bug，并完善了部分功能的逻辑
2026-08-04（v1.6.6包含 v1.6.4-v1.6.5 的调整） 增加了安装第三方游戏平台的功能（目前包含育碧，Epic，战网）
2026-08-01（v1.6.3包含 v1.6.2 的调整） 完善了卸载已安装应用功能的删除快捷方式的步骤，并增加了询问是否删除应用数据的步骤
2026-07-31（v1.6.1） 增加了GE-Proton 管理的功能，可以安装/卸载GE兼容层
2026-07-30（v1.6.0包含 v1.5.7-v1.5.9 的调整） 新增了安装Freedeck插件的功能，并修复了一些bug和优化完善了一些功能
2026-07-29（v1.5.6包含 v1.5.2-v1.5.5 的调整） 增加了安装Fcitx 5的功能并继续修复了一些bug,并调整了部分功能的逻辑
2026-07-27（v1.5.1包含 v1.5.0 的调整） 修复了一些bug,并优化完善了一些功能
2026-07-26（v1.4.9） 增加了安装Asklink远程的功能
2026-07-25（v1.4.8包含 v1.3.9-v1.4.7 的调整）将文字形式停止更新，替换为图文形式，操作更加便捷，并对功能进行了修改和优化完善
删除了设置管理员密码的功能，增加了安装奇游联机宝加速插件的功能
2026-07-18（v1.3.8包含 v1.3.7 的调整） 替换steamcommunity 302功能为安装Watt Toolkit (Steam++)，增加实用性
调整了安装插件商店以及安装LSFG-VK插件和Framegen插件功能的部分逻辑，将校准摇杆更改为校准设备，增加了校准扳机
2026-07-09（v1.3.6） 修改了修复互通盘功能的实现逻辑，更具有通用性
2026-07-08（v1.3.5包含 v1.3.4 的调整） 删除了"远程无法连接点我"功能，调整从 GitHub 安装的功能的镜像顺序
2026-06-30（v1.3.2） 修复了安装AnyDesk功能的bug
2026-06-28（v1.3.1） 修复了调整虚拟内存大小功能的bug
2026-06-27（v1.3.0） 增加"远程无法连接点我"功能
调整安装 AnyDesk 功能的安装逻辑，改为从官网安装
2026-06-03（v1.2.7） 增加安装/重装 Clover 引导功能，并进行多项完善
2026-06-02（v1.2.6） 调整从 GitHub 安装的功能的安装逻辑，支持预发布版本和正式版选择
2026-05-31（v1.2.4，包含 v1.1.9、v1.2.0、v1.2.1 的调整） 增加安装 LSFG‑VK 插件和 Framegen 插件功能（从 GitHub 安装，并使用镜像下载）
调整插件商店功能的安装步骤，改用国内镜像加快下载速度，并增加镜像下载失败后的自动重试
调整 Steam Deck 缓存管理器功能的部分参数
2026-05-30（v1.1.8） 调整自动更新的逻辑
2026-05-28（v1.1.8，包含 v1.1.7） 更改插件商店功能，改为从 GitHub 安装
更新工具箱打开后自动更新的步骤
2026-03-17（v1.1.2） 由于宝葫芦停止维护，删除"安装＆卸载宝葫芦"功能
2026-03-05（v1.1.1） 更改安装 ToMoon 功能的实现逻辑，改为从 Gitee 克隆下载安装
2026-03-02（v1.1.0） 更改安装插件商店功能的实现逻辑，改为从 Gitee 克隆下载安装
2026-01-21（v1.0.9） 新增安装 Steam 社区 302 功能
2026-01-16（v1.0.8） 完善调整虚拟内存大小功能的文本展示
2026-01-11（v1.0.7） 完善调整虚拟内存大小功能
最初发布在github，没做详细的统计，发布日期为2026-01-01"""
        self.changelog_textview.get_buffer().set_text(changelog_content)

    def on_func_row_activated(self, treeview, path, column):
        model = treeview.get_model(); iter_ = model.get_iter(path); func_name = model.get_value(iter_, 0)
        if not func_name: return
        if model.iter_has_child(iter_):
            if treeview.row_expanded(path): treeview.collapse_row(path)
            else: treeview.expand_row(path, False)
            return

        func_key = self.func_map.get(func_name)
        if not func_key: return
        self.run_function(func_name, func_key)

    def _run_standalone_script(self, func_key):
        # 这类功能用 zenity 弹窗交互，输出不进入内嵌终端。
        # 如果系统没有 zenity，脚本只会把错误打到日志里，用户完全看不到任何反馈，
        # 所以这里先检查，缺了就直接用对话框明确告知。
        if not shutil.which("zenity"):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                                    text="缺少 zenity 组件，无法运行该功能")
            dlg.format_secondary_text(
                "该功能依赖 zenity 提供图形化选择界面。\n"
                "请先安装后重试：sudo pacman -S zenity")
            dlg.run(); dlg.destroy()
            return
        tmp_path = create_temp_script()
        log_path = "/tmp/steamdeck_toolbox_standalone.log"
        try:
            with open(log_path, 'w', encoding='utf-8') as log_f:
                subprocess.Popen([tmp_path, func_key], stdout=log_f, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, start_new_session=True)
        except Exception as e:
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                                    text="启动任务失败")
            dlg.format_secondary_text(f"{e}")
            dlg.run(); dlg.destroy()

    def run_external_terminal(self, func_key):
        tmp_path = create_temp_script()
        cmd = f"bash {tmp_path} {func_key}; read -p '按回车键关闭...' -n1"
        if not launch_terminal(cmd):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                                    text="未找到可用的终端模拟器")
            dlg.format_secondary_text("请安装 konsole 或 xterm 后重试。")
            dlg.run(); dlg.destroy()

    def on_help_clicked(self, button):
        help_dialog = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Steam Deck 工具箱")
        help_dialog.format_secondary_text("本工具集成了系统优化、软件安装、网络工具等功能。\n点击左侧分类，右侧显示功能列表。\n小破站关注up主 AlanWake2100 可以来催更哦~")
        help_dialog.run(); help_dialog.destroy()

def ensure_desktop_shortcut():
    script_path = os.path.abspath(sys.argv[0])
    desktop_dir = os.path.expanduser("~/Desktop")
    desktop_file = os.path.join(desktop_dir, "Deck工具箱.desktop")
    if os.path.exists(desktop_file): return
    content = f"""[Desktop Entry]
Type=Application
Name=Deck工具箱
Exec={sys.executable} "{script_path}"
Icon=input-gamepad-symbolic
Terminal=false
StartupNotify=true
Categories=Utility;
"""
    try:
        with open(desktop_file, 'w') as f: f.write(content)
        os.chmod(desktop_file, 0o755)
    except Exception as e: print(f"创建桌面快捷方式失败: {e}")

def ensure_vte_installed():
    if VTE_AVAILABLE: return
    dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.NONE, "未检测到 VTE 终端组件。\n是否立即安装？(需要 sudo 密码，安装后请手动重启程序)")
    dialog.format_secondary_text("点击“是”将自动解除只读模式并安装 vte3。")
    dialog.add_button("是", Gtk.ResponseType.YES); dialog.add_button("否", Gtk.ResponseType.NO)
    dialog.set_icon_name("input-gamepad-symbolic")
    response = dialog.run(); dialog.destroy()
    if response == Gtk.ResponseType.YES:
        install_cmd = (
            "if command -v steamos-readonly >/dev/null 2>&1; then "
            "sudo steamos-readonly disable || { echo '✗ 禁用只读模式失败，请手动执行: sudo steamos-readonly disable'; read -n1; exit 1; }; "
            "fi; "
            "echo '正在初始化 pacman keyring（可能需要一点时间）...'; "
            "sudo pacman-key --init || { echo '✗ pacman keyring 初始化失败'; read -n1; exit 1; }; "
            "sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null; sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null; "
            # 关键：889B5EBD... 属于 holo-keyring，必须同时导入 holo 钥匙环，
            # 否则该密钥不在本地钥匙环中，--lsign-key 会报“无法在本地签署”。
            "echo '正在导入 Arch 官方与 SteamOS Holo 密钥...'; "
            "sudo pacman-key --populate archlinux || { echo '✗ archlinux 钥匙环填充失败'; read -n1; exit 1; }; "
            "if [ -f /usr/share/pacman/keyrings/holo.gpg ]; then "
            "sudo pacman-key --populate holo || { echo '✗ holo 钥匙环填充失败'; read -n1; exit 1; }; "
            "fi; "
            "echo '正在信任 SteamOS 打包者密钥...'; "
            "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || { "
            "echo '⚠ 签名失败，刷新钥匙环后重试...'; "
            "sudo pacman-key --refresh-keys 2>/dev/null; "
            "sudo pacman-key --populate archlinux holo 2>/dev/null; "
            "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || "
            "{ echo '✗ 密钥签署失败'; read -n1; exit 1; }; }; "
            "sudo pacman -Sy --noconfirm >/dev/null 2>&1; "
            "sudo pacman -S --needed --noconfirm vte3 || { echo '✗ vte3 安装失败，请检查网络或软件源'; read -n1; exit 1; }; "
            "pacman -Q vte3 >/dev/null 2>&1 || { echo '✗ vte3 安装后验证失败，请重启程序后重试'; read -n1; exit 1; }; "
            "command -v steamos-readonly >/dev/null 2>&1 && sudo steamos-readonly enable 2>/dev/null || true; "
            "echo '✓ 安装完成，请手动重启本程序。'; read -n1"
        )
        if not launch_terminal(install_cmd):
            err = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                    "未找到可用的终端模拟器")
            err.format_secondary_text("请手动打开终端执行：sudo pacman -S --noconfirm vte3")
            err.run(); err.destroy()

def sync_emoji_icons():
    """确保脚本目录下存在 emoji_icons 文件夹（从内嵌数据解出，离线可用，便于自定义图标）。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_icon_dir = os.path.join(script_dir, "emoji_icons")
    os.makedirs(local_icon_dir, exist_ok=True)
    for icon_name, data in EMBEDDED_ICONS.items():
        local_path = os.path.join(local_icon_dir, icon_name)
        if os.path.isfile(local_path):
            continue
        try:
            with open(local_path, 'wb') as f:
                f.write(base64.b64decode(data))
        except Exception as e:
            print(f"写入图标 {icon_name} 失败: {e}")

def get_remote_version():
    try:
        req = urllib.request.Request(REPO_RAW_URL, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=VERSION_CHECK_TIMEOUT) as response:
            content = response.read().decode('utf-8')
            match = re.search(r'^VERSION\s*=\s*["\']([0-9.]+)["\']', content, re.MULTILINE)
            if match: return match.group(1)
            match = re.search(r'VERSION\s*=\s*["\']([0-9.]+)["\']', content)
            if match: return match.group(1)
    except Exception as e: print(f"检查更新失败: {e}")
    return None

def _perform_update_in_dialog(dialog, remote_version):
    def do_download():
        tmp_path = None
        try:
            req = urllib.request.Request(REPO_RAW_URL, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, timeout=30) as response:
                new_content = response.read().decode('utf-8')
            if ('BASH_SCRIPT = ' not in new_content or 'VERSION = ' not in new_content
                    or len(new_content) < 50000):
                raise ValueError('下载内容校验失败（不是有效的脚本文件），已中止更新')
            # 再校验一次语法：远程文件若被人改坏，写进去就是个打不开的程序
            compile(new_content, '<remote>', 'exec')
            current_path = os.path.abspath(sys.argv[0])
            backup_path = current_path + ".bak"
            try: shutil.copy2(current_path, backup_path)
            except: pass
            # 先写临时文件再原子替换：直接以 'w' 打开自身会先把原文件截断，
            # 一旦写入过程中出错/断电，用户的工具箱就彻底损坏且无法启动。
            tmp_path = current_path + ".new"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                f.flush()
                os.fsync(f.fileno())
            os.chmod(tmp_path, 0o755)
            os.replace(tmp_path, current_path)
            tmp_path = None
            GLib.idle_add(_update_dialog_success, dialog, remote_version)
        except Exception as e:
            GLib.idle_add(_update_dialog_error, dialog, str(e))
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try: os.unlink(tmp_path)
                except Exception: pass
    threading.Thread(target=do_download, daemon=True).start()

def _update_dialog_success(dialog, remote_version):
    dialog.set_markup("<big><b>✅ 更新完成</b></big>")
    dialog.format_secondary_text(f"新版本 v{remote_version} 已下载。\n程序即将自动重启...")
    def restart():
        dialog.destroy(); subprocess.Popen([sys.executable, sys.argv[0]]); Gtk.main_quit()
    GLib.timeout_add(500, restart)

def _update_dialog_error(dialog, error_msg):
    dialog.set_markup("<big><b>❌ 更新失败</b></big>")
    dialog.format_secondary_text(f"更新过程中发生错误：{error_msg}\n请手动从以下地址下载最新版本：\n{REPO_RAW_URL}")
    for btn in dialog.get_action_area().get_children(): btn.destroy()
    dialog.add_button("确定", Gtk.ResponseType.CLOSE)
    dialog.connect("response", lambda d, r: (dialog.destroy(), show_main_window()))
    dialog.show_all()

class UpdateCheckWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="检查更新")
        self.set_icon_name("input-gamepad-symbolic"); self.set_default_size(400, 150); self.set_position(Gtk.WindowPosition.CENTER); self.set_deletable(False)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); vbox.set_margin_top(20); vbox.set_margin_bottom(20); vbox.set_margin_start(20); vbox.set_margin_end(20); self.add(vbox)
        self.label = Gtk.Label(label="正在检查更新..."); self.label.set_justify(Gtk.Justification.CENTER); vbox.pack_start(self.label, True, True, 0)
        self.button = None; self.vbox = vbox; self.show_all(); GLib.timeout_add(200, self.perform_check)

    def perform_check(self):
        def check_thread():
            sync_emoji_icons(); remote_version = get_remote_version(); GLib.idle_add(self.on_check_done, remote_version)
        threading.Thread(target=check_thread, daemon=True).start(); return False

    def on_check_done(self, remote_version):
        if remote_version is None:
            self.label.set_text("检查更新失败，请检查网络连接。")
            if self.button is None:
                self.button = Gtk.Button(label="进入主界面"); self.button.connect("clicked", self.on_button_clicked); self.vbox.pack_start(self.button, False, False, 0)
            self.button.show(); return
        if compare_versions(remote_version, VERSION) <= 0:
            self.label.set_text(f"当前已是最新版本 (v{VERSION})")
            if self.button is not None: self.button.hide()
            GLib.timeout_add(300, self.auto_enter_main); return
        self.label.set_text(f"发现新版本 v{remote_version}\n当前版本: v{VERSION}")
        if self.button is not None: self.button.hide()
        self.show_update_prompt(remote_version)

    def auto_enter_main(self):
        self.destroy(); show_main_window(); return False

    def show_update_prompt(self, remote_version):
        self.destroy()
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.NONE, "发现新版本")
        dialog.set_default_size(400, 150); dialog.set_markup(f"<big><b>发现新版本 v{remote_version}</b></big>")
        dialog.format_secondary_text(f"当前版本: v{VERSION}\n最新版本: v{remote_version}\n\n是否立即更新？")
        dialog.add_button("是", Gtk.ResponseType.YES); dialog.add_button("否", Gtk.ResponseType.NO); dialog.set_icon_name("input-gamepad-symbolic")
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            dialog.set_markup("<big><b>正在更新...</b></big>"); dialog.format_secondary_text("正在下载新版本，请稍候。")
            for btn in dialog.get_action_area().get_children(): btn.destroy()
            dialog.show_all(); _perform_update_in_dialog(dialog, remote_version)
        else:
            dialog.destroy(); show_main_window()

    def on_button_clicked(self, button):
        self.destroy(); show_main_window()

def show_main_window():
    window = MainWindow(); window.connect("destroy", Gtk.main_quit); window.show_all()
    GLib.idle_add(ensure_desktop_shortcut); GLib.idle_add(ensure_vte_installed)

def main():
    # 关键顺序：必须在 apply_app_css 改写 GTK prefer-dark 之前，
    # 先记录系统真实的配色方案，否则“跟随系统”会读到被自己改过的值。
    reset_system_theme_cache()
    # 启动时应用用户上次选择的主题（默认跟随系统）
    apply_app_css(load_theme_pref())
    update_win = UpdateCheckWindow(); Gtk.main()

if __name__ == "__main__":
    main()
