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
import urllib.parse
import hashlib
import tarfile
import fnmatch
import socket
import atexit
import base64
import signal

# ============================================================================
# 版本定义
# ============================================================================
VERSION = "2.1.3"
REPO_RAW_URL = "https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/steamdeck_gui.py"
REPO_URL = "https://github.com/Zhucy123/steamdeck_toolbox"
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
# 主题（深色 / 浅色）— Steam Deck OLED 主从布局视觉
# ============================================================================
# 配色表：键名相同，两套值不同，CSS 模板通过 {key} 占位符注入。
THEME_DARK = {
    "bg": "#07080c", "bg_alt": "#0e1016", "panel": "#141821", "panel_hi": "#1a2030",
    "border": "#2a3144", "accent": "#3dd6c6", "accent_dark": "#2bb8a9",
    "accent_soft": "rgba(61, 214, 198, 0.14)", "accent_mid": "rgba(61, 214, 198, 0.28)",
    "text": "#e8eef8", "dim": "#8b98a8",
    "header_top": "#0c0e14", "header_bottom": "#0a0c11", "header_border": "#1e2433",
    "header_backdrop_top": "#0c0e14", "header_backdrop_bottom": "#090b10",
    "title": "#f4f7fb", "search_bg": "#0c0f16",
    "sidebar_header_top": "#12151e", "sidebar_header_bottom": "#0e1118",
    "bottom_top": "#0c0e14", "bottom_bottom": "#090b10",
    "hover": "rgba(196, 92, 255, 0.10)",
    "scrollbar": "rgba(180, 200, 230, 0.22)",
    "btn_ghost": "rgba(255, 255, 255, 0.05)", "btn_ghost_border": "rgba(255, 255, 255, 0.08)",
    "titlebtn": "rgba(255, 255, 255, 0.08)", "titlebtn_border": "rgba(255, 255, 255, 0.12)",
    "titlebtn_hover": "rgba(255, 255, 255, 0.16)",
    "shadow": "rgba(0, 0, 0, 0.50)",
    "sel_text": "#061016",
    "suggested_hover": "#5ee6d6",
    "destructive": "#e35d6a", "destructive_border": "#c94a56",
    "destructive_hover": "#f0727d", "destructive_hover_border": "#e35d6a",
    "close_hover": "#e35d6a", "close_hover_border": "#f0727d",
    "alpha_accent_hover": "0.14", "alpha_accent_btn": "0.22", "alpha_accent_head": "0.24",
    "chip_bg": "rgba(61, 214, 198, 0.14)",
    "success": "#3dd68c",
    "term_bg": "#06080c", "term_fg": "#e8eef8",
    "card_glow": "rgba(196, 92, 255, 0.20)",
    "purple": "#c45cff", "purple_dark": "#9b3fd4",
    "purple_soft": "rgba(196, 92, 255, 0.16)", "purple_mid": "rgba(196, 92, 255, 0.30)",
    "rail_bg": "#0c0e15",
}

THEME_LIGHT = {
    "bg": "#eef2f6", "bg_alt": "#e4eaf1", "panel": "#ffffff", "panel_hi": "#f5f8fb",
    "border": "#c9d3de", "accent": "#0f9e90", "accent_dark": "#0c8579",
    "accent_soft": "rgba(15, 158, 144, 0.12)", "accent_mid": "rgba(15, 158, 144, 0.20)",
    "text": "#15202b", "dim": "#5d6b78",
    "header_top": "#ffffff", "header_bottom": "#f3f7fa", "header_border": "#d5dee8",
    "header_backdrop_top": "#f8fafc", "header_backdrop_bottom": "#eef3f7",
    "title": "#101820", "search_bg": "#ffffff",
    "sidebar_header_top": "#f5f8fb", "sidebar_header_bottom": "#eef3f7",
    "bottom_top": "#f5f8fb", "bottom_bottom": "#e8eef4",
    "hover": "rgba(140, 60, 200, 0.08)",
    "scrollbar": "rgba(21, 32, 43, 0.18)",
    "btn_ghost": "rgba(20, 30, 40, 0.04)", "btn_ghost_border": "rgba(20, 30, 40, 0.10)",
    "titlebtn": "rgba(20, 30, 40, 0.05)", "titlebtn_border": "rgba(20, 30, 40, 0.10)",
    "titlebtn_hover": "rgba(20, 30, 40, 0.12)",
    "shadow": "rgba(20, 35, 50, 0.12)",
    "sel_text": "#ffffff",
    "suggested_hover": "#14b3a3",
    "destructive": "#d64555", "destructive_border": "#bf3a48",
    "destructive_hover": "#e35a68", "destructive_hover_border": "#d64555",
    "close_hover": "#d64555", "close_hover_border": "#e35a68",
    "alpha_accent_hover": "0.10", "alpha_accent_btn": "0.16", "alpha_accent_head": "0.18",
    "chip_bg": "rgba(15, 158, 144, 0.10)",
    "success": "#1fa971",
    "term_bg": "#f7fafc", "term_fg": "#15202b",
    "card_glow": "rgba(140, 60, 200, 0.14)",
    "purple": "#8b3dd9", "purple_dark": "#6f2db0",
    "purple_soft": "rgba(139, 61, 217, 0.12)", "purple_mid": "rgba(139, 61, 217, 0.22)",
    "rail_bg": "#f3f6fa",
}

# CSS 模板：SteamOS / OLED 主从布局（左轨 + 右详情）
APP_CSS_TEMPLATE = """
/* =====================================================================
   Deck Console Master-Detail — OLED purple + cyan, always-on category rail
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
@define-color sd_purple {purple};
@define-color sd_purple_dark {purple_dark};

* {{
    outline-color: alpha(@sd_accent, 0.45);
}}

window {{ background-color: @sd_bg; color: @sd_text; }}
.background {{ background-color: @sd_bg; }}

decoration {{
    background-color: @sd_bg;
    border-radius: 0;
    box-shadow: none;
    border: none;
    margin: 0;
    padding: 0;
}}
decoration:backdrop {{
    background-color: @sd_bg;
    box-shadow: none;
}}
window.csd, window.csd:backdrop {{
    background-color: @sd_bg;
    border-radius: 0;
    border: none;
    margin: 0;
    padding: 0;
}}
window.csd > .titlebar, window.csd > headerbar, .titlebar {{
    background-color: @sd_bg;
    border: none;
    box-shadow: none;
    border-radius: 0;
}}
window.csd > box, window.csd > .background {{
    border-radius: 0;
    background-color: transparent;
}}

headerbar {{
    min-height: 50px;
    padding: 0 14px;
    background-image: none;
    background-color: {header_top};
    border-bottom: 1px solid {header_border};
    color: @sd_text;
    box-shadow: 0 1px 0 alpha(@sd_purple, 0.12);
}}
headerbar:backdrop {{
    background-image: none;
    background-color: {header_backdrop_top};
}}
headerbar .title {{
    font-weight: 800;
    font-size: 15px;
    letter-spacing: 0.4px;
    color: {title};
}}
headerbar .subtitle {{
    font-size: 11px;
    font-weight: 600;
    color: @sd_accent;
}}
headerbar button {{
    background-image: none;
    background-color: {btn_ghost};
    border: 1px solid {btn_ghost_border};
    border-radius: 12px;
    color: @sd_text;
    min-height: 30px;
    min-width: 30px;
    padding: 0 10px;
    box-shadow: none;
    text-shadow: none;
}}
headerbar button:hover {{
    background-color: alpha(@sd_accent, {alpha_accent_head});
    border-color: alpha(@sd_accent, 0.55);
}}
headerbar button:active, headerbar button:checked {{
    background-color: @sd_accent_dark;
    color: {sel_text};
}}
headerbar button.titlebutton {{
    background-image: none;
    background-color: {titlebtn};
    border: 1px solid {titlebtn_border};
    border-radius: 999px;
    color: {title};
    -gtk-icon-shadow: none;
    min-width: 22px;
    min-height: 22px;
    padding: 0;
    box-shadow: none;
}}
headerbar button.titlebutton:hover {{ background-color: {titlebtn_hover}; }}
headerbar button.titlebutton:active {{ background-color: @sd_accent_dark; }}
headerbar button.titlebutton.close:hover {{
    background-color: {close_hover};
    border-color: {close_hover_border};
}}
headerbar button.titlebutton image {{ color: {title}; }}

entry.search, entry.search-entry, searchentry {{
    background-image: none;
    background-color: {search_bg};
    border: 1px solid @sd_border;
    border-radius: 999px;
    color: @sd_text;
    min-height: 34px;
    padding: 0 16px;
    box-shadow: inset 0 1px 0 alpha(@sd_text, 0.03);
    caret-color: @sd_accent;
}}
entry.search:focus, entry.search-entry:focus, searchentry:focus {{
    border-color: @sd_accent;
    box-shadow: 0 0 0 2px alpha(@sd_accent, 0.22);
}}
entry.search image, entry.search-entry image, searchentry image {{ color: @sd_dim; }}
headerbar entry, headerbar entry.search {{ color: @sd_text; }}
headerbar entry text, headerbar entry.search text {{
    background-color: transparent;
    color: @sd_text;
}}

#content-area {{
    background-color: @sd_bg;
}}
.page-shell {{
    background-color: transparent;
}}
#page-title {{
    color: {title};
    font-weight: 800;
    font-size: 18px;
}}
#page-subtitle {{
    color: @sd_dim;
    font-size: 13px;
    font-weight: 500;
}}

/* ---- Master rail (left) ---- */
#cat-rail {{
    background-color: {rail_bg};
    border-right: 1px solid @sd_border;
    padding: 10px 10px 12px 10px;
    min-width: 232px;
}}
#sidebar-header {{
    background-image: none;
    background-color: transparent;
    padding: 6px 8px 10px 8px;
}}
#sidebar-header label {{
    font-weight: 800;
    color: {title};
    font-size: 13px;
    letter-spacing: 0.3px;
}}
button.nav-item {{
    background-image: none;
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 14px;
    color: @sd_text;
    padding: 8px 10px;
    min-height: 40px;
    box-shadow: none;
    text-shadow: none;
    font-weight: 600;
}}
button.nav-item:hover {{
    background-color: {purple_soft};
    border-color: alpha(@sd_purple, 0.28);
}}
button.nav-item:active {{
    background-color: {purple_mid};
}}
button.nav-item.selected {{
    background-color: {purple_soft};
    border-color: alpha(@sd_purple, 0.55);
    box-shadow: inset 3px 0 0 @sd_purple, 0 0 0 1px alpha(@sd_accent, 0.18);
}}
button.nav-item.selected:hover {{
    background-color: {purple_mid};
}}
.nav-item-title {{
    font-weight: 700;
    font-size: 13px;
    color: {title};
}}
button.nav-item.selected .nav-item-title {{
    color: @sd_purple;
}}
.nav-icon-wrap {{
    background-color: {chip_bg};
    border-radius: 10px;
    padding: 4px;
    border: 1px solid alpha(@sd_accent, 0.18);
}}
button.nav-item.selected .nav-icon-wrap {{
    background-color: {purple_soft};
    border-color: alpha(@sd_purple, 0.35);
}}

/* Detail / function row cards */
button.func-tile {{
    background-image: none;
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 14px;
    color: @sd_text;
    padding: 14px 22px 14px 16px;
    min-height: 52px;
    box-shadow: 0 4px 14px {shadow};
    text-shadow: none;
    font-weight: 600;
    margin-right: 8px;
}}
button.func-tile:hover {{
    background-color: @sd_panel_hi;
    border-color: alpha(@sd_accent, 0.65);
}}
button.func-tile:active {{
    background-color: {accent_mid};
}}
button.func-tile.child-tile {{
    margin-left: 18px;
    min-height: 44px;
    background-color: @sd_panel_hi;
}}
.func-group-label {{
    font-weight: 800;
    font-size: 15px;
    color: @sd_accent;
    letter-spacing: 0.4px;
    margin-top: 8px;
    margin-bottom: 2px;
}}
/* Collapsible function groups: big clickable header, default collapsed */
.func-group {{
    margin-top: 6px;
    margin-bottom: 4px;
    margin-right: 8px;
}}
button.func-group-header {{
    background-image: none;
    background-color: alpha(@sd_accent, 0.10);
    border: 1px solid alpha(@sd_accent, 0.55);
    border-left: 4px solid @sd_accent;
    border-radius: 12px;
    color: @sd_accent;
    padding: 12px 14px;
    min-height: 48px;
    box-shadow: 0 2px 10px alpha(@sd_purple, 0.18);
    text-shadow: none;
    font-weight: 800;
}}
button.func-group-header:hover {{
    background-color: alpha(@sd_accent, 0.18);
    border-color: @sd_accent;
    box-shadow: 0 0 0 1px alpha(@sd_purple, 0.35), 0 4px 14px alpha(@sd_accent, 0.22);
}}
button.func-group-header:active {{
    background-color: alpha(@sd_purple, 0.22);
}}
button.func-group-header.expanded {{
    background-color: alpha(@sd_purple, 0.16);
    border-color: alpha(@sd_purple, 0.70);
    border-left-color: @sd_purple;
}}
.func-group-header-label {{
    font-weight: 800;
    font-size: 15px;
    letter-spacing: 0.3px;
    color: @sd_accent;
}}
button.func-group-header.expanded .func-group-header-label {{
    color: @sd_purple;
}}
button.func-group-header image {{
    color: @sd_accent;
    opacity: 1;
}}

button.back-btn {{
    background-image: none;
    background-color: {btn_ghost};
    border: 1px solid {btn_ghost_border};
    border-radius: 999px;
    color: @sd_text;
    min-height: 34px;
    padding: 0 14px;
    font-weight: 700;
}}
button.back-btn:hover {{
    background-color: alpha(@sd_accent, {alpha_accent_btn});
    border-color: alpha(@sd_accent, 0.55);
}}

.card {{
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 16px;
    box-shadow: 0 8px 22px {shadow};
}}
.page-title-chip {{
    background-color: {chip_bg};
    border-radius: 999px;
    padding: 2px 10px;
    color: @sd_accent;
}}
#detail-panel {{
    background-color: @sd_bg;
}}

#bottom-bar {{
    background-image: none;
    background-color: {bottom_top};
    border-top: 1px solid @sd_border;
    padding: 6px 14px;
    border-radius: 0;
}}
#status-label {{
    font-size: 11px;
    font-weight: 500;
    color: @sd_dim;
}}
#task-timer {{
    font-size: 12px;
    font-weight: 700;
    color: @sd_accent;
}}
#task-toolbar {{
    background-color: @sd_bg_alt;
    border-top: 1px solid @sd_border;
    padding: 8px 12px;
}}

button {{
    background-image: none;
    background-color: @sd_panel_hi;
    border: 1px solid @sd_border;
    border-radius: 12px;
    color: @sd_text;
    min-height: 32px;
    padding: 2px 16px;
    box-shadow: none;
    text-shadow: none;
    font-weight: 600;
}}
button:hover {{
    background-color: alpha(@sd_accent, {alpha_accent_btn});
    border-color: alpha(@sd_accent, 0.55);
}}
button:active {{
    background-color: @sd_accent_dark;
    color: {sel_text};
}}
button:disabled {{
    color: @sd_dim;
    background-color: @sd_panel;
    border-color: @sd_border;
    opacity: 0.7;
}}
button.suggested-action {{
    background-image: none;
    background-color: @sd_accent;
    border-color: @sd_accent_dark;
    color: {sel_text};
}}
button.suggested-action:hover {{
    background-image: none;
    background-color: {suggested_hover};
}}
button.destructive-action {{
    background-color: {destructive};
    border-color: {destructive_border};
    color: #ffffff;
}}
button.destructive-action:hover {{
    background-color: {destructive_hover};
    border-color: {destructive_hover_border};
}}
button.flat, button.flat:hover {{
    background-image: none;
    box-shadow: none;
}}

textview, textview text {{
    background-color: @sd_panel;
    color: @sd_text;
    caret-color: @sd_accent;
}}
textview {{
    border-radius: 14px;
}}

scrollbar {{
    background-color: transparent;
    border: none;
    margin: 0 2px 0 6px;
}}
scrollbar.vertical {{
    min-width: 14px;
    padding-left: 4px;
}}
scrollbar slider {{
    background-color: {scrollbar};
    border-radius: 999px;
    min-width: 8px;
    min-height: 7px;
}}
scrollbar slider:hover {{ background-color: alpha(@sd_accent, 0.55); }}
/* keep func tiles clear of the non-overlay scrollbar gutter */
#detail-panel button.func-tile {{
    margin-right: 4px;
}}

popover, popover.background {{
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 14px;
    box-shadow: 0 10px 28px {shadow};
}}
popover > box, popover.background > box {{ background-color: transparent; }}
.theme-row, button.theme-row {{
    background-image: none;
    background-color: transparent;
    border: none;
    border-radius: 10px;
    box-shadow: none;
    padding: 8px 12px;
    min-height: 26px;
    color: @sd_text;
    font-weight: 500;
}}
.theme-row:hover, button.theme-row:hover {{
    background-image: none;
    background-color: {accent_soft};
    border: none;
    color: @sd_text;
}}
.theme-row:active, button.theme-row:active {{
    background-image: none;
    background-color: {accent_mid};
    color: @sd_text;
}}
.theme-row label {{ color: @sd_text; }}
.theme-row image {{ color: @sd_accent; }}

dialog, dialog.background, messagedialog, messagedialog.background {{
    background-color: @sd_panel;
    color: @sd_text;
}}
dialog .titlebar, messagedialog .titlebar,
dialog box.titlebar, messagedialog box.titlebar {{
    background-image: none;
    background-color: @sd_bg_alt;
    border-bottom: 1px solid @sd_border;
    color: @sd_text;
    box-shadow: none;
    border-radius: 0;
}}
dialog .titlebar .title, messagedialog .titlebar .title,
dialog .titlebar label, messagedialog .titlebar label {{
    color: @sd_text;
    font-weight: 700;
}}
dialog .titlebar button, messagedialog .titlebar button {{
    background-image: none;
    background-color: {btn_ghost};
    border: 1px solid {btn_ghost_border};
    border-radius: 10px;
    color: @sd_text;
    box-shadow: none;
    text-shadow: none;
}}
dialog .titlebar button image, messagedialog .titlebar button image {{
    color: @sd_text;
}}
dialog .dialog-action-area, messagedialog .dialog-action-area {{
    background-color: @sd_bg_alt;
    border-top: 1px solid @sd_border;
    padding: 8px;
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

menu, .menu, .context-menu, menuitem, tooltip, tooltip.background {{
    color: @sd_text;
}}
menu, .menu, .context-menu {{
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 10px;
}}
menuitem {{ background-color: transparent; border-radius: 8px; }}
menuitem:hover {{ background-color: {accent_soft}; }}
tooltip.background {{
    background-color: {panel_hi};
    border: 1px solid @sd_border;
    border-radius: 8px;
}}
tooltip label {{ color: @sd_text; }}

vte-terminal {{
    padding: 10px;
    border-radius: 10px;
}}
.term-card {{
    background-color: {term_bg};
    border: 1px solid @sd_border;
    border-radius: 14px;
}}

/* keep legacy list ids harmless if referenced */
#sidebar, #func-list {{
    background-color: transparent;
    color: @sd_text;
}}
.dash-card-desc {{
    font-size: 12px;
    color: @sd_dim;
    font-weight: 500;
}}
"""


def build_css(theme_name):
    """根据主题名生成对应的 CSS 文本。"""
    palette = THEME_LIGHT if theme_name == "light" else THEME_DARK
    return APP_CSS_TEMPLATE.format(**palette)

def theme_palette(theme_name=None):
    """返回当前或指定主题的配色字典。"""
    if theme_name is None:
        try:
            theme_name = resolve_theme_mode(load_theme_pref())
        except Exception:
            theme_name = "dark"
    return THEME_LIGHT if theme_name == "light" else THEME_DARK

def apply_terminal_theme(terminal):
    """按当前主题设置 VTE 前景/背景与基础调色板。"""
    if terminal is None:
        return
    try:
        pal = theme_palette()
        fg = Gdk.RGBA(); fg.parse(pal.get("term_fg", "#e8eefc"))
        bg = Gdk.RGBA(); bg.parse(pal.get("term_bg", "#0b1018"))
        if pal is THEME_LIGHT:
            colors = ("#e8edf5", "#d64555", "#1fa971", "#c48a1a",
                      "#4f6ef7", "#8b5cf6", "#0f9aa8", "#1a2236",
                      "#c5cede", "#e35a68", "#2cc084", "#e0a428",
                      "#6782ff", "#a78bfa", "#22b8c8", "#0f1522")
        else:
            colors = ("#1a2336", "#e35d6a", "#3dd68c", "#e0c05c",
                      "#5b8cff", "#b48cff", "#5cc8d0", "#c7d5e0",
                      "#3a4a5a", "#ff7a8a", "#6be8a8", "#ffd97a",
                      "#7aa0ff", "#c9a8ff", "#7fe0e8", "#ffffff")
        palette = []
        for hex_color in colors:
            c = Gdk.RGBA(); c.parse(hex_color); palette.append(c)
        terminal.set_colors(fg, bg, palette)
    except Exception:
        pass


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

# ---------------------------------------------------------------------------
# 语言配置：zh / en / system，持久化到同一 config.json 的 language 字段
# system = 跟随系统语言（LANG/LC_*）；解析后的实际界面语言仍是 zh 或 en
# ---------------------------------------------------------------------------
LANG_MODES = ("zh", "en", "system")
_current_lang = "zh"          # 实际生效的界面语言：仅 zh / en
_lang_pref = "zh"             # 用户偏好：zh / en / system；无已存偏好时默认中文


def detect_system_lang():
    """根据系统 locale 判断界面语言：英文系用 en，其余默认 zh。"""
    for key in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        val = (os.environ.get(key) or "").strip()
        if not val:
            continue
        # LANGUAGE 可能是 en_US:zh_CN 这类列表，取第一项
        first = val.split(":")[0].strip().replace("-", "_")
        if not first or first.upper() in ("C", "POSIX"):
            continue
        low = first.lower()
        if low.startswith("en"):
            return "en"
        if low.startswith("zh"):
            return "zh"
        # 其他语言：工具箱目前只有中英，默认中文
        return "zh"
    return "zh"


def resolve_lang(pref=None):
    """把用户偏好解析成实际 zh/en。"""
    if pref is None:
        pref = _lang_pref
    if pref == "en":
        return "en"
    if pref == "zh":
        return "zh"
    return detect_system_lang()


def load_lang_pref():
    """读取语言偏好。无配置/无 language 字段时默认中文；已显式保存的偏好仍尊重。"""
    try:
        with open(_config_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        if "language" not in data:
            return "zh"
        lang = data.get("language")
        return lang if lang in LANG_MODES else "zh"
    except Exception:
        return "zh"

def save_lang_pref(lang):
    """保存语言偏好；失败不影响使用。"""
    if lang not in LANG_MODES:
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
        data["language"] = lang
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存语言设置失败: {e}")
        return False

def get_lang():
    return _current_lang

def get_lang_pref():
    return _lang_pref

def set_lang(lang):
    """设置界面语言。可传 zh/en/system；system 会解析为当前系统语言。"""
    global _current_lang, _lang_pref
    if lang in ("zh", "en"):
        _lang_pref = lang
        _current_lang = lang
    elif lang == "system":
        _lang_pref = "system"
        _current_lang = detect_system_lang()

# GTK UI 字符串表；内嵌 shell 用户可见输出通过 BASH_SCRIPT_EN / get_bash_script() 切换
_UI_STRINGS = {
    "app_title": {"zh": "Steam Deck 工具箱", "en": "Steam Deck Toolbox"},
    "search_placeholder": {"zh": "全局搜索功能...", "en": "Search all functions..."},
    "theme_tooltip": {"zh": "切换深色 / 浅色模式", "en": "Switch dark / light mode"},
    "lang_tooltip": {"zh": "切换语言 / Language", "en": "Switch language / 语言"},
    "lang_button": {"zh": "语言", "en": "Language"},
    "lang_zh": {"zh": "中文", "en": "中文"},
    "lang_en": {"zh": "English", "en": "English"},
    "lang_system": {"zh": "跟随系统", "en": "Follow System"},
    "cat_sidebar": {"zh": "功能分类", "en": "Categories"},
    "back_home": {"zh": "← 返回首页", "en": "← Home"},
    "home_title": {"zh": "控制台", "en": "Console"},
    "home_hint": {"zh": "选择一个分类开始", "en": "Pick a category to get started"},
    "cat_desc_support": {"zh": "关于本工具与维护信息", "en": "About this tool and maintenance"},
    "cat_desc_changelog": {"zh": "查看版本更新记录", "en": "See what changed in each version"},
    "cat_desc_sysopt": {"zh": "日常调校、兼容层、急救与引导", "en": "Daily tweaks, compatibility layers, emergency and boot"},
    "cat_desc_software": {"zh": "桌面应用、第三方平台与小工具", "en": "Desktop apps, third-party platforms and utilities"},
    "cat_desc_network": {"zh": "加速器与网络相关工具", "en": "Accelerators and network utilities"},
    "cat_desc_plugins": {"zh": "Decky 插件商店与插件", "en": "Decky plugin store and plugins"},
    "cat_desc_update": {"zh": "更新或卸载已装软件", "en": "Update or uninstall installed apps"},
    "help": {"zh": "帮助", "en": "Help"},
    "quit": {"zh": "退出", "en": "Quit"},
    "ok": {"zh": "确定", "en": "OK"},
    "theme_dark": {"zh": "深色", "en": "Dark"},
    "theme_light": {"zh": "浅色", "en": "Light"},
    "theme_system": {"zh": "跟随系统", "en": "Follow System"},
    "cat_support": {"zh": "支持和维护", "en": "Support & Maintenance"},
    "cat_changelog": {"zh": "更新日志", "en": "Changelog"},
    "cat_sysopt": {"zh": "系统优化", "en": "System Optimization"},
    "cat_plugins": {"zh": "插件相关", "en": "Plugins"},
    "cat_software": {"zh": "软件安装", "en": "Software Installation"},
    "cat_network": {"zh": "网络工具", "en": "Network Tools"},
    "cat_update": {"zh": "更新和卸载软件", "en": "Update & Uninstall"},
    "sys_dual": {"zh": "双系统", "en": "Dual Boot"},
    "sys_single": {"zh": "单系统", "en": "Single System"},
    "about_title": {"zh": "关于本工具", "en": "About This Tool"},
    "search_col_func": {"zh": "功能", "en": "Function"},
    "search_col_cat": {"zh": "分类", "en": "Category"},
    "search_results": {"zh": "搜索结果（{n} 项）", "en": "Search Results ({n} items)"},
    "search_none": {"zh": "搜索结果（无匹配）", "en": "Search Results (no matches)"},
    "status": {"zh": "系统: {sys} ｜ 终端: {term} ｜ 版本: v{ver}",
               "en": "System: {sys} ｜ Terminal: {term} ｜ Version: v{ver}"},
    "term_embedded": {"zh": "内嵌终端", "en": "Embedded"},
    "term_external": {"zh": "外部终端", "en": "External"},
    "danger_title": {"zh": "危险操作确认：{name}", "en": "Dangerous operation: {name}"},
    "danger_default": {
        "zh": "该功能会修改系统引导、挂载或系统文件，请确认已了解风险。",
        "en": "This will modify system boot, mount or system files; make sure you understand the risks.",
    },
    "help_body_zh": (
        "本工具集成了系统优化、软件安装、网络工具等功能。\n"
        "在首页点分类卡片进入功能列表，顶栏可全局搜索。\n"
        "小破站关注up主 AlanWake2100 可以来催更哦~"
    ),
    "help_body_en_markup": (
        "This tool integrates system optimization, software installation, network tools and more.\n"
        "Tap a category card on the home screen to open its tools; use the top search anytime.\n"
        "Follow <a href=\"https://x.com/AlanWake2100\">AlanWake (@AlanWake2100)</a> on X for updates~"
    ),
    "no_terminal": {"zh": "未找到可用的终端模拟器", "en": "No usable terminal emulator found"},
    "no_terminal_hint": {"zh": "请安装任一终端模拟器（如 konsole / kitty / foot / alacritty / xterm）后重试。",
                          "en": "Please install a terminal emulator (e.g. konsole / kitty / foot / alacritty / xterm) and try again."},
    "task_running": {"zh": "任务运行中", "en": "Running"},
    "task_done": {"zh": "任务已完成", "en": "Task completed"},
    "task_failed": {"zh": "任务失败", "en": "Task failed"},
    "task_cancelled": {"zh": "任务已取消", "en": "Task cancelled"},
    "task_running_confirm": {"zh": "有任务正在运行，是否终止并继续？",
                              "en": "A task is still running. Stop it and continue?"},
    "external_start": {"zh": "任务已在外部终端启动（PID {pid}），请查看弹出的终端窗口。",
                        "en": "Task started in an external terminal (PID {pid}). Check the popup window."},
    "external_done_ok": {"zh": "外部终端任务已完成（退出码 0）。",
                          "en": "External terminal task finished (exit code 0)."},
    "external_done_fail": {"zh": "外部终端任务失败（退出码 {rc}）。",
                            "en": "External terminal task failed (exit code {rc})."},
    "external_running_close": {"zh": "外部终端任务仍在运行，关闭窗口不会终止它。",
                                "en": "The external terminal task is still running; closing this window will not stop it."},
    "check_fail_button": {"zh": "检查更新失败，请检查网络连接。\n可点击进入主界面。",
                           "en": "Update check failed. Please check your network.\nClick to enter the main window."},
    "vte_manual_en": {"zh": "请手动打开终端执行：sudo pacman -S --noconfirm vte3",
                       "en": "Please open a terminal and run: sudo pacman -S --noconfirm vte3"},
    "fp_query_fail": {"zh": "无法查询已安装应用（flatpak 未安装或命令失败）。",
                       "en": "Could not query installed apps (flatpak missing or command failed)."},
    "fp_search_fail": {"zh": "flathub 搜索失败（flatpak 未安装或命令失败）：{err}",
                        "en": "Flathub search failed (flatpak missing or command failed): {err}"},
    "fp_no_apps_title": {"zh": "没有可卸载的 Flatpak 应用。",
                          "en": "No Flatpak apps available to uninstall."},
    "update_target_unsafe": {"zh": "无法确定自身脚本路径（{path}），为安全起见未执行替换。\n请手动下载新版本：{url}",
                              "en": "Cannot determine a safe self-update target ({path}); replacement skipped.\nDownload manually: {url}"},
    "update_ver_mismatch": {"zh": "下载内容版本号与检查结果不一致（期望 v{want}，实得 v{got}），已中止更新。",
                              "en": "Downloaded version does not match the check result (expected v{want}, got v{got}); update aborted."},
    "update_backup_fail": {"zh": "⚠️ 备份当前版本失败：{err}\n更新将继续，但出错时无法自动回滚。",
                            "en": "⚠️ Failed to back up the current version: {err}\nThe update will continue, but there is no automatic rollback."},
    "task_external": {"zh": "任务已在外部终端中运行，请查看弹出的终端窗口。",
                      "en": "The task is running in an external terminal. Check the popup window."},
    "close": {"zh": "关闭", "en": "Close"},
    "task_complete_btn": {"zh": "完成", "en": "Done"},
    "cancel": {"zh": "取消", "en": "Cancel"},
    "cancelling": {"zh": "正在取消...", "en": "Cancelling..."},
    "copy": {"zh": "复制", "en": "Copy"},
    "copy_tooltip": {"zh": "复制选中的终端内容；未选中时复制全部输出",
                     "en": "Copy the selected terminal content; copies all output when nothing is selected"},
    "copy_sel_ok": {"zh": "已复制选中内容", "en": "Selection copied"},
    "copy_fail": {"zh": "复制失败", "en": "Copy failed"},
    "copy_all_ok": {"zh": "已复制全部输出", "en": "All output copied"},
    "copy_empty": {"zh": "没有可复制的内容", "en": "Nothing to copy"},
    "copy_sel": {"zh": "复制选中内容", "en": "Copy Selection"},
    "copy_all": {"zh": "复制全部输出", "en": "Copy All Output"},
    "paste": {"zh": "粘贴", "en": "Paste"},
    "select_all": {"zh": "全选", "en": "Select All"},
    "maximize": {"zh": "最大化 / 还原", "en": "Maximize / Restore"},
    "elapsed": {"zh": "已运行 {m}:{s:02d}", "en": "Elapsed {m}:{s:02d}"},
    "elapsed_zero": {"zh": "已运行 0:00", "en": "Elapsed 0:00"},
    "start_fail": {"zh": "启动失败", "en": "Failed to start"},
    "check_update": {"zh": "检查更新", "en": "Check for Updates"},
    "checking_update": {"zh": "正在检查更新...", "en": "Checking for updates..."},
    "check_update_fail": {"zh": "检查更新失败，请检查网络连接。",
                          "en": "Update check failed. Please check your network."},
    "enter_main": {"zh": "进入主界面", "en": "Enter Main Window"},
    "already_latest": {"zh": "当前已是最新版本 (v{ver})", "en": "Already up to date (v{ver})"},
    "found_new": {"zh": "发现新版本", "en": "New version available"},
    "found_new_big": {"zh": "发现新版本 v{ver}", "en": "New version v{ver}"},
    "update_prompt": {"zh": "当前版本: v{cur}\n最新版本: v{remote}\n\n是否立即更新？",
                      "en": "Current: v{cur}\nLatest: v{remote}\n\nUpdate now?"},
    "updating": {"zh": "正在更新...", "en": "Updating..."},
    "updating_hint": {"zh": "正在下载新版本，请稍候。", "en": "Downloading the new version, please wait."},
    "update_ok": {"zh": "✅ 更新完成", "en": "✅ Update complete"},
    "update_ok_hint": {"zh": "新版本 v{ver} 已下载。\n程序即将自动重启...",
                       "en": "Version v{ver} downloaded.\nThe app will restart shortly..."},
    "update_fail": {"zh": "❌ 更新失败", "en": "❌ Update failed"},
    "update_fail_hint": {"zh": "更新过程中发生错误：{err}\n请手动从以下地址下载最新版本：\n{url}",
                         "en": "An error occurred while updating: {err}\nPlease download the latest version manually from:\n{url}"},
    "vte_missing": {"zh": "未检测到 VTE 终端组件。\n是否立即安装？(需要 sudo 密码，安装后请手动重启程序)",
                    "en": "VTE terminal component not found.\nInstall now? (sudo password required; restart the app afterwards)"},
    "vte_missing_hint": {"zh": "点击“是”将自动解除只读模式并安装 vte3。",
                         "en": "Choosing Yes will disable read-only mode and install vte3."},
    "yes": {"zh": "是", "en": "Yes"},
    "no": {"zh": "否", "en": "No"},
    "vte_manual": {"zh": "请手动打开终端执行：sudo pacman -S --noconfirm vte3",
                   "en": "Please open a terminal and run: sudo pacman -S --noconfirm vte3"},
}

# 功能显示名（及分组标题）；功能 key 保持不变
_FUNC_LABELS = {
    "install_chinese_source": {"zh": "切换软件源（国内/官方）", "en": "Switch Software Source (China/Official)"},
    "adjust_swap": {"zh": "调整虚拟内存", "en": "Adjust Virtual Memory"},
    "fix_disk_write_error": {"zh": "修复磁盘写入错误", "en": "Fix Disk Write Errors"},
    "clear_hosts_cache": {"zh": "清理hosts缓存", "en": "Clean hosts Cache"},
    "grp_calibrate": {"zh": "校准设备", "en": "Calibrate Device"},
    "calibrate_joystick_stick": {"zh": "校准摇杆", "en": "Calibrate Joystick"},
    "calibrate_joystick_trigger": {"zh": "校准扳机", "en": "Calibrate Triggers"},
    "steamdeck_cache_manager": {"zh": "Steam缓存管理", "en": "Steam Cache Manager"},
    "ge_proton_manager": {"zh": "兼容层管理", "en": "Compatibility Layer Manager"},
    "fix_boot": {"zh": "修复引导", "en": "Fix Boot"},
    "fix_shared_disk": {"zh": "修复互通盘", "en": "Fix Shared Disk"},
    "install_anydesk": {"zh": "AnyDesk", "en": "AnyDesk"},
    "install_todesk": {"zh": "ToDesk", "en": "ToDesk"},
    "install_asklink": {"zh": "AskLink远程", "en": "AskLink Remote"},
    "install_flatpak_apps_gui": {"zh": "安装 Flatpak 应用", "en": "Install Flatpak Apps"},
    "install_uu_accelerator": {"zh": "UU加速器插件", "en": "UU Accelerator Plugin"},
    "install_xunyou_accelerator": {"zh": "迅游加速器插件", "en": "Xunyou Accelerator Plugin"},
    "install_qiyou_accelerator": {"zh": "奇游联机宝加速插件", "en": "Qiyou Accelerator Plugin"},
    "grp_watt": {"zh": "Watt Toolkit (Steam++)", "en": "Watt Toolkit (Steam++)"},
    "watt_toolkit_install": {"zh": "安装", "en": "Install"},
    "watt_toolkit_trust_cert": {"zh": "信任证书", "en": "Trust Certificate"},
    "watt_toolkit_uninstall": {"zh": "卸载", "en": "Uninstall"},
    "grp_plugin_store": {"zh": "安装/卸载插件商店", "en": "Install/Uninstall Plugin Store"},
    "install_plugin_store": {"zh": "安装插件商店", "en": "Install Plugin Store"},
    "uninstall_plugin_store": {"zh": "卸载插件商店", "en": "Uninstall Plugin Store"},
    "grp_tomoon": {"zh": "ToMoon 插件", "en": "ToMoon Plugin"},
    "install_tomoon_install": {"zh": "安装/更新 ToMoon", "en": "Install/Update ToMoon"},
    "install_tomoon_uninstall": {"zh": "卸载 ToMoon", "en": "Uninstall ToMoon"},
    "grp_freedeck": {"zh": "Freedeck 插件", "en": "Freedeck Plugin"},
    "install_freedeck_install": {"zh": "安装/更新 Freedeck", "en": "Install/Update Freedeck"},
    "install_freedeck_uninstall": {"zh": "卸载 Freedeck", "en": "Uninstall Freedeck"},
    "grp_lsfg": {"zh": "LSFG-VK插件", "en": "LSFG-VK Plugin"},
    "install_decky_lsfg_vk_install": {"zh": "安装/更新 LSFG-VK", "en": "Install/Update LSFG-VK"},
    "install_decky_lsfg_vk_uninstall": {"zh": "卸载 LSFG-VK", "en": "Uninstall LSFG-VK"},
    "grp_framegen": {"zh": "Framegen插件", "en": "Framegen Plugin"},
    "install_decky_framegen_install": {"zh": "安装/更新 Framegen", "en": "Install/Update Framegen"},
    "install_decky_framegen_uninstall": {"zh": "卸载 Framegen", "en": "Uninstall Framegen"},
    "clover_install_or_reinstall": {"zh": "安装/重装 Clover", "en": "Install/Reinstall Clover"},
    "update_installed_apps": {"zh": "更新已安装应用", "en": "Update Installed Apps"},
    "grp_uninstall_apps": {"zh": "卸载已安装应用", "en": "Uninstall Installed Apps"},
    "uninstall_anydesk": {"zh": "卸载 AnyDesk", "en": "Uninstall AnyDesk"},
    "uninstall_todesk": {"zh": "卸载 ToDesk", "en": "Uninstall ToDesk"},
    "uninstall_other_flatpak_apps": {"zh": "卸载其他已安装应用", "en": "Uninstall Other Installed Apps"},
    "grp_cheatdeck": {"zh": "CheatDeck 插件", "en": "CheatDeck Plugin"},
    "install_cheatdeck_install": {"zh": "安装/更新 CheatDeck", "en": "Install/Update CheatDeck"},
    "install_cheatdeck_uninstall": {"zh": "卸载 CheatDeck", "en": "Uninstall CheatDeck"},
    "grp_emergency": {"zh": "急救重置", "en": "Emergency Reset"},
    "grp_boot": {"zh": "引导与双系统", "en": "Boot & Dual Boot"},
    "emergency_steam_reset": {"zh": "重置 Steam 配置", "en": "Reset Steam Config"},
    "emergency_gamescope_reset": {"zh": "重置 Gamescope/游戏模式", "en": "Reset Gamescope / Game Mode"},
    "install_yellow_duck_software": {"zh": "小黄鸭软件", "en": "Yellow Duck Software"},
    "grp_third_party": {"zh": "安装/卸载第三方游戏平台", "en": "Install/Uninstall Third-party Game Platforms"},
    "install_third_party_platform": {"zh": "安装第三方游戏平台", "en": "Install Third-party Game Platform"},
    "uninstall_third_party_platform": {"zh": "卸载第三方游戏平台", "en": "Uninstall Third-party Game Platform"},
}

_DANGER_HINTS_I18N = {
    "clover_install_or_reinstall": {
        "zh": ("该功能会向 EFI 系统分区写入 Clover 引导文件，"
               "替换 BOOTX64.EFI 并修改 EFI 启动项。\n"
               "操作不当可能导致设备无法开机，请确认已了解风险并做好备份。"),
        "en": ("This will write Clover boot files to the EFI system partition, "
               "replace BOOTX64.EFI and modify EFI boot entries.\n"
               "Improper operation may make the device unbootable; make sure you understand the risks and have a backup."),
    },
    "fix_boot": {
        "zh": "该功能会修改 EFI 启动顺序，把 Clover 设为第一启动项。",
        "en": "This will modify the EFI boot order and set Clover as the first boot entry.",
    },
    "fix_shared_disk": {
        "zh": "该功能会修改 /etc/fstab 与 UDisks2 策略文件，用于自动挂载 Windows 分区。",
        "en": "This will modify /etc/fstab and the UDisks2 policy file to auto-mount the Windows partition.",
    },
    "uninstall_plugin_store": {
        "zh": "该功能会删除已安装的插件商店及其插件数据。",
        "en": "This will delete the installed plugin store and its plugin data.",
    },
    "clear_hosts_cache": {
        "zh": "该功能会修改系统 /etc/hosts 文件（会自动备份）。",
        "en": "This will modify the system /etc/hosts file (a backup is created automatically).",
    },
    "emergency_steam_reset": {
        "zh": ("将备份并重置 Steam 客户端配置/启动缓存，用于卡启动、配置损坏等急救。\n"
               "不会删除 steamapps 游戏本体；本地 Steam 设置可能丢失。操作前会自动备份到\n"
               "~/steamdeck_toolbox_backups/。"),
        "en": ("Backs up then resets Steam client config / launch caches for startup hangs or broken config.\n"
               "Does not delete steamapps game installs; local Steam settings may be lost.\n"
               "An automatic backup is written under ~/steamdeck_toolbox_backups/."),
    },
    "emergency_gamescope_reset": {
        "zh": ("将备份并清理 Gamescope / 游戏模式相关本地状态与部分 Steam UI 缓存，\n"
               "用于黑屏、进不去游戏模式等。不删游戏本体；操作前自动备份。"),
        "en": ("Backs up then clears Gamescope / Game Mode local state and some Steam UI caches\n"
               "for black screens or Game Mode boot issues. Games are not deleted; auto-backup first."),
    },
}

def t(key, **kwargs):
    entry = _UI_STRINGS.get(key)
    if not entry:
        return key
    if isinstance(entry, str):
        s = entry
    else:
        s = entry.get(_current_lang) or entry.get("zh") or key
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s

def fl(key):
    """功能 / 分组显示名。"""
    entry = _FUNC_LABELS.get(key)
    if not entry:
        return key
    return entry.get(_current_lang) or entry.get("zh") or key

def theme_label(mode):
    return t(f"theme_{mode}")

def system_type_display(system_type):
    """system_type 内部仍为「双系统」/「单系统」，仅显示时翻译。"""
    if system_type == "双系统":
        return t("sys_dual")
    return t("sys_single")

def dangerous_hint(func_key):
    entry = _DANGER_HINTS_I18N.get(func_key)
    if entry:
        return entry.get(_current_lang) or entry.get("zh")
    return t("danger_default")

def changelog_body_text():
    """更新日志正文：中英各一份。"""
    if get_lang() == "en":
        return CHANGELOG_BODY_EN
    return CHANGELOG_BODY_ZH

CHANGELOG_BODY_ZH = """2026-11-11（v2.1.3）
【维护：安装与自更新】
- 本次只改链接，没有功能变化
- 安装与自更新的 GitHub 地址改为 `main` 分支，不再使用 `master`
- 已安装的 v2.1.2 仍会从 `master` 拉取更新。请先升级到本版本，
  这样之后删除 `master` 才不会打断自动更新

2026-11-10（v2.1.2）
【问题修复：安装器】
- 修复 `install_gui.sh` 把 `pacman -Sy` 的失败与错误输出一并吞掉，导致装 vte3 时
  只显示含糊的「无法找到数据库」：现在会保留同步输出、检查返回码，失败时直接给出排查方向
- 新增废弃仓库检测：如果 `/etc/pacman.conf` 残留 `[community-3.9]`（SteamOS 3.9 已把
  community 合并进 extra，服务器不再提供 community-3.9.db），提前提示并给出修复命令，
  避免用户误以为是工具箱或「切换软件源」的问题

2026-11-10（v2.1.1）
【问题修复】
- 修复「更新全部应用」的下载进度刷屏：百分比、下载速度、进度条与
  「正在更新 X/Y」过渡帧现在合并为一行原地刷新，普通日志与完成提示才换行显示

2026-11-09（v2.1.0）
【全功能问题排查与修复】
- 逐项检查了工具箱全部功能（系统优化、双系统、插件、软件安装、网络工具、
  界面与自更新），修复下面的确定问题，并补充了跨设备依赖检查

【安全：下载与 root 执行】
- UU / 迅游 / 奇游加速器不再把明文 HTTP 内容直接管道给 root：改为 HTTPS、超时与
  HTTP 状态检查、下载到临时文件后校验是 shell 文本、显示来源，校验通过直接由 sudo
  提示密码执行；不再显示脚本预览和二次确认，体验回到「直接开始安装」
- 奇游：sd.qiyou.cn 只提供 HTTP、443 未开放，导致上一版统一改 HTTPS 后连不上。
  现改为直接取支持 HTTPS 的真实安装脚本 static.qiyou.cn/.../qyplug.sh；
  同时给下载 helper 增加「HTTPS 失败自动回退 HTTP 并明确警告」的通用能力
- Watt 证书信任：不再把 /etc/hosts 改成所有人可写；保存并恢复原权限，校验
  CA:TRUE 与 SHA256 指纹，卸载按指纹精确清理，程序目录已删时也能清理证书与权限
- Epic / 战网 / 育碧卸载前列出将删除的路径并二次确认，避免误删默认目录里的游戏

【安装器与任务窗】
- 安装器改为临时文件 + 标记/大小/语法校验通过后才原子替换，失败保留旧版；
  只读模式只恢复脚本自己关掉的那一次，不覆盖用户原本可写的设置
- 任务取消不再显示「任务已完成」，改为「任务已取消」；已有任务在跑时切换功能先确认；
  关闭 Flatpak 窗口会真正终止进程，附加包失败不再被主包成功掩盖
- 补充 XDG 桌面目录、更多终端模拟器、Flatpak 缺失与查询失败的明确提示，
  双系统探测放宽，避免 Clover 用户看不到修引导与互通盘入口

【引导与系统】
- 修复 Clover 文件检查返回码被 `local` 吞掉、可能给不存在的文件注册启动项的问题
- 交换分区操作失败时不再继续删除旧 Swap；Steam / Gamescope 急救在备份失败时
  立即中止，不再删除无法恢复的原配置
- 「清理虚拟内存配置」改为按 ZRAM 重置后的实际状态判定，修掉「实际已清理成功
  却误报 ZRAM 重置失败」；NTFS 修复失败会真实反映在结果里
- 「切换 Flatpak 软件源」当前地址能匹配到 5 个预设源时直接显示对应名称（如
  「中科大-联通节点」），不再只显示一串 URL
- 引导文件配置工具按工具箱语言联动：中文界面用汉化版，英文界面保留社区原版英文

【Watt Toolkit / 软件安装】
- 修掉安装 Watt 时删除临时工作目录导致后续每条 sudo 刷上百行
  `getcwd: 无法访问父目录`；备份改到同一文件系统，复制时不带
  security.capability xattr，修掉 `mv: setting attribute ... 不允许的操作`
- 证书信任改为显式写入系统 anchors 目录并刷新证书包，再用 openssl verify 验证
  是否真正生效（此前「✓ 已加入」但 HTTPS 加速仍会报证书错误）；hosts 及整体
  结果都按实际状态判定，不再假成功
- 同版本不再误报更新（v3.1.0 与 3.1.0）；ToDesk / AnyDesk / 小黄鸭等不再
  「先删旧版再装」导致半安装，下载、解压、服务启动、卸载与更新的失败都会如实反映
- 「更新全部应用」恢复显示下载百分比与速度：去掉 --noninteractive、启用
  FLATPAK_TTY_PROGRESS，并用过滤器把原地刷新转成干净逐行文本，不重现乱码

【插件商店】
- Decky 服务用户不再写死 deck 并补齐官方字段；卸载插件商店会停止、禁用并删除
  systemd 服务与 CEF 标记；插件安装改为临时目录校验后再替换，失败保留旧插件

【依赖与兼容性】
- 补充 GTK3/VTE3、flatpak、p11-kit、openssl、ntfs-3g/ntfsprogs、efibootmgr、7z、
  jupiter-hw-support 等依赖的检查与提示；未在其他发行版上假定这些组件一定存在

2026-11-08（v2.0.4）
【修复互通盘】
- 脏卷(NTFS dirty)不再「假成功」：卷带脏标志、或 Windows 用了快速启动/休眠没真正关机时，
  Linux 的 NTFS 驱动不会报错，而是悄悄把分区挂成只读。旧版只看挂载命令的返回值，
  于是显示「✓ 挂载成功」，实际一个文件都写不进去。现在挂载后会回查实际挂载选项，
  是只读就明确提示，并给出能真正解决的处理步骤
- 修复「已挂载但为只读」时仍提示「所有分区均已挂载，无需操作」：该提示会让脏卷用户
  误以为一切正常。现在只读挂载被视为未就绪，会继续往下修复
- 挂载失败不再只丢一句「请检查 dmesg 输出」：现在只读取本次操作新产生的内核日志
  （不再把开机以来的旧报错当成本次问题），识别出「卷脏 / 休眠 / 未干净卸载」后
  直接给出对应步骤——进 Windows 关快速启动完整关机、用 ntfsfix 清标志、或应急只读/强制挂载
- 开工前先输入一次管理员密码，并自动检查 NTFS 工具：缺 ntfs-3g 就自动装上（缺它根本挂不了），
  缺 ntfsfix 只给警告不中断（只在清脏标志时才用得到）。不再让用户自己去装
- 修复 fstab 把挂载用户写死成 uid=1000,gid=1000 的问题：用户名不是 deck 或 UID 不是 1000
  的设备上，分区挂上了却读写不了。现在按当前实际用户写入
- 挂载前用 ntfs-3g.probe 预检该卷能否读写挂载：能读写就直接挂，不能就先把原因和处理方式
  说清楚，不必等挂完才发现是只读

【修复磁盘写入错误】
- 流程改为「先输入管理员密码 → 按需解除 SteamOS 只读 → 缺工具自动安装」，
  不再一上来就提示「未安装 ntfsfix」让用户自己去装
- 修复安装提示给错包名：旧版让装 ntfs-3g，但 ntfsfix/ntfsinfo 在 Arch/SteamOS 上属 ntfsprogs，
  照提示装完依然缺工具。现在自动安装正确的包，两类系包名差异也已分清
- 调用 ntfsfix 时加上 -d（清除 dirty 脏标志），避免修复完标志仍在、ntfs3 驱动依旧拒绝挂载
【全功能问题修复】
- 安全：UU / 迅游 / 奇游不再用明文 HTTP 把远端脚本直接管道给 root，改为 HTTPS、
  超时与 HTTP 状态检查、临时文件校验、显示来源并二次确认后再执行
- 安全：Watt 证书信任不再把 /etc/hosts 改成所有人可写；保存并恢复原权限，
  校验 CA 属性与指纹，卸载按指纹精确清理，程序目录已删时也能清理证书与 hosts 权限
- 安全：Epic / 战网 / 育碧等卸载前列出将删除的路径并二次确认，避免误删默认目录里的游戏
- 安装器：下载改为临时文件 + 标记/大小/语法校验通过后才原子替换，失败保留旧版；
  只读模式只恢复脚本自己关掉的那一次，不覆盖用户原本可写的设置
- 任务窗：取消不再显示「任务已完成」，改为「任务已取消」；已有任务在跑时切换功能会先确认；
  关闭 Flatpak 窗口会真正终止进程，附加包失败不再被主包成功掩盖
- 引导：修复 Clover 文件检查返回码被 `local` 吞掉、可能给不存在的文件注册启动项的问题；
  交换分区操作失败时不再继续删除旧 Swap
- 急救：Steam / Gamescope 重置在备份失败时立即中止，不再删除无法恢复的原配置
- 插件商店：服务用户不再写死 deck 并补齐官方字段；卸载会停止、禁用并删除 systemd 服务；
  插件安装改为临时目录校验后再替换，失败保留旧插件
- 软件安装：ToDesk / AnyDesk / Watt / 小黄鸭等不再「先删旧版再装」导致半安装，
  下载、解压、服务启动、卸载与更新的失败都会真实反映在结果里
- 兼容性：补充 XDG 桌面目录、更多终端模拟器、Flatpak 缺失与查询失败的明确提示，
  双系统探测放宽，避免 Clover 用户看不到修引导与互通盘入口


2026-11-07（v2.0.3）
【问题修复】
- 修复「功能点了没反应」：GTK 回调里抛异常时错误只写到终端，而用桌面快捷方式启动根本看不到，
  表现出来就是点了毫无反应。现在任何未捕获异常都会弹窗提示「这个功能执行出错，已跳过」，
  完整堆栈写入 ~/.cache/steamdeck_toolbox_error.log，反馈问题时把该文件发来即可定位
- 修复缺少 VTE 组件时，启动弹出的「是否安装 vte3」提示框会吞掉主界面所有点击：
  该框是模态且没有父窗口，部分桌面环境下会跑到主窗口背后，用户看到工具箱窗口在、
  但点点什么反应都没有。改为非模态并置顶显示，即使框被压到后面，主界面也照常可用
- 功能窗口打开后主动置顶到最前，避免在部分桌面环境下新窗口被主窗口挡住

2026-11-05（v2.0.2）
【界面重构：原生 GTK 窗口】
- 「安装 Flatpak 应用」与「卸载其他已安装应用」改为原生 GTK 窗口，不再调用 zenity
  · 应用列表、勾选框、进度条、结果全部在主程序自己的窗口里，主题与主界面一致
  · 卸载时的「是否删除本地数据」也并入同一窗口，不再额外弹窗
  · 彻底修复「点取消或关窗后安装仍在后台继续」：改由 Python 直接启动 flatpak，
    点取消就是终止该进程本身，实测 0.5 秒内退出，应用不会被装上
  · 新增应用搜索框：先匹配内置清单秒出结果，没有匹配时再自动搜索 flathub，远端结果同样可勾选安装
  · 按钮精简为单一主按钮，按阶段自动切换（安装 / 取消 / 完成 / 返回列表），未勾选时自动隐藏
  · 装完或卸完回到列表可继续操作，不必反复进出功能入口
  · 安装过程中搜索框自动隐藏，只在选择应用时有意义
  · 勾选状态在搜索、切换查询、远端结果返回后都会保留，不会被重绘冲掉
- 「Steam 缓存管理」改为原生 GTK 窗口
  · 打开即列出着色器缓存与兼容数据，选类型后自动扫描全部 Steam 库（默认库 + libraryfolders.vdf 登记的其它库）
  · 列表显示应用名与占用大小并按大小排序，底部实时显示已选数量与总大小
  · 删除前有独立确认页列出待删条目；删除中显示「正在删除 2/3：应用名」与实时进度，可随时取消
- 「兼容层管理」改为原生 GTK 窗口，一个窗口管理三套兼容层（GE-Proton、Proton-CachyOS、DW Proton）的安装与卸载
  · 版本列表联网从 GitHub Releases 读取，安装页自动跳过已装版本，卸载页只列当前已安装的目录
  · 确认页可选下载镜像（gh-proxy.com / gh.3w.pm / cors.isteed.cc / ghproxy.net / GitHub 官方），整批共用同一镜像
  · 下载显示真实字节进度（如「128.0 MB / 540.6 MB」），不再是空转动画
  · 下载完成做双重校验：先比对文件大小，再核对 sha512 摘要，任何一项对不上就判失败并说明原因，
    绝不把坏包解压进 Steam；解压先落临时目录，校验通过才移入正式目录，中途取消不留半成品
  · 失败时逐条列出「· 版本号：原因」，如「sha512 校验失败，包已损坏」「这个版本没有适合 Deck 的 x86_64 安装包」
  · 取消响应约 0.5 秒（改用 read1 逐段读取，取消时直接对底层 socket 做 shutdown）
  · 镜像源带失败检测与自动换源：连不上、下到一半断开、文件大小或 sha512 对不上，都会自动换下一个镜像重试，
    全部镜像都失败才报错，并逐条列出每个镜像的具体失败原因
  · 取消覆盖「获取版本列表」「获取下载信息」「下载」「取校验值」全过程；此前只有下载中能取消，前面几步点取消毫无反应
  · 取消后回到版本列表而不是初始页，已勾选的版本保留，可直接换镜像或换版本重试

【安装 / 卸载整合】
- 软件安装分类里通过 Flatpak 安装的 8 个应用合并为一个「安装 Flatpak 应用」入口；
  卸载已安装应用里的 8 个 Flatpak 卸载入口一并并入「卸载其他已安装应用」
  · 关键修正：该卸载界面原先把这 8 个应用列在排除名单里（因为它们当时各有专属卸载入口），
    专属入口删掉后若不清理名单，这 8 个应用将永远无法卸载；现已清空，
    仅保留 Fcitx 5 中文插件作为内部组件随主程序移除
  · 卸载列表从固定名单改为实时读取 flatpak list，装了什么就能卸什么

【功能扩充】
- 「安装 Flatpak 应用」的可选应用从 8 个扩充到 37 个，覆盖日常、办公、影音、创作、远程与游戏工具
  · 通讯 7 个、浏览器 3 个、影音 4 个、网盘与下载 2 个、办公与笔记 5 个、
    创作工具 6 个、远程控制 2 个、游戏工具 6 个、系统工具 2 个
- 37 个应用 ID 全部内置，打开列表不再联网查询，离线也照常完整显示，打开速度从 3 秒多降到 1 秒内
  · 顺带优化：flatpak remote-add 即使 flathub 已存在也会联网约 1.1 秒，改为先本地检查，已存在就跳过

【问题修复】
- 修复勾选后提示「失败的 ID: 飞书」这类安装必定失败的问题
  · 根因：zenity 勾选列表的第一列必须是勾选状态列，遗漏它会让后续列全部错位，
    且未指定回传列时拿到的值是应用显示名而非应用 ID，于是执行的是 flatpak install flathub 飞书
  · 修法：第一列放勾选状态，第二列放真实应用 ID 并隐藏，回传即纯 ID；另加白名单校验杜绝脏数据
- 修复安装进度显示 100% 但实际还在下载
  · 根因：flatpak 装一个应用会拆成多个子任务（运行时、本地化、主程序…），每段各自 0 到 100%，
    原实现只取段内百分比，第一段到 100% 进度条就满了
  · 修法：解析「第几步/共几步」，按已完成子任务数折算真实总进度
- 修复安装/卸载失败时不显示原因（或只显示一个字母）
  · 非进度输出行被整体丢弃，flatpak 的真实报错看不到；现在会列出「未在远程仓库 flathub 中发现 xxx 的匹配项」等原始报错
- 修复卸载后桌面快捷方式没有被删除
  · 根因：安装时快捷方式用显示名命名（飞书.desktop、Google Chrome.desktop），卸载却按应用 ID 匹配，永远对不上
  · 修法：改为读 .desktop 的 Exec 行，凡是 flatpak run <该应用ID> 的快捷方式都删除，与文件名无关
- 修复点取消或关闭进度窗后整个功能直接结束、没有回到应用选择界面
  · 根因：内嵌脚本开头的 INT/TERM trap（用于关掉终端就结束工具）会被进度窗关闭的信号触发
- 修复取消后 flatpak 实际没被终止、仍在后台下载（改为整进程组清理，连同孙进程一并带走）
- 修复卸载完点「返回列表」后列表一片空白（重绘后未调用 show_all，新建行默认隐藏）
- 修复桌面目录不存在时创建快捷方式报「没有那个文件或目录」（按 XDG 规范解析并自动创建）
- 修复进度条百分比为空、百分比重复显示、进度条倒退等问题
- 修复离线时所有应用被误判为「不存在」而全部隐藏（界面变空像是坏了）

【其他】
- 移除「系统体检」功能（暂时不需要）：侧栏入口、搜索索引、危险操作确认同步清理，
  内嵌脚本中的 6 类检查与配套修复流程一并删除；「修复引导」「修复互通盘」不受影响
- 删除被 GTK 窗口取代的 50 个 bash 函数（中英两段共 100 处定义，约 4160 行）
  · 体检 14 个、Flatpak 安装卸载 19 个、Steam 缓存管理 1 个、兼容层 16 个
  · Python 侧已直接打开对应 GTK 窗口，这些函数不会再被调用

2026-11-03（v2.0.1）
【问题修复】
- 修复「AskLink远程」安装 dpkg 时因 /var/lib/dpkg/{available,status} 残留报「文件系统中已存在」冲突：先常规安装，失败再用 --overwrite '/var/lib/dpkg/*' 覆盖残留后重试，并校验 dpkg 可用
- 修复内嵌脚本 EXIT trap 强制 exit 0，导致失败任务仍显示「任务已完成」：保留真实退出码，任务窗按成功/失败分别显示「任务已完成」/「任务失败」

【体验优化】
- 无已保存语言偏好时默认中文（显式选过的 zh/en/system 仍尊重）
- 顶栏语言入口改为直接显示文字「语言」/ Language，一眼能懂
- Steam Deck 等小屏默认窗口略缩小，边距更舒服
- 启动检查更新后点「是」的更新过程，复用同一个检查更新窗口（同尺寸，不再跳到另一块对话框）

2026-11-02（v2.0.0）
【问题修复】
- 修复「更新全部应用」进度条后面出现乱码的一串字符（^[[20;68R^[[20;68R^[[20;77R）
  · 根因：flatpak 画进度条前先发 ESC[6n 问终端「光标在哪」，VTE 按协议把
    ESC[行;列R 写回终端的输入方向；而终端默认开着 ECHO，内核就把这串应答
    回显到屏幕上，于是成了看得见的乱码
  · 修法：给 flatpak update 加上 --noninteractive，让它走纯文本逐行输出、
    不画 ANSI 进度条。没有进度条就不会发光标查询，从源头消除乱码
  · 实测对比（同一台机器、同样无更新的状态）：
    默认 → 转义符 31 个，含 ANSI 加粗与光标控制；加该参数后 → 转义符 0 个
  · 为什么不用「关掉终端 ECHO」的办法：那只是让应答不显示，字节仍留在输入
    缓冲区里，后续 read 会读到残留（实测 read -n1 取到的是 ESC 而不是用户
    按的键），比乱码更严重，故不采用
  · 代价：输出更精简、不再显示百分比进度条，但每步仍有文字反馈

【版本】
- 版本号升至 2.0.0：功能与稳定性已较 1.x 有较大积累，标记为正式版

2026-11-02（v1.11.4）
【体验优化】
- 「更新全部应用」精简输出提示
  · 移除「已跳过刷新软件目录(appstream)」那三行说明：这是实现细节，用户不需要知道。
    实测 flatpak update 默认并不刷新 appstream（只有显式加 --appstream 参数才会），
    所以本来就不存在该步骤，提示属于多余
  · 有更新时同样不涉及 appstream 刷新，超时提示里那句「若卡在更新 appstream 数据」
    也一并删掉，只保留「已下载部分不会丢失」这类有用信息
  · 更新完成提示精简为「✓ 所有应用更新完成」，不再附带「当前均为最新版本」等赘述

2026-11-02（v1.11.3）
【问题修复】
- 修复启动「检测更新」结束后任务栏图标消失：先显示主窗口再关闭更新检查窗；统一 WM_CLASS=Steamdeck-toolbox，桌面快捷方式补 StartupWMClass；更新闪屏不占任务栏

2026-11-02（v1.11.2）
【界面改进】
- 侧栏精简为 7 项：支持和维护、更新日志、系统优化、插件相关、软件安装、网络工具、更新和卸载
  · 兼容层、急救重置、Clover/双系统检修全部收进「系统优化」底部分组（默认折叠）
  · 去掉独立的游戏兼容 / 急救与恢复 / 引导与双系统 / 其他
  · 小黄鸭并入「软件安装」；第三方游戏平台仍在软件安装分组内
- 启动默认仍为「支持和维护」

2026-11-02（v1.11.1）
【界面改进】
- 信息架构重排：侧栏按「日常优化 → 游戏兼容 → 插件 → 装软 → 网络 → 急救 → 引导/双系统 → 卸载 → 其他」组织
  · 系统优化只保留源/虚拟内存/磁盘/hosts/校准/Steam 缓存
  · 新增「游戏兼容」承载兼容层管理（GE / CachyOS / DW）
  · 新增「急救与恢复」：Steam / Gamescope 重置
  · 「引导管理」改为「引导与双系统」，双系统体检/修引导/互通盘归入此分类
  · 第三方游戏平台并入「软件安装」；「其他」仅保留小黄鸭等杂项
- 分组折叠默认仍收起；启动默认仍打开「支持和维护」

2026-11-02（v1.11.0）
【新功能】
- 「GE-Proton 管理」扩展为「兼容层管理」：同一入口管理 GE-Proton、Proton-CachyOS(SLR)、DW Proton
  · CachyOS 仅安装 SLR 的 x86_64 包到 ~/.local/share/Steam/compatibilitytools.d/
  · DW Proton 走 dawn-winery/dwproton-mirror；文案标明偏二次元/特定游戏，与 CheatDeck 分开展示
  · 复用 GE 的镜像源选择、体积/sha512 校验、先解压到临时目录再迁入的安全安装流程（tar.xz）
- 插件相关新增 CheatDeck：只下载资产 CheatDeck.zip；安装前检查 Decky、提示开发者模式与 ToS 免责，不附带修改器
- 系统优化新增「急救重置」：Steam 配置重置、Gamescope/游戏模式重置；强制确认，操作前自动备份到 ~/steamdeck_toolbox_backups/

2026-11-02（v1.10.0）
【界面改进】
- 主窗口尺寸改为按屏幕自适应，不再固定 1100x720
  · 原因：原尺寸在 Steam Deck（1280x800，可用工作区 1280x746）上，
    窗口内容 720 + 标题栏约 40 = 760px，超出可用高度，底部被挤出屏幕
  · 现在启动时读取显示器 workarea（已扣除顶部面板），按可用高度分三档计算：
    - 小屏/掌机（可用高 < 900）：占比 86%x92%，上限 1400x820
    - 1K（可用高 < 1150）：占比 82%x88%，上限 1700x1000
    - 2K/4K 大屏：占比 72%x78%，上限 2000x1300
  · 实际效果：掌机 1100x686、1K 1574x915、2K 1843x1092、4K 2000x1300，
    既不会占满整个屏幕，也不会小到看不清
- 任务窗口（终端）同样跟随自适应，比主窗口小一号（缩放系数 0.8）：
  掌机 880x549、1K 1259x732、2K 1474x873
- 用 workarea 而非物理分辨率，且设置了兜底：即使屏幕小于最小尺寸，
  窗口也不会超出可用区域；取不到显示器信息时退回原来的 1100x720

2026-11-02（v1.9.9）
【问题修复】
- 修复「安装 ToDesk」重装时报「无法提交处理 (有冲突的文件) / 文件系统中已存在 /opt/todesk/bin/...」：
  根因是机器处于「孤儿残留」状态——pacman 数据库里已无 todesk-bin 记录（卸载被中断、
  手动删过数据库、或当初解包安装），但 /opt/todesk 等文件仍留在系统里。原清理逻辑是
  「pacman 有记录才卸载」，这种状态下判断为假，清理被整体跳过，于是 pacman -U 发现要写的
  文件已存在，直接拒绝安装
- 现在安装前增加孤儿文件清理：包未登记但文件仍在时，先停服务、结束占用进程，
  再清除 /opt/todesk、/usr/bin/todesk、todeskd.service、todesk.desktop、licenses 目录、
  hicolor 下 todesk 图标以及 pacman 的 db.lck 残留锁，然后才安装
- 清理后做了复核：仍有残留会明确列出路径并提示手动删除，不再让 pacman 抛看不懂的冲突错误
- 只删 todesk 自己的图标，不影响 hicolor 目录下其他软件；pacman 包正常登记的机器不触发此逻辑

2026-11-02（v1.9.8）
【界面改进】
- 主界面改为 SteamOS / OLED 风主从布局：左侧常驻分类轨，右侧即时显示对应内容，
  不再使用首页 3×3 大卡片再钻二级页
- 深色主题近黑底 + 紫/品红选中与青蓝强调；浅色主题同步可用
- 功能行卡与右侧滚动条错开，避免 chevron 与滚动条重叠
- 启动默认选中并打开「支持和维护」，右侧直接显示关于/维护正文（与手动点击一致）
【说明】
- 语言切换、主题、全局搜索、危险确认、任务窗与脚本业务逻辑保持不变
- 制作人：Zhucy

2026-11-01（v1.9.7）
【新功能】
- 新增界面语言切换（中文 / English）：顶栏可随时切换，偏好写入
  ~/.config/steamdeck_toolbox/config.json 的 language 字段，下次启动自动恢复
- 英文模式下界面文案、分类/功能名、更新日志、对话框按钮（含 Yes / No / OK）、
  以及内嵌终端脚本的用户可见输出均为英文；中文模式保持中文
- 帮助页按语言分流：中文仍保留 B 站催更入口；英文显示可点击的 X 链接
  @AlanWake2100（https://x.com/AlanWake2100）
【界面改进】
- 制作人署名改为 Zhucy（中英文一致）
- 危险确认等对话框不再依赖系统语言的「是/否」「确定」按钮文案，改为跟随工具箱语言
- 说明：系统 sudo 密码提示语仍随本机系统语言显示，属于正常现象，并非工具箱文案

2026-10-27（v1.9.6）
【问题修复】
- 修复「切换软件源」每次都会误报「无法下载 flathub 公钥」的警告：
  · 原因：原逻辑每次切源都无条件去 dl.flathub.org 重新下载一遍公钥，而该站经常连不上，
    于是每次都打一条黄字警告。但公钥是「导入一次就长期有效」的，正常设备上早就有了
    （/var/lib/flatpak/repo/flathub.trustedkeys.gpg），功能完全正常，这条警告纯属误导
  · 现在先检查本地是否已有可用公钥（并用 gpg 确认里面确实是 Flathub 的密钥，
    避免损坏的空壳文件误判），有就直接跳过下载，不再打印任何警告
  · 本地确实没有时才去下载，且按「官方 → 中科大 → CERNET」依次尝试
  · 只有真的全都拿不到才告警，并明确写出后果（安装/更新会报 Could not find public key）
    和两条手动修复命令，而不是让用户猜

2026-10-26（v1.9.5）
【问题修复】
- 修复「更新全部应用」在提示「没有更新。」之后长时间卡住：
  · 根因：flatpak update 的流程是「先查更新 → 再刷新 appstream 元数据」。第二步要去
    dl.flathub.org 拉约 10MB 的 appstream 数据，而该站当前连通率极低（实测 8 次试连
    只有 1 次成功），连接超时后还会重试 5 轮，于是卡在「正在为远程仓库 flathub 更新
    appstream 数据」几分钟甚至更久
  · 但 appstream 只是软件介绍/图标等展示用元数据，和「能不能更新」完全无关，
    所以现在改为直接跳过它：用 remote-ls 查更新（只刷新 summary，走镜像站，很快），
    再按需执行 update
  · 现在没有更新时会明确显示「所有已安装应用均为最新版本，无需更新」，不再卡住
  · 联网检查失败时先退回本地缓存判断；缓存里也没有才报「无法检查更新」，不会假装最新
  · 更新下载加了 20 分钟超时，超时会明确提示而不是静默挂起；更新完再用本地缓存复核一遍，
    还有残留会列出来

【功能改进】
- 「安装国内源」改为「切换软件源（国内/官方）」，改为菜单选择，不再写死单一镜像：
  · 新增 4 个国内可选源 + 1 个「恢复官方源」选项，逐个实测确认可用：
    中科大 (USTC)、中科大-联通节点、中科大-移动节点、CERNET 教育网聚合
  · 菜单里会先显示当前使用的源，选完再做可用性验证；验证失败会自动回滚到原来的源，
    并提示「可换一个源再试」
  · 恢复官方源时若因为网络不通而验证失败，不会误报失败，而是说明「地址已设置成功，
    网络恢复后即可用」
  · 顺带纠正原注释里过时的探测结论：sjtu 已 301 跳回官方（等于没加速），
    nju / sustech / bfsu / tuna / aliyun / tencent / huawei / zju / jlu / iscas /
    xjtu / scau / qlu 的 flathub 返回 HTML 首页或 404，并非真实镜像
  · 说明：国内镜像都是 Flathub 的缓存而非完整镜像，未命中的文件会 302 回官方站，
    因此仍需能基本连通 dl.flathub.org

2026-10-26（v1.9.4）
【问题修复】
- 修复「GE-Proton 管理」安装时误报「解压失败（压缩包损坏或解压中断）」：
  · 根因一（主因）：上游从 GE-Proton11-4 起改了产物命名，压缩包和包内顶层目录都带架构后缀
    （GE-Proton11-11-x86_64.tar.gz，解开是 GE-Proton11-11-x86_64/），而 release tag 仍是
    GE-Proton11-11。旧代码解压后写死检查 $STAGE_DIR/GE-Proton11-11，找不到就当成解压失败。
    实际包是好的，tar 退出码也是 0，纯粹是判据写死了目录名
  · 根因二：镜像断流时返回 200 + 截断的包，curl 认为成功，tar 一路解到末尾才报 EOF，
    表现同样是「解压失败」。现在下载后先用文件大小 + sha512 校验，截断/损坏的包在解压前就被拦下
  · 现在解压后按「stage 里唯一的顶层目录」定位，并用 <tag> 与 <tag>-* 前缀兜底；
    安装目录名仍保持 <tag>（GE-Proton11-11），已装列表/卸载/Steam 显示名与旧版本一致
  · 下载失败提示更具体：区分「下载不完整（x/y 字节）」「sha512 校验失败」「压缩包结构异常」，
    不再一律报「解压失败」，便于判断是网络问题还是上游改名
  · 安装循环结束后补充清理下载临时目录，用户中途取消不再留 /tmp/ge_proton_* 残留

2026-10-26（v1.9.3）
【功能改进】
- 「Watt Toolkit (Steam++)」安装完成后新增一步「信任证书」，不再需要装完再手动敲命令
  · 把加速插件自签的根证书（~/.local/share/Steam++/Plugins/Accelerator/SteamTools.Certificate.cer）
    写入系统信任库；把 /etc/hosts 设为可读写，加速改 hosts 时不用每次提权
  · 证书由 Watt Toolkit 首次运行时生成，安装包里没有；若检测不到会提示先启动软件点一次「加速」，
    并可代为拉起 Watt Toolkit，之后按回车重新检测（Q 放弃）
  · 写入前用 openssl 校验证书可解析、未过期，避免把损坏文件写进信任库；已存在则提示为覆盖更新
  · 明确告知安全影响：信任该根证书等价于允许对应私钥持有者解密本机 https 流量
- 「网络工具 → Watt Toolkit (Steam++)」新增独立的「信任证书」菜单项，可随时重跑
  （证书重新生成、换设备后需要再次信任）
- 卸载 Watt Toolkit 时提示并可选一并清除系统级改动：从信任库移除该根证书、
  把 /etc/hosts 权限从所有人可写恢复，并刷新系统证书包；跳过则给出手动命令

2026-10-26（v1.9.2）
【功能改进】
- 「安装 ToDesk」检测到本机已安装时，选项从两个增加为三个：新增「3. 卸载 ToDesk（不再安装）」，
  可以直接在安装流程里把 ToDesk 卸掉，不用再绕到「更新和卸载软件」里找（回车默认仍是 2 不安装，
  不会误触）
- 新增独立的「卸载 ToDesk」菜单项（更新和卸载软件 → 卸载已安装应用），可单独调用
- 卸载范围覆盖 ToDesk 的两种安装来源：pacman 包（todesk-bin / todesk）、手动解包安装的
  /opt/todesk 目录；卸载前先停用 todeskd 服务并结束残留进程，避免二进制被占用导致删不干净
- 一并清理 pacman 不负责的痕迹：桌面快捷方式、~/.config/autostart 自启项、旧方案遗留的
  「安装/重装 ToDesk」图标；用户数据（~/.local/share/todesk）单独询问后再删，默认保留

2026-10-25（v1.9.1）
【功能改进】
- 「安装 ToDesk」完善已安装检测：安装前先判断本机是否已装，已装则显示当前版本、安装来源、
  目标版本，并给出「1. 重新安装 / 2. 不安装直接退出」两个明确选项（回车默认选 2，不误装）
- 检测范围不再只看 pacman 包：pacman 包数据库损坏、或当初是手动解包安装的设备，
  只要 /opt/todesk 目录或 ToDesk 主程序存在，同样会被识别为已安装（此前会漏判，
  导致重复安装覆盖）
- 未安装时不再出现询问，直接进入安装流程

2026-10-25（v1.9.0）
【功能改进】
- 重写「安装 ToDesk」：不再下载并执行第三方安装脚本，改为直接取回安装包用 pacman 安装
  · 原因：原方案执行的 todesk.lanbai.top 脚本里，真正安装的那行 `sh /tmp/lanbai/install.sh`
    其实是注释掉的（第 14 行 `#sh ...`），它只在桌面丢一个「ToDesk安装」图标，要用户再点一次
    才会下载另一个脚本执行，属于四段式绕路，而且并不真正完成安装
  · 新做法：git clone 社区仓库取到 todesk-bin 4.7.2.0 的 .pkg.tar.zst，校验完整性后
    直接 pacman -U 安装，全程不执行任何第三方 shell 脚本
  · 顺带不再做这些多余且有风险的操作：重建 pacman 钥匙环（pacman-key --init/--populate）、
    安装 base-devel 整套编译工具链、硬编码 /home/deck 路径（非 deck 用户名会出错）
  · 增加了已安装检测（可保持或卸载重装）、依赖自动补齐（gtk3 / libappindicator-gtk3）、
    旧版 todesk 4.1.0 冲突自动卸载、安装包完整性校验、上游包名变更时安全中止
  · 自动创建桌面快捷方式并启用 todeskd 服务，同时清理旧方案遗留的桌面「安装/重装」图标
  · 说明：Gitee 禁止匿名直链下载仓库内 >1MB 的文件（返回 403），所以 80MB 的安装包
    只能通过 git clone 取回，无法用 curl 直接下载

2026-10-23（v1.8.9）
【界面修复】
- 彻底修复「窗口外面多一圈黑色区域」：不再使用「透明圆角 + 投影」这套窗口外观。
  那套做法要求窗口表面比可见内容大一圈（CSD 透明边距，实测四周 68/60/76px），
  一旦系统没开桌面特效合成器（按 Alt+Shift+F12 就会关掉），X11 无法做透明混合，
  这圈透明边距就被渲染成纯黑，也就是那圈黑边
- 现在窗口改为不透明直角样式：窗口边距恒为 0，无论合成器开还是关都不会出现黑边，
  也不再有切换时黑边闪一下再消失的过程
- 对话框、内部卡片的圆角样式保持不变，只是窗口外框改为直角

2026-10-22（v1.8.7）
【界面修复】
- 真正修复「点击帮助时主界面闪一下」：根因是 CSS 里窗口「失焦态」的阴影比正常态小，
  弹出模态对话框后主窗口一失焦，GTK 就会按新阴影重算窗口边距，窗口管理器随之把
  主窗口重新缩放一遍（实测 1086x806 → 1018x738）。现在两种状态用同样的阴影，
  主窗口再也不会因为失焦/获焦而改变尺寸
- 顺带说明：模态对话框打开时系统会把主窗口「压暗」一点点，这是 KDE 的 Dialog Parent
  效果（所有程序都这样），不属于闪烁

2026-10-22（v1.8.6）
【界面修复】
- 彻底修复对话框打开时的闪烁：改为在窗口完成尺寸计算后再显示出来，
  用户不会再看到「先小后大」的跳变
- 此前几个版本还修了：深色模式下对话框标题栏白边、窗口四角圆角不一致

2026-10-22（v1.8.5）
【界面修复】
- 修复对话框刚打开时尺寸偏小、内容被裁剪、过一会儿才变大的问题
- 修复点击「帮助」时窗口闪烁一下的问题（去掉了会触发窗口闪现的尺寸处理方式）

2026-10-22（v1.8.4）
【界面修复】
- 修复对话框刚打开时尺寸偏小、内容被裁剪，过一会儿才变大的问题：现改为显示前先按内容计算好尺寸，一次性正确显示

2026-10-22（v1.8.3）
【界面修复】
- 修复深色模式下对话框顶部出现白色横条：系统为浅色主题时，窗口管理器会用系统主题绘制对话框标题区，导致与深色界面不一致；现改为由程序自己绘制标题栏，配色跟随应用主题
- 修复窗口四角圆角不一致：原来上方两角圆润、下方两角是直角（底部状态栏的不透明背景盖住了下方圆角），现四角圆角保持一致

2026-10-19（v1.8.2）
【功能整合】
- 「系统体检」升级为统一的排障入口：发现引导类问题时内联执行修复（不再跳转到独立的「修复引导」界面导致上下文丢失），发现挂载类问题时内联写入 fstab 自动挂载
- 「修复引导」补齐关键能力：原来 Clover 启动项缺失时只会报错退出（因此对"掉引导"实际无能为力），现在会先动态探测 ESP，再自动重建 Clover / SteamOS 启动项，并顺带把 Clover 设为第一启动项
- 「修复引导」不再硬编码 /dev/nvme0n1p1 与 /dev/nvme0n1 分区 1：改用 findmnt + EFI 分区类型 GUID 动态定位，兼容 eMMC / SATA 机型与不同分区号
- 消除体检与「修复引导」「修复互通盘」的重复实现：启动顺序调整、启动项重建统一走同一套逻辑；体检内联执行时不再清屏、不重开界面
- 体检的挂载修复写入 fstab 前自动备份（fstab 写坏会导致下次开机进不了系统）

【问题修复】
- 修复「修复引导」判断 Clover 文件是否存在时无法区分「文件缺失」与「读取失败」，可能误导用户去重装 Clover；现改为三态判断，权限不足时明确提示并继续尝试注册启动项
- 清理体检中已不再使用的 3 个冗余修复函数（原 hc_fix_clover_entry / hc_fix_steamos_entry / hc_fix_boot_order），避免两套实现并存

2026-10-19（v1.8.1）
【问题修复】
- 修复系统体检的结论误导：即使只有「注意」项（如 Windows 启动项被 Clover 接管、ESP 剩余空间偏小等环境差异），也会输出「以上问题需要手动处理」，让人误以为系统有故障；现改为按「异常」数量判定，无异常时明确显示「✅ 结论：未发现异常，引导与挂载均正常」，并说明提示项不影响使用
- 修复系统体检第 3 项「Clover 引导文件完整性」在已输入 sudo 密码的情况下仍提示「无法读取 EFI 目录」：原代码用普通用户的 [ -d ] 判断 EFI 目录位置，而 /esp 权限为 700 root，普通用户永远看不到，导致路径判断错误后 sudo 探测也失败
- EFI 目录定位改为依次用 sudo 探测 /esp/EFI 与 /esp/efi/EFI 两个候选路径，兼容不同机型与系统布局；两者都不存在时再区分「目录确实缺失」与「无 sudo 权限」，并给出 ESP 根目录的实际内容供排查

2026-10-19（v1.8.0）
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

CHANGELOG_BODY_EN = """2026-11-11 (v2.1.3)
[Maintenance: install and self-update]
- Link migration only; no feature changes
- Install and self-update URLs now use the GitHub `main` branch instead of `master`
- Already-installed v2.1.2 still fetches updates from `master`. Update to this
  version first so removing `master` later will not break auto-update

2026-11-10 (v2.1.2)
[Bug fixes: installer]
- Fixed `install_gui.sh` swallowing both the failure and the stderr of `pacman -Sy`,
  which made a failed vte3 install show only a vague "cannot find database" error.
  Sync output is now shown and the return code is checked; on failure, concrete
  troubleshooting steps are printed.
- Added detection for a stale `[community-3.9]` repository in `/etc/pacman.conf`
  (SteamOS 3.9 merged community into extra, so community-3.9.db no longer exists on the
  server). It now warns early with the fix commands, so users do not mistake it for a
  toolbox or "switch software source" problem.

2026-11-10 (v2.1.1)
[Bug fixes]
- Fixed "Update All Apps" flooding the screen with progress lines: percentage,
  download speed, the progress bar and "Updating X/Y" transition frames now refresh
  in place on a single line, while normal log lines and the completion message still
  get their own lines.

2026-11-09 (v2.1.0)
[Repo-wide audit and fixes]
- Reviewed every toolbox feature (system optimization, dual boot, plugins, software
  installs, network tools, UI and self-update). The confirmed issues below were fixed,
  and missing cross-device dependencies were checked.

[Security: downloads and root execution]
- UU / Xunyou / Qiyou accelerators no longer pipe plaintext-HTTP content straight into a
  root shell: they now use HTTPS, timeouts and HTTP status checks, validate a temporary
  download as shell text, show its origin, then let sudo prompt for the password directly.
  The script preview and extra confirmation were removed to restore the "start installing
  immediately" experience.
- Qiyou: sd.qiyou.cn only serves HTTP (port 443 closed), so the previous HTTPS-only
  change broke it. It now fetches the real installer from static.qiyou.cn over HTTPS, and
  the download helper gained a generic "fall back to HTTP with an explicit warning" path.
- Watt certificate trust no longer makes /etc/hosts world-writable: original permissions
  are saved and restored, CA:TRUE and the SHA256 fingerprint are verified, cleanup is
  fingerprint-based and still runs when the program directory is gone.
- Epic / Battle.net / Ubisoft uninstalls now list the paths to be removed and ask for
  confirmation, so games in default folders are not deleted by accident.

[Installer and task window]
- Installer: temporary file + marker/size/syntax checks before an atomic replace; a
  failure keeps the old version. Read-only mode is restored only when this script
  disabled it, never overriding the user's own writable setting.
- Cancelling a task now shows "Task cancelled" instead of "Task completed"; switching
  features while a task runs asks for confirmation; closing a Flatpak window really
  terminates the process, and a failed addon no longer hides behind a successful main app.
- Added XDG desktop dirs, more terminal emulators, explicit messages when Flatpak is
  missing or a query fails, and more permissive dual-boot detection so Clover users can
  still see the boot and shared-disk repairs.

[Boot and system]
- Fixed the Clover file-check return code being swallowed by `local`, which could
  register a boot entry for a missing file.
- Swap operations no longer delete the old swap when deactivation fails; Steam / Gamescope
  emergency reset aborts immediately if the backup fails, instead of deleting data that
  cannot be restored.
- "Clean Virtual Memory Config" now judges by the actual post-reset ZRAM state, fixing
  the false "ZRAM reset failed" when it had in fact succeeded; NTFS repair failures are
  now reported honestly.
- "Switch Flatpak Software Source" shows the matching preset name (e.g. "USTC - China
  Unicom node") when the current URL matches one of the 5 sources, instead of a raw URL.
- The boot configuration tool now follows the toolbox language: the Chinese UI keeps
  the translated script, the English UI keeps the original community English version.

[Watt Toolkit / software installs]
- Fixed the Watt installer removing its own working directory, which made every later
  sudo print hundreds of "getcwd: cannot access parent directory" lines. Backups now
  live on the same filesystem and copies drop security.capability xattrs, fixing
  "mv: setting attribute ... operation not permitted".
- Certificate trust now writes explicitly to the system anchors dir, refreshes the CA
  bundle and verifies with openssl verify that it really took effect (previously it
  reported success while HTTPS acceleration still failed). hosts and the overall result
  are judged by actual state, no more false success.
- The same version is no longer reported as an update (v3.1.0 vs 3.1.0). ToDesk /
  AnyDesk / Lossless Scaling no longer "remove the old version first" and leave a
  half-install; download, extraction, service start, uninstall and update failures are
  reported honestly.
- "Update All Apps" shows download percentage and speed again: dropped --noninteractive,
  enabled FLATPAK_TTY_PROGRESS, and added a filter that turns in-place redraws into
  clean lines without reintroducing the old garbage characters.

[Plugin Store]
- The Decky service user is no longer hardcoded to deck and the official fields are
  filled in; uninstall stops, disables and removes the systemd unit and CEF markers;
  plugin installs validate a temporary directory before replacing, keeping the old
  plugin on failure.

[Dependencies and compatibility]
- Added checks and hints for GTK3/VTE3, flatpak, p11-kit, openssl, ntfs-3g/ntfsprogs,
  efibootmgr, 7z, jupiter-hw-support and others; these are no longer assumed to exist
  on every distro.

2026-11-08 (v2.0.4)
[Bug fixes: Fix Shared Disk]
- No more "false success" on dirty volumes: when a volume carries the NTFS dirty flag, or Windows used Fast Startup / hibernation and never really shut down, the Linux NTFS driver does not fail -- it quietly mounts the partition read-only. The old code only checked the mount command's exit code, so it reported "✓ Mounted successfully" for a volume where not a single file could be written. It now re-reads the real mount options and, when read-only, says so plainly and gives the steps that actually fix it
- Fixed "Fix Shared Disk" claiming "all partitions are mounted, no action needed" when a partition was mounted read-only: that message made dirty-volume users think everything was fine. A read-only mount now counts as not ready, so the repair continues
- A failed mount no longer just prints "please check the dmesg output": it now reads only the kernel messages produced by this operation (old boot-time errors are no longer surfaced as if they were current) and, on recognising "dirty volume / hibernated / not cleanly unmounted", gives the matching steps -- turn off Fast Startup in Windows and shut down fully, clear the flag with ntfsfix, or mount read-only / forced as an emergency
- The password is now asked once up front and the NTFS tools are checked automatically: a missing ntfs-3g is installed for you (nothing can be mounted without it), while a missing ntfsfix only produces a warning (it is needed solely to clear the dirty flag). You no longer have to install anything by hand
- Fixed the fstab line hardcoding the mount user as uid=1000,gid=1000: on a machine whose user is not deck or whose UID is not 1000, partitions mounted but could not be written to. The ids now come from the current user
- Each volume is pre-checked with ntfs-3g.probe before mounting: if it can be mounted read-write it mounts normally, and if not the reason and remedy are explained up front instead of after discovering a read-only mount

[Bug fixes: Fix Disk Write Errors]
- The flow is now "enter the admin password -> disable SteamOS read-only mode as needed -> install missing tools automatically" instead of immediately telling you that ntfsfix is not installed and leaving the install to you
- Fixed the wrong package name in the install hint: the old version pointed at ntfs-3g, but on Arch/SteamOS ntfsfix and ntfsinfo belong to ntfsprogs, so following that hint left them still missing. The correct package is now installed automatically, and the package-name difference between the two distro families is handled
- ntfsfix is now called with -d (clear the dirty flag), so the flag does not survive the repair and make ntfs3 refuse the mount again
[Repo-wide bug fixes]
- Security: UU / Xunyou / Qiyou no longer pipe a plaintext-HTTP remote script straight into a root shell; they now use HTTPS, timeouts and HTTP status checks, validate a temporary download, show its origin and ask for confirmation before executing
- Security: Watt certificate trust no longer makes /etc/hosts world-writable; original permissions are saved and restored, CA constraints and fingerprints are verified, cleanup is fingerprint-based and still runs when the program directory is already gone
- Security: Epic / Battle.net / Ubisoft uninstalls now list the paths to be removed and ask for confirmation, so games in default folders are not deleted by accident
- Installer: downloads go to a temporary file and only atomically replace the target after marker / size / syntax checks pass; a failure keeps the old version. Read-only mode is restored only when this script disabled it, never overriding the user's own writable setting
- Task window: cancelling now shows "Task cancelled" instead of "Task completed"; switching features while a task runs asks for confirmation; closing a Flatpak window really terminates the process, and a failed addon no longer hides behind a successful main package
- Boot: fixed the Clover file-check return code being swallowed by `local`, which could register a boot entry for a missing file; swap operations no longer delete the old swap when deactivation fails
- Emergency reset: Steam / Gamescope reset aborts immediately if the backup fails, instead of deleting data that cannot be restored
- Plugin Store: the service user is no longer hardcoded to deck and the official fields are filled in; uninstall stops, disables and removes the systemd unit; plugin installs validate a temporary directory before replacing, keeping the old plugin on failure
- Software installs: ToDesk / AnyDesk / Watt / Lossless Scaling no longer "remove the old version first" and leave a half-install; download, extraction, service start, uninstall and update failures are now reported honestly
- Compatibility: added XDG desktop dirs, more terminal emulators, explicit messages when Flatpak is missing or a query fails, and more permissive dual-boot detection so Clover users can still see the boot and shared-disk repairs


2026-11-07 (v2.0.3)
[Bug fixes]
- Fixed "clicking a feature does nothing": when a GTK callback raised, the traceback only went to the terminal, which is invisible when launched from a desktop shortcut — so clicks appeared to do nothing. Any uncaught exception now shows "This action failed and was skipped" and writes the full traceback to ~/.cache/steamdeck_toolbox_error.log; send that file with any bug report
- Fixed the "install vte3?" prompt swallowing every click on the main window when VTE is missing: that dialog was modal with no parent window, so on some desktops it landed behind the main window — the toolbox window was there but nothing responded. It is now non-modal and always kept on top, so the main window stays usable even if the dialog ends up behind it
- Feature windows now raise themselves to the front, so they are not hidden behind the main window on some desktops

2026-11-05 (v2.0.2)
[UI rework: native GTK windows]
- "Install Flatpak Apps" and "Uninstall Other Installed Apps" are now native GTK windows; zenity is no longer used
  · The app list, checkboxes, progress bar and results all live in the tool's own window, matching the main UI theme
  · The "delete local data?" prompt is part of the same window instead of a separate dialog
  · Fully fixes "install keeps running in the background after cancel/close": Python now starts flatpak directly, so cancelling terminates that very process -- measured 0.5s to exit, with nothing installed
  · New search box: matches the built-in catalog instantly, and falls back to searching flathub when nothing matches; remote results are installable too
  · Buttons are reduced to a single primary button that switches with the stage (install / cancel / done / back to list) and hides itself when nothing is selected
  · After finishing you return to the list and can keep going instead of re-entering the entry each time
  · The search box hides itself during install; it only matters while picking apps
  · Selections survive searching, switching queries and late remote results instead of being wiped by a redraw
- "Steam Cache Manager" is now a native GTK window
  · Opening it lists shader cache and compat data; pick a type and it scans every Steam library (the default one plus any registered in libraryfolders.vdf)
  · The list shows app names and sizes, sorted by size, with a live count and total at the bottom
  · A separate confirmation page lists what will be deleted; during deletion it shows "Deleting 2/3: app name" with live progress and can be cancelled at any point
- "Compatibility Layer Manager" is now a native GTK window, and one window handles install and uninstall for all three families (GE-Proton, Proton-CachyOS, DW Proton)
  · Version lists are read from GitHub Releases; the install list skips versions already present and the uninstall list only shows installed directories
  · The confirmation page offers a download mirror (gh-proxy.com / gh.3w.pm / cors.isteed.cc / ghproxy.net / GitHub official), shared by the whole batch
  · Downloads show real byte progress (e.g. "128.0 MB / 540.6 MB") instead of an idle animation
  · Two checks after downloading: compare the file size first, then the sha512 digest. If either fails the version is reported as failed with the reason, and a bad archive is never unpacked into Steam; extraction goes to a temporary directory first and is only moved into place after validation, so cancelling leaves no half-finished folder
  · Failures are listed one per line ("· version: reason"), e.g. "sha512 mismatch, archive is corrupt" or "this version has no x86_64 package for the Deck"
  · Cancel responds in about 0.5s (read1 chunked reads plus a socket shutdown)
  · Mirrors now have failure detection and automatic failover: unreachable hosts, dropped connections,
    size mismatches and sha512 mismatches all move on to the next mirror; only when every mirror fails
    does it report an error, listing the specific reason for each one
  · Cancelling works while fetching the version list, the download info, the archive and the checksum;
    before this only an in-progress download could be cancelled
  · Cancelling returns to the version list instead of the first page, keeping the current selection so a
    different mirror or version can be tried right away

[Install / uninstall consolidation]
- The 8 Flatpak apps under Software are merged into one "Install Flatpak Apps" entry, and the 8 Flatpak uninstall entries are merged into "Uninstall Other Installed Apps"
  · Key fix: that uninstall screen used to list those 8 apps as exclusions (because each had its own dedicated uninstall entry). With the dedicated entries gone, leaving the list intact would have made those apps impossible to uninstall forever; the list is now emptied, keeping only the Fcitx 5 Chinese add-on hidden as an internal component removed together with the main program
  · The listing is now read live from flatpak list instead of a fixed name list, so whatever is installed can be uninstalled

[Feature expansion]
- "Install Flatpak Apps" grows from 8 apps to 37, covering everyday, office, media, creative, remote and gaming tools
  · Messaging 7, browsers 3, media 4, cloud storage and downloads 2, office and notes 5, creative tools 6, remote control 2, gaming tools 6, system tools 2
- All 37 app IDs are built in, so opening the list no longer queries the network; it also shows the full list offline, and opens in under a second instead of over 3
  · Related fix: `flatpak remote-add` contacts the network (~1.1s) even when flathub already exists, so the code now checks locally first and skips it

[Bug fixes]
- Fixed installs always failing with "failed IDs: 飞书"
  · Root cause: the first column of a zenity checklist must be the tick state; omitting it shifts every following column, and without an explicit return column the value returned is the display name rather than the app ID -- so the command run was `flatpak install flathub 飞书`
  · Fix: put the tick state in column one and the real app ID in a hidden second column so the output is plain IDs; a whitelist check rejects anything unexpected
- Fixed the bar showing 100% while the download was still running
  · Root cause: installing one app is split into several subtasks (runtime, locales, the app itself...), each running 0 to 100%; the old code took only the sub-task percentage, so the bar filled during the first one
  · Fix: parse "step N of M" and fold it into one continuous total
- Fixed failures showing no reason, or just a single letter
  · Non-progress output was discarded, hiding flatpak's real error; the window now lists the original message, e.g. "no match for xxx found in remote flathub"
- Fixed desktop shortcuts not being removed on uninstall
  · Root cause: shortcuts are named after the display name (飞书.desktop, Google Chrome.desktop) but uninstall matched on the app ID, so they never lined up
  · Fix: read the Exec line of each .desktop file and delete any that runs `flatpak run <that ID>`, regardless of filename
- Fixed the whole feature exiting instead of returning to the app list after cancel or closing the progress window
  · Root cause: the INT/TERM trap at the top of the embedded script (meant for "close the terminal and the tool quits") fired on the signal from closing the progress window
- Fixed flatpak not actually being terminated after cancel, leaving it downloading in the background (now cleans up the whole process group, grandchildren included)
- Fixed the list going blank after "back to list" on uninstall (rows were rebuilt without calling show_all, so new rows stayed hidden)
- Fixed "No such file or directory" when creating a shortcut and the desktop directory does not exist (now resolves it per XDG and creates it)
- Fixed an empty percentage, a duplicated percentage and a progress bar that went backwards
- Fixed every app being treated as "missing" and hidden when offline (an empty screen that looks broken)

[Other]
- Removed the "System Health Check" feature (not needed for now): its sidebar entry, search index and dangerous-operation confirmation are gone too, along with the six check groups and their repair flows in the embedded scripts; "Fix Boot" and "Fix Shared Disk" are unaffected
- Deleted 50 bash functions superseded by the GTK windows (100 definitions across both language scripts, about 4,160 lines)
  · 14 health check, 19 Flatpak install/uninstall, 1 Steam cache manager, 16 compatibility layer
  · Python now opens the corresponding GTK window directly, so these functions can no longer be reached

2026-11-03 (v2.0.1)
[Bug fixes]
- Fixed AskLink Remote failing to install dpkg when leftover /var/lib/dpkg/{available,status} files already exist: try a normal install first, then retry with --overwrite '/var/lib/dpkg/*', and verify dpkg is usable
- Fixed the embedded script EXIT trap forcing exit 0 so failed tasks still showed "Task completed": preserve the real exit code and show "Task completed" / "Task failed" accordingly

[UX]
- Default UI language is Chinese when no saved preference exists (explicit zh/en/system choices are still respected)
- Top-bar language control now shows the text "语言" / Language instead of an ambiguous icon
- Slightly smaller default window on Steam Deck-class screens
- After choosing Yes on a startup update, the download runs in the same update-check window (same size; no jump to a different dialog)

2026-11-02 (v2.0.0)
[Bug fixes]
- Fixed the garbage characters appearing after the "Update all apps" progress line (^[[20;68R^[[20;68R^[[20;77R)
  - Root cause: before drawing its progress bar flatpak sends ESC[6n to ask the terminal where the cursor is, and VTE answers with ESC[row;colR on the terminal's *input* side. The PTY has ECHO enabled by default, so the kernel echoes that reply back to the screen, where it shows up as visible garbage
  - Fix: pass --noninteractive to flatpak update so it emits plain line-by-line text instead of an ANSI progress bar. No progress bar means no cursor query, removing the garbage at the source
  - Measured on the same machine in the same state (nothing to update): default produced 31 escape sequences including ANSI bold and cursor control; with the flag, 0
  - Why not simply disable terminal ECHO: that merely hides the reply while its bytes stay in the input buffer, so later reads pick them up (measured: read -n1 returned ESC instead of the key the user pressed), which is worse than the garbage
  - Tradeoff: terser output with no percentage progress bar, but every step still prints a line

[Version]
- Version bumped to 2.0.0: features and stability have accumulated well beyond 1.x, marking it as a stable release

2026-11-02 (v1.11.4)
[UX improvements]
- Streamlined the "Update all apps" output
  - Removed the three-line "skipped refreshing the appstream catalog" note: that is an implementation detail users do not need. In practice `flatpak update` does not refresh appstream by default (only with the explicit `--appstream` flag), so the step never existed and the note was redundant
  - When updates exist, appstream is likewise not involved; the "If it hangs on Updating appstream data" line in the timeout message is gone too, keeping only useful info such as partially downloaded data being kept
  - The completion message is now just "✓ All apps updated" without the extra "everything is current" wording

2026-11-02 (v1.11.3)
[Bug fixes]
- Fixed taskbar icon disappearing after the startup update check: show the main window before closing the splash; unify WM_CLASS=Steamdeck-toolbox and add StartupWMClass to the desktop shortcut; the update splash no longer takes a taskbar slot

2026-11-02 (v1.11.2)
[UI improvements]
- Sidebar trimmed to 7 items: Support, Changelog, System Optimization, Plugins, Software, Network, Update & Uninstall
  · Compatibility layers, emergency reset, and Clover/dual-boot repair fold into System Optimization groups (collapsed by default)
  · Removed standalone Game Compatibility / Emergency / Boot & Dual Boot / Other categories
  · Yellow Duck moves under Software Installation; third-party platforms stay there too
- Launch still defaults to Support & Maintenance

2026-11-02 (v1.11.1)
[UI improvements]
- Information architecture reshuffle: sidebar order is daily optimization → game compatibility → plugins → software → network → emergency → boot/dual-boot → uninstall → other
  · System Optimization keeps repos/swap/disk/hosts/calibration/Steam cache only
  · New "Game Compatibility" hosts the compatibility-layer manager (GE / CachyOS / DW)
  · New "Emergency & Recovery" for Steam / Gamescope resets
  · "Boot Management" becomes "Boot & Dual Boot"; dual-boot health/fix-boot/shared-disk live there
  · Third-party game platforms move under Software Installation; Other keeps Yellow Duck and similar odds and ends
- Collapsible groups still start collapsed; launch still opens Support & Maintenance

2026-11-02 (v1.11.0)
[New features]
- Expanded "GE-Proton Manager" into "Compatibility Layer Manager": GE-Proton, Proton-CachyOS (SLR), and DW Proton in one place
  · CachyOS installs the SLR x86_64 package into ~/.local/share/Steam/compatibilitytools.d/
  · DW Proton uses dawn-winery/dwproton-mirror; copy notes anime/specific-game focus and keeps CheatDeck separate
  · Reuses GE mirror picking, size/sha512 checks, and stage-then-move installs (tar.xz)
- Plugins: CheatDeck installs only CheatDeck.zip; checks for Decky, prompts for Developer mode and a ToS disclaimer; no cheat files bundled
- System Optimization: Emergency Reset for Steam config and Gamescope/Game Mode; strong confirm + auto-backup under ~/steamdeck_toolbox_backups/

2026-11-02 (v1.10.0)
[UI improvements]
- Main window now sizes itself to the display instead of a fixed 1100x720
  - Reason: on a Steam Deck (1280x800, usable workarea 1280x746) the content height of 720 plus roughly 40px of title bar totals 760px, exceeding the usable height, so the bottom was pushed off screen
  - On startup it reads the monitor workarea (panel already excluded) and picks one of three tiers by usable height:
    - Small/handheld (usable height < 900): 86% x 92%, cap 1400x820
    - 1K (usable height < 1150): 82% x 88%, cap 1700x1000
    - 2K/4K large screens: 72% x 78%, cap 2000x1300
  - Results: handheld 1100x686, 1K 1574x915, 2K 1843x1092, 4K 2000x1300 -- neither full-screen nor too small to read
- The task window (terminal) follows the same adaptive sizing, one notch smaller than the main window (scale factor 0.8): handheld 880x549, 1K 1259x732, 2K 1474x873
- Uses workarea rather than raw resolution, with a fallback so the window never exceeds the usable area even on very small screens; if monitor info is unavailable it falls back to the original 1100x720

2026-11-02 (v1.9.9)
[Bug fixes]
- Fixed "Install ToDesk" failing on reinstall with "could not commit transaction (conflicting files) / exists in filesystem /opt/todesk/bin/...": the machine was in an orphaned state where pacman no longer had a todesk-bin record (interrupted uninstall, pruned database, or a manual extraction install) but files such as /opt/todesk were still on disk. The old cleanup only ran "if pacman has a record", which was false here, so cleanup was skipped entirely and `pacman -U` refused because the files it wanted to write already existed
- The installer now clears orphaned leftovers first: when the package is unregistered but files remain, it stops the service, kills holding processes, then removes /opt/todesk, /usr/bin/todesk, todeskd.service, todesk.desktop, the licenses directory, ToDesk icons under hicolor, and any stale pacman db.lck before installing
- Cleanup is verified afterwards: any remaining leftovers are listed explicitly with a manual-removal hint instead of letting pacman raise a cryptic conflict
- Only ToDesk's own icons are removed (other software under hicolor is untouched), and machines with a properly registered pacman package skip this logic entirely

2026-11-02 (v1.9.8)
[UI improvements]
- Main window is now a SteamOS / OLED-style master-detail layout: a persistent left category rail and an immediate right-hand detail pane (no more 3×3 home tiles then a second page)
- Dark theme uses near-black charcoal with purple/magenta selection and cyan accents; light theme remains fully usable
- Function row cards no longer sit under the vertical scrollbar (chevron and scrollbar stay apart)
- On launch, "Support & maintenance" is selected by default and its about/maintenance content is shown right away (same as clicking the rail item)
[Notes]
- Language switching, themes, global search, danger confirms, the task window, and script logic are unchanged
- Made by: Zhucy

2026-11-01 (v1.9.7)
[New features]
- Added UI language switching (Chinese / English): switch anytime from the top bar; preference is saved to the language field in ~/.config/steamdeck_toolbox/config.json and restored on next launch
- In English mode, UI strings, category/feature names, the changelog, dialog buttons (including Yes / No / OK), and user-visible embedded terminal script output are all English; Chinese mode stays Chinese
- Help page follows the language: Chinese keeps the Bilibili nudge entry; English shows a clickable X link @AlanWake2100 (https://x.com/AlanWake2100)
[UI improvements]
- Credits updated to Made by / 制作人 Zhucy in both languages
- Dangerous-confirm and other dialogs no longer rely on system-locale Yes/No/OK labels; they follow the toolbox language instead
- Note: the system sudo password prompt still follows the OS language; that is expected and not toolbox UI text

2026-10-27 (v1.9.6)
[Bug fixes]
- Fixed "Switch software source" falsely warning that the flathub public key could not be downloaded:
  · Cause: every switch unconditionally re-downloaded the key from dl.flathub.org, which is often unreachable, so a yellow warning appeared every time. The key only needs to be imported once and is already present on normal devices (/var/lib/flatpak/repo/flathub.trustedkeys.gpg); the feature itself worked, the warning was misleading.
  · Now check for a usable local key first (and verify with gpg that it really contains the Flathub key, to avoid empty/corrupt stubs). If present, skip the download and print no warning.
  · Only download when missing, trying Official → USTC → CERNET in order.
  · Warn only when all sources fail, and clearly state the consequence (installs/updates may report Could not find public key) plus two manual fix commands.

2026-10-22 (v1.9.5)
[Maintenance]
- Repository baseline rebuilt on top of the upstream Gitee master; all changes
  re-applied as a single commit (no functional change from v1.9.4)

2026-10-22 (v1.9.4)
[Interface]
- Fixed the remaining light strip above dialogs in dark mode: on KDE/KWin the window manager draws the dialog title area using the system (light) colours, which our CSS cannot reach. Client-side decorations are now forced so GTK paints that area and the app theme applies
- Fixed window corners: all four corners are now rounded (previously only the top two were, because the bottom status bar painted an opaque square over them)

2026-10-22 (v1.9.3)
[Interface]
- The X handle in the Help dialog is now a real clickable link (opens https://x.com/AlanWake2100)
- Fixed a white strip above the title bar when the app runs in dark mode on a light desktop theme: the client-side decoration frame and the GTK theme variant now follow the app theme instead of the system one

2026-10-22 (v1.9.2)
[Interface]
- Help dialog: the social link now points to X (Twitter) — "Follow AlanWake (@AlanWake2100) on X for updates"
- All dialog buttons are now English regardless of system locale: replaced GTK built-in button sets (OK / Yes-No) with explicit English labels, and forced an English locale for the process so system-provided strings stay English

2026-10-22 (v1.9.1)
[Bug Fixes]
- Self-update now fetches from GitHub only: the update check and self-update read VERSION and the script body from the official GitHub repository
- Replaced the remaining Gitee references:
  - Watt Toolkit (Steam++) download now uses the official GitHub release (BeyondDimension/SteamTools) instead of the Gitee mirror
  - ToDesk notice now points to the GitHub project page
  - Changelog wording no longer references Gitee

2026-10-22 (v1.9.0)
[International Release]
- The entire toolbox is now English-only: all UI text, menus, dialogs, status messages, terminal output, comments and documentation have been translated to English
- Added an English README and translated all installer scripts (install_gui.sh, steamdeck_toolbox.sh, install_decky_loader.sh, install_steamcommunity_302.sh)
- Default download source changed to the official GitHub repository (https://github.com/Zhucy123/steamdeck_toolbox)

[Feature Removals]
- Removed the "Install Chinese Source" feature (China-only Flatpak mirror configuration)
- Removed all third-party China mirror sources (gh-proxy.com, gh.3w.pm, cors.isteed.cc, ghproxy.net): all downloads now use the official GitHub source only, and the mirror selection menus have been removed
- Removed the "Others" category together with its only two features:
  - Yellow Duck Software (Lossless Scaling installer)
  - Third-Party Game Platforms (Ubisoft Connect / Epic / Battle.net install and uninstall)

2026-10-19 (v1.8.2)
[Feature Integration]
- "System Health Check" is now the unified troubleshooting entry: boot-related problems are fixed inline (no longer jumping to the separate "Fix Boot" view and losing context), and mount-related problems are fixed inline by writing fstab for auto-mount
- "Fix Boot" gains key capabilities: previously it only errored out when the Clover boot entry was missing (so it could not really help with "lost boot"); it now dynamically detects the ESP first, then automatically recreates the Clover / SteamOS boot entries and sets Clover as the first boot entry
- "Fix Boot" no longer hardcodes /dev/nvme0n1p1 and /dev/nvme0n1 partition 1: it now uses findmnt + the EFI partition type GUID for dynamic detection, compatible with eMMC / SATA models and different partition numbers
- Removed duplicated implementations shared by the health check, "Fix Boot" and "Fix Shared Disk": boot order adjustment and boot entry recreation now use one single code path; inline health-check execution no longer clears the screen or reopens the UI
- The health check backs up fstab before writing mount fixes (a broken fstab prevents the system from booting next time)

[Bug Fixes]
- Fixed "Fix Boot" being unable to distinguish "file missing" from "read failure" when checking whether Clover files exist, which could mislead users into reinstalling Clover; it now uses a three-state check and, when permissions are insufficient, clearly says so and still tries to register the boot entry
- Removed 3 redundant fix functions no longer used by the health check (formerly hc_fix_clover_entry / hc_fix_steamos_entry / hc_fix_boot_order) to avoid two parallel implementations

2026-10-19 (v1.8.1)
[Bug Fixes]
- Fixed misleading conclusions from the system health check: even when only "notice" items existed (e.g. the Windows boot entry taken over by Clover, or low free space on the ESP), it printed "the above problems need manual handling", making users think the system was broken; it now decides by the number of "errors" and, when there are none, clearly shows "✅ Conclusion: no errors found, boot and mounts are normal", while explaining that notice items do not affect usage
- Fixed item 3 "Clover boot file integrity" of the health check still reporting "cannot read the EFI directory" even after the sudo password was entered: the old code used a normal user's [ -d ] test to locate the EFI directory, but /esp is mode 700 root, so a normal user can never see it, which made the path detection wrong and also made the sudo probe fail
- EFI directory detection now probes both candidate paths /esp/EFI and /esp/efi/EFI with sudo, compatible with different models and system layouts; when neither exists, it distinguishes "directory really missing" from "no sudo permission" and prints the actual contents of the ESP root for troubleshooting

2026-10-19 (v1.8.0)
[New Features]
- Added the "System Health Check" feature (visible to dual-boot users): designed for troubleshooting lost disks, lost boot and broken mounts after a SteamOS update, covering 6 categories and 18 checks
  · ESP partition: detected or not, mount state, free space (Clover needs about 15MB)
  · UEFI boot entries: whether Clover / SteamOS / Windows entries exist, and whether Clover is the first boot entry
  · Clover boot files: whether cloverx64.efi, config.plist, BOOTX64.EFI and their .orig backups are complete
  · Windows partition: whether it exists, whether it is mounted, whether the Windows system file structure is complete
  · /etc/fstab: whether entries point to partitions that still exist, and whether any mount units failed
  · System and boot services: SteamOS read-only mode, and whether the Clover boot daemon (clover-bootmanager) is enabled and running
- The health check is read-only; after finding problems it lists "auto-fixable" items and only fixes them after confirmation
- One-click fixes: recreate lost Clover / SteamOS boot entries, set Clover as the first boot entry, enable the Clover boot daemon, and comment out stale fstab entries (backed up before modification)

[Bug Fixes]
- ESP detection in the health check no longer hardcodes /dev/nvme0n1p1: it now uses findmnt + the EFI partition type GUID for dynamic detection, compatible with eMMC/SATA models and different partition numbers
- Distinguishes "file really missing" from "cannot read without sudo permission": when there is no permission it clearly reports a skip instead of falsely reporting every file as missing

2026-10-19 (v1.7.7)
[Bug Fixes]
- Fixed dual boot being misjudged as single boot: after installing Clover, the Windows EFI boot entry is removed/hidden, so only checking efibootmgr for the word "Windows" missed it, and dual-boot features such as "Fix Boot" and "Fix Shared Disk" were not shown
- System type detection now uses multiple criteria: (1) the EFI boot entries contain Windows; (2) an NTFS partition labelled Windows exists; (3) the NTFS partition contains a Windows\\Program Files or Windows\\Users directory structure (detectable even if the label was changed); any one of them declares dual boot
- Single-boot machines that only have a Clover entry and no Windows are still correctly reported as "Single Boot" and no longer accidentally expose dangerous dual-boot features

2026-10-19 (v1.7.6)
[UI Improvements]
- The embedded terminal window gains a "Copy" button: copies the selection when there is one, otherwise copies all output, with brief status feedback
- The embedded terminal gains a context menu: Copy Selection / Copy All Output / Paste / Select All
- The embedded terminal gains keyboard shortcuts: Ctrl+Shift+C copy, Ctrl+Shift+V paste, Ctrl+Shift+A select all (Ctrl+C is still reserved for interrupting the process)
- The task window header bar gains a "Maximize / Restore" button to fill the screen with the terminal; the window is no longer forced modal, so it can be resized freely and switched away from

[Bug Fixes]
- Fixed the command shown after "Install Chinese Source" to restore the official source missing sudo, which failed when copied and run directly; it also now notes that it must be run in Konsole

2026-10-19 (v1.7.5)
[Bug Fixes]
- Unified all GitHub download mirrors: of the original 3 mirrors, gh.ddlc.top was rate-limited (429) and the mirror.ghproxy.com domain had expired; only ghproxy.net still worked but was very slow, so plugin / GE-Proton / Clover downloads often failed
- New mirror list (each verified with 5 stability rounds + sha256 integrity of a 33MB file + real speed tests): gh-proxy.com (fast), gh.3w.pm (stable), cors.isteed.cc (stable), ghproxy.net (slow fallback), GitHub official
- Fixed the download mirror selection menu showing empty entries: the official source uses an empty prefix internally (to avoid URLs like https://github.com/https://github.com/...), so the menu now shows readable names
- Fixed the Clover clone mirror selection: real-world tests showed gh-proxy.com / cors.isteed.cc / ghproxy.net do not support git clone, so only gh.3w.pm and the official source are offered
- Fixed the Flatpak Chinese mirror: the configured mirror.sjtu.edu.cn/flathub now 301-redirects back to the official server and was effectively broken; switched to mirrors.ustc.edu.cn/flathub (verified working for queries and installs), with automatic import of the flathub signing public key, a usability check after switching, and automatic rollback on failure
- Fixed the Flatpak source configuration using the non-existent `flatpak remote-get-url` command to read the original URL; it is now parsed from the remotes list
- Fixed Flatpak source verification always failing because no branch was specified, and the system-level remote-modify getting stuck at the password prompt without sudo
- Fixed the unnecessary "disable SteamOS read-only mode" step in "Install Chinese Source": the flatpak configuration lives on the writable /var partition and has nothing to do with the read-only root

2026-10-19 (v1.7.4)
[Bug Fixes]
- Fixed "one-click apply CryoByte33 recommended settings" writing duplicate swap entries into /etc/fstab when run repeatedly (a sed delimiter escaping bug made the deletion fail)
- Fixed unconditionally setting SteamOS read-only mode back to enabled on exit: now read-only is only restored when the script itself disabled it, no longer overriding a writable state the user set manually
- Fixed "Adjust Virtual Memory" not running swapoff before replacing the swapfile in use (which could cause "device busy" or OOM under memory pressure); it now disables and verifies first
- Fixed the mismatch between the free space shown by "Adjust Virtual Memory" and the actual pre-check of /home; fstab matching now compares the first field exactly (no longer misreading commented lines or swapfile2)
- Fixed "Configure ZRAM" settings not persisting: they are now written to /etc/systemd/zram-generator.conf and survive reboot, and fixed the old code accidentally deleting that config
- Fixed "Clean Virtual Memory Config" falsely reporting "ZRAM reset failed" when ZRAM was not enabled, and fstab now uses exact matching for deletion
- Fixed "Clean hosts Cache" failing silently in read-only mode while still reporting success; it now ensures writability first and aborts with a rollback method on failure
- Fixed "Steam Cache Manager" only scanning the default library (libraries on the SD card / second disk were invisible), game names containing the separator being misparsed, and the missing detailed confirmation before deletion
- Fixed "Install/Reinstall Clover" missing the dangerous-operation second confirmation; it now detects the ESP partition dynamically (the old hardcoded /dev/nvme0n1p1 failed on eMMC/SATA models)
- Fixed a failed Clover installation leaving half the files on the EFI partition: a failed backup/replace of BOOTX64.EFI now aborts and rolls back, and the install script stops on failure
- Fixed the Clover install script truncating sudo passwords containing backslashes when passed via echo -e, which caused authentication failures; it now passes them as-is with printf
- Fixed Clover-related scripts possibly leaving the system writable on exit, and leaving ISO/7z temp files behind
- Fixed self-update truncating itself before writing, so a failure mid-way corrupted the program: it now writes a temp file and atomically replaces, with syntax validation added
- Fixed version comparison treating 1.7 and 1.7.0 as different versions, which could prompt for updates repeatedly
- Fixed "Install/Uninstall Plugins" judging success only by the command return value; it now goes by the actual directory state to avoid false success
- Fixed plugin / Yellow Duck installations changing file ownership to deck on devices whose username is not deck
- Fixed "Install ToDesk" executing a third-party remote script directly: it now downloads it locally, shows the content, validates the syntax, then asks whether to run it, and clearly lists the script's changes to the system
- Fixed system type detection treating the Clover boot entry as evidence of dual boot (a single-boot system with Clover falsely showed "Dual Boot" and exposed dangerous features); it now judges only by the Windows boot entry
- Fixed "Install/Update GE-Proton" leaving a broken version in compatibilitytools.d when extraction was interrupted; it now extracts to a temp directory, verifies, then moves it in
- The default focus of the dangerous-operation confirmation is now "No", so pressing Enter by accident does not execute

2026-10-19 (v1.7.3)
[Bug Fixes]
- Fixed unreadable text in the dangerous-operation confirmation window in light mode: native dialogs have a light background but kept the dark theme's text color, producing "light text on a white background"; the dialog background and text colors are now set explicitly, and the title, body and buttons all follow the theme correctly
- Fixed the text colors of native popups (drop-down menus, context menus, tooltips) not following the theme in light mode

2026-10-19 (v1.7.2)
[New Features]
- Added dark / light theme switching: the header bar icon button switches between dark, light and follow-system modes; the choice is saved automatically and kept after restart
- The light theme is a complete theme with its own palette, and also syncs the colors of native GTK widgets (dialogs, menus)

[Bug Fixes]
- Fixed vte3 installation failing ("889B5EBD... cannot be signed locally"): SteamOS's holo keyring and the Arch official keyring are independent, so running only pacman-key --populate archlinux did not import that key and the subsequent signing always failed; both the archlinux and holo keyrings are now imported
- Fixed "Fix Disk Write Errors" detection being ineffective: the old logic relied on "Volume is dirty" in ntfsfix output, but ntfsfix does not print that text, so every partition always showed "normal"; it now reads the Volume Flags dirty bit of $Volume
- Fixed mounted NTFS partitions being undetectable: ntfsinfo/ntfsfix need exclusive access to the device and report "in use" for mounted partitions; they are now temporarily unmounted before the check and remounted afterwards
- Fixed the pointless password prompt of "Fix Disk Write Errors": on a single-boot system with no NTFS partition it no longer asks for a sudo password and directly gives the conclusion and troubleshooting advice
- Fixed the misleading "all NTFS partitions are normal" conclusion when some partitions were skipped; it now clearly states how many were not checked
- Fixed the NTFS partition numbering not matching the actual input
- Fixed "Fix Shared Disk" not working after reboot: the old logic skipped whenever the partition was currently mounted, but udisks auto-mounts do not survive a reboot; a partition now only counts as ready when it is "mounted and written into fstab", ensuring auto-mount after reboot
- Fixed "Fix Shared Disk" accidentally deleting user data disks: it no longer force-unmounts and deletes fstab entries of non-NTFS partitions under /run/media/deck/ (ext4 / USB drives / external Btrfs disks)
- Fixed fstab entry matching using substrings and causing false positives (UUIDs with the same prefix were treated as existing); it now uses anchored exact matching
- Fixed fstab writes possibly losing entries: it now uses atomic replacement and keeps the original entry on failure
- Fixed fstab deletion failing because of incomplete sed regex escaping; it now compares fields exactly
- Fixed "Fix Shared Disk" still showing "all done" when mounting failed; it now shows the failure count
- Fixed the false success messages of "Fix Shared Disk" and UDisks2 modifications; they now report real results
- Fixed the theme "Follow System" reading a value it had overwritten itself (self-pollution); the system's real color scheme is now snapshotted at startup

2026-09-09 (v1.7.1)
[UI Improvements]
- Brand-new Steam Deck style theme: dark blue-black background + Steam blue highlights, rounded cards and taller touch-friendly list rows
- The left sidebar gains a panel title; the function list and search results become rounded card containers; the Help/Quit buttons use the accent color
- The header bar subtitle shows the system type; window buttons and the search box share a unified rounded style
- The task window gains a header bar and a dark terminal color scheme, showing a timer while running and "Task completed" when done
- The changelog page gains a page title; the About/Changelog bodies become rounded cards

2026-09-06 (v1.7.0, includes the v1.6.9 changes)
[UI Improvements]
- Added a top header bar (HeaderBar) showing the version number
- Added global function search: the top search box searches functions across categories and the result page shows the category
- The task window gains a runtime timer, making the task state clear at a glance
- Second confirmation for dangerous operations: Fix Boot / Fix Shared Disk / Uninstall Plugin Store / Clean hosts now ask for confirmation before running
- The bottom status bar shows system type, terminal mode and version
- Global style improvements: more comfortable list spacing and selection highlight

[Bug Fixes]
- Fixed cancel not working: the task process is now really terminated (previously "Cancel" only closed the window and the process kept running in the background)
- Fixed SteamOS read-only mode not being restored after being disabled: it is now restored automatically when all functions finish, avoiding system update problems
- Fixed cleaning hosts accidentally deleting system entries: it now removes only Steam-related domains and backs up automatically
- Fixed self-update lacking content validation: the downloaded content is validated before updating, preventing an error page from overwriting the script
- Fixed the version comparison logic: numbers are compared segment by segment, so a newer local version no longer prompts for a downgrade
- Fixed plugin version retrieval for ToMoon/Freedeck and others: invalid build tags are excluded, tags without a "v" prefix are supported, download assets are chosen intelligently (source packages are skipped), and updates are detected correctly when a stable version is installed
- Fixed the GitHub API check falsely reporting an error when piped
- Fixed Watt Toolkit silently downloading again when already installed: it now asks before overwriting

[Enhancements]
- Swap file creation adds a space pre-check and step-by-step dd/mkswap/swapon validation with clear errors on failure
- Accelerator / ToDesk / AnyDesk / app updates now show failure messages
- Installing Ubisoft/Epic pre-checks whether Proton Experimental exists and gives guidance when missing
- Plugin installers are unified into generic logic, mirrors are globally unified, and zip downloads come with integrity validation
- Icon assets are embedded in the script, self-contained offline, with no external folder needed

[Other]
- Switched to the $HOME variable throughout to reduce hardcoded paths
- Desktop shortcuts now use sys.executable for better compatibility
- Automatic fallback when no terminal emulator is available (konsole -> xterm, etc.)

2026-08-07 (v1.6.8) Adjusted the version comparison logic of some features installed from GitHub
2026-08-05 (v1.6.7) Fixed some bugs and improved the logic of some features
2026-08-04 (v1.6.6, includes the v1.6.4-v1.6.5 changes) Added the third-party game platform installation feature (currently Ubisoft, Epic, Battle.net)
2026-08-01 (v1.6.3, includes the v1.6.2 changes) Improved the shortcut deletion step of uninstalling installed apps and added a prompt asking whether to delete app data
2026-07-31 (v1.6.1) Added the GE-Proton Manager feature to install/uninstall GE compatibility layers
2026-07-30 (v1.6.0, includes the v1.5.7-v1.5.9 changes) Added the Freedeck plugin installation feature, fixed some bugs and improved some features
2026-07-29 (v1.5.6, includes the v1.5.2-v1.5.5 changes) Added the Fcitx 5 installation feature, fixed more bugs and adjusted the logic of some features
2026-07-27 (v1.5.1, includes the v1.5.0 changes) Fixed some bugs and improved some features
2026-07-26 (v1.4.9) Added the AskLink Remote installation feature
2026-07-25 (v1.4.8, includes the v1.3.9-v1.4.7 changes) Switched the changelog from plain text to illustrated form for easier operation, and revised and improved the features
Removed the admin password feature and added the Qiyou accelerator plugin installation feature
2026-07-18 (v1.3.8, includes the v1.3.7 changes) Replaced the steamcommunity 302 feature with Watt Toolkit (Steam++) for more usefulness
Adjusted parts of the plugin store, LSFG-VK and Framegen installation logic, renamed Calibrate Joystick to Calibrate Device, and added trigger calibration
2026-07-09 (v1.3.6) Reworked the Fix Shared Disk logic to be more universal
2026-07-08 (v1.3.5, includes the v1.3.4 changes) Removed the "Remote cannot connect, click me" feature and adjusted the mirror order for GitHub installs
2026-06-30 (v1.3.2) Fixed a bug in the AnyDesk installation feature
2026-06-28 (v1.3.1) Fixed a bug in the virtual memory size adjustment feature
2026-06-27 (v1.3.0) Added the "Remote cannot connect, click me" feature
Adjusted the AnyDesk installation logic to install from the official website
2026-06-03 (v1.2.7) Added the Install/Reinstall Clover boot feature with various improvements
2026-06-02 (v1.2.6) Adjusted the GitHub installation logic to support choosing between pre-release and stable versions
2026-05-31 (v1.2.4, includes the v1.1.9, v1.2.0 and v1.2.1 changes) Added the LSFG-VK and Framegen plugin installation features (installed from GitHub with mirror downloads)
Adjusted the plugin store installation steps to use a Chinese mirror for faster downloads and added automatic retry when the mirror download fails
Adjusted some parameters of the Steam Deck cache manager feature
2026-05-30 (v1.1.8) Adjusted the auto-update logic
2026-05-28 (v1.1.8, includes v1.1.7) Changed the plugin store feature to install from GitHub
Updated the auto-update steps after the toolbox opens
2026-03-17 (v1.1.2) Removed the "Install & Uninstall Baohulu" feature because Baohulu is no longer maintained
2026-03-05 (v1.1.1) Changed the ToMoon installation logic to clone and install from a Git repository
2026-03-02 (v1.1.0) Changed the plugin store installation logic to clone and install from a Git repository
2026-01-21 (v1.0.9) Added the Steam Community 302 installation feature
2026-01-16 (v1.0.8) Improved the text display of the virtual memory size adjustment feature
2026-01-11 (v1.0.7) Improved the virtual memory size adjustment feature
First released on GitHub with no detailed statistics; release date 2026-01-01"""

def about_body_text():
    if _current_lang == "en":
        return (
            f"\nSteam Deck Toolbox v{VERSION}\n"
            f"Made by Zhucy\n"
            f"Release date: January 1, 2026\n"
            f"About: a toolbox designed for the Steam Deck, integrating system optimization, "
            f"software installation, network tools and more.\n"
            f"Usage: click a category on the left to view its functions; the top search box "
            f"searches across categories; clicking a function opens a separate task window.\n"
            f"{REPO_URL}\n"
        )
    return (
        f"\nsteamdeck工具箱 v{VERSION}\n"
        f"制作人：Zhucy\n"
        f"发布日期：2026年1月1日\n"
        f"工具箱介绍：这是一个专为 Steam Deck 设计的工具箱，集成了系统优化、软件安装、网络工具等多种功能。\n"
        f"使用说明：点击左侧分类查看功能；顶部搜索框可跨分类查找；点击功能将弹出独立任务窗口。\n"
        f"{REPO_URL}\n"
    )

def build_icon_map():
    return {
        t("cat_support"): "pushpin.png",
        t("cat_changelog"): "clipboard_twemoji.png",
        t("cat_sysopt"): "hammer_wrench.png",
        t("cat_plugins"): "game_controller.png",
        t("cat_software"): "package.png",
        t("cat_network"): "globe.png",
        t("cat_update"): "inbox.png",
    }


def category_meta():
    """Stable category order for master-detail rail: (id, title_key, desc_key, icon_file)."""
    return [
        ("support", "cat_support", "cat_desc_support", "pushpin.png"),
        ("changelog", "cat_changelog", "cat_desc_changelog", "clipboard_twemoji.png"),
        ("sysopt", "cat_sysopt", "cat_desc_sysopt", "hammer_wrench.png"),
        ("plugins", "cat_plugins", "cat_desc_plugins", "game_controller.png"),
        ("software", "cat_software", "cat_desc_software", "package.png"),
        ("network", "cat_network", "cat_desc_network", "globe.png"),
        ("update", "cat_update", "cat_desc_update", "inbox.png"),
    ]


def build_category_tree():
    """按当前语言构建分类树；叶子第二项始终是稳定功能 key。"""
    return {
        t("cat_support"): [],
        t("cat_changelog"): [],
        t("cat_sysopt"): [
            (fl("install_chinese_source"), "install_chinese_source"),
            (fl("adjust_swap"), "adjust_swap"),
            (fl("fix_disk_write_error"), "fix_disk_write_error"),
            (fl("clear_hosts_cache"), "clear_hosts_cache"),
            (fl("grp_calibrate"), [
                (fl("calibrate_joystick_stick"), "calibrate_joystick_stick"),
                (fl("calibrate_joystick_trigger"), "calibrate_joystick_trigger"),
            ]),
            (fl("steamdeck_cache_manager"), "steamdeck_cache_manager"),
            (fl("ge_proton_manager"), "ge_proton_manager"),
            (fl("grp_emergency"), [
                (fl("emergency_steam_reset"), "emergency_steam_reset"),
                (fl("emergency_gamescope_reset"), "emergency_gamescope_reset"),
            ]),
            (fl("grp_boot"), [
                (fl("clover_install_or_reinstall"), "clover_install_or_reinstall"),
            ]),
        ],
        t("cat_plugins"): [
            (fl("grp_plugin_store"), [
                (fl("install_plugin_store"), "install_plugin_store"),
                (fl("uninstall_plugin_store"), "uninstall_plugin_store"),
            ]),
            (fl("grp_tomoon"), [
                (fl("install_tomoon_install"), "install_tomoon_install"),
                (fl("install_tomoon_uninstall"), "install_tomoon_uninstall"),
            ]),
            (fl("grp_freedeck"), [
                (fl("install_freedeck_install"), "install_freedeck_install"),
                (fl("install_freedeck_uninstall"), "install_freedeck_uninstall"),
            ]),
            (fl("grp_lsfg"), [
                (fl("install_decky_lsfg_vk_install"), "install_decky_lsfg_vk_install"),
                (fl("install_decky_lsfg_vk_uninstall"), "install_decky_lsfg_vk_uninstall"),
            ]),
            (fl("grp_framegen"), [
                (fl("install_decky_framegen_install"), "install_decky_framegen_install"),
                (fl("install_decky_framegen_uninstall"), "install_decky_framegen_uninstall"),
            ]),
            (fl("grp_cheatdeck"), [
                (fl("install_cheatdeck_install"), "install_cheatdeck_install"),
                (fl("install_cheatdeck_uninstall"), "install_cheatdeck_uninstall"),
            ]),
        ],
        t("cat_software"): [
            (fl("install_anydesk"), "install_anydesk"),
            (fl("install_todesk"), "install_todesk"),
            (fl("install_asklink"), "install_asklink"),
            (fl("install_flatpak_apps_gui"), "install_flatpak_apps_gui"),
            (fl("install_yellow_duck_software"), "install_yellow_duck_software"),
            (fl("grp_third_party"), [
                (fl("install_third_party_platform"), "install_third_party_platform"),
                (fl("uninstall_third_party_platform"), "uninstall_third_party_platform"),
            ]),
        ],
        t("cat_network"): [
            (fl("install_uu_accelerator"), "install_uu_accelerator"),
            (fl("install_xunyou_accelerator"), "install_xunyou_accelerator"),
            (fl("install_qiyou_accelerator"), "install_qiyou_accelerator"),
            (fl("grp_watt"), [
                (fl("watt_toolkit_install"), "watt_toolkit_install"),
                (fl("watt_toolkit_trust_cert"), "watt_toolkit_trust_cert"),
                (fl("watt_toolkit_uninstall"), "watt_toolkit_uninstall"),
            ]),
        ],
        t("cat_update"): [
            (fl("update_installed_apps"), "update_installed_apps"),
            (fl("grp_uninstall_apps"), [
                (fl("uninstall_anydesk"), "uninstall_anydesk"),
                (fl("uninstall_todesk"), "uninstall_todesk"),
                (fl("uninstall_other_flatpak_apps"), "uninstall_other_flatpak_apps"),
            ]),
        ],
    }



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

def compute_window_size(fallback_w=1040, fallback_h=680,
                        min_w=900, min_h=580, scale=1.0):
    """按屏幕可用工作区算出合适的窗口尺寸，返回 (宽, 高)。

    设计目标：既不占满屏幕，也不至于过小。

    做法：按 workarea 的高度分三档，每档用不同的目标占比与尺寸上限。
      · 小屏（掌机 1280x800 这类，可用高 < 900）
        占比 82% x 88%，上限 1280x760。掌机上略收一点边距，避免默认窗口偏满。
      · 1K（1920x1080 这类，可用高 < 1150）
        占比 80% x 86%，上限 1640x980。
      · 2K / 4K 大屏
        占比 70% x 76%，上限 1960x1260。大屏上不再按高占比铺开，
        否则窗口会大得离谱；但下限仍保证足够大。

    为什么用 workarea 而不是物理分辨率：
      workarea 已扣除顶部面板/任务栏，窗口加上标题栏后不会溢出屏幕底部。
      它返回的是逻辑像素，HiDPI 下已按 scale_factor 折算，
      所以 4K 屏在 2 倍缩放下与 1K 表现接近，物理观感一致。

    预期结果（括号内为 workarea）：
      1280x800  掌机    (1280x746)  → 约 1050x657
      1920x1080 1K      (1920x1040) → 约 1536x894
      2560x1440 2K      (2560x1400) → 约 1792x1064
      3840x2160 4K@1x   (3840x2120) → 1960x1260
      3840x2160 4K@2x   (1920x1060) → 约 1536x912

    取不到显示器信息时返回 fallback 尺寸，保证窗口一定能显示出来。

    参数 scale：整体缩放系数，默认 1.0 用于主窗口。
      任务窗等次级窗口传 0.8 左右，就会比主窗口小一号，且同样自适应屏幕。
    """
    try:
        display = Gdk.Display.get_default()
        if display is None:
            return fallback_w, fallback_h
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        if monitor is None:
            return fallback_w, fallback_h
        workarea = monitor.get_workarea()
        avail_w, avail_h = workarea.width, workarea.height
        if avail_w <= 0 or avail_h <= 0:
            return fallback_w, fallback_h

        # 按可用高度分档：小屏给足占比，大屏收敛占比并放大上限
        if avail_h < 900:
            width_ratio, height_ratio, max_w, max_h = 0.82, 0.88, 1280, 760
        elif avail_h < 1150:
            width_ratio, height_ratio, max_w, max_h = 0.80, 0.86, 1640, 980
        else:
            width_ratio, height_ratio, max_w, max_h = 0.70, 0.76, 1960, 1260

        # 按 scale 整体缩放（任务窗等次级窗口用 <1 的系数，保持比主窗口小一号）
        width_ratio *= scale
        height_ratio *= scale
        max_w = int(max_w * scale)
        max_h = int(max_h * scale)

        w = int(avail_w * width_ratio)
        h = int(avail_h * height_ratio)

        # 先夹到上下限之间（保证既不过小也不过宽）
        w = max(min(w, max_w), min_w)
        h = max(min(h, max_h), min_h)

        # 最后兜底：即使屏幕小于 min 尺寸，也不能让窗口超出可用区域
        w = min(w, max(avail_w - 32, 320))
        h = min(h, max(avail_h - 32, 240))

        return int(w), int(h)
    except Exception:
        return fallback_w, fallback_h

# ============================================================================
# 崩溃与异常兜底：让任何失败都有可见反馈
#
# 为什么需要：GTK 的信号回调（按钮 clicked、超时、线程 idle 回调）里抛出的
# 异常不会被调用方捕获，只会经 sys.excepthook 打到 stderr。用户从桌面快捷方式
# 启动时 stderr 没有任何窗口承载，表现出来的就是「点了按钮什么都没发生」——
# 既没有报错也没有窗口，看起来像按钮失灵或程序卡死。
#
# 这里的做法：装上 excepthook，把 traceback 写进日志文件，并弹一个错误框说明
# 发生了什么、日志在哪。程序不会因此退出，用户还能继续用别的功能。
# ============================================================================
APP_LOG_PATH = os.path.join(os.path.expanduser("~"), ".cache", "steamdeck_toolbox_error.log")
_excepthook_installed = False
_in_excepthook = False       # 防止错误框自身出错导致无限递归


def log_exception(exc_type, exc_value, exc_tb, context=""):
    """把异常写进日志文件，返回日志路径（写失败也返回路径，界面照常提示）。"""
    import traceback as _tb
    try:
        os.makedirs(os.path.dirname(APP_LOG_PATH), exist_ok=True)
        with open(APP_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("\n===== %s =====\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
            if context:
                f.write("context: %s\n" % context)
            f.write("version: %s\n" % VERSION)
            _tb.print_exception(exc_type, exc_value, exc_tb, file=f)
    except Exception:
        pass
    return APP_LOG_PATH


def report_exception(exc_type, exc_value, exc_tb, context=""):
    """记录异常并弹窗告知。异常发生时程序没崩，所以给用户一个「继续」按钮。"""
    global _in_excepthook
    path = log_exception(exc_type, exc_value, exc_tb, context)
    # 错误框自己再出错时不要再递归弹窗（否则会连环弹到卡死）
    if _in_excepthook:
        print("exception while showing error dialog", file=sys.stderr)
        return
    _in_excepthook = True
    try:
        dlg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
                                Gtk.ButtonsType.NONE,
                                "这个功能执行出错，已跳过" if get_lang() != "en"
                                else "This action failed and was skipped")
        dlg.add_button(t("ok"), Gtk.ResponseType.OK)
        detail = "%s: %s" % (exc_type.__name__, exc_value)
        if get_lang() == "en":
            hint = ("The rest of the toolbox still works.\n\n"
                    "Detail: %s\nLog: %s" % (detail, path))
        else:
            hint = ("工具箱的其它功能不受影响。\n\n"
                    "错误：%s\n日志：%s" % (detail, path))
        dlg.format_secondary_text(hint)
        fix_dialog_size(dlg)
        dlg.run()
        dlg.destroy()
    except Exception as e:
        print("failed to show error dialog: %s" % e, file=sys.stderr)
    finally:
        _in_excepthook = False


def install_excepthook():
    """安装全局异常钩子。main() 里调用；测试可重复调用（幂等）。"""
    global _excepthook_installed
    if _excepthook_installed:
        return
    _excepthook_installed = True

    def _hook(exc_type, exc_value, exc_tb):
        # Ctrl+C 保持默认行为，不弹窗
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        report_exception(exc_type, exc_value, exc_tb, context="unhandled")

    sys.excepthook = _hook


def guarded(fn):
    """装饰 GTK 回调：异常不再「无声消失」，而是走统一的报错路径。

    为什么不用 try/except 包住每个回调：要改几十处、还容易漏。装饰器只在
    run_function 这类统一入口上用，其余靠 install_excepthook 兜住。
    """
    import functools
    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            report_exception(*sys.exc_info(), context=getattr(fn, "__name__", ""))
            return None
    return _wrapper


def fix_dialog_size(dlg):
    """修正对话框首次显示时「先小后大」的闪烁。

    背景：为消除深色模式下对话框标题栏的白条，启用了 gtk-dialogs-use-header
    让 GTK 用 CSD 绘制标题栏。但 GTK3 在 KWin 下首次 map 时尺寸协商分两步：
      第 1 帧 ~498x296（错误尺寸，内容被裁剪）
      第 2 帧 ~566x364（正确尺寸）
    用户会看到窗口闪一下。

    试过无效的方案：
      - set_size_request / set_geometry_hints / set_default_size：首帧仍偏小
      - realize()+resize()：会触发窗口闪现，且 resize 被 run 内的 show_all 覆盖
      - 自建 Gtk.Dialog：同样有首帧过渡，是 CSD 固有行为
      - X11 _GTK_THEME_VARIANT=dark：KWin 不响应，标题栏仍是浅色

    有效方案：先完全透明，等尺寸稳定后再恢复不透明。
    这样用户看到的第一个可见帧就是正确尺寸。

    同时仍设置 natural_size（不能用 minimum，带 CSD 时 minimum 高度可能更大，
    取 max 会让对话框过高、留下大片空白）。
    """
    try:
        req = dlg.get_preferred_size()
        w = req.natural_size.width or req.minimum_size.width
        h = req.natural_size.height or req.minimum_size.height
        if w > 0 and h > 0:
            dlg.set_size_request(w, h)

        # 遮住首帧尺寸协商（WM 不支持透明度时会退化为原有的轻微闪烁）
        dlg.set_opacity(0.0)

        def _reveal():
            try:
                dlg.set_opacity(1.0)
            except Exception:
                pass
            return False

        GLib.timeout_add(90, _reveal)
    except Exception:
        pass


def apply_app_css(mode=None):
    """应用主题样式；mode 为 dark/light/system，None 表示使用已保存的偏好。"""
    global _css_provider
    try:
        if mode is None:
            mode = load_theme_pref()
        resolved = resolve_theme_mode(mode)

        screen = Gdk.Screen.get_default()
        if screen is None:
            return
        css = build_css(resolved)

        # 同步 GTK 自身的深色偏好，让对话框、下拉菜单等原生控件配色一致
        try:
            settings = Gtk.Settings.get_default()
            if settings is not None:
                settings.set_property("gtk-application-prefer-dark-theme", resolved == "dark")
                # 让 GtkDialog 使用 CSD 标题栏。否则 KDE/KWin 会用系统主题绘制对话框
                # 标题区，浅色系统主题 + 深色应用主题时表现为一条白边，CSS 无法覆盖。
                try:
                    if settings.find_property("gtk-dialogs-use-header") is not None:
                        settings.set_property("gtk-dialogs-use-header", True)
                except Exception:
                    pass
        except Exception:
            pass

        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode('utf-8'))
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
    # 覆盖 Steam Deck / 常见 Linux 桌面上的终端；顺序按常见度与参数兼容性排。
    for t in ("konsole", "gnome-terminal", "xfce4-terminal", "lxterminal", "xterm",
              "kitty", "foot", "alacritty", "kgx", "tilix", "qterminal",
              "mate-terminal", "terminator", "wezterm"):
        if shutil.which(t):
            return t
    return None

def terminal_command(term, command_str):
    """不同终端用不同的命令行参数把命令喂给它。"""
    if term == "gnome-terminal":
        return [term, "--", "bash", "-c", command_str]
    if term == "kitty":
        return [term, "bash", "-c", command_str]
    if term == "foot":
        return [term, "bash", "-c", command_str]
    if term == "alacritty":
        return [term, "-e", "bash", "-c", command_str]
    if term == "kgx":                 # GNOME Console
        return [term, "--", "bash", "-c", command_str]
    if term == "tilix":
        return [term, "-e", "bash", "-c", command_str]
    if term == "wezterm":
        return [term, "start", "--", "bash", "-c", command_str]
    # konsole / xterm / xfce4-terminal / lxterminal / qterminal /
    # mate-terminal / terminator 都用 -e
    return [term, "-e", "bash", "-c", command_str]

def launch_terminal(command_str):
    """在可用的终端模拟器中执行命令，返回是否成功启动。"""
    term = find_terminal()
    if not term:
        return False
    try:
        subprocess.Popen(terminal_command(term, command_str),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL, start_new_session=True)
        return True
    except Exception:
        return False

# GUI 层二次确认的危险操作（对应 bash 内部提示较弱的系统级修改）
# clover_install_or_reinstall 会往 EFI 分区写文件、替换 BOOTX64.EFI、改 efibootmgr
# 启动项，一旦出错可能导致机器无法启动，必须走确认框。
DANGEROUS_FUNCS = {"fix_boot", "fix_shared_disk", "uninstall_plugin_store", "clear_hosts_cache",
                   "clover_install_or_reinstall",
                   "emergency_steam_reset", "emergency_gamescope_reset"}

# 每个危险功能的额外风险说明（缺省用通用文案）
DANGEROUS_HINTS = {
    "clover_install_or_reinstall": "该功能会向 EFI 系统分区写入 Clover 引导文件，"
                                   "替换 BOOTX64.EFI 并修改 EFI 启动项。\n"
                                   "操作不当可能导致设备无法开机，请确认已了解风险并做好备份。",
    "fix_boot": "该功能会修改 EFI 启动顺序，把 Clover 设为第一启动项。",
    "fix_shared_disk": "该功能会修改 /etc/fstab 与 UDisks2 策略文件，用于自动挂载 Windows 分区。",
    "uninstall_plugin_store": "该功能会删除已安装的插件商店及其插件数据。",
    "clear_hosts_cache": "该功能会修改系统 /etc/hosts 文件（会自动备份）。",
    "emergency_steam_reset": "将备份并重置 Steam 配置/启动缓存；不删 steamapps。\n"
                            "本地 Steam 设置可能丢失。",
    "emergency_gamescope_reset": "将备份并清理 Gamescope/游戏模式相关状态；不删游戏。",
}
DEFAULT_DANGEROUS_HINT = "该功能会修改系统引导、挂载或系统文件，请确认已了解风险。"

# ============================================================================
# 内嵌 Bash 脚本
# ============================================================================
BASH_SCRIPT_ZH = r'''#!/bin/bash
set -uo pipefail
# FIX-SOFTWARE: avoid predictable shared /tmp path (symlink/TOCTOU).
TEMP_DIR="$(mktemp -d /tmp/steamdeck_toolbox.XXXXXXXX 2>/dev/null || echo /tmp/steamdeck_toolbox)"
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
trap 'ec=$?; restore_readonly; cleanup_temp; exit $ec' EXIT
# 用户点「取消」会收到 INT/TERM：用专用退出码 75 区分「已取消」与「成功(0)」。
# 不写 exit 0，否则 TaskWindow 会把取消当成功显示「任务已完成」。
# EXIT trap 仍用 ec=$? 保留这个真实退出码（restore_readonly / cleanup_temp 不能改掉它）。
CANCEL_EXIT_CODE=75
trap 'echo -e "\n${YELLOW}用户取消操作，关闭窗口。${NC}"; exit $CANCEL_EXIT_CODE' INT TERM

PYTHON_CMD="python3"
command -v python3 &>/dev/null || PYTHON_CMD="python"
# 当前用户名/组：不能硬编码 deck，非 deck 用户名的设备会把文件属主改错
CURRENT_USER="${USER:-$(id -un)}"
CURRENT_GROUP="$(id -gn "$CURRENT_USER" 2>/dev/null || echo "$CURRENT_USER")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'; NC='\033[0m'

# ===== FIX-SOFTWARE: shared safe helpers =====
# Resolve the real Desktop dir (XDG) and make sure it exists.
fs_desktop_dir() {
    local d=""
    if command -v xdg-user-dir >/dev/null 2>&1; then
        d="$(xdg-user-dir DESKTOP 2>/dev/null)"
    fi
    [ -n "$d" ] && [ "$d" != "$HOME" ] || d="${XDG_DESKTOP_DIR:-$HOME/Desktop}"
    mkdir -p "$d" 2>/dev/null || d="$HOME/Desktop"
    printf '%s' "$d"
}
# curl with hard fail/timeouts; download to a temp file; verify it is a non-trivial,
# non-HTML shell text before anything gets executed.
# usage: fs_fetch_shell URL TMPFILE  -> 0 ok, 1 fail (TMPFILE cleaned on failure)
fs_fetch_shell() {
    local url="$1" out="$2" rc=0
    rm -f "$out"
    curl -fsSL --connect-timeout 15 --max-time 120 -o "$out" "$url" || rc=$?
    # FIX-QIYOU: 有些厂商的安装域名只开了 80 端口、没开 443（例如 sd.qiyou.cn）。
    # HTTPS 连接失败时自动退回 HTTP，并通过下面的内容校验；同时明确告知用户
    # 正在使用明文连接，让用户自己决定是否继续以 root 执行。
    if [ "$rc" -ne 0 ] && [ "${url#https://}" != "$url" ]; then
        local http_url="http://${url#https://}" rc2=0
        echo -e "${YELLOW}⚠️  HTTPS 连接失败，尝试改用 HTTP 明文连接: $http_url${NC}"
        echo -e "${YELLOW}   明文连接无法验证对方身份，请确认来源可信后再继续。${NC}"
        curl -fsSL --connect-timeout 15 --max-time 120 -o "$out" "$http_url" || rc2=$?
        if [ "$rc2" -eq 0 ]; then rc=0; url="$http_url"; fi
    fi
    if [ "$rc" -ne 0 ]; then
        rm -f "$out"; return 1
    fi
    if [ ! -s "$out" ]; then
        rm -f "$out"; return 1
    fi
    # Reject obvious HTML error / login pages (case-insensitive, first 4KB).
    if head -c 4096 "$out" | grep -qiE '<!doctype[[:space:]]+html|<html([[:space:]>])|<head([[:space:]>])|<title>'; then
        rm -f "$out"; return 1
    fi
    # Must look like a shell script: shebang, or shell keywords / parameter expansion.
    if ! grep -qE '(^#!.*(/|env )?(ba)?sh|^#!/bin/(ba)?sh|\b(sudo|apt|pacman|systemctl|echo|set|if|then|fi|for|while|curl|wget|mkdir|cp|mv|rm|cat|chmod|chown)\b|\$\(|`|#.*)' "$out"; then
        rm -f "$out"; return 1
    fi
    return 0
}
# Compare dotted version strings: returns 0 if $1 > $2, 1 otherwise (equal/less/invalid).
fs_ver_gt() {
    local a="$1" b="$2" i av bv
    [ -n "$a" ] && [ -n "$b" ] || return 1
    IFS='.' read -ra A <<< "$a"; IFS='.' read -ra B <<< "$b"
    for i in "${!A[@]}"; do
        av="${A[$i]}"; bv="${B[$i]:-0}"
        [[ "$av" =~ ^[0-9]+$ ]] || av=0
        [[ "$bv" =~ ^[0-9]+$ ]] || bv=0
        if [ "$((10#$av))" -gt "$((10#$bv))" ]; then return 0; fi
        if [ "$((10#$av))" -lt "$((10#$bv))" ]; then return 1; fi
    done
    return 1
}
# FIX-PROGRESS: 把 flatpak/ostree 用 \r 原地刷新的进度条转成干净的逐行文本，
# 保留「Receiving objects: NN% ... X MB/s」这类含百分比与速度的行。
# --noninteractive 会关闭进度输出，所以更新命令要去掉它并设 FLATPAK_TTY_PROGRESS=1；
# 本过滤器负责清除 ANSI 控制符与光标位置应答，避免再次出现乱码。
fp_progress_filter() {
    "${PYTHON_CMD:-python3}" -u -c '
import sys, re
ansi = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*(?:\x07|\x1b\\)|\x1b[@-Z\\\\-_]")
# 属于「同一条进度行」的帧：X/Y 步骤、百分比、速度、进度条、正在更新/正在安装
prog = re.compile(r"\d+/\d+|\d+%|\d+\s*(?:字节|bytes|B|kB|MB|GB)/s|[█▍▌▊▏▎▋▐░]|正在更新|正在安装|Receiving objects")
def clean(t):
    t = ansi.sub("", t)
    t = re.sub(r"\^\[\[[0-9;]*R", "", t)
    return t.strip()
buf = b""
active = False
def emit_progress(t):
    # 回车 + 清到行尾：始终覆盖同一行，不换行，视觉上只显示一行
    global active
    sys.stdout.write("\r\033[K" + t)
    sys.stdout.flush()
    active = True
def emit_log(t):
    global active
    if active:
        sys.stdout.write("\n")
        active = False
    print(t, flush=True)
while True:
    ch = sys.stdin.buffer.read(1)
    if not ch:
        break
    if ch[0] in (13, 10):
        t = clean(buf.decode("utf-8", "replace"))
        buf = b""
        if not t:
            continue
        (emit_progress if prog.search(t) else emit_log)(t)
    else:
        buf += ch
if buf:
    t = clean(buf.decode("utf-8", "replace"))
    if t:
        (emit_progress if prog.search(t) else emit_log)(t)
if active:
    sys.stdout.write("\n")
    sys.stdout.flush()
' 2>/dev/null
}

# Verify a downloaded Windows installer is not an HTML error page.
# usage: fs_verify_installer FILE mz|msi
fs_verify_installer() {
    local f="$1" kind="$2" sz
    [ -f "$f" ] || return 1
    sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
    [ "$sz" -ge 65536 ] || return 1
    if head -c 4096 "$f" | grep -qiE '<!doctype[[:space:]]+html|<html([[:space:]>])|<head([[:space:]>])|<title>'; then
        return 1
    fi
    if [ "$kind" = "mz" ]; then
        [ "$(head -c 2 "$f")" = "MZ" ] || return 1
        if command -v file >/dev/null 2>&1; then
            file "$f" | grep -qiE 'PE32|MS-DOS|executable' || return 1
        fi
    else
        # MSI is an OLE2 compound file: D0 CF 11 E0 A1 B1 1A E1
        [ "$(head -c 8 "$f" | od -An -tx1 | tr -d ' \n')" = "d0cf11e0a1b11ae1" ] || return 1
    fi
    return 0
}
# Reject tar/zip archives containing path traversal or absolute paths.
# usage: fs_archive_safe ARCHIVE tar|zip
fs_archive_safe() {
    local f="$1" kind="$2" line
    if [ "$kind" = "tar" ]; then
        line=$(tar -tf "$f" 2>/dev/null | grep -E '(^/|(^|/)\.\./)' | head -1)
    else
        line=$(unzip -Z1 "$f" 2>/dev/null | grep -E '(^/|(^|/)\.\./)' | head -1)
    fi
    if [ -n "$line" ]; then
        return 1
    fi
    return 0
}
# ===== END FIX-SOFTWARE shared helpers =====

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
    # FIX-SOFTWARE: /dev/tty EOF 时按「取消」处理，避免 read 失败后
    # 变量沿用上一次的值被误判为确认，以及菜单空转死循环。
    local confirm=""
    read -r -n1 -p "按回车键或 A 键确认，其他键取消: " confirm < /dev/tty || { echo; return 1; }
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

# 需要写系统分区的功能用这个：先查状态再决定要不要 disable。
# 直接调 disable_readonly 的问题是——系统本来就已可写（用户手动关掉只读）时，
# `steamos-readonly disable` 同样返回成功，标志会被置 1，退出时 trap 就把用户
# 自己设的「可写」强行改回「只读」，覆盖掉用户的设置。
ensure_writable() {
    command -v steamos-readonly &>/dev/null || return 0
    if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
        if sudo steamos-readonly disable 2>/dev/null; then
            RO_READONLY_DISABLED_BY_US=1
            echo -e "${GREEN}✓ 已禁用只读模式${NC}"
        else
            echo -e "${RED}✗ 禁用只读模式失败，操作中止。${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✓ 只读模式已处于可写状态${NC}"
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

install_chinese_source() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════ 切换 Flatpak 软件源 ════════════${NC}"
    echo "可选择国内镜像加速，也可恢复为官方源。"
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
    echo -e "${CYAN}步骤2: 选择 Flatpak 软件源${NC}"
    echo ""

    # 实测（2026-10，逐个探测 summary.idx 魔数确认是否为真实 ostree 数据）：
    #   ✓ 可用：
    #     mirrors.ustc.edu.cn/flathub            中科大（yadex 增量方案），已验证
    #     unicom.mirrors.ustc.edu.cn/flathub     中科大联通节点
    #     mobile.mirrors.ustc.edu.cn/flathub     中科大移动节点
    #     mirrors.cernet.edu.cn/flathub          CERNET 聚合入口（按地理位置分发到各校节点）
    #   ✗ 不可用（保留记录，避免以后又踩）：
    #     mirror.sjtu.edu.cn/flathub   → 301 跳回官方 dl.flathub.org，等于没加速
    #     mirrors.nju / sustech / bfsu / tuna / aliyun / tencent / huawei / zju / jlu /
    #     iscas / xjtu / scau / qlu 的 flathub → 返回 HTML 首页或 404，没有这个镜像
    #
    # 所有国内镜像都只是 Flathub 的「缓存」而不是完整镜像：
    # 未命中的对象会 302 回 dl.flathub.org，所以官方站仍需要基本连通性。
    local MIRROR_LABELS=(
        "中科大 (USTC)"
        "中科大-联通节点"
        "中科大-移动节点"
        "CERNET 教育网聚合"
        "恢复官方源 (dl.flathub.org)"
    )
    local MIRROR_URLS=(
        "https://mirrors.ustc.edu.cn/flathub/"
        "https://unicom.mirrors.ustc.edu.cn/flathub/"
        "https://mobile.mirrors.ustc.edu.cn/flathub/"
        "https://mirrors.cernet.edu.cn/flathub/"
        "https://dl.flathub.org/repo/"
    )

    # 显示当前源：能匹配到菜单里的 5 个预设源就显示对应名称，否则显示原始地址
    local FP_OLD_URL FP_CURRENT_LABEL="" FP_NORM_OLD FP_NORM_URL mi
    # 注意：flatpak 没有 remote-get-url 这个子命令，要从 remotes 列表里取
    FP_OLD_URL=$(flatpak remotes --columns=name,url 2>/dev/null | awk '$1 == "flathub" {print $2; exit}')
    if [ -n "$FP_OLD_URL" ]; then
        # 规范化后再比：去掉结尾斜杠并转小写，避免仅斜杠/大小写不同就匹配不上
        FP_NORM_OLD=$(echo "$FP_OLD_URL" | tr '[:upper:]' '[:lower:]' | sed 's#/*$##')
        for mi in "${!MIRROR_URLS[@]}"; do
            FP_NORM_URL=$(echo "${MIRROR_URLS[$mi]}" | tr '[:upper:]' '[:lower:]' | sed 's#/*$##')
            if [ "$FP_NORM_OLD" = "$FP_NORM_URL" ]; then
                FP_CURRENT_LABEL="${MIRROR_LABELS[$mi]}"
                break
            fi
        done
        if [ -n "$FP_CURRENT_LABEL" ]; then
            echo -e "当前 flathub 源: ${GREEN}${FP_CURRENT_LABEL}${NC}"
            echo -e "  地址: ${CYAN}${FP_OLD_URL}${NC}"
        else
            echo -e "当前 flathub 源: ${CYAN}${FP_OLD_URL}${NC}"
            echo -e "${YELLOW}  （该地址不在预设的 5 个软件源中）${NC}"
        fi
        echo ""
    fi

    echo "请选择要使用的软件源（国内源可加速下载，官方源需能访问 dl.flathub.org）："
    local i
    for i in "${!MIRROR_LABELS[@]}"; do
        echo "  $((i+1)). ${MIRROR_LABELS[$i]}"
    done
    echo ""
    local choice
    while true; do
        read -p "请输入编号 [1-${#MIRROR_LABELS[@]}]（回车取消）: " choice < /dev/tty || { echo "操作已取消。"; return 0; }
        [ -z "$choice" ] && { echo "操作已取消。"; return 0; }
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRROR_LABELS[@]} ]; then
            break
        fi
        echo -e "${RED}输入无效，请输入 1-${#MIRROR_LABELS[@]} 之间的数字。${NC}"
    done

    local FP_MIRROR="${MIRROR_URLS[$((choice-1))]}"
    local FP_MIRROR_NAME="${MIRROR_LABELS[$((choice-1))]}"
    echo ""
    echo -e "${CYAN}已选择: ${FP_MIRROR_NAME}${NC}"
    echo "  地址: $FP_MIRROR"

    local FP_KEY_TMP="${TEMP_DIR}/flathub.gpg"

    # 先确认 sudo 可用：系统级 flatpak remote 配置需要 root，
    # 若这里不先验证，后面 remote-modify 会卡在密码提示上（输出被 2>/dev/null 吞掉，看起来像无响应）
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}✗ 需要 sudo 权限才能修改 Flatpak 源，已中止。${NC}"
        return 1
    fi

    # 1) 确保 flathub 签名公钥存在（镜像的摘要带 flathub 签名，缺公钥会被拒绝）
    #
    # 关键在于：公钥是「装一次就长期有效」的东西，正常设备上早就有了，
    # 不需要每次切源都从 dl.flathub.org 重新下一遍。以前每次无条件下载，
    # 而 dl.flathub.org 现在经常连不上，于是每次都打一条「无法下载公钥」的
    # 黄字警告 —— 但公钥其实一直都在，功能完全正常，属于纯误导。
    # 所以改成：先看本地有没有可用公钥，有就跳过下载。
    echo ""
    echo "正在检查 flathub 签名公钥..."
    local FP_KEYSTORE="/var/lib/flatpak/repo/flathub.trustedkeys.gpg"
    local have_key=false
    if [ -s "$FP_KEYSTORE" ]; then
        # 文件存在还不够，确认里面确实是 flathub 的签名密钥（避免损坏的空壳文件误判）
        if command -v gpg &>/dev/null; then
            gpg --show-keys "$FP_KEYSTORE" 2>/dev/null | grep -qi "Flathub" && have_key=true
        else
            have_key=true
        fi
    fi

    if $have_key; then
        echo -e "${GREEN}✓ 签名公钥已存在，无需重复导入${NC}"
    else
        # 本地没有公钥才去下载：先官方，再试镜像（部分镜像也托管了这份公钥）
        echo -e "${YELLOW}本地未找到 flathub 公钥，正在下载...${NC}"
        local key_url got_key=false
        for key_url in \
            "https://dl.flathub.org/repo/flathub.gpg" \
            "https://mirrors.ustc.edu.cn/flathub/flathub.gpg" \
            "https://mirrors.cernet.edu.cn/flathub/flathub.gpg"; do
            if curl -fsSL --connect-timeout 10 --max-time 30 -o "$FP_KEY_TMP" "$key_url" 2>/dev/null \
               && [ -s "$FP_KEY_TMP" ] \
               && gpg --show-keys "$FP_KEY_TMP" >/dev/null 2>&1; then
                got_key=true
                echo -e "${CYAN}  已从 $key_url 获取${NC}"
                break
            fi
        done

        if $got_key; then
            if sudo flatpak remote-modify --gpg-import="$FP_KEY_TMP" flathub 2>/dev/null; then
                echo -e "${GREEN}✓ 已导入 flathub 签名公钥${NC}"
            else
                echo -e "${YELLOW}⚠ 导入公钥失败，继续（若安装报签名错误再手动处理）${NC}"
            fi
        else
            # 只有真的拿不到才告警，并说清后果和办法
            echo -e "${YELLOW}⚠ 未能获取 flathub 签名公钥。${NC}"
            echo -e "${YELLOW}  影响：安装/更新时会因签名校验失败而报错（Could not find public key）。${NC}"
            echo -e "${YELLOW}  办法：网络恢复后重新运行本功能，或手动执行：${NC}"
            echo -e "${YELLOW}    curl -fsSL https://dl.flathub.org/repo/flathub.gpg -o /tmp/f.gpg${NC}"
            echo -e "${YELLOW}    sudo flatpak remote-modify --gpg-import=/tmp/f.gpg flathub${NC}"
        fi
    fi
    rm -f "$FP_KEY_TMP"

    # 2) 切换 flathub 地址
    if ! sudo flatpak remote-modify flathub --url="$FP_MIRROR" 2>/dev/null; then
        echo -e "${RED}✗ Flatpak 源配置失败${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Flatpak 源已切换为 $FP_MIRROR${NC}"

    # 3) 实际拉一次元数据验证，不只看命令返回值
    #    remote-info 必须指定分支，否则会因"多个可用分支"直接报错，被误判为镜像不可用
    echo ""
    echo "正在验证源可用性..."
    if timeout 90 flatpak remote-info flathub org.freedesktop.Platform/x86_64/24.08 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ 验证通过（可正常查询软件包）${NC}"
    else
        # 官方源本身也可能因为网络问题暂时查不到，不能一律判为「源坏了」
        if [ "$FP_MIRROR" = "https://dl.flathub.org/repo/" ]; then
            echo -e "${YELLOW}⚠ 已切回官方源，但当前无法验证（dl.flathub.org 可能不通）。${NC}"
            echo -e "${YELLOW}  源地址本身已设置成功，网络恢复后即可正常使用。${NC}"
            return 0
        fi
        echo -e "${RED}✗ 该源验证失败，正在回滚到原来的源...${NC}"
        if [ -n "$FP_OLD_URL" ]; then
            sudo flatpak remote-modify flathub --url="$FP_OLD_URL" 2>/dev/null \
                && echo -e "${YELLOW}已回滚到原地址: $FP_OLD_URL${NC}" \
                || echo -e "${RED}回滚失败，请手动执行: sudo flatpak remote-modify flathub --url=$FP_OLD_URL${NC}"
        else
            echo -e "${RED}未获取到原地址，请手动恢复: sudo flatpak remote-modify flathub --url=https://dl.flathub.org/repo/${NC}"
        fi
        echo -e "${YELLOW}提示：可换一个源再试（部分镜像偶尔会临时失效）。${NC}"
        return 1
    fi
    echo ""
    if [ "$FP_MIRROR" = "https://dl.flathub.org/repo/" ]; then
        echo -e "${GREEN}✓ 已恢复为 Flathub 官方源。${NC}"
    else
        echo -e "${GREEN}✓ 已切换到 ${FP_MIRROR_NAME}。${NC}"
        echo -e "${YELLOW}说明：国内镜像都是 Flathub 的缓存，未命中的文件会跳回官方站，${NC}"
        echo -e "${YELLOW}      因此仍需要能基本连通 dl.flathub.org。${NC}"
    fi
    echo ""
    echo -e "${CYAN}  如需再次切换，重新运行本功能即可（含「恢复官方源」选项）。${NC}"
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
    # FIX-LEAD: cryo swapoff
    # swapoff 失败时仍删除 /home/swapfile 会让正在使用的 Swap 失去路径且无法恢复，
    # 低内存时可能触发 OOM。先确认旧 Swap 已全部停用，否则中止并保持原状。
    if ! sudo swapoff /home/swapfile 2>/dev/null && swapon --show=NAME --noheadings 2>/dev/null | grep -qx '/home/swapfile'; then
        echo -e "${RED}✗ Failed to deactivate existing /home/swapfile; aborted, original swap untouched.${NC}"
        return 1
    fi
    if ! sudo swapoff -a 2>/dev/null; then
        echo -e "${RED}✗ Failed to deactivate all swap devices; aborted to avoid deleting an active file.${NC}"
        return 1
    fi
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
        # zramctl --reset 在部分内核上会「实际已经重置成功但返回非 0」：
        # 写完 sysfs 的 reset 后设备状态瞬间变化，命令读回校验失败。
        # 因此不能只看返回码，要按重置后的实际状态判定。
        sudo zramctl /dev/zram0 --reset 2>/dev/null
        local _zram_still_on=0 _zram_disk_size=""
        if swapon --show=NAME --noheadings 2>/dev/null | grep -qx "/dev/zram0"; then
            _zram_still_on=1
        fi
        _zram_disk_size=$(cat /sys/block/zram0/disksize 2>/dev/null || echo "")
        if [ "$_zram_still_on" -eq 0 ] && { [ ! -e /sys/block/zram0/disksize ] || [ "${_zram_disk_size:-1}" = "0" ]; }; then
            echo -e "${GREEN}✓ ZRAM 已重置${NC}"
        else
            echo -e "${YELLOW}⚠️ ZRAM 仍在使用中（设备未释放），重启后会自动恢复默认配置。${NC}"
            echo "    当前交换设备：$(swapon --show=NAME --noheadings 2>/dev/null | tr '\n' ' ')"
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
    echo "  正在运行 ntfsfix -d（修复常见错误并清除 dirty 脏标志）..."
    local _dmark _mlog
    _dmark="$(sudo dmesg 2>/dev/null | wc -l)"
    # -d/--clear-dirty：能修复且能挂载时清除卷上的 dirty 标志。
    # 不带 -d 时 ntfsfix 只做基础修复，脏标志可能残留，ntfs3 依旧拒挂。
    if sudo ntfsfix -d "$device" 2>/dev/null; then
        echo -e "${GREEN}  ✓ 修复成功（已尝试清除 dirty 标志）${NC}"
    else
        echo -e "${RED}  ✗ 修复失败${NC}"
        _mlog="$(sudo dmesg 2>/dev/null | tail -n "+$(( _dmark + 1 ))")"
        if [ -n "$_mlog" ]; then
            echo "  本次操作的 dmesg 输出："
            echo "$_mlog" | grep -iE 'ntfs|volume' | tail -8 | sed 's/^/    /'
        fi
        echo "  若提示卷损坏严重，请进 Windows 运行 chkdsk /f 后再试。"
        # FIX-LEAD: fix_single_ntfs ZH
        return 1
    fi
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
    # 确认存在 NTFS 分区后，才需要 root 权限。
    # 顺序刻意排成「先要密码 → 再解只读 → 再补工具」：
    #   ntfsfix / ntfsinfo 在 Arch 上属于 ntfsprogs 包，而装包要写系统目录，
    #   SteamOS 上必须先 steamos-readonly disable。所以密码在第一步就拿，
    #   后面装包才不会卡在权限上。缺工具也不再让用户自己去装。
    # ------------------------------------------------------------------
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
    echo "步骤3: 检查 NTFS 工具（ntfsfix / ntfsinfo）"
    # 缺什么补什么，装完就地重查；装不上才报错，且直接给出可复制的命令。
    local missing_ntfs_tools=()
    command -v ntfsfix  &> /dev/null || missing_ntfs_tools+=("ntfsfix")
    command -v ntfsinfo &> /dev/null || missing_ntfs_tools+=("ntfsinfo")

    if [ ${#missing_ntfs_tools[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ ntfsfix / ntfsinfo 已就绪${NC}"
    else
        echo -e "${YELLOW}  缺少: ${missing_ntfs_tools[*]}，正在自动安装...${NC}"
        # Arch/SteamOS：ntfsfix、ntfsinfo 都在 ntfsprogs 包里（不在 ntfs-3g 包里）
        # Debian/Ubuntu：同名工具在 ntfs-3g 包里，两个系别包名相反，不能混用
        if command -v pacman &> /dev/null; then
            sudo pacman -S --needed --noconfirm ntfsprogs >/dev/null 2>&1
        elif command -v apt-get &> /dev/null; then
            sudo apt-get install -y ntfs-3g >/dev/null 2>&1
        fi
        # 清掉 bash 的命令查找缓存：刚装上的二进制若不刷新，可能仍被判为找不到
        hash -r 2>/dev/null || true

        missing_ntfs_tools=()
        command -v ntfsfix  &> /dev/null || missing_ntfs_tools+=("ntfsfix")
        command -v ntfsinfo &> /dev/null || missing_ntfs_tools+=("ntfsinfo")

        if [ ${#missing_ntfs_tools[@]} -eq 0 ]; then
            echo -e "${GREEN}✓ 安装完成${NC}"
        else
            echo -e "${RED}✗ 自动安装失败，仍缺少: ${missing_ntfs_tools[*]}${NC}"
            echo "  可手动安装后重试："
            echo "    sudo steamos-readonly disable"
            echo "    sudo pacman -S ntfsprogs        (Arch/SteamOS)"
            echo "    sudo apt install ntfs-3g        (Debian/Ubuntu)"
            # 不必在这里手动恢复只读：EXIT trap 里的 restore_readonly 会按
            # RO_READONLY_DISABLED_BY_US 决定是否 enable
            return 1
        fi
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

    # FIX-LEAD: ntfs fix count
    local fix_fail=0
    case $fix_choice in
        1)
            for idx in "${dirty_indices[@]}"; do
                fix_single_ntfs "${ntfs_devices[$idx]}" "${ntfs_mountpoints[$idx]}" || ((fix_fail++))
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
                fix_single_ntfs "${ntfs_devices[$target_idx]}" "${ntfs_mountpoints[$target_idx]}" || ((fix_fail++))
            done
            # FIX-LEAD: ntfs selected count ZH
            ;;
        3|*)
            echo "操作取消。"
            ;;
    esac

    _restore_readonly_after_fix
    echo ""
    # FIX-LEAD: ntfs final ZH
    if [ "${fix_fail:-0}" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  修复流程结束，但有 ${fix_fail} 个分区修复失败，请查看上面的错误信息。${NC}"
        return 1
    fi
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

# ---------------------------------------------------------------------------
# 动态探测 ESP 分区，供「重建启动项」使用。
# 不能硬编码 /dev/nvme0n1p1：Steam Deck 有 eMMC(/dev/mmcblk0)、SATA(/dev/sda)
# 等机型，分区号也不一定为 1。
# ---------------------------------------------------------------------------
detect_esp() {
    local dev=""
    ESP_DEV=""; ESP_DISK=""; ESP_PARTN=""

    # 1) 已挂载的 /esp 或 /boot/efi
    for mp in /esp /boot/efi; do
        dev=$(findmnt -n -o SOURCE -M "$mp" 2>/dev/null | grep '^/dev/' | head -1 || true)
        [ -n "$dev" ] || dev=$(mount 2>/dev/null | awk -v m="$mp" '$3 == m {print $1; exit}')
        if [ -n "$dev" ] && [ -b "$dev" ]; then ESP_DEV="$dev"; break; fi
    done
    # 2) 按 EFI 分区类型 GUID 查找
    if [ -z "$ESP_DEV" ]; then
        dev=$(lsblk -P -n -o PATH,PARTTYPE 2>/dev/null \
            | awk -F'"' '/PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b"/{print $2; exit}' || true)
        [ -n "$dev" ] && [ -b "$dev" ] && ESP_DEV="$dev"
    fi
    [ -n "$ESP_DEV" ] || return 1
    ESP_DISK="/dev/$(lsblk -n -o PKNAME "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')"
    ESP_PARTN=$(lsblk -n -o PARTN "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')
    [ -n "$ESP_PARTN" ] || ESP_PARTN=1
    return 0
}

# 检查 ESP 上 Clover 引导文件是否存在（决定「重建启动项」是否有意义）
# 返回值：0 = 文件存在；1 = 确认不存在；2 = 无法判断（权限/挂载问题）
clover_files_ok() {
    local mnt=""
    if [ -n "${ESP_DEV:-}" ]; then
        if mountpoint -q /esp 2>/dev/null; then mnt=/esp
        elif mountpoint -q /boot/efi 2>/dev/null; then mnt=/boot/efi
        else
            mnt=$(mktemp -d 2>/dev/null) || return 2
            if ! mount -o ro "$ESP_DEV" "$mnt" 2>/dev/null; then
                rmdir "$mnt" 2>/dev/null; return 2
            fi
            TMP_ESP_MNT="$mnt"
        fi
    else
        return 2
    fi
    # EFI 目录可能在根下或在 efi 子目录下。
    # 注意：本脚本已通过 sudo 提权运行，但仍需区分「目录不存在」与「读不了」，
    # 否则会把权限问题误报成"Clover 文件缺失"，误导用户去重装 Clover。
    local efi_root=""
    for cand in "$mnt/EFI" "$mnt/efi/EFI"; do
        if [ -d "$cand" ] && ls "$cand" &>/dev/null; then efi_root="$cand"; break; fi
    done
    if [ -z "$efi_root" ]; then
        # 无法判断是"没有 EFI 目录"还是"读不了"
        if [ ! -r "$mnt" ]; then return 2; fi
        return 1
    fi
    for cand in "$efi_root/clover/cloverx64.efi"; do
        if [ -f "$cand" ]; then return 0; fi
    done
    return 1
}

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

# 找不到 Clover 启动项时，不再直接退出：SteamOS 更新或固件重置后启动项
# 常被清除，而 ESP 上的 Clover 文件往往还在，此时可以自动重建。
if [ -z "$CLOVER_ENTRY" ]; then
    echo "⚠️  未找到 Clover 启动项，尝试自动重建..."
    echo ""

    if ! detect_esp; then
        echo "❌ 无法识别 ESP 分区，无法重建启动项。"
        echo "   请确认系统为 SteamOS/Bazzite，且 ESP 分区正常挂载。"
        exit 1
    fi
    echo "   ESP 分区: $ESP_DEV （磁盘 $ESP_DISK，分区号 $ESP_PARTN）"

    clover_files_ok
    # FIX-LEAD: fix_boot files_rc ZH
    # 该段在生成的子脚本里运行于函数外：bash 的 `local` 会失败并覆盖 $?，
    # 导致 Clover 文件缺失 (返回 1) 被误当成 0 而继续注册无效启动项。
    files_rc=$?
    if [ "$files_rc" -eq 2 ]; then
        echo ""
        echo "⚠️  无法读取 ESP 内容来判断 Clover 文件是否存在（权限或挂载问题）。"
        echo "   已跳过文件检查，将直接尝试注册启动项。"
        echo "   若注册后仍无法启动，请重新安装 Clover（引导管理 → 安装/重装 Clover）。"
    elif [ "$files_rc" -eq 1 ]; then
        echo ""
        echo "❌ ESP 上未找到 Clover 引导文件（cloverx64.efi）。"
        echo "   可能原因："
        echo "   • Clover 尚未安装"
        echo "   • SteamOS 更新覆盖了 ESP 上的 Clover 文件"
        echo ""
        echo "   → 请使用「引导管理 → 安装/重装 Clover」重新安装。"
        [ -n "${TMP_ESP_MNT:-}" ] && { umount "$TMP_ESP_MNT" 2>/dev/null; rmdir "$TMP_ESP_MNT" 2>/dev/null; }
        exit 1
    fi

    # 清理可能残留的同名条目，避免重复
    for old_entry in $(efibootmgr | grep -i "clover" | grep -o 'Boot[0-9A-Fa-f]\{4\}' | sed 's/Boot//'); do
        efibootmgr -b "$old_entry" -B &>/dev/null || true
    done

    echo "   正在注册 Clover 启动项..."
    if efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
        -L "Clover - GUI Boot Manager" -l '\EFI\clover\cloverx64.efi'; then
        echo "   ✅ Clover 启动项已重建"
        CLOVER_ENTRY=$(efibootmgr -v | grep -i "CLOVER" | head -1)
    else
        echo "   ❌ 重建失败。请尝试「引导管理 → 安装/重装 Clover」。"
        [ -n "${TMP_ESP_MNT:-}" ] && { umount "$TMP_ESP_MNT" 2>/dev/null; rmdir "$TMP_ESP_MNT" 2>/dev/null; }
        exit 1
    fi

    # 顺带检查 SteamOS 启动项
    if ! efibootmgr | grep -qi "steamos\|steamcl"; then
        echo ""
        echo "⚠️  未找到 SteamOS 启动项，一并重建..."
        if efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
            -L "SteamOS" -l '\EFI\steamos\steamcl.efi'; then
            echo "   ✅ SteamOS 启动项已重建"
        else
            echo "   ⚠️  SteamOS 启动项重建失败，请手动检查 ESP 上的 steamcl.efi"
        fi
    fi

    [ -n "${TMP_ESP_MNT:-}" ] && { umount "$TMP_ESP_MNT" 2>/dev/null; rmdir "$TMP_ESP_MNT" 2>/dev/null; }

    if [ -z "$CLOVER_ENTRY" ]; then
        echo ""
        echo "❌ 重建后仍找不到 Clover 启动项。"
        echo "   当前所有启动项："
        efibootmgr | grep "Boot[0-9A-F][0-9A-F][0-9A-F][0-9A-F]"
        exit 1
    fi
    echo ""
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

# 生成 NTFS 挂载/fstab 选项。
# 原来的实现把 uid=1000,gid=1000 写死，用户名不是 deck、或 UID 不是 1000 的设备
# 挂载后会变成「挂上了但普通用户读写不了」，这里统一改成取当前实际用户。
ntfs_mount_opts() {
    local u g
    u="$(id -u 2>/dev/null)"; g="$(id -g 2>/dev/null)"
    [ -z "$u" ] && u=1000
    [ -z "$g" ] && g=1000
    printf 'rw,exec,uid=%s,gid=%s,windows_names,nofail' "$u" "$g"
}

# 判断某个挂载点当前是否只读。
# ntfs-3g(FUSE) 遇到脏卷/休眠卷时不会报错，而是静默降级成 ro 挂载，
# 只看 mount 命令返回值和 systemd 日志会误以为读写挂载成功，因此必须回查实际选项。
ntfs_mountpoint_is_ro() {
    local mp="$1" opts
    [ -z "$mp" ] && return 1
    opts="$(findmnt -n -o OPTIONS -M "$mp" 2>/dev/null | head -1)"
    [ -z "$opts" ] && return 1
    case ",$opts," in
        *,ro,*) return 0 ;;
    esac
    return 1
}

# dmesg 行数基线：用于只提取「本次操作新产生」的内核日志。
# 原来直接 dmesg | grep -i ntfs | tail -5，会把陈年旧日志当成这次的错误，把人带偏。
dmesg_line_count() {
    sudo dmesg 2>/dev/null | wc -l
}

dmesg_since() {
    local mark="${1:-0}"
    case "$mark" in ''|*[!0-9]*) mark=0 ;; esac
    # 基线为 0 说明基线没取到（不是「dmesg 是空的」），此时宁可什么都不输出，
    # 也不要把整份 dmesg 当成「本次操作」的日志拿去做诊断。
    [ "$mark" -gt 0 ] || return 0
    sudo dmesg 2>/dev/null | tail -n "+$(( mark + 1 ))"
}

# 挂载失败时，根据本次新增的内核日志给出可操作的处理步骤
ntfs_explain_failure() {
    local dev="$1" mp="$2" log="$3"
    local hit=0
    if echo "$log" | grep -qiE 'volume is dirty|"force" flag is not set'; then
        hit=1
        echo -e "${YELLOW}    诊断：卷上带有 NTFS 脏标志(dirty)，内核 ntfs3 驱动据此拒绝挂载。${NC}"
    elif echo "$log" | grep -qiE 'hibernat'; then
        hit=1
        echo -e "${YELLOW}    诊断：Windows 处于休眠/快速启动状态，卷被标记为不可安全写入。${NC}"
    elif echo "$log" | grep -qiE 'unclean|not clean|chkdsk'; then
        hit=1
        echo -e "${YELLOW}    诊断：文件系统处于未干净卸载状态，需要先修复再挂载。${NC}"
    fi
    if [ $hit -eq 1 ]; then
        echo -e "${CYAN}    按顺序尝试：${NC}"
        echo "      a) 进 Windows 关闭「快速启动」后选择「关机」，再回到 SteamOS 重试（最干净）"
        echo "      b) 在本机清除标志："
        echo "           sudo steamos-readonly disable"
        echo "           sudo pacman -S ntfsprogs"
        echo "           sudo umount $dev 2>/dev/null; sudo ntfsfix -d $dev"
        echo "         然后重新运行本功能"
        echo "      c) 应急只读挂载先取数据：sudo mount -o ro $dev $mp"
        echo "      d) 应急读写（不清标志，有损坏元数据风险）："
        echo "           sudo mount -t ntfs3 -o force,uid=$(id -u),gid=$(id -g) $dev $mp"
    else
        echo -e "${CYAN}    常见原因：${NC}"
        echo "      a) 卷有 dirty/休眠标志 → 进 Windows 关闭快速启动并完整关机，"
        echo "         或安装 ntfsprogs 后用 sudo ntfsfix -d $dev 清理"
        echo "      b) 该分区是 Windows 恢复分区 → 本功能已自动跳过，不需要挂载"
        echo "      c) 设备被占用 → 先 sudo umount $dev 再重试"
        echo "      d) fstab 或挂载点异常 → 检查 /etc/fstab 与 $mp 的属主权限"
    fi
}

# 挂载前预检：ntfs-3g.probe 随 ntfs-3g 包一起提供，不需要 ntfsprogs。
# 它能提前判断「这个卷能不能以读写方式挂载」，从而在真正 mount 之前就给出
# 明确提示，而不是等挂载后才发现是只读。
# 返回 0=可读写挂载；1=只能只读/需要修复；2=无法判断（工具缺失或设备忙）
ntfs_probe_writable() {
    local dev="$1" probe out rc
    for probe in /usr/bin/ntfs-3g.probe /bin/ntfs-3g.probe /usr/sbin/ntfs-3g.probe; do
        [ -x "$probe" ] || continue
        out="$(sudo "$probe" --readwrite "$dev" 2>&1)"
        rc=$?
        if [ $rc -eq 0 ]; then
            return 0
        fi
        # 只有真正匹配到脏卷/休眠/未干净卸载的症状才算「不能读写挂载」，
        # 其余失败（权限、设备忙、工具行为变化等）一律按「无法判断」处理，
        # 避免给出错误的预检警告。
        if echo "$out" | grep -qiE 'dirty|hibernat|unclean|not clean|chkdsk|refus'; then
            return 1
        fi
        return 2
    done
    return 2
}

# 挂载成功但被降级为只读时的说明
ntfs_explain_readonly() {
    local dev="$1" mp="$2"
    echo -e "${YELLOW}    原因：该卷带有 NTFS 脏标志(dirty) 或处于休眠状态，Linux 的 NTFS 驱动只肯以只读方式挂载。${NC}"
    echo "    最常见来源：Windows 的「快速启动」或「休眠」导致系统没有真正关机。"
    echo ""
    echo -e "${CYAN}    彻底解决（推荐）：${NC}"
    echo "      1) 进入 Windows → 设置 → 系统 → 电源 → 选择电源按钮的功能"
    echo "         → 更改当前不可用的设置 → 取消勾选「启用快速启动」→ 保存修改"
    echo "      2) 在 Windows 里选择「关机」（不要用「重启」，重启不会清除脏标志）"
    echo "      3) 回到 SteamOS 重新运行本功能"
    echo ""
    echo -e "${CYAN}    不想进 Windows 时，可在 SteamOS 里清除脏标志：${NC}"
    echo "      sudo steamos-readonly disable"
    echo "      sudo pacman -S ntfsprogs          # 注意：ntfsfix 不在 ntfs-3g 包里"
    echo "      sudo umount $dev 2>/dev/null; sudo ntfsfix -d $dev"
    echo "      sudo mount $mp"
    echo ""
    echo -e "${CYAN}    仅应急（不清标志，强行读写，有损坏元数据的风险）：${NC}"
    echo "      sudo umount $dev 2>/dev/null"
    echo "      sudo mount -t ntfs3 -o force,uid=$(id -u),gid=$(id -g) $dev $mp"
}

fix_shared_disk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 自动挂载 Windows 分区 ════════════════${NC}"
    echo ""

    # 挂载分区、写入 /etc/fstab 都要 root；先一次性拿到 sudo 授权，
    # 后面的步骤就不会各自弹一次密码提示。
    echo -e "${CYAN}此操作需要 root 权限（挂载分区、写入 /etc/fstab）。${NC}"
    echo -e "${CYAN}请输入您的 sudo 密码以继续操作（输入时不会显示）${NC}"
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}密码验证失败或已取消，操作终止。${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ 密码验证通过，继续。${NC}"
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

    echo "步骤2: 检查 NTFS 工具（ntfs-3g / ntfsfix）"
    # 缺什么装什么。ntfs-3g 是挂载 NTFS 的必需品，缺了后面根本挂不上，属致命；
    # ntfsfix 只在「卷脏需要清标志」时用得上，缺了只警告不中断。
    local missing_core=()
    local missing_opt=()
    if ! command -v mount.ntfs-3g &>/dev/null && ! command -v ntfs-3g &>/dev/null; then
        missing_core+=("ntfs-3g")
    fi
    command -v ntfs-3g.probe &>/dev/null || missing_core+=("ntfs-3g.probe")
    command -v ntfsfix &>/dev/null || missing_opt+=("ntfsfix")

    if [ ${#missing_core[@]} -eq 0 ] && [ ${#missing_opt[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ NTFS 工具已就绪${NC}"
    else
        # 拼接缺失清单时避免出现多余空格（可能只有缺 ntfsfix 一种情况）
        local need_list=""
        if [ ${#missing_core[@]} -gt 0 ]; then need_list="${missing_core[*]}"; fi
        if [ ${#missing_opt[@]} -gt 0 ]; then need_list="${need_list:+$need_list }${missing_opt[*]}"; fi
        echo -e "${YELLOW}  缺少: ${need_list}，正在自动安装...${NC}"
        # Arch/SteamOS：ntfs-3g 与 ntfs-3g.probe 在 ntfs-3g 包里，
        #                 ntfsfix 在 ntfsprogs 包里（两者的工具不是同一个包）
        # Debian/Ubuntu：以上全部在 ntfs-3g 包里
        if command -v pacman &>/dev/null; then
            sudo pacman -S --needed --noconfirm ntfs-3g ntfsprogs >/dev/null 2>&1
        elif command -v apt-get &>/dev/null; then
            sudo apt-get install -y ntfs-3g >/dev/null 2>&1
        fi
        # 清掉 bash 的命令查找缓存：刚装上的二进制若不刷新，可能仍被判为找不到
        hash -r 2>/dev/null || true

        missing_core=()
        missing_opt=()
        if ! command -v mount.ntfs-3g &>/dev/null && ! command -v ntfs-3g &>/dev/null; then
            missing_core+=("ntfs-3g")
        fi
        command -v ntfs-3g.probe &>/dev/null || missing_core+=("ntfs-3g.probe")
        command -v ntfsfix &>/dev/null || missing_opt+=("ntfsfix")

        if [ ${#missing_core[@]} -eq 0 ]; then
            echo -e "${GREEN}✓ 安装完成${NC}"
        else
            echo -e "${RED}✗ 自动安装失败，仍缺少: ${missing_core[*]}${NC}"
            echo "  NTFS 驱动缺失时无法挂载 Windows 分区，请手动安装后重试："
            echo "    sudo steamos-readonly disable"
            echo "    sudo pacman -S ntfs-3g          (Arch/SteamOS)"
            echo "    sudo apt install ntfs-3g        (Debian/Ubuntu)"
            return 1
        fi
        if [ ${#missing_opt[@]} -gt 0 ]; then
            echo -e "${YELLOW}  ⚠️  仍未安装 ${missing_opt[*]}：不影响本次挂载，"
            echo -e "      但若卷是脏卷、需要用它清脏标志，请先执行 sudo pacman -S ntfsprogs${NC}"
        fi
    fi
    echo ""

    echo "步骤3: 修改 UDisks2 权限文件"
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

    echo "步骤4: 扫描 Windows (NTFS) 分区（忽略恢复分区）..."
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
    # 已挂载但被降级为只读的分区（脏卷/休眠卷时 ntfs-3g 会静默挂成 ro）
    local ro_mounts=()

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
                # 挂载了、fstab 也有，但还要确认不是「被降级成只读」的假成功：
                # 脏卷时 ntfs-3g 会以 ro 挂上且不报错，这种情况绝不能宣称「全部就绪」。
                if ntfs_mountpoint_is_ro "$mountpoint"; then
                    all_ready=false
                    ro_mounts+=("$mountpoint")
                fi
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

    echo "步骤5: 清理 /run/media/deck/ 下非 Windows 分区的挂载和 fstab 条目..."
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

    # 分区虽然挂上了，但被降级成只读：这种情况必须继续往下走，尝试重新以读写挂载，
    # 不能像以前那样直接宣称「全部就绪」把用户打发走。
    if [ ${#ro_mounts[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  检测到 ${#ro_mounts[@]} 个分区当前是「只读」挂载：${NC}"
        local _ro_mp
        for _ro_mp in "${ro_mounts[@]}"; do
            echo "    $_ro_mp"
        done
        echo "  只读挂载说明卷上带有 NTFS 脏标志或处于休眠状态，即使 fstab 正确也写不进文件。"
        echo "  下面会先尝试重新以读写方式挂载；若仍为只读，会给出具体处理步骤。"
        echo ""
    fi

    echo "步骤6: 开始挂载并写入 fstab..."
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
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g $(ntfs_mount_opts) 0 0"
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
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g $(ntfs_mount_opts) 0 0"
                } > "$_tmp2" 2>/dev/null && chmod 644 "$_tmp2" 2>/dev/null \
                    && sudo cp "$_tmp2" /etc/fstab && rm -f "$_tmp2" \
                    && echo "  已添加 fstab 条目。" \
                    || { rm -f "$_tmp2"; echo -e "${RED}  ✗ 写入 fstab 失败${NC}"; ((fail_count++)); }
            fi
        fi

        if mountpoint -q "$mount_point" 2>/dev/null; then
            if ntfs_mountpoint_is_ro "$mount_point"; then
                # ntfs-3g 是 FUSE 挂载，只读/读写是在挂载那一刻定下的，
                # `mount -o remount,rw` 对 FUSE 无效。要真正有机会转成读写，
                # 只能先卸载再按 fstab 重新挂载，这里就这么做。
                echo -e "${YELLOW}  分区已挂载到 $mount_point，但当前是只读模式，正在重新挂载...${NC}"
                if sudo umount "$device" 2>/dev/null; then
                    if sudo mount "$mount_point" 2>/dev/null; then :; else
                        [ -n "$uuid" ] && sudo mount -U "$uuid" "$mount_point" 2>/dev/null
                    fi
                else
                    echo "  （分区正被占用，无法卸载，跳过重新挂载）"
                fi
                if ! mountpoint -q "$mount_point" 2>/dev/null; then
                    # 卸载成功但重新挂载失败：此时分区根本没挂上，
                    # 绝不能因为「不是只读」就报成功（那正是本功能要消灭的假成功）。
                    echo -e "${RED}  ✗ 重新挂载失败，分区当前未挂载。${NC}"
                    # 原来至少还是只读可访问，别让用户比修复前更糟：
                    # 退回只读挂载，先保证能读到数据。
                    if sudo mount -o ro "$device" "$mount_point" 2>/dev/null; then
                        echo -e "${YELLOW}    已回退为只读挂载，至少可以读取其中的文件。${NC}"
                    else
                        echo "    回退只读挂载也失败了，请重新运行本功能或手动挂载。"
                    fi
                    ((fail_count++))
                elif ntfs_mountpoint_is_ro "$mount_point"; then
                    echo -e "${YELLOW}  ✗ 仍为只读挂载，无法写入文件。${NC}"
                    ntfs_explain_readonly "$device" "$mount_point"
                    ((fail_count++))
                else
                    echo -e "${GREEN}  ✓ 已切换为读写挂载：$mount_point${NC}"
                fi
            else
                echo "  分区已挂载到 $mount_point"
            fi
        else
            # 记录 dmesg 基线，只取本次挂载新产生的内核日志，
            # 避免把开机以来累积的旧 NTFS 报错当成本次错误。
            local _dmark _mlog
            _dmark="$(dmesg_line_count)"
            # 挂载前预检：能提前发现「挂上也只会是只读」的情况，先把原因讲清楚
            local _prc=0
            ntfs_probe_writable "$device" || _prc=$?
            if [ "$_prc" -eq 1 ]; then
                echo -e "${YELLOW}  预检提示：该卷当前不允许读写挂载（脏标志/休眠/未干净卸载）。${NC}"
            fi
            if sudo systemctl daemon-reload 2>/dev/null; then :; fi
            if sudo mount "$mount_point" 2>/dev/null || sudo mount -U "$uuid" "$mount_point" 2>/dev/null; then
                if ntfs_mountpoint_is_ro "$mount_point"; then
                    echo -e "${YELLOW}  ⚠️  已挂载到 $mount_point，但被系统降级为「只读」${NC}"
                    ntfs_explain_readonly "$device" "$mount_point"
                    ((fail_count++))
                else
                    echo -e "${GREEN}  ✓ 挂载成功到 $mount_point（读写）${NC}"
                fi
            else
                _mlog="$(dmesg_since "$_dmark")"
                echo -e "${RED}  ✗ 挂载失败。${NC}"
                if [ -n "$_mlog" ]; then
                    echo "  本次操作期间的 dmesg 输出："
                    echo "$_mlog" | grep -iE 'ntfs|fuseblk' | tail -8 | sed 's/^/    /'
                fi
                ntfs_explain_failure "$device" "$mount_point" "$_mlog"
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

install_uu_accelerator() {
    # FIX-SOFTWARE: 不再把网络内容直接管道给 root。
    # https + 超时 + 下载到临时文件 + 校验是 shell 文本 + 校验通过后直接 sudo 执行（由 sudo 提示密码）。
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装UU加速器插件 ════════════════${NC}"
    local url="https://uudeck.com"
    local tmp="$(mktemp "$TEMP_DIR/uudeck.com.XXXXXX.sh" 2>/dev/null)"
    if [ -z "$tmp" ]; then
        echo -e "${RED}✗ 无法创建临时文件，操作中止。${NC}"
        return 1
    fi
    echo -e "${CYAN}正在下载并校验安装脚本（来源: $url）...${NC}"
    if ! fs_fetch_shell "$url" "$tmp"; then
        echo -e "${RED}✗ 下载失败，或返回内容不是有效的 shell 脚本（可能拿到了 HTML 错误页），已中止。${NC}"
        rm -f "$tmp"
        return 1
    fi
    echo -e "${GREEN}✓ 已下载并通过基本校验，即将以 root 执行（下一步需要输入密码）。${NC}"
    echo -e "${CYAN}正在以 sudo 执行已下载的脚本...${NC}"
    if sudo sh "$tmp"; then
        echo -e "${GREEN}✓ 安装UU加速器插件完成。${NC}"
        rm -f "$tmp"
        return 0
    fi
    echo -e "${RED}✗ 安装脚本返回错误码，请检查上方输出。${NC}"
    rm -f "$tmp"
    return 1
}

install_xunyou_accelerator() {
    # FIX-SOFTWARE: 不再把网络内容直接管道给 root。
    # https + 超时 + 下载到临时文件 + 校验是 shell 文本 + 校验通过后直接 sudo 执行（由 sudo 提示密码）。
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装迅游加速器插件 ════════════════${NC}"
    local url="https://sd.xunyou.com"
    local tmp="$(mktemp "$TEMP_DIR/sd.xunyou.com.XXXXXX.sh" 2>/dev/null)"
    if [ -z "$tmp" ]; then
        echo -e "${RED}✗ 无法创建临时文件，操作中止。${NC}"
        return 1
    fi
    echo -e "${CYAN}正在下载并校验安装脚本（来源: $url）...${NC}"
    if ! fs_fetch_shell "$url" "$tmp"; then
        echo -e "${RED}✗ 下载失败，或返回内容不是有效的 shell 脚本（可能拿到了 HTML 错误页），已中止。${NC}"
        rm -f "$tmp"
        return 1
    fi
    echo -e "${GREEN}✓ 已下载并通过基本校验，即将以 root 执行（下一步需要输入密码）。${NC}"
    echo -e "${CYAN}正在以 sudo 执行已下载的脚本...${NC}"
    if sudo sh "$tmp"; then
        echo -e "${GREEN}✓ 安装迅游加速器插件完成。${NC}"
        rm -f "$tmp"
        return 0
    fi
    echo -e "${RED}✗ 安装脚本返回错误码，请检查上方输出。${NC}"
    rm -f "$tmp"
    return 1
}

install_qiyou_accelerator() {
    # FIX-SOFTWARE: 不再把网络内容直接管道给 root。
    # https + 超时 + 下载到临时文件 + 校验是 shell 文本 + 校验通过后直接 sudo 执行（由 sudo 提示密码）。
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装奇游联机宝加速插件 ════════════════${NC}"
    # FIX-QIYOU: sd.qiyou.cn 只提供 HTTP（443 未开放），一级引导脚本本身也用
    # 明文 http 去 static.qiyou.cn 拉真正的安装脚本。static.qiyou.cn 支持 HTTPS，
    # 因此直接取真实脚本，既避开连不上的 443，也不再经过明文引导层。
    local url="https://static.qiyou.cn/upgrade/ljb/plugin/qyplug.sh"
    local tmp="$(mktemp "$TEMP_DIR/qyplug.XXXXXX.sh" 2>/dev/null)"
    if [ -z "$tmp" ]; then
        echo -e "${RED}✗ 无法创建临时文件，操作中止。${NC}"
        return 1
    fi
    echo -e "${CYAN}正在下载并校验安装脚本（来源: $url）...${NC}"
    if ! fs_fetch_shell "$url" "$tmp"; then
        echo -e "${RED}✗ 下载失败，或返回内容不是有效的 shell 脚本（可能拿到了 HTML 错误页），已中止。${NC}"
        rm -f "$tmp"
        return 1
    fi
    echo -e "${GREEN}✓ 已下载并通过基本校验，即将以 root 执行（下一步需要输入密码）。${NC}"
    echo -e "${CYAN}正在以 sudo 执行已下载的脚本...${NC}"
    if sudo sh "$tmp"; then
        echo -e "${GREEN}✓ 安装奇游联机宝加速插件完成。${NC}"
        rm -f "$tmp"
        return 0
    fi
    echo -e "${RED}✗ 安装脚本返回错误码，请检查上方输出。${NC}"
    rm -f "$tmp"
    return 1
}

install_asklink() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ AskLink 远程 ════════════════${NC}"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        # FIX-SOFTWARE: 二次确认 + 检查返回值 + 用户数据目录单独确认。
        echo -e "${GREEN}AskLink 已安装。${NC}"
        echo -e "${YELLOW}将删除 /opt/AskLink 及桌面/系统快捷方式。${NC}"
        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        echo -e "${RED}警告：卸载会移除程序文件；配置目录可能含用户数据。${NC}"
        if ! confirm_action; then
            echo -e "${GREEN}已取消，保持 AskLink 安装。${NC}"
            return 0
        fi
        local fail=0
        # 结束可能占用二进制的进程（检查返回值但不因「没找到进程」而失败）
        if pgrep -f '/opt/AskLink' >/dev/null 2>&1; then
            sudo pkill -f '/opt/AskLink' 2>/dev/null || echo -e "${YELLOW}⚠ 结束进程失败，请手动关闭后重试${NC}"
        fi
        if ! sudo rm -rf /opt/AskLink; then
            echo -e "${RED}✗ 删除 /opt/AskLink 失败${NC}"; fail=1
        fi
        local f
        for f in "$DESKTOP_DIR/AskLink.desktop" "$HOME/Desktop/AskLink.desktop"                  "$HOME/.local/share/applications/AskLink.desktop"; do
            if [ -e "$f" ] && ! rm -f "$f"; then
                echo -e "${RED}✗ 删除 $f 失败${NC}"; fail=1
            fi
        done
        if [ -e /usr/share/applications/AskLink.desktop ] && ! sudo rm -f /usr/share/applications/AskLink.desktop; then
            echo -e "${RED}✗ 删除系统快捷方式失败${NC}"; fail=1
        fi
        # 用户数据目录：单独确认
        if [ -d "$HOME/Documents/AskLink" ]; then
            echo ""
            echo -e "${CYAN}是否删除配置与用户数据目录 $HOME/Documents/AskLink？${NC}"
            echo -e "${YELLOW}该目录可能含登录信息/配置，删除后无法恢复。${NC}"
            if confirm_action; then
                if ! rm -rf "$HOME/Documents/AskLink"; then
                    echo -e "${RED}✗ 删除配置目录失败${NC}"; fail=1
                else
                    echo -e "${GREEN}✓ 已删除配置目录${NC}"
                fi
            else
                echo -e "${YELLOW}已保留配置目录。${NC}"
            fi
        fi
        echo ""
        if [ "$fail" -ne 0 ]; then
            echo -e "${RED}✗ 卸载过程中有失败项，请按上方提示手动处理。${NC}"
            return 1
        fi
        echo -e "${GREEN}✅ AskLink 已卸载。${NC}"
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
            # SteamOS/Holo 上常残留 /var/lib/dpkg/{available,status}
            #（曾手动 dpkg -i 留下，且不属于任何 pacman 包）。
            # 直接 pacman -S dpkg 会报「文件系统中已存在」冲突。
            if ! sudo pacman -S --needed --noconfirm dpkg; then
                echo -e "${YELLOW}常规安装遇到文件冲突，尝试覆盖 /var/lib/dpkg 残留文件...${NC}"
                if ! sudo pacman -S --needed --noconfirm --overwrite '/var/lib/dpkg/*' dpkg; then
                    echo -e "${RED}安装 dpkg 失败，请手动执行:${NC}"
                    echo -e "${RED}  sudo pacman -S --overwrite '/var/lib/dpkg/*' dpkg${NC}"
                    return 1
                fi
            fi
            if ! command -v dpkg &>/dev/null; then
                echo -e "${RED}dpkg 安装后仍不可用，请手动检查。${NC}"
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
    # FIX-SOFTWARE: 关键下载加 --fail/超时；dpkg 不再 2>/dev/null 吞错误。
    if command -v wget &>/dev/null; then
        wget --show-progress --connect-timeout=15 --timeout=120 --tries=1 "$ASKLINK_URL" -O "$FILENAME"
    else
        curl -L --fail --connect-timeout 15 --max-time 120 --progress-bar "$ASKLINK_URL" -o "$FILENAME"
    fi
    if [ $? -ne 0 ] || [ ! -s "$FILENAME" ]; then
        echo -e "${RED}下载失败或文件为空。${NC}"
        rm -f "$FILENAME"
        return 1
    fi

    echo -e "${CYAN}正在安装（dpkg 输出不再被抑制，失败将如实显示）...${NC}"
    if ! sudo dpkg --force-depends -i "$FILENAME"; then
        echo -e "${RED}✗ dpkg 安装失败，请查看上方真实错误。${NC}"
        echo -e "${YELLOW}  常见原因：缺依赖。可尝试 sudo pacman -S 相应依赖后重试。${NC}"
        rm -f "$FILENAME"
        return 1
    fi
    rm -f "$FILENAME"

    # 安装后验证可执行文件/服务，而不是只看目录存在
    if [ ! -x /opt/AskLink/AskLink ] && ! command -v asklink &>/dev/null; then
        echo -e "${RED}✗ dpkg 返回成功但未找到可执行的 AskLink，安装视为失败。${NC}"
        return 1
    fi
    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}✅ AskLink 安装成功！${NC}"
        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        local DESKTOP_FILE="$DESKTOP_DIR/AskLink.desktop"
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
    local trust_now=""

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
        # FIX-WATT: .version 可能是 "v3.1.0" 而下载常量是 "3.1.0"，
        # 比较前去掉开头的 v，否则同版本也会误报「检测到新版本」。
        local installed_cmp="${installed_version#v}"
        if [ -n "$installed_version" ] && [ "$installed_cmp" = "$VERSION" ]; then
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

    # FIX-SOFTWARE: 下载到 mktemp 临时目录 + curl --fail/超时；先校验关键文件
    # 再替换旧目录；mv/mkdir 失败立即中止；.version 只在全部成功后写。
    echo -e "${GREEN}将安装版本: ${VERSION}${NC}"
    echo "正在下载 ${DOWNLOAD_URL} ..."

    local temp_dir
    temp_dir="$(mktemp -d /tmp/watt_toolkit_install.XXXXXXXX 2>/dev/null)" || {
        echo -e "${RED}✗ 无法创建临时目录，已中止（旧安装未动）。${NC}"; return 1; }
    # FIX-WATT: 绝不 cd 进临时目录。安装末尾会 rm -rf 该目录，若当前工作目录
    # 还在里面，后续每条 sudo 都会 getcwd 失败并刷上百行
    # "job-working-directory: getcwd: 无法访问父目录"。全部改用绝对路径。
    local filename="$temp_dir/Steam_v${VERSION}_linux_x64.tgz"
    if ! curl -L --fail --connect-timeout 15 --max-time 300 --progress-bar -o "$filename" "$DOWNLOAD_URL"; then
        echo -e "${RED}下载失败，请检查网络后重试。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if [ ! -s "$filename" ]; then
        echo -e "${RED}下载文件为空，已中止。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi

    echo -e "${CYAN}正在解压...${NC}"
    local temp_extract="$temp_dir/extracted"
    if ! mkdir -p "$temp_extract"; then
        echo -e "${RED}✗ 创建解压目录失败，已中止。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if ! tar -xzf "$filename" -C "$temp_extract"; then
        echo -e "${RED}解压失败。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi

    local content_count=$(ls -1 "$temp_extract" | wc -l)
    local first_item=$(ls -1 "$temp_extract" | head -1)
    local src_root="$temp_extract"
    if [ "$content_count" -eq 1 ] && [ -d "$temp_extract/$first_item" ]; then
        src_root="$temp_extract/$first_item"
    fi

    # 先在暂存区校验关键文件（DLL 存在、dotnet 可执行），验证通过才动旧目录。
    local stage_dotnet="$src_root/dotnet/dotnet"
    local stage_dll="$src_root/assemblies/Steam++.dll"
    if [ ! -f "$stage_dll" ] || [ ! -x "$stage_dotnet" ]; then
        echo -e "${RED}错误: 解压内容缺少关键文件或 dotnet 不可执行，安装中止（旧安装未动）。${NC}"
        echo "  期望: $stage_dll 存在、$stage_dotnet 可执行(-x)"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    echo -e "${GREEN}✓ 关键文件校验通过（DLL + dotnet 可执行）${NC}"

    # FIX-WATT: 备份目标必须与安装目录位于同一文件系统（/tmp 与 /home 常是不同设备），
    # 且压缩包里的 dotnet 带 security.capability xattr —— mv/cp -a 在跨设备或
    # 不允许设置 capability 时会报 "setting attribute 'security.capability'"。
    # 因此：备份放到 $HOME 下，用 cp -a 复制而非 mv；新文件先装到同文件系统的
    # 暂存目录，用 cp -r --no-preserve=xattr 避免把 capability 带过去。
    local backup_dir="$HOME/.watt_toolkit_backup.$$"
    local had_backup=0
    if [ -d "$INSTALL_DIR" ]; then
        echo "检测到旧安装目录，先备份再替换..."
        if ! cp -a "$INSTALL_DIR" "$backup_dir" 2>/dev/null; then
            echo -e "${RED}✗ 备份旧目录失败，已中止（旧安装未动）。${NC}"
            rm -rf "$backup_dir" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
        had_backup=1
    fi
    local stage_install="$HOME/.watt_toolkit_new.$$"
    rm -rf "$stage_install" 2>/dev/null
    if ! mkdir -p "$stage_install"; then
        echo -e "${RED}✗ 创建暂存安装目录失败，已中止（旧安装未动）。${NC}"
        [ "$had_backup" -eq 1 ] && rm -rf "$backup_dir" 2>/dev/null
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if cp -r --no-preserve=xattr "$src_root"/. "$stage_install"/ 2>/dev/null || cp -r "$src_root"/. "$stage_install"/; then
        :
    else
        echo -e "${RED}✗ 复制安装文件失败，已中止（旧安装未动）。${NC}"
        rm -rf "$stage_install" "$backup_dir" 2>/dev/null
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if [ ! -f "$stage_install/assemblies/Steam++.dll" ] || [ ! -x "$stage_install/dotnet/dotnet" ]; then
        echo -e "${RED}✗ 暂存内容缺少关键文件或 dotnet 不可执行，已中止（旧安装未动）。${NC}"
        rm -rf "$stage_install" "$backup_dir" 2>/dev/null
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if [ -d "$INSTALL_DIR" ]; then
        if ! mv "$INSTALL_DIR" "$INSTALL_DIR.old.$$" 2>/dev/null; then
            echo -e "${RED}✗ 移走旧安装目录失败，已中止（旧安装未动）。${NC}"
            rm -rf "$stage_install" "$backup_dir" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
        if ! mv "$stage_install" "$INSTALL_DIR" 2>/dev/null; then
            echo -e "${RED}✗ 移入新版本失败，正在恢复旧版本...${NC}"
            mv "$INSTALL_DIR.old.$$" "$INSTALL_DIR" 2>/dev/null
            rm -rf "$stage_install" "$backup_dir" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
        rm -rf "$INSTALL_DIR.old.$$" 2>/dev/null
    else
        if ! mv "$stage_install" "$INSTALL_DIR" 2>/dev/null; then
            echo -e "${RED}✗ 移入新版本失败，已中止。${NC}"
            rm -rf "$stage_install" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
    fi
    rm -rf "$backup_dir" 2>/dev/null
    rm -rf "$temp_dir"

    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local desktop_file="$DESKTOP_DIR/Watt_Toolkit.desktop"
    local dotnet_root="$INSTALL_DIR/dotnet"
    local dll_path="$INSTALL_DIR/assemblies/Steam++.dll"
    local icon_path="$INSTALL_DIR/Icons/Watt-Toolkit.png"

    # 二次复核：dotnet 必须可执行(-x)，而非仅存在(-f)
    if [ ! -f "$dll_path" ] || [ ! -x "$dotnet_root/dotnet" ]; then
        echo -e "${RED}错误: 安装后关键文件缺失或 dotnet 不可执行，安装视为失败。${NC}"
        echo "请检查 $INSTALL_DIR 目录内容。"
        return 1
    fi
    # 启动脚本兼容：Steam++.sh 或直接用 dotnet 跑 DLL
    if [ ! -x "$INSTALL_DIR/Steam++.sh" ] && [ ! -x "$dotnet_root/dotnet" ]; then
        echo -e "${YELLOW}⚠ 未找到 Steam++.sh 且 dotnet 不可用，桌面快捷方式可能无法启动。${NC}"
    fi
    # 全部成功后才写 .version
    if ! echo "$VERSION" > "$INSTALL_DIR/.version"; then
        echo -e "${RED}✗ 写入 .version 失败。${NC}"
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
    echo "  · 请在桌面启动 Watt Toolkit。"
    echo "  · 首次加速前需要让加速插件生成证书：在「网络加速」里点一次「加速」即可。"
    echo "  · 证书生成后运行本工具的「信任证书」，加速才不会报证书错误。"
    echo ""

    # ---------- 安装后直接进入证书信任 ----------
    echo -e "${YELLOW}加速功能还需要信任证书，否则 https 加速会报证书错误。${NC}"
    read -n1 -p "现在信任加速证书吗？[回车/A=是，其他键=稍后] " trust_now < /dev/tty
    echo
    if [[ -z "$trust_now" || "$trust_now" =~ [Aa] ]]; then
        watt_toolkit_trust_cert skip_clear
    else
        echo -e "${CYAN}已跳过。之后可在「网络工具 → Watt Toolkit (Steam++) → 信任证书」里执行。${NC}"
    fi
}

watt_toolkit_trust_cert() {
    # FIX-SOFTWARE: 不再 chmod a+w /etc/hosts（所有本地用户可写）。
    # 证书先校验 CA:TRUE 与指纹，写入记录文件供卸载精确匹配。
    [ "${1:-}" = "skip_clear" ] || clear
    echo -e "${YELLOW}═══════ 信任 Watt Toolkit (Steam++) 加速证书 ═══════${NC}"
    echo ""
    echo "加速功能需要两项系统级改动："
    echo "  1. 把 Watt Toolkit 自签的根证书加入系统信任库（否则 https 加速报证书错误）"
    echo "  2. 让当前用户能写 /etc/hosts（用 sudo 临时提权，不永久放开权限）"
    echo ""
    echo -e "${YELLOW}安全提示：${NC}"
    echo "  该证书是 Watt Toolkit 在本机自己生成的根证书（CN=SteamTools Certificate），"
    echo "  信任它意味着持有对应私钥的进程可以解密本机的 https 流量。"
    echo "  不再使用 Watt Toolkit 时，建议运行卸载功能移除该信任。"
    echo ""

    local CERT_DIR="$HOME/.local/share/Steam++/Plugins/Accelerator"
    local CERT_FILE="$CERT_DIR/SteamTools.Certificate.cer"
    local RECORD_FILE="$HOME/.local/share/Steam++/watt_toolkit_trust.record"
    local INSTALL_DIR="$HOME/Watt Toolkit"
    local launch_now="" retry="" confirm=""
    local CERT_FP=""

    if ! command -v trust >/dev/null 2>&1; then
        echo -e "${RED}✗ 未找到 trust 命令（由 p11-kit 提供），无法写入系统信任库。${NC}"
        echo -e "${YELLOW}  可尝试：sudo pacman -S p11-kit${NC}"
        return 1
    fi

    # ---------- 证书存在性 ----------
    if [ ! -f "$CERT_FILE" ]; then
        echo -e "${YELLOW}未找到加速证书：${NC}"
        echo "  $CERT_FILE"
        echo ""
        echo "这个证书由 Watt Toolkit 首次运行时生成，安装包里并没有。"
        echo "请先启动 Watt Toolkit，在「网络加速」里点一次「加速」，证书才会出现。"
        echo ""
        local start_cmd=""
        if [ -x "$INSTALL_DIR/Steam++.sh" ]; then
            start_cmd="$INSTALL_DIR/Steam++.sh"
        elif [ -f "$INSTALL_DIR/assemblies/Steam++.dll" ] && [ -x "$INSTALL_DIR/dotnet/dotnet" ]; then
            start_cmd="$INSTALL_DIR/dotnet/dotnet"
        fi
        if [ -n "$start_cmd" ]; then
            read -r -n1 -p "现在启动 Watt Toolkit 吗？[回车/A=启动，其他键=跳过] " launch_now < /dev/tty || launch_now="q"
            echo
            if [[ -z "$launch_now" || "$launch_now" =~ [Aa] ]]; then
                if [ "$start_cmd" = "$INSTALL_DIR/dotnet/dotnet" ]; then
                    (cd "$INSTALL_DIR" && nohup env DOTNET_ROOT="$INSTALL_DIR/dotnet" "$start_cmd" "$INSTALL_DIR/assemblies/Steam++.dll" >/dev/null 2>&1 &)
                else
                    nohup "$start_cmd" >/dev/null 2>&1 &
                fi
                echo -e "${GREEN}✓ 已启动 Watt Toolkit${NC}"
                echo ""
            fi
        else
            echo -e "${YELLOW}未找到 Steam++.sh / dotnet 启动入口，请手动从桌面启动。${NC}"
            echo ""
        fi
        local wait_count=0
        while [ ! -f "$CERT_FILE" ]; do
            wait_count=$((wait_count + 1))
            if [ "$wait_count" -gt 30 ]; then
                echo -e "${YELLOW}等待超时，已退出。证书生成后可再运行本功能。${NC}"
                return 0
            fi
            read -r -n1 -p "在 Watt Toolkit 里点一次「加速」后按回车重新检测（Q 放弃）: " retry < /dev/tty || { echo; echo -e "${CYAN}输入不可用，已退出。${NC}"; return 0; }
            echo
            if [[ "${retry:-}" =~ [Qq] ]]; then
                echo -e "${CYAN}已放弃。证书生成后可再运行「信任证书」。${NC}"
                return 0
            fi
        done
        echo ""
    fi

    echo -e "${GREEN}✓ 找到证书: $CERT_FILE${NC}"

    # ---------- 证书校验：必须是 CA:TRUE，且记录指纹 ----------
    if command -v openssl >/dev/null 2>&1; then
        local cert_subject cert_end bc
        if ! cert_subject=$(openssl x509 -in "$CERT_FILE" -noout -subject 2>/dev/null); then
            echo -e "${RED}✗ 证书无法解析，文件可能已损坏。${NC}"
            return 1
        fi
        echo "  $cert_subject"
        bc=$(openssl x509 -in "$CERT_FILE" -noout -text 2>/dev/null | grep -A1 "Basic Constraints" | tr '\n' ' ')
        if ! printf '%s' "$bc" | grep -qi "CA:TRUE"; then
            echo -e "${RED}✗ 该证书不是 CA 证书（Basic Constraints 缺少 CA:TRUE），拒绝加入系统信任库。${NC}"
            echo -e "${YELLOW}  只信任 Watt Toolkit 自己生成的根证书，避免误信普通终端证书。${NC}"
            return 1
        fi
        echo -e "${GREEN}  ✓ Basic Constraints: CA:TRUE${NC}"
        cert_end=$(openssl x509 -in "$CERT_FILE" -noout -enddate 2>/dev/null | cut -d= -f2)
        [ -n "$cert_end" ] && echo "  有效期至: $cert_end"
        if ! openssl x509 -in "$CERT_FILE" -noout -checkend 0 >/dev/null 2>&1; then
            echo -e "${RED}✗ 证书已过期，请先在 Watt Toolkit 里重新生成证书。${NC}"
            return 1
        fi
        CERT_FP=$(openssl x509 -in "$CERT_FILE" -noout -fingerprint -sha256 2>/dev/null | cut -d= -f2 | tr -d ':' | tr 'A-F' 'a-f')
        if [ -z "$CERT_FP" ]; then
            echo -e "${RED}✗ 无法读取证书指纹，已中止。${NC}"
            return 1
        fi
        echo "  SHA256 指纹: $CERT_FP"
    else
        if ! grep -q "BEGIN CERTIFICATE" "$CERT_FILE" 2>/dev/null; then
            echo -e "${RED}✗ 文件不是有效的 PEM 证书，已中止。${NC}"
            return 1
        fi
        echo -e "${YELLOW}⚠ 未安装 openssl，无法校验 CA:TRUE / 指纹；仅做 PEM 基本检查。${NC}"
        echo -e "${YELLOW}  建议先安装 openssl 后重试，以便在卸载时按指纹精确移除。${NC}"
    fi

    local already_trusted=false
    if trust list 2>/dev/null | grep -qi "SteamTools Certificate"; then
        already_trusted=true
        echo ""
        echo -e "${CYAN}系统信任库里已存在该证书，本次将覆盖更新。${NC}"
    fi

    echo ""
    read -r -n1 -p "按回车键或 A 键确认写入系统信任库，其他键取消: " confirm < /dev/tty || confirm="q"
    echo
    if [[ -n "$confirm" && ! "$confirm" =~ [Aa] ]]; then
        echo -e "${GREEN}已取消，未做任何改动。${NC}"
        return 0
    fi

    if ! ensure_writable; then return 1; fi

    # ---------- 保存 hosts 原权限 ----------
    local HOSTS_PERM=""
    HOSTS_PERM=$(stat -c %a /etc/hosts 2>/dev/null)
    [ -z "$HOSTS_PERM" ] && HOSTS_PERM="644"
    echo -e "${CYAN}/etc/hosts 原权限: $HOSTS_PERM（已记录，卸载时恢复）${NC}"

    # ---------- 写入信任库 ----------
    echo ""
    echo -e "${CYAN}正在把证书写入系统信任库...${NC}"
    # FIX-WATT: `sudo trust anchor --store` 会写到 root 的私有 anchor 位置，
    # 普通用户的 `trust list` 看不到，且不会刷新系统证书包 —— 结果就是
    # "✓ 已加入" 但 HTTPS 加速仍报证书错误。改为显式写入系统 anchors 目录、
    # 刷新证书包，再用 openssl 指纹验证是否真正生效。
    local ANCHOR_DIR="/etc/ca-certificates/trust-source/anchors"
    local ANCHOR_FILE="$ANCHOR_DIR/SteamTools.Certificate.crt"
    if [ ! -d "$ANCHOR_DIR" ]; then
        if ! sudo mkdir -p "$ANCHOR_DIR" 2>/dev/null; then
            echo -e "${RED}✗ 无法创建系统证书目录 $ANCHOR_DIR。${NC}"
            return 1
        fi
    fi
    if ! sudo cp "$CERT_FILE" "$ANCHOR_FILE" 2>/dev/null; then
        echo -e "${RED}✗ 写入系统证书目录失败，请检查上方输出。${NC}"
        return 1
    fi
    sudo chmod 644 "$ANCHOR_FILE" 2>/dev/null
    # p11-kit 也登记一份（失败不致命，系统 anchors 已就位）
    sudo trust anchor --store "$CERT_FILE" 2>/dev/null || true
    # 刷新系统证书包，让浏览器/openssl 立刻能看到新 CA
    if command -v update-ca-trust >/dev/null 2>&1; then
        if ! sudo update-ca-trust 2>/dev/null; then
            echo -e "${YELLOW}⚠ 刷新系统证书包失败，可稍后手动执行 sudo update-ca-trust。${NC}"
        fi
    fi
    # 功能判据：用系统 bundle 直接验证这张证书能否通过
    local TRUST_OK=0
    if command -v openssl >/dev/null 2>&1 && [ -f /etc/ca-certificates/extracted/tls-ca-bundle.pem ]; then
        if openssl verify -CAfile /etc/ca-certificates/extracted/tls-ca-bundle.pem "$CERT_FILE" >/dev/null 2>&1; then
            TRUST_OK=1
        fi
    fi
    if [ "$TRUST_OK" -eq 1 ]; then
        echo -e "${GREEN}✓ 已确认证书在系统信任库中生效（openssl verify 通过）${NC}"
    else
        echo -e "${YELLOW}⚠ 无法确认证书已在系统信任库生效，HTTPS 加速可能仍报证书错误。${NC}"
        echo "    可手动检查: openssl verify -CAfile /etc/ca-certificates/extracted/tls-ca-bundle.pem $CERT_FILE"
    fi

    # ---------- 记录文件：保存 hosts 原权限与证书指纹 ----------
    if ! mkdir -p "$(dirname "$RECORD_FILE")" 2>/dev/null; then
        echo -e "${RED}✗ 无法创建记录目录，已中止（避免以后无法精确卸载）。${NC}"
        return 1
    fi
    {
        echo "HOSTS_PERM=$HOSTS_PERM"
        echo "CERT_FP=$CERT_FP"
        echo "CERT_FILE=$CERT_FILE"
    } > "$RECORD_FILE" || {
        echo -e "${RED}✗ 无法写入记录文件 $RECORD_FILE，已中止。${NC}"
        return 1
    }
    chmod 600 "$RECORD_FILE" 2>/dev/null || true

    # ---------- hosts 可写：用 sudo 临时提权，不永久 chmod a+w ----------
    # Watt Toolkit 以普通用户运行需要写 hosts；这里只把 hosts 的属主改成当前用户，
    # 并保留原权限位（不再放开 group/others 写权限），卸载时按记录恢复。
    echo ""
    echo -e "${CYAN}配置 /etc/hosts 可写（仅属主可写，使用 sudo 临时提权）...${NC}"
    local hosts_fail=0
    if ! sudo chown "$CURRENT_USER":"$CURRENT_GROUP" /etc/hosts 2>/dev/null; then
        echo -e "${YELLOW}⚠ 无法调整 /etc/hosts 属主，加速时可能需要手动授权。${NC}"
        hosts_fail=1
    fi
    # 只给属主写权限；去掉 group/others 的写位（绝不 a+w）
    if ! sudo chmod u+w,go-w /etc/hosts 2>/dev/null; then
        echo -e "${YELLOW}⚠ 调整 /etc/hosts 权限失败，加速时可能需要手动授权。${NC}"
        hosts_fail=1
    fi
    # 功能判据：当前用户是否真的能写 /etc/hosts
    if ! [ -w /etc/hosts ]; then
        echo -e "${YELLOW}⚠ /etc/hosts 当前仍不可写，加速功能改 hosts 可能失败。${NC}"
        hosts_fail=1
    fi
    local hosts_perm
    hosts_perm=$(stat -c '%A %U:%G' /etc/hosts 2>/dev/null)
    [ -n "$hosts_perm" ] && echo "  当前权限/属主: $hosts_perm"

    echo ""
    if [ "$hosts_fail" -ne 0 ] || [ "$TRUST_OK" -ne 1 ]; then
        echo -e "${YELLOW}⚠ 加速证书信任流程结束，但有项目未生效，请按上方提示处理。${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ 加速证书信任完成${NC}"
    echo -e "${YELLOW}提示：${NC}"
    echo "  · 已打开的浏览器需要重启，才会重新加载系统证书库"
    echo "  · /etc/hosts 原权限 $HOSTS_PERM 与证书指纹已记录到 $RECORD_FILE"
    echo "  · 卸载时会按记录恢复，而非一律改成 644"
    if $already_trusted; then
        echo "  · 本次是覆盖更新，旧证书已被替换"
    fi
}

watt_toolkit_uninstall() {
    # FIX-SOFTWARE: 即使程序目录不存在也继续清理根 CA / hosts 权限；
    # 按记录文件恢复 hosts 原权限、按指纹精确移除证书；失败如实报告。
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Watt Toolkit ══════════════${NC}"
    local INSTALL_DIR="$HOME/Watt Toolkit"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local RECORD_FILE="$HOME/.local/share/Steam++/watt_toolkit_trust.record"
    local cert_dir="$HOME/.local/share/Steam++/Plugins/Accelerator"
    local cert_file="$cert_dir/SteamTools.Certificate.cer"
    local confirm=""
    local HOSTS_PERM="" CERT_FP="" REC_CERT_FILE=""

    if [ -f "$RECORD_FILE" ]; then
        while IFS='=' read -r rk rv; do
            case "$rk" in
                HOSTS_PERM) HOSTS_PERM="$rv" ;;
                CERT_FP) CERT_FP="$rv" ;;
                CERT_FILE) REC_CERT_FILE="$rv" ;;
            esac
        done < "$RECORD_FILE"
    fi
    [ -n "$REC_CERT_FILE" ] && cert_file="$REC_CERT_FILE"

    local install_exists=false
    [ -d "$INSTALL_DIR" ] && install_exists=true
    if ! $install_exists; then
        echo -e "${YELLOW}未检测到程序目录，但仍会继续清理证书信任与 /etc/hosts 权限。${NC}"
    fi

    echo -e "${CYAN}将执行以下操作：${NC}"
    $install_exists && echo "  · 删除目录: $INSTALL_DIR"
    echo "  · 删除桌面快捷方式: $DESKTOP_DIR/Watt_Toolkit.desktop"
    echo "  · 从系统信任库移除 SteamTools 根证书（有记录时按 SHA256 指纹精确匹配）"
    echo "  · 恢复 /etc/hosts 权限${HOSTS_PERM:+（原权限 $HOSTS_PERM）}"
    echo ""
    echo -e "${YELLOW}警告：目录内可能含用户数据；删除系统级改动需要 sudo。${NC}"
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}已取消，未做任何改动。${NC}"
        return 0
    fi

    local fail_count=0
    # ---------- 删除程序目录（symlink 不跟随） ----------
    if $install_exists; then
        if [ -L "$INSTALL_DIR" ]; then
            echo -e "${RED}✗ $INSTALL_DIR 是符号链接，拒绝删除，请手动检查。${NC}"
            fail_count=$((fail_count + 1))
        elif rm -rf "$INSTALL_DIR"; then
            echo -e "${GREEN}✓ 已删除安装目录${NC}"
        else
            echo -e "${RED}✗ 删除安装目录失败${NC}"
            fail_count=$((fail_count + 1))
        fi
    fi

    # ---------- 桌面快捷方式（XDG + 兼容旧路径） ----------
    local df
    for df in "$DESKTOP_DIR/Watt_Toolkit.desktop" "$HOME/Desktop/Watt_Toolkit.desktop"; do
        if [ -e "$df" ] || [ -L "$df" ]; then
            if rm -f "$df"; then
                echo -e "${GREEN}✓ 已删除桌面快捷方式 $df${NC}"
            else
                echo -e "${RED}✗ 删除桌面快捷方式失败: $df${NC}"
                fail_count=$((fail_count + 1))
            fi
        fi
    done

    # ---------- 系统级清理（无条件执行） ----------
    echo ""
    echo -e "${CYAN}清理系统级改动...${NC}"
    if ! ensure_writable; then
        fail_count=$((fail_count + 1))
    else
        # 按指纹精确移除，而不是只按显示名
        local removed=false fp=""
        fs_cert_fp() {
            command -v openssl >/dev/null 2>&1 || return 1
            openssl x509 -in "$1" -noout -fingerprint -sha256 2>/dev/null \
                | cut -d= -f2 | tr -d ':' | tr 'A-F' 'a-f'
        }
        # FIX-WATT: 信任功能会显式写 /etc/ca-certificates/trust-source/anchors/
        # SteamTools.Certificate.crt，卸载必须先删它，否则 update-ca-trust 后仍会信任。
        if [ -f /etc/ca-certificates/trust-source/anchors/SteamTools.Certificate.crt ]; then
            if sudo rm -f /etc/ca-certificates/trust-source/anchors/SteamTools.Certificate.crt 2>/dev/null; then
                echo -e "${GREEN}✓ 已删除系统证书锚点 SteamTools.Certificate.crt${NC}"
                removed=true
            else
                echo -e "${YELLOW}⚠ 删除系统证书锚点失败${NC}"
                fail_count=$((fail_count + 1))
            fi
        fi
        # 候选：记录里的证书文件 + 系统 anchors 目录里的 PEM
        local cand anchor_dirs=(
            /etc/pki/ca-trust/source/anchors
            /etc/ca-certificates/trust-source/anchors
            "$HOME/.local/share/p11-kit/anchors"
        )
        if [ -n "$CERT_FP" ]; then
            echo "  目标指纹: $CERT_FP"
            if [ -f "$cert_file" ]; then
                fp="$(fs_cert_fp "$cert_file")"
                if [ -n "$fp" ] && [ "$fp" = "$CERT_FP" ]; then
                    if sudo trust anchor --remove "$cert_file" 2>/dev/null; then
                        echo -e "${GREEN}✓ 已按指纹移除证书文件 $cert_file${NC}"
                        removed=true
                    fi
                fi
            fi
            for ad in "${anchor_dirs[@]}"; do
                [ -d "$ad" ] || continue
                for cand in "$ad"/*; do
                    [ -f "$cand" ] || continue
                    fp="$(fs_cert_fp "$cand")" || continue
                    if [ "$fp" = "$CERT_FP" ]; then
                        if sudo trust anchor --remove "$cand" 2>/dev/null; then
                            echo -e "${GREEN}✓ 已按指纹移除锚点 $cand${NC}"
                            removed=true
                        else
                            echo -e "${YELLOW}⚠ 移除锚点失败: $cand${NC}"
                            fail_count=$((fail_count + 1))
                        fi
                    fi
                done
            done
            if ! $removed; then
                echo -e "${YELLOW}⚠ 未在信任库中找到指纹匹配的锚点（可能已手动移除）。${NC}"
            fi
        else
            # 旧版本遗留：没有指纹记录时按精确 pkcs11 id 兜底，不再只按显示名删
            echo -e "${YELLOW}⚠ 记录文件里没有证书指纹（旧版信任或缺少 openssl），改用锚点 id 兜底。${NC}"
            local anchor_id
            anchor_id=$(trust list 2>/dev/null | grep -i -B 1 "label: SteamTools Certificate" \
                        | grep -o 'pkcs11:id=[^;]*;type=cert' | head -1)
            if [ -n "$anchor_id" ] && sudo trust anchor --remove "$anchor_id" 2>/dev/null; then
                echo -e "${GREEN}✓ 已按锚点 id 移除证书${NC}"
            elif [ -f "$cert_file" ] && sudo trust anchor --remove "$cert_file" 2>/dev/null; then
                echo -e "${GREEN}✓ 已按证书文件移除${NC}"
            else
                echo -e "${YELLOW}⚠ 未能自动移除证书，请手动执行：${NC}"
                echo "    trust list | grep -i -B1 'SteamTools'"
                echo "    sudo trust anchor --remove '<pkcs11:id=...>'"
                fail_count=$((fail_count + 1))
            fi
        fi

        # ---------- 恢复 /etc/hosts 原权限 ----------
        echo -e "${CYAN}正在恢复 /etc/hosts 权限...${NC}"
        local target_perm="$HOSTS_PERM"
        [ -z "$target_perm" ] && target_perm="644"
        if sudo chmod "$target_perm" /etc/hosts 2>/dev/null; then
            echo -e "${GREEN}✓ /etc/hosts 已恢复为 $target_perm${NC}"
        else
            echo -e "${YELLOW}⚠ 恢复失败，请手动执行: sudo chmod $target_perm /etc/hosts${NC}"
            fail_count=$((fail_count + 1))
        fi
        # 属主也恢复为 root（信任功能曾把它改成当前用户）
        if ! sudo chown root:root /etc/hosts 2>/dev/null; then
            echo -e "${YELLOW}⚠ 无法恢复 /etc/hosts 属主为 root，请手动执行: sudo chown root:root /etc/hosts${NC}"
            fail_count=$((fail_count + 1))
        fi
        local hosts_perm
        hosts_perm=$(stat -c '%A' /etc/hosts 2>/dev/null)
        [ -n "$hosts_perm" ] && echo "  当前权限: $hosts_perm"

        if command -v update-ca-trust >/dev/null 2>&1; then
            if ! sudo update-ca-trust 2>/dev/null; then
                echo -e "${YELLOW}⚠ 刷新系统证书包失败（可稍后手动执行 sudo update-ca-trust）。${NC}"
            fi
        fi
    fi

    if [ -f "$RECORD_FILE" ]; then
        rm -f "$RECORD_FILE" && echo -e "${GREEN}✓ 已清理记录文件${NC}"
    fi

    echo ""
    if [ "$fail_count" -gt 0 ]; then
        echo -e "${RED}✗ 卸载完成但有 $fail_count 项失败，请按上方提示手动处理。${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Watt Toolkit 卸载完成，证书与 hosts 权限已恢复。${NC}"
    return 0
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
# FIX-LEAD: decky service
User=${CURRENT_USER}
Environment="HOMEBREW_FOLDER=${HOMEBREW_DIR}"
Environment="UNPRIVILEGED_PATH=${HOMEBREW_DIR}"
Environment="PRIVILEGED_PATH=${HOMEBREW_DIR}"
WorkingDirectory=${HOMEBREW_DIR}
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

    # FIX-LEAD: uninstall_plugin_store ZH
    # 旧版只删 homebrew，留下已启用的 plugin_loader.service；重启后 systemd 会
    # 反复尝试启动已不存在的二进制。卸载前先停服务并删除 unit。
    local _fail=0
    if systemctl is-enabled --quiet plugin_loader 2>/dev/null || systemctl is-active --quiet plugin_loader 2>/dev/null; then
        if ! sudo systemctl disable --now plugin_loader 2>/dev/null; then
            echo -e "${YELLOW}⚠️  停止/禁用 plugin_loader 服务失败，请稍后手动处理。${NC}"
            _fail=1
        fi
    fi
    if [ -f /etc/systemd/system/plugin_loader.service ]; then
        sudo rm -f /etc/systemd/system/plugin_loader.service 2>/dev/null || _fail=1
    fi
    if [ -f "$HOME/.config/systemd/user/plugin_loader.service" ]; then
        rm -f "$HOME/.config/systemd/user/plugin_loader.service" 2>/dev/null || _fail=1
    fi
    sudo systemctl daemon-reload 2>/dev/null || _fail=1
    # 安装时创建的 CEF 远程调试标记
    rm -f "$HOME/.steam/steam/.cef-enable-remote-debugging" \
          "$HOME/.var/app/com.valvesoftware.Steam/data/Steam/.cef-enable-remote-debugging" 2>/dev/null
    rm -rf /tmp/plugin_loader 2>/dev/null

    echo "正在执行卸载..."
    sudo rm -rf "$HOME/homebrew"
    # 以目录是否真的消失为准（rm 在部分失败时也可能返回 0）
    if [ -d "$HOME/homebrew" ]; then
        echo -e "${RED}✗ 插件商店卸载失败，目录仍存在: $HOME/homebrew${NC}"
        echo -e "${YELLOW}  请手动删除：sudo rm -rf \"$HOME/homebrew\"${NC}"
        return 1
    fi
    if [ "$_fail" -ne 0 ]; then
        echo -e "${YELLOW}⚠️  主目录已删除，但服务/标记清理有失败项，请按上面的提示手动检查。${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ 插件商店卸载完成${NC}"
    echo "如需重新安装，请使用 '安装插件商店' 功能。"
}

# ===== CheatDeck（Decky 插件）=====
install_cheatdeck_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 CheatDeck ════════════════${NC}"
    echo ""
    echo -e "${CYAN}CheatDeck 是 Decky 插件，用于在游戏模式管理第三方修改器入口。${NC}"
    echo -e "${YELLOW}重要声明：${NC}"
    echo "  · 本工具只安装插件本体（CheatDeck.zip），不附带任何修改器文件"
    echo "  · 使用修改器可能违反游戏服务条款（ToS），账号风险自负"
    echo "  · 与 DW Proton 等兼容层无关，请勿混用场景"
    echo ""
    if [ ! -d "$HOME/homebrew" ] || [ ! -e "$HOME/homebrew/services/PluginLoader" ]; then
        echo -e "${RED}未检测到 Decky Loader（~/homebrew）。请先到「插件相关 → 插件商店」安装 Decky。${NC}"
        return 1
    fi
    echo -e "${CYAN}安装后请在游戏模式打开 Decky：设置 → Developer → 开启开发者模式（Developer mode），${NC}"
    echo -e "${CYAN}以便插件正常加载；然后重启 Steam 或 PluginLoader。${NC}"
    echo ""
    read -n1 -p "已阅读风险说明，继续安装请按回车或 Y，其它键取消: " ans < /dev/tty
    echo
    if [[ -n "$ans" && "$ans" != "y" && "$ans" != "Y" ]]; then
        echo "已取消。"
        return 0
    fi
    # 只装资产 CheatDeck.zip（install_github_plugin 会按插件名优先选非源码 zip）
    install_github_plugin "SheffeyG/CheatDeck" "CheatDeck" "CheatDeck"
}

install_cheatdeck_uninstall() {
    uninstall_plugin_generic "CheatDeck" "CheatDeck"
}

# ===== 急救：Steam / Gamescope 重置 =====
_emergency_backup_root() {
    local stamp
    stamp=$(date +%Y%m%d_%H%M%S)
    local root="$HOME/steamdeck_toolbox_backups"
    mkdir -p "$root"
    echo "${root}/$1_${stamp}"
}

_emergency_stop_steam() {
    echo -e "${CYAN}正在结束 Steam / gamescope 相关进程（如有）...${NC}"
    # 尽量温和；失败不阻断
    # 不要在此切换会话；仅结束 Steam 相关进程
    pkill -TERM -u "$USER" -x steam 2>/dev/null || true
    pkill -TERM -u "$USER" -f '/steam(\.sh)?$' 2>/dev/null || true
    sleep 2
    pkill -KILL -u "$USER" -x steam 2>/dev/null || true
    sleep 1
}

emergency_steam_reset() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 急救：Steam 配置重置 ════════════════${NC}"
    echo ""
    echo "用途：桌面模式还能进，但 Steam 卡启动、转圈、配置损坏时尝试修复。"
    echo ""
    echo -e "${GREEN}会保留：${NC} steamapps（游戏本体）、大部分 userdata 存档云相关目录"
    echo -e "${YELLOW}会重置/清理（先自动备份）：${NC}"
    echo "  · ~/.local/share/Steam/config（客户端配置）"
    echo "  · Steam 启动/登录相关缓存（如 registry.vdf、.cef-cache、htmlcache、steamui 缓存）"
    echo -e "${RED}不会删除游戏安装目录 steamapps。${NC}"
    echo ""
    echo "备份目录示例：~/steamdeck_toolbox_backups/steam_reset_时间戳/"
    echo ""
    read -n1 -p "确认执行？输入 Y 继续，其它键取消: " ans < /dev/tty
    echo
    [[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "已取消。"; return 0; }
    read -n1 -p "再次确认：本地 Steam 设置会丢失（游戏本体保留）。输入 Y: " ans2 < /dev/tty
    echo
    [[ "$ans2" == "y" || "$ans2" == "Y" ]] || { echo "已取消。"; return 0; }

    _emergency_stop_steam
    local bak
    bak=$(_emergency_backup_root "steam_reset")
    mkdir -p "$bak"
    echo -e "${CYAN}备份到: $bak${NC}"

    local steam_root="$HOME/.local/share/Steam"
    # 兼容 ~/.steam/steam 符号链接场景：以真实 Steam 数据根为准
    if [ -d "$HOME/.steam/steam" ] && [ ! -d "$steam_root" ]; then
        steam_root="$HOME/.steam/steam"
    fi

    # 备份并移走配置
    if [ -d "$steam_root/config" ]; then
        # FIX-LEAD: emergency backup ZH
        # 备份失败仍删除原目录会造成不可恢复的配置丢失，这里必须成功才继续。
        if ! cp -a "$steam_root/config" "$bak/config" 2>/dev/null; then
            echo -e "${RED}✗ 备份 config 失败，已中止删除（原数据未改动）。${NC}"
            return 1
        fi
        rm -rf "$steam_root/config"
        echo -e "${GREEN}✓ 已重置 config${NC}"
    else
        echo -e "${YELLOW}- 未找到 config，跳过${NC}"
    fi

    # 常见启动缓存 / 注册表
    local f
    for f in \
        "$HOME/.steam/registry.vdf" \
        "$steam_root/registry.vdf" \
        "$steam_root/.cef-cache" \
        "$steam_root/config/htmlcache" \
        "$steam_root/steamui" \
        "$steam_root/appcache/httpcache"
    do
        if [ -e "$f" ]; then
            local base
            base=$(basename "$f")
            # 避免重名
            if [ -e "$bak/$base" ]; then
                base="${base}_$(echo "$f" | md5sum | awk '{print $1}' | cut -c1-6)"
            fi
            # FIX-LEAD: emergency loop backup
            if ! cp -a "$f" "$bak/$base" 2>/dev/null; then
                echo -e "${RED}✗ 备份 $f 失败，已中止删除。${NC}"
                return 1
            fi
            rm -rf "$f"
            echo -e "${GREEN}✓ 已清理 $f${NC}"
        fi
    done

    # htmlcache 可能在 config 下，上面已整夹移走；再清用户 HTML 缓存
    if [ -d "$steam_root/config/htmlcache" ]; then
        rm -rf "$steam_root/config/htmlcache"
    fi

    echo ""
    echo -e "${GREEN}✅ Steam 配置重置完成。${NC}"
    echo "备份位置: $bak"
    echo "请重新打开 Steam / 回到游戏模式试一次。若异常，可从备份目录手动拷回。"
}

emergency_gamescope_reset() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 急救：Gamescope / 游戏模式重置 ════════════════${NC}"
    echo ""
    echo "用途：游戏模式黑屏、进不去、分辨率/缩放异常，但桌面模式正常时尝试修复。"
    echo ""
    echo -e "${YELLOW}将备份并清理（不删游戏本体）：${NC}"
    echo "  · ~/.config/gamescope*（若存在）"
    echo "  · Steam 相关显示/UI 缓存（htmlcache、.cef-cache、steamui 部分缓存）"
    echo "  · 用户 gamescope 会话残留（~/.local/share/gamescope 等，若存在）"
    echo ""
    read -n1 -p "确认执行？输入 Y 继续，其它键取消: " ans < /dev/tty
    echo
    [[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "已取消。"; return 0; }
    read -n1 -p "再次确认：游戏模式相关本地设置可能丢失。输入 Y: " ans2 < /dev/tty
    echo
    [[ "$ans2" == "y" || "$ans2" == "Y" ]] || { echo "已取消。"; return 0; }

    _emergency_stop_steam
    local bak
    bak=$(_emergency_backup_root "gamescope_reset")
    mkdir -p "$bak"
    echo -e "${CYAN}备份到: $bak${NC}"

    local steam_root="$HOME/.local/share/Steam"
    [ -d "$HOME/.steam/steam" ] && [ ! -d "$steam_root" ] && steam_root="$HOME/.steam/steam"

    local p
    for p in \
        "$HOME/.config/gamescope" \
        "$HOME/.config/gamescope-session" \
        "$HOME/.local/share/gamescope" \
        "$steam_root/.cef-cache" \
        "$steam_root/config/htmlcache" \
        "$steam_root/steamui/movies" \
        "$HOME/.steam/steam.pid"
    do
        if [ -e "$p" ]; then
            local dest
            dest="$bak/$(echo "$p" | sed 's#^/##; s#/#_#g')"
            mkdir -p "$(dirname "$dest")"
            # FIX-LEAD: emergency gamescope backup
            if ! cp -a "$p" "$dest" 2>/dev/null; then
                echo -e "${RED}✗ 备份 $p 失败，已中止删除。${NC}"
                return 1
            fi
            rm -rf "$p"
            echo -e "${GREEN}✓ 已清理 $p${NC}"
        fi
    done

    # 清临时 gamescope socket/残留（不备份）
    rm -rf /tmp/gamescope-*=* 2>/dev/null || true
    rm -f /tmp/gamescope.* 2>/dev/null || true

    echo ""
    echo -e "${GREEN}✅ Gamescope / 游戏模式相关状态已重置。${NC}"
    echo "备份位置: $bak"
    echo "请从桌面模式切换回游戏模式，或重启后再试。"
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
    echo -e "${GREEN}✓ 中文界面：已写入汉化版 Clover-Toolbox.sh。${NC}"

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

    # FIX-SOFTWARE: 版本查询加 --fail/超时；无法获取版本时不臆造默认版本去降级。
    echo "正在检查最新版本..."
    local REMOTE_VERSION=$(curl -fsSL --connect-timeout 15 --max-time 60 https://anydesk.com.cn/zhs/downloads/linux 2>/dev/null | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/^v//')
    if [ -z "$REMOTE_VERSION" ]; then
        echo -e "${YELLOW}无法可靠获取官网版本（网络异常或页面改版），已取消更新，保持现有安装。${NC}"
        echo -e "${YELLOW}  不再使用硬编码默认版本，避免把已安装的新版本误降级。${NC}"
        return 0
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
        # 只有远程版本「严格大于」本地才更新；相等/更小/无法比较都保持本地。
        if ! fs_ver_gt "$REMOTE_VERSION" "$LOCAL_VERSION"; then
            echo -e "${GREEN}✅ 本地版本 ${LOCAL_VERSION} 不低于官网 ${REMOTE_VERSION}，保持现有安装，不更新（避免误降级）。${NC}"
            return 0
        fi
        echo -e "${YELLOW}发现更高的新版本 ${REMOTE_VERSION}（当前: ${LOCAL_VERSION}）${NC}"
        if ! confirm_action; then
            echo "取消更新。"
            return 0
        fi
        TARGET_VERSION="$REMOTE_VERSION"
    else
        TARGET_VERSION="$REMOTE_VERSION"
    fi

    if [ -z "$TARGET_VERSION" ]; then
        echo "未指定目标版本，操作取消。"
        return 0
    fi

    echo "正在安装 AnyDesk ${TARGET_VERSION}..."
    cd /tmp || return

    # FIX-SOFTWARE: mktemp -d 避免共享固定 /tmp 名；curl/wget 加 --fail/超时。
    local URL="https://download.anydesk.com/linux/anydesk-${TARGET_VERSION}-amd64.tar.gz"
    local WORK_DIR
    WORK_DIR="$(mktemp -d /tmp/anydesk-install.XXXXXXXX 2>/dev/null)" || {
        echo -e "${RED}✗ 无法创建临时目录，已中止。${NC}"; return 1; }
    local TARBALL="$WORK_DIR/anydesk-${TARGET_VERSION}.tar.gz"
    local EXTRACT_DIR="$WORK_DIR/extract"
    echo "下载中..."

    if ! wget -q --show-progress --connect-timeout=15 --timeout=180 --tries=1 "$URL" -O "$TARBALL"; then
        echo -e "${RED}下载失败，请检查网络后重试。${NC}"
        echo -e "${YELLOW}已保留原有的 AnyDesk 安装（如有）。${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    if [ ! -s "$TARBALL" ]; then
        echo -e "${RED}下载文件为空或不是有效归档，已中止。${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    mkdir -p "$EXTRACT_DIR" || { rm -rf "$WORK_DIR"; return 1; }
    if ! tar -xzf "$TARBALL" -C "$EXTRACT_DIR" --strip-components=1; then
        echo -e "${RED}✗ 解压失败，安装中止。${NC}"
        rm -rf "$WORK_DIR"
        echo -e "${YELLOW}已保留原有的 AnyDesk 安装（如有）。${NC}"
        return 1
    fi
    if [ ! -x "$EXTRACT_DIR/anydesk" ]; then
        echo -e "${RED}✗ 安装包内容不完整（未找到 anydesk 可执行文件），安装中止。${NC}"
        rm -rf "$WORK_DIR"
        echo -e "${YELLOW}已保留原有的 AnyDesk 安装（如有）。${NC}"
        return 1
    fi

    # 原子替换：先把新内容放到临时目录，mv 成功后再切换，绝不先删旧目录。
    local STAGE_DIR="$WORK_DIR/stage"
    if ! mkdir -p "$STAGE_DIR"; then rm -rf "$WORK_DIR"; return 1; fi
    if ! cp -a "$EXTRACT_DIR"/. "$STAGE_DIR"/; then
        echo -e "${RED}✗ 安装文件复制失败。${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    chmod +x "$STAGE_DIR/anydesk" 2>/dev/null
    if [ ! -x "$STAGE_DIR/anydesk" ]; then
        echo -e "${RED}✗ 暂存目录缺少可执行文件，已中止（旧安装未动）。${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    local BACKUP_DIR=""
    if [ -d "$ANYDESK_INSTALL_DIR" ]; then
        BACKUP_DIR="$WORK_DIR/backup"
        if ! mv "$ANYDESK_INSTALL_DIR" "$BACKUP_DIR"; then
            echo -e "${RED}✗ 备份旧安装目录失败，已中止（旧安装未动）。${NC}"
            rm -rf "$WORK_DIR"
            return 1
        fi
    fi
    if ! mv "$STAGE_DIR" "$ANYDESK_INSTALL_DIR"; then
        echo -e "${RED}✗ 安装新版本失败，正在恢复旧版本...${NC}"
        [ -n "$BACKUP_DIR" ] && mv "$BACKUP_DIR" "$ANYDESK_INSTALL_DIR" 2>/dev/null
        rm -rf "$WORK_DIR"
        return 1
    fi
    rm -rf "$WORK_DIR"
    if [ ! -x "$ANYDESK_BIN" ]; then
        echo -e "${RED}✗ 安装文件不完整（未找到可执行文件）。${NC}"
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

    local fail=0
    if $local_found; then
        if rm -rf "$ANYDESK_INSTALL_DIR"; then
            echo -e "${GREEN}✓ 已删除本地安装目录${NC}"
        else
            echo -e "${RED}✗ 删除本地安装目录失败${NC}"; fail=1
        fi
        if rm -f "$DESKTOP_FILE"; then
            echo -e "${GREEN}✓ 已删除本地桌面快捷方式${NC}"
        else
            echo -e "${RED}✗ 删除本地桌面快捷方式失败${NC}"; fail=1
        fi
        if rm -f "$BIN_LINK"; then
            echo -e "${GREEN}✓ 已删除命令链接${NC}"
        else
            echo -e "${RED}✗ 删除命令链接失败${NC}"; fail=1
        fi
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
            fail=1
        fi
    fi

    echo ""
    if [ "$fail" -ne 0 ]; then
        echo -e "${RED}✗ 卸载过程中有失败项，不报告为完全成功，请按上方提示手动处理。${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ AnyDesk 卸载完成。${NC}"
}

install_todesk() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 安装 ToDesk ════════════════${NC}"
    echo ""

    # ToDesk 官方 Arch 包长期停留在 4.1.0，社区（archtodesk）重打包了 4.7.2.0。
    # 这里不再执行任何第三方 shell 脚本，改为自己取回 .pkg.tar.zst 后用 pacman 直接装：
    # 少跑一段 root 脚本、不重建 pacman 钥匙环、不装 base-devel、不硬编码 /home/deck。
    local TODESK_REPO="https://gitee.com/mclanbai/archtodesk.git"
    local TODESK_PKG="todesk-bin-4.7.2.0-4-x86_64.pkg.tar.zst"
    local TODESK_VERSION="4.7.2.0"
    local CLONE_DIR="$TEMP_DIR/archtodesk"
    local DESKTOP_FILE="$HOME/Desktop/ToDesk.desktop"

    echo "  来源: gitee.com/mclanbai/archtodesk（社区重打包的官方 4.7.2.0 安装包）"
    echo "  本功能只下载该仓库里的 .pkg.tar.zst 并用 pacman 安装，不执行其中任何脚本。"
    echo ""

    # ---------- 已安装检测 ----------
    # 三种来源都算「已安装」：pacman 包（todesk-bin / todesk）、/opt/todesk 程序目录、
    # 以及能直接跑起来的 ToDesk 二进制。只看 pacman 会漏掉包数据库损坏或手动解包的情况。
    local installed_ver="" installed_src=""
    if pacman -Q todesk-bin &>/dev/null; then
        installed_ver=$(pacman -Q todesk-bin 2>/dev/null | awk '{print $2}')
        installed_src="pacman 包 todesk-bin"
    elif pacman -Q todesk &>/dev/null; then
        installed_ver=$(pacman -Q todesk 2>/dev/null | awk '{print $2}')
        installed_src="pacman 包 todesk"
    elif [ -x /opt/todesk/bin/ToDesk ] || [ -d /opt/todesk ]; then
        installed_ver="未知（非 pacman 安装）"
        installed_src="/opt/todesk 目录"
    fi

    if [ -n "$installed_ver" ]; then
        echo -e "${GREEN}✓ 检测到已安装 ToDesk${NC}"
        echo "    当前版本: ${installed_ver}"
        echo "    安装来源: ${installed_src}"
        echo "    目标版本: ${TODESK_VERSION}"
        echo ""
        echo -e "${YELLOW}请选择操作：${NC}"
        echo "  1. 重新安装（卸载现有版本后重装 ${TODESK_VERSION}）"
        echo "  2. 不安装，直接退出"
        echo "  3. 卸载 ToDesk（不再安装）"
        echo ""
        local choice
        while true; do
            if ! read -p "请输入选择 [1-3]（回车默认 2）: " choice < /dev/tty; then
                echo ""
                echo -e "${GREEN}保持当前安装，未做任何改动。${NC}"
                return 0
            fi
            case "$choice" in
                1) break ;;
                3)
                    echo ""
                    uninstall_todesk
                    return $? ;;
                ""|2)
                    echo -e "${GREEN}保持当前安装，未做任何改动。${NC}"
                    return 0 ;;
                *) echo -e "${RED}无效输入，请输入 1、2 或 3。${NC}" ;;
            esac
        done
        echo -e "${CYAN}将卸载现有版本后重装...${NC}"
    fi

    # ---------- 前置工具 ----------
    local missing_tools=()
    command -v git &>/dev/null || missing_tools+=("git")
    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${YELLOW}缺少必要工具: ${missing_tools[*]}${NC}"
        if ! ensure_writable; then return 1; fi
        if ! sudo pacman -S --needed --noconfirm "${missing_tools[@]}"; then
            echo -e "${RED}✗ 安装 ${missing_tools[*]} 失败。${NC}"
            return 1
        fi
    fi

    # ---------- 解除只读（pacman 写系统需要） ----------
    if ! ensure_writable; then return 1; fi

    # ---------- 运行依赖 ----------
    echo ""
    echo -e "${CYAN}检查运行依赖...${NC}"
    local missing_deps=()
    for dep in gtk3 libappindicator-gtk3; do
        pacman -Q "$dep" &>/dev/null || missing_deps+=("$dep")
    done
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${YELLOW}缺少依赖: ${missing_deps[*]}，正在安装...${NC}"
        if ! sudo pacman -S --needed --noconfirm "${missing_deps[@]}"; then
            echo -e "${RED}✗ 依赖安装失败，已中止。${NC}"
            return 1
        fi
        echo -e "${GREEN}✓ 依赖安装完成${NC}"
    else
        echo -e "${GREEN}✓ 依赖已满足（gtk3、libappindicator-gtk3）${NC}"
    fi

    # ---------- 取回安装包 ----------
    # 注意：Gitee 对仓库内 >1MB 的文件禁止匿名 raw 直链（返回 403 large file require
    # login），所以 80MB 的包只能通过 git clone 取，不能直接 curl 下载。
    echo ""
    echo -e "${CYAN}正在下载 ToDesk $TODESK_VERSION 安装包（约 80MB）...${NC}"
    echo -e "${YELLOW}（Gitee 限制大文件直链下载，这里用 git clone 取包，请稍候）${NC}"
    rm -rf "$CLONE_DIR"
    if ! git clone --depth 1 --progress "$TODESK_REPO" "$CLONE_DIR"; then
        echo -e "${RED}✗ 下载失败，请检查网络后重试。${NC}"
        rm -rf "$CLONE_DIR"
        return 1
    fi

    local pkg_path="$CLONE_DIR/$TODESK_PKG"
    if [ ! -f "$pkg_path" ]; then
        echo -e "${RED}✗ 未在仓库中找到 $TODESK_PKG，上游仓库结构可能已变更。${NC}"
        echo -e "${YELLOW}  已中止，未修改系统。${NC}"
        rm -rf "$CLONE_DIR"
        return 1
    fi

    # ---------- 完整性校验 ----------
    echo ""
    echo -e "${CYAN}校验安装包完整性...${NC}"
    local verify_ok=0
    if command -v zstd &>/dev/null; then
        zstd -t "$pkg_path" &>/dev/null && verify_ok=1
    else
        pacman -Qip "$pkg_path" &>/dev/null && verify_ok=1
    fi
    if [ "$verify_ok" -ne 1 ]; then
        echo -e "${RED}✗ 安装包校验失败（文件损坏或不完整），已中止。${NC}"
        rm -rf "$CLONE_DIR"
        return 1
    fi
    echo -e "${GREEN}✓ 安装包完整${NC}"

    # ---------- 清理旧版本 ----------
    # FIX-SOFTWARE: 记录旧包信息；卸载失败立即中止（不再 || true 继续）。
    local OLD_PKGS=""
    pacman -Q todesk &>/dev/null && OLD_PKGS="$OLD_PKGS todesk"
    pacman -Q todesk-bin &>/dev/null && OLD_PKGS="$OLD_PKGS todesk-bin"
    OLD_PKGS="${OLD_PKGS# }"
    [ -n "$OLD_PKGS" ] && echo -e "${CYAN}安装前检测到旧包:$OLD_PKGS（已记录，失败时可据此恢复）${NC}"
    if pacman -Q todesk &>/dev/null; then
        echo -e "${CYAN}卸载旧版 todesk 包...${NC}"
        if ! sudo pacman -R --noconfirm todesk; then
            echo -e "${RED}✗ 卸载旧版 todesk 失败，为避免版本冲突已中止，未安装新包。${NC}"
            echo -e "${YELLOW}  请手动处理: sudo pacman -R --noconfirm todesk${NC}"
            rm -rf "$CLONE_DIR"
            return 1
        fi
    fi
    if pacman -Q todesk-bin &>/dev/null; then
        echo -e "${CYAN}卸载现有 todesk-bin...${NC}"
        if ! sudo pacman -R --noconfirm todesk-bin; then
            echo -e "${RED}✗ 卸载现有 todesk-bin 失败，已中止。${NC}"
            echo -e "${YELLOW}  旧包信息:${OLD_PKGS:-无}${NC}"
            echo -e "${YELLOW}  恢复指引: sudo pacman -U --noconfirm $pkg_path（安装包仍在 $CLONE_DIR）${NC}"
            rm -rf "$CLONE_DIR"
            return 1
        fi
    fi

    # ---------- 清理孤儿文件（关键） ----------
    # 处理 pacman -R 管不到的脏状态：包记录已经没了（卸载被中断、手动删过数据库、
    # 或当初是解包安装），但 /opt/todesk 等文件还留在系统里。
    # 此时 `pacman -U` 会报「文件系统中已存在 xxx」直接拒绝安装，而上面两个
    # `pacman -Q` 判断都为假，清理被整体跳过 —— 这正是重装失败的根因。
    # 判据：包未登记 + 文件确实存在 = 无主残留，必须自己清掉。
    # 注意 db.lck 不参与「是否存在残留」的判断：它是 pacman 的全局锁，
    # 平时有 pacman 在跑就会存在，与 ToDesk 无关；只有确认要清理时才顺手删。
    local orphan_paths=(
        /opt/todesk
        /usr/bin/todesk
        /usr/lib/systemd/system/todeskd.service
        /usr/share/applications/todesk.desktop
        /usr/share/licenses/todesk-bin
    )
    local orphan_found=false
    for op in "${orphan_paths[@]}"; do
        if [ -e "$op" ]; then orphan_found=true; break; fi
    done
    if [ "$orphan_found" = true ] \
       && ! pacman -Q todesk-bin &>/dev/null \
       && ! pacman -Q todesk &>/dev/null; then
        echo ""
        echo -e "${YELLOW}检测到 ToDesk 残留文件（包未登记，但文件仍在系统中）${NC}"
        echo -e "${CYAN}清理残留文件，避免 pacman 报「文件系统中已存在」...${NC}"
        # 先停服务、杀进程，否则 /opt/todesk 下被占用的二进制删不干净
        sudo systemctl stop todeskd.service 2>/dev/null || true
        sudo systemctl disable todeskd.service 2>/dev/null || true
        sudo pkill -f '/opt/todesk/bin/' 2>/dev/null || true
        sleep 1
        for op in "${orphan_paths[@]}"; do
            [ -e "$op" ] || continue
            sudo rm -rf "$op" 2>/dev/null || true
        done
        # 图标目录：只删 todesk 自己的图标，不动 hicolor 下别家的文件
        sudo rm -f /usr/share/icons/hicolor/*/apps/todesk.png 2>/dev/null || true
        # pacman 的数据库锁：上次安装被中断可能留下它，会让后续 pacman 操作一直报
        # 「无法锁定数据库」。只在没有 pacman 进程运行时才删，避免打断正在进行的操作。
        if [ -e /usr/lib/holo/pacmandb/db.lck ] && ! pgrep -x pacman &>/dev/null; then
            sudo rm -f /usr/lib/holo/pacmandb/db.lck 2>/dev/null || true
        fi
        sudo systemctl daemon-reload 2>/dev/null || true

        # 复核：还有残留就明确告知，而不是让 pacman 再报一次看不懂的冲突
        local still_left=""
        for op in "${orphan_paths[@]}"; do
            if [ -e "$op" ]; then still_left="$still_left $op"; fi
        done
        if [ -n "$still_left" ]; then
            echo -e "${RED}✗ 以下残留文件未能删除:$still_left${NC}"
            echo -e "${YELLOW}  请手动执行: sudo rm -rf$still_left${NC}"
            rm -rf "$CLONE_DIR"
            return 1
        fi
        echo -e "${GREEN}✓ 残留文件已清理${NC}"
    fi

    # ---------- 安装 ----------
    echo ""
    echo -e "${CYAN}正在安装 ToDesk $TODESK_VERSION ...${NC}"
    if ! sudo pacman -U --noconfirm "$pkg_path"; then
        echo -e "${RED}✗ 安装失败，请检查上方 pacman 输出。${NC}"
        echo -e "${YELLOW}  安装前的旧包:${OLD_PKGS:-无} 已被卸载，未自动重装以免再次失败。${NC}"
        echo -e "${YELLOW}  手动恢复指引: sudo pacman -U --noconfirm $pkg_path${NC}"
        echo -e "${YELLOW}  （安装包保留在 $CLONE_DIR，未清理）${NC}"
        return 1
    fi

    # ---------- 服务与快捷方式：检查返回码 + is-active 验证 ----------
    # FIX-SOFTWARE: 不再 || true 吞掉 enable/restart 失败，服务未起不报安装成功。
    local svc_fail=0
    if ! sudo systemctl daemon-reload 2>/dev/null; then
        echo -e "${YELLOW}⚠ systemctl daemon-reload 失败${NC}"
    fi
    if ! sudo systemctl enable todeskd.service 2>/dev/null; then
        echo -e "${RED}✗ 启用 todeskd.service 失败${NC}"
        svc_fail=1
    fi
    if ! sudo systemctl restart todeskd.service 2>/dev/null; then
        echo -e "${RED}✗ 重启 todeskd.service 失败${NC}"
        svc_fail=1
    fi
    if ! systemctl is-active --quiet todeskd.service 2>/dev/null; then
        echo -e "${RED}✗ todeskd.service 未处于 active 状态${NC}"
        echo -e "${YELLOW}  可手动检查: systemctl status todeskd.service${NC}"
        svc_fail=1
    else
        echo -e "${GREEN}✓ todeskd.service 已启用并处于 active 状态${NC}"
    fi

    if [ -f /usr/share/applications/todesk.desktop ]; then
        mkdir -p "$HOME/Desktop"
        if cp -f /usr/share/applications/todesk.desktop "$DESKTOP_FILE" 2>/dev/null; then
            chmod +x "$DESKTOP_FILE" 2>/dev/null || true
            echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
        fi
    fi

    # ---------- 清理旧方案残留 ----------
    # 旧版本会引导用户执行第三方脚本，在桌面留下这两个「安装/重装」图标，顺手清掉。
    rm -f "$HOME/Desktop/install-todesk-service.desktop" \
          "$HOME/Desktop/reinstall-todesk-service.desktop" 2>/dev/null || true
    sudo rm -rf /tmp/lanbai 2>/dev/null || true
    rm -rf "$CLONE_DIR"

    # ---------- 结果确认 ----------
    echo ""
    if [ "$svc_fail" -ne 0 ]; then
        echo -e "${RED}✗ 包已安装，但服务未正常启动，不视为安装成功。${NC}"
        return 1
    fi
    if pacman -Q todesk-bin &>/dev/null || [ -x /opt/todesk/bin/ToDesk ]; then
        echo -e "${GREEN}✅ ToDesk $TODESK_VERSION 安装完成${NC}"
        echo -e "${YELLOW}提示: ToDesk 仅支持 X11 会话，不支持 Wayland。${NC}"
        echo -e "${YELLOW}      在游戏模式下请先切到桌面模式运行；桌面快捷方式已放在 $DESKTOP_FILE${NC}"
    else
        echo -e "${RED}✗ 安装后未检测到 ToDesk，请检查上方输出。${NC}"
        return 1
    fi
}

uninstall_todesk() {
    clear
    echo -e "${YELLOW}════════════════ 卸载 ToDesk ════════════════${NC}"
    echo ""

    local DESKTOP_FILE="$HOME/Desktop/ToDesk.desktop"
    local AUTOSTART_FILE="$HOME/.config/autostart/todesk.desktop"
    local USER_DATA_DIR="$HOME/.local/share/todesk"

    # ---------- 已安装检测 ----------
    # 与 install_todesk 用同一套判据：pacman 包（todesk-bin / todesk）或 /opt/todesk 目录，
    # 任一存在就算已安装。只看 pacman 会漏掉「包数据库损坏」和「手动解包安装」这两种情况。
    local pkg_name="" pkg_ver=""
    if pacman -Q todesk-bin &>/dev/null; then
        pkg_name="todesk-bin"
        pkg_ver=$(pacman -Q todesk-bin 2>/dev/null | awk '{print $2}')
    elif pacman -Q todesk &>/dev/null; then
        pkg_name="todesk"
        pkg_ver=$(pacman -Q todesk 2>/dev/null | awk '{print $2}')
    fi
    local has_dir=false
    [ -d /opt/todesk ] && has_dir=true

    if [ -z "$pkg_name" ] && [ "$has_dir" = false ]; then
        echo -e "${YELLOW}未检测到已安装的 ToDesk，无需卸载。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到 ToDesk 安装：${NC}"
    [ -n "$pkg_name" ] && echo "  • pacman 包 ${pkg_name} ${pkg_ver}"
    [ "$has_dir" = true ] && echo "  • 程序目录 /opt/todesk"
    echo ""
    echo -e "${YELLOW}将执行以下操作：${NC}"
    echo "  1. 停止并禁用 todeskd 服务，结束正在运行的 ToDesk 进程"
    echo "  2. 卸载 pacman 包（若存在），并清理 /opt/todesk 残留目录"
    echo "  3. 删除桌面快捷方式与开机自启项"
    echo ""
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo -e "${CYAN}继续卸载...${NC}"
    else
        echo -e "${GREEN}已取消，未做任何改动。${NC}"
        return 0
    fi

    # ---------- 停止服务与进程 ----------
    echo ""
    echo -e "${CYAN}停止 ToDesk 服务...${NC}"
    sudo systemctl stop todeskd.service 2>/dev/null || true
    sudo systemctl disable todeskd.service 2>/dev/null || true
    echo -e "${GREEN}✓ todeskd 服务已停止并禁用${NC}"
    # 卸载前先结束残留进程，否则 /opt/todesk 里的二进制被占用会让删除不干净
    sudo pkill -f '/opt/todesk/bin/' 2>/dev/null || true

    # ---------- 卸载 pacman 包 ----------
    if [ -n "$pkg_name" ]; then
        if ! ensure_writable; then return 1; fi
        echo ""
        echo -e "${CYAN}正在卸载 pacman 包 ${pkg_name} ...${NC}"
        if sudo pacman -R --noconfirm "$pkg_name"; then
            echo -e "${GREEN}✓ ${pkg_name} 已卸载${NC}"
        else
            echo -e "${RED}✗ 卸载 ${pkg_name} 失败，请检查上方 pacman 输出。${NC}"
            return 1
        fi
    fi

    # ---------- 清理残留目录 ----------
    # 手动解包安装（不经过 pacman）的设备，/opt/todesk 不在包数据库里，
    # pacman -R 不会删它，必须自己清掉，否则下次检测仍会判成「已安装」。
    if [ -d /opt/todesk ]; then
        if ! ensure_writable; then return 1; fi
        echo ""
        echo -e "${CYAN}清理 /opt/todesk 残留目录...${NC}"
        sudo rm -rf /opt/todesk 2>/dev/null || true
        if [ -d /opt/todesk ]; then
            echo -e "${YELLOW}⚠ /opt/todesk 未能完全删除，请手动执行: sudo rm -rf /opt/todesk${NC}"
        else
            echo -e "${GREEN}✓ /opt/todesk 已删除${NC}"
        fi
    fi
    sudo systemctl daemon-reload 2>/dev/null || true

    # ---------- 快捷方式与自启项 ----------
    # 桌面快捷方式、自启项都不是包内文件（pacman -R 不会删），
    # 连同旧方案遗留的两个「安装/重装」图标一起清掉。
    local f
    for f in "$DESKTOP_FILE" "$HOME/Desktop/todesk.desktop" \
             "$HOME/Desktop/install-todesk-service.desktop" \
             "$HOME/Desktop/reinstall-todesk-service.desktop" \
             "$AUTOSTART_FILE"; do
        if [ -e "$f" ]; then
            rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ 已删除 $f${NC}"
        fi
    done

    # ---------- 用户数据 ----------
    if [ -d "$USER_DATA_DIR" ]; then
        echo ""
        echo -e "${CYAN}是否删除 ToDesk 的配置和用户数据（$USER_DATA_DIR）？${NC}"
        echo -e "${YELLOW}删除后重装需要重新登录、重新配置设备列表。${NC}"
        read -n1 -p "按回车键或 A 键确认删除，其他键保留: " del_data < /dev/tty
        echo
        if [[ -z "$del_data" || "$del_data" =~ [Aa] ]]; then
            rm -rf "$USER_DATA_DIR" && echo -e "${GREEN}✓ 用户数据已删除${NC}"
        else
            echo -e "${YELLOW}已保留用户数据（$USER_DATA_DIR）。${NC}"
        fi
    fi

    # ---------- 结果确认 ----------
    echo ""
    if pacman -Q todesk-bin &>/dev/null || pacman -Q todesk &>/dev/null || [ -d /opt/todesk ]; then
        echo -e "${RED}✗ 卸载后仍检测到 ToDesk，请检查上方输出。${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ ToDesk 卸载完成${NC}"
}

update_installed_apps() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ 更新全部应用 ════════════════${NC}"
    echo ""

    # 为什么不用 flatpak update 一条命令搞定：
    # 先查更新这一步如果混在 update 里，用户要等整个流程开始才知道有没有更新。
    # 所以分开做：用 remote-ls 查更新（只刷新 summary，走镜像站，快）先列出来，
    # 再按需执行 update。
    # 另：flatpak update 默认并不刷新 appstream 元数据，只有显式加 --appstream 才会，
    # 所以这里无需额外跳过，也不会卡在「更新 appstream 数据」。

    # FIX-SOFTWARE: 区分「无更新 / 查询失败 / 超时」，不再把空输出当"全部最新"。
    echo -e "${CYAN}正在检查可用更新...${NC}"
    local updates="" check_rc=0 check_err="" check_tmp
    check_tmp="$(mktemp "$TEMP_DIR/flatpak_check.XXXXXX" 2>/dev/null)"
    updates=$(timeout 120 flatpak remote-ls --updates 2>"$check_tmp") || check_rc=$?
    [ -f "$check_tmp" ] && check_err="$(cat "$check_tmp")"
    rm -f "$check_tmp"

    if [ $check_rc -ne 0 ]; then
        if [ $check_rc -eq 124 ] || [ $check_rc -eq 137 ]; then
            echo -e "${RED}✗ 更新查询超时或被强制终止（rc=$check_rc），不作为「无更新」处理。${NC}"
        else
            echo -e "${RED}✗ 更新查询失败（rc=$check_rc）。${NC}"
            [ -n "$check_err" ] && echo -e "${YELLOW}  flatpak stderr: $(echo "$check_err" | head -3 | tr '\n' ' ')${NC}"
        fi
        echo -e "${YELLOW}  请检查网络后重试，或在「切换软件源」里换个镜像源。${NC}"
        return 1
    fi

    if [ -z "$updates" ]; then
        echo ""
        echo -e "${GREEN}✓ 查询成功且无待更新项：所有已安装应用均为最新版本。${NC}"
        return 0
    fi

    echo ""
    echo -e "${CYAN}以下应用可更新：${NC}"
    printf '%s\n' "$updates" | sed 's/^/  · /'
    echo ""

    # FIX-PROGRESS: 显示百分比与下载速度。
    # --noninteractive 会关掉进度输出，所以去掉它并设 FLATPAK_TTY_PROGRESS=1
    # 让 flatpak/ostree 输出「Receiving objects: NN% (...) X MB/s」；
    # 输出经 fp_progress_filter 把 \r 原地刷新转成逐行文本、清除 ANSI 与光标应答，
    # 既保留进度/速度，又不会重现之前的乱码。
    echo -e "${CYAN}开始更新（大包可能较慢，请耐心等待）...${NC}"
    echo -e "${CYAN}下方会实时显示下载百分比与速度${NC}"
    echo ""
    local rc=0
    # 用临时文件保存 flatpak 的真实退出码：管道里 $? 会是过滤器或 pipefail 的结果
    local _fp_status="${TEMP_DIR}/fp_update_status.$$"
    ( FLATPAK_TTY_PROGRESS=1 timeout 1200 flatpak update -y < /dev/null 2>&1; echo $? > "$_fp_status" ) \
        | fp_progress_filter
    if [ -f "$_fp_status" ]; then
        rc=$(cat "$_fp_status" 2>/dev/null || echo 1)
        rm -f "$_fp_status"
    else
        rc=1
    fi

    echo ""
    # FIX-SOFTWARE: rc=137/124 单列为超时/被杀，不再笼统"更新失败"。
    if [ $rc -eq 124 ] || [ $rc -eq 137 ]; then
        echo -e "${RED}✗ 更新超时或被强制终止（rc=$rc），已中止，不视为完成。${NC}"
        echo -e "${YELLOW}  已下载的部分不会丢失，可稍后重试或先切换软件源。${NC}"
        return 1
    elif [ $rc -ne 0 ]; then
        echo -e "${RED}✗ 更新失败（rc=$rc），请检查上方输出。${NC}"
        return 1
    fi

    # 复核：检查 returncode 与 stderr，复核失败不能报"全部完成"
    local left="" left_rc=0 left_err="" left_tmp
    left_tmp="$(mktemp "$TEMP_DIR/flatpak_recheck.XXXXXX" 2>/dev/null)"
    left=$(timeout 30 flatpak remote-ls --updates --cached 2>"$left_tmp") || left_rc=$?
    [ -f "$left_tmp" ] && left_err="$(cat "$left_tmp")"
    rm -f "$left_tmp"
    if [ $left_rc -ne 0 ]; then
        echo -e "${RED}✗ 复核更新结果失败（rc=$left_rc），不能确认更新已完成。${NC}"
        [ -n "$left_err" ] && echo -e "${YELLOW}  flatpak stderr: $(echo "$left_err" | head -3 | tr '\n' ' ')${NC}"
        return 1
    fi
    if [ -z "$left" ]; then
        echo -e "${GREEN}✓ 所有应用更新完成${NC}"
        return 0
    fi
    echo -e "${YELLOW}⚠ 更新命令已结束，但以下应用仍显示有更新：${NC}"
    printf '%s\n' "$left" | sed 's/^/  · /'
    echo -e "${YELLOW}  可能被跳过（如正在运行）或需要重启后再试。${NC}"
    return 1
}

install_yellow_duck_software() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装小黄鸭软件 ════════════════${NC}"
    echo ""
    # FIX-SOFTWARE: 失败一律 return 1（原来 return 默认 0，GUI 误报成功）。
    local LOSS_DIR="$HOME/.local/share/Steam/steamapps/common/Lossless Scaling"
    local STEAM_COMMON="$HOME/.local/share/Steam/steamapps/common"
    if [[ -d "$LOSS_DIR" ]]; then
        echo -e "${CYAN}检测到已安装小黄鸭软件。${NC}"
        echo "   安装目录: $LOSS_DIR"
        echo -e "${RED}警告：将删除整个目录，可能含用户数据，删除后无法恢复。${NC}"
        if ! confirm_action; then
            echo -e "${GREEN}已取消，未删除任何文件。${NC}"
            return 0
        fi
        if [ -L "$LOSS_DIR" ]; then
            echo -e "${RED}✗ 目标是符号链接，拒绝删除，请手动检查。${NC}"
            return 1
        fi
        echo "开始卸载小黄鸭软件..."
        if ! sudo rm -rf "$LOSS_DIR"; then
            echo -e "${RED}❌ 卸载失败，请检查权限。${NC}"
            return 1
        fi
        if [ -d "$LOSS_DIR" ]; then
            echo -e "${RED}❌ 目录仍存在，卸载未生效。${NC}"
            return 1
        fi
        echo -e "${GREEN}✅ 小黄鸭软件已成功卸载。${NC}"
        echo "如需重新安装，请再次运行此功能。"
        return 0
    fi

    echo -e "${CYAN}未检测到小黄鸭软件，开始从 Gitee 下载分卷文件...${NC}"
    if [ ! -d "$STEAM_COMMON" ]; then
        echo -e "${RED}✗ 目标目录不存在：$STEAM_COMMON，已中止。${NC}"
        return 1
    fi
    local DOWNLOAD_DIR
    DOWNLOAD_DIR="$(mktemp -d /tmp/lossless_scaling_download.XXXXXXXX 2>/dev/null)" || {
        echo -e "${RED}✗ 无法创建临时目录。${NC}"; return 1; }
    cd "$DOWNLOAD_DIR" || { rm -rf "$DOWNLOAD_DIR"; return 1; }

    local BASE_URL="https://gitee.com/Zhucy2100/app-backup/raw/master/Lossless%20Scaling/Lossless%20Scaling.zip"
    local failed=0
    for i in 001 002 003 004 005 006 007; do
        echo "正在下载 Lossless Scaling.zip.${i} ..."
        if ! curl -L --fail --connect-timeout 15 --max-time 180 -o "Lossless Scaling.zip.${i}" "${BASE_URL}.${i}"; then
            echo -e "${RED}下载 Lossless Scaling.zip.${i} 失败。${NC}"
            failed=1
            break
        fi
        if [ ! -s "Lossless Scaling.zip.${i}" ]; then
            echo -e "${RED}分卷 Lossless Scaling.zip.${i} 为空，疑似错误页。${NC}"
            failed=1
            break
        fi
    done

    if [ $failed -ne 0 ]; then
        echo -e "${RED}下载失败，请检查网络。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    echo "合并分卷文件并解压..."
    if ! cat "Lossless Scaling.zip".* > Lossless-Scaling-Combined.zip; then
        echo -e "${RED}✗ 合并分卷失败。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    # 解压前校验归档不含 ../ 或绝对路径，防止解压到 Steam common 之外
    if ! fs_archive_safe Lossless-Scaling-Combined.zip zip; then
        echo -e "${RED}✗ 归档包含 ../ 或绝对路径，拒绝解压（防目录穿越），已中止。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if ! unzip -o Lossless-Scaling-Combined.zip -d "$STEAM_COMMON/"; then
        echo -e "${RED}解压失败。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if [ ! -d "$LOSS_DIR" ]; then
        echo -e "${RED}✗ 解压后未找到目标目录 $LOSS_DIR，安装失败。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if ! sudo chown -R "${CURRENT_USER}:${CURRENT_GROUP}" "$LOSS_DIR"; then
        echo -e "${RED}✗ chown 失败，安装未正确完成。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
    echo -e "${GREEN}✅ 小黄鸭软件安装完成！${NC}"
    return 0
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

    # FIX-SOFTWARE: --fail/超时 + 校验 PE 头，不把 HTML 错误页交给 Proton。
    echo -e "${CYAN}正在下载育碧安装程序...${NC}"
    cd "$HOME" || return
    rm -f UbisoftConnectInstaller.exe
    if ! curl -# -L --fail --connect-timeout 15 --max-time 300 -o UbisoftConnectInstaller.exe "https://ubistatic3-a.akamaihd.net/orbit/launcher_installer/UbisoftConnectInstaller.exe"; then
        echo -e "${RED}下载失败，请检查网络。${NC}"
        rm -f UbisoftConnectInstaller.exe
        return 1
    fi
    if ! fs_verify_installer UbisoftConnectInstaller.exe mz; then
        echo -e "${RED}✗ 下载内容不是有效的 PE 安装程序（文件过小或为 HTML 错误页），已中止。${NC}"
        rm -f UbisoftConnectInstaller.exe
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
    # FIX-SOFTWARE: 检查 Proton 退出码，失败不再继续"等待安装完成"。
    if ! "$PROTON_BIN" waitforexitandrun \
        "$HOME/UbisoftConnectInstaller.exe" /S; then
        echo -e "${RED}✗ Proton 运行安装程序失败（返回非 0），请检查 Proton 环境或日志。${NC}"
        return 1
    fi

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

    local EXE_PATH="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/UbisoftConnect.exe"
    # FIX-SOFTWARE: 除目录存在外，还验证目标 exe 出现，不把空目录当安装成功。
    if [ -d "$UBISOFT_DIR" ] && [ -f "$EXE_PATH" ]; then
        echo -e "${GREEN}✓ 育碧平台安装成功！${NC}"

        echo -e "${CYAN}正在添加到 Steam 库...${NC}"
        # FIX-SOFTWARE: 先确认工具存在，避免命令缺失时误判为"已添加"
        if ! command -v steamos-add-to-steam >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠ 未找到 steamos-add-to-steam，跳过自动添加，请手动在 Steam 库添加该 exe。${NC}"
        else
            steamos-add-to-steam "$EXE_PATH"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 已添加 Steam 快捷方式。${NC}"
            echo -e "${YELLOW}请手动在 Steam 库中为该快捷方式设置兼容层为 Proton Experimental。${NC}"
            echo -e "${YELLOW}或者点击桌面快捷方式运行。${NC}"
        else
            echo -e "${YELLOW}⚠️ 自动添加到 Steam 失败，请手动添加该 exe 文件。${NC}"
        fi
        fi  # FIX-SOFTWARE: add_to_steam guard end

        local ICON_PATH=""
        echo -e "${CYAN}正在从 exe 提取图标...${NC}"
        ICON_PATH=$(extract_exe_icon "$EXE_PATH")
        if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
            echo -e "${GREEN}✓ 图标已提取: $ICON_PATH${NC}"
        else
            ICON_PATH="applications-games"
            echo -e "${YELLOW}⚠️ 图标提取失败，使用系统游戏图标。${NC}"
        fi

        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        local DESKTOP_FILE="$DESKTOP_DIR/Ubisoft Connect.desktop"
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

    # FIX-SOFTWARE: --fail/超时 + 校验 MSI(OLE2) 头，不把 HTML 错误页交给 Proton。
    echo -e "${CYAN}正在下载 Epic 安装程序...${NC}"
    cd "$HOME" || return
    rm -f EpicGamesLauncherInstaller.msi
    if ! wget --connect-timeout=15 --timeout=300 --tries=1 -O EpicGamesLauncherInstaller.msi "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi"; then
        echo -e "${RED}下载失败，请检查网络。${NC}"
        rm -f EpicGamesLauncherInstaller.msi
        return 1
    fi
    if ! fs_verify_installer EpicGamesLauncherInstaller.msi msi; then
        echo -e "${RED}✗ 下载内容不是有效的 MSI 安装程序（文件过小或为 HTML 错误页），已中止。${NC}"
        rm -f EpicGamesLauncherInstaller.msi
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
    # FIX-SOFTWARE: Epic MSI 用显式 msiexec /i ... /quiet 经 Proton 运行，并检查退出码。
    if ! "$PROTON_BIN" waitforexitandrun \
        msiexec /i "Z:\\home\\deck\\EpicGamesLauncherInstaller.msi" /quiet /log "$MSI_LOG"; then
        echo -e "${RED}✗ Proton 运行 msiexec 失败（返回非 0），请检查日志：${MSI_LOG}${NC}"
        return 1
    fi

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

    local EXE_PATH="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games/Launcher/Portal/Binaries/Win64/EpicGamesLauncher.exe"
    # FIX-SOFTWARE: 除目录存在外，还验证目标 exe 出现。
    if [ -d "$EPIC_DIR" ] && [ -f "$EXE_PATH" ]; then
        echo -e "${GREEN}✓ Epic平台安装成功！${NC}"

        echo -e "${CYAN}正在添加到 Steam 库...${NC}"
        # FIX-SOFTWARE: 先确认工具存在，避免命令缺失时误判为"已添加"
        if ! command -v steamos-add-to-steam >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠ 未找到 steamos-add-to-steam，跳过自动添加，请手动在 Steam 库添加该 exe。${NC}"
        else
            steamos-add-to-steam "$EXE_PATH"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 已添加 Steam 快捷方式。${NC}"
            echo -e "${YELLOW}请手动在 Steam 库中为该快捷方式设置兼容层为 Proton Experimental。${NC}"
            echo -e "${YELLOW}或者点击桌面快捷方式运行。${NC}"
        else
            echo -e "${YELLOW}⚠️ 自动添加到 Steam 失败，请手动添加该 exe 文件。${NC}"
        fi
        fi  # FIX-SOFTWARE: add_to_steam guard end

        local ICON_PATH=""
        echo -e "${CYAN}正在从 exe 提取图标...${NC}"
        ICON_PATH=$(extract_exe_icon "$EXE_PATH")
        if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
            echo -e "${GREEN}✓ 图标已提取: $ICON_PATH${NC}"
        else
            ICON_PATH="applications-games"
            echo -e "${YELLOW}⚠️ 图标提取失败，使用系统游戏图标。${NC}"
        fi

        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        local DESKTOP_FILE="$DESKTOP_DIR/Epic Games Launcher.desktop"
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
        # FIX-SOFTWARE: 关键下载加 connect/max-time 超时。
        if ! curl -L --fail --connect-timeout 15 --max-time 180 --retry 2 \
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
    local BN_TARGET="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)"
    if ! mkdir -p "$BN_TARGET"; then
        echo -e "${RED}✗ 创建目标目录失败。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    # 解压前校验归档不含 ../ 或绝对路径
    if ! fs_archive_safe Battle.net_backup.tar.xz tar; then
        echo -e "${RED}✗ 归档包含 ../ 或绝对路径，拒绝解压（防目录穿越），已中止。${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if ! tar -xJf Battle.net_backup.tar.xz -C "$BN_TARGET/"; then
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
    if ! command -v steamos-add-to-steam >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ 未找到 steamos-add-to-steam，跳过自动添加，请手动添加该 exe。${NC}"
    else
        steamos-add-to-steam "$EXE_PATH"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 已添加 Steam 快捷方式。${NC}"
        echo -e "${YELLOW}请手动在 Steam 库中为该快捷方式设置兼容层为 Proton Experimental。${NC}"
        echo -e "${YELLOW}或者点击桌面快捷方式运行。${NC}"
    else
        echo -e "${YELLOW}⚠️ 自动添加到 Steam 失败，请手动添加该 exe 文件。${NC}"
    fi
    fi  # FIX-SOFTWARE: bn add_to_steam guard end

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
    # FIX-SOFTWARE: 增加「取消/返回」项；/dev/tty EOF 不死循环。
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}═══════════ 卸载第三方游戏平台 ═══════════${NC}"
        echo ""
        local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
        local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
        local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
        local ubisoft_installed=false epic_installed=false battle_installed=false
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
        echo "  0) 取消 / 返回（不卸载）"
        local choice=""
        if ! read -r -p "请输入 [0-3]（回车=取消）: " choice < /dev/tty; then
            echo -e "${GREEN}已取消，未做任何改动。${NC}"
            return 0
        fi
        case "$choice" in
            1) uninstall_ubisoft; return $? ;;
            2) uninstall_epic; return $? ;;
            3) uninstall_battle_net; return $? ;;
            ""|0) echo -e "${GREEN}已取消，未做任何改动。${NC}"; return 0 ;;
            *) echo -e "${RED}无效选项 请重新输入${NC}"; sleep 0.5 ;;
        esac
    done
}

uninstall_ubisoft() {
    # FIX-SOFTWARE: 明确列出删除路径 + 二次确认 + symlink 检查 + 卸载器失败不报成功。
    local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local DESKTOP_FILE="$DESKTOP_DIR/Ubisoft Connect.desktop"
    if [ ! -d "$UBISOFT_DIR" ]; then
        echo -e "${YELLOW}未检测到育碧平台，无需卸载。${NC}"
        return 0
    fi

    echo -e "${CYAN}将删除以下路径：${NC}"
    local p
    for p in "$@"; do
        [ -e "$p" ] || [ -L "$p" ] || continue
        if [ -L "$p" ]; then
            echo -e "${RED}  ✗ $p 是符号链接，拒绝删除，请先手动检查。${NC}"
            return 1
        fi
        echo -e "${YELLOW}  · $p${NC}"
    done
    echo -e "${RED}警告：以上目录可能含已安装游戏、存档和用户数据，删除后无法恢复！${NC}"
    echo -e "${YELLOW}建议先确认没有正在运行的该平台/游戏进程。${NC}"
    if pgrep -f 'third-party-game-platform' >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ 检测到可能仍在运行的平台/游戏进程，建议先退出再删除。${NC}"
    fi
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}已取消，未删除任何文件。${NC}"
        return 0
    fi

    local uninstaller="$UBISOFT_DIR/Ubisoft Game Launcher/Uninstall.exe"
    local uninstaller_ok=false
    if [ -f "$uninstaller" ]; then
        echo -e "${CYAN}正在执行育碧官方卸载程序...${NC}"
        export STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform"
        export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"
        local PROTON_BIN="$HOME/.steam/root/steamapps/common/Proton - Experimental/proton"
        if [ -x "$PROTON_BIN" ] && "$PROTON_BIN" waitforexitandrun "$uninstaller" /S; then
            uninstaller_ok=true
            echo -e "${GREEN}✓ 官方卸载程序执行成功。${NC}"
        else
            echo -e "${YELLOW}⚠ 未找到 Proton 或官方卸载程序执行失败，将仅删除目录（不视为完全成功）。${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ 未找到官方卸载程序，将仅删除目录。${NC}"
    fi

    local fail=0
    if ! rm -rf "$UBISOFT_DIR"; then
        echo -e "${RED}✗ 删除目录失败：$UBISOFT_DIR${NC}"
        fail=1
    elif [ -d "$UBISOFT_DIR" ]; then
        echo -e "${RED}✗ 目录仍存在，删除未生效：$UBISOFT_DIR${NC}"
        fail=1
    else
        echo -e "${GREEN}✓ 育碧平台目录已删除${NC}"
    fi

    # 只有卸载器成功且目录删除成功，才清理桌面并报成功
    if [ "$fail" -eq 0 ] && $uninstaller_ok; then
        if [ -f "$DESKTOP_FILE" ]; then
            if rm -f "$DESKTOP_FILE"; then
                echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
            else
                echo -e "${RED}✗ 删除桌面快捷方式失败${NC}"
                fail=1
            fi
        fi
    elif [ "$fail" -eq 0 ]; then
        echo -e "${RED}✗ 官方卸载程序未成功完成，保留桌面快捷方式，请手动确认后再清理。${NC}"
        fail=1
    fi

    echo ""
    echo -e "${YELLOW}请手动在 Steam 库中删除对应的非 Steam 游戏快捷方式（右键→管理→从您的库中删除非 Steam 游戏）。${NC}"
    [ "$fail" -eq 0 ] || return 1
    echo -e "${GREEN}✓ 育碧平台已成功卸载。${NC}"
    return 0
}

uninstall_epic() {
    # FIX-SOFTWARE: 二次确认 + symlink 检查 + rm 失败 return 1。
    local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
    local EPIC_DIR_X86="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Epic Games"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local DESKTOP_FILE="$DESKTOP_DIR/Epic Games Launcher.desktop"
    if [ ! -d "$EPIC_DIR" ] && [ ! -d "$EPIC_DIR_X86" ]; then
        echo -e "${YELLOW}未检测到 Epic 平台，无需卸载。${NC}"
        return 0
    fi

    echo -e "${CYAN}将删除以下路径：${NC}"
    local p
    for p in "$@"; do
        [ -e "$p" ] || [ -L "$p" ] || continue
        if [ -L "$p" ]; then
            echo -e "${RED}  ✗ $p 是符号链接，拒绝删除，请先手动检查。${NC}"
            return 1
        fi
        echo -e "${YELLOW}  · $p${NC}"
    done
    echo -e "${RED}警告：以上目录可能含已安装游戏、存档和用户数据，删除后无法恢复！${NC}"
    echo -e "${YELLOW}建议先确认没有正在运行的该平台/游戏进程。${NC}"
    if pgrep -f 'third-party-game-platform' >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ 检测到可能仍在运行的平台/游戏进程，建议先退出再删除。${NC}"
    fi
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}已取消，未删除任何文件。${NC}"
        return 0
    fi

    local fail=0 d
    for d in "$EPIC_DIR" "$EPIC_DIR_X86"; do
        [ -d "$d" ] || continue
        if ! rm -rf "$d"; then
            echo -e "${RED}✗ 删除失败：$d${NC}"
            fail=1
        elif [ -d "$d" ]; then
            echo -e "${RED}✗ 目录仍存在：$d${NC}"
            fail=1
        else
            echo -e "${GREEN}✓ 已删除：$d${NC}"
        fi
    done
    if [ -f "$DESKTOP_FILE" ]; then
        if rm -f "$DESKTOP_FILE"; then
            echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
        else
            echo -e "${RED}✗ 删除桌面快捷方式失败${NC}"
            fail=1
        fi
    fi
    echo ""
    echo -e "${YELLOW}请手动在 Steam 库中删除对应的非 Steam 游戏快捷方式。${NC}"
    [ "$fail" -eq 0 ] || return 1
    echo -e "${GREEN}✓ Epic 平台已卸载。${NC}"
    return 0
}

uninstall_battle_net() {
    # FIX-SOFTWARE: 二次确认 + symlink 检查 + rm 失败 return 1。
    local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local DESKTOP_FILE="$DESKTOP_DIR/Battle.net.desktop"
    if [ ! -d "$BATTLE_DIR" ]; then
        echo -e "${YELLOW}未检测到战网平台，无需卸载。${NC}"
        return 0
    fi

    echo -e "${CYAN}将删除以下路径：${NC}"
    local p
    for p in "$@"; do
        [ -e "$p" ] || [ -L "$p" ] || continue
        if [ -L "$p" ]; then
            echo -e "${RED}  ✗ $p 是符号链接，拒绝删除，请先手动检查。${NC}"
            return 1
        fi
        echo -e "${YELLOW}  · $p${NC}"
    done
    echo -e "${RED}警告：以上目录可能含已安装游戏、存档和用户数据，删除后无法恢复！${NC}"
    echo -e "${YELLOW}建议先确认没有正在运行的该平台/游戏进程。${NC}"
    if pgrep -f 'third-party-game-platform' >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ 检测到可能仍在运行的平台/游戏进程，建议先退出再删除。${NC}"
    fi
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}已取消，未删除任何文件。${NC}"
        return 0
    fi

    local fail=0
    if ! rm -rf "$BATTLE_DIR"; then
        echo -e "${RED}✗ 删除目录失败：$BATTLE_DIR${NC}"
        fail=1
    elif [ -d "$BATTLE_DIR" ]; then
        echo -e "${RED}✗ 目录仍存在：$BATTLE_DIR${NC}"
        fail=1
    else
        echo -e "${GREEN}✓ 战网平台目录已删除${NC}"
    fi
    if [ -f "$DESKTOP_FILE" ]; then
        if rm -f "$DESKTOP_FILE"; then
            echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
        else
            echo -e "${RED}✗ 删除桌面快捷方式失败${NC}"
            fail=1
        fi
    fi
    echo ""
    echo -e "${YELLOW}请手动在 Steam 库中删除对应的非 Steam 游戏快捷方式。${NC}"
    [ "$fail" -eq 0 ] || return 1
    echo -e "${GREEN}✓ 战网平台已成功卸载。${NC}"
    return 0
}

if [ -n "${1:-}" ] && declare -f "$1" > /dev/null; then
    "$@"
else
    echo "此脚本为内嵌库，请通过参数调用具体功能。"
fi
'''

BASH_SCRIPT_EN = r'''#!/bin/bash
set -uo pipefail
# FIX-SOFTWARE: avoid predictable shared /tmp path (symlink/TOCTOU).
TEMP_DIR="$(mktemp -d /tmp/steamdeck_toolbox.XXXXXXXX 2>/dev/null || echo /tmp/steamdeck_toolbox)"
cleanup_temp() { rm -rf "$TEMP_DIR" 2>/dev/null; }
# SteamOS read-only mode: automatically restore when the script exits (sudo -n non-interactive, to avoid hanging on a password prompt)
# Key point: only restore when the script itself disabled read-only mode.
# Otherwise, if the user manually set the system to writable (disabled), running any function would force it back to
# enabled on exit, overriding the user's own setting.
RO_READONLY_DISABLED_BY_US=0
restore_readonly() {
    command -v steamos-readonly &>/dev/null || return 0
    # 脚本没动过只读开关 → 保持用户原状，绝不擅自 enable
    [ "${RO_READONLY_DISABLED_BY_US:-0}" -eq 1 ] || return 0
    if sudo -n steamos-readonly status 2>/dev/null | grep -q "disabled"; then
        if sudo -n steamos-readonly enable 2>/dev/null; then
            echo -e "${GREEN}✓ Read-only mode restored${NC}"
        else
            echo -e "${YELLOW}⚠ Cannot restore read-only mode automatically, please run manually: sudo steamos-readonly enable${NC}"
        fi
    fi
    return 0
}
trap 'ec=$?; restore_readonly; cleanup_temp; exit $ec' EXIT
# INT/TERM = user clicked Cancel: use dedicated exit code 75 so TaskWindow can
# distinguish "cancelled" from "success(0)". EXIT trap keeps the real code via ec=$?.
CANCEL_EXIT_CODE_EN_OK=75
trap 'echo -e "\n${YELLOW}User cancelled the operation, closing window.${NC}"; exit 75' INT TERM

PYTHON_CMD="python3"
command -v python3 &>/dev/null || PYTHON_CMD="python"
# 当前用户名/组：不能硬编码 deck，非 deck 用户名的设备会把文件属主改错
CURRENT_USER="${USER:-$(id -un)}"
CURRENT_GROUP="$(id -gn "$CURRENT_USER" 2>/dev/null || echo "$CURRENT_USER")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'; NC='\033[0m'

# ===== FIX-SOFTWARE: shared safe helpers =====
# Resolve the real Desktop dir (XDG) and make sure it exists.
fs_desktop_dir() {
    local d=""
    if command -v xdg-user-dir >/dev/null 2>&1; then
        d="$(xdg-user-dir DESKTOP 2>/dev/null)"
    fi
    [ -n "$d" ] && [ "$d" != "$HOME" ] || d="${XDG_DESKTOP_DIR:-$HOME/Desktop}"
    mkdir -p "$d" 2>/dev/null || d="$HOME/Desktop"
    printf '%s' "$d"
}
# curl with hard fail/timeouts; download to a temp file; verify it is a non-trivial,
# non-HTML shell text before anything gets executed.
# usage: fs_fetch_shell URL TMPFILE  -> 0 ok, 1 fail (TMPFILE cleaned on failure)
fs_fetch_shell() {
    local url="$1" out="$2" rc=0
    rm -f "$out"
    curl -fsSL --connect-timeout 15 --max-time 120 -o "$out" "$url" || rc=$?
    # FIX-QIYOU: 有些厂商的安装域名只开了 80 端口、没开 443（例如 sd.qiyou.cn）。
    # HTTPS 连接失败时自动退回 HTTP，并通过下面的内容校验；同时明确告知用户
    # 正在使用明文连接，让用户自己决定是否继续以 root 执行。
    if [ "$rc" -ne 0 ] && [ "${url#https://}" != "$url" ]; then
        local http_url="http://${url#https://}" rc2=0
        echo -e "${YELLOW}⚠️  HTTPS 连接失败，尝试改用 HTTP 明文连接: $http_url${NC}"
        echo -e "${YELLOW}   明文连接无法验证对方身份，请确认来源可信后再继续。${NC}"
        curl -fsSL --connect-timeout 15 --max-time 120 -o "$out" "$http_url" || rc2=$?
        if [ "$rc2" -eq 0 ]; then rc=0; url="$http_url"; fi
    fi
    if [ "$rc" -ne 0 ]; then
        rm -f "$out"; return 1
    fi
    if [ ! -s "$out" ]; then
        rm -f "$out"; return 1
    fi
    # Reject obvious HTML error / login pages (case-insensitive, first 4KB).
    if head -c 4096 "$out" | grep -qiE '<!doctype[[:space:]]+html|<html([[:space:]>])|<head([[:space:]>])|<title>'; then
        rm -f "$out"; return 1
    fi
    # Must look like a shell script: shebang, or shell keywords / parameter expansion.
    if ! grep -qE '(^#!.*(/|env )?(ba)?sh|^#!/bin/(ba)?sh|\b(sudo|apt|pacman|systemctl|echo|set|if|then|fi|for|while|curl|wget|mkdir|cp|mv|rm|cat|chmod|chown)\b|\$\(|`|#.*)' "$out"; then
        rm -f "$out"; return 1
    fi
    return 0
}
# Compare dotted version strings: returns 0 if $1 > $2, 1 otherwise (equal/less/invalid).
fs_ver_gt() {
    local a="$1" b="$2" i av bv
    [ -n "$a" ] && [ -n "$b" ] || return 1
    IFS='.' read -ra A <<< "$a"; IFS='.' read -ra B <<< "$b"
    for i in "${!A[@]}"; do
        av="${A[$i]}"; bv="${B[$i]:-0}"
        [[ "$av" =~ ^[0-9]+$ ]] || av=0
        [[ "$bv" =~ ^[0-9]+$ ]] || bv=0
        if [ "$((10#$av))" -gt "$((10#$bv))" ]; then return 0; fi
        if [ "$((10#$av))" -lt "$((10#$bv))" ]; then return 1; fi
    done
    return 1
}
# FIX-PROGRESS: 把 flatpak/ostree 用 \r 原地刷新的进度条转成干净的逐行文本，
# 保留「Receiving objects: NN% ... X MB/s」这类含百分比与速度的行。
# --noninteractive 会关闭进度输出，所以更新命令要去掉它并设 FLATPAK_TTY_PROGRESS=1；
# 本过滤器负责清除 ANSI 控制符与光标位置应答，避免再次出现乱码。
fp_progress_filter() {
    "${PYTHON_CMD:-python3}" -u -c '
import sys, re
ansi = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*(?:\x07|\x1b\\)|\x1b[@-Z\\\\-_]")
# 属于「同一条进度行」的帧：X/Y 步骤、百分比、速度、进度条、正在更新/正在安装
prog = re.compile(r"\d+/\d+|\d+%|\d+\s*(?:字节|bytes|B|kB|MB|GB)/s|[█▍▌▊▏▎▋▐░]|正在更新|正在安装|Receiving objects")
def clean(t):
    t = ansi.sub("", t)
    t = re.sub(r"\^\[\[[0-9;]*R", "", t)
    return t.strip()
buf = b""
active = False
def emit_progress(t):
    # 回车 + 清到行尾：始终覆盖同一行，不换行，视觉上只显示一行
    global active
    sys.stdout.write("\r\033[K" + t)
    sys.stdout.flush()
    active = True
def emit_log(t):
    global active
    if active:
        sys.stdout.write("\n")
        active = False
    print(t, flush=True)
while True:
    ch = sys.stdin.buffer.read(1)
    if not ch:
        break
    if ch[0] in (13, 10):
        t = clean(buf.decode("utf-8", "replace"))
        buf = b""
        if not t:
            continue
        (emit_progress if prog.search(t) else emit_log)(t)
    else:
        buf += ch
if buf:
    t = clean(buf.decode("utf-8", "replace"))
    if t:
        (emit_progress if prog.search(t) else emit_log)(t)
if active:
    sys.stdout.write("\n")
    sys.stdout.flush()
' 2>/dev/null
}

# Verify a downloaded Windows installer is not an HTML error page.
# usage: fs_verify_installer FILE mz|msi
fs_verify_installer() {
    local f="$1" kind="$2" sz
    [ -f "$f" ] || return 1
    sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
    [ "$sz" -ge 65536 ] || return 1
    if head -c 4096 "$f" | grep -qiE '<!doctype[[:space:]]+html|<html([[:space:]>])|<head([[:space:]>])|<title>'; then
        return 1
    fi
    if [ "$kind" = "mz" ]; then
        [ "$(head -c 2 "$f")" = "MZ" ] || return 1
        if command -v file >/dev/null 2>&1; then
            file "$f" | grep -qiE 'PE32|MS-DOS|executable' || return 1
        fi
    else
        # MSI is an OLE2 compound file: D0 CF 11 E0 A1 B1 1A E1
        [ "$(head -c 8 "$f" | od -An -tx1 | tr -d ' \n')" = "d0cf11e0a1b11ae1" ] || return 1
    fi
    return 0
}
# Reject tar/zip archives containing path traversal or absolute paths.
# usage: fs_archive_safe ARCHIVE tar|zip
fs_archive_safe() {
    local f="$1" kind="$2" line
    if [ "$kind" = "tar" ]; then
        line=$(tar -tf "$f" 2>/dev/null | grep -E '(^/|(^|/)\.\./)' | head -1)
    else
        line=$(unzip -Z1 "$f" 2>/dev/null | grep -E '(^/|(^|/)\.\./)' | head -1)
    fi
    if [ -n "$line" ]; then
        return 1
    fi
    return 0
}
# ===== END FIX-SOFTWARE shared helpers =====

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
    "gh-proxy.com (China mirror, fast)"
    "gh.3w.pm (China mirror, stable)"
    "cors.isteed.cc (China mirror, stable)"
    "ghproxy.net (China mirror, slow fallback)"
    "GitHub (official)"
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

# Mirror download with zip integrity verification (reuses the global MIRRORS)
download_zip_with_mirrors() {
    local url="$1" output="$2" desc="${3:-ZIP file}"
    while true; do
        clear
        echo -e "${CYAN}Downloading ${desc}${NC}\n"
        echo "Please choose a download mirror (enter a number, 0 to cancel):"
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRROR_LABELS[$i]:-${MIRRORS[$i]}}"
        done
        read -p "Enter your choice: " choice < /dev/tty
        [[ -z "$choice" ]] && echo -e "${RED}Invalid input${NC}" && sleep 1 && continue
        [[ "$choice" == "0" ]] && echo "Operation cancelled." && return 1
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            local mirror="${MIRRORS[$((choice-1))]}"
            local full_url="${mirror}${url}"
            echo -e "Trying to download from ${MIRROR_LABELS[$((choice-1))]:-${mirror}} ..."
            if curl -L --progress-bar -f -o "$output" "$full_url" && [ -s "$output" ] && unzip -t "$output" &>/dev/null; then
                echo -e "${GREEN}Download successful, file is complete.${NC}"
                return 0
            fi
            echo -e "${RED}Download failed or the file is incomplete, please choose another mirror.${NC}"
            rm -f "$output"; sleep 1
        else
            echo -e "${RED}Invalid number.${NC}"; sleep 1
        fi
    done
}

mk_temp_dir() { mkdir -p "$TEMP_DIR"; }

confirm_action() {
    # FIX-SOFTWARE: treat /dev/tty EOF as "cancel" so a failed read
    # cannot reuse a stale value or spin the menu forever.
    local confirm=""
    read -r -n1 -p "Press Enter or A to confirm, any other key to cancel: " confirm < /dev/tty || { echo; return 1; }
    echo
    [[ -z "$confirm" || "$confirm" =~ [Aa] ]]
}

disable_readonly() {
    if command -v steamos-readonly &>/dev/null; then
        if sudo steamos-readonly disable 2>/dev/null; then
            # Record that "read-only was turned off by the script" so the exit trap restores it, without overriding the user's own setting
            RO_READONLY_DISABLED_BY_US=1
            echo -e "${GREEN}✓ Read-only mode disabled${NC}"
        else
            echo -e "${RED}✗ Failed to disable read-only mode, operation aborted.${NC}"
            return 1
        fi
    fi
    return 0
}

ensure_writable() {
    command -v steamos-readonly &>/dev/null || return 0
    if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
        if sudo steamos-readonly disable 2>/dev/null; then
            RO_READONLY_DISABLED_BY_US=1
            echo -e "${GREEN}✓ Read-only mode disabled${NC}"
        else
            echo -e "${RED}✗ Failed to disable read-only mode, operation aborted.${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✓ Read-only mode is already writable${NC}"
    fi
    return 0
}

download_with_mirrors() {
    local url="$1" output="$2" desc="${3:-file}"
    while true; do
        clear
        echo -e "${CYAN}Downloading ${desc}${NC}\n"
        echo "Please choose a download mirror (enter a number, 0 to cancel):"
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRROR_LABELS[$i]:-${MIRRORS[$i]}}"
        done
        read -p "Enter your choice: " choice < /dev/tty
        [[ -z "$choice" ]] && echo -e "${RED}Invalid input${NC}" && sleep 1 && continue
        [[ "$choice" == "0" ]] && echo "Operation cancelled." && return 1
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            local mirror="${MIRRORS[$((choice-1))]}"
            local full_url="${mirror}${url}"
            echo -e "Trying to download from ${MIRROR_LABELS[$((choice-1))]:-${mirror}} ..."
            if curl -L --progress-bar -f -o "$output" "$full_url" && [ -s "$output" ]; then
                echo -e "${GREEN}Download successful.${NC}"
                return 0
            fi
            echo -e "${RED}Download failed, please choose another mirror.${NC}"
            rm -f "$output"; sleep 1
        else
            echo -e "${RED}Invalid number.${NC}"; sleep 1
        fi
    done
}

install_chinese_source() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════ Switch Flatpak software source ════════════${NC}"
    echo "You can switch to a China mirror for speed, or restore the official source."
    echo ""
    # 不需要禁用 SteamOS 只读模式：flatpak remote 配置在 /var/lib/flatpak（可写分区），
    # 与只读的根分区无关。原实现先 disable_readonly 属于多余操作，还会顺手改掉系统只读状态。
    echo -e "${CYAN}Step 1: check flatpak environment${NC}"
    if ! command -v flatpak &>/dev/null; then
        echo -e "${RED}✗ flatpak command not found; cannot configure mirrors.${NC}"
        return 1
    fi
    if ! flatpak remotes --columns=name 2>/dev/null | grep -qx "flathub"; then
        echo -e "${YELLOW}⚠ No flathub remote found; adding the official URL...${NC}"
        if ! sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null; then
            echo -e "${RED}✗ Failed to add flathub; aborted.${NC}"
            return 1
        fi
    fi
    echo -e "${GREEN}✓ flatpak environment OK${NC}"
    echo ""
    echo -e "${CYAN}Step 2: choose Flatpak software source${NC}"
    echo ""

    # 实测（2026-10，逐个探测 summary.idx 魔数确认是否为真实 ostree 数据）：
    #   ✓ 可用：
    #     mirrors.ustc.edu.cn/flathub            中科大（yadex 增量方案），已验证
    #     unicom.mirrors.ustc.edu.cn/flathub     中科大联通节点
    #     mobile.mirrors.ustc.edu.cn/flathub     中科大移动节点
    #     mirrors.cernet.edu.cn/flathub          CERNET 聚合入口（按地理位置分发到各校节点）
    #   ✗ 不可用（保留记录，避免以后又踩）：
    #     mirror.sjtu.edu.cn/flathub   → 301 跳回官方 dl.flathub.org，等于没加速
    #     mirrors.nju / sustech / bfsu / tuna / aliyun / tencent / huawei / zju / jlu /
    #     iscas / xjtu / scau / qlu 的 flathub → 返回 HTML 首页或 404，没有这个镜像
    #
    # 所有国内镜像都只是 Flathub 的「缓存」而不是完整镜像：
    # 未命中的对象会 302 回 dl.flathub.org，所以官方站仍需要基本连通性。
    local MIRROR_LABELS=(
        "USTC"
        "USTC - China Unicom node"
        "USTC - China Mobile node"
        "CERNET education network aggregate"
        "Restore official source (dl.flathub.org)"
    )
    local MIRROR_URLS=(
        "https://mirrors.ustc.edu.cn/flathub/"
        "https://unicom.mirrors.ustc.edu.cn/flathub/"
        "https://mobile.mirrors.ustc.edu.cn/flathub/"
        "https://mirrors.cernet.edu.cn/flathub/"
        "https://dl.flathub.org/repo/"
    )

    # Show the current source: display its name when it matches one of the 5 presets, otherwise the raw URL
    local FP_OLD_URL FP_CURRENT_LABEL="" FP_NORM_OLD FP_NORM_URL mi
    FP_OLD_URL=$(flatpak remotes --columns=name,url 2>/dev/null | awk '$1 == "flathub" {print $2; exit}')
    if [ -n "$FP_OLD_URL" ]; then
        # Normalise before comparing: strip the trailing slash and lowercase, so a
        # difference in just the slash or case does not make the match fail.
        FP_NORM_OLD=$(echo "$FP_OLD_URL" | tr '[:upper:]' '[:lower:]' | sed 's#/*$##')
        for mi in "${!MIRROR_URLS[@]}"; do
            FP_NORM_URL=$(echo "${MIRROR_URLS[$mi]}" | tr '[:upper:]' '[:lower:]' | sed 's#/*$##')
            if [ "$FP_NORM_OLD" = "$FP_NORM_URL" ]; then
                FP_CURRENT_LABEL="${MIRROR_LABELS[$mi]}"
                break
            fi
        done
        if [ -n "$FP_CURRENT_LABEL" ]; then
            echo -e "Current flathub source: ${GREEN}${FP_CURRENT_LABEL}${NC}"
            echo -e "  URL: ${CYAN}${FP_OLD_URL}${NC}"
        else
            echo -e "Current flathub source: ${CYAN}${FP_OLD_URL}${NC}"
            echo -e "${YELLOW}  (this URL is not one of the 5 preset sources)${NC}"
        fi
        echo ""
    fi

    echo "Please choose a software source (China mirrors are faster; official needs access to dl.flathub.org):"
    local i
    for i in "${!MIRROR_LABELS[@]}"; do
        echo "  $((i+1)). ${MIRROR_LABELS[$i]}"
    done
    echo ""
    local choice
    while true; do
        read -p "Enter number [1-${#MIRROR_LABELS[@]}] (Enter to cancel): " choice < /dev/tty || { echo "Operation cancelled."; return 0; }
        [ -z "$choice" ] && { echo "Operation cancelled."; return 0; }
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRROR_LABELS[@]} ]; then
            break
        fi
        echo -e "${RED}Invalid input; enter a number between 1 and ${#MIRROR_LABELS[@]}.${NC}"
    done

    local FP_MIRROR="${MIRROR_URLS[$((choice-1))]}"
    local FP_MIRROR_NAME="${MIRROR_LABELS[$((choice-1))]}"
    echo ""
    echo -e "${CYAN}Selected: ${FP_MIRROR_NAME}${NC}"
    echo "  URL: $FP_MIRROR"

    local FP_KEY_TMP="${TEMP_DIR}/flathub.gpg"

    # 先确认 sudo 可用：系统级 flatpak remote 配置需要 root，
    # 若这里不先验证，后面 remote-modify 会卡在密码提示上（输出被 2>/dev/null 吞掉，看起来像无响应）
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}✗ sudo is required to modify Flatpak remotes; aborted.${NC}"
        return 1
    fi

    # 1) 确保 flathub 签名公钥存在（镜像的摘要带 flathub 签名，缺公钥会被拒绝）
    #
    # 关键在于：公钥是「装一次就长期有效」的东西，正常设备上早就有了，
    # 不需要每次切源都从 dl.flathub.org 重新下一遍。以前每次无条件下载，
    # 而 dl.flathub.org 现在经常连不上，于是每次都打一条「无法下载公钥」的
    # 黄字警告 —— 但公钥其实一直都在，功能完全正常，属于纯误导。
    # 所以改成：先看本地有没有可用公钥，有就跳过下载。
    echo ""
    echo "Checking flathub signing public key..."
    local FP_KEYSTORE="/var/lib/flatpak/repo/flathub.trustedkeys.gpg"
    local have_key=false
    if [ -s "$FP_KEYSTORE" ]; then
        # 文件存在还不够，确认里面确实是 flathub 的签名密钥（避免损坏的空壳文件误判）
        if command -v gpg &>/dev/null; then
            gpg --show-keys "$FP_KEYSTORE" 2>/dev/null | grep -qi "Flathub" && have_key=true
        else
            have_key=true
        fi
    fi

    if $have_key; then
        echo -e "${GREEN}✓ Signing public key already present; no need to import again${NC}"
    else
        # 本地没有公钥才去下载：先官方，再试镜像（部分镜像也托管了这份公钥）
        echo -e "${YELLOW}Local flathub public key not found; downloading...${NC}"
        local key_url got_key=false
        for key_url in \
            "https://dl.flathub.org/repo/flathub.gpg" \
            "https://mirrors.ustc.edu.cn/flathub/flathub.gpg" \
            "https://mirrors.cernet.edu.cn/flathub/flathub.gpg"; do
            if curl -fsSL --connect-timeout 10 --max-time 30 -o "$FP_KEY_TMP" "$key_url" 2>/dev/null \
               && [ -s "$FP_KEY_TMP" ] \
               && gpg --show-keys "$FP_KEY_TMP" >/dev/null 2>&1; then
                got_key=true
                echo -e "${CYAN}  Fetched from $key_url${NC}"
                break
            fi
        done

        if $got_key; then
            if sudo flatpak remote-modify --gpg-import="$FP_KEY_TMP" flathub 2>/dev/null; then
                echo -e "${GREEN}✓ Imported flathub signing public key${NC}"
            else
                echo -e "${YELLOW}⚠ Failed to import public key; continuing (fix manually if installs fail signature checks)${NC}"
            fi
        else
            # 只有真的拿不到才告警，并说清后果和办法
            echo -e "${YELLOW}⚠ Could not obtain the flathub signing public key.${NC}"
            echo -e "${YELLOW}  Impact: installs/updates may fail signature checks (Could not find public key).${NC}"
            echo -e "${YELLOW}  Fix: rerun this after the network recovers, or run manually:${NC}"
            echo -e "${YELLOW}    curl -fsSL https://dl.flathub.org/repo/flathub.gpg -o /tmp/f.gpg${NC}"
            echo -e "${YELLOW}    sudo flatpak remote-modify --gpg-import=/tmp/f.gpg flathub${NC}"
        fi
    fi
    rm -f "$FP_KEY_TMP"

    # 2) 切换 flathub 地址
    if ! sudo flatpak remote-modify flathub --url="$FP_MIRROR" 2>/dev/null; then
        echo -e "${RED}✗ Flatpak source configuration failed${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Flatpak source switched to $FP_MIRROR${NC}"

    # 3) 实际拉一次元数据验证，不只看命令返回值
    #    remote-info 必须指定分支，否则会因"多个可用分支"直接报错，被误判为镜像不可用
    echo ""
    echo "Verifying source availability..."
    if timeout 90 flatpak remote-info flathub org.freedesktop.Platform/x86_64/24.08 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Verification passed (package queries work)${NC}"
    else
        # 官方源本身也可能因为网络问题暂时查不到，不能一律判为「源坏了」
        if [ "$FP_MIRROR" = "https://dl.flathub.org/repo/" ]; then
            echo -e "${YELLOW}⚠ Reverted to official source, but verification failed (dl.flathub.org may be unreachable).${NC}"
            echo -e "${YELLOW}  The source URL was set successfully; it will work once the network recovers.${NC}"
            return 0
        fi
        echo -e "${RED}✗ Source verification failed; rolling back to the previous source...${NC}"
        if [ -n "$FP_OLD_URL" ]; then
            sudo flatpak remote-modify flathub --url="$FP_OLD_URL" 2>/dev/null \
                && echo -e "${YELLOW}Rolled back to previous URL: $FP_OLD_URL${NC}" \
                || echo -e "${RED}Rollback failed, please run manually: sudo flatpak remote-modify flathub --url=$FP_OLD_URL${NC}"
        else
            echo -e "${RED}Previous URL unknown, please restore manually: sudo flatpak remote-modify flathub --url=https://dl.flathub.org/repo/${NC}"
        fi
        echo -e "${YELLOW}Tip: try another mirror (some mirrors occasionally go down).${NC}"
        return 1
    fi
    echo ""
    if [ "$FP_MIRROR" = "https://dl.flathub.org/repo/" ]; then
        echo -e "${GREEN}✓ Restored Flathub official source.${NC}"
    else
        echo -e "${GREEN}✓ Switched to ${FP_MIRROR_NAME}.${NC}"
        echo -e "${YELLOW}Note: China mirrors cache Flathub; cache misses fall back to the official site,${NC}"
        echo -e "${YELLOW}      so basic connectivity to dl.flathub.org is still required.${NC}"
    fi
    echo ""
    echo -e "${CYAN}  To switch again, rerun this feature (includes Restore official source).${NC}"
}

adjust_swap() {
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}════════════════ Adjusting virtual memory size ════════════════${NC}"
        echo ""
        echo -e "${CYAN}Current system status${NC}"
        echo "--------------------------------------------"
        if command -v free &> /dev/null; then
            mem_line=$(LANG=C free -h | grep '^Mem:')
            swap_line=$(LANG=C free -h | grep '^Swap:')
            [ -n "$mem_line" ] && echo -e "Physical memory: ${GREEN}$(echo "$mem_line" | awk '{print $2}')${NC} | Used: ${YELLOW}$(echo "$mem_line" | awk '{print $3}')${NC}"
            [ -n "$swap_line" ] && echo -e "Swap space: ${GREEN}$(echo "$swap_line" | awk '{print $2}')${NC} | Used: ${YELLOW}$(echo "$swap_line" | awk '{print $3}')${NC}"
        fi
        echo ""
        echo -e "${CYAN}Please choose an operation${NC}"
        echo "============================================"
        echo -e "${GREEN}[1] Apply the recommended CryoByte33 settings${NC}"
        echo -e "${GREEN}[2] Adjust the traditional Swap file size${NC}"
        echo -e "${GREEN}[3] Configure ZRAM (compressed memory swap)${NC}"
        echo -e "${GREEN}[4] Clean up all virtual memory settings and start over${NC}"
        echo "============================================"
        echo ""
        read -p "Enter an option [1-4]: " main_choice < /dev/tty
        case $main_choice in
            1) apply_cryo_recommendation ;;
            2) adjust_swapfile ;;
            3) configure_zram ;;
            4) cleanup_swap ;;
            *) echo -e "${RED}Invalid choice, please try again.${NC}"; sleep 1; continue ;;
        esac
        echo ""
        read -p "Press Enter to continue..." < /dev/tty
    done
}

# Check whether /home has enough free space for a swap file of the given size (GB)
check_swap_space() {
    local need_gb="$1"
    local avail_kb=$(df --block-size=1K --output=avail /home 2>/dev/null | tail -1 | tr -d ' ')
    if [ -z "$avail_kb" ] || [ "$avail_kb" -lt $((need_gb * 1024 * 1024)) ]; then
        echo -e "${RED}✗ Not enough free space on /home: about ${need_gb}GB needed, about $((avail_kb / 1024 / 1024))GB available.${NC}"
        return 1
    fi
    echo -e "${CYAN}✓ /home has enough free space (about $((avail_kb / 1024 / 1024))GB).${NC}"
    return 0
}

apply_cryo_recommendation() {
    mk_temp_dir
    echo -e "${YELLOW}═══════════════ Applying the recommended CryoByte33 settings ═══════════════${NC}"
    confirm_action || { echo "Operation cancelled."; return; }
    local swap_size_gb=16; local block_count=$((swap_size_gb*1024))
    check_swap_space "$swap_size_gb" || return 1
    # FIX-LEAD: cryo swapoff
    # swapoff 失败时仍删除 /home/swapfile 会让正在使用的 Swap 失去路径且无法恢复，
    # 低内存时可能触发 OOM。先确认旧 Swap 已全部停用，否则中止并保持原状。
    if ! sudo swapoff /home/swapfile 2>/dev/null && swapon --show=NAME --noheadings 2>/dev/null | grep -qx '/home/swapfile'; then
        echo -e "${RED}✗ Failed to deactivate existing /home/swapfile; aborted, original swap untouched.${NC}"
        return 1
    fi
    if ! sudo swapoff -a 2>/dev/null; then
        echo -e "${RED}✗ Failed to deactivate all swap devices; aborted to avoid deleting an active file.${NC}"
        return 1
    fi
    sudo rm -f /home/swapfile
    sudo touch /home/swapfile; sudo chattr +C /home/swapfile 2>/dev/null || true
    if ! sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$block_count conv=fsync status=progress 2>/dev/null; then
        echo -e "${RED}✗ Failed to create the swap file (dd error, possibly not enough disk space).${NC}"
        return 1
    fi
    sudo chmod 600 /home/swapfile
    if ! sudo mkswap /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ mkswap formatting failed.${NC}"
        return 1
    fi
    if ! sudo swapon /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ swapon failed.${NC}"
        return 1
    fi
    sudo sed -i '\|/home/swapfile|d' /etc/fstab 2>/dev/null
    echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null
    echo -e "${GREEN}✓ 16GB swap file created${NC}"
    sudo tee /etc/sysctl.d/99-cryo-optimizations.conf > /dev/null <<'EOF'
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.page-cluster=0
vm.dirty_background_ratio=3
vm.dirty_ratio=50
EOF
    sudo sysctl --system --load=/etc/sysctl.d/99-cryo-optimizations.conf >/dev/null 2>&1
    if [ -f /etc/sysctl.d/99-cryo-optimizations.conf ]; then
        echo -e "${GREEN}✓ Kernel parameter optimization complete${NC}"
    else
        echo -e "${YELLOW}⚠ Failed to write the kernel parameter config file, this optimization will not persist${NC}"
    fi
    # Disabling ZRAM must be judged by the actual result, not by printing success unconditionally
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    if ! systemctl is-active systemd-zram-setup@zram0 &>/dev/null \
       && ! systemctl is-enabled systemd-zram-setup@zram0 &>/dev/null 2>&1; then
        echo -e "${GREEN}✓ ZRAM disabled${NC}"
    else
        echo -e "${YELLOW}⚠ ZRAM could not be fully disabled, to disable it completely please run manually:"
        echo -e "   sudo systemctl disable --now systemd-zram-setup@zram0${NC}"
    fi
    echo -e "${GREEN}✅ The recommended CryoByte33 settings were applied successfully!${NC}"
}

adjust_swapfile() {
    mk_temp_dir
    while true; do
        clear; echo -e "${YELLOW}Adjust traditional Swap file size${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        [ -f "/home/swapfile" ] && echo -e "Current file size: ${GREEN}$(sudo du -h /home/swapfile 2>/dev/null | cut -f1)${NC}" || echo -e "Current file: ${YELLOW}not found${NC}"
        echo -n "/home free space: "; df -h /home | tail -1
        echo "Choose a new size: 1)1G 2)4G 3)8G 4)16G 5)32G 6)Custom"
        local swap_size_gb=""
        read -p "Please choose [1-6]: " size_choice < /dev/tty
        case $size_choice in
            1) swap_size_gb=1;; 2) swap_size_gb=4;; 3) swap_size_gb=8;; 4) swap_size_gb=16;; 5) swap_size_gb=32;;
            6) read -p "Enter the size (GB): " custom_size < /dev/tty
               [[ "$custom_size" =~ ^[0-9]+$ ]] && swap_size_gb=$custom_size || { echo -e "${RED}Invalid number.${NC}"; sleep 1; continue; };;
            *) echo -e "${RED}Invalid option.${NC}"; sleep 1; continue;;
        esac
        break
    done
    check_swap_space "$swap_size_gb" || return 1
    # The old swapfile must be disabled before replacement, otherwise rm/mkswap hit "device busy",
    # and deleting the only swap area while memory is tight risks an OOM.
    if swapon --show=NAME --noheadings 2>/dev/null | awk '$1 == "/home/swapfile" {found=1} END {exit !found}'; then
        echo -e "${CYAN}Disabling the old /home/swapfile ...${NC}"
        if ! sudo swapoff /home/swapfile 2>/dev/null; then
            echo -e "${RED}✗ Cannot disable the /home/swapfile in use, aborted (please check memory usage and try again).${NC}"
            return 1
        fi
        # Double-check that it is really released, to avoid rm errors from entries left in the swap table
        if swapon --show=NAME --noheadings 2>/dev/null | awk '$1 == "/home/swapfile" {found=1} END {exit !found}'; then
            echo -e "${RED}✗ /home/swapfile is still in use, aborted, no changes were made.${NC}"
            return 1
        fi
    fi
    sudo rm -f /home/swapfile
    sudo touch /home/swapfile
    if mount | grep " /home " | grep -q btrfs; then sudo chattr +C /home/swapfile 2>/dev/null || echo -e "${YELLOW}⚠ chattr +C failed, continuing${NC}"; fi
    if ! sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$((swap_size_gb*1024)) status=progress conv=fsync 2>/dev/null; then
        echo -e "${RED}✗ Failed to create the swap file (dd error, possibly not enough disk space).${NC}"
        return 1
    fi
    sudo chmod 600 /home/swapfile
    if ! sudo mkswap /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ mkswap formatting failed.${NC}"
        return 1
    fi
    if ! sudo swapon /home/swapfile 2>/dev/null; then
        echo -e "${RED}✗ swapon failed.${NC}"
        return 1
    fi
    # Match the first field exactly before deciding "already exists": the old grep -q "/home/swapfile" would also match
    # comment lines (#/home/swapfile ...) or /home/swapfile2, so the entry was missing or added twice.
    if ! awk '$1 == "/home/swapfile" {found=1} END {exit !found}' /etc/fstab 2>/dev/null; then
        echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null
    fi
    echo -e "${GREEN}✅ Swap file created successfully${NC}"
}

configure_zram() {
    mk_temp_dir
    while true; do
        clear; echo -e "${YELLOW}Configure ZRAM (compressed memory swap)${NC}"
        echo -e "${CYAN}The settings will be written to a persistent config and remain in effect after reboot.${NC}"
        echo "Choose the ZRAM size: 1)2G 2)4G 3)8G"
        local zram_size_gb=""
        read -p "Please choose [1-3]: " zram_choice < /dev/tty
        case $zram_choice in 1) zram_size_gb=2;; 2) zram_size_gb=4;; 3) zram_size_gb=8;; *) echo -e "${RED}Invalid option.${NC}"; sleep 1; continue;; esac
        break
    done
    if ! command -v zramctl &>/dev/null; then
        echo -e "${RED}❌ zramctl not found, cannot configure ZRAM.${NC}"
        return 1
    fi
    sudo modprobe zram 2>/dev/null

    # Persistence: write a zram-generator override config. /etc/systemd/zram-generator.conf takes priority
    # over SteamOS's /usr/lib/systemd/zram-generator.conf (default ram/2 + zstd);
    # without this file, zram-generator recreates it with the vendor default after reboot and this choice is lost.
    # The old code also did rm -f on the same file at the end, which deleted the setting again; fixed here as well.
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
        echo -e "${GREEN}✓ Persistent config written to /etc/systemd/zram-generator.conf (still effective after reboot)${NC}"
    else
        persist_ok=0
        echo -e "${RED}❌ Failed to write the persistent config: this setting will be lost after reboot.${NC}"
    fi
    rm -f "$zram_conf_tmp"

    # Take effect immediately: disable the old zram swap area first, then rebuild it with the chosen size
    if swapon --show=NAME --noheadings 2>/dev/null | awk '$1 == "/dev/zram0" {found=1} END {exit !found}'; then
        sudo swapoff /dev/zram0 2>/dev/null || echo -e "${YELLOW}⚠️ Cannot disable the existing /dev/zram0, will try to resize it directly.${NC}"
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
        echo -e "${RED}❌ Cannot create the ZRAM device.${NC}"
        [ "$persist_ok" -eq 1 ] && echo -e "${CYAN}   Persistent config written, it will be created automatically as ${zram_size_gb}G after reboot.${NC}"
        return 1
    fi
    sudo mkswap "$zram_dev" >/dev/null 2>&1
    if ! sudo swapon "$zram_dev" -p 100 2>/dev/null; then
        echo -e "${RED}❌ Failed to enable ZRAM (swapon error).${NC}"
        return 1
    fi
    # Judge by the actual result, not by guessing success from the command exit code
    if swapon --show=NAME --noheadings 2>/dev/null | awk -v d="$zram_dev" '$1 == d {found=1} END {exit !found}'; then
        local real_size=$(zramctl "$zram_dev" --noheadings --output DISKSIZE 2>/dev/null | tr -d ' ')
        echo -e "${GREEN}✅ ZRAM enabled successfully: $zram_dev (requested ${zram_size_gb}G, actual ${real_size:-unknown}, lz4, priority 100)${NC}"
        [ "$zram_dev" != "/dev/zram0" ] && echo -e "${YELLOW}⚠️ The actual device this time is $zram_dev; the persistent config uses zram0, so zram0 applies after reboot.${NC}"
        [ "$persist_ok" -eq 1 ] && echo -e "${GREEN}✓ This configuration will be restored automatically after reboot.${NC}" \
            || echo -e "${YELLOW}⚠️ Failed to write the persistent config, the vendor default ZRAM will be restored after reboot.${NC}"
    else
        echo -e "${RED}❌ ZRAM does not appear in the swap list after being enabled.${NC}"
        return 1
    fi
}

cleanup_swap() {
    mk_temp_dir
    confirm_action || { echo "Operation cancelled."; return; }
    sudo swapoff -a 2>/dev/null
    # Only reset /dev/zram0 when it really exists; when it does not, that means "ZRAM is not enabled", not a failure.
    # The old form `[ -b ... ] && reset || echo failed` wrongly reported "ZRAM reset failed" when the device did not exist.
    if [ -b /dev/zram0 ]; then
        # On some kernels `zramctl --reset` really succeeds but returns non-zero:
        # right after writing the sysfs reset attribute the device state changes and
        # the read-back check fails. So judge by the actual post-reset state, not the exit code.
        sudo zramctl /dev/zram0 --reset 2>/dev/null
        local _zram_still_on=0 _zram_disk_size=""
        if swapon --show=NAME --noheadings 2>/dev/null | grep -qx "/dev/zram0"; then
            _zram_still_on=1
        fi
        _zram_disk_size=$(cat /sys/block/zram0/disksize 2>/dev/null || echo "")
        if [ "$_zram_still_on" -eq 0 ] && { [ ! -e /sys/block/zram0/disksize ] || [ "${_zram_disk_size:-1}" = "0" ]; }; then
            echo -e "${GREEN}✓ ZRAM reset${NC}"
        else
            echo -e "${YELLOW}⚠️ ZRAM is still in use (device not released); it will return to the default config after a reboot.${NC}"
            echo "    Active swap devices: $(swapon --show=NAME --noheadings 2>/dev/null | tr '\n' ' ')"
        fi
    else
        echo -e "${CYAN}ℹ No ZRAM device found, skipping the reset.${NC}"
    fi
    sudo rm -f /home/swapfile 2>/dev/null
    # Delete by exact match on the first field, to avoid also deleting comment lines / entries with a similar prefix
    if awk '$1 == "/home/swapfile" {found=1} END {exit !found}' /etc/fstab 2>/dev/null; then
        local fstab_tmp="${TEMP_DIR}/fstab.$$"
        if awk '$1 != "/home/swapfile"' /etc/fstab > "$fstab_tmp" 2>/dev/null; then
            sudo cp "$fstab_tmp" /etc/fstab && echo -e "${GREEN}✓ Removed the swapfile entry from fstab${NC}"
        else
            echo -e "${YELLOW}⚠️ Failed to write the temporary fstab, the swapfile entry in /etc/fstab was not removed.${NC}"
        fi
        rm -f "$fstab_tmp"
    fi
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    # After cleaning up swap, zram-generator should no longer rebuild ZRAM with the previously chosen size,
    # so deleting the persistence file written by "Configure ZRAM" here is the correct behavior.
    if [ -f /etc/systemd/zram-generator.conf ]; then
        if sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null; then
            echo -e "${GREEN}✓ Removed the ZRAM persistent config${NC}"
        else
            echo -e "${YELLOW}⚠️ Cannot delete /etc/systemd/zram-generator.conf, ZRAM may still be rebuilt from the old config after reboot.${NC}"
        fi
    fi
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ All virtual memory settings cleaned up (effective after reboot).${NC}"
}

fix_single_ntfs() {
    local device="$1" mountpoint="$2"
    echo ""
    echo -e "${CYAN}Repairing partition: $device${NC}"
    if [ -n "$mountpoint" ] && mountpoint -q "$mountpoint" 2>/dev/null; then
        echo "  Partition is currently mounted at $mountpoint, unmounting..."
        if sudo umount "$device" 2>/dev/null || sudo umount -f "$device" 2>/dev/null; then echo -e "${GREEN}  ✓ Unmounted${NC}"; else echo -e "${RED}  ✗ Unmount failed, cannot continue the repair${NC}"; return 1; fi
    fi
    echo "  Running ntfsfix -d (repairs common errors and clears the dirty flag)..."
    local _dmark _mlog
    _dmark="$(sudo dmesg 2>/dev/null | wc -l)"
    # -d/--clear-dirty: clear the volume dirty flag when the volume can be fixed and mounted.
    # Without -d ntfsfix only does the basic repair and the dirty flag can remain, so ntfs3 still refuses to mount.
    if sudo ntfsfix -d "$device" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Repair succeeded (dirty flag cleared where possible)${NC}"
    else
        echo -e "${RED}  ✗ Repair failed${NC}"
        _mlog="$(sudo dmesg 2>/dev/null | tail -n "+$(( _dmark + 1 ))")"
        if [ -n "$_mlog" ]; then
            echo "  dmesg output from this operation:"
            echo "$_mlog" | grep -iE 'ntfs|volume' | tail -8 | sed 's/^/    /'
        fi
        echo "  If it reports severe corruption, run chkdsk /f in Windows and try again."
        # FIX-LEAD: fix_single_ntfs EN
        return 1
    fi
    if [ -n "$mountpoint" ] && [ -d "$mountpoint" ]; then
        echo "  Trying to remount at $mountpoint ..."
        if sudo mount "$device" "$mountpoint" 2>/dev/null; then echo -e "${GREEN}  ✓ Remounted successfully${NC}"; else echo -e "${YELLOW}  ⚠️ Automatic mount failed, please mount manually later${NC}"; fi
    fi
}

fix_disk_write_error() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Fix disk write errors ════════════════${NC}"
    echo -e "${CYAN}Scanning NTFS partitions and checking for errors...${NC}"

    # ------------------------------------------------------------------
    # Scan first, then decide whether sudo is needed:
    # a single-system SteamOS usually has no NTFS partition at all, and the user should not be asked for a password then.
    # ------------------------------------------------------------------
    echo ""
    echo "Step 1: Scanning NTFS partitions..."
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
        ntfs_labels+=("${LABEL:-no label}")
        ntfs_uuids+=("${UUID:-}")

        if [ -z "$MOUNTPOINT" ] || [ "$MOUNTPOINT" = "None" ]; then
            ntfs_mountpoints+=("")
        else
            ntfs_mountpoints+=("$MOUNTPOINT")
        fi
        ((ntfs_count++))
    done < <(lsblk -P -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID --noheadings 2>/dev/null)

    # If lsblk shows no NTFS, blkid almost certainly has none either, but keep the fallback probe
    # (note: blkid needs root to read all information, so sudo -n is used here and the probe is skipped if unavailable)
    if [ $ntfs_count -eq 0 ] && sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}⚠️  lsblk found no NTFS partitions, trying blkid ...${NC}"
        while IFS= read -r line; do
            [ -z "$line" ] && continue
            dev=$(echo "$line" | cut -d: -f1)
            fstype=$(echo "$line" | sed -n 's/.* TYPE="\([^"]*\)".*/\1/p')
            label=$(echo "$line" | sed -n 's/.* LABEL="\([^"]*\)".*/\1/p')
            uuid=$(echo "$line" | sed -n 's/.* UUID="\([^"]*\)".*/\1/p')

            if [[ "$fstype" == "ntfs" || "$fstype" == "fuseblk" || "$fstype" == "ntfs3" ]]; then
                ntfs_devices+=("$dev")
                ntfs_labels+=("${label:-no label}")
                ntfs_uuids+=("${uuid:-}")
                ntfs_mountpoints+=("")
                ((ntfs_count++))
            fi
        done < <(sudo -n blkid 2>/dev/null)
    fi

    # No NTFS partition: give a clear conclusion directly, without asking for a password or touching read-only mode
    if [ $ntfs_count -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ No NTFS partitions detected, nothing to repair.${NC}"
        echo -e "${CYAN}   This function repairs the dirty flag (Volume dirty) left on"
        echo -e "${CYAN}   Windows dual-boot / NTFS memory cards after unsafe removal or power loss; a SteamOS-only system does not have this problem.${NC}"
        echo ""
        echo -e "${CYAN}   If you really do see disk write errors, it may be one of the following:${NC}"
        echo "     · Filesystem error (btrfs/ext4) -> run sudo btrfs check or sudo fsck"
        echo "     · Not enough space           -> run df -h to check free space"
        echo "     · Hardware/IO error          -> run sudo dmesg | grep -i error to check"
        echo ""
        echo -e "${YELLOW}   Tip: if an NTFS memory card or external drive is inserted, make sure it is fully seated and try again.${NC}"
        return 0
    fi

    # ------------------------------------------------------------------
    # Only after confirming an NTFS partition exists is root access needed.
    # The order is deliberately "ask for the password -> disable read-only -> install tools":
    #   on Arch, ntfsfix / ntfsinfo live in the ntfsprogs package, and installing a
    #   package writes to system directories, which on SteamOS needs
    #   steamos-readonly disable first. So the password is collected up front and
    #   the tools are installed automatically instead of telling the user to do it.
    # ------------------------------------------------------------------
    echo ""
    echo -e "${CYAN}$ntfs_count NTFS partition(s) found, root permission is required for the check.${NC}"
    echo -e "${CYAN}Please enter your sudo password to continue (it will not be shown while typing)${NC}"
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}Password verification failed or was cancelled, operation terminated.${NC}"
        return 1
    fi
    echo -e "${GREEN}Password verified, continuing.${NC}"

    # Record the read-only state on entry and restore it as needed on exit, so the system is not left writable permanently
    local readonly_was_enabled=0
    if command -v steamos-readonly &> /dev/null; then
        echo ""
        echo "Step 2: Check and disable SteamOS read-only mode"
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            readonly_was_enabled=1
            if sudo steamos-readonly disable 2>/dev/null; then
                RO_READONLY_DISABLED_BY_US=1
                echo -e "${GREEN}✓ Read-only mode disabled${NC}"
            else
                echo -e "${YELLOW}⚠️  Failed to disable read-only mode, trying to continue...${NC}"
            fi
        else
            echo -e "${GREEN}✓ The system is already in read-write mode${NC}"
        fi
    else
        echo ""
        echo "Step 2: Skipping the SteamOS read-only check (not SteamOS)"
    fi

    echo ""
    echo "Step 3: Checking the NTFS tools (ntfsfix / ntfsinfo)"
    # Install whatever is missing and re-check right away; only fail if the
    # install itself fails, and then print ready-to-copy commands.
    local missing_ntfs_tools=()
    command -v ntfsfix  &> /dev/null || missing_ntfs_tools+=("ntfsfix")
    command -v ntfsinfo &> /dev/null || missing_ntfs_tools+=("ntfsinfo")

    if [ ${#missing_ntfs_tools[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ ntfsfix / ntfsinfo are ready${NC}"
    else
        echo -e "${YELLOW}  Missing: ${missing_ntfs_tools[*]}, installing automatically...${NC}"
        # Arch/SteamOS: ntfsfix and ntfsinfo both live in ntfsprogs (NOT in ntfs-3g).
        # Debian/Ubuntu: the same tools live in ntfs-3g. The package names are swapped
        # between the two distro families, so they must not be mixed up.
        if command -v pacman &> /dev/null; then
            sudo pacman -S --needed --noconfirm ntfsprogs >/dev/null 2>&1
        elif command -v apt-get &> /dev/null; then
            sudo apt-get install -y ntfs-3g >/dev/null 2>&1
        fi
        # 清掉 bash 的命令查找缓存：刚装上的二进制若不刷新，可能仍被判为找不到
        hash -r 2>/dev/null || true

        missing_ntfs_tools=()
        command -v ntfsfix  &> /dev/null || missing_ntfs_tools+=("ntfsfix")
        command -v ntfsinfo &> /dev/null || missing_ntfs_tools+=("ntfsinfo")

        if [ ${#missing_ntfs_tools[@]} -eq 0 ]; then
            echo -e "${GREEN}✓ Installation complete${NC}"
        else
            echo -e "${RED}✗ Automatic installation failed, still missing: ${missing_ntfs_tools[*]}${NC}"
            echo "  Install manually and retry:"
            echo "    sudo steamos-readonly disable"
            echo "    sudo pacman -S ntfsprogs        (Arch/SteamOS)"
            echo "    sudo apt install ntfs-3g        (Debian/Ubuntu)"
            # No need to restore read-only here: restore_readonly in the EXIT trap
            # decides based on RO_READONLY_DISABLED_BY_US
            return 1
        fi
    fi

    echo ""
    echo -e "${CYAN}Checking the error status of $ntfs_count NTFS partition(s)...${NC}"
    local dirty_indices=()
    local skipped_count=0
    for ((i=0; i<ntfs_count; i++)); do
        echo -n "  Checking ${ntfs_devices[$i]} ... "
        # Note: ntfsinfo / ntfsfix both need exclusive access to the device; a mounted volume reports
        #      “Access is denied because the NTFS volume is already exclusively opened”.
        #     The Windows partition the user really cares about is usually mounted, so it must be temporarily unmounted before checking,
        #     and remounted at its original mount point right after the check.
        local dev="${ntfs_devices[$i]}"
        local mp="${ntfs_mountpoints[$i]}"
        local was_mounted=0
        if [ -n "$mp" ] && mountpoint -q "$mp" 2>/dev/null; then
            was_mounted=1
            # Discard all unmount/mount output so it does not interrupt the "Checking xxx ..." line
            if ! sudo umount "$dev" >/dev/null 2>&1 && ! sudo umount -f "$dev" >/dev/null 2>&1; then
                echo -e "${YELLOW}Skipped (partition is in use and cannot be unmounted)${NC}"
                skipped_count=$((skipped_count + 1))
                continue
            fi
        fi

        # Read the Volume Flags of $Volume to test the DIRTY bit (0x0001).
        # Do not look for "Volume is dirty" in `ntfsfix -n` output -- ntfsfix never prints that.
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
                check_err="read failed"
            fi
        fi

        # Whatever the check result, remount the volume at its original location first so normal use is not affected
        if [ "$was_mounted" -eq 1 ] && [ -n "$mp" ]; then
            if ! sudo mount "$mp" >/dev/null 2>&1 && ! sudo mount "$dev" "$mp" >/dev/null 2>&1; then
                echo -e "${YELLOW}⚠ Cannot remount $mp automatically after the check, please mount it manually${NC}"
            fi
        fi

        if [ "$dirty" -eq 1 ]; then
            echo -e "${RED}Errors found (dirty)${NC}"
            dirty_indices+=("$i")
        elif [ -n "$check_err" ]; then
            echo -e "${YELLOW}Skipped ($check_err)${NC}"
            skipped_count=$((skipped_count + 1))
        else
            echo -e "${GREEN}Normal${NC}"
        fi
    done

    # Whichever branch is taken, try to restore read-only mode before exiting
    _restore_readonly_after_fix() {
        if [ "$readonly_was_enabled" -eq 1 ] && command -v steamos-readonly &> /dev/null; then
            echo ""
            echo "Restoring SteamOS read-only mode..."
            if sudo -n steamos-readonly enable 2>/dev/null; then
                echo -e "${GREEN}✓ Read-only mode restored${NC}"
            else
                echo -e "${YELLOW}⚠️  Cannot restore read-only mode automatically, please run manually: sudo steamos-readonly enable${NC}"
            fi
        fi
    }

    if [ ${#dirty_indices[@]} -eq 0 ]; then
        echo ""
        if [ "$skipped_count" -gt 0 ]; then
            # If some partitions could not be checked, do not claim "everything is fine"
            echo -e "${YELLOW}⚠️  ${skipped_count} partition(s) could not be checked (in use or read failure), the other $((ntfs_count - skipped_count)) partition(s) are in normal state.${NC}"
            echo -e "${CYAN}   Close programs that are using these partitions (Steam library, file manager) and try again.${NC}"
        else
            echo -e "${GREEN}✅ All NTFS partitions are in normal state, no disk write errors.${NC}"
        fi
        _restore_readonly_after_fix
        return 0
    fi

    echo ""
    echo -e "${YELLOW}${#dirty_indices[@]} partition(s) have write errors (dirty flag):${NC}"
    # Numbering uses consecutive indices within the dirty partition list (1,2,3...), matching the input of option 2 below
    local n=0
    for idx in "${dirty_indices[@]}"; do
        n=$((n + 1))
        local mp_display="${ntfs_mountpoints[$idx]:-not mounted}"
        echo "  ${n}. ${ntfs_devices[$idx]}  Label:${ntfs_labels[$idx]}  Mount point:${mp_display}"
    done

    echo ""
    echo "Please choose a repair method:"
    echo "  1) Repair all partitions with errors"
    echo "  2) Choose specific partitions to repair"
    echo "  3) Cancel the repair"

    local fix_choice
    while true; do
        # On read failure (no tty / EOF) exit the loop, to avoid endless retry spam
        if ! read -p "Enter an option [1-3]: " fix_choice < /dev/tty; then
            echo -e "${YELLOW}Cannot read input, operation cancelled.${NC}"
            _restore_readonly_after_fix
            return 1
        fi
        case $fix_choice in
            1|2|3) break ;;
            *) echo -e "${RED}Invalid option, please try again.${NC}" ;;
        esac
    done

    # FIX-LEAD: ntfs fix count
    local fix_fail=0
    case $fix_choice in
        1)
            for idx in "${dirty_indices[@]}"; do
                fix_single_ntfs "${ntfs_devices[$idx]}" "${ntfs_mountpoints[$idx]}" || ((fix_fail++))
            done
            ;;
        2)
            echo "Enter the partition number(s) to repair (separate multiple numbers with spaces, e.g. 1 3):"
            while true; do
                if ! read -p "Number: " -a indices < /dev/tty; then
                    echo -e "${YELLOW}Cannot read input, operation cancelled.${NC}"
                    _restore_readonly_after_fix
                    return 1
                fi
                local valid=true
                for num in "${indices[@]}"; do
                    # Number range is 1..number of dirty partitions
                    if [[ ! "$num" =~ ^[0-9]+$ ]] || [ "$num" -lt 1 ] || [ "$num" -gt ${#dirty_indices[@]} ]; then
                        valid=false; break
                    fi
                done
                if $valid; then
                    break
                else
                    echo -e "${RED}Invalid number, please enter a number between 1 and ${#dirty_indices[@]}.${NC}"
                fi
            done
            for num in "${indices[@]}"; do
                # Map the "dirty partition list index" back to the real partition index
                local target_idx="${dirty_indices[$((num-1))]}"
                fix_single_ntfs "${ntfs_devices[$target_idx]}" "${ntfs_mountpoints[$target_idx]}" || ((fix_fail++))
            done
            # FIX-LEAD: ntfs selected count EN
            ;;
        3|*)
            echo "Operation cancelled."
            ;;
    esac

    _restore_readonly_after_fix
    echo ""
    # FIX-LEAD: ntfs final EN
    if [ "${fix_fail:-0}" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Repair finished, but ${fix_fail} partition(s) failed; see the errors above.${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Repair process finished.${NC}"
}

clear_hosts_cache() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Clean hosts cache ════════════════${NC}"
    echo -e "${CYAN}Removes only Steam-related hosts entries, keeps system entries, and backs up automatically.${NC}"
    # /etc/hosts lives on the SteamOS read-only root partition: in read-only mode sudo sed fails silently,
    # and the old code ignored the return value and still printed "cleanup complete". Here we ensure writability first and abort clearly on failure.
    if command -v steamos-readonly &>/dev/null; then
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            echo -e "${CYAN}Temporarily disabling read-only mode to modify /etc/hosts (restored automatically on exit)...${NC}"
            disable_readonly || { echo -e "${RED}✗ Cannot disable read-only mode, /etc/hosts was not modified.${NC}"; return 1; }
        fi
    fi
    local backup="/etc/hosts.backup.$(date +%Y%m%d_%H%M%S)"
    if ! sudo cp /etc/hosts "$backup" 2>/dev/null; then
        echo -e "${RED}✗ Failed to back up /etc/hosts (or the target is read-only), aborted, no changes were made.${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Original hosts backed up to $backup${NC}"
    local steam_hosts_re='^\s*([0-9a-fA-F:.]+|\*)\s+(steamcommunity\.com|steamstatic\.com|steamcontent\.com|steamusercontent\.com|api\.steampowered\.com|store\.steampowered\.com|s\.team|steamcdn-a\.akamaihd\.net)(\s|$)'
    if ! sudo sed -i -E "/${steam_hosts_re}/d" /etc/hosts 2>/dev/null; then
        echo -e "${RED}✗ Failed to write /etc/hosts (disk read-only or insufficient permission), the original file was not modified.${NC}"
        echo -e "${YELLOW}   To roll back: sudo cp $backup /etc/hosts${NC}"
        return 1
    fi
    # Verify by actual content, not just by the command exit code
    if grep -qE "$steam_hosts_re" /etc/hosts 2>/dev/null; then
        echo -e "${RED}✗ Some Steam-related entries could not be removed, please check /etc/hosts.${NC}"
        echo -e "${YELLOW}   Backup file: $backup (roll back with sudo cp $backup /etc/hosts)${NC}"
        return 1
    fi
    # The localhost check must anchor on the full host name, otherwise 127.0.0.1 localhost.localdomain
    # is wrongly treated as "localhost entry already present" and the real localhost entry never gets added
    grep -qE '^\s*127\.0\.0\.1\s+localhost([[:space:]]|$)' /etc/hosts 2>/dev/null \
        || echo "127.0.0.1 localhost" | sudo tee -a /etc/hosts > /dev/null
    grep -qE '^\s*::1\s+localhost([[:space:]]|$)' /etc/hosts 2>/dev/null \
        || echo "::1 localhost ip6-localhost ip6-loopback" | sudo tee -a /etc/hosts > /dev/null
    echo -e "${GREEN}✓ hosts cleanup complete (backup: $backup)${NC}"
}

calibrate_joystick_stick() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Calibrate joystick ════════════════${NC}"
    if thumbstick_cal; then echo -e "${GREEN}✓ Joystick calibration complete${NC}"; else echo -e "${RED}✗ Joystick calibration failed${NC}"; echo "Please make sure the joystick calibration tool (thumbstick_cal) is installed"; fi
}

calibrate_joystick_trigger() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Calibrate trigger ════════════════${NC}"
    if trigger_cal; then echo -e "${GREEN}✓ Trigger calibration complete${NC}"; else echo -e "${RED}✗ Trigger calibration failed${NC}"; echo "Please make sure the trigger calibration tool (trigger_cal) is installed"; fi
}

fix_boot() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Repair boot ════════════════${NC}"
    echo -e "${CYAN}Running the boot repair script...${NC}"

    cat > "$TEMP_DIR/fix_boot.sh" << 'EOF'
#!/bin/bash

echo "========================================"
echo "  Clover boot order auto-configuration script"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "⚠️ Administrator privileges are required, elevating..."
    echo "   To change the boot order, please enter your user password (it will not be shown while typing)"
    echo ""
    sudo "$0" "$@"
    exit $?
fi

if ! command -v efibootmgr &> /dev/null; then
    echo "❌ Error: efibootmgr command not found."
    echo "   Please make sure the efibootmgr tool is installed on the system."
    exit 1
fi

# ---------------------------------------------------------------------------
# Dynamically detect the ESP partition for "rebuild boot entries".
# Do not hard-code /dev/nvme0n1p1: Steam Deck has eMMC (/dev/mmcblk0) and SATA (/dev/sda)
# models, and the partition number is not necessarily 1.
# ---------------------------------------------------------------------------
detect_esp() {
    local dev=""
    ESP_DEV=""; ESP_DISK=""; ESP_PARTN=""

    # 1) 已挂载的 /esp 或 /boot/efi
    for mp in /esp /boot/efi; do
        dev=$(findmnt -n -o SOURCE -M "$mp" 2>/dev/null | grep '^/dev/' | head -1 || true)
        [ -n "$dev" ] || dev=$(mount 2>/dev/null | awk -v m="$mp" '$3 == m {print $1; exit}')
        if [ -n "$dev" ] && [ -b "$dev" ]; then ESP_DEV="$dev"; break; fi
    done
    # 2) 按 EFI 分区类型 GUID 查找
    if [ -z "$ESP_DEV" ]; then
        dev=$(lsblk -P -n -o PATH,PARTTYPE 2>/dev/null \
            | awk -F'"' '/PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b"/{print $2; exit}' || true)
        [ -n "$dev" ] && [ -b "$dev" ] && ESP_DEV="$dev"
    fi
    [ -n "$ESP_DEV" ] || return 1
    ESP_DISK="/dev/$(lsblk -n -o PKNAME "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')"
    ESP_PARTN=$(lsblk -n -o PARTN "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')
    [ -n "$ESP_PARTN" ] || ESP_PARTN=1
    return 0
}

# 检查 ESP 上 Clover 引导文件是否存在（决定「重建启动项」是否有意义）
# 返回值：0 = 文件存在；1 = 确认不存在；2 = 无法判断（权限/挂载问题）
clover_files_ok() {
    local mnt=""
    if [ -n "${ESP_DEV:-}" ]; then
        if mountpoint -q /esp 2>/dev/null; then mnt=/esp
        elif mountpoint -q /boot/efi 2>/dev/null; then mnt=/boot/efi
        else
            mnt=$(mktemp -d 2>/dev/null) || return 2
            if ! mount -o ro "$ESP_DEV" "$mnt" 2>/dev/null; then
                rmdir "$mnt" 2>/dev/null; return 2
            fi
            TMP_ESP_MNT="$mnt"
        fi
    else
        return 2
    fi
    # The EFI directory may be at the root or in an efi subdirectory.
    # Note: this script already runs with sudo, but "directory does not exist" must still be distinguished from "cannot read it",
    # otherwise permission problems are misreported as "Clover files missing" and mislead the user into reinstalling Clover.
    local efi_root=""
    for cand in "$mnt/EFI" "$mnt/efi/EFI"; do
        if [ -d "$cand" ] && ls "$cand" &>/dev/null; then efi_root="$cand"; break; fi
    done
    if [ -z "$efi_root" ]; then
        # Cannot tell whether there is no EFI directory or it cannot be read
        if [ ! -r "$mnt" ]; then return 2; fi
        return 1
    fi
    for cand in "$efi_root/clover/cloverx64.efi"; do
        if [ -f "$cand" ]; then return 0; fi
    done
    return 1
}

echo "1. Scanning UEFI boot entries..."
echo "----------------------------------------"

BACKUP_FILE="/tmp/boot_backup_$(date +%Y%m%d_%H%M%S).txt"
CURRENT_BOOT_ORDER=$(efibootmgr | grep "BootOrder")
echo "Current boot order: $CURRENT_BOOT_ORDER"
efibootmgr -v > "$BACKUP_FILE"
echo "Boot entry backup saved to: $BACKUP_FILE"

echo ""
echo "2. Looking for the Clover boot entry..."
echo "----------------------------------------"

CLOVER_ENTRY=$(efibootmgr -v | grep -i "CLOVER" | head -1)

# When the Clover boot entry is missing, do not just exit: after a SteamOS update or firmware reset boot entries
# are often cleared while the Clover files on the ESP are usually still there, so it can be rebuilt automatically.
if [ -z "$CLOVER_ENTRY" ]; then
    echo "⚠️  Clover boot entry not found, trying to rebuild it automatically..."
    echo ""

    if ! detect_esp; then
        echo "❌ Cannot identify the ESP partition, cannot rebuild the boot entry."
        echo "   Please confirm the system is SteamOS/Bazzite and the ESP partition is mounted properly."
        exit 1
    fi
    echo "   ESP partition: $ESP_DEV (disk $ESP_DISK, partition number $ESP_PARTN)"

    clover_files_ok
    # FIX-LEAD: fix_boot files_rc EN
    # This runs outside a function in the generated sub-script: `local` fails
    # and overwrites $?, so a missing Clover file (rc 1) was treated as fine.
    files_rc=$?
    if [ "$files_rc" -eq 2 ]; then
        echo ""
        echo "⚠️  Cannot read the ESP contents to determine whether the Clover files exist (permission or mount problem)."
        echo "   File check skipped, will try to register the boot entry directly."
        echo "   If it still does not boot after registering, please reinstall Clover (Boot Management -> Install/Reinstall Clover)."
    elif [ "$files_rc" -eq 1 ]; then
        echo ""
        echo "❌ Clover boot file (cloverx64.efi) not found on the ESP."
        echo "   Possible causes:"
        echo "   • Clover is not installed yet"
        echo "   • A SteamOS update overwrote the Clover files on the ESP"
        echo ""
        echo "   -> Please reinstall using Boot Management -> Install/Reinstall Clover."
        [ -n "${TMP_ESP_MNT:-}" ] && { umount "$TMP_ESP_MNT" 2>/dev/null; rmdir "$TMP_ESP_MNT" 2>/dev/null; }
        exit 1
    fi

    # Clean up leftover entries with the same name to avoid duplicates
    for old_entry in $(efibootmgr | grep -i "clover" | grep -o 'Boot[0-9A-Fa-f]\{4\}' | sed 's/Boot//'); do
        efibootmgr -b "$old_entry" -B &>/dev/null || true
    done

    echo "   Registering the Clover boot entry..."
    if efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
        -L "Clover - GUI Boot Manager" -l '\EFI\clover\cloverx64.efi'; then
        echo "   ✅ Clover boot entry rebuilt"
        CLOVER_ENTRY=$(efibootmgr -v | grep -i "CLOVER" | head -1)
    else
        echo "   ❌ Rebuild failed. Please try Boot Management -> Install/Reinstall Clover."
        [ -n "${TMP_ESP_MNT:-}" ] && { umount "$TMP_ESP_MNT" 2>/dev/null; rmdir "$TMP_ESP_MNT" 2>/dev/null; }
        exit 1
    fi

    # Also check the SteamOS boot entry
    if ! efibootmgr | grep -qi "steamos\|steamcl"; then
        echo ""
        echo "⚠️  SteamOS boot entry not found, rebuilding it as well..."
        if efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
            -L "SteamOS" -l '\EFI\steamos\steamcl.efi'; then
            echo "   ✅ SteamOS boot entry rebuilt"
        else
            echo "   ⚠️  Failed to rebuild the SteamOS boot entry, please check steamcl.efi on the ESP manually"
        fi
    fi

    [ -n "${TMP_ESP_MNT:-}" ] && { umount "$TMP_ESP_MNT" 2>/dev/null; rmdir "$TMP_ESP_MNT" 2>/dev/null; }

    if [ -z "$CLOVER_ENTRY" ]; then
        echo ""
        echo "❌ The Clover boot entry still cannot be found after rebuilding."
        echo "   Current boot entries:"
        efibootmgr | grep "Boot[0-9A-F][0-9A-F][0-9A-F][0-9A-F]"
        exit 1
    fi
    echo ""
fi

CLOVER_BOOTNUM=$(echo "$CLOVER_ENTRY" | grep -o 'Boot[0-9A-F]\{4\}' | head -1 | sed 's/Boot//')

echo "✅ Clover boot entry found:"
echo "   Boot number: Boot$CLOVER_BOOTNUM"
echo "   Description: $CLOVER_ENTRY"

echo ""
echo "3. Analyzing the current boot order..."
echo "----------------------------------------"

CURRENT_ORDER=$(efibootmgr | grep "BootOrder" | cut -d: -f2 | tr -d ' ')

if [ -z "$CURRENT_ORDER" ]; then
    echo "⚠️  Cannot get the current boot order, a new order will be created."
    NEW_ORDER="$CLOVER_BOOTNUM"
else
    if [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM,"* ]] || [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM" ]]; then
        echo "✅ Clover is already first in the boot order, no change needed."
        echo "   Current order: $CURRENT_ORDER"
        exit 0
    fi

    NEW_ORDER="$CLOVER_BOOTNUM,$(echo "$CURRENT_ORDER" | tr ',' '\n' | grep -v "^$CLOVER_BOOTNUM$" | tr '\n' ',' | sed 's/,$//')"
fi

echo "Current order: $CURRENT_ORDER"
echo "New order: $NEW_ORDER"

echo ""
echo "4. Confirm the setting"
echo "----------------------------------------"
echo "The script will perform the following actions:"
echo "  • Set Clover (Boot$CLOVER_BOOTNUM) as the first boot entry"
echo "  • Keep the order of the other boot entries unchanged"
echo ""

read -n1 -p "Press Enter or A to confirm, any other key to cancel: " confirm_boot < /dev/tty
echo

if [[ -z "$confirm_boot" || "$confirm_boot" =~ [Aa] ]]; then
    echo "Continuing..."
else
    echo "❌ Operation cancelled."
    exit 0
fi

echo ""
echo "5. Setting the boot order..."
echo "----------------------------------------"

efibootmgr -o "$NEW_ORDER"

echo ""
echo "6. Verifying the result"
echo "----------------------------------------"

RESULT=$(efibootmgr | grep "BootOrder")
echo "Final boot order: $RESULT"

if echo "$RESULT" | grep -q "^BootOrder: $CLOVER_BOOTNUM,"; then
    echo ""
    echo "✅ Success! Clover (Boot$CLOVER_BOOTNUM) is now the first boot entry."
    echo ""
    echo "The Clover boot menu will be entered first on the next reboot."
    echo "To test the setting, please restart the Steam Deck."
else
    echo ""
    echo "⚠️  The setting may not have taken full effect."
    echo "   Please run 'efibootmgr -v' manually to check the setting."
fi

echo ""
echo "========================================"
echo "Script execution finished"
echo "========================================"
echo "Tip: to restore the original setting, refer to the backup file: $BACKUP_FILE"
EOF

    chmod +x "$TEMP_DIR/fix_boot.sh"
    "$TEMP_DIR/fix_boot.sh"
}

# Safely remove a given entry from fstab (exact comparison on the first field, no regex, to avoid special characters / prefix damage)
fstab_remove_entry() {
    local key="$1"
    [ -z "$key" ] && return 1
    [ -f /etc/fstab ] || return 1
    # Check whether the key exists first, to avoid a pointless write
    awk -v k="$key" '$1 == k {found=1} END {exit !found}' /etc/fstab 2>/dev/null || return 1
    # Back up, then filter and write back with awk (temp file in /tmp with explicit read permission to avoid permission problems)
    local tmp="${TEMP_DIR:-/tmp}/fstab.$$"
    mkdir -p "$(dirname "$tmp")" 2>/dev/null
    awk -v k="$key" '$1 != k' /etc/fstab > "$tmp" 2>/dev/null || { rm -f "$tmp"; return 1; }
    chmod 644 "$tmp" 2>/dev/null
    sudo cp "$tmp" /etc/fstab && rm -f "$tmp"
}

# Build the NTFS mount / fstab options.
# The old code hardcoded uid=1000,gid=1000; on a machine whose user is not deck or whose
# UID is not 1000 the partition mounts but ordinary users cannot write to it, so derive
# the ids from the current user instead.
ntfs_mount_opts() {
    local u g
    u="$(id -u 2>/dev/null)"; g="$(id -g 2>/dev/null)"
    [ -z "$u" ] && u=1000
    [ -z "$g" ] && g=1000
    printf 'rw,exec,uid=%s,gid=%s,windows_names,nofail' "$u" "$g"
}

# Is the given mountpoint currently read-only?
# ntfs-3g(FUSE) does not fail on a dirty/hibernated volume: it silently downgrades the
# mount to read-only. Checking only the mount exit code and the systemd journal therefore
# reports success for a volume you cannot actually write to, so re-read the real options.
ntfs_mountpoint_is_ro() {
    local mp="$1" opts
    [ -z "$mp" ] && return 1
    opts="$(findmnt -n -o OPTIONS -M "$mp" 2>/dev/null | head -1)"
    [ -z "$opts" ] && return 1
    case ",$opts," in
        *,ro,*) return 0 ;;
    esac
    return 1
}

# dmesg line-count baseline: used to extract only the kernel messages produced by THIS
# operation. The old code ran `dmesg | grep -i ntfs | tail -5`, which surfaced months-old
# errors from boot and pointed troubleshooting at the wrong thing.
dmesg_line_count() {
    sudo dmesg 2>/dev/null | wc -l
}

dmesg_since() {
    local mark="${1:-0}"
    case "$mark" in ''|*[!0-9]*) mark=0 ;; esac
    # A baseline of 0 means it could not be read (not that dmesg is empty).
    # Print nothing then, instead of feeding the whole log to the diagnosis
    # as if it were this operation's output.
    [ "$mark" -gt 0 ] || return 0
    sudo dmesg 2>/dev/null | tail -n "+$(( mark + 1 ))"
}

# Turn a failed mount into actionable steps, based on this operation's kernel log
ntfs_explain_failure() {
    local dev="$1" mp="$2" log="$3"
    local hit=0
    if echo "$log" | grep -qiE 'volume is dirty|"force" flag is not set'; then
        hit=1
        echo -e "${YELLOW}    Diagnosis: the volume carries the NTFS dirty flag, so the in-kernel ntfs3 driver refuses to mount it.${NC}"
    elif echo "$log" | grep -qiE 'hibernat'; then
        hit=1
        echo -e "${YELLOW}    Diagnosis: Windows is hibernated or Fast Startup is on, so the volume is not marked safe to write.${NC}"
    elif echo "$log" | grep -qiE 'unclean|not clean|chkdsk'; then
        hit=1
        echo -e "${YELLOW}    Diagnosis: the filesystem was not cleanly unmounted and must be repaired before mounting.${NC}"
    fi
    if [ $hit -eq 1 ]; then
        echo -e "${CYAN}    Try these in order:${NC}"
        echo "      a) Boot Windows, turn off Fast Startup, choose Shut down, then come back and retry (cleanest)"
        echo "      b) Clear the flag on this machine:"
        echo "           sudo steamos-readonly disable"
        echo "           sudo pacman -S ntfsprogs"
        echo "           sudo umount $dev 2>/dev/null; sudo ntfsfix -d $dev"
        echo "         then run this feature again"
        echo "      c) Mount read-only for now, just to get at your data: sudo mount -o ro $dev $mp"
        echo "      d) Emergency read-write (flag not cleared, risks corrupting metadata):"
        echo "           sudo mount -t ntfs3 -o force,uid=$(id -u),gid=$(id -g) $dev $mp"
    else
        echo -e "${CYAN}    Common causes:${NC}"
        echo "      a) dirty/hibernated flag on the volume -> turn off Fast Startup in Windows and shut"
        echo "         down completely, or install ntfsprogs and run: sudo ntfsfix -d $dev"
        echo "      b) this is a Windows recovery partition -> this feature already skips those"
        echo "      c) the device is busy -> run sudo umount $dev first, then retry"
        echo "      d) bad fstab entry or mountpoint -> check /etc/fstab and the owner of $mp"
    fi
}

# Pre-mount check: ntfs-3g.probe ships with the ntfs-3g package, so ntfsprogs is not needed.
# It tells us up front whether the volume can be mounted read-write, so the reason can be
# explained before the mount instead of only after discovering a read-only mount.
# Returns 0=read-write mount possible; 1=read-only/repair needed; 2=cannot tell (tool missing or device busy)
ntfs_probe_writable() {
    local dev="$1" probe out rc
    for probe in /usr/bin/ntfs-3g.probe /bin/ntfs-3g.probe /usr/sbin/ntfs-3g.probe; do
        [ -x "$probe" ] || continue
        out="$(sudo "$probe" --readwrite "$dev" 2>&1)"
        rc=$?
        if [ $rc -eq 0 ]; then
            return 0
        fi
        # Only a genuine dirty / hibernated / unclean symptom counts as "cannot mount read-write";
        # every other failure (permissions, busy device, changed tool behaviour) is reported as
        # "cannot tell", so the pre-check never raises a wrong warning.
        if echo "$out" | grep -qiE 'dirty|hibernat|unclean|not clean|chkdsk|refus'; then
            return 1
        fi
        return 2
    done
    return 2
}

# Explanation for a mount that succeeded but was downgraded to read-only
ntfs_explain_readonly() {
    local dev="$1" mp="$2"
    echo -e "${YELLOW}    Reason: this volume carries the NTFS dirty flag or is hibernated, and the Linux NTFS driver only agrees to mount it read-only.${NC}"
    echo "    The usual source is Windows Fast Startup or Hibernation: the system never really shut down."
    echo ""
    echo -e "${CYAN}    Proper fix (recommended):${NC}"
    echo "      1) Boot Windows -> Settings -> System -> Power -> Choose what the power buttons do"
    echo "         -> Change settings that are currently unavailable -> untick 'Turn on fast startup' -> save"
    echo "      2) In Windows choose Shut down (do not use Restart; restarting does not clear the dirty flag)"
    echo "      3) Come back to SteamOS and run this feature again"
    echo ""
    echo -e "${CYAN}    Without booting Windows you can clear the dirty flag inside SteamOS:${NC}"
    echo "      sudo steamos-readonly disable"
    echo "      sudo pacman -S ntfsprogs          # note: ntfsfix is NOT in the ntfs-3g package"
    echo "      sudo umount $dev 2>/dev/null; sudo ntfsfix -d $dev"
    echo "      sudo mount $mp"
    echo ""
    echo -e "${CYAN}    Emergency only (flag not cleared, forced read-write, may corrupt metadata):${NC}"
    echo "      sudo umount $dev 2>/dev/null"
    echo "      sudo mount -t ntfs3 -o force,uid=$(id -u),gid=$(id -g) $dev $mp"
}

fix_shared_disk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Automatically mount Windows partitions ════════════════${NC}"
    echo ""

    # Mounting partitions and writing /etc/fstab both need root; authorise sudo
    # once up front so the following steps do not each prompt for a password.
    echo -e "${CYAN}This operation requires root permission (mounting partitions and writing /etc/fstab).${NC}"
    echo -e "${CYAN}Please enter your sudo password to continue (it will not be shown while typing)${NC}"
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}Password verification failed or was cancelled, operation terminated.${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Password verified, continuing.${NC}"
    echo ""

    echo "Step 1: Check SteamOS read-only mode"
    if command -v steamos-readonly &>/dev/null; then
        # Record the state on entry; the global trap restores it on exit (only when the script turned it off)
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            if sudo steamos-readonly disable 2>/dev/null; then
                RO_READONLY_DISABLED_BY_US=1
                echo -e "${GREEN}✓ Read-only mode temporarily disabled${NC}"
            else
                echo -e "${YELLOW}⚠️  Failed to disable read-only mode, writing fstab later may fail${NC}"
            fi
        else
            echo -e "${GREEN}✓ The system is already in writable mode${NC}"
        fi
    else
        echo -e "${GREEN}✓ Not a SteamOS system, skipping${NC}"
    fi
    echo ""

    echo "Step 2: Checking the NTFS tools (ntfs-3g / ntfsfix)"
    # Install whatever is missing. ntfs-3g is required to mount NTFS at all, so its
    # absence is fatal; ntfsfix is only needed when a dirty volume must be cleared,
    # so a failure there is only a warning.
    local missing_core=()
    local missing_opt=()
    if ! command -v mount.ntfs-3g &>/dev/null && ! command -v ntfs-3g &>/dev/null; then
        missing_core+=("ntfs-3g")
    fi
    command -v ntfs-3g.probe &>/dev/null || missing_core+=("ntfs-3g.probe")
    command -v ntfsfix &>/dev/null || missing_opt+=("ntfsfix")

    if [ ${#missing_core[@]} -eq 0 ] && [ ${#missing_opt[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ The NTFS tools are ready${NC}"
    else
        # Join the missing items without leaving stray spaces (maybe only ntfsfix is missing)
        local need_list=""
        if [ ${#missing_core[@]} -gt 0 ]; then need_list="${missing_core[*]}"; fi
        if [ ${#missing_opt[@]} -gt 0 ]; then need_list="${need_list:+$need_list }${missing_opt[*]}"; fi
        echo -e "${YELLOW}  Missing: ${need_list}, installing automatically...${NC}"
        # Arch/SteamOS: ntfs-3g and ntfs-3g.probe live in ntfs-3g, while ntfsfix lives
        #               in ntfsprogs -- they are not the same package
        # Debian/Ubuntu: all of the above live in ntfs-3g
        if command -v pacman &>/dev/null; then
            sudo pacman -S --needed --noconfirm ntfs-3g ntfsprogs >/dev/null 2>&1
        elif command -v apt-get &>/dev/null; then
            sudo apt-get install -y ntfs-3g >/dev/null 2>&1
        fi
        # Clear the bash command cache: a freshly installed binary may otherwise still be reported as missing
        hash -r 2>/dev/null || true

        missing_core=()
        missing_opt=()
        if ! command -v mount.ntfs-3g &>/dev/null && ! command -v ntfs-3g &>/dev/null; then
            missing_core+=("ntfs-3g")
        fi
        command -v ntfs-3g.probe &>/dev/null || missing_core+=("ntfs-3g.probe")
        command -v ntfsfix &>/dev/null || missing_opt+=("ntfsfix")

        if [ ${#missing_core[@]} -eq 0 ]; then
            echo -e "${GREEN}✓ Installation complete${NC}"
        else
            echo -e "${RED}✗ Automatic installation failed, still missing: ${missing_core[*]}${NC}"
            echo "  Windows partitions cannot be mounted without the NTFS driver. Install it manually and retry:"
            echo "    sudo steamos-readonly disable"
            echo "    sudo pacman -S ntfs-3g          (Arch/SteamOS)"
            echo "    sudo apt install ntfs-3g        (Debian/Ubuntu)"
            return 1
        fi
        if [ ${#missing_opt[@]} -gt 0 ]; then
            echo -e "${YELLOW}  ⚠️  ${missing_opt[*]} is still not installed: this does not affect mounting,"
            echo -e "      but if the volume is dirty and needs its flag cleared, run sudo pacman -S ntfsprogs first${NC}"
        fi
    fi
    echo ""

    echo "Step 3: Modify the UDisks2 permission file"
    UDISKS2_FILE="/usr/share/polkit-1/actions/org.freedesktop.UDisks2.policy"
    if [ -f "$UDISKS2_FILE" ]; then
        sudo cp "$UDISKS2_FILE" "$UDISKS2_FILE.backup.$(date +%Y%m%d)" 2>/dev/null
        sudo sed -i '/<action id="org.freedesktop.udisks2.filesystem-mount-system">/,/<\/action>/ {
            s|<allow_active>[^<]*</allow_active>|<allow_active>yes</allow_active>|
        }' "$UDISKS2_FILE" 2>/dev/null
        # Verify that the change really succeeded, instead of reporting "modified" unconditionally
        if awk '/<action id="org.freedesktop.udisks2.filesystem-mount-system">/,/<\/action>/' "$UDISKS2_FILE" 2>/dev/null | grep -q '<allow_active>yes</allow_active>'; then
            echo -e "${GREEN}✓ Modified${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not confirm the modification result, please check $UDISKS2_FILE${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  UDisks2 file not found, skipping${NC}"
    fi
    echo ""

    echo "Step 4: Scanning Windows (NTFS) partitions (ignoring recovery partitions)..."
    local sys_mounts=("/" "/home" "/var" "/efi" "/esp" "/boot" "/boot/efi")
    local recovery_guid="de94bba4-06d1-4d40-a16a-bfd50179d6ac"

    local part_devices=()
    local part_labels=()
    local part_mountpoints=()
    local part_uuids=()
    local part_sizes=()
    local part_count=0
    # The core goal of the shared drive is "still auto-mounted after reboot", which relies on fstab persistence.
    # So do not just check whether the partition is currently mounted -- a udisks auto-mount disappears after reboot.
    # Changed to: only "mounted AND an entry exists in fstab AND the mount point matches" counts as really ready.
    local all_ready=true
    local fail_count=0
    # Partitions that are mounted but downgraded to read-only (ntfs-3g mounts dirty/hibernated volumes as ro)
    local ro_mounts=()

    echo "  Cleaning up invalid fstab entries..."
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
        echo "  ${#bad_entries[@]} invalid entry/entries detected, deleting..."
        sudo cp /etc/fstab "/etc/fstab.toolbox.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null
        for entry in "${bad_entries[@]}"; do
            # Delete by exact match on the first field, no regex, to avoid special characters causing wrong deletions
            fstab_remove_entry "$(echo "$entry" | awk '{print $1}')"
        done
        echo -e "${GREEN}✓ Invalid entries removed${NC}"
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
                echo "  Recovery partition $name is mounted, unmounting..."
                sudo umount "$mountpoint" 2>/dev/null
            fi
            if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ] && [ -d "$mountpoint" ]; then
                if [ -z "$(ls -A "$mountpoint" 2>/dev/null)" ]; then
                    sudo rmdir "$mountpoint" 2>/dev/null && echo "  Removed the empty mount point $mountpoint"
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
            # If mounted, also confirm fstab has an entry matching this UUID exactly (substring matching misjudges; use anchored regex)
            if [ -n "$uuid" ] && grep -qE "^[[:space:]]*UUID=${uuid}[[:space:]]" /etc/fstab 2>/dev/null; then
                # Mounted and in fstab, but also verify this is not a false success at read-only:
                # on a dirty volume ntfs-3g mounts ro without any error, and such a volume must never be
                # reported as "everything is ready".
                if ntfs_mountpoint_is_ro "$mountpoint"; then
                    all_ready=false
                    ro_mounts+=("$mountpoint")
                fi
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
                part_labels+=("${label:-no label}")
                part_mountpoints+=("$mountpoint")
                part_uuids+=("${uuid:-}")
                part_sizes+=("${size:-}")
                ((part_count++))
            fi
        done < <(findmnt -t ntfs,fuseblk,ntfs3 -o SOURCE,FSTYPE,TARGET -n 2>/dev/null)
    fi

    if [ $part_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No matching Windows (NTFS) partition detected.${NC}"
        return
    fi

    echo -e "${CYAN}The following Windows partitions were detected:${NC}"
    for ((i=0; i<part_count; i++)); do
        local mp_display="${part_mountpoints[$i]:-not mounted}"
        echo "  $((i+1)). ${part_devices[$i]}  Label:${part_labels[$i]:-none}  Size:${part_sizes[$i]}  Mount point:${mp_display}"
    done
    echo ""

    echo "Step 5: Cleaning up mounts and fstab entries of non-Windows partitions under /run/media/deck/..."
    local cleaned=0

    # Note: this used to force-unmount all non-NTFS partitions under /run/media/deck/ and delete their fstab entries,
    # which damaged the user's ext4 external drives / USB sticks / Btrfs external disks. The shared-drive feature has no reason to touch them,
    # so it was changed to: only clean up leftover entries in fstab that reference devices which no longer exist; never unmount any partition.
    while IFS= read -r mp; do
        [ -z "$mp" ] && continue
        dev=$(findmnt -n -o SOURCE "$mp" 2>/dev/null)
        fstype=$(findmnt -n -o FSTYPE "$mp" 2>/dev/null)
        if [[ ! "$fstype" =~ ^(ntfs|fuseblk|ntfs3|ntfs-3g)$ ]]; then
            if [ -n "$dev" ] && [ ! -b "$dev" ]; then
                echo "  Cleaning up the stale mount record: $mp ($fstype)"
                if [ -n "$dev" ]; then
                    local _u
                    _u=$(lsblk -n -o UUID "$dev" 2>/dev/null)
                    [ -n "$_u" ] && fstab_remove_entry "UUID=$_u"
                    fstab_remove_entry "$dev"
                fi
                ((cleaned++))
            else
                echo -e "${YELLOW}  Keeping the mounted non-NTFS partition: $mp ($fstype)${NC}"
            fi
        fi
    done < <(findmnt -o TARGET -n -l 2>/dev/null | grep '^/run/media/deck/')

    # Only delete leftover empty directories no longer referenced by fstab, to avoid deleting the user's own empty folders
    for d in /run/media/deck/*; do
        [ -d "$d" ] || continue
        mountpoint -q "$d" 2>/dev/null && continue
        [ -z "$(ls -A "$d" 2>/dev/null)" ] || continue
        if grep -qE "^[[:space:]]*(UUID=|/dev/)[^[:space:]]+[[:space:]]+${d}[[:space:]]" /etc/fstab 2>/dev/null; then
            continue
        fi
        echo "  Removing the leftover empty directory $d"
        sudo rmdir "$d" 2>/dev/null && ((cleaned++))
    done

    while IFS= read -r line; do
        if echo "$line" | grep -qE '^\s*(UUID=|/dev/)\S+\s+/run/media/deck/'; then
            mp=$(echo "$line" | awk '{print $2}')
            fs=$(echo "$line" | awk '{print $3}')
            if [[ ! "$fs" =~ ^(ntfs|fuseblk|ntfs3|ntfs-3g)$ ]]; then
                # Safety restriction: only handle leftover entries whose "device no longer exists".
                # Never unmount/delete a non-NTFS partition that still really exists (such as the user's ext4 external drive,
                # USB stick, Btrfs external disk), otherwise the user's data disk would be damaged.
                local src
                src=$(echo "$line" | awk '{print $1}')
                local dev_exists=1
                if [[ "$src" =~ ^UUID= ]]; then
                    if [ -e "/dev/disk/by-uuid/${src#UUID=}" ]; then dev_exists=0; fi
                elif [[ "$src" =~ ^/dev/ ]]; then
                    if [ -b "$src" ]; then dev_exists=0; fi
                fi
                if [ $dev_exists -eq 1 ]; then
                    echo "  Cleaning up the stale device entry: $mp ($fs)"
                    fstab_remove_entry "$src"
                    ((cleaned++))
                    if [ -d "$mp" ] && [ -z "$(ls -A "$mp" 2>/dev/null)" ]; then
                        sudo rmdir "$mp" 2>/dev/null
                    fi
                else
                    echo -e "${YELLOW}  Keeping the non-NTFS partition entry (device still exists): $mp ($fs)${NC}"
                fi
            fi
        fi
    done < /etc/fstab

    if [ $cleaned -gt 0 ]; then
        echo -e "${GREEN}✓ Cleanup complete${NC}"
    else
        echo "  Nothing to clean up."
    fi
    echo ""

    if $all_ready; then
        echo -e "${GREEN}✅ All Windows partitions are mounted and written to fstab; they will still be mounted automatically after reboot, no action needed.${NC}"
        return
    fi

    # The partitions are mounted but downgraded to read-only: keep going and try to remount them
    # read-write instead of dismissing the user with "everything is ready" as the old code did.
    if [ ${#ro_mounts[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  ${#ro_mounts[@]} partition(s) are currently mounted READ-ONLY:${NC}"
        local _ro_mp
        for _ro_mp in "${ro_mounts[@]}"; do
            echo "    $_ro_mp"
        done
        echo "  A read-only mount means the volume carries the NTFS dirty flag or is hibernated;"
        echo "  even with a correct fstab entry you cannot write any files."
        echo "  We will try to remount it read-write below; if it stays read-only you will get the exact steps."
        echo ""
    fi

    echo "Step 6: Mounting and writing to fstab..."
    for ((i=0; i<part_count; i++)); do
        device="${part_devices[$i]}"
        label="${part_labels[$i]}"
        mountpoint="${part_mountpoints[$i]}"
        uuid="${part_uuids[$i]}"

        echo -e "\n${CYAN}Processing partition $device${NC}"

        # Key point: first decide which mount point this partition should finally use, then handle fstab.
        # Prefer the mount point already present in fstab (to avoid two mount points for the same partition),
        # then the current actual mount point, and only then create a new one from the label/device name.
        local fstab_mp=""
        if [ -n "$uuid" ] && grep -qE "^[[:space:]]*UUID=${uuid}[[:space:]]" /etc/fstab 2>/dev/null; then
            fstab_mp=$(awk -v u="UUID=$uuid" '$1==u {print $2; exit}' /etc/fstab)
        fi

        if [ -n "$fstab_mp" ]; then
            mount_point="$fstab_mp"
            echo "  fstab already has an entry, mount point: $mount_point"
        elif [ -n "$mountpoint" ]; then
            mount_point="$mountpoint"
            echo "  Currently mounted at $mount_point"
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
            echo "  Planned mount point: $mount_point"
        fi
        sudo mkdir -p "$mount_point"
        sudo chown "${CURRENT_USER}:${CURRENT_GROUP}" "$mount_point" 2>/dev/null

        # Write/update fstab: match the UUID exactly with an anchored regex, to avoid substring misjudgement
        if [ -n "$fstab_mp" ]; then
            if [ "$fstab_mp" != "$mount_point" ]; then
                # Already exists but with a different mount point (e.g. the old path is invalid).
                # Note: do not "delete first, then append" -- if a large write fails, the entry would be lost completely.
                # Instead, generate the complete new file at once and atomically replace it with mv, so fstab never has an intermediate state.
                sudo cp /etc/fstab "/etc/fstab.toolbox.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null
                local _tmp="${TEMP_DIR:-/tmp}/fstab_upd.$$"
                mkdir -p "$(dirname "$_tmp")" 2>/dev/null
                {
                    awk -v k="UUID=$uuid" '$1 != k' /etc/fstab 2>/dev/null
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g $(ntfs_mount_opts) 0 0"
                } > "$_tmp" 2>/dev/null && chmod 644 "$_tmp" 2>/dev/null \
                    && sudo cp "$_tmp" /etc/fstab && rm -f "$_tmp" \
                    && echo "  Updated the fstab mount point -> $mount_point" \
                    || { rm -f "$_tmp"; echo -e "${RED}  ✗ Failed to update fstab (the original entry was not changed)${NC}"; ((fail_count++)); continue; }
            else
                echo "  fstab entry is already correct, no change needed."
            fi
        else
            if [ -z "$uuid" ]; then
                echo -e "${YELLOW}  ⚠ This partition has no UUID, skipping the fstab write (it may not be mounted automatically after reboot)${NC}"
            else
                sudo cp /etc/fstab "/etc/fstab.toolbox.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null
                local _tmp2="${TEMP_DIR:-/tmp}/fstab_add.$$"
                mkdir -p "$(dirname "$_tmp2")" 2>/dev/null
                {
                    cat /etc/fstab 2>/dev/null
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g $(ntfs_mount_opts) 0 0"
                } > "$_tmp2" 2>/dev/null && chmod 644 "$_tmp2" 2>/dev/null \
                    && sudo cp "$_tmp2" /etc/fstab && rm -f "$_tmp2" \
                    && echo "  fstab entry added." \
                    || { rm -f "$_tmp2"; echo -e "${RED}  ✗ Failed to write fstab${NC}"; ((fail_count++)); }
            fi
        fi

        if mountpoint -q "$mount_point" 2>/dev/null; then
            if ntfs_mountpoint_is_ro "$mount_point"; then
                # ntfs-3g is a FUSE mount: read-only vs read-write is fixed at mount time, so
                # `mount -o remount,rw` has no effect on it. The only real chance of switching is
                # to unmount and mount again via fstab, which is what we do here.
                echo -e "${YELLOW}  Partition mounted at $mount_point, but read-only; remounting...${NC}"
                if sudo umount "$device" 2>/dev/null; then
                    if sudo mount "$mount_point" 2>/dev/null; then :; else
                        [ -n "$uuid" ] && sudo mount -U "$uuid" "$mount_point" 2>/dev/null
                    fi
                else
                    echo "  (partition is in use and cannot be unmounted; skipping the remount)"
                fi
                if ! mountpoint -q "$mount_point" 2>/dev/null; then
                    # The unmount succeeded but the remount did not: the partition is not mounted at all,
                    # so it must never be reported as a success just because it is "not read-only".
                    echo -e "${RED}  ✗ Remount failed; the partition is currently not mounted.${NC}"
                    # It was at least readable before, do not leave the user worse off than before the
                    # repair: fall back to a read-only mount so the files stay accessible.
                    if sudo mount -o ro "$device" "$mount_point" 2>/dev/null; then
                        echo -e "${YELLOW}    Fell back to a read-only mount, so the files can still be read.${NC}"
                    else
                        echo "    The read-only fallback failed too; run this feature again or mount it manually."
                    fi
                    ((fail_count++))
                elif ntfs_mountpoint_is_ro "$mount_point"; then
                    echo -e "${YELLOW}  ✗ Still read-only, files cannot be written.${NC}"
                    ntfs_explain_readonly "$device" "$mount_point"
                    ((fail_count++))
                else
                    echo -e "${GREEN}  ✓ Remounted read-write: $mount_point${NC}"
                fi
            else
                echo "  Partition mounted at $mount_point"
            fi
        else
            # Record a dmesg baseline so only the messages produced by THIS mount are shown,
            # instead of surfacing every NTFS error accumulated since boot.
            local _dmark _mlog
            _dmark="$(dmesg_line_count)"
            # Pre-mount check: catch "it will only mount read-only" before it happens and explain why
            local _prc=0
            ntfs_probe_writable "$device" || _prc=$?
            if [ "$_prc" -eq 1 ]; then
                echo -e "${YELLOW}  Pre-check: this volume does not currently allow a read-write mount (dirty flag / hibernated / not cleanly unmounted).${NC}"
            fi
            if sudo systemctl daemon-reload 2>/dev/null; then :; fi
            if sudo mount "$mount_point" 2>/dev/null || sudo mount -U "$uuid" "$mount_point" 2>/dev/null; then
                if ntfs_mountpoint_is_ro "$mount_point"; then
                    echo -e "${YELLOW}  ⚠️  Mounted at $mount_point, but the system downgraded it to READ-ONLY${NC}"
                    ntfs_explain_readonly "$device" "$mount_point"
                    ((fail_count++))
                else
                    echo -e "${GREEN}  ✓ Mounted successfully at $mount_point (read-write)${NC}"
                fi
            else
                _mlog="$(dmesg_since "$_dmark")"
                echo -e "${RED}  ✗ Mount failed.${NC}"
                if [ -n "$_mlog" ]; then
                    echo "  dmesg output during this operation:"
                    echo "$_mlog" | grep -iE 'ntfs|fuseblk' | tail -8 | sed 's/^/    /'
                fi
                ntfs_explain_failure "$device" "$mount_point" "$_mlog"
                ((fail_count++))
            fi
        fi
    done
    echo ""
    if [ $fail_count -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Finished, but $fail_count partition(s) failed to mount, please check the error messages above.${NC}"
    else
        echo -e "${GREEN}════════════════ All done ════════════════${NC}"
    fi
}

install_uu_accelerator() {
    # FIX-SOFTWARE: never pipe network content straight into a root shell.
    # https + timeouts + temp file + shell-text validation, then run with sudo directly (sudo prompts for the password).
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install the UU accelerator plugin ════════════════${NC}"
    local url="https://uudeck.com"
    local tmp="$(mktemp "$TEMP_DIR/uudeck.com.XXXXXX.sh" 2>/dev/null)"
    if [ -z "$tmp" ]; then
        echo -e "${RED}✗ Cannot create a temp file; aborted.${NC}"
        return 1
    fi
    echo -e "${CYAN}Downloading and validating the install script (source: $url)...${NC}"
    if ! fs_fetch_shell "$url" "$tmp"; then
        echo -e "${RED}✗ Download failed, or the response is not a valid shell script (e.g. an HTML error page); aborted.${NC}"
        rm -f "$tmp"
        return 1
    fi
    echo -e "${GREEN}✓ Downloaded and validated; running as root now (password prompt follows).${NC}"
    echo -e "${CYAN}Running the downloaded script with sudo...${NC}"
    if sudo sh "$tmp"; then
        echo -e "${GREEN}✓ Install the UU accelerator plugin done.${NC}"
        rm -f "$tmp"
        return 0
    fi
    echo -e "${RED}✗ The install script returned an error; check output above.${NC}"
    rm -f "$tmp"
    return 1
}

install_xunyou_accelerator() {
    # FIX-SOFTWARE: never pipe network content straight into a root shell.
    # https + timeouts + temp file + shell-text validation, then run with sudo directly (sudo prompts for the password).
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install the Xunyou accelerator plugin ════════════════${NC}"
    local url="https://sd.xunyou.com"
    local tmp="$(mktemp "$TEMP_DIR/sd.xunyou.com.XXXXXX.sh" 2>/dev/null)"
    if [ -z "$tmp" ]; then
        echo -e "${RED}✗ Cannot create a temp file; aborted.${NC}"
        return 1
    fi
    echo -e "${CYAN}Downloading and validating the install script (source: $url)...${NC}"
    if ! fs_fetch_shell "$url" "$tmp"; then
        echo -e "${RED}✗ Download failed, or the response is not a valid shell script (e.g. an HTML error page); aborted.${NC}"
        rm -f "$tmp"
        return 1
    fi
    echo -e "${GREEN}✓ Downloaded and validated; running as root now (password prompt follows).${NC}"
    echo -e "${CYAN}Running the downloaded script with sudo...${NC}"
    if sudo sh "$tmp"; then
        echo -e "${GREEN}✓ Install the Xunyou accelerator plugin done.${NC}"
        rm -f "$tmp"
        return 0
    fi
    echo -e "${RED}✗ The install script returned an error; check output above.${NC}"
    rm -f "$tmp"
    return 1
}

install_qiyou_accelerator() {
    # FIX-SOFTWARE: never pipe network content straight into a root shell.
    # https + timeouts + temp file + shell-text validation, then run with sudo directly (sudo prompts for the password).
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install the Qiyou accelerator plugin ════════════════${NC}"
    # FIX-QIYOU: sd.qiyou.cn only serves HTTP (port 443 is closed), and its
    # bootstrap script itself fetches the real installer over plaintext http from
    # static.qiyou.cn. That host supports HTTPS, so fetch the real installer directly:
    # this avoids the dead 443 port and skips the plaintext bootstrap layer entirely.
    local url="https://static.qiyou.cn/upgrade/ljb/plugin/qyplug.sh"
    local tmp="$(mktemp "$TEMP_DIR/qyplug.XXXXXX.sh" 2>/dev/null)"
    if [ -z "$tmp" ]; then
        echo -e "${RED}✗ Cannot create a temp file; aborted.${NC}"
        return 1
    fi
    echo -e "${CYAN}Downloading and validating the install script (source: $url)...${NC}"
    if ! fs_fetch_shell "$url" "$tmp"; then
        echo -e "${RED}✗ Download failed, or the response is not a valid shell script (e.g. an HTML error page); aborted.${NC}"
        rm -f "$tmp"
        return 1
    fi
    echo -e "${GREEN}✓ Downloaded and validated; running as root now (password prompt follows).${NC}"
    echo -e "${CYAN}Running the downloaded script with sudo...${NC}"
    if sudo sh "$tmp"; then
        echo -e "${GREEN}✓ Install the Qiyou accelerator plugin done.${NC}"
        rm -f "$tmp"
        return 0
    fi
    echo -e "${RED}✗ The install script returned an error; check output above.${NC}"
    rm -f "$tmp"
    return 1
}

install_asklink() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ AskLink remote assistance ════════════════${NC}"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        # FIX-SOFTWARE: confirm + check rc + separately confirm user data removal.
        echo -e "${GREEN}AskLink is installed.${NC}"
        echo -e "${YELLOW}Will delete /opt/AskLink and the desktop/system shortcuts.${NC}"
        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        echo -e "${RED}Warning: this removes program files; the config dir may contain user data.${NC}"
        if ! confirm_action; then
            echo -e "${GREEN}Cancelled; keeping AskLink installed.${NC}"
            return 0
        fi
        local fail=0
        if pgrep -f '/opt/AskLink' >/dev/null 2>&1; then
            sudo pkill -f '/opt/AskLink' 2>/dev/null || echo -e "${YELLOW}⚠ Could not stop the process; close it manually and retry${NC}"
        fi
        if ! sudo rm -rf /opt/AskLink; then
            echo -e "${RED}✗ Failed to delete /opt/AskLink${NC}"; fail=1
        fi
        local f
        for f in "$DESKTOP_DIR/AskLink.desktop" "$HOME/Desktop/AskLink.desktop"                  "$HOME/.local/share/applications/AskLink.desktop"; do
            if [ -e "$f" ] && ! rm -f "$f"; then
                echo -e "${RED}✗ Failed to delete $f${NC}"; fail=1
            fi
        done
        if [ -e /usr/share/applications/AskLink.desktop ] && ! sudo rm -f /usr/share/applications/AskLink.desktop; then
            echo -e "${RED}✗ Failed to delete the system shortcut${NC}"; fail=1
        fi
        if [ -d "$HOME/Documents/AskLink" ]; then
            echo ""
            echo -e "${CYAN}Delete the config/user-data directory $HOME/Documents/AskLink?${NC}"
            echo -e "${YELLOW}It may contain login info / settings; deletion is irreversible.${NC}"
            if confirm_action; then
                if ! rm -rf "$HOME/Documents/AskLink"; then
                    echo -e "${RED}✗ Failed to delete the config dir${NC}"; fail=1
                else
                    echo -e "${GREEN}✓ Config directory deleted${NC}"
                fi
            else
                echo -e "${YELLOW}Config directory kept.${NC}"
            fi
        fi
        echo ""
        if [ "$fail" -ne 0 ]; then
            echo -e "${RED}✗ Uninstall had failures; see hints above.${NC}"
            return 1
        fi
        echo -e "${GREEN}✅ AskLink uninstalled.${NC}"
        return 0
    fi

    echo -e "${CYAN}Checking the SteamOS read-only state...${NC}"
    if command -v steamos-readonly &>/dev/null; then
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            echo -e "${CYAN}Disabling read-only mode...${NC}"
            if ! sudo steamos-readonly disable; then
                echo -e "${RED}Failed to disable read-only mode, please run manually: sudo steamos-readonly disable${NC}"
                return 1
            fi
            RO_READONLY_DISABLED_BY_US=1
        else
            echo -e "${GREEN}Read-only mode disabled${NC}"
        fi
    fi

    if ! command -v dpkg &>/dev/null; then
        echo -e "${CYAN}dpkg not detected, installing...${NC}"
        if command -v pacman &>/dev/null; then
            # SteamOS/Holo often leaves leftover /var/lib/dpkg/{available,status}
            # from a previous manual dpkg -i; those files are not owned by any
            # pacman package, so a plain pacman -S dpkg hits "exists in filesystem".
            if ! sudo pacman -S --needed --noconfirm dpkg; then
                echo -e "${YELLOW}Normal install hit file conflicts; retrying with overwrite of /var/lib/dpkg leftovers...${NC}"
                if ! sudo pacman -S --needed --noconfirm --overwrite '/var/lib/dpkg/*' dpkg; then
                    echo -e "${RED}Failed to install dpkg, please run manually:${NC}"
                    echo -e "${RED}  sudo pacman -S --overwrite '/var/lib/dpkg/*' dpkg${NC}"
                    return 1
                fi
            fi
            if ! command -v dpkg &>/dev/null; then
                echo -e "${RED}dpkg still unavailable after install; please check manually.${NC}"
                return 1
            fi
            echo -e "${GREEN}dpkg installation complete${NC}"
        else
            echo -e "${RED}No package manager found, cannot install dpkg. Please install dpkg manually.${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}dpkg already present${NC}"
    fi

    local ASKLINK_URL="https://dl.asklink.com/linux/4.0.33.0/AskLink-4.0.33.0-x86_64.deb"
    local FILENAME="AskLink-4.0.33.0-x86_64.deb"

    echo -e "${CYAN}Download address: ${ASKLINK_URL}${NC}"
    echo -e "${CYAN}Downloading ${FILENAME} ...${NC}"

    cd "$TEMP_DIR" || return
    # FIX-SOFTWARE: add --fail/timeouts; dpkg errors are no longer sent to /dev/null.
    if command -v wget &>/dev/null; then
        wget --show-progress --connect-timeout=15 --timeout=120 --tries=1 "$ASKLINK_URL" -O "$FILENAME"
    else
        curl -L --fail --connect-timeout 15 --max-time 120 --progress-bar "$ASKLINK_URL" -o "$FILENAME"
    fi
    if [ $? -ne 0 ] || [ ! -s "$FILENAME" ]; then
        echo -e "${RED}Download failed or the file is empty.${NC}"
        rm -f "$FILENAME"
        return 1
    fi

    echo -e "${CYAN}Installing (dpkg output is no longer suppressed; real errors will show)...${NC}"
    if ! sudo dpkg --force-depends -i "$FILENAME"; then
        echo -e "${RED}✗ dpkg failed; see the real error above.${NC}"
        echo -e "${YELLOW}  Usually a missing dependency; install it (sudo pacman -S ...) and retry.${NC}"
        rm -f "$FILENAME"
        return 1
    fi
    rm -f "$FILENAME"

    if [ ! -x /opt/AskLink/AskLink ] && ! command -v asklink &>/dev/null; then
        echo -e "${RED}✗ dpkg reported success but no runnable AskLink was found; treating as failed.${NC}"
        return 1
    fi
    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}✅ AskLink installed successfully!${NC}"
        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        local DESKTOP_FILE="$DESKTOP_DIR/AskLink.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=AskLink
Comment=Remote assistance tool
Exec=/opt/AskLink/AskLink
Icon=AskLink
Terminal=false
Categories=Network;RemoteAccess;
EOF
        chmod +x "$DESKTOP_FILE"
        echo -e "${GREEN}✓ Desktop shortcut created.${NC}"
    else
        echo -e "${RED}Installation failed, please check manually.${NC}"
        return 1
    fi

    echo -e "${GREEN}AskLink installation finished.${NC}"
}

watt_toolkit_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}═══════ Install/Update Watt Toolkit (Steam++) ═══════${NC}"
    echo ""

    local INSTALL_DIR="$HOME/Watt Toolkit"
    local DESKTOP_DIR="$HOME/Desktop"
    local DOWNLOAD_URL="https://gitee.com/rmbgame/SteamTools/releases/download/3.1.0/Steam%20%20_v3.1.0_linux_x64.tgz"
    local VERSION="3.1.0"
    local trust_now=""

    for cmd in curl sudo unzip tar; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}Error: $cmd command not found, please install it first.${NC}"
            return 1
        fi
    done

    local installed_version=""
    local has_install=false
    if [ -d "$INSTALL_DIR" ]; then
        has_install=true
        if [ -f "$INSTALL_DIR/.version" ]; then
            installed_version=$(cat "$INSTALL_DIR/.version")
            echo -e "${CYAN}Currently installed version: ${installed_version}${NC}"
        else
            echo -e "${YELLOW}Install directory found, but version number could not be read.${NC}"
        fi
    else
        echo -e "${YELLOW}No installed Watt Toolkit detected.${NC}"
    fi

    if $has_install; then
        # FIX-WATT: .version may be "v3.1.0" while the download constant is
        # "3.1.0"; strip a leading v so the same version is not reported as new.
        local installed_cmp="${installed_version#v}"
        if [ -n "$installed_version" ] && [ "$installed_cmp" = "$VERSION" ]; then
            echo -e "${GREEN}✅ Already up to date (${installed_version}); nothing to do.${NC}"
            return 0
        fi
        # 已安装但版本不同或无法读取 → 先询问再下载，避免静默覆盖
        if [ -n "$installed_version" ]; then
            echo -e "${YELLOW}New version detected ${VERSION} (currently installed: ${installed_version}).${NC}"
        else
            echo -e "${YELLOW}Will re-download and install version ${VERSION}.${NC}"
        fi
        read -n1 -p "Press Enter or A to continue download/install; any other key cancels: " confirm < /dev/tty
        echo
        if [[ -n "$confirm" && ! "$confirm" =~ [Aa] ]]; then
            echo "Operation cancelled."
            return 0
        fi
    fi

    # FIX-SOFTWARE: download into a mktemp dir + curl --fail/timeouts; validate key
    # files BEFORE touching the old install; abort on mv/mkdir failure; write .version last.
    echo -e "${GREEN}Will install version: ${VERSION}${NC}"
    echo "Downloading ${DOWNLOAD_URL} ..."

    local temp_dir
    temp_dir="$(mktemp -d /tmp/watt_toolkit_install.XXXXXXXX 2>/dev/null)" || {
        echo -e "${RED}✗ Cannot create a temp dir; aborted (old install untouched).${NC}"; return 1; }
    # FIX-WATT: never cd into the temp dir. It is removed at the end of the
    # install; if the shell still sits in it, every later sudo prints hundreds of
    # "job-working-directory: getcwd" errors. Use absolute paths throughout.
    local filename="$temp_dir/Steam_v${VERSION}_linux_x64.tgz"
    if ! curl -L --fail --connect-timeout 15 --max-time 300 --progress-bar -o "$filename" "$DOWNLOAD_URL"; then
        echo -e "${RED}Download failed, please check your network and try again.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if [ ! -s "$filename" ]; then
        echo -e "${RED}Downloaded file is empty; aborted.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi

    echo -e "${CYAN}Extracting...${NC}"
    local temp_extract="$temp_dir/extracted"
    if ! mkdir -p "$temp_extract"; then
        echo -e "${RED}✗ Failed to create the extraction dir; aborted.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if ! tar -xzf "$filename" -C "$temp_extract"; then
        echo -e "${RED}Extraction failed.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi

    local content_count=$(ls -1 "$temp_extract" | wc -l)
    local first_item=$(ls -1 "$temp_extract" | head -1)
    local src_root="$temp_extract"
    if [ "$content_count" -eq 1 ] && [ -d "$temp_extract/$first_item" ]; then
        src_root="$temp_extract/$first_item"
    fi

    # Validate key files in the staging area first (DLL present, dotnet executable).
    local stage_dotnet="$src_root/dotnet/dotnet"
    local stage_dll="$src_root/assemblies/Steam++.dll"
    if [ ! -f "$stage_dll" ] || [ ! -x "$stage_dotnet" ]; then
        echo -e "${RED}Error: staged contents lack key files or dotnet is not executable; aborted (old install untouched).${NC}"
        echo "  Expected: $stage_dll present, $stage_dotnet executable (-x)"
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    echo -e "${GREEN}✓ Key files validated (DLL + executable dotnet)${NC}"

    # FIX-WATT: 备份目标必须与安装目录位于同一文件系统（/tmp 与 /home 常是不同设备），
    # 且压缩包里的 dotnet 带 security.capability xattr —— mv/cp -a 在跨设备或
    # 不允许设置 capability 时会报 "setting attribute 'security.capability'"。
    # 因此：备份放到 $HOME 下，用 cp -a 复制而非 mv；新文件先装到同文件系统的
    # 暂存目录，用 cp -r --no-preserve=xattr 避免把 capability 带过去。
    local backup_dir="$HOME/.watt_toolkit_backup.$$"
    local had_backup=0
    if [ -d "$INSTALL_DIR" ]; then
        echo "检测到旧安装目录，先备份再替换..."
        if ! cp -a "$INSTALL_DIR" "$backup_dir" 2>/dev/null; then
            echo -e "${RED}✗ 备份旧目录失败，已中止（旧安装未动）。${NC}"
            rm -rf "$backup_dir" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
        had_backup=1
    fi
    local stage_install="$HOME/.watt_toolkit_new.$$"
    rm -rf "$stage_install" 2>/dev/null
    if ! mkdir -p "$stage_install"; then
        echo -e "${RED}✗ 创建暂存安装目录失败，已中止（旧安装未动）。${NC}"
        [ "$had_backup" -eq 1 ] && rm -rf "$backup_dir" 2>/dev/null
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if cp -r --no-preserve=xattr "$src_root"/. "$stage_install"/ 2>/dev/null || cp -r "$src_root"/. "$stage_install"/; then
        :
    else
        echo -e "${RED}✗ 复制安装文件失败，已中止（旧安装未动）。${NC}"
        rm -rf "$stage_install" "$backup_dir" 2>/dev/null
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if [ ! -f "$stage_install/assemblies/Steam++.dll" ] || [ ! -x "$stage_install/dotnet/dotnet" ]; then
        echo -e "${RED}✗ 暂存内容缺少关键文件或 dotnet 不可执行，已中止（旧安装未动）。${NC}"
        rm -rf "$stage_install" "$backup_dir" 2>/dev/null
        cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
        return 1
    fi
    if [ -d "$INSTALL_DIR" ]; then
        if ! mv "$INSTALL_DIR" "$INSTALL_DIR.old.$$" 2>/dev/null; then
            echo -e "${RED}✗ 移走旧安装目录失败，已中止（旧安装未动）。${NC}"
            rm -rf "$stage_install" "$backup_dir" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
        if ! mv "$stage_install" "$INSTALL_DIR" 2>/dev/null; then
            echo -e "${RED}✗ 移入新版本失败，正在恢复旧版本...${NC}"
            mv "$INSTALL_DIR.old.$$" "$INSTALL_DIR" 2>/dev/null
            rm -rf "$stage_install" "$backup_dir" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
        rm -rf "$INSTALL_DIR.old.$$" 2>/dev/null
    else
        if ! mv "$stage_install" "$INSTALL_DIR" 2>/dev/null; then
            echo -e "${RED}✗ 移入新版本失败，已中止。${NC}"
            rm -rf "$stage_install" 2>/dev/null
            cd "$HOME" 2>/dev/null; rm -rf "$temp_dir"
            return 1
        fi
    fi
    rm -rf "$backup_dir" 2>/dev/null
    rm -rf "$temp_dir"

    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local desktop_file="$DESKTOP_DIR/Watt_Toolkit.desktop"
    local dotnet_root="$INSTALL_DIR/dotnet"
    local dll_path="$INSTALL_DIR/assemblies/Steam++.dll"
    local icon_path="$INSTALL_DIR/Icons/Watt-Toolkit.png"

    # Re-check: dotnet must be executable (-x), not merely present (-f).
    if [ ! -f "$dll_path" ] || [ ! -x "$dotnet_root/dotnet" ]; then
        echo -e "${RED}Error: key files missing or dotnet not executable after install; treating as failed.${NC}"
        echo "Please inspect the contents of $INSTALL_DIR."
        return 1
    fi
    # Launcher compatibility: Steam++.sh or running the DLL via dotnet directly.
    if [ ! -x "$INSTALL_DIR/Steam++.sh" ] && [ ! -x "$dotnet_root/dotnet" ]; then
        echo -e "${YELLOW}⚠ No Steam++.sh and dotnet unusable; the desktop shortcut may not launch.${NC}"
    fi
    # Write .version only after everything succeeded.
    if ! echo "$VERSION" > "$INSTALL_DIR/.version"; then
        echo -e "${RED}✗ Failed to write .version.${NC}"
        return 1
    fi

    cat > "$desktop_file" << EOF
[Desktop Entry]
Categories=Network;Game;
Comment[zh_CN]=Steam Toolbox
Comment=Steam Toolbox
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
    echo -e "${GREEN}✓ Desktop shortcut created: ${desktop_file}${NC}"

    echo ""
    echo -e "${GREEN}✅ Watt Toolkit ${VERSION} installed!${NC}"
    echo -e "${GREEN}Install directory: ${INSTALL_DIR}${NC}"
    echo ""
    echo -e "${YELLOW}Tips:${NC}"
    echo "  · Please launch Watt Toolkit from the desktop."
    echo "  · Before first acceleration, let the plugin generate a certificate: click Accelerate once under Network Acceleration."
    echo "  · After the certificate is generated, run Trust Certificate in this tool so acceleration does not fail."
    echo ""

    # ---------- 安装后直接进入证书信任 ----------
    echo -e "${YELLOW}Acceleration also needs a trusted certificate, or HTTPS accel will fail.${NC}"
    read -n1 -p "Trust the acceleration certificate now? [Enter/A=yes, other=later] " trust_now < /dev/tty
    echo
    if [[ -z "$trust_now" || "$trust_now" =~ [Aa] ]]; then
        watt_toolkit_trust_cert skip_clear
    else
        echo -e "${CYAN}Skipped. You can run it later under Network Tools → Watt Toolkit (Steam++) → Trust Certificate.${NC}"
    fi
}

watt_toolkit_trust_cert() {
    # FIX-SOFTWARE: never chmod a+w /etc/hosts (world-writable).
    # Validate CA:TRUE + fingerprint, store them in a record file for exact removal.
    [ "${1:-}" = "skip_clear" ] || clear
    echo -e "${YELLOW}═══════ Trust Watt Toolkit (Steam++) acceleration certificate ═══════${NC}"
    echo ""
    echo "Acceleration needs two system-level changes:"
    echo "  1. Add Watt Toolkit's self-signed root CA to the system trust store (otherwise HTTPS acceleration fails)"
    echo "  2. Allow the current user to write /etc/hosts (via temporary sudo, never a permanent world-writable bit)"
    echo ""
    echo -e "${YELLOW}Security note:${NC}"
    echo "  This certificate is a root CA generated locally by Watt Toolkit (CN=SteamTools Certificate)."
    echo "  Trusting it means a process with the matching private key can decrypt local HTTPS traffic."
    echo "  When you stop using Watt Toolkit, run the uninstall feature to remove this trust."
    echo ""

    local CERT_DIR="$HOME/.local/share/Steam++/Plugins/Accelerator"
    local CERT_FILE="$CERT_DIR/SteamTools.Certificate.cer"
    local RECORD_FILE="$HOME/.local/share/Steam++/watt_toolkit_trust.record"
    local INSTALL_DIR="$HOME/Watt Toolkit"
    local launch_now="" retry="" confirm=""
    local CERT_FP=""

    if ! command -v trust >/dev/null 2>&1; then
        echo -e "${RED}✗ trust command not found (from p11-kit); cannot write to the system trust store.${NC}"
        echo -e "${YELLOW}  Try: sudo pacman -S p11-kit${NC}"
        return 1
    fi

    # ---------- Certificate presence ----------
    if [ ! -f "$CERT_FILE" ]; then
        echo -e "${YELLOW}Acceleration certificate not found:${NC}"
        echo "  $CERT_FILE"
        echo ""
        echo "This certificate is generated the first time Watt Toolkit runs; it is not in the package."
        echo "Please start Watt Toolkit, click Accelerate once under Network Acceleration, then the certificate will appear."
        echo ""
        local start_cmd=""
        if [ -x "$INSTALL_DIR/Steam++.sh" ]; then
            start_cmd="$INSTALL_DIR/Steam++.sh"
        elif [ -f "$INSTALL_DIR/assemblies/Steam++.dll" ] && [ -x "$INSTALL_DIR/dotnet/dotnet" ]; then
            start_cmd="$INSTALL_DIR/dotnet/dotnet"
        fi
        if [ -n "$start_cmd" ]; then
            read -r -n1 -p "Launch Watt Toolkit now? [Enter/A=launch, other=skip] " launch_now < /dev/tty || launch_now="q"
            echo
            if [[ -z "$launch_now" || "$launch_now" =~ [Aa] ]]; then
                if [ "$start_cmd" = "$INSTALL_DIR/dotnet/dotnet" ]; then
                    (cd "$INSTALL_DIR" && nohup env DOTNET_ROOT="$INSTALL_DIR/dotnet" "$start_cmd" "$INSTALL_DIR/assemblies/Steam++.dll" >/dev/null 2>&1 &)
                else
                    nohup "$start_cmd" >/dev/null 2>&1 &
                fi
                echo -e "${GREEN}✓ Watt Toolkit launched${NC}"
                echo ""
            fi
        else
            echo -e "${YELLOW}No Steam++.sh / dotnet launcher found; please launch from the desktop shortcut.${NC}"
            echo ""
        fi
        local wait_count=0
        while [ ! -f "$CERT_FILE" ]; do
            wait_count=$((wait_count + 1))
            if [ "$wait_count" -gt 30 ]; then
                echo -e "${YELLOW}Timed out waiting; exited. Rerun this after the certificate is generated.${NC}"
                return 0
            fi
            read -r -n1 -p "After clicking Accelerate once in Watt Toolkit, press Enter to re-check (Q to abort): " retry < /dev/tty || { echo; echo -e "${CYAN}Input unavailable; exited.${NC}"; return 0; }
            echo
            if [[ "${retry:-}" =~ [Qq] ]]; then
                echo -e "${CYAN}Aborted. You can run Trust Certificate again after generating the cert.${NC}"
                return 0
            fi
        done
        echo ""
    fi

    echo -e "${GREEN}✓ Certificate found: $CERT_FILE${NC}"

    # ---------- Validate: must be CA:TRUE, and record the fingerprint ----------
    if command -v openssl >/dev/null 2>&1; then
        local cert_subject cert_end bc
        if ! cert_subject=$(openssl x509 -in "$CERT_FILE" -noout -subject 2>/dev/null); then
            echo -e "${RED}✗ Certificate could not be parsed; file may be corrupt.${NC}"
            return 1
        fi
        echo "  $cert_subject"
        bc=$(openssl x509 -in "$CERT_FILE" -noout -text 2>/dev/null | grep -A1 "Basic Constraints" | tr '\n' ' ')
        if ! printf '%s' "$bc" | grep -qi "CA:TRUE"; then
            echo -e "${RED}✗ Not a CA certificate (Basic Constraints CA:TRUE missing); refusing to trust it.${NC}"
            echo -e "${YELLOW}  Only Watt Toolkit's own generated root CA should be trusted.${NC}"
            return 1
        fi
        echo -e "${GREEN}  ✓ Basic Constraints: CA:TRUE${NC}"
        cert_end=$(openssl x509 -in "$CERT_FILE" -noout -enddate 2>/dev/null | cut -d= -f2)
        [ -n "$cert_end" ] && echo "  Valid until: $cert_end"
        if ! openssl x509 -in "$CERT_FILE" -noout -checkend 0 >/dev/null 2>&1; then
            echo -e "${RED}✗ Certificate expired; regenerate it inside Watt Toolkit first.${NC}"
            return 1
        fi
        CERT_FP=$(openssl x509 -in "$CERT_FILE" -noout -fingerprint -sha256 2>/dev/null | cut -d= -f2 | tr -d ':' | tr 'A-F' 'a-f')
        if [ -z "$CERT_FP" ]; then
            echo -e "${RED}✗ Cannot read the certificate fingerprint; aborted.${NC}"
            return 1
        fi
        echo "  SHA256 fingerprint: $CERT_FP"
    else
        if ! grep -q "BEGIN CERTIFICATE" "$CERT_FILE" 2>/dev/null; then
            echo -e "${RED}✗ File is not a valid PEM certificate; aborted.${NC}"
            return 1
        fi
        echo -e "${YELLOW}⚠ openssl not available; cannot verify CA:TRUE / fingerprint.${NC}"
        echo -e "${YELLOW}  Install openssl and retry so uninstall can remove the cert by exact fingerprint.${NC}"
    fi

    local already_trusted=false
    if trust list 2>/dev/null | grep -qi "SteamTools Certificate"; then
        already_trusted=true
        echo ""
        echo -e "${CYAN}Certificate already in the system trust store; this run will overwrite it.${NC}"
    fi

    echo ""
    read -r -n1 -p "Press Enter or A to write the system trust store; any other key cancels: " confirm < /dev/tty || confirm="q"
    echo
    if [[ -n "$confirm" && ! "$confirm" =~ [Aa] ]]; then
        echo -e "${GREEN}Cancelled; no changes made.${NC}"
        return 0
    fi

    if ! ensure_writable; then return 1; fi

    # ---------- Save original hosts permissions ----------
    local HOSTS_PERM=""
    HOSTS_PERM=$(stat -c %a /etc/hosts 2>/dev/null)
    [ -z "$HOSTS_PERM" ] && HOSTS_PERM="644"
    echo -e "${CYAN}Original /etc/hosts mode: $HOSTS_PERM (recorded for restore on uninstall)${NC}"

    # ---------- Write trust store ----------
    echo ""
    echo -e "${CYAN}Writing certificate into the system trust store...${NC}"
    # FIX-WATT: `sudo trust anchor --store` writes to root's private anchor
    # location, which the user's `trust list` cannot see, and it does not refresh
    # the system CA bundle -- so it reports success while HTTPS acceleration still
    # fails. Write explicitly to the system anchors dir, refresh the bundle, then
    # verify with openssl that the trust really works.
    local ANCHOR_DIR="/etc/ca-certificates/trust-source/anchors"
    local ANCHOR_FILE="$ANCHOR_DIR/SteamTools.Certificate.crt"
    if [ ! -d "$ANCHOR_DIR" ]; then
        if ! sudo mkdir -p "$ANCHOR_DIR" 2>/dev/null; then
            echo -e "${RED}✗ Cannot create the system certificate directory $ANCHOR_DIR.${NC}"
            return 1
        fi
    fi
    if ! sudo cp "$CERT_FILE" "$ANCHOR_FILE" 2>/dev/null; then
        echo -e "${RED}✗ Failed to write to the system certificate directory; check the output above.${NC}"
        return 1
    fi
    sudo chmod 644 "$ANCHOR_FILE" 2>/dev/null
    sudo trust anchor --store "$CERT_FILE" 2>/dev/null || true
    if command -v update-ca-trust >/dev/null 2>&1; then
        if ! sudo update-ca-trust 2>/dev/null; then
            echo -e "${YELLOW}⚠ Failed to refresh the CA bundle; run sudo update-ca-trust later.${NC}"
        fi
    fi
    local TRUST_OK=0
    if command -v openssl >/dev/null 2>&1 && [ -f /etc/ca-certificates/extracted/tls-ca-bundle.pem ]; then
        if openssl verify -CAfile /etc/ca-certificates/extracted/tls-ca-bundle.pem "$CERT_FILE" >/dev/null 2>&1; then
            TRUST_OK=1
        fi
    fi
    if [ "$TRUST_OK" -eq 1 ]; then
        echo -e "${GREEN}✓ Confirmed the certificate is trusted by the system (openssl verify passed)${NC}"
    else
        echo -e "${YELLOW}⚠ Could not confirm the certificate is trusted; HTTPS acceleration may still report certificate errors.${NC}"
        echo "    Check manually: openssl verify -CAfile /etc/ca-certificates/extracted/tls-ca-bundle.pem $CERT_FILE"
    fi

    # ---------- Record file: hosts mode + cert fingerprint ----------
    if ! mkdir -p "$(dirname "$RECORD_FILE")" 2>/dev/null; then
        echo -e "${RED}✗ Cannot create the record directory; aborted (uninstall would be unable to restore).${NC}"
        return 1
    fi
    {
        echo "HOSTS_PERM=$HOSTS_PERM"
        echo "CERT_FP=$CERT_FP"
        echo "CERT_FILE=$CERT_FILE"
    } > "$RECORD_FILE" || {
        echo -e "${RED}✗ Cannot write $RECORD_FILE; aborted.${NC}"
        return 1
    }
    chmod 600 "$RECORD_FILE" 2>/dev/null || true

    # ---------- hosts writable: temporary sudo, never permanent a+w ----------
    # Give only the owner write access and strip group/other write bits.
    echo ""
    echo -e "${CYAN}Configuring /etc/hosts write access (owner only, via temporary sudo)...${NC}"
    local hosts_fail=0
    if ! sudo chown "$CURRENT_USER":"$CURRENT_GROUP" /etc/hosts 2>/dev/null; then
        echo -e "${YELLOW}⚠ Could not change /etc/hosts owner; acceleration may need manual authorization.${NC}"
        hosts_fail=1
    fi
    if ! sudo chmod u+w,go-w /etc/hosts 2>/dev/null; then
        echo -e "${YELLOW}⚠ Could not adjust /etc/hosts permissions; acceleration may need manual authorization.${NC}"
        hosts_fail=1
    fi
    if ! [ -w /etc/hosts ]; then
        echo -e "${YELLOW}⚠ /etc/hosts is still not writable; acceleration may fail to update hosts.${NC}"
        hosts_fail=1
    fi
    local hosts_perm
    hosts_perm=$(stat -c '%A %U:%G' /etc/hosts 2>/dev/null)
    [ -n "$hosts_perm" ] && echo "  Current permissions/owner: $hosts_perm"

    echo ""
    if [ "$hosts_fail" -ne 0 ] || [ "$TRUST_OK" -ne 1 ]; then
        echo -e "${YELLOW}⚠ The certificate trust flow finished, but some items did not take effect; see the hints above.${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Acceleration certificate trusted${NC}"
    echo -e "${YELLOW}Tip:${NC}"
    echo "  · Open browsers must be restarted to reload the system certificate store"
    echo "  · Original hosts mode $HOSTS_PERM and the cert fingerprint were saved to $RECORD_FILE"
    echo "  · Uninstall restores from that record instead of blindly forcing 644"
    if $already_trusted; then
        echo "  · This was an overwrite update; the old certificate was replaced"
    fi
}

watt_toolkit_uninstall() {
    # FIX-SOFTWARE: keep cleaning the root CA / hosts even if the program dir is gone;
    # restore hosts from the record file, remove the cert by exact fingerprint, report failures.
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Uninstall Watt Toolkit ══════════════${NC}"
    local INSTALL_DIR="$HOME/Watt Toolkit"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local RECORD_FILE="$HOME/.local/share/Steam++/watt_toolkit_trust.record"
    local cert_dir="$HOME/.local/share/Steam++/Plugins/Accelerator"
    local cert_file="$cert_dir/SteamTools.Certificate.cer"
    local confirm=""
    local HOSTS_PERM="" CERT_FP="" REC_CERT_FILE=""

    if [ -f "$RECORD_FILE" ]; then
        while IFS='=' read -r rk rv; do
            case "$rk" in
                HOSTS_PERM) HOSTS_PERM="$rv" ;;
                CERT_FP) CERT_FP="$rv" ;;
                CERT_FILE) REC_CERT_FILE="$rv" ;;
            esac
        done < "$RECORD_FILE"
    fi
    [ -n "$REC_CERT_FILE" ] && cert_file="$REC_CERT_FILE"

    local install_exists=false
    [ -d "$INSTALL_DIR" ] && install_exists=true
    if ! $install_exists; then
        echo -e "${YELLOW}Program directory not found, but certificate trust and /etc/hosts permissions will still be cleaned.${NC}"
    fi

    echo -e "${CYAN}The following actions will be performed:${NC}"
    $install_exists && echo "  · Delete directory: $INSTALL_DIR"
    echo "  · Delete desktop shortcut: $DESKTOP_DIR/Watt_Toolkit.desktop"
    echo "  · Remove the SteamTools root CA from the system trust store (matched by SHA256 fingerprint when recorded)"
    echo "  · Restore /etc/hosts permissions${HOSTS_PERM:+ (original mode $HOSTS_PERM)}"
    echo ""
    echo -e "${YELLOW}Warning: the directory may contain user data; system changes need sudo.${NC}"
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}Cancelled; no changes made.${NC}"
        return 0
    fi

    local fail_count=0
    # ---------- Delete program dir (never follow a symlink) ----------
    if $install_exists; then
        if [ -L "$INSTALL_DIR" ]; then
            echo -e "${RED}✗ $INSTALL_DIR is a symlink; refusing to delete, check manually.${NC}"
            fail_count=$((fail_count + 1))
        elif rm -rf "$INSTALL_DIR"; then
            echo -e "${GREEN}✓ Install directory deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete install directory${NC}"
            fail_count=$((fail_count + 1))
        fi
    fi

    # ---------- Desktop shortcut (XDG + legacy path) ----------
    local df
    for df in "$DESKTOP_DIR/Watt_Toolkit.desktop" "$HOME/Desktop/Watt_Toolkit.desktop"; do
        if [ -e "$df" ] || [ -L "$df" ]; then
            if rm -f "$df"; then
                echo -e "${GREEN}✓ Desktop shortcut deleted: $df${NC}"
            else
                echo -e "${RED}✗ Failed to delete desktop shortcut: $df${NC}"
                fail_count=$((fail_count + 1))
            fi
        fi
    done

    # ---------- System-level cleanup (always) ----------
    echo ""
    echo -e "${CYAN}Cleaning system-level changes...${NC}"
    if ! ensure_writable; then
        fail_count=$((fail_count + 1))
    else
        # Remove by exact fingerprint, not merely by display name
        local removed=false fp=""
        fs_cert_fp() {
            command -v openssl >/dev/null 2>&1 || return 1
            openssl x509 -in "$1" -noout -fingerprint -sha256 2>/dev/null \
                | cut -d= -f2 | tr -d ':' | tr 'A-F' 'a-f'
        }
        # FIX-WATT: the trust feature explicitly wrote
        # /etc/ca-certificates/trust-source/anchors/SteamTools.Certificate.crt;
        # remove it first or update-ca-trust will keep trusting it after uninstall.
        if [ -f /etc/ca-certificates/trust-source/anchors/SteamTools.Certificate.crt ]; then
            if sudo rm -f /etc/ca-certificates/trust-source/anchors/SteamTools.Certificate.crt 2>/dev/null; then
                echo -e "${GREEN}✓ Removed the system certificate anchor SteamTools.Certificate.crt${NC}"
                removed=true
            else
                echo -e "${YELLOW}⚠ Failed to remove the system certificate anchor${NC}"
                fail_count=$((fail_count + 1))
            fi
        fi
        local cand anchor_dirs=(
            /etc/pki/ca-trust/source/anchors
            /etc/ca-certificates/trust-source/anchors
            "$HOME/.local/share/p11-kit/anchors"
        )
        if [ -n "$CERT_FP" ]; then
            echo "  Target fingerprint: $CERT_FP"
            if [ -f "$cert_file" ]; then
                fp="$(fs_cert_fp "$cert_file")"
                if [ -n "$fp" ] && [ "$fp" = "$CERT_FP" ]; then
                    if sudo trust anchor --remove "$cert_file" 2>/dev/null; then
                        echo -e "${GREEN}✓ Removed cert file by fingerprint: $cert_file${NC}"
                        removed=true
                    fi
                fi
            fi
            for ad in "${anchor_dirs[@]}"; do
                [ -d "$ad" ] || continue
                for cand in "$ad"/*; do
                    [ -f "$cand" ] || continue
                    fp="$(fs_cert_fp "$cand")" || continue
                    if [ "$fp" = "$CERT_FP" ]; then
                        if sudo trust anchor --remove "$cand" 2>/dev/null; then
                            echo -e "${GREEN}✓ Removed anchor by fingerprint: $cand${NC}"
                            removed=true
                        else
                            echo -e "${YELLOW}⚠ Failed to remove anchor: $cand${NC}"
                            fail_count=$((fail_count + 1))
                        fi
                    fi
                done
            done
            if ! $removed; then
                echo -e "${YELLOW}⚠ No anchor matched that fingerprint (it may have been removed already).${NC}"
            fi
        else
            # Legacy: no fingerprint recorded; fall back to an exact pkcs11 id, not just the label
            echo -e "${YELLOW}⚠ No fingerprint in the record (old install or openssl missing); using anchor id fallback.${NC}"
            local anchor_id
            anchor_id=$(trust list 2>/dev/null | grep -i -B 1 "label: SteamTools Certificate" \
                        | grep -o 'pkcs11:id=[^;]*;type=cert' | head -1)
            if [ -n "$anchor_id" ] && sudo trust anchor --remove "$anchor_id" 2>/dev/null; then
                echo -e "${GREEN}✓ Certificate removed by anchor id${NC}"
            elif [ -f "$cert_file" ] && sudo trust anchor --remove "$cert_file" 2>/dev/null; then
                echo -e "${GREEN}✓ Certificate removed by cert file${NC}"
            else
                echo -e "${YELLOW}⚠ Automatic removal failed; run manually:${NC}"
                echo "    trust list | grep -i -B1 'SteamTools'"
                echo "    sudo trust anchor --remove '<pkcs11:id=...>'"
                fail_count=$((fail_count + 1))
            fi
        fi

        # ---------- Restore original /etc/hosts mode ----------
        echo -e "${CYAN}Restoring /etc/hosts permissions...${NC}"
        local target_perm="$HOSTS_PERM"
        [ -z "$target_perm" ] && target_perm="644"
        if sudo chmod "$target_perm" /etc/hosts 2>/dev/null; then
            echo -e "${GREEN}✓ /etc/hosts restored to $target_perm${NC}"
        else
            echo -e "${YELLOW}⚠ Restore failed; run manually: sudo chmod $target_perm /etc/hosts${NC}"
            fail_count=$((fail_count + 1))
        fi
        if ! sudo chown root:root /etc/hosts 2>/dev/null; then
            echo -e "${YELLOW}⚠ Could not restore /etc/hosts owner to root; run: sudo chown root:root /etc/hosts${NC}"
            fail_count=$((fail_count + 1))
        fi
        local hosts_perm
        hosts_perm=$(stat -c '%A' /etc/hosts 2>/dev/null)
        [ -n "$hosts_perm" ] && echo "  Current permissions: $hosts_perm"

        if command -v update-ca-trust >/dev/null 2>&1; then
            if ! sudo update-ca-trust 2>/dev/null; then
                echo -e "${YELLOW}⚠ Failed to refresh the CA bundle (you can run sudo update-ca-trust later).${NC}"
            fi
        fi
    fi

    if [ -f "$RECORD_FILE" ]; then
        rm -f "$RECORD_FILE" && echo -e "${GREEN}✓ Record file removed${NC}"
    fi

    echo ""
    if [ "$fail_count" -gt 0 ]; then
        echo -e "${RED}✗ Uninstall finished with $fail_count failure(s); see the hints above.${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Watt Toolkit uninstalled; certificate and hosts permissions restored.${NC}"
    return 0
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
    echo -e "${YELLOW}════════════════ Install/Update ${DISPLAY_NAME} ════════════════${NC}"
    echo ""

    for cmd in curl sudo unzip python3; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}Error: $cmd command not found, please install it first.${NC}"
            return 1
        fi
    done

    echo -e "${CYAN}Fetching version information from GitHub...${NC}"
    local releases_json=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases")
    if [ -z "$releases_json" ]; then
        echo -e "${RED}Error: cannot connect to the GitHub API, please check your network.${NC}"
        return 1
    fi
    if ! [[ "$releases_json" == \[* ]]; then
        echo -e "${RED}Error: the GitHub API returned an abnormal response (the repository may have no Release, or the network is limited).${NC}"
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
        echo -e "${RED}Error: cannot parse the version information.${NC}"
        return 1
    fi

    local stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
    local prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

    local latest_stable=""
    if [ -n "$stable_list" ]; then
        # The GitHub API returns results newest-first, so the first stable release is the latest
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
            echo -e "${CYAN}Currently installed version: ${local_version}${NC}"
        else
            echo -e "${YELLOW}Installed, but the version number cannot be read.${NC}"
        fi
    else
        echo -e "${YELLOW}${DISPLAY_NAME} is not installed.${NC}"
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
        labels+=("Stable version $latest_stable")
    fi
    if [ "$show_prerelease" = true ]; then
        options+=("$latest_prerelease")
        labels+=("Pre-release version $latest_prerelease")
    fi

    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}Error: no version found.${NC}"
        return 1
    fi

    local target_version=""

    if [ -z "$local_version" ]; then
        while true; do
            clear
            echo -e "${YELLOW}════════════════ Install/Update ${DISPLAY_NAME} ════════════════${NC}"
            echo ""
            echo -e "${CYAN}Fetching version information from GitHub...${NC}"
            echo -e "${YELLOW}${DISPLAY_NAME} is not installed.${NC}"
            echo ""
            if [ ${#options[@]} -eq 1 ]; then
                target_version="${options[0]}"
                echo -e "${GREEN}The only version available will be installed: ${target_version}${NC}"
                break
            else
                echo "Please choose the version to install:"
                for i in "${!options[@]}"; do
                    echo "$((i+1))) ${labels[$i]}"
                done
                read -p "Enter your choice [1-${#options[@]}]: " choice < /dev/tty
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#options[@]} ]; then
                    target_version="${options[$((choice-1))]}"
                    break
                else
                    echo -e "${RED}Invalid choice, please try again.${NC}"
                    sleep 1
                fi
            fi
        done
        echo -e "${GREEN}Version to install: ${target_version}${NC}"
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
                echo -e "${YELLOW}Currently installed pre-release version ${local_version}.${NC}"
                echo -e "${YELLOW}Update detected: pre-release ${new_prerelease}.${NC}"
                echo "Please choose an action:"
                echo "1) Update to the latest pre-release ${new_prerelease}"
                if [ -n "$latest_stable" ]; then
                    echo "2) Switch to the stable version ${latest_stable}"
                    echo "3) Keep the current version"
                else
                    echo "2) Keep the current version"
                fi
                while true; do
                    read -p "Enter your choice: " choice < /dev/tty
                    if [ "$choice" = "1" ]; then
                        target_version="$new_prerelease"
                        echo -e "${GREEN}Updating to the pre-release: ${target_version}${NC}"
                        break
                    elif [ "$choice" = "2" ]; then
                        if [ -n "$latest_stable" ]; then
                            target_version="$latest_stable"
                            echo -e "${GREEN}Switching to the stable version: ${target_version}${NC}"
                            break
                        else
                            echo "Keeping the current version."
                            return 0
                        fi
                    elif [ -n "$latest_stable" ] && [ "$choice" = "3" ]; then
                        echo "Keeping the current version."
                        return 0
                    else
                        echo -e "${RED}Invalid choice, please try again.${NC}"
                    fi
                done
            elif [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}Currently installed pre-release version ${local_version}.${NC}"
                echo -e "${YELLOW}Switch to the stable version ${latest_stable}?${NC}"
                read -n1 -p "Press Enter or A to switch, any other key to keep: " switch_choice < /dev/tty
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}Switching to the stable version: ${target_version}${NC}"
                else
                    echo "Keeping the current version."
                    return 0
                fi
            else
                echo -e "${GREEN}Already the latest pre-release ${local_version}, and there is no stable version to switch to.${NC}"
                return 0
            fi
        else
            # Compare the local version with the latest stable release first (stable updates must also be detected when there is no pre-release)
            local stable_num=$(echo "$local_version" | sed 's/^v//')
            local latest_stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local higher_stable=$(printf '%s\n' "$stable_num" "$latest_stable_num" | sort -V | tail -1)
            if [ -n "$latest_stable" ] && [ "$higher_stable" = "$latest_stable_num" ] && [ "$stable_num" != "$latest_stable_num" ]; then
                echo -e "${YELLOW}New version detected: stable ${latest_stable} (currently ${local_version}).${NC}"
                read -n1 -p "Press Enter or A to update, any other key to keep: " up_choice < /dev/tty
                echo
                if [[ -z "$up_choice" || "$up_choice" == "a" || "$up_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}Will update to: ${target_version}${NC}"
                else
                    echo "Keeping the current version."
                    return 0
                fi
            elif [ -n "$latest_prerelease" ]; then
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
                if [ "$higher" = "$prerelease_num" ]; then
                    echo -e "${YELLOW}Currently installed stable version ${local_version}.${NC}"
                    echo -e "${YELLOW}A higher or equal pre-release ${latest_prerelease} was found, switch to it?${NC}"
                    read -n1 -p "Press Enter or A to switch, any other key to keep: " switch_choice < /dev/tty
                    echo
                    if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                        target_version="$latest_prerelease"
                        echo -e "${GREEN}Will switch to the pre-release: ${target_version}${NC}"
                    else
                        echo "Keeping the current version."
                        return 0
                    fi
                else
                    echo -e "${GREEN}Already the latest stable version ${local_version}, and there is no higher pre-release.${NC}"
                    return 0
                fi
            else
                echo -e "${GREEN}Already the latest stable version ${local_version}, and there is no pre-release.${NC}"
                return 0
            fi
        fi
    fi

    if [ -z "$target_version" ]; then
        echo -e "${RED}Error: the target version was not determined.${NC}"
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
        # 1. Prefer names containing the plugin directory name and not a source package
        for a in assets:
            n = a.get('name', '')
            if plugin_dir in n.lower() and not is_source(n):
                return a
        # 2. Then prefer names containing the display name
        for a in assets:
            n = a.get('name', '')
            if display in n.lower() and not is_source(n):
                return a
        # 3. Then prefer any non-source .zip
        for a in assets:
            n = a.get('name', '')
            if n.endswith('.zip') and not is_source(n):
                return a
        # 4. Last resort: the first .zip
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
        echo -e "${RED}Error: cannot get the download link for ${target_version}.${NC}"
        return 1
    fi

    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return

    local zip_filename="${DISPLAY_NAME}.zip"

    if ! download_zip_with_mirrors "$download_url" "$zip_filename" "${DISPLAY_NAME} ${target_version}"; then
        echo -e "${RED}Download failed, installation aborted.${NC}"
        return 1
    fi

    echo -e "${CYAN}Extracting and installing to ${PLUGIN_PATH}...${NC}"

    local EXTRACT_DIR="$TEMP_DIR/extract"
    mkdir -p "$EXTRACT_DIR"

    if ! sudo unzip -q "$zip_filename" -d "$EXTRACT_DIR"; then
        echo -e "${RED}Extraction failed.${NC}"
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

    echo -e "${GREEN}✅ ${DISPLAY_NAME} plugin ${target_version} installed!${NC}"
    echo -e "${GREEN}Install directory: ${PLUGIN_PATH}${NC}"
}

install_decky_lsfg_vk_install() { install_github_plugin "xXJSONDeruloXx/decky-lsfg-vk" "Decky-LSFG-VK" "LSFG-VK"; }
install_decky_framegen_install() { install_github_plugin "xXJSONDeruloXx/Decky-Framegen" "Decky-Framegen" "Framegen"; }
install_tomoon_install() { install_github_plugin "YukiCoco/ToMoon" "tomoon" "ToMoon"; }
install_freedeck_install() { install_github_plugin "panyiwei-home/Freedeck" "Freedeck" "Freedeck"; }

uninstall_plugin_generic() {
    local plugin_dir="$1" display_name="$2"
    local plugin_path="$HOME/homebrew/plugins/${plugin_dir}"
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Uninstalling ${display_name} ════════════════${NC}"
    [ -d "$plugin_path" ] || { echo -e "${YELLOW}${display_name} is not installed.${NC}"; return 0; }
    confirm_action || { echo "Uninstall cancelled."; return 0; }
    sudo rm -rf "$plugin_path"
    # Judge the deletion result by whether the directory really disappeared, never report success unconditionally
    if [ -d "$plugin_path" ]; then
        echo -e "${RED}✗ Failed to uninstall ${display_name}, the directory still exists: $plugin_path${NC}"
        echo -e "${YELLOW}  Please delete it manually: sudo rm -rf \"$plugin_path\"${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ ${display_name} uninstalled.${NC}"
}
install_tomoon_uninstall() { uninstall_plugin_generic "tomoon" "ToMoon"; }
install_freedeck_uninstall() { uninstall_plugin_generic "Freedeck" "Freedeck"; }
install_decky_lsfg_vk_uninstall() { uninstall_plugin_generic "Decky-LSFG-VK" "LSFG-VK"; }
install_decky_framegen_uninstall() { uninstall_plugin_generic "Decky-Framegen" "Framegen"; }

install_plugin_store() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Install/Update Plugin Store (Decky Loader) ════════════════${NC}"
    echo -e "${CYAN}Fetching version information from GitHub...${NC}"

    local releases_json=$(curl -s "https://api.github.com/repos/SteamDeckHomebrew/decky-loader/releases")
    if [ -z "$releases_json" ]; then
        echo -e "${RED}Error: cannot connect to the GitHub API, please check your network.${NC}"
        return 1
    fi
    if ! [[ "$releases_json" == \[* ]]; then
        echo -e "${RED}Error: the GitHub API returned an abnormal response (the repository may have no Release, or the network is limited).${NC}"
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
        echo -e "${RED}Error: cannot parse the version information.${NC}"
        return 1
    fi

    local stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
    local prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

    local latest_stable=""
    if [ -n "$stable_list" ]; then
        # The GitHub API returns results newest-first, so the first stable release is the latest
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
            echo -e "${CYAN}Currently installed version: ${installed_version}${NC}"
        else
            echo -e "${YELLOW}Installed, but the version cannot be obtained.${NC}"
        fi
    else
        echo "No existing installation detected."
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
        labels+=("Stable version $latest_stable")
    fi
    if [ "$show_prerelease" = true ]; then
        options+=("$latest_prerelease")
        labels+=("Pre-release version $latest_prerelease")
    fi

    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}Error: no version found.${NC}"
        return 1
    fi

    local target_version=""

    if [ -z "$installed_version" ]; then
        while true; do
            clear
            echo -e "${YELLOW}════════════════ Install/Update Plugin Store ════════════════${NC}"
            echo ""
            echo -e "${YELLOW}No existing installation detected.${NC}"
            echo ""
            if [ ${#options[@]} -eq 1 ]; then
                target_version="${options[0]}"
                echo -e "${GREEN}The only version available will be installed: ${target_version}${NC}"
                break
            else
                echo "Please choose the version to install:"
                for i in "${!options[@]}"; do
                    echo "$((i+1))) ${labels[$i]}"
                done
                read -p "Enter your choice [1-${#options[@]}]: " choice < /dev/tty
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#options[@]} ]; then
                    target_version="${options[$((choice-1))]}"
                    break
                else
                    echo -e "${RED}Invalid choice, please try again.${NC}"
                    sleep 1
                fi
            fi
        done
        echo -e "${GREEN}Version to install: ${target_version}${NC}"
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
                echo -e "${YELLOW}Currently installed pre-release version ${installed_version}.${NC}"
                echo -e "${YELLOW}Update detected: pre-release ${new_prerelease}.${NC}"
                echo "Please choose an action:"
                echo "1) Update to the latest pre-release ${new_prerelease}"
                if [ -n "$latest_stable" ]; then
                    echo "2) Switch to the stable version ${latest_stable}"
                    echo "3) Keep the current version"
                else
                    echo "2) Keep the current version"
                fi
                while true; do
                    read -p "Enter your choice: " choice < /dev/tty
                    if [ "$choice" = "1" ]; then
                        target_version="$new_prerelease"
                        echo -e "${GREEN}Updating to the pre-release: ${target_version}${NC}"
                        break
                    elif [ "$choice" = "2" ]; then
                        if [ -n "$latest_stable" ]; then
                            target_version="$latest_stable"
                            echo -e "${GREEN}Switching to the stable version: ${target_version}${NC}"
                            break
                        else
                            echo "Keeping the current version."
                            return 0
                        fi
                    elif [ -n "$latest_stable" ] && [ "$choice" = "3" ]; then
                        echo "Keeping the current version."
                        return 0
                    else
                        echo -e "${RED}Invalid choice, please try again.${NC}"
                    fi
                done
            elif [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}Currently installed pre-release version ${installed_version}.${NC}"
                echo -e "${YELLOW}Switch to the stable version ${latest_stable}?${NC}"
                read -n1 -p "Press Enter or A to switch, any other key to keep: " switch_choice < /dev/tty
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}Switching to the stable version: ${target_version}${NC}"
                else
                    echo "Keeping the current version."
                    return 0
                fi
            else
                echo -e "${GREEN}Already the latest pre-release ${installed_version}, and there is no stable version to switch to.${NC}"
                return 0
            fi
        else
            # Compare the local version with the latest stable release first (stable updates must also be detected when there is no pre-release)
            local stable_num=$(echo "$installed_version" | sed 's/^v//')
            local latest_stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local higher_stable=$(printf '%s\n' "$stable_num" "$latest_stable_num" | sort -V | tail -1)
            if [ -n "$latest_stable" ] && [ "$higher_stable" = "$latest_stable_num" ] && [ "$stable_num" != "$latest_stable_num" ]; then
                echo -e "${YELLOW}New version detected: stable ${latest_stable} (currently ${installed_version}).${NC}"
                read -n1 -p "Press Enter or A to update, any other key to keep: " up_choice < /dev/tty
                echo
                if [[ -z "$up_choice" || "$up_choice" == "a" || "$up_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}Will update to: ${target_version}${NC}"
                else
                    echo "Keeping the current version."
                    return 0
                fi
            elif [ -n "$latest_prerelease" ]; then
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
                if [ "$higher" = "$prerelease_num" ]; then
                    echo -e "${YELLOW}Currently installed stable version ${installed_version}.${NC}"
                    echo -e "${YELLOW}A higher or equal pre-release ${latest_prerelease} was found, switch to it?${NC}"
                    read -n1 -p "Press Enter or A to switch, any other key to keep: " switch_choice < /dev/tty
                    echo
                    if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                        target_version="$latest_prerelease"
                        echo -e "${GREEN}Will switch to the pre-release: ${target_version}${NC}"
                    else
                        echo "Keeping the current version."
                        return 0
                    fi
                else
                    echo -e "${GREEN}Already the latest stable version ${installed_version}, and there is no higher pre-release.${NC}"
                    return 0
                fi
            else
                echo -e "${GREEN}Already the latest stable version ${installed_version}, and there is no pre-release.${NC}"
                return 0
            fi
        fi
    fi

    if [ -z "$target_version" ]; then
        echo -e "${RED}Error: the target version was not determined.${NC}"
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

    echo -e "${CYAN}Downloading PluginLoader...${NC}"
    if ! download_with_mirrors "$DOWNLOAD_URL" "$TMP_FILE" "PluginLoader"; then
        echo -e "${RED}Download failed, installation aborted.${NC}"
        return 1
    fi

    FILE_SIZE=$(stat -c%s "$TMP_FILE" 2>/dev/null || stat -f%z "$TMP_FILE" 2>/dev/null)
    if [[ -z "$FILE_SIZE" || "$FILE_SIZE" -lt 1000000 ]]; then
        echo -e "${RED}The downloaded file is invalid (size: ${FILE_SIZE:-0} bytes).${NC}"
        rm -f "$TMP_FILE"
        return 1
    fi
    echo -e "\n${GREEN}Download successful (size: $((FILE_SIZE/1024/1024)) MB)${NC}"

    for cmd in curl "$PYTHON_CMD" systemctl sudo journalctl stat; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}Error: $cmd command not found, please install it first.${NC}"
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
# FIX-LEAD: decky service
User=${CURRENT_USER}
Environment="HOMEBREW_FOLDER=${HOMEBREW_DIR}"
Environment="UNPRIVILEGED_PATH=${HOMEBREW_DIR}"
Environment="PRIVILEGED_PATH=${HOMEBREW_DIR}"
WorkingDirectory=${HOMEBREW_DIR}
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
    echo -e "${GREEN}✅ Decky Loader ${target_version} installed/updated!${NC}"
    echo "Please switch back to Game Mode and press the '...' button to open the sidebar and check."
}

uninstall_plugin_store() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Uninstall Plugin Store ════════════════${NC}"
    if [ ! -d "$HOME/homebrew" ]; then
        echo -e "${YELLOW}Plugin Store is not installed.${NC}"
        return 0
    fi

    echo -e "${CYAN}An installed Plugin Store was detected.${NC}"
    echo "Warning: this deletes the entire $HOME/homebrew directory, including all plugins."
    echo ""
    read -n1 -p "Press Enter or A to confirm uninstalling, any other key to cancel: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "Continuing the uninstall..."
    else
        echo "Uninstall cancelled."
        return 0
    fi

    # FIX-LEAD: uninstall_plugin_store EN
    # The old version only removed homebrew and left plugin_loader.service enabled;
    # systemd would then keep trying to start a binary that no longer exists.
    local _fail=0
    if systemctl is-enabled --quiet plugin_loader 2>/dev/null || systemctl is-active --quiet plugin_loader 2>/dev/null; then
        if ! sudo systemctl disable --now plugin_loader 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Failed to stop/disable plugin_loader; please check it manually.${NC}"
            _fail=1
        fi
    fi
    if [ -f /etc/systemd/system/plugin_loader.service ]; then
        sudo rm -f /etc/systemd/system/plugin_loader.service 2>/dev/null || _fail=1
    fi
    if [ -f "$HOME/.config/systemd/user/plugin_loader.service" ]; then
        rm -f "$HOME/.config/systemd/user/plugin_loader.service" 2>/dev/null || _fail=1
    fi
    sudo systemctl daemon-reload 2>/dev/null || _fail=1
    rm -f "$HOME/.steam/steam/.cef-enable-remote-debugging" \
          "$HOME/.var/app/com.valvesoftware.Steam/data/Steam/.cef-enable-remote-debugging" 2>/dev/null
    rm -rf /tmp/plugin_loader 2>/dev/null

    echo "Running the uninstall..."
    sudo rm -rf "$HOME/homebrew"
    # Judge by whether the directory really disappeared (rm may also return 0 on partial failure)
    if [ -d "$HOME/homebrew" ]; then
        echo -e "${RED}✗ Failed to uninstall the Plugin Store, the directory still exists: $HOME/homebrew${NC}"
        echo -e "${YELLOW}  Please delete it manually: sudo rm -rf \"$HOME/homebrew\"${NC}"
        return 1
    fi
    if [ "$_fail" -ne 0 ]; then
        echo -e "${YELLOW}⚠️  The main directory is gone, but some service/marker cleanup failed; check the hints above.${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Plugin Store uninstalled${NC}"
    echo "To reinstall, use the 'Install Plugin Store' feature."
}

install_cheatdeck_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Install/Update CheatDeck ════════════════${NC}"
    echo ""
    echo -e "${CYAN}CheatDeck is a Decky plugin for managing third-party trainer entry points in Game Mode.${NC}"
    echo -e "${YELLOW}Disclaimer:${NC}"
    echo "  · This toolbox only installs the plugin package (CheatDeck.zip); no cheat files are bundled"
    echo "  · Trainers may violate a game ToS; you accept the account risk"
    echo "  · Separate from DW Proton / other compatibility layers"
    echo ""
    if [ ! -d "$HOME/homebrew" ] || [ ! -e "$HOME/homebrew/services/PluginLoader" ]; then
        echo -e "${RED}Decky Loader not detected (~/homebrew). Install Decky under Plugins → Plugin Store first.${NC}"
        return 1
    fi
    echo -e "${CYAN}After install, in Game Mode open Decky → Settings → Developer → enable Developer mode,${NC}"
    echo -e "${CYAN}then restart Steam or PluginLoader so the plugin can load.${NC}"
    echo ""
    read -n1 -p "Press Enter or Y to continue, any other key to cancel: " ans < /dev/tty
    echo
    if [[ -n "$ans" && "$ans" != "y" && "$ans" != "Y" ]]; then
        echo "Cancelled."
        return 0
    fi
    install_github_plugin "SheffeyG/CheatDeck" "CheatDeck" "CheatDeck"
}

install_cheatdeck_uninstall() {
    uninstall_plugin_generic "CheatDeck" "CheatDeck"
}

_emergency_backup_root() {
    local stamp
    stamp=$(date +%Y%m%d_%H%M%S)
    local root="$HOME/steamdeck_toolbox_backups"
    mkdir -p "$root"
    echo "${root}/$1_${stamp}"
}

_emergency_stop_steam() {
    echo -e "${CYAN}Stopping Steam / related processes if running...${NC}"
    # 不要在此切换会话；仅结束 Steam 相关进程
    pkill -TERM -u "$USER" -x steam 2>/dev/null || true
    pkill -TERM -u "$USER" -f '/steam(\.sh)?$' 2>/dev/null || true
    sleep 2
    pkill -KILL -u "$USER" -x steam 2>/dev/null || true
    sleep 1
}

emergency_steam_reset() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Emergency: Steam config reset ════════════════${NC}"
    echo ""
    echo "Use when Desktop Mode still works but Steam hangs, spins, or has a broken config."
    echo ""
    echo -e "${GREEN}Kept:${NC} steamapps (game installs), most userdata save-related trees"
    echo -e "${YELLOW}Reset/cleared (auto-backed up first):${NC}"
    echo "  · ~/.local/share/Steam/config"
    echo "  · Steam launch/login caches (registry.vdf, .cef-cache, htmlcache, steamui caches)"
    echo -e "${RED}Does NOT delete steamapps game libraries.${NC}"
    echo ""
    echo "Backup example: ~/steamdeck_toolbox_backups/steam_reset_TIMESTAMP/"
    echo ""
    read -n1 -p "Type Y to continue, anything else cancels: " ans < /dev/tty
    echo
    [[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "Cancelled."; return 0; }
    read -n1 -p "Confirm again: local Steam settings will be lost (games kept). Type Y: " ans2 < /dev/tty
    echo
    [[ "$ans2" == "y" || "$ans2" == "Y" ]] || { echo "Cancelled."; return 0; }

    _emergency_stop_steam
    local bak
    bak=$(_emergency_backup_root "steam_reset")
    mkdir -p "$bak"
    echo -e "${CYAN}Backup dir: $bak${NC}"

    local steam_root="$HOME/.local/share/Steam"
    if [ -d "$HOME/.steam/steam" ] && [ ! -d "$steam_root" ]; then
        steam_root="$HOME/.steam/steam"
    fi

    if [ -d "$steam_root/config" ]; then
        # FIX-LEAD: emergency backup EN
        # Deleting the original after a failed backup loses data irrecoverably.
        if ! cp -a "$steam_root/config" "$bak/config" 2>/dev/null; then
            echo -e "${RED}✗ Failed to back up config; aborting before any deletion.${NC}"
            return 1
        fi
        rm -rf "$steam_root/config"
        echo -e "${GREEN}✓ Reset config${NC}"
    else
        echo -e "${YELLOW}- config not found, skipped${NC}"
    fi

    local f
    for f in \
        "$HOME/.steam/registry.vdf" \
        "$steam_root/registry.vdf" \
        "$steam_root/.cef-cache" \
        "$steam_root/config/htmlcache" \
        "$steam_root/steamui" \
        "$steam_root/appcache/httpcache"
    do
        if [ -e "$f" ]; then
            local base
            base=$(basename "$f")
            if [ -e "$bak/$base" ]; then
                base="${base}_$(echo "$f" | md5sum | awk '{print $1}' | cut -c1-6)"
            fi
            # FIX-LEAD: emergency loop backup
            if ! cp -a "$f" "$bak/$base" 2>/dev/null; then
                echo -e "${RED}✗ 备份 $f 失败，已中止删除。${NC}"
                return 1
            fi
            rm -rf "$f"
            echo -e "${GREEN}✓ Cleared $f${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}✅ Steam config reset finished.${NC}"
    echo "Backup: $bak"
    echo "Relaunch Steam / Game Mode. Restore from the backup folder if needed."
}

emergency_gamescope_reset() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Emergency: Gamescope / Game Mode reset ════════════════${NC}"
    echo ""
    echo "Use for Game Mode black screens, boot loops, or bad scaling when Desktop Mode still works."
    echo ""
    echo -e "${YELLOW}Will backup then clear (games are not deleted):${NC}"
    echo "  · ~/.config/gamescope* if present"
    echo "  · Steam UI/display caches (htmlcache, .cef-cache, some steamui caches)"
    echo "  · User gamescope session leftovers if present"
    echo ""
    read -n1 -p "Type Y to continue, anything else cancels: " ans < /dev/tty
    echo
    [[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "Cancelled."; return 0; }
    read -n1 -p "Confirm again: local Game Mode settings may be lost. Type Y: " ans2 < /dev/tty
    echo
    [[ "$ans2" == "y" || "$ans2" == "Y" ]] || { echo "Cancelled."; return 0; }

    _emergency_stop_steam
    local bak
    bak=$(_emergency_backup_root "gamescope_reset")
    mkdir -p "$bak"
    echo -e "${CYAN}Backup dir: $bak${NC}"

    local steam_root="$HOME/.local/share/Steam"
    [ -d "$HOME/.steam/steam" ] && [ ! -d "$steam_root" ] && steam_root="$HOME/.steam/steam"

    local p
    for p in \
        "$HOME/.config/gamescope" \
        "$HOME/.config/gamescope-session" \
        "$HOME/.local/share/gamescope" \
        "$steam_root/.cef-cache" \
        "$steam_root/config/htmlcache" \
        "$steam_root/steamui/movies" \
        "$HOME/.steam/steam.pid"
    do
        if [ -e "$p" ]; then
            local dest
            dest="$bak/$(echo "$p" | sed 's#^/##; s#/#_#g')"
            mkdir -p "$(dirname "$dest")"
            # FIX-LEAD: emergency gamescope backup
            if ! cp -a "$p" "$dest" 2>/dev/null; then
                echo -e "${RED}✗ 备份 $p 失败，已中止删除。${NC}"
                return 1
            fi
            rm -rf "$p"
            echo -e "${GREEN}✓ Cleared $p${NC}"
        fi
    done

    rm -rf /tmp/gamescope-*=* 2>/dev/null || true
    rm -f /tmp/gamescope.* 2>/dev/null || true

    echo ""
    echo -e "${GREEN}✅ Gamescope / Game Mode related state reset.${NC}"
    echo "Backup: $bak"
    echo "Switch back to Game Mode from Desktop, or reboot, then retry."
}


clover_install_or_reinstall() {
    clear
    echo -e "${YELLOW}════════════════ Install/Reinstall Clover bootloader ════════════════${NC}"
    echo ""
    echo -e "${CYAN}This will install or reinstall the Clover graphical boot manager.${NC}"
    echo -e "${YELLOW}Important: first apply the following settings in Windows (if Windows already exists and this is the first bootloader install). Skip if reinstalling the bootloader:${NC}"
    echo "  1. Open Command Prompt or PowerShell as Administrator"
    echo "  2. Run: bcdedit.exe -set \"{globalsettings}\" highestmode on"
    echo "  3. Run: reg add \"HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\TimeZoneInformation\" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f"
    echo ""

    echo "========================================="
    echo "   Steam Deck Clover Install Helper"
    echo "========================================="
    # 注意：这里克隆走的是 git 协议，不是普通 HTTP 下载。
    # 2026-10 实测：gh-proxy.com / cors.isteed.cc / ghproxy.net 都**不支持** git clone
    # （只有 gh.3w.pm 和官方源可用），所以克隆镜像单独列，不套用下载镜像列表。
    echo "Choose clone mirror:"
    echo "  1) gh.3w.pm        (China mirror, recommended)"
    echo "  2) GitHub official (may be slow in China)"
    read -p "Enter a number [1-2]: " choice < /dev/tty

    case "$choice" in
        1) BASE_URL="https://gh.3w.pm/https://github.com" ;;
        2) BASE_URL="https://github.com" ;;
        *) echo "Operation cancelled."; return 0 ;;
    esac

    REPO_FULL_PATH="ryanrudolfoba/SteamDeck-Clover-dualboot"
    REPO_URL="${BASE_URL}/${REPO_FULL_PATH}"
    TARGET_DIR="$HOME/SteamDeck-Clover-dualboot"

    if [ -d "$TARGET_DIR" ]; then
        echo -e "${YELLOW}Directory $TARGET_DIR already exists.${NC}"
        read -p "Delete the old folder and clone again? (y/N): " -n 1 -r < /dev/tty
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$TARGET_DIR"
        else
            echo "Operation cancelled."
            read -p "Press Enter to return to the main menu..." < /dev/tty
            return 0
        fi
    fi

    echo -e "${CYAN}Cloning repository...${NC}"
    if ! git clone --progress --depth=1 "$REPO_URL" "$TARGET_DIR" 2>&1 | tee /tmp/clone_log.txt; then
        echo -e "${RED}Clone failed; check network or switch mirrors.${NC}"
        rm -rf "$TARGET_DIR"
        read -p "Press Enter to return to the main menu..." < /dev/tty
        return 1
    fi

    echo -e "${GREEN}Clone finished.${NC}"
    cd "$TARGET_DIR" || { echo -e "${RED}Cannot enter directory${NC}"; return 1; }

    echo -e "${CYAN}Generating optimized install-Clover.sh...${NC}"
    cat > install-Clover.sh << 'CLOVER_SCRIPT_EOF'
#!/bin/bash
# 失败即中止：原脚本没有 set -e，中间任何一步失败（cp/挂载/efibootmgr）都会继续
# 往下执行，可能在 ESP 上写出半套 Clover，最后还打印“安装完成”。
# 这里加 -euo pipefail，并对“允许失败”的命令（grep 探测、efibootmgr -B、umount）
# 显式写 `|| true` 或放进 if 里，见下方逐处注释。
set -euo pipefail

clear

echo "Clover dual-boot install script - Steam Deck edition"
echo "Project: https://github.com/ryanrudolfoba/SteamDeck-Clover-dualboot"
echo "Author YT: 10MinuteSteamDeckGamer"
echo "Running initial checks..."

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
    echo "❌ Cannot identify the EFI system partition (ESP), aborted, no changes were made to the system."
    exit 1
fi
echo "ESP partition detected: $ESP_DEV (disk $ESP_DISK, partition number $ESP_PARTN)"

# Compute free space from the detected ESP device; the ESP variable is in KB
ESP=$(df --output=avail "$ESP_DEV" 2>/dev/null | tail -n1 | tr -d ' ' || true)
if ! [[ "$ESP" =~ ^[0-9]+$ ]]; then
    echo "❌ Cannot read the free space of the ESP partition, aborted."
    exit 1
fi

# ===== SteamOS read-only mode guard =====
# In the old script, if the rEFInd branch disabled read-only and then exited midway, the system stayed writable.
# Use an EXIT trap to restore uniformly: only restore if this script really did disable it successfully.
# Note: the trap must be installed before any disable (the rEFInd branch runs earlier than the old install point).
RO_DISABLED_BY_US=0
restore_readonly() {
    if [ "${RO_DISABLED_BY_US:-0}" -eq 1 ]; then
        if sudo -n steamos-readonly enable 2>/dev/null; then
            echo "SteamOS read-only mode restored."
        else
            echo "⚠️ Cannot restore read-only mode automatically, please run manually: sudo steamos-readonly enable"
        fi
        RO_DISABLED_BY_US=0
    fi
    return 0
}
enable_readonly_mode() {
    sudo -n steamos-readonly enable 2>/dev/null || true
    RO_DISABLED_BY_US=0
}
# ISO/temp directory cleanup flag, merged into the same EXIT hook as the read-only restore
# (two separate EXIT traps would overwrite each other, only the last one installed survives).
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
    echo "Supported device detected - Steam Deck $BOARD_NAME, no need to modify config.plist."
elif [ "$PRODUCT_NAME" = "83L3" ] || [ "$PRODUCT_NAME" = "83Q2" ] || [ "$PRODUCT_NAME" = "83Q3" ]; then
    echo "Legion Go S detected, applying the dedicated configuration."
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1200<\/string>' custom/config.plist
elif [ "$PRODUCT_NAME" = "83N6" ]; then
    echo "Unsupported device - Legion Go S 83N6, exiting."
    exit
elif [ "$PRODUCT_NAME" = "83E1" ]; then
    echo "Legion Go detected, applying the dedicated configuration."
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>2560x1600<\/string>' custom/config.plist
elif [ "$BOARD_NAME" = "RC71L" ]; then
    echo "ROG Ally detected, applying the dedicated configuration."
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' custom/config.plist
elif [ "$BOARD_NAME" = "RC72LA" ]; then
    echo "ROG Ally X detected, applying the dedicated configuration."
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' custom/config.plist
elif [ "$PRODUCT_NAME" = "ONEXPLAYER 2 PRO ARP23P" ]; then
    echo "Onexplayer 2 Pro detected, applying the dedicated configuration."
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>2560x1600<\/string>' custom/config.plist
else
    echo "⚠️ Warning: the device is not on the officially supported list, forcing the installation to continue (at your own risk)!"
fi

if grep -qi bazzite /etc/os-release; then
    OS=bazzite
    EFI_PATH=/boot/efi/EFI
    BOOTX64=$EFI_PATH/BOOT/BOOTX64.EFI
    echo "Operating system detected: Bazzite"
else
    grep -qi SteamOS /etc/os-release || { echo "Neither SteamOS nor Bazzite! Exiting."; exit; }
    OS=SteamOS
    EFI_PATH=/esp/efi
    BOOTX64=$EFI_PATH/boot/bootx64.efi
    echo "Operating system detected: SteamOS"
fi

if blkid "$ESP_DEV" 2>/dev/null | grep -qi microsoft; then
    echo "Unsupported dual-boot configuration detected (Windows installed before SteamOS). Make sure SteamOS is installed before Windows!"
    exit 1
else
    echo "Dual-boot configuration check passed."
fi

# 密码处理：
#  - 原写法把密码经 `echo -e "$pw\n"` 放进管道。密码是 shell 变量而非外部命令参数，
#    实测 ps 里看不到明文；但 `echo -e` 会解释反斜杠，密码里含 `\` 时会被改写/截断
#    （实测 'p\cw' → 'p'），导致 sudo 认证失败。改用 printf '%s\n' 原样输出。
#  - 验证成功后立刻 `sudo -v` 取到时间戳，后续统一 `sudo -n`，不再反复喂密码。
if [ "$(passwd --status "$(whoami)" | tr -s " " | cut -d " " -f 2)" == "P" ]; then
    read -s -p "Please enter the current sudo password: " current_password < /dev/tty; echo
    echo "Verifying the sudo password..."
    if ! printf '%s\n' "$current_password" | sudo -S -v &> /dev/null; then
        echo "Wrong sudo password! Please run the script again and enter the correct password."
        exit 1
    fi
    echo "sudo password is correct."
else
    echo "No sudo password is set! Please set one before running the script."
    passwd || true
    exit 1
fi

# 后续统一走 sudo -n（密码已由上面的 sudo -v 缓存）；失败直接中止而不是继续写 EFI。
mkdir -p ~/temp-ESP
if ! sudo -n mount "$ESP_DEV" ~/temp-ESP; then
    echo "Failed to mount the ESP partition! Aborted, the system was not modified."
    rmdir ~/temp-ESP 2>/dev/null || true
    exit 1
fi
echo "ESP partition mounted."
if [ "$ESP" -ge 15000 ]; then
    echo "ESP partition free space: $ESP KB, sufficient."
    sudo -n umount ~/temp-ESP || true
    rmdir ~/temp-ESP 2>/dev/null || true
else
    echo "ESP partition free space: $ESP KB, not enough space! Please clean up and try again."
    # 注意：这里输出“空间不足”，外层成功判定已同步匹配该关键字
    sudo -n du -hd2 /esp || true
    sudo -n umount ~/temp-ESP || true
    rmdir ~/temp-ESP 2>/dev/null || true
    exit 1
fi

if efibootmgr | grep -qi refind; then
    echo "rEFInd detected, trying to uninstall it..."
    for rEFInd_boot in $REFIND; do
        sudo -n efibootmgr -b "$rEFInd_boot" -B &> /dev/null || true
    done
    sudo -n systemctl disable bootnext-refind.service &> /dev/null || true
    sudo -n systemctl disable rEFInd_bg_randomizer.service &> /dev/null || true
    sudo -n rm -rf "$EFI_PATH/refind" &> /dev/null || true
    if sudo -n steamos-readonly disable; then
        RO_DISABLED_BY_US=1
    else
        echo "⚠️ Cannot disable read-only mode, the rEFInd uninstall may fail."
    fi
    sudo -n rm -f /etc/systemd/system/bootnext-refind.service &> /dev/null || true
    sudo -n rm -f /etc/systemd/system/rEFInd_bg_randomizer.service &> /dev/null || true
    sudo -n pacman-key --init || true
    sudo -n pacman-key --populate archlinux || true
    sudo -n pacman -R --noconfirm SteamDeck_rEFInd || true
    enable_readonly_mode
    rm -rf ~/.local/SteamDeck_rEFInd ~/.SteamDeck_rEFInd ~/Desktop/SteamDeck_rEFInd.desktop
    if efibootmgr | grep -qi refind; then
        echo "Failed to uninstall rEFInd, please uninstall it manually and try again."
        exit 1
    fi
    echo "rEFInd uninstalled successfully."
else
    echo "rEFInd not detected, continuing with the Clover installation."
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
    "gh-proxy.com (China mirror, fast)"
    "gh.3w.pm (China mirror, stable)"
    "cors.isteed.cc (China mirror, stable)"
    "ghproxy.net (China mirror, slow fallback)"
    "GitHub (official)"
)

DOWNLOAD_SUCCESS=0
while true; do
    echo ""
    echo "Please choose a download mirror (enter a number, 0 to cancel):"
    for i in "${!MIRRORS[@]}"; do
        echo "  $((i+1)). ${MIRROR_LABELS[$i]:-${MIRRORS[$i]}}"
    done
    read -p "Enter your choice: " choice < /dev/tty

    if [[ -z "$choice" ]]; then
        echo "Invalid input, please choose again."
        continue
    fi
    if [[ "$choice" == "0" ]]; then
        echo "Operation cancelled."
        exit 0
    fi
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
        mirror="${MIRRORS[$((choice-1))]}"
        CLOVER_URL="${mirror}${CLOVER_GH_BASE}/releases/download/${CLOVER_VERSION}/${CLOVER_FILE}"
        echo "Trying to download from ${MIRROR_LABELS[$((choice-1))]:-${mirror}} ..."
        if curl -# -L --fail --connect-timeout 10 --max-time 120 -o "${CLOVER_FILE}" "${CLOVER_URL}"; then
            echo "✅ Download successful!"
            DOWNLOAD_SUCCESS=1
            break
        else
            echo "⚠️ Download failed, please choose another mirror."
            rm -f "${CLOVER_FILE}"
        fi
    else
        echo "Invalid number, please choose again."
    fi
done

if [ ${DOWNLOAD_SUCCESS} -eq 0 ]; then
    echo "❌ Failed to download Clover! All mirrors are unavailable, please check your network and try again."
    exit 1
fi

# 解压失败时清理下载的 7z 与可能残留的 ISO，避免占满 /home
if ! 7z x "${CLOVER_FILE}" -aoa "${CLOVER_BASE}" &> /dev/null; then
    echo "Failed to extract the Clover ISO!"
    rm -f "${CLOVER_FILE}" "${CLOVER_BASE}"
    exit 1
fi
if [ ! -f "${CLOVER_BASE}" ]; then
    echo "ISO file ${CLOVER_BASE} not found after extraction, aborted."
    rm -f "${CLOVER_FILE}"
    exit 1
fi
echo "Clover ISO extracted successfully."

# 挂载失败时把临时目录、ISO、7z 一并清理干净
mkdir -p ~/temp-clover
if ! sudo -n mount "${CLOVER_BASE}" ~/temp-clover &> /dev/null; then
    echo "Failed to mount the Clover ISO! Temporary files were cleaned up."
    sudo -n umount ~/temp-clover &> /dev/null || true
    rmdir ~/temp-clover 2>/dev/null || true
    rm -f "${CLOVER_FILE}" "${CLOVER_BASE}"
    exit 1
fi
ISO_MOUNTED=1
echo "Clover ISO mounted."

# 安装中途任何一步失败都要卸载 ISO、清理临时文件，不留半套环境。
# 注意：trap ... ERR 在脚本里 `exit 1` 触发的路径上**不会**执行（实测残留 ISO），
# 所以清理挂在上面已装好的 EXIT 钩子里，用 ISO_MOUNTED 标志决定是否卸载。
if ! sudo -n cp -Rf ~/temp-clover/efi/clover "$EFI_PATH"; then
    echo "❌ Failed to copy the Clover EFI files to the ESP (possibly not enough ESP space). Aborted."
    exit 1
fi
sudo -n cp custom/config.plist "$EFI_PATH/clover/config.plist"
sudo -n cp -Rf custom/themes/. "$EFI_PATH/clover/themes/" \
    || { echo "❌ Failed to copy the theme files, aborted."; exit 1; }
sudo -n rm -rf "$EFI_PATH/clover/themes/bgm" "$EFI_PATH/clover/themes/cesium" \
    "$EFI_PATH/clover/themes/christmas" "$EFI_PATH/clover/themes/glass" \
    "$EFI_PATH/clover/themes/purple_swirl" "$EFI_PATH/clover/themes/theme-sample.plist" \
    || true

if [ "$PRODUCT_NAME" = "83N6" ] || [ "$PRODUCT_NAME" = "83L3" ] || [ "$PRODUCT_NAME" = "83Q2" ] || [ "$PRODUCT_NAME" = "83Q3" ] || [ "$PRODUCT_NAME" = "83E1" ] || [ "$BOARD_NAME" = "RC71L" ] || [ "$BOARD_NAME" = "RC72LA" ] || [ "$PRODUCT_NAME" = "ONEXPLAYER 2 PRO ARP23P" ]; then
    echo "Non-Steam Deck device, installing the Xbox 360 UEFI driver..."
    if sudo -n cp custom/UsbXbox360Dxe.efi "$EFI_PATH/clover/drivers/uefi"; then
        echo "Xbox 360 driver installed successfully."
    else
        echo "Failed to install the Xbox 360 driver!"
        exit 1
    fi
else
    echo "Steam Deck does not need the Xbox 360 driver."
fi

cleanup_iso
echo "Temporary files cleaned up."

for entry in $CLOVER; do
    sudo -n efibootmgr -b "$entry" -B &> /dev/null || true
done

# 修复：原来 efibootmgr -c 硬编码 /dev/nvme0n1 -p 1。eMMC 机型是 /dev/mmcblk0，
# SATA 机型是 /dev/sda，且 ESP 分区号不一定是 1。改用上面动态探测的 ESP_DISK/ESP_PARTN，
# 并且把输出留出来（不再 &>/dev/null 丢弃），失败时能中止并回滚。
if ! sudo -n efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" -L "Clover - GUI Boot Manager" -l "$CLOVER_EFI"; then
    echo "❌ Failed to create the Clover EFI boot entry (disk $ESP_DISK partition $ESP_PARTN). Installation aborted."
    exit 1
fi
CLOVER=$(efibootmgr | grep -i "Clover - GUI" | colrm 9 | colrm 1 4 || true)
if [ -z "$CLOVER" ]; then
    echo "❌ The Clover boot entry still cannot be found after writing the EFI files, installation aborted."
    exit 1
fi
echo "Clover boot entry created: $CLOVER"

# BOOTX64 替换：必须先备份成功再覆盖；任何一步失败立刻回滚到备份。
if [ ! -e "$BOOTX64" ]; then
    echo "❌ $BOOTX64 not found, cannot back up/replace. Aborted (the EFI boot entry will be rolled back)."
    sudo -n efibootmgr -b "$CLOVER" -B &> /dev/null || true
    exit 1
fi
if [ -e "$BOOTX64.orig" ]; then
    echo "$BOOTX64.orig already exists, no backup needed."
else
    echo "Backing up $BOOTX64 to $BOOTX64.orig"
    if ! sudo -n cp "$BOOTX64" "$BOOTX64.orig"; then
        echo "❌ Failed to back up $BOOTX64, aborted, the original file was not overwritten."
        sudo -n efibootmgr -b "$CLOVER" -B &> /dev/null || true
        exit 1
    fi
fi
if ! sudo -n cp "$EFI_PATH/clover/cloverx64.efi" "$BOOTX64"; then
    echo "❌ Failed to replace bootx64.efi with the Clover EFI! Rolling back..."
    if sudo -n cp "$BOOTX64.orig" "$BOOTX64"; then
        echo "BOOTX64.EFI rolled back to the original version."
    else
        echo "⚠️ The rollback also failed! Please run manually: sudo cp $BOOTX64.orig $BOOTX64"
    fi
    sudo -n efibootmgr -b "$CLOVER" -B &> /dev/null || true
    exit 1
fi
echo "bootx64.efi replaced with the Clover EFI."

if [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" ]; then
    if [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" ]; then
        sudo -n mv "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/bootmgfw.efi"
        echo "Windows EFI direct boot disabled."
    else
        echo "Windows EFI disabled."
    fi
else
    sudo -n cp "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig"
    sudo -n mv "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/bootmgfw.efi"
    echo "Windows EFI direct boot disabled."
fi

sudo -n efibootmgr -n "$CLOVER" || true
sudo -n efibootmgr -o "$CLOVER" || true

if efibootmgr | grep -q "Clover - GUI"; then
    echo "Clover installed successfully to the EFI system partition!"
else
    echo "Oops, something went wrong, Clover was not installed successfully."
    exit 1
fi

# 以下属于“EFI 已经写好之后”的附加组件。失败时只警告不中止：
# 此时 Clover 已可引导，若因工具/SYSTEMD 失败而整体报错，反而会让用户以为没装上。
mkdir -p ~/1Clover-tools
rm -f ~/1Clover-tools/* 2>/dev/null || true
cp custom/Clover-Toolbox.sh ~/1Clover-tools || echo "⚠️ Failed to copy Clover-Toolbox.sh, the desktop toolbox may be unavailable."
sudo -n cp custom/clover-bootmanager.service custom/clover-bootmanager.sh /etc/systemd/system \
    || echo "⚠️ Failed to install the clover-bootmanager service files."
cp -R custom/logos ~/1Clover-tools 2>/dev/null || true
cp -R custom/efi ~/1Clover-tools 2>/dev/null || true

chmod +x ~/1Clover-tools/Clover-Toolbox.sh 2>/dev/null || true
sudo -n chmod +x /etc/systemd/system/clover-bootmanager.sh 2>/dev/null || true

sudo -n systemctl daemon-reload || echo "⚠️ systemctl daemon-reload failed."
sudo -n systemctl enable --now clover-bootmanager.service \
    || echo "⚠️ Failed to enable clover-bootmanager.service; the next boot will go straight to Clover instead of the last system."
sudo -n /etc/systemd/system/clover-bootmanager.sh \
    || echo "⚠️ Failed to run clover-bootmanager.sh, BootNext may not be set."

if [ "$OS" = "SteamOS" ]; then
    mkdir -p ~/.local/share/kservices5/ServiceMenus
    cp custom/open_as_root.desktop ~/.local/share/kservices5/ServiceMenus 2>/dev/null || true
    sudo -n cp custom/clover-whitelist.conf /etc/atomic-update.conf.d \
        || echo "⚠️ Failed to install clover-whitelist.conf; the Clover config may be reverted after a system update."
else
    if ! blkid "$ESP_DEV" 2>/dev/null | grep -qi esp; then
        sudo -n fatlabel "$ESP_DEV" esp || true
        echo "ESP partition label set."
    fi
    sudo -n sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\fedora\\shimx64\.efi<\/string>' $EFI_PATH/clover/config.plist
fi

echo "Clover installation complete on $OS!"
CLOVER_SCRIPT_EOF

    chmod +x install-Clover.sh || {
        echo -e "${RED}Cannot set the executable permission of install-Clover.sh.${NC}"
        read -p "Press Enter to return to the main menu..." < /dev/tty
        return 1
    }

    echo -e "${CYAN}About to run the Clover installation script; enter the sudo password when prompted (if needed)...${NC}"
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
        || grep -q "Not enough space" "$LOG_FILE"; then
        echo -e "${RED}Installation failed: not enough space on the ESP partition, please clean up and try again.${NC}"
        read -p "Press Enter to return to the main menu..." < /dev/tty
        return 1
    elif [ $INSTALL_EXIT -eq 0 ] && grep -q "Clover install complete" "$LOG_FILE"; then
        echo -e "${GREEN}Clover installed/reinstalled successfully!${NC}"
    else
        echo -e "${RED}Installation/reinstallation failed, please check the output above.${NC}"
        read -p "Press Enter to return to the main menu..." < /dev/tty
        return 1
    fi

    SHORTCUT="$HOME/Desktop/Boot Config.desktop"
    if [ -f "$SHORTCUT" ]; then
        echo -e "${GREEN}Desktop shortcut \"Boot Configuration\" already exists, no need to create it.${NC}"
    else
        # 修复：原 heredoc 带引号（<< 'EOF'）不会展开变量，Exec 里写死 /home/deck，
        # 用户名不是 deck 的机器上快捷方式直接失效。这里去掉引号让 $HOME 展开；
        # 已确认该 heredoc 除路径外没有其它 $ 或反引号。
        cat > "$SHORTCUT" << EOF
[Desktop Entry]
Type=Application
Name=Boot Config
Exec=konsole -e bash -c '$HOME/1Clover-tools/Clover-Toolbox.sh; read -p "Press Enter to close..." -n1'
Icon=kdiamond
Terminal=false
Categories=Utility;
EOF
        chmod +x "$SHORTCUT"
        echo -e "${GREEN}Desktop shortcut \"Boot Configuration\" created.${NC}"
    fi

    # FIX-CLOVER-LANG: 英文界面保留 custom/Clover-Toolbox.sh 原版英文，
    # 不再覆盖成汉化版：原版存在时直接保留；仅当原版缺失时才写入下面的
    # 汉化版作为兜底，避免英文界面下桌面工具箱完全不可用。
    if [ -f "$HOME/1Clover-tools/Clover-Toolbox.sh" ]; then
        chmod +x "$HOME/1Clover-tools/Clover-Toolbox.sh" 2>/dev/null || true
        echo -e "${GREEN}✓ Kept the original English Clover-Toolbox.sh (English UI).${NC}"
    else
        echo -e "${YELLOW}⚠️ Original Clover-Toolbox.sh not found; falling back to the translated copy.${NC}"
        # 原版缺失时才退回汉化版，避免英文界面下工具箱打不开
        cat > "$HOME/1Clover-tools/Clover-Toolbox.sh" << 'TOOLBOX_EOF'
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

current_password=$(zenity --password --title "sudo password verification")
printf '%s\n' "$current_password" | sudo -S ls &> /dev/null
if [ $? -ne 0 ]
then
	echo "Wrong sudo password!" | \
		zenity --text-info --title "Clover Toolbox" --width 400 --height 200
	exit
fi

while true
do
Choice=$(zenity --width 750 --height 450 --list --radiolist --multiple \
	--title "Clover toolbox - https://github.com/ryanrudolfoba/SteamDeck-clover-dualboot" \
	--column "Select" \
	--column "Options" \
	--column "Notes - please read carefully" \
	FALSE Status "Use this when submitting a bug report" \
	FALSE Batocera "Choose Batocera v39 (and newer) or v38 (and older) config" \
	FALSE Theme "Choose fixed theme or random theme" \
	FALSE Timeout "Set default timeout (1/5/10/15 sec) before auto-booting the default OS" \
	FALSE Service "Disable/enable Clover EFI entry and systemd service" \
	FALSE DefaultBoot "Set the default boot OS" \
	FALSE NewLogo "Replace BGRT boot logo" \
	FALSE RestoreLogo "Restore default BGRT boot logo" \
	FALSE Resolution "Set screen resolution (DeckHD or DeckSight display mod)" \
	FALSE Custom "Replace Clover EFI with a custom build that hides the OPTIONS button" \
	FALSE Uninstall "Uninstall Clover and restore all changes" \
	TRUE Exit "***** Exit Clover toolbox *****")

if [ $? -eq 1 ] || [ "$Choice" == "Exit" ]
then
	echo "The user pressed cancel/exit."
	exit

elif [ "$Choice" == "Status" ]
then
	zenity --warning --title "Clover Toolbox" --text "$(fold -w 120 -s ~/1Clover-tools/status.txt)" --width 1000 --height 400

elif [ "$Choice" == "Batocera" ]
then
Batocera_Choice=$(zenity --width 550 --height 220 --list --radiolist --multiple --title "Clover Toolbox" --column "Select" \
	--column "Options" --column "Notes - please read carefully" \
	FALSE v39 "Configure Clover for Batocera v39 and newer" \
	FALSE v38 "Configure Clover for Batocera v38 and older" \
	TRUE Exit "***** Exit Clover toolbox *****")

	if [ $? -eq 1 ] || [ "$Batocera_Choice" == "Exit" ]
	then
		echo "The user pressed cancel. Returning to the main menu."

	elif [ "$Batocera_Choice" == "v39" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<string>os_batocera<\/string>/!b;n;n;c\\t\t\t\t\t<string>\\efi\\batocera\\grubx64\.efi<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover Toolbox" --text "The Clover configuration was updated for Batocera v39 and newer!" --width 450 --height 75

	elif [ "$Batocera_Choice" == "v38" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<string>os_batocera<\/string>/!b;n;n;c\\t\t\t\t\t<string>\\efi\\boot\\bootx64\.efi<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover Toolbox" --text "The Clover configuration was updated for Batocera v38 and older!" --width 450 --height 75

	fi

elif [ "$Choice" == "Theme" ]
then
Theme_Choice=$(zenity --title "Clover Toolbox"	--width 200 --height 325 --list \
	--column "Theme name" $(printf '%s\n' "$current_password" | sudo -S ls $EFI_PATH/clover/themes) )

	if [ $? -eq 1 ]
	then
		echo "The user pressed cancel. Returning to the main menu."
	else
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>Theme<\/key>/!b;n;c\\t\t<string>'$Theme_Choice'<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "The theme was changed to $Theme_Choice!" --width 400 --height 75
	fi

elif [ "$Choice" == "Timeout" ]
then
Timeout_Choice=$(zenity --width 500 --height 300 --list --radiolist --multiple \
	--title "Clover Toolbox" --column "Select" --column "Options" --column "Notes - please read carefully" \
	FALSE 1 "Set default timeout to 1 second" \
	FALSE 5 "Set default timeout to 5 seconds" \
	FALSE 10 "Set default timeout to 10 seconds" \
	FALSE 15 "Set default timeout to 15 seconds" \
 	FALSE 60 "Set default timeout to 60 seconds" \
	TRUE Exit "***** Exit Clover toolbox *****")

	if [ $? -eq 1 ] || [ "$Timeout_Choice" == "Exit" ]
	then
		echo "The user pressed cancel. Returning to the main menu."
	else
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>Timeout<\/key>/!b;n;c\\t\t<integer>'$Timeout_Choice'<\/integer>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "The default timeout was set to $Timeout_Choice seconds!" --width 400 --height 75
	fi

elif [ "$Choice" == "Service" ]
then
Service_Choice=$(zenity --width 650 --height 250 --list --radiolist --multiple --title "Clover Toolbox" \
	--column "Select" --column "Options" --column "Notes - please read carefully" \
	FALSE Disable "Disable Clover EFI entry and systemd service" \
	FALSE Enable "Enable Clover EFI entry and systemd service" \
	TRUE Exit "***** Exit Clover toolbox *****")

	if [ $? -eq 1 ] || [ "$Service_Choice" == "Exit" ]
	then
		echo "The user pressed cancel. Returning to the main menu."

	elif [ "$Service_Choice" == "Disable" ]
	then
		printf '%s\n' "$current_password" | sudo -S cp $EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig $EFI_PATH/Microsoft/Boot/bootmgfw.efi

		Windows=$(efibootmgr | grep -i Windows | colrm 9 | colrm 1 4)
		printf '%s\n' "$current_password" | sudo -S efibootmgr -n $Windows &> /dev/null

		printf '%s\n' "$current_password" | sudo -S systemctl disable --now clover-bootmanager
		zenity --warning --title "Clover Toolbox" --text "The Clover systemd service was disabled. Windows is now active!" --width 500 --height 75

	elif [ "$Service_Choice" == "Enable" ]
	then
		sudo systemctl enable --now clover-bootmanager
		printf '%s\n' "$current_password" | sudo -S /etc/systemd/system/clover-bootmanager.sh
		zenity --warning --title "Clover Toolbox" --text "The Clover systemd service was enabled. Windows is now disabled!" --width 500 --height 75
	fi

elif [ "$Choice" == "Default boot" ]
then
Boot_Choice=$(zenity --width 550 --height 300 --list --radiolist --multiple --title "Clover Toolbox" --column "Select" \
	--column "Options" --column "Notes - please read carefully" \
	FALSE Windows "Set Windows as the default boot OS" \
	FALSE SteamOS "Set SteamOS as the default boot OS" \
	FALSE Bazzite "Set Bazzite as the default boot OS" \
	FALSE LastOS "Set the last-booted OS as default" \
	TRUE Exit "***** Exit Clover toolbox *****")

	if [ $? -eq 1 ] || [ "$Boot_Choice" == "Exit" ]
	then
		echo "The user pressed cancel. Returning to the main menu."

	elif [ "$Boot_Choice" == "Windows" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\microsoft\\bootmgfw\.efi<\/string>' $EFI_PATH/clover/config.plist
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover Toolbox" --text "Windows is now the default boot entry in Clover!" --width 400 --height 75

	elif [ "$Boot_Choice" == "SteamOS" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\steamos\\steamcl\.efi<\/string>' $EFI_PATH/clover/config.plist
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "SteamOS is now the default boot entry in Clover!" --width 400 --height 75

	elif [ "$Boot_Choice" == "Bazzite" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\EFI\\FEDORA\\shimx64\.efi<\/string>' $EFI_PATH/clover/config.plist
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "Bazzite is now the default boot entry in Clover!" --width 400 --height 75

	elif [ "$Boot_Choice" == "Last OS" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>LastBootedVolume<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "The last used system is now the default boot entry in Clover!" --width 425 --height 75
	fi

elif [ "$Choice" == "New Logo" ]
then
Logo_Choice=$(zenity --title "Clover Toolbox" --width 200 --height 350 --list \
	--column "Logo name" $(ls -l ~/1Clover-tools/logos/*.png | sed s/^.*\\/\//) )
	if [ $? -eq 1 ]
	then
		echo "The user pressed cancel. Returning to the main menu."
	else
		printf '%s\n' "$current_password" | sudo -S cp ~/1Clover-tools/logos/$Logo_Choice $EFI_PATH/steamos/steamos.png
		zenity --warning --title "Clover Toolbox" --text "The BGRT logo was changed to $Logo_Choice!" --width 400 --height 75
	fi

elif [ "$Choice" == "Restore Logo" ]
then
	printf '%s\n' "$current_password" | sudo -S rm $EFI_PATH/steamos/steamos.png &> /dev/null
	zenity --warning --title "Clover Toolbox" --text "The BGRT logo was restored to the default!" --width 400 --height 75

elif [ "$Choice" == "Resolution" ]
then
Resolution_Choice=$(zenity --width 550 --height 250 --list --radiolist --multiple --title "Clover Toolbox" \
	--column "Select" --column "Options" --column "Notes - please read carefully" \
	FALSE Default "Use default resolution 1280x800" \
	FALSE DeckHD "Use DeckHD resolution 1920x1200" \
	FALSE DeckSight "Use DeckSight resolution 1920x1080" \
	TRUE Exit "***** Exit Clover toolbox *****")

	if [ $? -eq 1 ] || [ "$Resolution_Choice" == "Exit" ]
	then
		echo "The user pressed cancel. Returning to the main menu."

	elif [ "$Resolution_Choice" == "Default" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1280x800<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "The screen resolution was set to 1280x800." --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckHD" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1200<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "The screen resolution was set to 1920x1200." --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckSight" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "The screen resolution was set to 1920x1080." --width 400 --height 75

	fi

elif [ "$Choice" == "Custom" ]
then
	printf '%s\n' "$current_password" | sudo -S cp ~/1Clover-tools/efi/custom_clover_5157.efi $EFI_PATH/clover/cloverx64.efi
	zenity --warning --title "Clover Toolbox" --text "The custom Clover EFI was installed!" --width 400 --height 75

elif [ "$Choice" == "Uninstall" ]
then
	# 修复：卸载前先确认要恢复的文件都存在。原来 .orig 不存在时 mv 失败后
	# 不做任何检查就继续 rm -rf $EFI_PATH/clover，会留下“Clover 文件删了、
	# Windows/BOOTX64 又没恢复”的半卸载状态，可能直接无法开机。
	UNINSTALL_OK=1
	if [ ! -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" ] \
		&& [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" ]; then
		echo "⚠️ bootmgfw.efi.orig not found, skipping the Windows EFI restore (leaving it as is)."
	elif [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" ]; then
		if ! sudo -n mv -f "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" "$EFI_PATH/Microsoft/Boot/bootmgfw.efi"; then
			echo "❌ Failed to restore Windows bootmgfw.efi, uninstall aborted, no other changes were made."
			UNINSTALL_OK=0
		fi
	fi
	if [ "$UNINSTALL_OK" -eq 1 ] && [ ! -e "$BOOTX64.orig" ]; then
		echo "⚠️ $BOOTX64.orig not found, skipping the BOOTX64.EFI restore (leaving it as is)."
	elif [ "$UNINSTALL_OK" -eq 1 ]; then
		if ! sudo -n mv -f "$BOOTX64.orig" "$BOOTX64"; then
			echo "❌ Failed to restore BOOTX64.EFI, uninstall aborted, no other changes were made."
			UNINSTALL_OK=0
		fi
	fi
	if [ "$UNINSTALL_OK" -ne 1 ]; then
		zenity --error --title "Clover Toolbox" --text "Uninstall aborted: failed to restore the critical boot files.\nPlease check the EFI partition manually and try again." --width 500 --height 100
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
				&& echo "Read-only mode restored." \
				|| echo "⚠️ Cannot restore read-only mode, please run manually: sudo steamos-readonly enable"
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

	rm -f ~/Desktop/Boot\ Config.desktop

	zenity --warning --title "Clover Toolbox" --text "Clover was uninstalled and the Windows EFI entry is active again!" --width 600 --height 75
	exit
fi
done
TOOLBOX_EOF
    fi


    chmod +x ~/1Clover-tools/Clover-Toolbox.sh 2>/dev/null || true
    # 提示已在上面的分支里按「原版/回退」分别打印，这里不再重复宣称汉化

    echo -e "${YELLOW}It is recommended to reboot the device for the boot changes to take effect.${NC}"
    echo ""
}

install_anydesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Install/Update AnyDesk ════════════════${NC}"

    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    local ANYDESK_BIN="$ANYDESK_INSTALL_DIR/anydesk"
    local DESKTOP_FILE="$HOME/Desktop/AnyDesk.desktop"

    # FIX-SOFTWARE: add --fail/timeouts; never invent a default version that could downgrade.
    echo "Checking the latest version..."
    local REMOTE_VERSION=$(curl -fsSL --connect-timeout 15 --max-time 60 https://anydesk.com.cn/zhs/downloads/linux 2>/dev/null | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/^v//')
    if [ -z "$REMOTE_VERSION" ]; then
        echo -e "${YELLOW}Could not reliably read the remote version (network or page changed); update cancelled, keeping the current install.${NC}"
        echo -e "${YELLOW}  No hardcoded fallback version, to avoid accidentally downgrading.${NC}"
        return 0
    fi
    echo "Latest version: $REMOTE_VERSION"

    local LOCAL_VERSION=""
    if [ -f "$ANYDESK_BIN" ] && [ -x "$ANYDESK_BIN" ]; then
        LOCAL_VERSION=$("$ANYDESK_BIN" --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [ -n "$LOCAL_VERSION" ]; then
            echo -e "${CYAN}Currently installed version: ${LOCAL_VERSION}${NC}"
        else
            echo -e "${YELLOW}Installed, but the version number cannot be read; reinstalling.${NC}"
        fi
    else
        echo -e "${YELLOW}AnyDesk is not installed.${NC}"
    fi

    local TARGET_VERSION=""
    if [ -n "$LOCAL_VERSION" ]; then
        # Only update when the remote version is strictly greater than the local one.
        if ! fs_ver_gt "$REMOTE_VERSION" "$LOCAL_VERSION"; then
            echo -e "${GREEN}✅ Local ${LOCAL_VERSION} is not older than remote ${REMOTE_VERSION}; keeping the current install (no downgrade).${NC}"
            return 0
        fi
        echo -e "${YELLOW}A newer version ${REMOTE_VERSION} was found (current: ${LOCAL_VERSION})${NC}"
        if ! confirm_action; then
            echo "Update cancelled."
            return 0
        fi
        TARGET_VERSION="$REMOTE_VERSION"
    else
        TARGET_VERSION="$REMOTE_VERSION"
    fi

    if [ -z "$TARGET_VERSION" ]; then
        echo "No target version specified, operation cancelled."
        return 0
    fi

    echo "Installing AnyDesk ${TARGET_VERSION}..."
    cd /tmp || return

    # FIX-SOFTWARE: mktemp -d (no shared fixed /tmp name); --fail/timeouts on download.
    local URL="https://download.anydesk.com/linux/anydesk-${TARGET_VERSION}-amd64.tar.gz"
    local WORK_DIR
    WORK_DIR="$(mktemp -d /tmp/anydesk-install.XXXXXXXX 2>/dev/null)" || {
        echo -e "${RED}✗ Cannot create a temp dir; aborted.${NC}"; return 1; }
    local TARBALL="$WORK_DIR/anydesk-${TARGET_VERSION}.tar.gz"
    local EXTRACT_DIR="$WORK_DIR/extract"
    echo "Downloading..."

    if ! wget -q --show-progress --connect-timeout=15 --timeout=180 --tries=1 "$URL" -O "$TARBALL"; then
        echo -e "${RED}Download failed, please check your network and try again.${NC}"
        echo -e "${YELLOW}The existing AnyDesk installation (if any) was kept.${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    if [ ! -s "$TARBALL" ]; then
        echo -e "${RED}Downloaded file is empty or not a valid archive; aborted.${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    mkdir -p "$EXTRACT_DIR" || { rm -rf "$WORK_DIR"; return 1; }
    if ! tar -xzf "$TARBALL" -C "$EXTRACT_DIR" --strip-components=1; then
        echo -e "${RED}✗ Extraction failed, installation aborted.${NC}"
        rm -rf "$WORK_DIR"
        echo -e "${YELLOW}The existing AnyDesk installation (if any) was kept.${NC}"
        return 1
    fi
    if [ ! -x "$EXTRACT_DIR/anydesk" ]; then
        echo -e "${RED}✗ The package contents are incomplete (anydesk executable not found), installation aborted.${NC}"
        rm -rf "$WORK_DIR"
        echo -e "${YELLOW}The existing AnyDesk installation (if any) was kept.${NC}"
        return 1
    fi

    # Atomic replace: stage new content, then mv into place; never delete the old dir first.
    local STAGE_DIR="$WORK_DIR/stage"
    if ! mkdir -p "$STAGE_DIR"; then rm -rf "$WORK_DIR"; return 1; fi
    if ! cp -a "$EXTRACT_DIR"/. "$STAGE_DIR"/; then
        echo -e "${RED}✗ Failed to copy the installation files.${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    chmod +x "$STAGE_DIR/anydesk" 2>/dev/null
    if [ ! -x "$STAGE_DIR/anydesk" ]; then
        echo -e "${RED}✗ Staged files lack the executable; aborted (old install untouched).${NC}"
        rm -rf "$WORK_DIR"
        return 1
    fi
    local BACKUP_DIR=""
    if [ -d "$ANYDESK_INSTALL_DIR" ]; then
        BACKUP_DIR="$WORK_DIR/backup"
        if ! mv "$ANYDESK_INSTALL_DIR" "$BACKUP_DIR"; then
            echo -e "${RED}✗ Failed to back up the old install; aborted (old install untouched).${NC}"
            rm -rf "$WORK_DIR"
            return 1
        fi
    fi
    if ! mv "$STAGE_DIR" "$ANYDESK_INSTALL_DIR"; then
        echo -e "${RED}✗ Failed to install the new version; restoring the old one...${NC}"
        [ -n "$BACKUP_DIR" ] && mv "$BACKUP_DIR" "$ANYDESK_INSTALL_DIR" 2>/dev/null
        rm -rf "$WORK_DIR"
        return 1
    fi
    rm -rf "$WORK_DIR"
    if [ ! -x "$ANYDESK_BIN" ]; then
        echo -e "${RED}✗ The installation files are incomplete (executable not found).${NC}"
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
    echo -e "${GREEN}✅ AnyDesk ${TARGET_VERSION} installed! Desktop shortcut created.${NC}"
}

uninstall_anydesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Uninstall AnyDesk ════════════════${NC}"

    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    local DESKTOP_FILE="$HOME/Desktop/AnyDesk.desktop"
    local BIN_LINK="$HOME/.local/bin/anydesk"
    local flatpak_id="com.anydesk.Anydesk"

    local local_found=false
    local flatpak_found=false
    [ -d "$ANYDESK_INSTALL_DIR" ] && local_found=true
    flatpak info "$flatpak_id" &>/dev/null && flatpak_found=true

    if ! $local_found && ! $flatpak_found; then
        echo -e "${YELLOW}AnyDesk is not installed.${NC}"
        return 0
    fi

    echo -e "${CYAN}AnyDesk installation detected:${NC}"
    $local_found && echo "  • Local installation ($ANYDESK_INSTALL_DIR)"
    $flatpak_found && echo "  • Flatpak installation ($flatpak_id)"

    read -n1 -p "Press Enter or A to confirm uninstalling, any other key to cancel: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "Continuing the uninstall..."
    else
        echo "Uninstall cancelled."
        return 0
    fi

    local fail=0
    if $local_found; then
        if rm -rf "$ANYDESK_INSTALL_DIR"; then
            echo -e "${GREEN}✓ Local installation directory deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete local installation directory${NC}"; fail=1
        fi
        if rm -f "$DESKTOP_FILE"; then
            echo -e "${GREEN}✓ Local desktop shortcut deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete local desktop shortcut${NC}"; fail=1
        fi
        if rm -f "$BIN_LINK"; then
            echo -e "${GREEN}✓ Command link deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete command link${NC}"; fail=1
        fi
    fi

    if $flatpak_found; then
        echo "Uninstalling the Flatpak version of AnyDesk..."
        if flatpak uninstall "$flatpak_id" -y &>/dev/null; then
            echo -e "${GREEN}✓ Flatpak version uninstalled${NC}"
            local desktop_dir="$HOME/Desktop"
            if [ -d "$desktop_dir" ]; then
                for f in "$desktop_dir"/*.desktop; do
                    local base=$(basename "$f")
                    if [ "$base" = "AnyDesk.desktop" ] || \
                       [ "$base" = "${flatpak_id}.desktop" ] || \
                       [[ "$base" == *"${flatpak_id//./_}"* ]]; then
                        rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ Desktop shortcut deleted: $base${NC}"
                    fi
                done
            fi

            local data_dir="$HOME/.var/app/$flatpak_id"
            if [ -d "$data_dir" ]; then
                echo ""
                echo -e "${CYAN}Delete all settings and user data for AnyDesk?${NC}"
                read -n1 -p "Press Enter or A to confirm deletion, any other key to keep: " del_data < /dev/tty
                echo
                if [[ -z "$del_data" || "$del_data" =~ [Aa] ]]; then
                    rm -rf "$data_dir" && echo -e "${GREEN}✓ User data deleted${NC}"
                else
                    echo -e "${YELLOW}User data kept.${NC}"
                fi
            else
                echo -e "${YELLOW}User data directory not found, skipping.${NC}"
            fi

        else
            echo -e "${RED}✗ Failed to uninstall the Flatpak version${NC}"
            fail=1
        fi
    fi

    echo ""
    if [ "$fail" -ne 0 ]; then
        echo -e "${RED}✗ Uninstall had failures; not reporting full success, see hints above.${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ AnyDesk uninstalled.${NC}"
}

install_todesk() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install ToDesk ════════════════${NC}"
    echo ""

    # ToDesk 官方 Arch 包长期停留在 4.1.0，社区（archtodesk）重打包了 4.7.2.0。
    # 这里不再执行任何第三方 shell 脚本，改为自己取回 .pkg.tar.zst 后用 pacman 直接装：
    # 少跑一段 root 脚本、不重建 pacman 钥匙环、不装 base-devel、不硬编码 /home/deck。
    local TODESK_REPO="https://gitee.com/mclanbai/archtodesk.git"
    local TODESK_PKG="todesk-bin-4.7.2.0-4-x86_64.pkg.tar.zst"
    local TODESK_VERSION="4.7.2.0"
    local CLONE_DIR="$TEMP_DIR/archtodesk"
    local DESKTOP_FILE="$HOME/Desktop/ToDesk.desktop"

    echo "  Source: gitee.com/mclanbai/archtodesk (community-repacked official 4.7.2.0 package)"
    echo "  This only downloads the .pkg.tar.zst from that repo and installs it with pacman; no other scripts are run."
    echo ""

    # ---------- 已安装检测 ----------
    # 三种来源都算「已安装」：pacman 包（todesk-bin / todesk）、/opt/todesk 程序目录、
    # 以及能直接跑起来的 ToDesk 二进制。只看 pacman 会漏掉包数据库损坏或手动解包的情况。
    local installed_ver="" installed_src=""
    if pacman -Q todesk-bin &>/dev/null; then
        installed_ver=$(pacman -Q todesk-bin 2>/dev/null | awk '{print $2}')
        installed_src="pacman package todesk-bin"
    elif pacman -Q todesk &>/dev/null; then
        installed_ver=$(pacman -Q todesk 2>/dev/null | awk '{print $2}')
        installed_src="pacman package todesk"
    elif [ -x /opt/todesk/bin/ToDesk ] || [ -d /opt/todesk ]; then
        installed_ver="Unknown (not installed via pacman)"
        installed_src="/opt/todesk directory"
    fi

    if [ -n "$installed_ver" ]; then
        echo -e "${GREEN}✓ Installed ToDesk detected${NC}"
        echo "    Current version: ${installed_ver}"
        echo "    Install source: ${installed_src}"
        echo "    Target version: ${TODESK_VERSION}"
        echo ""
        echo -e "${YELLOW}Please choose an action:${NC}"
        echo "  1. Reinstall (uninstall current version, then install ${TODESK_VERSION})"
        echo "  2. Do not install; exit"
        echo "  3. Uninstall ToDesk (do not reinstall)"
        echo ""
        local choice
        while true; do
            if ! read -p "Enter choice [1-3] (Enter defaults to 2): " choice < /dev/tty; then
                echo ""
                echo -e "${GREEN}Keeping current install; no changes made.${NC}"
                return 0
            fi
            case "$choice" in
                1) break ;;
                3)
                    echo ""
                    uninstall_todesk
                    return $? ;;
                ""|2)
                    echo -e "${GREEN}Keeping current install; no changes made.${NC}"
                    return 0 ;;
                *) echo -e "${RED}Invalid input; enter 1, 2, or 3.${NC}" ;;
            esac
        done
        echo -e "${CYAN}Will uninstall the current version and reinstall...${NC}"
    fi

    # ---------- 前置工具 ----------
    local missing_tools=()
    command -v git &>/dev/null || missing_tools+=("git")
    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${YELLOW}Missing required tools: ${missing_tools[*]}${NC}"
        if ! ensure_writable; then return 1; fi
        if ! sudo pacman -S --needed --noconfirm "${missing_tools[@]}"; then
            echo -e "${RED}✗ Failed to install ${missing_tools[*]}.${NC}"
            return 1
        fi
    fi

    # ---------- 解除只读（pacman 写系统需要） ----------
    if ! ensure_writable; then return 1; fi

    # ---------- 运行依赖 ----------
    echo ""
    echo -e "${CYAN}Checking runtime dependencies...${NC}"
    local missing_deps=()
    for dep in gtk3 libappindicator-gtk3; do
        pacman -Q "$dep" &>/dev/null || missing_deps+=("$dep")
    done
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${YELLOW}Missing dependencies: ${missing_deps[*]}; installing...${NC}"
        if ! sudo pacman -S --needed --noconfirm "${missing_deps[@]}"; then
            echo -e "${RED}✗ Dependency install failed; aborted.${NC}"
            return 1
        fi
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✓ Dependencies satisfied (gtk3, libappindicator-gtk3)${NC}"
    fi

    # ---------- 取回安装包 ----------
    # 注意：Gitee 对仓库内 >1MB 的文件禁止匿名 raw 直链（返回 403 large file require
    # login），所以 80MB 的包只能通过 git clone 取，不能直接 curl 下载。
    echo ""
    echo -e "${CYAN}Downloading ToDesk $TODESK_VERSION package (~80MB)...${NC}"
    echo -e "${YELLOW}(Gitee blocks large direct downloads; cloning the repo instead, please wait)${NC}"
    rm -rf "$CLONE_DIR"
    if ! git clone --depth 1 --progress "$TODESK_REPO" "$CLONE_DIR"; then
        echo -e "${RED}✗ Download failed; check network and retry.${NC}"
        rm -rf "$CLONE_DIR"
        return 1
    fi

    local pkg_path="$CLONE_DIR/$TODESK_PKG"
    if [ ! -f "$pkg_path" ]; then
        echo -e "${RED}✗ $TODESK_PKG not found in the repo; upstream layout may have changed.${NC}"
        echo -e "${YELLOW}  Aborted; system was not modified.${NC}"
        rm -rf "$CLONE_DIR"
        return 1
    fi

    # ---------- 完整性校验 ----------
    echo ""
    echo -e "${CYAN}Verifying package integrity...${NC}"
    local verify_ok=0
    if command -v zstd &>/dev/null; then
        zstd -t "$pkg_path" &>/dev/null && verify_ok=1
    else
        pacman -Qip "$pkg_path" &>/dev/null && verify_ok=1
    fi
    if [ "$verify_ok" -ne 1 ]; then
        echo -e "${RED}✗ Package checksum failed (corrupt/incomplete); aborted.${NC}"
        rm -rf "$CLONE_DIR"
        return 1
    fi
    echo -e "${GREEN}✓ Package is intact${NC}"

    # ---------- Remove old versions ----------
    # FIX-SOFTWARE: record old packages; abort immediately on removal failure (no || true).
    local OLD_PKGS=""
    pacman -Q todesk &>/dev/null && OLD_PKGS="$OLD_PKGS todesk"
    pacman -Q todesk-bin &>/dev/null && OLD_PKGS="$OLD_PKGS todesk-bin"
    OLD_PKGS="${OLD_PKGS# }"
    [ -n "$OLD_PKGS" ] && echo -e "${CYAN}Old packages before install:$OLD_PKGS (recorded for recovery)${NC}"
    if pacman -Q todesk &>/dev/null; then
        echo -e "${CYAN}Uninstalling old todesk package...${NC}"
        if ! sudo pacman -R --noconfirm todesk; then
            echo -e "${RED}✗ Failed to remove old todesk; aborted to avoid version conflicts.${NC}"
            echo -e "${YELLOW}  Run manually: sudo pacman -R --noconfirm todesk${NC}"
            rm -rf "$CLONE_DIR"
            return 1
        fi
    fi
    if pacman -Q todesk-bin &>/dev/null; then
        echo -e "${CYAN}Uninstalling existing todesk-bin...${NC}"
        if ! sudo pacman -R --noconfirm todesk-bin; then
            echo -e "${RED}✗ Failed to remove existing todesk-bin; aborted.${NC}"
            echo -e "${YELLOW}  Old packages:${OLD_PKGS:-none}${NC}"
            echo -e "${YELLOW}  To restore: sudo pacman -U --noconfirm $pkg_path (package kept at $CLONE_DIR)${NC}"
            rm -rf "$CLONE_DIR"
            return 1
        fi
    fi

    # ---------- Clean orphaned files (critical) ----------
    # Handles a dirty state that `pacman -R` cannot reach: the package record is gone
    # (interrupted uninstall, manually pruned database, or a manual extraction install),
    # but files such as /opt/todesk are still on disk.
    # In that case `pacman -U` refuses with "exists in filesystem" and both `pacman -Q`
    # checks above are false, so the cleanup is skipped entirely -- this is exactly the
    # root cause of the reinstall failure.
    # Rule: package not registered + files present = orphaned leftovers, clear them here.
    # Note: db.lck is NOT part of the "are there leftovers" test -- it is pacman's global
    # lock and exists whenever any pacman runs, unrelated to ToDesk. It is only removed
    # as part of an actual cleanup.
    local orphan_paths=(
        /opt/todesk
        /usr/bin/todesk
        /usr/lib/systemd/system/todeskd.service
        /usr/share/applications/todesk.desktop
        /usr/share/licenses/todesk-bin
    )
    local orphan_found=false
    for op in "${orphan_paths[@]}"; do
        if [ -e "$op" ]; then orphan_found=true; break; fi
    done
    if [ "$orphan_found" = true ] \
       && ! pacman -Q todesk-bin &>/dev/null \
       && ! pacman -Q todesk &>/dev/null; then
        echo ""
        echo -e "${YELLOW}Found leftover ToDesk files (package not registered, files still present)${NC}"
        echo -e "${CYAN}Cleaning leftovers so pacman does not report 'exists in filesystem'...${NC}"
        # Stop the service and kill processes first, otherwise busy binaries under
        # /opt/todesk cannot be removed cleanly.
        sudo systemctl stop todeskd.service 2>/dev/null || true
        sudo systemctl disable todeskd.service 2>/dev/null || true
        sudo pkill -f '/opt/todesk/bin/' 2>/dev/null || true
        sleep 1
        for op in "${orphan_paths[@]}"; do
            [ -e "$op" ] || continue
            sudo rm -rf "$op" 2>/dev/null || true
        done
        # Icons: remove only ToDesk's own icons, leave other packages in hicolor alone.
        sudo rm -f /usr/share/icons/hicolor/*/apps/todesk.png 2>/dev/null || true
        # pacman's database lock: a previously interrupted install may have left it behind,
        # which makes every later pacman run report "could not lock database". Only remove
        # it when no pacman process is running, so an in-progress operation is not disturbed.
        if [ -e /usr/lib/holo/pacmandb/db.lck ] && ! pgrep -x pacman &>/dev/null; then
            sudo rm -f /usr/lib/holo/pacmandb/db.lck 2>/dev/null || true
        fi
        sudo systemctl daemon-reload 2>/dev/null || true

        # Re-check: report clearly instead of letting pacman fail with a cryptic conflict.
        local still_left=""
        for op in "${orphan_paths[@]}"; do
            if [ -e "$op" ]; then still_left="$still_left $op"; fi
        done
        if [ -n "$still_left" ]; then
            echo -e "${RED}✗ Could not remove these leftovers:$still_left${NC}"
            echo -e "${YELLOW}  Please run manually: sudo rm -rf$still_left${NC}"
            rm -rf "$CLONE_DIR"
            return 1
        fi
        echo -e "${GREEN}✓ Leftovers cleaned${NC}"
    fi

    # ---------- Install ----------
    echo ""
    echo -e "${CYAN}Installing ToDesk $TODESK_VERSION ...${NC}"
    if ! sudo pacman -U --noconfirm "$pkg_path"; then
        echo -e "${RED}✗ Install failed; check pacman output above.${NC}"
        echo -e "${YELLOW}  Old packages:${OLD_PKGS:-none} were removed and are NOT auto-reinstalled.${NC}"
        echo -e "${YELLOW}  Restore manually: sudo pacman -U --noconfirm $pkg_path${NC}"
        echo -e "${YELLOW}  (package kept at $CLONE_DIR)${NC}"
        return 1
    fi

    # ---------- Service & shortcut: check rc + verify with is-active ----------
    # FIX-SOFTWARE: no more || true swallowing enable/restart failures; no false success.
    local svc_fail=0
    if ! sudo systemctl daemon-reload 2>/dev/null; then
        echo -e "${YELLOW}⚠ systemctl daemon-reload failed${NC}"
    fi
    if ! sudo systemctl enable todeskd.service 2>/dev/null; then
        echo -e "${RED}✗ Failed to enable todeskd.service${NC}"
        svc_fail=1
    fi
    if ! sudo systemctl restart todeskd.service 2>/dev/null; then
        echo -e "${RED}✗ Failed to restart todeskd.service${NC}"
        svc_fail=1
    fi
    if ! systemctl is-active --quiet todeskd.service 2>/dev/null; then
        echo -e "${RED}✗ todeskd.service is not active${NC}"
        echo -e "${YELLOW}  Check manually: systemctl status todeskd.service${NC}"
        svc_fail=1
    else
        echo -e "${GREEN}✓ todeskd.service enabled and active${NC}"
    fi

    if [ -f /usr/share/applications/todesk.desktop ]; then
        mkdir -p "$HOME/Desktop"
        if cp -f /usr/share/applications/todesk.desktop "$DESKTOP_FILE" 2>/dev/null; then
            chmod +x "$DESKTOP_FILE" 2>/dev/null || true
            echo -e "${GREEN}✓ Desktop shortcut created${NC}"
        fi
    fi

    # ---------- 清理旧方案残留 ----------
    # 旧版本会引导用户执行第三方脚本，在桌面留下这两个「安装/重装」图标，顺手清掉。
    rm -f "$HOME/Desktop/install-todesk-service.desktop" \
          "$HOME/Desktop/reinstall-todesk-service.desktop" 2>/dev/null || true
    sudo rm -rf /tmp/lanbai 2>/dev/null || true
    rm -rf "$CLONE_DIR"

    # ---------- Result ----------
    echo ""
    if [ "$svc_fail" -ne 0 ]; then
        echo -e "${RED}✗ Package installed but the service did not start; not reporting success.${NC}"
        return 1
    fi
    if pacman -Q todesk-bin &>/dev/null || [ -x /opt/todesk/bin/ToDesk ]; then
        echo -e "${GREEN}✅ ToDesk $TODESK_VERSION installed${NC}"
        echo -e "${YELLOW}Tip: ToDesk supports X11 only, not Wayland.${NC}"
        echo -e "${YELLOW}      In Gaming Mode, switch to Desktop Mode first; the desktop shortcut is at $DESKTOP_FILE${NC}"
    else
        echo -e "${RED}✗ ToDesk not detected after install; check output above.${NC}"
        return 1
    fi
}

uninstall_todesk() {
    clear
    echo -e "${YELLOW}════════════════ Uninstall ToDesk ════════════════${NC}"
    echo ""

    local DESKTOP_FILE="$HOME/Desktop/ToDesk.desktop"
    local AUTOSTART_FILE="$HOME/.config/autostart/todesk.desktop"
    local USER_DATA_DIR="$HOME/.local/share/todesk"

    # ---------- 已安装检测 ----------
    # 与 install_todesk 用同一套判据：pacman 包（todesk-bin / todesk）或 /opt/todesk 目录，
    # 任一存在就算已安装。只看 pacman 会漏掉「包数据库损坏」和「手动解包安装」这两种情况。
    local pkg_name="" pkg_ver=""
    if pacman -Q todesk-bin &>/dev/null; then
        pkg_name="todesk-bin"
        pkg_ver=$(pacman -Q todesk-bin 2>/dev/null | awk '{print $2}')
    elif pacman -Q todesk &>/dev/null; then
        pkg_name="todesk"
        pkg_ver=$(pacman -Q todesk 2>/dev/null | awk '{print $2}')
    fi
    local has_dir=false
    [ -d /opt/todesk ] && has_dir=true

    if [ -z "$pkg_name" ] && [ "$has_dir" = false ]; then
        echo -e "${YELLOW}No installed ToDesk detected; nothing to uninstall.${NC}"
        return 0
    fi

    echo -e "${CYAN}Detected ToDesk install:${NC}"
    [ -n "$pkg_name" ] && echo "  • pacman package ${pkg_name} ${pkg_ver}"
    [ "$has_dir" = true ] && echo "  • Program directory /opt/todesk"
    echo ""
    echo -e "${YELLOW}The following actions will be performed:${NC}"
    echo "  1. Stop and disable the todeskd service; kill running ToDesk processes"
    echo "  2. Uninstall the pacman package (if present) and clean leftover /opt/todesk"
    echo "  3. Delete desktop shortcut and autostart entries"
    echo ""
    read -n1 -p "Press Enter or A to confirm uninstall; any other key cancels: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo -e "${CYAN}Continuing uninstall...${NC}"
    else
        echo -e "${GREEN}Cancelled; no changes made.${NC}"
        return 0
    fi

    # ---------- 停止服务与进程 ----------
    echo ""
    echo -e "${CYAN}Stopping ToDesk service...${NC}"
    sudo systemctl stop todeskd.service 2>/dev/null || true
    sudo systemctl disable todeskd.service 2>/dev/null || true
    echo -e "${GREEN}✓ todeskd service stopped and disabled${NC}"
    # 卸载前先结束残留进程，否则 /opt/todesk 里的二进制被占用会让删除不干净
    sudo pkill -f '/opt/todesk/bin/' 2>/dev/null || true

    # ---------- 卸载 pacman 包 ----------
    if [ -n "$pkg_name" ]; then
        if ! ensure_writable; then return 1; fi
        echo ""
        echo -e "${CYAN}Uninstalling pacman package ${pkg_name} ...${NC}"
        if sudo pacman -R --noconfirm "$pkg_name"; then
            echo -e "${GREEN}✓ ${pkg_name} uninstalled${NC}"
        else
            echo -e "${RED}✗ Failed to uninstall ${pkg_name}; check pacman output above.${NC}"
            return 1
        fi
    fi

    # ---------- 清理残留目录 ----------
    # 手动解包安装（不经过 pacman）的设备，/opt/todesk 不在包数据库里，
    # pacman -R 不会删它，必须自己清掉，否则下次检测仍会判成「已安装」。
    if [ -d /opt/todesk ]; then
        if ! ensure_writable; then return 1; fi
        echo ""
        echo -e "${CYAN}Cleaning leftover /opt/todesk ...${NC}"
        sudo rm -rf /opt/todesk 2>/dev/null || true
        if [ -d /opt/todesk ]; then
            echo -e "${YELLOW}⚠ /opt/todesk could not be fully removed; run manually: sudo rm -rf /opt/todesk${NC}"
        else
            echo -e "${GREEN}✓ /opt/todesk deleted${NC}"
        fi
    fi
    sudo systemctl daemon-reload 2>/dev/null || true

    # ---------- 快捷方式与自启项 ----------
    # 桌面快捷方式、自启项都不是包内文件（pacman -R 不会删），
    # 连同旧方案遗留的两个「安装/重装」图标一起清掉。
    local f
    for f in "$DESKTOP_FILE" "$HOME/Desktop/todesk.desktop" \
             "$HOME/Desktop/install-todesk-service.desktop" \
             "$HOME/Desktop/reinstall-todesk-service.desktop" \
             "$AUTOSTART_FILE"; do
        if [ -e "$f" ]; then
            rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ Deleted $f${NC}"
        fi
    done

    # ---------- 用户数据 ----------
    if [ -d "$USER_DATA_DIR" ]; then
        echo ""
        echo -e "${CYAN}Delete ToDesk config and user data ($USER_DATA_DIR)?${NC}"
        echo -e "${YELLOW}After deletion you must log in again and reconfigure the device list.${NC}"
        read -n1 -p "Press Enter or A to confirm deletion; any other key keeps it: " del_data < /dev/tty
        echo
        if [[ -z "$del_data" || "$del_data" =~ [Aa] ]]; then
            rm -rf "$USER_DATA_DIR" && echo -e "${GREEN}✓ User data deleted${NC}"
        else
            echo -e "${YELLOW}Kept user data ($USER_DATA_DIR).${NC}"
        fi
    fi

    # ---------- 结果确认 ----------
    echo ""
    if pacman -Q todesk-bin &>/dev/null || pacman -Q todesk &>/dev/null || [ -d /opt/todesk ]; then
        echo -e "${RED}✗ ToDesk still detected after uninstall; check output above.${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ ToDesk uninstall complete${NC}"
}

update_installed_apps() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Update all apps ════════════════${NC}"
    echo ""

    # 为什么不用 flatpak update 一条命令搞定：
    # 先查更新这一步如果混在 update 里，用户要等整个流程开始才知道有没有更新。
    # 所以分开做：用 remote-ls 查更新（只刷新 summary，走镜像站，快）先列出来，
    # 再按需执行 update。
    # 另：flatpak update 默认并不刷新 appstream 元数据，只有显式加 --appstream 才会，
    # 所以这里无需额外跳过，也不会卡在「更新 appstream 数据」。

    # FIX-SOFTWARE: distinguish "no updates / query failed / timeout"; empty output is not "all up to date".
    echo -e "${CYAN}Checking for available updates...${NC}"
    local updates="" check_rc=0 check_err="" check_tmp
    check_tmp="$(mktemp "$TEMP_DIR/flatpak_check.XXXXXX" 2>/dev/null)"
    updates=$(timeout 120 flatpak remote-ls --updates 2>"$check_tmp") || check_rc=$?
    [ -f "$check_tmp" ] && check_err="$(cat "$check_tmp")"
    rm -f "$check_tmp"

    if [ $check_rc -ne 0 ]; then
        if [ $check_rc -eq 124 ] || [ $check_rc -eq 137 ]; then
            echo -e "${RED}✗ Update query timed out or was killed (rc=$check_rc); not treated as 'no updates'.${NC}"
        else
            echo -e "${RED}✗ Update query failed (rc=$check_rc).${NC}"
            [ -n "$check_err" ] && echo -e "${YELLOW}  flatpak stderr: $(echo "$check_err" | head -3 | tr '\n' ' ')${NC}"
        fi
        echo -e "${YELLOW}  Check your network and retry, or pick another mirror under Switch Software Source.${NC}"
        return 1
    fi

    if [ -z "$updates" ]; then
        echo ""
        echo -e "${GREEN}✓ Query succeeded with no pending updates: all installed apps are up to date.${NC}"
        return 0
    fi

    echo ""
    echo -e "${CYAN}These apps can be updated:${NC}"
    printf '%s\n' "$updates" | sed 's/^/  · /'
    echo ""

    # FIX-PROGRESS: show percentages and download speed.
    # --noninteractive disables progress output, so drop it and set
    # FLATPAK_TTY_PROGRESS=1 so flatpak/ostree emits
    # "Receiving objects: NN% (...) X MB/s". The output goes through
    # fp_progress_filter, which turns \r redraws into plain lines and strips ANSI
    # sequences and cursor-position replies, keeping progress/speed without the
    # old garbage characters.
    echo -e "${CYAN}Starting update (large packages may be slow; please wait)...${NC}"
    echo -e "${CYAN}Download percentage and speed are shown live below${NC}"
    echo ""
    local rc=0
    # Save flatpak's real exit code to a file: in a pipeline $? would be the filter's.
    local _fp_status="${TEMP_DIR}/fp_update_status.$$"
    ( FLATPAK_TTY_PROGRESS=1 timeout 1200 flatpak update -y < /dev/null 2>&1; echo $? > "$_fp_status" ) \
        | fp_progress_filter
    if [ -f "$_fp_status" ]; then
        rc=$(cat "$_fp_status" 2>/dev/null || echo 1)
        rm -f "$_fp_status"
    else
        rc=1
    fi

    echo ""
    # FIX-SOFTWARE: rc=137/124 are timeouts/kills, reported separately from generic failure.
    if [ $rc -eq 124 ] || [ $rc -eq 137 ]; then
        echo -e "${RED}✗ Update timed out or was killed (rc=$rc); aborted, not reported as done.${NC}"
        echo -e "${YELLOW}  Partially downloaded data is kept; retry later or switch mirrors first.${NC}"
        return 1
    elif [ $rc -ne 0 ]; then
        echo -e "${RED}✗ Update failed (rc=$rc); check output above.${NC}"
        return 1
    fi

    # Re-check: inspect returncode and stderr; a failed recheck must not report "all done".
    local left="" left_rc=0 left_err="" left_tmp
    left_tmp="$(mktemp "$TEMP_DIR/flatpak_recheck.XXXXXX" 2>/dev/null)"
    left=$(timeout 30 flatpak remote-ls --updates --cached 2>"$left_tmp") || left_rc=$?
    [ -f "$left_tmp" ] && left_err="$(cat "$left_tmp")"
    rm -f "$left_tmp"
    if [ $left_rc -ne 0 ]; then
        echo -e "${RED}✗ Recheck failed (rc=$left_rc); cannot confirm updates completed.${NC}"
        [ -n "$left_err" ] && echo -e "${YELLOW}  flatpak stderr: $(echo "$left_err" | head -3 | tr '\n' ' ')${NC}"
        return 1
    fi
    if [ -z "$left" ]; then
        echo -e "${GREEN}✓ All apps updated${NC}"
        return 0
    fi
    echo -e "${YELLOW}⚠ Update command finished, but these apps still show updates:${NC}"
    printf '%s\n' "$left" | sed 's/^/  · /'
    echo -e "${YELLOW}  It may have been skipped (e.g. still running) or need a reboot.${NC}"
    return 1
}

install_yellow_duck_software() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Install Yellow Duck software ════════════════${NC}"
    echo ""
    # FIX-SOFTWARE: every failure returns 1 (bare return used to report success to the GUI).
    local LOSS_DIR="$HOME/.local/share/Steam/steamapps/common/Lossless Scaling"
    local STEAM_COMMON="$HOME/.local/share/Steam/steamapps/common"
    if [[ -d "$LOSS_DIR" ]]; then
        echo -e "${CYAN}Yellow Duck software already installed.${NC}"
        echo "   Install directory: $LOSS_DIR"
        echo -e "${RED}Warning: the whole directory will be deleted; it may contain user data (irreversible).${NC}"
        if ! confirm_action; then
            echo -e "${GREEN}Cancelled; nothing was deleted.${NC}"
            return 0
        fi
        if [ -L "$LOSS_DIR" ]; then
            echo -e "${RED}✗ Target is a symlink; refusing to delete, check manually.${NC}"
            return 1
        fi
        echo "Starting Yellow Duck uninstall..."
        if ! sudo rm -rf "$LOSS_DIR"; then
            echo -e "${RED}❌ Uninstall failed; check permissions.${NC}"
            return 1
        fi
        if [ -d "$LOSS_DIR" ]; then
            echo -e "${RED}❌ Directory still exists; uninstall did not take effect.${NC}"
            return 1
        fi
        echo -e "${GREEN}✅ Yellow Duck software uninstalled.${NC}"
        echo "To reinstall, run this feature again."
        return 0
    fi

    echo -e "${CYAN}Yellow Duck software not found; downloading split archives from Gitee...${NC}"
    if [ ! -d "$STEAM_COMMON" ]; then
        echo -e "${RED}✗ Target directory missing: $STEAM_COMMON; aborted.${NC}"
        return 1
    fi
    local DOWNLOAD_DIR
    DOWNLOAD_DIR="$(mktemp -d /tmp/lossless_scaling_download.XXXXXXXX 2>/dev/null)" || {
        echo -e "${RED}✗ Cannot create a temp dir.${NC}"; return 1; }
    cd "$DOWNLOAD_DIR" || { rm -rf "$DOWNLOAD_DIR"; return 1; }

    local BASE_URL="https://gitee.com/Zhucy2100/app-backup/raw/master/Lossless%20Scaling/Lossless%20Scaling.zip"
    local failed=0
    for i in 001 002 003 004 005 006 007; do
        echo "Downloading Lossless Scaling.zip.${i} ..."
        if ! curl -L --fail --connect-timeout 15 --max-time 180 -o "Lossless Scaling.zip.${i}" "${BASE_URL}.${i}"; then
            echo -e "${RED}Failed to download Lossless Scaling.zip.${i}.${NC}"
            failed=1
            break
        fi
        if [ ! -s "Lossless Scaling.zip.${i}" ]; then
            echo -e "${RED}Part Lossless Scaling.zip.${i} is empty (likely an error page).${NC}"
            failed=1
            break
        fi
    done

    if [ $failed -ne 0 ]; then
        echo -e "${RED}Download failed; check your network.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    echo "Merging split archives and extracting..."
    if ! cat "Lossless Scaling.zip".* > Lossless-Scaling-Combined.zip; then
        echo -e "${RED}✗ Failed to merge split parts.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    # Reject ../ or absolute paths before extracting into Steam common.
    if ! fs_archive_safe Lossless-Scaling-Combined.zip zip; then
        echo -e "${RED}✗ Archive contains ../ or absolute paths; refusing to extract (path traversal), aborted.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if ! unzip -o Lossless-Scaling-Combined.zip -d "$STEAM_COMMON/"; then
        echo -e "${RED}Extraction failed.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if [ ! -d "$LOSS_DIR" ]; then
        echo -e "${RED}✗ Target dir $LOSS_DIR not found after extract; install failed.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if ! sudo chown -R "${CURRENT_USER}:${CURRENT_GROUP}" "$LOSS_DIR"; then
        echo -e "${RED}✗ chown failed; install not complete.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
    echo -e "${GREEN}✅ Yellow Duck software installed!${NC}"
    return 0
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
    print('Icon extraction failed: %s' % e, file=sys.stderr)
    sys.exit(1)
PYEOF

}

install_third_party_platform() {
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}═══════════ Install third-party game platforms ═══════════${NC}"
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

        echo "Current status:"
        if $ubisoft_installed; then
            echo -e "  ${GREEN}✓ Ubisoft platform installed${NC}"
        else
            echo -e "  ${YELLOW}✗ Ubisoft platform not installed${NC}"
        fi
        if $epic_installed; then
            echo -e "  ${GREEN}✓ Epic platform installed${NC}"
        else
            echo -e "  ${YELLOW}✗ Epic platform not installed${NC}"
        fi
        if $battle_installed; then
            echo -e "  ${GREEN}✓ Battle.net platform installed${NC}"
        else
            echo -e "  ${YELLOW}✗ Battle.net platform not installed${NC}"
        fi
        echo ""

        echo "Choose platforms to install:"
        echo "  1) Install Ubisoft platform"
        echo "  2) Install Epic platform"
        echo "  3) Install Battle.net platform"
        read -p "Enter [1-3]: " choice < /dev/tty
        case $choice in
            1) install_ubisoft; break ;;
            2) install_epic; break ;;
            3) install_battle_net; break ;;
            *) echo -e "${RED}Invalid option; try again${NC}"; sleep 0.5 ;;
        esac
    done
}

install_ubisoft() {
    local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
    if [ -d "$UBISOFT_DIR" ]; then
        echo -e "${GREEN}✓ Ubisoft platform already installed; nothing to do.${NC}"
        return 0
    fi

    # FIX-SOFTWARE: --fail/timeouts + PE header check, never hand an HTML page to Proton.
    echo -e "${CYAN}Downloading Ubisoft installer...${NC}"
    cd "$HOME" || return
    rm -f UbisoftConnectInstaller.exe
    if ! curl -# -L --fail --connect-timeout 15 --max-time 300 -o UbisoftConnectInstaller.exe "https://ubistatic3-a.akamaihd.net/orbit/launcher_installer/UbisoftConnectInstaller.exe"; then
        echo -e "${RED}Download failed; check your network.${NC}"
        rm -f UbisoftConnectInstaller.exe
        return 1
    fi
    if ! fs_verify_installer UbisoftConnectInstaller.exe mz; then
        echo -e "${RED}✗ Downloaded file is not a valid PE installer (too small or an HTML error page); aborted.${NC}"
        rm -f UbisoftConnectInstaller.exe
        return 1
    fi

    echo -e "${CYAN}Quiet-installing via Proton Experimental...${NC}"
    mkdir -p "$HOME/Applications/third-party-game-platform"

    export STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform"
    export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"

    local PROTON_BIN="$HOME/.steam/root/steamapps/common/Proton - Experimental/proton"
    if [ ! -x "$PROTON_BIN" ]; then
        echo -e "${RED}✗ Proton Experimental compatibility tool not found.${NC}"
        echo "   Please install Proton Experimental from Steam Library → Tools, then retry."
        return 1
    fi
    # FIX-SOFTWARE: check Proton's exit code; no more "waiting" after a failed run.
    if ! "$PROTON_BIN" waitforexitandrun \
        "$HOME/UbisoftConnectInstaller.exe" /S; then
        echo -e "${RED}✗ Proton failed to run the installer (non-zero exit); check the Proton environment or logs.${NC}"
        return 1
    fi

    echo -e "${CYAN}Waiting for install to finish...${NC}"
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

    local EXE_PATH="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/UbisoftConnect.exe"
    # FIX-SOFTWARE: verify the target exe exists, not just the directory.
    if [ -d "$UBISOFT_DIR" ] && [ -f "$EXE_PATH" ]; then
        echo -e "${GREEN}✓ Ubisoft platform installed successfully!${NC}"

        echo -e "${CYAN}Adding to Steam library...${NC}"
        # FIX-SOFTWARE: check the tool exists first, so a missing command is not a false "added"
        if ! command -v steamos-add-to-steam >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠ steamos-add-to-steam not found; skipping auto-add, please add the exe manually.${NC}"
        else
            steamos-add-to-steam "$EXE_PATH"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Steam shortcut added.${NC}"
            echo -e "${YELLOW}Please set this shortcut's compatibility tool to Proton Experimental in your Steam library.${NC}"
            echo -e "${YELLOW}Or launch it from the desktop shortcut.${NC}"
        else
            echo -e "${YELLOW}⚠️ Failed to add to Steam automatically; add the exe manually.${NC}"
        fi
        fi  # FIX-SOFTWARE: add_to_steam guard end

        local ICON_PATH=""
        echo -e "${CYAN}Extracting icon from exe...${NC}"
        ICON_PATH=$(extract_exe_icon "$EXE_PATH")
        if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
            echo -e "${GREEN}✓ Icon extracted: $ICON_PATH${NC}"
        else
            ICON_PATH="applications-games"
            echo -e "${YELLOW}⚠️ Icon extraction failed; using the system game icon.${NC}"
        fi

        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        local DESKTOP_FILE="$DESKTOP_DIR/Ubisoft Connect.desktop"
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
        echo -e "${GREEN}✓ Desktop shortcut created: ~/Desktop/Ubisoft Connect.desktop${NC}"

        rm -f "$HOME/UbisoftConnectInstaller.exe"
    else
        echo -e "${RED}✗ Install failed (timeout); check the Proton environment or logs.${NC}"
        echo -e "${YELLOW}Installer kept at $HOME/UbisoftConnectInstaller.exe; you can run it manually.${NC}"
    fi
}

install_epic() {
    local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
    if [ -d "$EPIC_DIR" ]; then
        echo -e "${GREEN}✓ Epic platform already installed; nothing to do.${NC}"
        return 0
    fi

    # FIX-SOFTWARE: --fail/timeouts + MSI(OLE2) header check, never hand HTML to Proton.
    echo -e "${CYAN}Downloading Epic installer...${NC}"
    cd "$HOME" || return
    rm -f EpicGamesLauncherInstaller.msi
    if ! wget --connect-timeout=15 --timeout=300 --tries=1 -O EpicGamesLauncherInstaller.msi "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi"; then
        echo -e "${RED}Download failed; check your network.${NC}"
        rm -f EpicGamesLauncherInstaller.msi
        return 1
    fi
    if ! fs_verify_installer EpicGamesLauncherInstaller.msi msi; then
        echo -e "${RED}✗ Downloaded file is not a valid MSI installer (too small or an HTML error page); aborted.${NC}"
        rm -f EpicGamesLauncherInstaller.msi
        return 1
    fi

    echo -e "${CYAN}Quiet-installing via Proton Experimental...${NC}"
    mkdir -p "$HOME/Applications/third-party-game-platform"

    export STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform"
    export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"

    MSI_LOG="/tmp/epic_install_msi_$(date +%Y%m%d_%H%M%S).log"
    echo "Install log will be saved to: $MSI_LOG"

    local PROTON_BIN="$HOME/.steam/root/steamapps/common/Proton - Experimental/proton"
    if [ ! -x "$PROTON_BIN" ]; then
        echo -e "${RED}✗ Proton Experimental compatibility tool not found.${NC}"
        echo "   Please install Proton Experimental from Steam Library → Tools, then retry."
        return 1
    fi
    # FIX-SOFTWARE: run Epic MSI via explicit msiexec /i ... /quiet through Proton, check rc.
    if ! "$PROTON_BIN" waitforexitandrun \
        msiexec /i "Z:\\home\\deck\\EpicGamesLauncherInstaller.msi" /quiet /log "$MSI_LOG"; then
        echo -e "${RED}✗ Proton failed to run msiexec (non-zero exit); check log: ${MSI_LOG}${NC}"
        return 1
    fi

    echo -e "${CYAN}Waiting for install to finish...${NC}"
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

    local EXE_PATH="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games/Launcher/Portal/Binaries/Win64/EpicGamesLauncher.exe"
    # FIX-SOFTWARE: verify the target exe exists, not just the directory.
    if [ -d "$EPIC_DIR" ] && [ -f "$EXE_PATH" ]; then
        echo -e "${GREEN}✓ Epic platform installed successfully!${NC}"

        echo -e "${CYAN}Adding to Steam library...${NC}"
        # FIX-SOFTWARE: check the tool exists first, so a missing command is not a false "added"
        if ! command -v steamos-add-to-steam >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠ steamos-add-to-steam not found; skipping auto-add, please add the exe manually.${NC}"
        else
            steamos-add-to-steam "$EXE_PATH"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Steam shortcut added.${NC}"
            echo -e "${YELLOW}Please set this shortcut's compatibility tool to Proton Experimental in your Steam library.${NC}"
            echo -e "${YELLOW}Or launch it from the desktop shortcut.${NC}"
        else
            echo -e "${YELLOW}⚠️ Failed to add to Steam automatically; add the exe manually.${NC}"
        fi
        fi  # FIX-SOFTWARE: add_to_steam guard end

        local ICON_PATH=""
        echo -e "${CYAN}Extracting icon from exe...${NC}"
        ICON_PATH=$(extract_exe_icon "$EXE_PATH")
        if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
            echo -e "${GREEN}✓ Icon extracted: $ICON_PATH${NC}"
        else
            ICON_PATH="applications-games"
            echo -e "${YELLOW}⚠️ Icon extraction failed; using the system game icon.${NC}"
        fi

        local DESKTOP_DIR
        DESKTOP_DIR="$(fs_desktop_dir)"
        local DESKTOP_FILE="$DESKTOP_DIR/Epic Games Launcher.desktop"
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
        echo -e "${GREEN}✓ Desktop shortcut created: ~/Desktop/Epic Games Launcher.desktop${NC}"

        rm -f "$HOME/EpicGamesLauncherInstaller.msi"
        rm -f "$MSI_LOG"
    else
        echo -e "${RED}✗ Install failed (timeout); check log: ${MSI_LOG}${NC}"
        echo -e "${YELLOW}Installer kept at $HOME/EpicGamesLauncherInstaller.msi; you can run it manually.${NC}"
    fi
}

install_battle_net() {
    local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
    if [ -d "$BATTLE_DIR" ]; then
        echo -e "${GREEN}✓ Battle.net platform already installed; nothing to do.${NC}"
        return 0
    fi

    echo -e "${CYAN}Downloading Battle.net backup parts from Gitee Release...${NC}"
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
        echo "Downloading Battle.net_backup.part_${part} ..."
        # FIX-SOFTWARE: connect/max-time timeouts on this key download.
        if ! curl -L --fail --connect-timeout 15 --max-time 180 --retry 2 \
             -H "User-Agent: ${CURL_UA}" \
             -H "Referer: ${CURL_REFERER}" \
             -o "Battle.net_backup.part_${part}" "${BASE_URL}_${part}"; then
            echo -e "${RED}Failed to download Battle.net_backup.part_${part}.${NC}"
            failed=1
            break
        fi
    done

    if [ $failed -ne 0 ]; then
        echo -e "${RED}Download failed; check your network.${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    echo "Merging split archives..."
    cat Battle.net_backup.part_* > Battle.net_backup.tar.xz

    echo -e "${CYAN}Extracting to the target directory...${NC}"
    local BN_TARGET="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)"
    if ! mkdir -p "$BN_TARGET"; then
        echo -e "${RED}✗ Failed to create the target dir.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    # Reject ../ or absolute paths before extracting.
    if ! fs_archive_safe Battle.net_backup.tar.xz tar; then
        echo -e "${RED}✗ Archive contains ../ or absolute paths; refusing to extract (path traversal), aborted.${NC}"
        cd "$HOME" 2>/dev/null; rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
    if ! tar -xJf Battle.net_backup.tar.xz -C "$BN_TARGET/"; then
        echo -e "${RED}Extraction failed.${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    local EXE_PATH="$BATTLE_DIR/Battle.net Launcher.exe"
    if [ ! -f "$EXE_PATH" ]; then
        echo -e "${RED}Error: Battle.net Launcher.exe not found after extract; install failed.${NC}"
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    echo -e "${CYAN}Adding to Steam library...${NC}"
    if ! command -v steamos-add-to-steam >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ steamos-add-to-steam not found; skipping auto-add, please add the exe manually.${NC}"
    else
        steamos-add-to-steam "$EXE_PATH"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Steam shortcut added.${NC}"
        echo -e "${YELLOW}Please set this shortcut's compatibility tool to Proton Experimental in your Steam library.${NC}"
        echo -e "${YELLOW}Or launch it from the desktop shortcut.${NC}"
    else
        echo -e "${YELLOW}⚠️ Failed to add to Steam automatically; add the exe manually.${NC}"
    fi
    fi  # FIX-SOFTWARE: bn add_to_steam guard end

    local ICON_PATH=""
    echo -e "${CYAN}Extracting icon from exe...${NC}"
    ICON_PATH=$(extract_exe_icon "$EXE_PATH")
    if [ -n "$ICON_PATH" ] && [ -s "$ICON_PATH" ]; then
        echo -e "${GREEN}✓ Icon extracted: $ICON_PATH${NC}"
    else
        ICON_PATH="applications-games"
        echo -e "${YELLOW}⚠️ Icon extraction failed; using the system game icon.${NC}"
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
        echo -e "${GREEN}✓ Desktop shortcut created: ~/Desktop/Battle.net.desktop${NC}"

    rm -rf "$DOWNLOAD_DIR"
    echo -e "${GREEN}✅ Battle.net platform installed!${NC}"
}

uninstall_third_party_platform() {
    # FIX-SOFTWARE: add a cancel/back option; /dev/tty EOF no longer loops forever.
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}═══════════ Uninstall third-party game platforms ═══════════${NC}"
        echo ""
        local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
        local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
        local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
        local ubisoft_installed=false epic_installed=false battle_installed=false
        [ -d "$UBISOFT_DIR" ] && ubisoft_installed=true
        [ -d "$EPIC_DIR" ] && epic_installed=true
        [ -d "$BATTLE_DIR" ] && battle_installed=true

        if ! $ubisoft_installed && ! $epic_installed && ! $battle_installed; then
            echo -e "${YELLOW}No third-party game platforms installed by this tool were found.${NC}"
            sleep 2
            return 0
        fi

        echo "Currently installed platforms:"
        $ubisoft_installed && echo -e "  ${GREEN}✓ Ubisoft platform${NC}"
        $epic_installed && echo -e "  ${GREEN}✓ Epic platform${NC}"
        $battle_installed && echo -e "  ${GREEN}✓ Battle.net platform${NC}"
        echo ""
        echo "Choose platforms to uninstall:"
        echo "  1) Uninstall Ubisoft platform"
        echo "  2) Uninstall Epic platform"
        echo "  3) Uninstall Battle.net platform"
        echo "  0) Cancel / back (do not uninstall)"
        local choice=""
        if ! read -r -p "Enter [0-3] (Enter=cancel): " choice < /dev/tty; then
            echo -e "${GREEN}Cancelled; no changes made.${NC}"
            return 0
        fi
        case "$choice" in
            1) uninstall_ubisoft; return $? ;;
            2) uninstall_epic; return $? ;;
            3) uninstall_battle_net; return $? ;;
            ""|0) echo -e "${GREEN}Cancelled; no changes made.${NC}"; return 0 ;;
            *) echo -e "${RED}Invalid option; try again${NC}"; sleep 0.5 ;;
        esac
    done
}

uninstall_ubisoft() {
    # FIX-SOFTWARE: list paths + confirm + symlink check + uninstaller failure is not success.
    local UBISOFT_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Ubisoft"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local DESKTOP_FILE="$DESKTOP_DIR/Ubisoft Connect.desktop"
    if [ ! -d "$UBISOFT_DIR" ]; then
        echo -e "${YELLOW}Ubisoft platform not detected; nothing to uninstall.${NC}"
        return 0
    fi

    echo -e "${CYAN}The following paths will be deleted:${NC}"
    local p
    for p in "$@"; do
        [ -e "$p" ] || [ -L "$p" ] || continue
        if [ -L "$p" ]; then
            echo -e "${RED}  ✗ $p is a symlink; refusing to delete, check manually.${NC}"
            return 1
        fi
        echo -e "${YELLOW}  · $p${NC}"
    done
    echo -e "${RED}Warning: these directories may contain installed games, saves and user data. This is irreversible!${NC}"
    echo -e "${YELLOW}Make sure the platform/game processes are not running.${NC}"
    if pgrep -f 'third-party-game-platform' >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ A platform/game process may still be running; consider quitting it first.${NC}"
    fi
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}Cancelled; nothing was deleted.${NC}"
        return 0
    fi

    local uninstaller="$UBISOFT_DIR/Ubisoft Game Launcher/Uninstall.exe"
    local uninstaller_ok=false
    if [ -f "$uninstaller" ]; then
        echo -e "${CYAN}Running the official Ubisoft uninstaller...${NC}"
        export STEAM_COMPAT_DATA_PATH="$HOME/Applications/third-party-game-platform"
        export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"
        local PROTON_BIN="$HOME/.steam/root/steamapps/common/Proton - Experimental/proton"
        if [ -x "$PROTON_BIN" ] && "$PROTON_BIN" waitforexitandrun "$uninstaller" /S; then
            uninstaller_ok=true
            echo -e "${GREEN}✓ Official uninstaller finished.${NC}"
        else
            echo -e "${YELLOW}⚠ Proton missing or the official uninstaller failed; only the directory will be removed (not a full success).${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Official uninstaller not found; only the directory will be removed.${NC}"
    fi

    local fail=0
    if ! rm -rf "$UBISOFT_DIR"; then
        echo -e "${RED}✗ Failed to delete: $UBISOFT_DIR${NC}"
        fail=1
    elif [ -d "$UBISOFT_DIR" ]; then
        echo -e "${RED}✗ Directory still exists: $UBISOFT_DIR${NC}"
        fail=1
    else
        echo -e "${GREEN}✓ Ubisoft directory deleted${NC}"
    fi

    # Only clean the shortcut and report success when the uninstaller AND rm both succeeded
    if [ "$fail" -eq 0 ] && $uninstaller_ok; then
        if [ -f "$DESKTOP_FILE" ]; then
            if rm -f "$DESKTOP_FILE"; then
                echo -e "${GREEN}✓ Desktop shortcut deleted${NC}"
            else
                echo -e "${RED}✗ Failed to delete the desktop shortcut${NC}"
                fail=1
            fi
        fi
    elif [ "$fail" -eq 0 ]; then
        echo -e "${RED}✗ Official uninstaller did not succeed; desktop shortcut kept, verify manually before removing.${NC}"
        fail=1
    fi

    echo ""
    echo -e "${YELLOW}Please manually remove the corresponding non-Steam shortcut from your Steam library (right-click → Manage → Remove non-Steam game).${NC}"
    [ "$fail" -eq 0 ] || return 1
    echo -e "${GREEN}✓ Ubisoft platform uninstalled.${NC}"
    return 0
}

uninstall_epic() {
    # FIX-SOFTWARE: confirm + symlink check + rm failure returns 1.
    local EPIC_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files/Epic Games"
    local EPIC_DIR_X86="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Epic Games"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local DESKTOP_FILE="$DESKTOP_DIR/Epic Games Launcher.desktop"
    if [ ! -d "$EPIC_DIR" ] && [ ! -d "$EPIC_DIR_X86" ]; then
        echo -e "${YELLOW}Epic platform not detected; nothing to uninstall.${NC}"
        return 0
    fi

    echo -e "${CYAN}The following paths will be deleted:${NC}"
    local p
    for p in "$@"; do
        [ -e "$p" ] || [ -L "$p" ] || continue
        if [ -L "$p" ]; then
            echo -e "${RED}  ✗ $p is a symlink; refusing to delete, check manually.${NC}"
            return 1
        fi
        echo -e "${YELLOW}  · $p${NC}"
    done
    echo -e "${RED}Warning: these directories may contain installed games, saves and user data. This is irreversible!${NC}"
    echo -e "${YELLOW}Make sure the platform/game processes are not running.${NC}"
    if pgrep -f 'third-party-game-platform' >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ A platform/game process may still be running; consider quitting it first.${NC}"
    fi
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}Cancelled; nothing was deleted.${NC}"
        return 0
    fi

    local fail=0 d
    for d in "$EPIC_DIR" "$EPIC_DIR_X86"; do
        [ -d "$d" ] || continue
        if ! rm -rf "$d"; then
            echo -e "${RED}✗ Failed to delete: $d${NC}"
            fail=1
        elif [ -d "$d" ]; then
            echo -e "${RED}✗ Directory still exists: $d${NC}"
            fail=1
        else
            echo -e "${GREEN}✓ Deleted: $d${NC}"
        fi
    done
    if [ -f "$DESKTOP_FILE" ]; then
        if rm -f "$DESKTOP_FILE"; then
            echo -e "${GREEN}✓ Desktop shortcut deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete the desktop shortcut${NC}"
            fail=1
        fi
    fi
    echo ""
    echo -e "${YELLOW}Please manually remove the corresponding non-Steam shortcut from your Steam library.${NC}"
    [ "$fail" -eq 0 ] || return 1
    echo -e "${GREEN}✓ Epic platform uninstalled.${NC}"
    return 0
}

uninstall_battle_net() {
    # FIX-SOFTWARE: confirm + symlink check + rm failure returns 1.
    local BATTLE_DIR="$HOME/Applications/third-party-game-platform/pfx/drive_c/Program Files (x86)/Battle.net"
    local DESKTOP_DIR
    DESKTOP_DIR="$(fs_desktop_dir)"
    local DESKTOP_FILE="$DESKTOP_DIR/Battle.net.desktop"
    if [ ! -d "$BATTLE_DIR" ]; then
        echo -e "${YELLOW}Battle.net platform not detected; nothing to uninstall.${NC}"
        return 0
    fi

    echo -e "${CYAN}The following paths will be deleted:${NC}"
    local p
    for p in "$@"; do
        [ -e "$p" ] || [ -L "$p" ] || continue
        if [ -L "$p" ]; then
            echo -e "${RED}  ✗ $p is a symlink; refusing to delete, check manually.${NC}"
            return 1
        fi
        echo -e "${YELLOW}  · $p${NC}"
    done
    echo -e "${RED}Warning: these directories may contain installed games, saves and user data. This is irreversible!${NC}"
    echo -e "${YELLOW}Make sure the platform/game processes are not running.${NC}"
    if pgrep -f 'third-party-game-platform' >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ A platform/game process may still be running; consider quitting it first.${NC}"
    fi
    echo ""
    if ! confirm_action; then
        echo -e "${GREEN}Cancelled; nothing was deleted.${NC}"
        return 0
    fi

    local fail=0
    if ! rm -rf "$BATTLE_DIR"; then
        echo -e "${RED}✗ Failed to delete: $BATTLE_DIR${NC}"
        fail=1
    elif [ -d "$BATTLE_DIR" ]; then
        echo -e "${RED}✗ Directory still exists: $BATTLE_DIR${NC}"
        fail=1
    else
        echo -e "${GREEN}✓ Battle.net directory deleted${NC}"
    fi
    if [ -f "$DESKTOP_FILE" ]; then
        if rm -f "$DESKTOP_FILE"; then
            echo -e "${GREEN}✓ Desktop shortcut deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete the desktop shortcut${NC}"
            fail=1
        fi
    fi
    echo ""
    echo -e "${YELLOW}Please manually remove the corresponding non-Steam shortcut from your Steam library.${NC}"
    [ "$fail" -eq 0 ] || return 1
    echo -e "${GREEN}✓ Battle.net platform uninstalled.${NC}"
    return 0
}

if [ -n "${1:-}" ] && declare -f "$1" > /dev/null; then
    "$@"
else
    echo "This script is an embedded library; call a specific function via arguments."
fi
'''

def get_bash_script():
    """Return embedded shell library for the current UI language."""
    return BASH_SCRIPT_EN if get_lang() == 'en' else BASH_SCRIPT_ZH

# Back-compat alias; create_temp_script() uses get_bash_script().
BASH_SCRIPT = BASH_SCRIPT_ZH


# ============================================================================
# Python GUI
# ============================================================================
def create_temp_script(extra_content=''):
    fd, path = tempfile.mkstemp(suffix='.sh')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(get_bash_script())
        if extra_content:
            f.write('\n' + extra_content + '\n')
    os.chmod(path, 0o755)
    atexit.register(lambda: os.path.exists(path) and os.unlink(path))
    return path

class TaskWindow(Gtk.Window):
    def __init__(self, parent, func_key, display_name):
        super().__init__(title=(f"Running Task: {display_name}" if get_lang() == "en" else f"执行任务: {display_name}"))
        # 任务窗是终端窗口，比主窗口小一号；同样跟随屏幕自适应，
        # 避免大屏上终端太小、小屏上又顶到屏幕边缘。
        _task_w, _task_h = compute_window_size(fallback_w=760, fallback_h=520,
                                               min_w=700, min_h=460, scale=0.80)
        self.set_default_size(_task_w, _task_h)
        task_header = Gtk.HeaderBar()
        task_header.set_show_close_button(True)
        task_header.props.title = display_name
        task_header.props.subtitle = t("task_running")
        # HeaderBar 默认只画「关闭」一个按钮，最小化/最大化按钮要自己加
        # （gtk-decoration-layout 只对系统原生装饰生效，对自定义 HeaderBar 无效）
        self._max_btn = Gtk.Button()
        self._max_btn.set_relief(Gtk.ReliefStyle.NONE)
        self._max_btn.set_tooltip_text(t("maximize"))
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
            label = Gtk.Label(label=t("task_external"))
            label.set_margin_top(20)
            label.set_margin_bottom(20)
            vbox.pack_start(label, True, True, 0)
            self.label = label  # external branch
            self.action_btn = Gtk.Button(label=t("close"))
            self.action_btn.connect("clicked", lambda btn: self.destroy())
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_margin_bottom(5)
            button_box.pack_start(Gtk.Label(), True, True, 0)
            button_box.pack_start(self.action_btn, False, False, 0)
            vbox.pack_start(button_box, False, False, 0)
            # 任务仍在运行时关窗给一次明确提示，不再只显示「运行中」永不更新。
            self.connect("delete-event", self._on_external_close)
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
            apply_terminal_theme(self.terminal)
            term_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            term_frame.get_style_context().add_class("card")
            term_frame.get_style_context().add_class("term-card")
            term_frame.set_margin_top(12); term_frame.set_margin_bottom(0); term_frame.set_margin_start(12); term_frame.set_margin_end(12)
            term_frame.pack_start(self.terminal, True, True, 0)
            vbox.pack_start(term_frame, True, True, 0)

            # 终端右键菜单：复制选中 / 复制全部输出 / 粘贴 / 全选
            self.terminal.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            self.terminal.connect("button-press-event", self._on_terminal_button_press)
            # 键盘快捷键：Ctrl+Shift+C 复制、Ctrl+Shift+V 粘贴、Ctrl+Shift+A 全选
            self.terminal.connect("key-press-event", self._on_terminal_key_press)

            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_name("task-toolbar")
            button_box.set_margin_top(0)
            button_box.set_margin_bottom(0)
            button_box.set_margin_start(0)
            button_box.set_margin_end(0)
            self.timer_label = Gtk.Label(label=t("elapsed_zero"))
            self.timer_label.set_name("task-timer")
            button_box.pack_start(self.timer_label, False, False, 0)
            button_box.pack_start(Gtk.Label(), True, True, 0)

            # 复制按钮：有选中内容时复制选中，否则复制全部输出
            self.copy_btn = Gtk.Button(label=t("copy"))
            self.copy_btn.set_tooltip_text(t("copy_tooltip"))
            self.copy_btn.connect("clicked", self.on_copy_clicked)
            button_box.pack_start(self.copy_btn, False, False, 0)

            self.action_btn = Gtk.Button(label=t("cancel"))
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
    def _on_external_close(self, *_a):
        if not getattr(self, "completed", False):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.NONE,
                                    text=t("external_running_close"))
            dlg.add_button(t("ok"), Gtk.ResponseType.OK)
            fix_dialog_size(dlg)
            dlg.run(); dlg.destroy()
        return False  # 继续关窗

    def _on_terminal_button_press(self, widget, event):
        # 右键（button 3）弹菜单
        if event.button == 3:
            return self._show_terminal_menu(widget, event)
        return False

    def on_copy_clicked(self, button):
        """有选中内容时复制选中，否则复制全部输出，并给出短时反馈。"""
        if self._terminal_has_selection():
            ok = self._copy_selection()
            msg = t("copy_sel_ok") if ok else t("copy_fail")
        else:
            ok = self._copy_all_output()
            msg = t("copy_all_ok") if ok else t("copy_empty")
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
                    self.copy_btn.set_label(old if old else t("copy"))
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

        item_copy = Gtk.MenuItem(label=t("copy_sel"))
        item_copy.set_sensitive(has_sel)
        item_copy.connect("activate", lambda *_: self._copy_selection())
        menu.append(item_copy)

        item_copy_all = Gtk.MenuItem(label=t("copy_all"))
        item_copy_all.connect("activate", lambda *_: self._copy_all_output())
        menu.append(item_copy_all)

        item_paste = Gtk.MenuItem(label=t("paste"))
        item_paste.connect("activate", lambda *_: self._paste_to_terminal())
        menu.append(item_paste)

        menu.append(Gtk.SeparatorMenuItem())

        item_sel_all = Gtk.MenuItem(label=t("select_all"))
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

    def run_external(self, func_key):  # with result feedback
        tmp_path = create_temp_script()
        close_prompt = ("Press Enter to close..." if get_lang() == "en" else "按回车键关闭...")
        # 让 read 在脚本被取消时也能结束：用脚本真实退出码作为提示的一部分。
        cmd = (f"bash {tmp_path} {func_key}; __rc=$?; "
               f"echo ''; echo '(exit code: '$__rc')'; "
               f"read -p '{close_prompt}' -n1; exit $__rc")
        argv = terminal_command(find_terminal(), cmd) if find_terminal() else None
        if not argv:
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.NONE,
                                    text=t("no_terminal"))
            dlg.add_button(t("ok"), Gtk.ResponseType.OK)
            dlg.format_secondary_text(t("no_terminal_hint"))
            fix_dialog_size(dlg)
            dlg.run(); dlg.destroy()
            self.completed = True
            self.action_btn.set_sensitive(True)
            try:
                self._task_header.props.subtitle = t("task_failed")
            except Exception:
                pass
            return
        try:
            self._ext_proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL,
                                               stdin=subprocess.DEVNULL,
                                               start_new_session=True)
        except Exception as e:
            self.completed = True
            self.action_btn.set_sensitive(True)
            try:
                self._task_header.props.subtitle = t("start_fail")
            except Exception:
                pass
            print(f"启动外部终端失败: {e}")
            return
        pid = self._ext_proc.pid
        self._ext_pid = pid
        self.label.set_text(t("external_start", pid=pid))
        # 用后台线程 Popen.wait()：终端关掉后把真实返回码反馈到窗口。
        def _wait():
            try:
                rc = self._ext_proc.wait()
            except Exception:
                rc = -1
            GLib.idle_add(self._on_external_done, rc)
        threading.Thread(target=_wait, daemon=True).start()

    def _on_external_done(self, rc):
        self.completed = True
        self.action_btn.set_sensitive(True)
        self.action_btn.set_label(t("task_complete_btn"))
        try:
            if rc == 0:
                self._task_header.props.subtitle = t("external_done_ok")
            else:
                self._task_header.props.subtitle = t("external_done_fail", rc=rc)
        except Exception:
            pass
        return False

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
            self.action_btn.set_label(t("start_fail"))
            self.action_btn.set_sensitive(True)
            return
        self.terminal.connect("child-exited", self.on_child_exited)

    def on_child_exited(self, terminal, status):
        # VTE 传入 waitpid 风格状态；内嵌脚本 EXIT trap 已保留真实退出码。
        success = False
        cancelled = False
        try:
            if os.WIFEXITED(status):
                ec = os.WEXITSTATUS(status)
                # 内嵌 bash 的 INT/TERM trap 用 75 表示「用户取消」，
                # 既不是成功(0)也不是普通失败，必须单独区分显示。
                self._cancel_exit_code = 75
                cancelled = (ec == self._cancel_exit_code)
                success = (ec == 0)
            elif hasattr(os, "WIFSIGNALED") and os.WIFSIGNALED(status):
                cancelled = False
                success = False
            else:
                cancelled = (status == 75)
                success = (status == 0)
        except Exception:
            cancelled = False
            success = (status == 0)
        GLib.idle_add(self.set_completed, success, cancelled)

    def set_completed(self, success=True, cancelled=False):
        self.completed = True
        self.action_btn.set_sensitive(True)
        self.action_btn.set_label(t("task_complete_btn"))
        try:
            if cancelled:
                self._task_header.props.subtitle = t("task_cancelled")
            else:
                self._task_header.props.subtitle = t("task_done") if success else t("task_failed")
        except Exception:
            pass

    def _tick(self):
        if self.completed:
            return False
        elapsed = int(time.time() - self.start_time)
        m, s = divmod(elapsed, 60)
        self.timer_label.set_text(t("elapsed", m=m, s=s))
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
        self.action_btn.set_label(t("cancelling"))
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
        super().__init__(title=t("app_title"))
        self.set_icon_name("input-gamepad-symbolic")
        # 明确作为普通应用窗，避免从更新检查窗切换后被 Plasma 当成无任务栏项的临时窗
        try:
            self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
            self.set_skip_taskbar_hint(False)
            self.set_skip_pager_hint(False)
        except Exception:
            pass
        # 按屏幕可用区域自适应窗口尺寸，避免在掌机 1280x800 上底边溢出、
        # 也避免在大屏上窗口过小。详见 compute_window_size()。
        _win_w, _win_h = compute_window_size()
        self.set_default_size(_win_w, _win_h)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.system_type = self.detect_system_type()
        self.task_window = None
        self._current_page = "func"
        self._current_cat_id = None
        self._nav_before_search = "func"
        self._nav_buttons = {}

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = t("app_title")
        header.props.subtitle = f"v{VERSION}  ·  {system_type_display(self.system_type)}"
        self._header = header
        self.set_titlebar(header)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(t("search_placeholder"))
        self.search_entry.set_width_chars(24)
        self.search_entry.connect("search-changed", self.on_search_changed)
        header.pack_end(self.search_entry)

        self.theme_button = Gtk.MenuButton()
        self.theme_button.set_tooltip_text(t("theme_tooltip"))
        self.theme_button.set_relief(Gtk.ReliefStyle.NONE)
        self._theme_icon = Gtk.Image.new_from_icon_name("weather-clear-night-symbolic",
                                                        Gtk.IconSize.BUTTON)
        self.theme_button.add(self._theme_icon)
        header.pack_end(self.theme_button)
        self._build_theme_menu()

        self.lang_button = Gtk.MenuButton()
        self.lang_button.set_tooltip_text(t("lang_tooltip"))
        self.lang_button.set_relief(Gtk.ReliefStyle.NONE)
        # 顶栏语言入口优先显示文字（中文「语言」/ 英文 Language），一眼能懂
        self._lang_btn_label = Gtk.Label(label=t("lang_button"))
        self.lang_button.add(self._lang_btn_label)
        header.pack_end(self.lang_button)
        self._build_lang_menu()

        self.icon_map = build_icon_map()
        self.category_tree = build_category_tree()
        self.category_icons = {}
        for cat_id, title_key, _desc_key, icon_file in category_meta():
            pix = load_icon_pixbuf(icon_file, 28) if icon_file else None
            self.category_icons[cat_id] = pix
            self.category_icons[t(title_key)] = pix

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        body.set_vexpand(True)
        main_vbox.pack_start(body, True, True, 0)

        # ---- Left category rail ----
        rail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        rail.set_name("cat-rail")
        rail.set_size_request(248, -1)
        rail.set_hexpand(False)
        rail.set_vexpand(True)

        sidebar_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        sidebar_header.set_name("sidebar-header")
        sidebar_icon = Gtk.Image.new_from_icon_name("input-gamepad-symbolic", Gtk.IconSize.BUTTON)
        self.sidebar_title = Gtk.Label(label=t("cat_sidebar"))
        self.sidebar_title.set_halign(Gtk.Align.START)
        sidebar_header.pack_start(sidebar_icon, False, False, 0)
        sidebar_header.pack_start(self.sidebar_title, False, False, 0)
        rail.pack_start(sidebar_header, False, False, 0)

        nav_scroll = Gtk.ScrolledWindow()
        nav_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        nav_scroll.set_vexpand(True)
        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.nav_box.set_valign(Gtk.Align.START)
        nav_scroll.add(self.nav_box)
        rail.pack_start(nav_scroll, True, True, 0)
        body.pack_start(rail, False, False, 0)

        # ---- Right content stack ----
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(140)
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)
        self.stack.set_name("content-area")
        body.pack_start(self.stack, True, True, 0)

        # Detail / function page (no back button)
        cat_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        cat_page.get_style_context().add_class("page-shell")
        cat_page.set_name("detail-panel")
        cat_page.set_margin_top(16); cat_page.set_margin_bottom(16)
        cat_page.set_margin_start(20); cat_page.set_margin_end(12)
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_box.set_halign(Gtk.Align.START)
        self.title_icon = Gtk.Image(); self.title_icon.set_visible(False)
        title_box.pack_start(self.title_icon, False, False, 0)
        self.category_title = Gtk.Label(); self.category_title.set_name("page-title")
        self.category_title.set_halign(Gtk.Align.START)
        title_box.pack_start(self.category_title, False, False, 0)
        cat_page.pack_start(title_box, False, False, 0)

        self.func_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.func_list_box.set_valign(Gtk.Align.START)
        self.func_list_box.set_margin_end(8)
        func_scroll = Gtk.ScrolledWindow()
        func_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        func_scroll.set_vexpand(True)
        try:
            func_scroll.set_overlay_scrolling(False)
        except Exception:
            pass
        # Viewport child with right padding so chevrons never sit under the scrollbar
        func_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        func_inner.set_margin_end(20)
        func_inner.set_margin_start(0)
        func_inner.pack_start(self.func_list_box, False, False, 0)
        func_scroll.add(func_inner)
        cat_page.pack_start(func_scroll, True, True, 0)
        self.stack.add_named(cat_page, "func")
        # keep dummy back_btn for language refresh compatibility
        self.back_btn = Gtk.Button(label=t("back_home"))

        # About (no back)
        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        about_box.get_style_context().add_class("page-shell")
        about_box.set_margin_top(16); about_box.set_margin_bottom(16)
        about_box.set_margin_start(20); about_box.set_margin_end(20)
        self.about_title = Gtk.Label()
        self.about_title.set_name("page-title")
        self.about_title.set_markup(f"<span size='large'><b>{t('about_title')}</b></span>")
        self.about_title.set_halign(Gtk.Align.START)
        about_box.pack_start(self.about_title, False, False, 0)
        self.about_textview = Gtk.TextView()
        self.about_textview.set_editable(False)
        self.about_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.about_textview.set_left_margin(18); self.about_textview.set_right_margin(18)
        self.about_textview.set_top_margin(16); self.about_textview.set_bottom_margin(16)
        self.about_textview.get_style_context().add_class("card")
        self.about_textview.get_buffer().set_text(about_body_text())
        scrolled_about = Gtk.ScrolledWindow()
        scrolled_about.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_about.set_vexpand(True)
        scrolled_about.add(self.about_textview)
        about_box.pack_start(scrolled_about, True, True, 0)
        self.stack.add_named(about_box, "about")
        self.about_back_btn = Gtk.Button(label=t("back_home"))

        # Changelog (no back)
        changelog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        changelog_box.get_style_context().add_class("page-shell")
        changelog_box.set_margin_top(16); changelog_box.set_margin_bottom(16)
        changelog_box.set_margin_start(20); changelog_box.set_margin_end(20)
        self.changelog_title = Gtk.Label()
        self.changelog_title.set_name("page-title")
        self.changelog_title.set_markup(f"<span size='large'><b>{t('cat_changelog')}</b></span>")
        self.changelog_title.set_halign(Gtk.Align.START)
        changelog_box.pack_start(self.changelog_title, False, False, 0)
        self.changelog_textview = Gtk.TextView()
        self.changelog_textview.set_editable(False)
        self.changelog_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.changelog_textview.set_cursor_visible(False)
        self.changelog_textview.set_left_margin(18); self.changelog_textview.set_right_margin(18)
        self.changelog_textview.set_top_margin(16); self.changelog_textview.set_bottom_margin(16)
        self.changelog_textview.get_style_context().add_class("card")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b'textview { font: 10pt Monospace; }')
        self.changelog_textview.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        scrolled_changelog = Gtk.ScrolledWindow()
        scrolled_changelog.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_changelog.set_vexpand(True)
        scrolled_changelog.add(self.changelog_textview)
        changelog_box.pack_start(scrolled_changelog, True, True, 0)
        self.changelog_textview.get_buffer().set_text(changelog_body_text())
        self.stack.add_named(changelog_box, "changelog")
        self.changelog_back_btn = Gtk.Button(label=t("back_home"))

        # Search results (clear search via back)
        search_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        search_page.get_style_context().add_class("page-shell")
        search_page.set_margin_top(16); search_page.set_margin_bottom(16)
        search_page.set_margin_start(20); search_page.set_margin_end(20)
        search_head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.search_back_btn = Gtk.Button(label=t("back_home"))
        self.search_back_btn.get_style_context().add_class("back-btn")
        self.search_back_btn.connect("clicked", self.on_search_back)
        search_head.pack_start(self.search_back_btn, False, False, 0)
        self.search_title = Gtk.Label(label="")
        self.search_title.set_name("page-title")
        self.search_title.set_halign(Gtk.Align.START)
        search_head.pack_start(self.search_title, True, True, 0)
        search_page.pack_start(search_head, False, False, 0)
        self.search_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.search_list_box.set_valign(Gtk.Align.START)
        self.search_list_box.set_margin_end(28)
        scrolled_search = Gtk.ScrolledWindow()
        scrolled_search.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_search.set_vexpand(True)
        try:
            scrolled_search.set_overlay_scrolling(False)
        except Exception:
            pass
        scrolled_search.add(self.search_list_box)
        search_page.pack_start(scrolled_search, True, True, 0)
        self.search_store = Gtk.ListStore(str, str, str)
        self.stack.add_named(search_page, "search")

        # Bottom bar (restrained)
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bottom_bar.set_name("bottom-bar")
        self.status_label = Gtk.Label(label="")
        self.status_label.set_name("status-label")
        self.status_label.set_halign(Gtk.Align.START)
        bottom_bar.pack_start(self.status_label, False, False, 0)
        bottom_bar.pack_start(Gtk.Label(), True, True, 0)
        self.help_btn = Gtk.Button(label=t("help"))
        self.help_btn.connect("clicked", self.on_help_clicked)
        bottom_bar.pack_start(self.help_btn, False, False, 0)
        self.quit_btn = Gtk.Button(label=t("quit"))
        self.quit_btn.get_style_context().add_class("destructive-action")
        self.quit_btn.connect("clicked", lambda b: self.destroy())
        bottom_bar.pack_start(self.quit_btn, False, False, 0)
        main_vbox.pack_start(bottom_bar, False, False, 0)

        self.func_map = {}
        self.build_func_map()
        self.rebuild_nav_rail()
        self.update_status()
        # Default: 支持和维护 (about/support)
        self.open_category("support")

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
        for mode in THEME_MODES:
            row = Gtk.Button()
            row.set_relief(Gtk.ReliefStyle.NONE)
            row.get_style_context().add_class("theme-row")
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            check = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.MENU)
            check.set_opacity(1.0 if mode == current else 0.0)
            hbox.pack_start(check, False, False, 0)
            lbl = Gtk.Label(label=theme_label(mode))
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
        resolved = resolve_theme_mode(mode)
        icons = {
            "dark": "weather-clear-night-symbolic",
            "light": "weather-clear-symbolic",
        }
        name = icons.get(resolved, "weather-clear-night-symbolic")
        try:
            if self._theme_icon is not None:
                self._theme_icon.set_from_icon_name(name, Gtk.IconSize.BUTTON)
        except Exception:
            pass

    def on_theme_row_clicked(self, button, mode):
        apply_app_css(mode)
        save_theme_pref(mode)
        self._refresh_theme_icon(mode)
        try:
            tw = getattr(self, "task_window", None)
            if tw is not None and getattr(tw, "terminal", None) is not None:
                apply_terminal_theme(tw.terminal)
        except Exception:
            pass
        for m, (_row, chk) in self._theme_items.items():
            try:
                chk.set_opacity(1.0 if m == mode else 0.0)
            except Exception:
                pass
        try:
            popover = self.theme_button.get_popover()
            if popover is not None:
                popover.popdown()
        except Exception:
            pass

    def on_theme_selected(self, item, mode):
        if not item.get_active():
            return
        apply_app_css(mode)
        save_theme_pref(mode)
        self._refresh_theme_icon(mode)
        try:
            popover = self.theme_button.get_popover()
            if popover is not None:
                popover.popdown()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 语言切换
    # ------------------------------------------------------------------
    def _build_lang_menu(self):
        current = get_lang_pref()
        popover = Gtk.Popover()
        popover.set_relative_to(self.lang_button)
        popover.set_position(Gtk.PositionType.BOTTOM)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_top(6); box.set_margin_bottom(6)
        box.set_margin_start(6); box.set_margin_end(6)
        box.get_style_context().add_class("theme-popover")
        self._lang_items = {}
        for lang, label_key in (("system", "lang_system"), ("zh", "lang_zh"), ("en", "lang_en")):
            row = Gtk.Button()
            row.set_relief(Gtk.ReliefStyle.NONE)
            row.get_style_context().add_class("theme-row")
            h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            check = Gtk.Image.new_from_icon_name(
                "object-select-symbolic" if lang == current else "",
                Gtk.IconSize.BUTTON)
            lbl = Gtk.Label(label=t(label_key))
            lbl.set_halign(Gtk.Align.START)
            h.pack_start(check, False, False, 0)
            h.pack_start(lbl, True, True, 0)
            row.add(h)
            row.connect("clicked", self.on_lang_row_clicked, lang)
            self._lang_items[lang] = (row, check)
            box.pack_start(row, False, False, 0)
        box.show_all()
        popover.add(box)
        self.lang_button.set_popover(popover)
        self._lang_menu = popover

    def on_lang_row_clicked(self, button, lang):
        if lang == get_lang_pref():
            try:
                popover = self.lang_button.get_popover()
                if popover is not None:
                    popover.popdown()
            except Exception:
                pass
            return
        set_lang(lang)
        save_lang_pref(lang)
        self._refresh_ui_language()
        try:
            popover = self.lang_button.get_popover()
            if popover is not None:
                popover.popdown()
        except Exception:
            pass

    def _refresh_ui_language(self):
        page = getattr(self, "_current_page", "func")
        cat_id = getattr(self, "_current_cat_id", None)
        search_text = self.search_entry.get_text() if self.search_entry else ""

        self.set_title(t("app_title"))
        if getattr(self, "_header", None) is not None:
            self._header.props.title = t("app_title")
            self._header.props.subtitle = f"v{VERSION}  ·  {system_type_display(self.system_type)}"
        self.search_entry.set_placeholder_text(t("search_placeholder"))
        self.theme_button.set_tooltip_text(t("theme_tooltip"))
        self.lang_button.set_tooltip_text(t("lang_tooltip"))
        if getattr(self, "_lang_btn_label", None) is not None:
            self._lang_btn_label.set_text(t("lang_button"))
        self.help_btn.set_label(t("help"))
        self.quit_btn.set_label(t("quit"))
        self.sidebar_title.set_text(t("cat_sidebar"))
        for btn in (self.back_btn, self.about_back_btn, self.changelog_back_btn, self.search_back_btn):
            btn.set_label(t("back_home"))
        self.about_title.set_markup(f"<span size='large'><b>{t('about_title')}</b></span>")
        self.about_textview.get_buffer().set_text(about_body_text())
        self.changelog_title.set_markup(f"<span size='large'><b>{t('cat_changelog')}</b></span>")
        self.changelog_textview.get_buffer().set_text(changelog_body_text())

        self.icon_map = build_icon_map()
        self.category_tree = build_category_tree()
        self.category_icons = {}
        for cid, title_key, _desc_key, icon_file in category_meta():
            pix = load_icon_pixbuf(icon_file, 28) if icon_file else None
            self.category_icons[cid] = pix
            self.category_icons[t(title_key)] = pix
        self.func_map = {}
        self.build_func_map()
        self._build_theme_menu()
        self._build_lang_menu()
        self.rebuild_nav_rail()
        self.update_status()

        if search_text.strip():
            self.search_entry.set_text(search_text)
            self.on_search_changed(self.search_entry)
        elif cat_id:
            self.open_category(cat_id)
        else:
            self.open_category("support")

    def build_func_map(self):
        for items in self.category_tree.values():
            def walk(items):
                for item in items:
                    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], str):
                        self.func_map[item[0]] = item[1]
                    elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list):
                        walk(item[1])
            walk(items)

    def rebuild_nav_rail(self):
        self._clear_box(self.nav_box)
        self._nav_buttons = {}
        for cat_id, title_key, _desc_key, icon_file in category_meta():
            btn = self._make_nav_item(cat_id, t(title_key), icon_file)
            self.nav_box.pack_start(btn, False, False, 0)
            self._nav_buttons[cat_id] = btn
        self.nav_box.show_all()
        if self._current_cat_id:
            self._set_nav_selected(self._current_cat_id)

    def _make_nav_item(self, cat_id, title, icon_file):
        btn = Gtk.Button()
        btn.get_style_context().add_class("nav-item")
        btn.set_relief(Gtk.ReliefStyle.NONE)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        icon_wrap = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        icon_wrap.get_style_context().add_class("nav-icon-wrap")
        pix = self.category_icons.get(cat_id)
        if pix is None and icon_file:
            pix = load_icon_pixbuf(icon_file, 28)
        if pix is not None:
            img = Gtk.Image.new_from_pixbuf(pix)
        else:
            img = Gtk.Image.new_from_icon_name("applications-games-symbolic", Gtk.IconSize.BUTTON)
        icon_wrap.pack_start(img, False, False, 0)
        row.pack_start(icon_wrap, False, False, 0)
        lbl = Gtk.Label(label=title)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_xalign(0.0)
        lbl.set_line_wrap(True)
        lbl.get_style_context().add_class("nav-item-title")
        row.pack_start(lbl, True, True, 0)
        btn.add(row)
        btn.connect("clicked", lambda *_a, cid=cat_id: self.open_category(cid))
        return btn

    def _set_nav_selected(self, cat_id):
        for cid, btn in self._nav_buttons.items():
            ctx = btn.get_style_context()
            if cid == cat_id:
                ctx.add_class("selected")
            else:
                ctx.remove_class("selected")

    def show_home(self):
        """Master-detail has no home grid; jump to default category."""
        if self.search_entry.get_text().strip():
            self.search_entry.set_text("")
        self.open_category("support")

    def open_category(self, cat_id):
        if self.search_entry.get_text().strip():
            self.search_entry.set_text("")
        meta = {m[0]: m for m in category_meta()}
        info = meta.get(cat_id)
        if not info:
            cat_id = "support"
            info = meta.get(cat_id)
            if not info:
                return
        _cid, title_key, _desc_key, icon_file = info
        title = t(title_key)
        self._current_cat_id = cat_id
        self._set_nav_selected(cat_id)

        if cat_id == "support":
            self._current_page = "about"
            try:
                self.about_title.set_markup(f"<span size='large'><b>{t('about_title')}</b></span>")
                self.about_textview.get_buffer().set_text(about_body_text())
            except Exception:
                pass
            self.stack.set_visible_child_name("about")
            try:
                child = self.stack.get_visible_child()
                if child is not None:
                    child.show_all()
            except Exception:
                pass
            return
        if cat_id == "changelog":
            self._current_page = "changelog"
            self.stack.set_visible_child_name("changelog")
            self.display_changelog()
            try:
                child = self.stack.get_visible_child()
                if child is not None:
                    child.show_all()
            except Exception:
                pass
            return

        self._current_page = "func"
        self.stack.set_visible_child_name("func")
        icon_pixbuf = self.category_icons.get(cat_id)
        if icon_pixbuf is None and icon_file:
            icon_pixbuf = load_icon_pixbuf(icon_file, 32)
        if icon_pixbuf:
            self.title_icon.set_from_pixbuf(icon_pixbuf)
            self.title_icon.set_visible(True)
        else:
            self.title_icon.set_visible(False)
        if cat_id == "sysopt":
            title_text = f"<span size='large'><b>{title} [{system_type_display(self.system_type)}]</b></span>"
        else:
            title_text = f"<span size='large'><b>{title}</b></span>"
        self.category_title.set_markup(title_text)

        items = list(self.category_tree.get(title, []))
        if cat_id == "sysopt" and self.system_type == "双系统":
            # 把双系统检修项并进「引导与双系统」分组，避免再占一个侧栏分类
            dual_kids = [
                (fl("fix_boot"), "fix_boot"),
                (fl("fix_shared_disk"), "fix_shared_disk"),
            ]
            merged = []
            boot_title = fl("grp_boot")
            for item in items:
                if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list) and item[0] == boot_title:
                    merged.append((item[0], list(item[1]) + dual_kids))
                else:
                    merged.append(item)
            items = merged
            self.func_map[fl("fix_boot")] = "fix_boot"
            self.func_map[fl("fix_shared_disk")] = "fix_shared_disk"
        self._populate_func_tiles(items)

    def _clear_box(self, box):
        for child in list(box.get_children()):
            box.remove(child)

    def _make_func_group(self, title, children):
        """Collapsible group: accent header button + Revealer. Starts collapsed."""
        wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        wrap.get_style_context().add_class("func-group")

        header = Gtk.Button()
        header.set_relief(Gtk.ReliefStyle.NONE)
        header.get_style_context().add_class("func-group-header")
        header.set_tooltip_text(title)
        hrow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl = Gtk.Label(label=title)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_xalign(0.0)
        lbl.set_line_wrap(True)
        lbl.get_style_context().add_class("func-group-header-label")
        hrow.pack_start(lbl, True, True, 0)
        # collapsed: point right; expanded: point down
        chevron = Gtk.Image.new_from_icon_name("pan-end-symbolic", Gtk.IconSize.BUTTON)
        hrow.pack_end(chevron, False, False, 0)
        header.add(hrow)

        revealer = Gtk.Revealer()
        revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        revealer.set_transition_duration(160)
        revealer.set_reveal_child(False)  # 默认收起

        child_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        child_box.set_margin_top(2)
        child_box.set_margin_bottom(2)
        for child in children:
            if isinstance(child, tuple) and len(child) == 2 and isinstance(child[1], str):
                child_box.pack_start(
                    self._make_func_tile(child[0], child[1], child=True), False, False, 0)
        revealer.add(child_box)

        def _toggle(*_a):
            open_ = not revealer.get_reveal_child()
            revealer.set_reveal_child(open_)
            ctx = header.get_style_context()
            if open_:
                ctx.add_class("expanded")
                chevron.set_from_icon_name("pan-down-symbolic", Gtk.IconSize.BUTTON)
            else:
                ctx.remove_class("expanded")
                chevron.set_from_icon_name("pan-end-symbolic", Gtk.IconSize.BUTTON)

        header.connect("clicked", _toggle)
        wrap.pack_start(header, False, False, 0)
        wrap.pack_start(revealer, False, False, 0)
        return wrap

    def _populate_func_tiles(self, items):
        """Fill the detail list. Nested groups are collapsible and start collapsed."""
        self._clear_box(self.func_list_box)
        for item in items:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], str):
                self.func_list_box.pack_start(
                    self._make_func_tile(item[0], item[1], child=False), False, False, 0)
            elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list):
                title = item[0].upper() if get_lang() == "en" else item[0]
                self.func_list_box.pack_start(
                    self._make_func_group(title, item[1]), False, False, 0)
        self.func_list_box.show_all()

    def _make_func_tile(self, name, func_key, child=False):
        btn = Gtk.Button()
        btn.get_style_context().add_class("func-tile")
        if child:
            btn.get_style_context().add_class("child-tile")
        btn.set_relief(Gtk.ReliefStyle.NONE)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl = Gtk.Label(label=name)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_xalign(0.0)
        lbl.set_line_wrap(True)
        row.pack_start(lbl, True, True, 0)
        arrow = Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        row.pack_end(arrow, False, False, 0)
        btn.add(row)
        btn.connect("clicked", lambda *_a, n=name, k=func_key: self.run_function(n, k))
        return btn

    def detect_system_type(self):  # clover+ntfs aware
        """探测当前是否为「SteamOS + Windows」双系统。

        判据（任一成立即双系统）：
        1) EFI 启动项里有 Windows；
        2) 存在 NTFS 分区且标签为 Windows；
        3) NTFS 分区里可探测到 Windows 目录结构（Windows/ + Program Files/Users）；
        4) EFI 启动项含 Clover 且存在任意 NTFS 分区 —— Clover 接管 EFI 后
           Windows 启动项常被移除/改名，卷也可能没挂载或卷标被改，
           此时「Clover + 任意 NTFS」足以说明这是双系统机器。
        无权限读取 EFI / 分区表或探测异常时，宁可返回「双系统」把
        fix_boot / fix_shared_disk 显示出来，也不误隐藏这两项（fail-open）。
        """
        efi_output = None
        efi_read_ok = False
        saw_clover = False
        if shutil.which("efibootmgr"):
            for cmd in (["sudo", "-n", "efibootmgr"], ["efibootmgr"]):
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        efi_output = result.stdout or ""
                        efi_read_ok = True
                        if re.search(r'(?i)windows', efi_output):
                            return "双系统"
                        if re.search(r'(?i)clover', efi_output):
                            saw_clover = True
                        break  # 拿到有效输出即可，不必再试下一种方式
                except Exception:
                    continue
        else:
            # 连 efibootmgr 都没有：视为「无法可靠探测」，别因此隐藏功能。
            efi_read_ok = False

        ntfs_found = False
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
                    ntfs_found = True            # 任意 NTFS 分区都算
                    label = (fields.get("LABEL") or "").strip()
                    if label.lower() == "windows":
                        return "双系统"
                    ntfs_entries.append(fields)

                # 判据 3：看分区内容里有没有 Windows 目录结构
                cannot_read_content = False
                for fields in ntfs_entries:
                    name = fields.get("NAME") or ""
                    mountpoint = (fields.get("MOUNTPOINT") or "").strip()
                    candidates = []
                    if mountpoint and os.path.isdir(mountpoint):
                        candidates.append(mountpoint)
                    if name:
                        for base in ("/run/media", "/media"):
                            try:
                                for user_dir in os.listdir(base):
                                    p = os.path.join(base, user_dir, name)
                                    if os.path.isdir(p):
                                        candidates.append(p)
                            except Exception:
                                cannot_read_content = True
                    for path in candidates:
                        try:
                            has_win_dir = os.path.isdir(os.path.join(path, "Windows"))
                            has_pf = os.path.isdir(os.path.join(path, "Program Files"))
                            has_users = os.path.isdir(os.path.join(path, "Users"))
                            if has_win_dir and (has_pf or has_users):
                                return "双系统"
                        except Exception:
                            cannot_read_content = True
                # Clover 接管 EFI：只要存在任意 NTFS 分区就判双系统。
                if saw_clover and ntfs_found:
                    return "双系统"
                # NTFS 在，但内容读不到（无权限 / 未挂载）：宁可显示两项，别误隐藏。
                if ntfs_found and cannot_read_content:
                    return "双系统"
            else:
                # lsblk 失败（无权限等）：无法可靠探测，fail-open 显示双系统功能。
                return "双系统"
        except Exception:
            return "双系统"

        # EFI 读不到（无权限、命令缺失）也无法排除双系统，fail-open。
        if not efi_read_ok:
            return "双系统"
        return "单系统"

    def on_category_activated(self, treeview, path, column):
        """兼容旧接口：侧栏激活改为打开分类。"""
        try:
            model = treeview.get_model(); iter_ = model.get_iter(path)
            category = model.get_value(iter_, 1)
        except Exception:
            return
        for cat_id, title_key, _d, _i in category_meta():
            if category == t(title_key):
                self.open_category(cat_id)
                return

    def on_search_back(self, *_args):
        self.search_entry.set_text("")
        page = getattr(self, "_nav_before_search", "func")
        cat_id = getattr(self, "_current_cat_id", None) or "support"
        if page == "about":
            self.open_category("support")
        elif page == "changelog":
            self.open_category("changelog")
        else:
            self.open_category(cat_id)

    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()
        if not query:
            page = getattr(self, "_nav_before_search", "func")
            if self.stack.get_visible_child_name() == "search":
                cat_id = getattr(self, "_current_cat_id", None) or "support"
                if page == "about":
                    self.open_category("support")
                elif page == "changelog":
                    self.open_category("changelog")
                else:
                    self.open_category(cat_id)
            return

        if self.stack.get_visible_child_name() != "search":
            self._nav_before_search = getattr(self, "_current_page", "func")

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
            for key in ("fix_boot", "fix_shared_disk"):
                name = fl(key)
                if query in name.lower():
                    matches.append((name, t("cat_sysopt"), key))
        self.search_store.clear()
        self._clear_box(self.search_list_box)
        for name, cat, key in matches:
            self.search_store.append([name, cat, key])
            btn = Gtk.Button()
            btn.get_style_context().add_class("func-tile")
            btn.set_relief(Gtk.ReliefStyle.NONE)
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            n = Gtk.Label(label=name); n.set_halign(Gtk.Align.START); n.set_xalign(0.0)
            c = Gtk.Label(label=cat); c.set_halign(Gtk.Align.START); c.set_xalign(0.0)
            c.get_style_context().add_class("dash-card-desc")
            row.pack_start(n, False, False, 0)
            row.pack_start(c, False, False, 0)
            outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            outer.pack_start(row, True, True, 0)
            outer.pack_end(Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON), False, False, 0)
            btn.add(outer)
            btn.connect("clicked", lambda *_a, nn=name, kk=key: self.run_function(nn, kk))
            self.search_list_box.pack_start(btn, False, False, 0)
        self.search_list_box.show_all()
        if matches:
            self.search_title.set_markup(f"<span size='large'><b>{t('search_results', n=len(matches))}</b></span>")
        else:
            self.search_title.set_markup(f"<span size='large'><b>{t('search_none')}</b></span>")
        self.stack.set_visible_child_name("search")

    def on_search_row_activated(self, treeview, path, column):
        model = treeview.get_model(); iter_ = model.get_iter(path)
        func_name = model.get_value(iter_, 0)
        func_key = model.get_value(iter_, 2)
        self.run_function(func_name, func_key)

    @guarded
    def run_function(self, func_name, func_key):
        if func_key in DANGEROUS_FUNCS:
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.NONE,
                                    text=t("danger_title", name=func_name))
            dlg.add_button(t("no"), Gtk.ResponseType.NO)
            dlg.add_button(t("yes"), Gtk.ResponseType.YES)
            dlg.format_secondary_text(dangerous_hint(func_key))
            # 危险操作默认焦点放在「否」上，避免误按回车直接执行
            try:
                dlg.set_default_response(Gtk.ResponseType.NO)
            except Exception:
                pass
            fix_dialog_size(dlg)
            response = dlg.run()
            dlg.destroy()
            if response != Gtk.ResponseType.YES:
                return

        # Flatpak 安装/卸载改为原生 GTK 窗口（不再走 zenity 脚本）
        if func_key == "install_flatpak_apps_gui":
            win = FlatpakInstallWindow(self)
            self._fp_win = win
            return
        if func_key == "uninstall_other_flatpak_apps":
            win = FlatpakUninstallWindow(self)
            self._fp_win = win
            return

        # Steam 缓存管理器改为原生 GTK 窗口（不再走 zenity 脚本）
        if func_key == "steamdeck_cache_manager":
            win = CacheManagerWindow(self)
            self._cm_win = win
            return

        # 兼容层管理改为原生 GTK 窗口（安装/卸载 GE-Proton、CachyOS、DW Proton）
        if func_key == "ge_proton_manager":
            win = CompatManagerWindow(self)
            self._compat_win = win
            return
        if func_key == "install_uu_accelerator":
            self.run_external_terminal(func_key); return

        # FIX-GUI: confirm before killing running task
        old = getattr(self, "task_window", None)
        # 旧任务仍在运行：先弹确认，不再直接 destroy（那会悄悄杀掉正在跑的任务）。
        if old is not None and not getattr(old, "completed", True):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                                    text=t("task_running_confirm"))
            dlg.add_button(t("no"), Gtk.ResponseType.NO)
            dlg.add_button(t("yes"), Gtk.ResponseType.YES)
            fix_dialog_size(dlg)
            response = dlg.run()
            dlg.destroy()
            if response != Gtk.ResponseType.YES:
                return
            old.force_kill()
        elif old is not None:
            old.destroy()
        self.task_window = TaskWindow(self, func_key, func_name)

    def update_status(self):
        term = t("term_embedded") if VTE_AVAILABLE else t("term_external")
        self.status_label.set_text(t("status", sys=system_type_display(self.system_type), term=term, ver=VERSION))

    def display_changelog(self):
        self.changelog_textview.get_buffer().set_text(changelog_body_text())

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
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.NONE,
                                    text="缺少 zenity 组件，无法运行该功能")
            dlg.add_button(t("ok"), Gtk.ResponseType.OK)
            dlg.format_secondary_text(
                "该功能依赖 zenity 提供图形化选择界面。\n"
                "请先安装后重试：sudo pacman -S zenity")
            fix_dialog_size(dlg)
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
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.NONE,
                                    text="启动任务失败")
            dlg.add_button(t("ok"), Gtk.ResponseType.OK)
            dlg.format_secondary_text(f"{e}")
            fix_dialog_size(dlg)
            dlg.run(); dlg.destroy()

    def run_external_terminal(self, func_key):
        tmp_path = create_temp_script()
        close_prompt = ("Press Enter to close..." if get_lang() == "en" else "按回车键关闭...")
        cmd = f"bash {tmp_path} {func_key}; read -p '{close_prompt}' -n1"
        if not launch_terminal(cmd):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.NONE,
                                    text=t("no_terminal"))
            dlg.add_button(t("ok"), Gtk.ResponseType.OK)
            dlg.format_secondary_text(t("no_terminal_hint"))
            fix_dialog_size(dlg)
            dlg.run(); dlg.destroy()

    def on_help_clicked(self, button):
        help_dialog = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                        type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.NONE,
                                        text=t("app_title"))
        help_dialog.add_button(t("ok"), Gtk.ResponseType.OK)
        if get_lang() == "en":
            # 英文：可点击 X 链接（与 GitHub 英文版一致）
            help_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            help_box.set_margin_start(12); help_box.set_margin_end(12)
            help_box.set_margin_top(4); help_box.set_margin_bottom(8)
            body = Gtk.Label()
            body.set_markup(t("help_body_en_markup"))
            body.set_line_wrap(True)
            body.set_xalign(0.0)
            body.set_selectable(False)
            body.connect("activate-link",
                         lambda lbl, uri: (Gtk.show_uri_on_window(help_dialog, uri, Gtk.get_current_event_time()), True)[1])
            help_box.pack_start(body, False, False, 0)
            help_box.show_all()
            help_dialog.get_message_area().pack_start(help_box, False, False, 0)
        else:
            help_dialog.format_secondary_text(t("help_body_zh"))
        fix_dialog_size(help_dialog)
        help_dialog.run(); help_dialog.destroy()


def _desktop_dir():
    """按 XDG 规范取桌面目录：xdg-user-dir DESKTOP → ~/.config/user-dirs.dirs → ~/Desktop。"""
    try:
        r = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True,
                           text=True, timeout=3)
        d = (r.stdout or "").strip()
        if d and os.path.isabs(d):
            return d
    except Exception:
        pass
    ud = os.path.join(os.path.expanduser("~"), ".config", "user-dirs.dirs")
    try:
        with open(ud, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("XDG_DESKTOP_DIR"):
                    val = line.split("=", 1)[1].strip().strip('"')
                    val = val.replace("$HOME", os.path.expanduser("~"))
                    if os.path.isabs(val):
                        return val
    except Exception:
        pass
    return os.path.expanduser("~/Desktop")


def ensure_desktop_shortcut():  # XDG aware
    # 整个流程只打印错误、绝不抛异常：快捷方式失败不能阻塞主界面启动。
    try:
        script_path = os.path.abspath(sys.argv[0])
        desktop_dir = _desktop_dir()
        os.makedirs(desktop_dir, exist_ok=True)
        desktop_name = "Deck Toolbox.desktop" if get_lang() == "en" else "Deck工具箱.desktop"
        app_name = "Deck Toolbox" if get_lang() == "en" else "Deck工具箱"
        desktop_file = os.path.join(desktop_dir, desktop_name)
        expected_exec = f'Exec={sys.executable} "{script_path}"'
        # 已有同名快捷方式：校验 Exec 是否指向当前脚本绝对路径，不一致则重写（自愈）。
        if os.path.isfile(desktop_file):
            try:
                with open(desktop_file, "r", encoding="utf-8", errors="replace") as f:
                    head = f.read(4096)
                if any(l.strip() == expected_exec for l in head.splitlines()):
                    return
            except Exception:
                pass
        content = f"""[Desktop Entry]
Type=Application
Name={app_name}
{expected_exec}
Icon=input-gamepad-symbolic
Terminal=false
StartupNotify=true
StartupWMClass=Steamdeck-toolbox
Categories=Utility;
"""
        with open(desktop_file, 'w', encoding='utf-8') as f:
            f.write(content)
        os.chmod(desktop_file, 0o755)
    except Exception as e:
        msg = (f"Failed to create desktop shortcut: {e}" if get_lang() == "en"
               else f"创建桌面快捷方式失败: {e}")
        print(msg)

def ensure_vte_installed():
    # 注意：这个提示框以前是 MODAL + parent=None。
    # 实测（xdotool 真实点击）：主窗口上只要存在一个模态框，所有瓷砖点击都会被吞掉，
    # 而 parent=None 的框在某些窗口管理器下会跑到主窗口**后面**——
    # 用户看到的是「工具箱窗口在，但点什么都没反应」，正是这个原因。
    # 改成非模态 + 置顶 + present()，即使它被压到后面，主界面也照常可用。
    if VTE_AVAILABLE: return
    # 找主窗口作为 parent：非模态框有明确父窗才不会跑到主界面后面。
    parent = None
    try:
        for w in Gtk.Window.list_toplevels():
            if isinstance(w, MainWindow):
                parent = w
                break
    except Exception:
        parent = None
    dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.NONE, t("vte_missing"))
    dialog.format_secondary_text(t("vte_missing_hint"))
    dialog.add_button(t("yes"), Gtk.ResponseType.YES); dialog.add_button(t("no"), Gtk.ResponseType.NO)
    dialog.set_icon_name("input-gamepad-symbolic")
    dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT if parent else Gtk.WindowPosition.CENTER)
    dialog.set_keep_above(True)
    if parent:
        dialog.set_transient_for(parent)
    dialog.set_modal(False)
    fix_dialog_size(dialog)

    def on_response(dlg, response):
        # 用 response 回调代替 dialog.run()：run() 会临时启用模态并嵌套主循环，
        # 与「非模态、主界面不被阻断」的注释不符。
        try:
            dlg.destroy()
        except Exception:
            pass
        if response != Gtk.ResponseType.YES:
            return
        _do_install_vte(parent)

    dialog.connect("response", on_response)
    dialog.show_all()
    dialog.present()
    return

def _do_install_vte(parent=None):
    if True:
        if get_lang() == "en":
            install_cmd = (
                "if command -v steamos-readonly >/dev/null 2>&1; then "
                "sudo steamos-readonly disable || { echo 'x Failed to disable read-only; run: sudo steamos-readonly disable'; read -n1; exit 1; }; "
                "fi; "
                "echo 'Initializing pacman keyring (may take a while)...'; "
                "sudo pacman-key --init || { echo 'x pacman keyring init failed'; read -n1; exit 1; }; "
                "sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null; sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null; "
                "echo 'Importing Arch + SteamOS Holo keys...'; "
                "sudo pacman-key --populate archlinux || { echo 'x archlinux keyring populate failed'; read -n1; exit 1; }; "
                "if [ -f /usr/share/pacman/keyrings/holo.gpg ]; then "
                "sudo pacman-key --populate holo || { echo 'x holo keyring populate failed'; read -n1; exit 1; }; "
                "fi; "
                "echo 'Trusting SteamOS packager key...'; "
                "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || { "
                "echo '! lsign failed, refreshing...'; "
                "sudo pacman-key --refresh-keys 2>/dev/null; "
                "sudo pacman-key --populate archlinux holo 2>/dev/null; "
                "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || "
                "{ echo 'x key lsign failed'; read -n1; exit 1; }; }; "
                "sudo pacman -Sy --noconfirm >/dev/null 2>&1; "
                "sudo pacman -S --needed --noconfirm vte3 || { echo 'x vte3 install failed, check network/repos'; read -n1; exit 1; }; "
                "pacman -Q vte3 >/dev/null 2>&1 || { echo 'x vte3 verification failed, restart the app and retry'; read -n1; exit 1; }; "
                "command -v steamos-readonly >/dev/null 2>&1 && sudo steamos-readonly enable 2>/dev/null || true; "
                "echo 'Done. Please restart this app manually.'; read -n1"
            )
        else:
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
        _vte_install_cmd_en = install_cmd
        if not launch_terminal(install_cmd):
            err = Gtk.MessageDialog(parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.NONE,
                                    t("no_terminal"))
            err.add_button(t("ok"), Gtk.ResponseType.OK)
            err.format_secondary_text(t("vte_manual"))
            fix_dialog_size(err)
            err.run(); err.destroy()

def sync_emoji_icons():  # fully guarded
    """确保脚本目录下存在 emoji_icons 文件夹（从内嵌数据解出，离线可用，便于自定义图标）。

    整个函数（含 os.makedirs）必须包在 try 里：目录只读时 makedirs 会在线程里
    抛异常，而更新检查窗口 deletable=False，线程一死就永远进不了主界面。
    这里任何异常都只打印，绝不外抛。
    """
    try:
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
    except Exception as e:
        print(f"同步 emoji_icons 失败（不影响启动）: {e}")

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

# 启动闪屏与更新过程共用同一窗口尺寸，避免「检查更新」与「正在更新」一大一小跳动
UPDATE_SPLASH_SIZE = (400, 150)

def _perform_update_in_window(win, remote_version):
    """在 UpdateCheckWindow 内下载并替换自身（与检查更新同窗同尺寸）。"""
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
            # 下载后再核对一次 VERSION 与检查结果一致，防止 CDN 缓存 / 中间人
            # 给了另一个版本却按 remote_version 提示并重启。
            m = re.search(r'^VERSION\s*=\s*["\']([0-9.]+)["\']', new_content, re.MULTILINE)
            got_ver = m.group(1) if m else None
            if got_ver is None or compare_versions(got_ver, remote_version) != 0:
                raise ValueError(
                    t("update_ver_mismatch", want=remote_version,
                      got=(got_ver or "?")))
            # sys.argv[0] 可能是 sh / 包装脚本 / 相对路径；只替换已知 GUI 文件名
            # 且是 regular file 的目标，否则绝不覆盖（可能覆盖错误文件）。
            KNOWN_GUI_BASENAMES = ("steamdeck_gui.py", "steamdeck_toolbox_gui.py",
                                   "steamdeck-toolbox.py")
            argv0 = os.path.abspath(sys.argv[0])
            is_safe = (os.path.basename(argv0) in KNOWN_GUI_BASENAMES
                       and os.path.isfile(argv0) and not os.path.islink(argv0))
            if not is_safe:
                raise ValueError(t("update_target_unsafe", path=argv0, url=REPO_RAW_URL))
            current_path = argv0
            backup_path = current_path + ".bak"
            try:
                shutil.copy2(current_path, backup_path)
            except Exception as be:
                # 备份失败要提示，不能静默吞掉；更新继续但明确告知无自动回滚。
                print(t("update_backup_fail", err=be))
                try:
                    GLib.idle_add(lambda: win.label.set_text(t("update_backup_fail", err=be)))
                except Exception:
                    pass
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
            GLib.idle_add(_update_window_success, win, remote_version)
        except Exception as e:
            GLib.idle_add(_update_window_error, win, str(e))
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try: os.unlink(tmp_path)
                except Exception: pass
    threading.Thread(target=do_download, daemon=True).start()

def _update_window_success(win, remote_version):
    try:
        win._clear_action_buttons()
        win.label.set_text(t("update_ok") + "\n" + t("update_ok_hint", ver=remote_version))
    except Exception:
        pass
    def restart():
        try:
            win.destroy()
        except Exception:
            pass
        subprocess.Popen([sys.executable, sys.argv[0]])
        Gtk.main_quit()
    GLib.timeout_add(500, restart)

def _update_window_error(win, error_msg):
    try:
        win._clear_action_buttons()
        win.label.set_text(t("update_fail") + "\n" + t("update_fail_hint", err=error_msg, url=REPO_RAW_URL))
        btn = Gtk.Button(label=t("ok"))
        btn.connect("clicked", lambda *_: (win.destroy(), show_main_window()))
        win.vbox.pack_start(btn, False, False, 0)
        win._action_buttons = [btn]
        btn.show()
    except Exception:
        show_main_window()


# ============================================================================
# Flatpak 应用安装 / 卸载（GTK 版，替代原来的 zenity 实现）
# ============================================================================
# 为什么改：zenity 只是外挂子进程，bash 侧靠 kill -0 轮询判断"窗口还在不在"，
# 实测真实窗口下取消不可靠（flatpak 常常在检测到之前就装完了）。
# 改成 GTK 后由 Python 直接 Popen 跑 flatpak，取消 = terminate() 该进程，
# 是确定的、立即生效的操作，不依赖任何间接推断。
# ============================================================================
# ============================================================================
# Flatpak 应用安装 / 卸载（GTK 版）
# ============================================================================
# 为什么不再用 zenity：
#   1) 取消/关窗无法真正终止 flatpak —— zenity 只是外挂子进程，bash 侧靠 kill -0
#      轮询检测，实测真实窗口下要么检测不到、要么 flatpak 已经把包装完了；
#   2) 进度只能靠管道喂百分比，拿不到"取消"这种即时控制权。
# 改成 GTK 后，Python 用 Popen 直接跑 flatpak，取消时 terminate() 就是权威操作，
# 不需要任何轮询推断。
FLATPAK_CATALOG = [
    # (显示名, 候选 ID 列表, 桌面分类, 桌面快捷方式名, 附加包, 分组)
    ("WPS Office",      ["com.wps.Office", "cn.wps.wps-office", "com.kingsoft.wps"], "Office", "WPS Office", None, "办公"),
    ("微信",            ["com.tencent.WeChat", "com.qq.weixin"], "Network;Chat", "微信", None, "通讯"),
    ("QQ",              ["com.qq.QQ", "com.tencent.qq"], "Network;Chat", "QQ", None, "通讯"),
    ("钉钉",            ["com.dingtalk.DingTalk"], "Network;Chat", "DingTalk", None, "通讯"),
    ("飞书",            ["cn.feishu.Feishu"], "Network;Chat", "Feishu", None, "通讯"),
    ("腾讯会议",        ["com.tencent.wemeet"], "Network;Chat", "Wemeet", None, "通讯"),
    ("Telegram",        ["org.telegram.desktop"], "Network;Chat", "Telegram", None, "通讯"),
    ("Discord",         ["com.discordapp.Discord"], "Network;Chat", "Discord", None, "通讯"),
    ("Edge浏览器",      ["com.microsoft.Edge"], "Network;WebBrowser", "Microsoft Edge", None, "浏览器"),
    ("Google浏览器",    ["com.google.Chrome", "org.chromium.Chromium"], "Network;WebBrowser", "Google Chrome", None, "浏览器"),
    ("Firefox",         ["org.mozilla.firefox"], "Network;WebBrowser", "Firefox", None, "浏览器"),
    ("QQ音乐",          ["com.qq.QQmusic", "com.tencent.QQmusic"], "Audio", "QQ音乐", None, "影音"),
    ("网易云音乐",      ["com.github.gmg137.netease-cloud-music-gtk"], "Audio", "NetEase Cloud Music", None, "影音"),
    ("VLC",             ["org.videolan.VLC"], "AudioVideo", "VLC", None, "影音"),
    ("Spotify",         ["com.spotify.Client"], "Audio;Music", "Spotify", None, "影音"),
    ("百度网盘",        ["com.baidu.NetDisk", "com.baidu.pan"], "Network;FileTransfer", "百度网盘", None, "网盘下载"),
    ("迅雷",            ["com.xunlei.Thunder"], "Network;FileTransfer", "Thunder", None, "网盘下载"),
    ("LibreOffice",     ["org.libreoffice.LibreOffice"], "Office", "LibreOffice", None, "办公"),
    ("Obsidian",        ["md.obsidian.Obsidian"], "Office;Utility", "Obsidian", None, "笔记写作"),
    ("Joplin",          ["net.cozic.joplin_desktop"], "Office;Utility", "Joplin", None, "笔记写作"),
    ("Thunderbird",     ["org.mozilla.thunderbird"], "Network;Email", "Thunderbird", None, "办公"),
    ("OBS Studio",      ["com.obsproject.Studio"], "AudioVideo", "OBS Studio", None, "创作工具"),
    ("GIMP",            ["org.gimp.GIMP"], "Graphics", "GIMP", None, "创作工具"),
    ("Krita",           ["org.kde.krita"], "Graphics", "Krita", None, "创作工具"),
    ("Inkscape",        ["org.inkscape.Inkscape"], "Graphics", "Inkscape", None, "创作工具"),
    ("Audacity",        ["org.audacityteam.Audacity"], "AudioVideo", "Audacity", None, "创作工具"),
    ("Blender",         ["org.blender.Blender"], "Graphics;3DGraphics", "Blender", None, "创作工具"),
    ("RustDesk",        ["com.rustdesk.RustDesk"], "Network;RemoteAccess", "RustDesk", None, "远程控制"),
    ("Remmina",         ["org.remmina.Remmina"], "Network;RemoteAccess", "Remmina", None, "远程控制"),
    ("Lutris",          ["net.lutris.Lutris"], "Game", "Lutris", None, "游戏工具"),
    ("Heroic",          ["com.heroicgameslauncher.hgl"], "Game", "Heroic", None, "游戏工具"),
    ("Prism Launcher",  ["org.prismlauncher.PrismLauncher"], "Game", "Prism Launcher", None, "游戏工具"),
    ("RetroArch",       ["org.libretro.RetroArch"], "Game;Emulator", "RetroArch", None, "游戏工具"),
    ("PCSX2",           ["net.pcsx2.PCSX2"], "Game;Emulator", "PCSX2", None, "游戏工具"),
    ("Dolphin",         ["org.DolphinEmu.dolphin-emu"], "Game;Emulator", "Dolphin Emulator", None, "游戏工具"),
    ("Flatseal",        ["com.github.tchx84.Flatseal"], "Utility;Settings", "Flatseal", None, "系统工具"),
    ("Fcitx 5",         ["org.fcitx.Fcitx5"], "Utility;Settings", "Fcitx 5", "org.fcitx.Fcitx5.Addon.ChineseAddons", "系统工具"),
]

FLATPAK_EXCLUDE = {"org.fcitx.Fcitx5.Addon.ChineseAddons"}


def _fp_installed_ids():  # returns (ids, err)
    """返回 (已安装 ID 集合, 错误字符串)。err 为空串表示查询确实成功。

    旧实现忽略 returncode / FileNotFoundError，一律返回空集：flatpak 没装或
    命令失败时，卸载页显示「没有可卸载应用」、安装页把已装应用当成未装，
    属于把「查询失败」谎报成「确实没有」。"""
    try:
        r = subprocess.run(["flatpak", "list", "--app", "--columns=application"],
                           capture_output=True, text=True, timeout=15)
    except FileNotFoundError:
        return set(), "flatpak 命令未安装"
    except Exception as e:
        return set(), str(e)
    if r.returncode != 0:
        err = (r.stderr or "").strip() or ("flatpak list 退出码 %d" % r.returncode)
        return set(), err
    return set(x.strip() for x in r.stdout.splitlines() if x.strip()), ""


def _fp_pick_id(candidates, installed):
    """从候选 ID 里挑一个可用的：优先已安装的，否则取第一个。"""
    for c in candidates:
        if c in installed:
            return c
    return candidates[0]


def _fp_run_async(argv, on_line, on_done, cwd=None, env=None, owner=None):
    """跑一个子进程，按行回调输出，结束后回调退出码。

    Popen 句柄挂在 owner（窗口实例）上，而不是模块级 _fp_run_async.last_proc：
    那个全局变量被多个窗口共享，多窗并存时会互抢导致取消杀错进程。
    start_new_session=True 让子进程自成进程组，取消时可 killpg 整组终止。
    """
    def worker():
        proc = None
        rc = 1
        try:
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    cwd=cwd, env=env, bufsize=1, text=True,
                                    start_new_session=True)
            if owner is not None:
                owner.proc = proc
                try:
                    owner.proc_pgid = os.getpgid(proc.pid)
                except Exception:
                    owner.proc_pgid = proc.pid
            for line in iter(proc.stdout.readline, ""):
                if line:
                    GLib.idle_add(on_line, line)
            proc.wait()
            rc = proc.returncode
        except Exception as e:
            GLib.idle_add(on_line, f"{e}\n")
            rc = 1
        finally:
            try:
                if proc and proc.stdout:
                    proc.stdout.close()
            except Exception:
                pass
            GLib.idle_add(on_done, rc)

    th = threading.Thread(target=worker, daemon=True)
    th.start()
    return th


def _fp_progress_parse(line):
    """从 flatpak 输出里解析 (子步骤, 子步骤总数, 段内百分比, 速度)。"""
    step = steps = 0
    pct = None
    rate = ""
    m = re.search(r"(\d+)/(\d+)", line)
    if m:
        try:
            step, steps = int(m.group(1)), int(m.group(2))
        except Exception:
            step = steps = 0
    # 取最后一个百分号前的数字
    pcts = re.findall(r"(\d+)%", line)
    if pcts:
        pct = int(pcts[-1])
    m = re.search(r"([\d.]+)\s*([kKmMgG]?B/s)", line)
    if m:
        rate = f"{m.group(1)} {m.group(2)}"
    if pct is None:
        return None
    return step, steps, pct, rate


def _fp_fold_pct(step, steps, pct):
    """把「第 step 个子任务、段内 pct%」折算成整应用百分比。"""
    if steps and steps > 1:
        step = max(1, min(step or 1, steps))
        return ((step - 1) * 100 + pct) // steps
    return pct


def _fp_write_shortcut(desk_name, cat, app_id):
    """创建桌面快捷方式（仅在应用确实已安装时）。"""
    try:
        r = subprocess.run(["flatpak", "info", app_id], capture_output=True, timeout=10)
        if r.returncode != 0:
            return False
        desktop_dir = os.environ.get("XDG_DESKTOP_DIR") or os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(desktop_dir, exist_ok=True)
        path = os.path.join(desktop_dir, f"{desk_name}.desktop")
        with open(path, "w", encoding="utf-8") as f:
            f.write("[Desktop Entry]\nType=Application\n"
                    f"Name={desk_name}\nExec=flatpak run {app_id}\n"
                    f"Icon={app_id}\nTerminal=false\nCategories={cat};\n")
        os.chmod(path, 0o755)
        return True
    except Exception:
        return False


def _fp_remove_shortcuts(app_id):
    """删除指向该应用的桌面快捷方式。

    安装时快捷方式按「显示名」命名，所以不能靠文件名匹配；
    改为读 .desktop 的 Exec 行，凡是 flatpak run <ID> 的都删。
    """
    removed = []
    try:
        desktop_dir = os.environ.get("XDG_DESKTOP_DIR") or os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop_dir):
            return removed
        pat = re.compile(r"^Exec=.*flatpak\s+run\s+" + re.escape(app_id) + r"(\s|$)")
        for name in os.listdir(desktop_dir):
            if not name.endswith(".desktop"):
                continue
            p = os.path.join(desktop_dir, name)
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    head = f.read(4096)
            except Exception:
                continue
            if any(pat.match(l) for l in head.splitlines()):
                try:
                    os.remove(p)
                    removed.append(name)
                except Exception:
                    pass
    except Exception:
        pass
    return removed

# ---------- Steam 缓存管理器（GTK 原生，替代原有的 zenity 实现） ----------

def _cm_steamapps_dirs():
    """收集所有 Steam 库的 steamapps 目录：默认库 + libraryfolders.vdf 里的其它库。

    旧 zenity 实现只写死 $HOME/.local/share/Steam/steamapps，装在 SD 卡或
    第二块盘的库完全不出现；这里保持同样行为，把 VDF 里的路径也加进来。
    """
    dirs = []
    root = os.path.join(os.path.expanduser("~"), ".local", "share", "Steam")
    d0 = os.path.join(root, "steamapps")
    if os.path.isdir(d0):
        dirs.append(d0)
    vdf = os.path.join(d0, "libraryfolders.vdf")
    if os.path.isfile(vdf):
        try:
            with open(vdf, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    m = re.search(r'"path"\s*"([^"]+)"', line)
                    if not m:
                        continue
                    sa = os.path.join(m.group(1), "steamapps")
                    if os.path.isdir(sa) and sa not in dirs:
                        dirs.append(sa)
        except Exception:
            pass
    return dirs


def _cm_dir_size_mb(path):
    """用 du -sm 取目录大小（MB）。失败返回 0，调用方按「空目录」跳过。"""
    try:
        r = subprocess.run(["du", "-sm", "--", path], capture_output=True, text=True, timeout=180)
        v = r.stdout.split("\t")[0].strip()
        return int(v) if v.isdigit() else 0
    except Exception:
        return 0


def _cm_app_name(steamapps, app_id):
    """从 appmanifest_<id>.acf 里读游戏名，取不到返回空串。"""
    manifest = os.path.join(steamapps, "appmanifest_%s.acf" % app_id)
    try:
        with open(manifest, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"name"' in line:
                    parts = line.split('"')
                    if len(parts) > 3 and parts[3].strip():
                        return parts[3].strip()
                    break
    except Exception:
        pass
    return ""


def _cm_scan(cache_type):
    """扫描某一类缓存，返回 [(app_id, 名称, 大小MB, 目录), ...]，大的排前面。"""
    out = []
    for sa in _cm_steamapps_dirs():
        base = os.path.join(sa, cache_type)
        if not os.path.isdir(base):
            continue
        try:
            names = sorted(os.listdir(base))
        except Exception:
            continue
        for app_id in names:
            if not app_id.isdigit():
                continue
            full = os.path.join(base, app_id)
            if not os.path.isdir(full):
                continue
            mb = _cm_dir_size_mb(full)
            if mb <= 0:
                continue
            out.append((app_id, _cm_app_name(sa, app_id), mb, full))
    out.sort(key=lambda x: x[2], reverse=True)
    return out


def _cm_steam_running():
    """Steam 在跑时删 compatdata 可能损坏正在用的 Proton 前缀，删前要提示。"""
    for exe in ("steam", "steamwebhelper"):
        try:
            if subprocess.run(["pgrep", "-x", exe], capture_output=True).returncode == 0:
                return True
        except Exception:
            pass
    return False


def _cm_fmt_size(mb):
    if mb >= 1024:
        return "%.1f GB" % (mb / 1024.0)
    return "%d MB" % mb


class CacheManagerWindow(Gtk.Window):
    """Steam 缓存管理器：选类型 → 勾选条目 → 确认 → 删除 → 结果。

    全部在一个窗口里完成，不再弹 zenity。流程与 FlatpakUninstallWindow 一致：
    用显式 self.phase 驱动页面与按钮，而不是靠窗口是否还在来推断状态。
    """

    def __init__(self, parent=None):
        super().__init__(title=fl("steamdeck_cache_manager"))
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(660, 560)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT if parent else Gtk.WindowPosition.CENTER)
        if parent:
            self.set_transient_for(parent)
        self.set_deletable(True)

        self.phase = "type"        # type / items / confirm / running / done
        self.cache_type = "shadercache"
        self.items = []            # 当前类型扫描到的全部条目
        self.picked = []           # 勾选的条目
        self.scanning = False
        self.cancelled = False
        self.cur_proc = None       # 正在跑的 rm，取消时 terminate
        self.deleted = 0
        self.failed = 0
        self.freed_mb = 0
        self.total_mb = 0
        self.steamapps = _cm_steamapps_dirs()

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        head.set_margin_top(14); head.set_margin_bottom(8)
        head.set_margin_start(16); head.set_margin_end(16)
        title = Gtk.Label()
        title.set_markup("<span size='large'><b>%s</b></span>"
                         % GLib.markup_escape_text(fl("steamdeck_cache_manager")))
        title.set_xalign(0)
        head.pack_start(title, True, True, 0)
        outer.pack_start(head, False, False, 0)

        self.hint = Gtk.Label()
        self.hint.set_xalign(0); self.hint.set_line_wrap(True)
        self.hint.set_margin_start(16); self.hint.set_margin_end(16); self.hint.set_margin_bottom(8)
        self.hint.get_style_context().add_class("dash-card-desc")
        outer.pack_start(self.hint, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(160)
        self.stack.set_margin_start(16); self.stack.set_margin_end(16)
        outer.pack_start(self.stack, True, True, 0)
        self.stack.add_named(self._build_type_page(), "type")
        self.stack.add_named(self._build_items_page(), "items")
        self.stack.add_named(self._build_confirm_page(), "confirm")
        self.stack.add_named(self._build_progress_page(), "progress")

        # 底部按钮：一个主按钮随阶段变化 + 一个返回按钮（列表/确认页才有意义）
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_row.set_margin_top(10); btn_row.set_margin_bottom(14)
        btn_row.set_margin_start(16); btn_row.set_margin_end(16)
        self.back_btn = Gtk.Button(label=self._lbl("back"))
        self.back_btn.connect("clicked", self._on_back_clicked)
        btn_row.pack_start(self.back_btn, False, False, 0)
        self.main_btn = Gtk.Button(label=self._lbl("next"))
        self.main_btn.get_style_context().add_class("suggested-action")
        self.main_btn.connect("clicked", self._on_main_clicked)
        btn_row.pack_end(self.main_btn, False, False, 0)
        outer.pack_start(btn_row, False, False, 0)

        self.add(outer)
        self.connect("delete-event", self._on_delete_event)
        self.show_all()
        self.present()
        self._sync_buttons()

    # ---------- 文案 ----------

    def _lbl(self, key):
        m = {
            "next":     ("查看", "View"),
            "delete":   ("删除所选", "Delete selected"),
            "cancel":   ("取消", "Cancel"),
            "back":     ("返回", "Back"),
            "done":     ("完成", "Done"),
        }
        zh, en = m[key]
        return en if get_lang() == "en" else zh

    def _t(self, zh, en):
        return en if get_lang() == "en" else zh

    def _type_title(self, cache_type=None):
        ct = cache_type or self.cache_type
        if ct == "shadercache":
            return self._t("着色器缓存", "Shader cache")
        return self._t("兼容数据", "Compatibility data")

    # ---------- 页面构建 ----------

    def _build_type_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_valign(Gtk.Align.START)

        self.rb_shader = Gtk.RadioButton.new_with_label_from_widget(
            None, self._t("着色器缓存", "Shader cache"))
        self.rb_shader.connect("toggled", self._on_type_toggled)
        row1 = self._radio_row(self.rb_shader,
                               self._t("shadercache，删掉后会自动重建，不影响游戏数据",
                                       "shadercache, rebuilt automatically, game data untouched"))
        box.pack_start(row1, False, False, 0)

        self.rb_compat = Gtk.RadioButton.new_with_label_from_widget(
            self.rb_shader, self._t("兼容数据", "Compatibility data"))
        self.rb_compat.connect("toggled", self._on_type_toggled)
        row2 = self._radio_row(self.rb_compat,
                               self._t("compatdata，含各游戏的 Proton 前缀，删除后对应游戏需要重新初始化",
                                       "compatdata, holds each game's Proton prefix; those games must reinitialize"))
        box.pack_start(row2, False, False, 0)
        return box

    def _radio_row(self, radio, desc):
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        row.set_margin_top(6)
        radio.set_halign(Gtk.Align.START)
        row.pack_start(radio, False, False, 0)
        lbl = Gtk.Label(label=desc)
        lbl.set_xalign(0); lbl.set_line_wrap(True)
        lbl.set_margin_start(28)
        lbl.get_style_context().add_class("dash-card-desc")
        row.pack_start(lbl, False, False, 0)
        return row

    def _build_items_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sw.add(self.list_box)
        box.pack_start(sw, True, True, 0)
        return box

    def _build_confirm_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_valign(Gtk.Align.FILL)
        self.confirm_label = Gtk.Label()
        self.confirm_label.set_xalign(0); self.confirm_label.set_line_wrap(True)
        self.confirm_label.set_valign(Gtk.Align.START)
        self.confirm_label.set_selectable(False)
        sw.add(self.confirm_label)
        box.pack_start(sw, True, True, 0)
        return box

    def _build_progress_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_valign(Gtk.Align.CENTER)
        self.prog_label = Gtk.Label(label="")
        self.prog_label.set_xalign(0); self.prog_label.set_line_wrap(True)
        self.prog_label.get_style_context().add_class("dash-card-title")
        box.pack_start(self.prog_label, False, False, 0)
        self.prog_bar = Gtk.ProgressBar()
        self.prog_bar.set_show_text(False)
        box.pack_start(self.prog_bar, False, False, 0)
        self.detail_label = Gtk.Label(label="")
        self.detail_label.set_xalign(0); self.detail_label.set_line_wrap(True)
        self.detail_label.get_style_context().add_class("dash-card-desc")
        box.pack_start(self.detail_label, False, False, 0)
        return box

    # ---------- 状态与按钮 ----------

    def _sync_buttons(self):
        phase = self.phase
        if phase == "type":
            self.back_btn.set_visible(False)
            self.main_btn.set_visible(True)
            self.main_btn.set_label(self._lbl("next"))
            self.main_btn.set_sensitive(bool(self.steamapps) and not self.scanning)
            if not self.steamapps:
                self.hint.set_text(self._t(
                    "未找到 Steam 库目录，请确认 Steam 已安装并至少登录过一次。",
                    "No Steam library found. Make sure Steam is installed and you have logged in once."))
            elif self.scanning:
                self.hint.set_text(self._t("正在扫描，请稍候…", "Scanning, please wait…"))
            else:
                self.hint.set_text(self._t("请选择要清理的缓存类型。",
                                           "Choose the cache type to clean."))
        elif phase == "items":
            self.back_btn.set_visible(True)
            self.back_btn.set_label(self._lbl("back"))
            self.back_btn.set_sensitive(True)
            n = len(self.picked)
            self.main_btn.set_visible(n > 0)
            self.main_btn.set_sensitive(n > 0)
            self.main_btn.set_label(self._lbl("delete"))
        elif phase == "confirm":
            self.back_btn.set_visible(True)
            self.back_btn.set_label(self._lbl("cancel"))
            self.back_btn.set_sensitive(True)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("delete"))
        elif phase == "running":
            self.back_btn.set_visible(False)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("cancel"))
        else:  # done
            self.back_btn.set_visible(False)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("done"))

    def _set_phase(self, phase, page):
        self.phase = phase
        self.stack.set_visible_child_name(page)
        self._sync_buttons()

    # ---------- 交互 ----------

    def _on_type_toggled(self, *_a):
        if not self.rb_compat.get_active():
            self.cache_type = "shadercache"
        else:
            self.cache_type = "compatdata"
        # 换类型时清掉上一轮的扫描结果，避免按钮点击后看到旧数据
        self.items = []
        self.picked = []
        self._clear_rows()

    def _on_back_clicked(self, *_a):
        if self.phase == "confirm":
            # 从确认页退回列表，保留原有勾选，方便改选
            self._show_items_page()
            return
        if self.phase == "items":
            self._set_phase("type", "type")

    def _on_main_clicked(self, *_a):
        if self.phase == "type":
            if not self.scanning:
                self._start_scan()
        elif self.phase == "items":
            self._goto_confirm()
        elif self.phase == "confirm":
            self._start_delete()
        elif self.phase == "running":
            self.cancelled = True
            self.detail_label.set_text(self._t("正在取消…", "Cancelling…"))
            p = self.cur_proc
            if p:
                try:
                    p.terminate()
                except Exception:
                    pass
        else:  # done
            self._set_phase("type", "type")
            self.items = []
            self.picked = []
            self._clear_rows()
            self.stack.set_visible_child_name("type")

    def _on_delete_event(self, *_a):
        # 删除过程中关窗：先终止 rm，避免留下半个目录还在被写
        self.cancelled = True
        p = self.cur_proc
        if p:
            try:
                p.terminate()
            except Exception:
                pass
        return False

    # ---------- 扫描 ----------

    def _start_scan(self):
        self.scanning = True
        self._sync_buttons()
        cache_type = self.cache_type

        def worker():
            try:
                items = _cm_scan(cache_type)
            except Exception:
                items = []
            GLib.idle_add(self._on_scan_done, cache_type, items)

        threading.Thread(target=worker, daemon=True).start()

    def _on_scan_done(self, cache_type, items):
        self.scanning = False
        if cache_type != self.cache_type:
            # 扫描期间用户换了类型，结果作废
            self._sync_buttons()
            return
        self.items = items
        self.picked = []
        if not items:
            self.hint.set_text(self._t("没有找到可清理的%s。"
                                       % self._type_title(cache_type),
                                       "Nothing to clean in %s."
                                       % self._type_title(cache_type).lower()))
            self._sync_buttons()
            return
        self._populate_items()
        self._show_items_page()

    def _clear_rows(self):
        for ch in list(self.list_box.get_children()):
            self.list_box.remove(ch)

    def _populate_items(self):
        self._clear_rows()
        for app_id, name, mb, path in self.items:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            cb = Gtk.CheckButton()
            cb._cm_item = (app_id, name, mb, path)
            cb.connect("toggled", self._on_item_toggled)
            title = Gtk.Label()
            shown = name or self._t("未知应用", "Unknown app")
            if not name:
                shown = "%s (%s)" % (shown, app_id)
            title.set_markup("<b>%s</b>" % GLib.markup_escape_text(shown))
            title.set_xalign(0)
            size = Gtk.Label(label=_cm_fmt_size(mb))
            size.set_xalign(1.0)
            size.get_style_context().add_class("dash-card-desc")
            row.pack_start(cb, False, False, 0)
            row.pack_start(title, True, True, 0)
            row.pack_start(size, False, False, 0)
            eb = Gtk.EventBox()
            eb.add(row)
            eb.connect("button-press-event",
                       lambda _w, _e, c=cb: (c.set_active(not c.get_active()), True)[1])
            self.list_box.pack_start(eb, False, False, 0)
        # 重建行后必须显式 show_all：窗口早已显示过，新建的行默认是隐藏的
        self.list_box.show_all()

    def _walk_checkbuttons(self):
        found = []

        def rec(w):
            if isinstance(w, Gtk.CheckButton):
                found.append(w)
                return
            if hasattr(w, "get_children"):
                for c in w.get_children():
                    rec(c)

        for ch in self.list_box.get_children():
            rec(ch)
        return found

    def _on_item_toggled(self, *_a):
        self.picked = [cb._cm_item for cb in self._walk_checkbuttons() if cb.get_active()]
        if self.phase == "items":
            self._update_items_hint()
            self._sync_buttons()

    def _update_items_hint(self):
        n = len(self.picked)
        total = sum(x[2] for x in self.picked)
        label = self._type_title()
        if n:
            self.hint.set_text(self._t(
                "共 %d 项（%s），已选 %d 项，约 %s。"
                % (len(self.items), label, n, _cm_fmt_size(total)),
                "%d entries (%s), %d selected, about %s."
                % (len(self.items), label.lower(), n, _cm_fmt_size(total))))
        else:
            self.hint.set_text(self._t(
                "共 %d 项（%s），勾选要删除的项目后点「删除所选」。"
                % (len(self.items), label),
                "%d entries (%s). Tick the ones to delete, then press Delete selected."
                % (len(self.items), label.lower())))

    def _show_items_page(self):
        self.phase = "items"
        self.stack.set_visible_child_name("items")
        self._update_items_hint()
        self._sync_buttons()


    # ---------- 确认 ----------

    def _goto_confirm(self):
        self.picked = [cb._cm_item for cb in self._walk_checkbuttons() if cb.get_active()]
        if not self.picked:
            return
        self.total_mb = sum(x[2] for x in self.picked)
        lines = []
        for app_id, name, mb, path in self.picked:
            lines.append("  • %s  (%s)" % (name or self._t("未知应用", "Unknown app"),
                                           _cm_fmt_size(mb)))
        head = self._t("将永久删除以下%s：" % self._type_title(),
                       "The following %s will be deleted permanently:"
                       % self._type_title().lower())
        tail = self._t("\n\n共 %d 项，约 %s，删除后无法恢复。"
                       % (len(self.picked), _cm_fmt_size(self.total_mb)),
                       "\n\n%d entries, about %s. This cannot be undone."
                       % (len(self.picked), _cm_fmt_size(self.total_mb)))
        text = head + "\n\n" + "\n".join(lines) + tail
        if self.cache_type == "compatdata" and _cm_steam_running():
            text += self._t("\n\n⚠ 检测到 Steam 正在运行，删除兼容数据可能损坏正在使用的 "
                            "Proton 前缀，建议先退出 Steam。",
                            "\n\n⚠ Steam is running. Deleting compatibility data may damage "
                            "Proton prefixes in use; quit Steam first.")
        self.confirm_label.set_text(text)
        self.hint.set_text(self._t("请确认要删除的内容，删除后无法恢复。",
                                   "Review what will be deleted; this cannot be undone."))
        self._set_phase("confirm", "confirm")

    # ---------- 删除 ----------

    def _start_delete(self):
        sel = list(self.picked)
        self.cancelled = False
        self.deleted = self.failed = self.freed_mb = 0
        self.prog_label.set_text(self._t("正在删除…", "Deleting…"))
        self.prog_bar.set_fraction(0)
        self.detail_label.set_text("")
        self._set_phase("running", "progress")

        def worker():
            total = len(sel)
            for i, (app_id, name, mb, path) in enumerate(sel, 1):
                if self.cancelled:
                    break
                GLib.idle_add(self._on_delete_progress, i, total, name or app_id,
                              self.freed_mb, mb)
                rc = self._rm_path(path)
                if self.cancelled:
                    break
                if rc == 0:
                    self.deleted += 1
                    self.freed_mb += mb
                else:
                    self.failed += 1
            GLib.idle_add(self._finish_delete, total)

        threading.Thread(target=worker, daemon=True).start()

    def _rm_path(self, path):
        try:
            p = subprocess.Popen(["rm", "-rf", "--", path],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.cur_proc = p
            p.wait()
            self.cur_proc = None
            return p.returncode
        except Exception:
            self.cur_proc = None
            return 1

    def _on_delete_progress(self, i, total, name, freed_done, cur_mb):
        self.prog_label.set_text(self._t("正在删除 %d/%d：%s" % (i, total, name),
                                         "Deleting %d/%d: %s" % (i, total, name)))
        self.prog_bar.set_fraction(min(1.0, (i - 1) / float(max(1, total))))
        self.detail_label.set_text(self._t(
            "已释放 %s，本项 %s" % (_cm_fmt_size(freed_done), _cm_fmt_size(cur_mb)),
            "%s freed, this item %s" % (_cm_fmt_size(freed_done), _cm_fmt_size(cur_mb))))
        return False

    def _finish_delete(self, total):
        self.prog_bar.set_fraction(1.0)
        self.prog_label.set_text("")
        if self.cancelled:
            msg = self._t("已取消：删除 %d 项，释放 %s" % (self.deleted, _cm_fmt_size(self.freed_mb)),
                          "Cancelled: %d deleted, %s freed"
                          % (self.deleted, _cm_fmt_size(self.freed_mb)))
            if self.failed:
                msg += self._t("，失败 %d 项" % self.failed, ", %d failed" % self.failed)
        elif self.failed:
            msg = self._t("清理结束：成功 %d 项，失败 %d 项，释放 %s"
                          % (self.deleted, self.failed, _cm_fmt_size(self.freed_mb)),
                          "Cleaning finished: %d succeeded, %d failed, %s freed"
                          % (self.deleted, self.failed, _cm_fmt_size(self.freed_mb)))
        else:
            msg = self._t("✓ 清理完成：删除 %d 项，释放 %s"
                          % (self.deleted, _cm_fmt_size(self.freed_mb)),
                          "✓ Cleaning done: %d deleted, %s freed"
                          % (self.deleted, _cm_fmt_size(self.freed_mb)))
        self.prog_label.set_text(msg)
        detail_parts = []
        if self.failed:
            detail_parts.append(self._t("失败项可能正被占用，请退出 Steam 后重试。",
                                        "Failed entries may be in use; quit Steam and retry."))
        if _cm_steam_running():
            detail_parts.append(self._t("建议重启 Steam 让缓存重新生成。",
                                        "Restart Steam so the caches can be rebuilt."))
        self.detail_label.set_text("\n".join(detail_parts))
        self.phase = "done"
        self.hint.set_text("")
        self._sync_buttons()

# ===== 兼容层管理（GE-Proton / Proton-CachyOS / DW Proton）=====


def _compat_install_dir():
    return os.path.join(os.path.expanduser("~"), ".local", "share", "Steam",
                        "compatibilitytools.d")


COMPAT_MIRRORS = [
    ("gh-proxy.com（国内镜像，速度快）", "gh-proxy.com (fast mirror)", "https://gh-proxy.com/"),
    ("gh.3w.pm（国内镜像，稳定）", "gh.3w.pm (mirror)", "https://gh.3w.pm/"),
    ("cors.isteed.cc（国内镜像，稳定）", "cors.isteed.cc (mirror)", "https://cors.isteed.cc/"),
    ("ghproxy.net（国内镜像，慢速备用）", "ghproxy.net (slow mirror)", "https://ghproxy.net/"),
    # 官方源用空前缀：browser_download_url 本身已是完整的 https://github.com/... 地址，
    # 若这里也写 https://github.com/ 会拼成 .../https://github.com/... 导致 404
    ("GitHub（官方源）", "GitHub (official)", ""),
]

# 三个兼容层家族的差异都收在这张表里，安装/卸载流程完全共用
COMPAT_FAMILIES = {
    "ge": {
        "repo": "GloriousEggroll/proton-ge-custom",
        "title": ("GE-Proton", "GE-Proton"),
        "ext": ".tar.gz",
        "avoid_v3": False,     # 上游不发 x86_64_v3 包，无需排除
        "per_page": 100,
        "use_tag_as_dir": True,   # 目标目录名用 release tag
        "need_vdf": False,
        "dir_re": r"^GE-Proton",
    },
    "cachyos": {
        "repo": "CachyOS/proton-cachyos",
        "title": ("Proton-CachyOS (SLR)", "Proton-CachyOS (SLR)"),
        "ext": ".tar.xz",
        "avoid_v3": True,      # Deck 用普通 x86_64，不要 v3 变体
        "per_page": 50,
        "use_tag_as_dir": False,  # 目标目录名用资源名（tag 与资源名不一致）
        "need_vdf": True,
        "dir_re": r"proton-cachyos|cachyos",
    },
    "dw": {
        "repo": "dawn-winery/dwproton-mirror",
        "title": ("DW Proton", "DW Proton"),
        "ext": ".tar.xz",
        "avoid_v3": True,
        "per_page": 50,
        "use_tag_as_dir": False,
        "need_vdf": True,
        "dir_re": r"dwproton|dw-proton",
    },
}


def _compat_resp_socket(resp):
    """从 HTTPResponse 里挖出底层 socket，用于取消时 interrupt 阻塞读。

    结构是 http.client.HTTPResponse -> fp(BufferedReader) -> raw(HTTPResponse 的
    SocketIO) -> _sock。拿不到就返回 None（取消会退化为轮询，慢但不至于出错）。
    """
    try:
        return resp.fp.raw._sock
    except AttributeError:
        return None


class _CompatCancelled(Exception):
    pass


def _compat_open(url, timeout=25, owner=None, accept=None):
    """GET 一个 URL，返回 HTTPResponse；owner 存在时登记底层 socket。

    取消时 owner._abort_download() 会对这个 socket 做 shutdown，让阻塞中的
    read/read1 立刻抛 OSError。urlopen 本身没有取消接口，这是唯一可靠的打断
    方式（实测 0.1 毫秒生效；而 close() 只关本地文件对象，要等缓冲读完）。
    """
    headers = {"User-Agent": "steamdeck-toolbox"}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=timeout)
    if owner is not None:
        owner._track_resp(resp)
    return resp


def _compat_api(url, timeout=25, owner=None):
    """取 GitHub API 的 JSON。owner 传入窗口时，取消可以打断阻塞读。"""
    resp = _compat_open(url, timeout=timeout, owner=owner,
                        accept="application/vnd.github+json")
    try:
        raw = resp.read()
    except OSError:
        if owner is not None and getattr(owner, "cancelled", False):
            raise _CompatCancelled()
        raise
    finally:
        if owner is not None:
            owner._untrack()
        try:
            resp.close()
        except Exception:
            pass
    return json.loads(raw.decode("utf-8", "replace"))


def _compat_mirror_order(primary):
    """要尝试的镜像顺序：用户选的那个优先，其余按表内顺序兜底。

    弱网下最常见的失败是连不上、下到一半断、拿到的内容不对；换源比重试同一个
    源有效得多，所以这里永远返回全部镜像。
    """
    first = [m for m in COMPAT_MIRRORS if m[2] == primary]
    rest = [m for m in COMPAT_MIRRORS if m[2] != primary]
    return first + rest


def _compat_fetch_tags(family, owner=None):
    """取某个兼容层家族的全部可用版本 tag（新的在前）。"""
    fam = COMPAT_FAMILIES[family]
    url = ("https://api.github.com/repos/%s/releases?per_page=%d"
           % (fam["repo"], fam["per_page"]))
    data = _compat_api(url, owner=owner)
    tags = []
    for rel in data or []:
        tag = rel.get("tag_name") or ""
        if not tag:
            continue
        if family == "ge":
            if tag.startswith("GE-Proton"):
                tags.append(tag)
        elif rel.get("prerelease"):
            continue
        elif family == "cachyos":
            # tag 形如 cachyos-11.0-20261015-slr
            if "slr" in tag.lower() and any(ch.isdigit() for ch in tag):
                tags.append(tag)
        else:
            if tag.lower().startswith("dwproton") and any(ch.isdigit() for ch in tag):
                tags.append(tag)
    return tags


def _compat_installed(family):
    """已安装目录名列表（按名字排序）。"""
    fam = COMPAT_FAMILIES[family]
    d = _compat_install_dir()
    out = []
    if not os.path.isdir(d):
        return out
    pat = re.compile(fam["dir_re"], re.I)
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if not os.path.isdir(p) or name.startswith(".stage."):
            continue
        if family == "ge":
            # 旧实现按 GE-Proton* 判断，不校验 vdf（GE 包里确实带 vdf，但保持一致）
            if pat.match(name):
                out.append(name)
            continue
        if not os.path.isfile(os.path.join(p, "compatibilitytool.vdf")):
            continue
        if pat.search(name):
            out.append(name)
    return out


def _compat_already_installed(family, tag, installed):
    """判断某个 tag 是否已经装过（三家判定规则不同）。"""
    if family == "ge":
        return tag in installed
    if family == "cachyos":
        # tag cachyos-11.0-20261015-slr → 资源名含 11.0-20261015-slr-x86_64
        stem = tag.split("-", 1)[1] if "-" in tag else tag
        return any(stem in inst for inst in installed)
    return any(tag in inst for inst in installed)


def _compat_pick_asset(assets, ext, avoid_v3=True):
    """从 release assets 里挑适合 Deck 的包（x86_64，排除 arm64/aarch64/v3）。"""
    def ok(name, strict):
        low = name.lower()
        if not low.endswith(ext):
            return False
        if "arm64" in low or "aarch64" in low:
            return False
        if strict:
            if "x86_64" not in low:
                return False
            if avoid_v3 and "x86_64_v3" in low:
                return False
        return True

    for strict in (True, False):
        for a in assets or []:
            if ok(a.get("name", "") or "", strict):
                return a
    return None


def _compat_sha_asset(assets, asset_name):
    """找安装包对应的 .sha512sum 下载地址（两种命名都试）。"""
    ext = None
    for cand in (".tar.gz", ".tar.xz"):
        if asset_name.endswith(cand):
            ext = cand
            break
    wants = []
    if ext:
        wants.append(asset_name[: -len(ext)] + ".sha512sum")
        wants.append(asset_name + ".sha512sum")
    else:
        wants.append(asset_name + ".sha512sum")
    for a in assets or []:
        if (a.get("name") or "") in wants:
            return a.get("browser_download_url") or ""
    return ""


def _compat_stem(name, ext):
    return name[: -len(ext)] if name.endswith(ext) else name


def _compat_bytes(n):
    try:
        n = float(n)
    except Exception:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%.0f %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0
    return "?"


class CompatManagerWindow(Gtk.Window):
    """兼容层管理：GE-Proton / Proton-CachyOS(SLR) / DW Proton 的安装与卸载。

    与旧的 zenity 版本相比，下载/校验/解压全部在 Python 里完成：
    进度是真实字节进度（旧版只有 pulsate 动画），取消能立刻中断下载。
    """

    def __init__(self, parent=None):
        super().__init__(title=fl("ge_proton_manager"))
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(660, 560)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT if parent
                          else Gtk.WindowPosition.CENTER)
        if parent:
            self.set_transient_for(parent)
        self.set_deletable(True)

        self.phase = "type"        # type / list / confirm / running / done
        self.family = "ge"
        self.action = "install"
        self.versions = []         # 列表页要展示的条目
        self.picked = []
        self.loading = False
        self.cancelled = False
        self.mirror = ""           # 镜像前缀，官方源为空串
        self.batch_ok = 0
        self.batch_fail = 0
        self.failed_list = []
        self._last_ui = 0.0
        self._last_pct = -1.0
        self._dl_resp = None      # 正在下载的响应对象
        self._dl_sock = None      # 它的底层 socket，取消时 shutdown 打断阻塞读

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        head.set_margin_top(14); head.set_margin_bottom(8)
        head.set_margin_start(16); head.set_margin_end(16)
        title = Gtk.Label()
        title.set_markup("<span size='large'><b>%s</b></span>"
                         % GLib.markup_escape_text(fl("ge_proton_manager")))
        title.set_xalign(0)
        head.pack_start(title, True, True, 0)
        outer.pack_start(head, False, False, 0)

        self.hint = Gtk.Label()
        self.hint.set_xalign(0); self.hint.set_line_wrap(True)
        self.hint.set_margin_start(16); self.hint.set_margin_end(16)
        self.hint.set_margin_bottom(8)
        self.hint.get_style_context().add_class("dash-card-desc")
        outer.pack_start(self.hint, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(160)
        self.stack.set_margin_start(16); self.stack.set_margin_end(16)
        outer.pack_start(self.stack, True, True, 0)
        self.stack.add_named(self._build_type_page(), "type")
        self.stack.add_named(self._build_list_page(), "list")
        self.stack.add_named(self._build_confirm_page(), "confirm")
        self.stack.add_named(self._build_progress_page(), "progress")

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_row.set_margin_top(10); btn_row.set_margin_bottom(14)
        btn_row.set_margin_start(16); btn_row.set_margin_end(16)
        self.back_btn = Gtk.Button(label=self._lbl("back"))
        self.back_btn.connect("clicked", self._on_back_clicked)
        btn_row.pack_start(self.back_btn, False, False, 0)
        self.main_btn = Gtk.Button(label=self._lbl("next"))
        self.main_btn.get_style_context().add_class("suggested-action")
        self.main_btn.connect("clicked", self._on_main_clicked)
        btn_row.pack_end(self.main_btn, False, False, 0)
        outer.pack_start(btn_row, False, False, 0)

        self.add(outer)
        self.connect("delete-event", self._on_delete_event)
        self.show_all()
        self.present()
        self._sync_buttons()

    # ---------- 文案 ----------

    def _lbl(self, key):
        m = {
            "next":      ("下一步", "Next"),
            "install":   ("安装所选", "Install selected"),
            "uninstall": ("卸载所选", "Uninstall selected"),
            "start":     ("开始安装", "Start install"),
            "startrem":  ("开始卸载", "Start uninstall"),
            "cancel":    ("取消", "Cancel"),
            "back":      ("返回", "Back"),
            "done":      ("完成", "Done"),
        }
        zh, en = m[key]
        return en if get_lang() == "en" else zh

    def _t(self, zh, en):
        return en if get_lang() == "en" else zh

    def _family_title(self, family=None):
        zh, en = COMPAT_FAMILIES[family or self.family]["title"]
        return en if get_lang() == "en" else zh

    def _family_note(self, family):
        if family == "dw":
            return self._t("DW Proton 偏二次元与特定游戏；外挂请用独立的 CheatDeck 插件入口。",
                           "DW Proton targets anime/specific games; use the CheatDeck "
                           "plugin entry for trainers.")
        if family == "cachyos":
            return self._t("CachyOS 提供的 SLR 兼容层，使用普通 x86_64 包（不用 v3 变体）。",
                           "SLR builds from CachyOS, using the plain x86_64 package "
                           "(not the v3 variant).")
        return self._t("安装到 compatibilitytools.d，可与 Steam 自带的 Proton 并存。",
                       "Installed into compatibilitytools.d alongside Steam's built-in Proton.")

    # ---------- 页面构建 ----------

    def _build_type_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_valign(Gtk.Align.START)
        first = None
        self._op_radios = []
        for fam_key, act in (("ge", "install"), ("ge", "uninstall"),
                             ("cachyos", "install"), ("cachyos", "uninstall"),
                             ("dw", "install"), ("dw", "uninstall")):
            if act == "install":
                verb = self._t("安装", "Install")
            else:
                verb = self._t("卸载", "Uninstall")
            label = "%s：%s" % (self._family_title(fam_key), verb)
            if first is None:
                rb = Gtk.RadioButton.new_with_label_from_widget(None, label)
                first = rb
            else:
                rb = Gtk.RadioButton.new_with_label_from_widget(first, label)
            rb.set_margin_top(6)
            rb.set_halign(Gtk.Align.START)
            rb.connect("toggled", self._on_op_toggled, fam_key, act)
            box.pack_start(rb, False, False, 0)
            self._op_radios.append((rb, fam_key, act))
        return box

    def _build_list_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        sw.add(self.list_box)
        box.pack_start(sw, True, True, 0)
        return box

    def _build_confirm_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_valign(Gtk.Align.FILL)
        self.confirm_label = Gtk.Label()
        self.confirm_label.set_xalign(0); self.confirm_label.set_line_wrap(True)
        self.confirm_label.set_valign(Gtk.Align.START)
        sw.add(self.confirm_label)
        box.pack_start(sw, True, True, 0)

        # 镜像源只在安装时出现
        self.mirror_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        mlbl = Gtk.Label(label=self._t("下载镜像源（所有版本共用）",
                                       "Download mirror (shared by all versions)"))
        mlbl.set_xalign(0)
        mlbl.get_style_context().add_class("dash-card-title")
        self.mirror_box.pack_start(mlbl, False, False, 0)
        mfirst = None
        self._mirror_radios = []
        for zh, en, prefix in COMPAT_MIRRORS:
            label = en if get_lang() == "en" else zh
            if mfirst is None:
                rb = Gtk.RadioButton.new_with_label_from_widget(None, label)
                mfirst = rb
            else:
                rb = Gtk.RadioButton.new_with_label_from_widget(mfirst, label)
            rb.set_halign(Gtk.Align.START)
            if prefix == "":
                rb.set_active(True)   # 默认官方源，和旧版首次点击即官方一致
            rb.connect("toggled", self._on_mirror_toggled, prefix)
            self.mirror_box.pack_start(rb, False, False, 0)
            self._mirror_radios.append(rb)
        box.pack_start(self.mirror_box, False, False, 0)
        return box

    def _build_progress_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_valign(Gtk.Align.CENTER)
        self.prog_label = Gtk.Label(label="")
        self.prog_label.set_xalign(0); self.prog_label.set_line_wrap(True)
        self.prog_label.get_style_context().add_class("dash-card-title")
        box.pack_start(self.prog_label, False, False, 0)
        self.prog_bar = Gtk.ProgressBar()
        self.prog_bar.set_show_text(False)
        box.pack_start(self.prog_bar, False, False, 0)
        self.detail_label = Gtk.Label(label="")
        self.detail_label.set_xalign(0); self.detail_label.set_line_wrap(True)
        self.detail_label.get_style_context().add_class("dash-card-desc")
        box.pack_start(self.detail_label, False, False, 0)
        return box

    # ---------- 状态与按钮 ----------

    def _sync_buttons(self):
        phase = self.phase
        if phase == "type":
            self.back_btn.set_visible(False)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            # 获取版本列表时按钮变「取消」：弱网下这个请求可能挂满 25 秒超时，
            # 不让点会让人以为窗口卡死
            self.main_btn.set_label(self._lbl("cancel") if self.loading
                                    else self._lbl("next"))
            if not self.loading:
                self.hint.set_text(self._t("选择要管理的兼容层与操作。",
                                           "Choose the compatibility layer and action."))
        elif phase == "list":
            self.back_btn.set_visible(True)
            self.back_btn.set_label(self._lbl("back"))
            self.back_btn.set_sensitive(not self.loading)
            n = len(self.picked)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(bool(n) and not self.loading)
            if self.action == "install":
                self.main_btn.set_label(self._lbl("install"))
            else:
                self.main_btn.set_label(self._lbl("uninstall"))
        elif phase == "confirm":
            self.back_btn.set_visible(True)
            self.back_btn.set_label(self._lbl("back"))
            self.back_btn.set_sensitive(True)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("start") if self.action == "install"
                                    else self._lbl("startrem"))
        elif phase == "running":
            self.back_btn.set_visible(False)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("cancel"))
        else:  # done
            self.back_btn.set_visible(False)
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("done"))

    def _set_phase(self, phase, page):
        self.phase = phase
        self.stack.set_visible_child_name(page)
        self._sync_buttons()

    # ---------- 交互 ----------

    def _on_op_toggled(self, rb, family, act):
        if not rb.get_active():
            return
        self.family = family
        self.action = act
        self.versions = []
        self.picked = []
        self._clear_rows()
        self.hint.set_text(self._family_note(family))

    def _on_mirror_toggled(self, rb, prefix):
        if rb.get_active():
            self.mirror = prefix

    def _on_back_clicked(self, *_a):
        if self.phase == "confirm":
            self._set_phase("list", "list")
            self._update_list_hint()
            return
        if self.phase == "list":
            self.picked = []
            self._set_phase("type", "type")

    def _on_main_clicked(self, *_a):
        if self.phase == "type":
            if self.loading:
                self.cancelled = True
                self.hint.set_text(self._t("正在取消…", "Cancelling…"))
                self._abort_download()
            else:
                self._start_load()
        elif self.phase == "list":
            self._goto_confirm()
        elif self.phase == "confirm":
            self._start_batch()
        elif self.phase == "running":
            self.cancelled = True
            self.detail_label.set_text(self._t("正在取消…", "Cancelling…"))
            self._abort_download()
        else:  # done
            if self.cancelled and self.versions:
                # 取消后回到版本列表，勾选还在，可以换镜像/换版本重试
                self.cancelled = False
                self._set_phase("list", "list")
                self._update_list_hint()
                return
            self.cancelled = False
            self.picked = []
            self._clear_rows()
            self._set_phase("type", "type")

    def _on_delete_event(self, *_a):
        self.cancelled = True
        self._abort_download()
        return False

    def _track_resp(self, resp):
        """登记当前响应与它的底层 socket，供取消时 shutdown 打断。"""
        self._dl_resp = resp
        self._dl_sock = _compat_resp_socket(resp)

    def _untrack(self):
        self._dl_resp = None
        self._dl_sock = None

    def _abort_download(self):
        """取消时打断正在阻塞的网络读。

        close() 没用：HTTPResponse.close() 只关本地文件对象，不会打断已经在
        recv 里的读（实测要等 17 秒把缓冲读完）。真正有效的是对底层 socket
        做 shutdown(SHUT_RDWR)，实测 0.1 毫秒内让 read1 抛 BrokenPipeError。

        下载、取 sha512sum、取 GitHub API 三条路径都会登记 socket，所以
        "获取下载信息" 阶段点取消也能立刻停住，不会卡在「正在取消…」。
        """
        sock = self._dl_sock
        if sock is None:
            return
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    # ---------- 版本列表 ----------

    def _start_load(self):
        # 每次加载都重置取消态：上一次取消留下的 True 会让本轮直接判为已取消
        self.cancelled = False
        self.loading = True
        self._sync_buttons()
        family, action = self.family, self.action
        self.prog_label.set_text(self._t("正在获取版本列表…", "Fetching version list…"))
        self.prog_bar.set_fraction(0)
        self.detail_label.set_text("")
        self.hint.set_text(self._t("正在获取版本列表…", "Fetching version list…"))

        def worker():
            items = []
            err = ""
            try:
                if action == "install":
                    installed = _compat_installed(family)
                    items = [t for t in _compat_fetch_tags(family, owner=self)
                             if not _compat_already_installed(family, t, installed)]
                else:
                    items = _compat_installed(family)
            except Exception as e:
                err = str(e) or e.__class__.__name__
            GLib.idle_add(self._on_load_done, family, action, items, err)

        threading.Thread(target=worker, daemon=True).start()

    def _on_load_done(self, family, action, items, err):
        self.loading = False
        if family != self.family or action != self.action:
            # 加载期间用户换了选项，结果作废
            self._sync_buttons()
            return
        if self.cancelled:
            # 用户主动取消，不是网络错误；留在类型页让他重新选
            self.cancelled = False
            self._sync_buttons()
            # 取消提示要写在 _sync_buttons 之后，否则会被那里的默认文案盖掉
            self.hint.set_text(self._t("已取消获取版本列表。",
                                       "Cancelled fetching the version list."))
            return
        if err:
            self.hint.set_text(self._t("无法获取版本列表：%s\n请检查网络后重试。" % err,
                                       "Cannot fetch the version list: %s\n"
                                       "Check your network and try again." % err))
            self._sync_buttons()
            return
        self.versions = items
        self.picked = []
        self._clear_rows()
        if not items:
            if action == "install":
                self.hint.set_text(self._t("所有版本都已安装。",
                                           "Every version is already installed."))
            else:
                self.hint.set_text(self._t("未检测到已安装的%s。"
                                           % self._family_title(family),
                                           "No installed %s found."
                                           % self._family_title(family)))
            self._set_phase("list", "list")
            return
        self._populate_rows()
        self._set_phase("list", "list")
        self._update_list_hint()

    def _clear_rows(self):
        for ch in list(self.list_box.get_children()):
            self.list_box.remove(ch)

    def _populate_rows(self):
        self._clear_rows()
        for ver in self.versions:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            cb = Gtk.CheckButton()
            cb._compat_item = ver
            cb.connect("toggled", self._on_item_toggled)
            title = Gtk.Label()
            title.set_markup("<b>%s</b>" % GLib.markup_escape_text(ver))
            title.set_xalign(0)
            row.pack_start(cb, False, False, 0)
            row.pack_start(title, True, True, 0)
            eb = Gtk.EventBox()
            eb.add(row)
            eb.connect("button-press-event",
                       lambda _w, _e, c=cb: (c.set_active(not c.get_active()), True)[1])
            self.list_box.pack_start(eb, False, False, 0)
        # 重建行后必须显式 show_all：窗口早已显示过，新建的行默认隐藏
        self.list_box.show_all()

    def _walk_checkbuttons(self):
        found = []

        def rec(w):
            if isinstance(w, Gtk.CheckButton):
                found.append(w)
                return
            if hasattr(w, "get_children"):
                for c in w.get_children():
                    rec(c)

        for ch in self.list_box.get_children():
            rec(ch)
        return found

    def _collect_picked(self):
        self.picked = [cb._compat_item for cb in self._walk_checkbuttons()
                       if cb.get_active()]
        return self.picked

    def _on_item_toggled(self, *_a):
        self._collect_picked()
        if self.phase == "list":
            self._update_list_hint()
            self._sync_buttons()

    def _update_list_hint(self):
        n = len(self.picked)
        name = self._family_title()
        total = len(self.versions)
        if self.action == "install":
            if n:
                self.hint.set_text(self._t(
                    "%s：共 %d 个版本可安装，已选 %d 个。"
                    % (name, total, n),
                    "%s: %d versions available, %d selected." % (name, total, n)))
            else:
                self.hint.set_text(self._t(
                    "%s：共 %d 个版本可安装，勾选后点「安装所选」。"
                    % (name, total),
                    "%s: %d versions available. Tick the ones to install."
                    % (name, total)))
        else:
            if n:
                self.hint.set_text(self._t(
                    "%s：共 %d 个已安装，已选 %d 个。"
                    % (name, total, n),
                    "%s: %d installed, %d selected." % (name, total, n)))
            else:
                self.hint.set_text(self._t(
                    "%s：共 %d 个已安装，勾选后点「卸载所选」。"
                    % (name, total),
                    "%s: %d installed. Tick the ones to remove."
                    % (name, total)))

    # ---------- 确认 ----------

    def _goto_confirm(self):
        picked = self._collect_picked()
        if not picked:
            return
        verb = self._t("安装", "install") if self.action == "install" \
            else self._t("卸载", "remove")
        head = self._t("将%s以下 %d 个版本：" % (verb, len(picked)),
                       "%s the following %d version(s):" % (verb.capitalize(), len(picked)))
        lines = ["  • %s" % v for v in picked]
        text = head + "\n\n" + "\n".join(lines)
        if self.action == "install":
            text += self._t("\n\n将下载到 compatibilitytools.d，完成后重启 Steam 生效。",
                            "\n\nThey will be downloaded into compatibilitytools.d; "
                            "restart Steam afterwards.")
        else:
            text += self._t("\n\n目录会被永久删除，删除后无法恢复。",
                            "\n\nThe directories are deleted permanently.")
        self.confirm_label.set_text(text)
        self.mirror_box.set_visible(self.action == "install")
        self.hint.set_text(self._t("请确认后继续。", "Review and continue."))
        self._set_phase("confirm", "confirm")

    # ---------- 执行 ----------

    def _start_batch(self):
        sel = list(self._collect_picked())
        if not sel:
            return
        self.cancelled = False
        self.batch_ok = 0
        self.batch_fail = 0
        self.failed_list = []
        self._last_ui = 0.0
        self._last_pct = -1.0
        self.prog_bar.set_fraction(0)
        self.prog_label.set_text(self._t("准备中…", "Preparing…"))
        self.detail_label.set_text("")
        self.hint.set_text("")
        self._set_phase("running", "progress")
        if self.action == "install":
            threading.Thread(target=self._run_install, args=(sel, self.mirror),
                             daemon=True).start()
        else:
            threading.Thread(target=self._run_uninstall, args=(sel,),
                             daemon=True).start()

    # ---------- 进度回调（线程安全） ----------

    def _ui(self, idx, total, text, inner, detail=None, force=False):
        """从后台线程更新进度；字节级回调太密集，按时间/百分比节流。"""
        now = time.time()
        if not force and now - self._last_ui < 0.12:
            return
        self._last_ui = now
        GLib.idle_add(self._apply_progress, idx, total, text, inner, detail)

    def _apply_progress(self, idx, total, text, inner, detail):
        overall = ((idx - 1) + max(0.0, min(1.0, inner))) / float(max(1, total))
        self.prog_bar.set_fraction(min(1.0, overall))
        self.prog_label.set_text(text or "")
        if detail is not None:
            self.detail_label.set_text(detail)
        return False

    # ---------- 安装 ----------

    def _run_install(self, versions, mirror):
        total = len(versions)
        for i, ver in enumerate(versions, 1):
            if self.cancelled:
                break
            try:
                self._install_one(ver, mirror, i, total)
                self.batch_ok += 1
            except _CompatCancelled:
                break
            except Exception as e:
                self.batch_fail += 1
                self.failed_list.append((ver, str(e) or e.__class__.__name__))
        GLib.idle_add(self._finish_batch, total)

    def _install_one(self, ver, mirror, idx, total):
        fam = COMPAT_FAMILIES[self.family]
        repo = fam["repo"]
        ext = fam["ext"]

        self._ui(idx, total, self._t("正在获取 %s 的下载信息…" % ver,
                                     "Fetching download info for %s…" % ver),
                 0.0, "", force=True)
        rel = self._api_with_retry("https://api.github.com/repos/%s/releases/tags/%s"
                                   % (repo, urllib.parse.quote(ver)))
        assets = rel.get("assets") or []
        pick = _compat_pick_asset(assets, ext, fam.get("avoid_v3", True))
        if not pick:
            raise RuntimeError(self._t("这个版本没有适合 Deck 的 x86_64 安装包",
                                       "No x86_64 package suitable for Deck"))
        asset_name = pick.get("name") or ""
        dl_url = pick.get("browser_download_url") or ""
        asset_size = int(pick.get("size") or 0)
        if not dl_url:
            raise RuntimeError(self._t("拿不到下载地址", "No download URL"))
        sha_url = _compat_sha_asset(assets, asset_name)
        dest_name = ver if fam["use_tag_as_dir"] else _compat_stem(asset_name, ext)
        if self.cancelled:
            raise _CompatCancelled()

        tmpdir = tempfile.mkdtemp(prefix="compat_dl_")
        stage = None
        try:
            local = os.path.join(tmpdir, asset_name)
            # 下载 + 校验交给 _fetch_package：它负责逐个镜像重试
            self._fetch_package(ver, dl_url, sha_url, local, asset_size,
                                mirror, idx, total)

            self._ui(idx, total, self._t("正在解压 %s…" % ver, "Extracting %s…" % ver),
                     0.93, "", force=True)
            install_dir = _compat_install_dir()
            os.makedirs(install_dir, exist_ok=True)
            stage = tempfile.mkdtemp(prefix=".stage.", dir=install_dir)
            self._extract(local, stage)
            top = self._locate_extracted(stage, ver, fam)
            if top is None:
                raise RuntimeError(self._t("压缩包结构异常，未找到版本目录",
                                           "unexpected archive layout, version dir not found"))
            dest = os.path.join(install_dir, dest_name)
            if os.path.isdir(dest):
                shutil.rmtree(dest, ignore_errors=True)
            shutil.move(top, dest)
            if not os.path.isdir(dest):
                raise RuntimeError(self._t("移动到目标目录失败", "move into place failed"))
            self._ui(idx, total, self._t("%s 安装完成" % ver, "%s installed" % ver),
                     1.0, "", force=True)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
            if stage:
                shutil.rmtree(stage, ignore_errors=True)

    def _api_with_retry(self, url):
        """GitHub API 不走镜像，失败就再试一次（限速和抖动都很常见）。"""
        last = None
        for attempt in (0, 1):
            if self.cancelled:
                raise _CompatCancelled()
            try:
                return _compat_api(url, timeout=20, owner=self)
            except _CompatCancelled:
                raise
            except Exception as e:
                last = e
                if self.cancelled:
                    raise _CompatCancelled()
                if attempt == 0:
                    time.sleep(1.2)
        raise RuntimeError(self._t("获取版本信息失败：%s" % (str(last) or "网络错误"),
                                   "cannot fetch release info: %s"
                                   % (str(last) or "network error")))

    def _fetch_package(self, ver, dl_url, sha_url, local, asset_size,
                       mirror, idx, total):
        """按镜像顺序抓包并校验：一个源失败就换下一个，全都失败才报错。

        用户选的源优先，其余源按 COMPAT_MIRRORS 顺序兜底。下载不完整、sha512
        对不上都算这个源失败——镜像返回错误内容是真实存在的情况。
        """
        order = _compat_mirror_order(mirror)
        reasons = []
        for i, (zh, en, prefix) in enumerate(order):
            if self.cancelled:
                raise _CompatCancelled()
            mname = en if get_lang() == "en" else zh
            if i:
                self._ui(idx, total,
                         self._t("换用镜像 %s 重试…" % mname,
                                 "Retrying with mirror %s…" % mname),
                         0.0, "", force=True)
            try:
                self._download(prefix + dl_url, os.path.join(
                    os.path.dirname(local), os.path.basename(local)),
                    idx, total, ver, asset_size, mname)
                if self.cancelled:
                    raise _CompatCancelled()
                got = os.path.getsize(local)
                if asset_size and got != asset_size:
                    raise RuntimeError(self._t("下载不完整（%s / %s 字节）"
                                               % (got, asset_size),
                                               "incomplete download (%s / %s bytes)"
                                               % (got, asset_size)))
                self._ui(idx, total,
                         self._t("正在校验 %s…" % ver, "Verifying %s…" % ver),
                         0.88, "", force=True)
                if sha_url:
                    want = self._fetch_sha(prefix + sha_url, mname)
                    if want:
                        got_sha = self._sha512(local)
                        if got_sha and got_sha.lower() != want.lower():
                            raise RuntimeError(self._t("sha512 校验失败，包已损坏",
                                                       "sha512 mismatch, package corrupted"))
                if self.cancelled:
                    raise _CompatCancelled()
                return
            except _CompatCancelled:
                raise
            except Exception as e:
                if self.cancelled:
                    raise _CompatCancelled()
                reasons.append((mname, str(e) or e.__class__.__name__))
        if len(reasons) == 1:
            raise RuntimeError(reasons[0][1])
        raise RuntimeError(self._t(
            "所有镜像源都失败：%s"
            % "；".join("%s：%s" % (n, w) for n, w in reasons),
            "all mirrors failed: %s"
            % "; ".join("%s: %s" % (n, w) for n, w in reasons)))

    def _download(self, url, dest, idx, total, ver, expect, mname=""):
        try:
            return self._download_inner(url, dest, idx, total, ver, expect, mname)
        finally:
            self._untrack()

    def _download_inner(self, url, dest, idx, total, ver, expect, mname=""):
        resp = _compat_open(url, timeout=60, owner=self)
        done = 0
        try:
            length = int(resp.headers.get("Content-Length") or 0) or expect
            with open(dest, "wb") as f:
                while True:
                    if self.cancelled:
                        raise _CompatCancelled()
                    # read1：有多少读多少，不会为了凑满缓冲区一直等。
                    # 本机弱网时 read(262144) 会阻塞几十秒，取消要等半分钟才生效。
                    try:
                        chunk = resp.read1(65536)
                    except AttributeError:
                        chunk = resp.read(65536)
                    except OSError:
                        if self.cancelled:
                            raise _CompatCancelled()
                        raise
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    inner = (done / float(length)) * 0.85 if length else 0.0
                    if mname:
                        label = self._t("正在从 %s 下载 %s…" % (mname, ver),
                                        "Downloading %s from %s…" % (ver, mname))
                    else:
                        label = self._t("正在下载 %s…" % ver,
                                        "Downloading %s…" % ver)
                    self._ui(idx, total, label, inner,
                             "%s / %s" % (_compat_bytes(done),
                                          _compat_bytes(length) if length else "?"))
        finally:
            self._untrack()
            try:
                resp.close()
            except Exception:
                pass
        return done

    def _fetch_sha(self, url, mname=""):
        """取 .sha512sum 里的那串摘要；取不到返回空串（不影响安装，只是跳过校验）。"""
        try:
            resp = _compat_open(url, timeout=60, owner=self)
        except _CompatCancelled:
            raise
        except Exception:
            return ""
        try:
            text = resp.read().decode("utf-8", "replace").strip()
        except OSError:
            if self.cancelled:
                raise _CompatCancelled()
            return ""
        except Exception:
            return ""
        finally:
            self._untrack()
            try:
                resp.close()
            except Exception:
                pass
        parts = text.split()
        first = parts[0] if parts else ""
        return first if len(first) == 128 else ""

    def _sha512(self, path):
        try:
            h = hashlib.sha512()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _extract(self, archive, stage):
        try:
            with tarfile.open(archive, "r:*") as tf:
                try:
                    tf.extractall(stage, filter="tar")
                except TypeError:
                    # Python < 3.12 没有 filter 参数
                    tf.extractall(stage)
        except Exception as e:
            raise RuntimeError(self._t("解压失败：%s" % (str(e) or "未知错误"),
                                       "extraction failed: %s" % (str(e) or "unknown")))

    def _locate_extracted(self, stage, ver, fam):
        """定位解压出的顶层目录。

        GE-Proton11-4 起包内顶层目录带 -x86_64 后缀（与 tag 不同名），
        所以先取唯一的顶层目录，再按 tag 前缀 / compatibilitytool.vdf 兜底。
        """
        entries = [os.path.join(stage, n) for n in os.listdir(stage)]
        dirs = [p for p in entries if os.path.isdir(p)]
        if fam.get("need_vdf"):
            cands = [p for p in dirs
                     if os.path.isfile(os.path.join(p, "compatibilitytool.vdf"))]
            if len(cands) == 1:
                return cands[0]
            # 兜底：往下找一层
            for p in dirs:
                for sub in os.listdir(p):
                    sp = os.path.join(p, sub)
                    if os.path.isfile(os.path.join(sp, "compatibilitytool.vdf")):
                        return sp
            return None
        if len(dirs) == 1:
            return dirs[0]
        for p in dirs:
            base = os.path.basename(p)
            if base == ver or base.startswith(ver):
                return p
        return None

    # ---------- 卸载 ----------

    def _run_uninstall(self, names):
        total = len(names)
        install_dir = _compat_install_dir()
        for i, name in enumerate(names, 1):
            if self.cancelled:
                break
            path = os.path.join(install_dir, name)
            self._ui(i, total, self._t("正在删除 %s…" % name, "Removing %s…" % name),
                     (i - 1) / float(max(1, total)), "", force=True)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                if os.path.isdir(path):
                    self.batch_fail += 1
                    self.failed_list.append((name, self._t("删除失败，可能仍被占用",
                                                           "delete failed, maybe in use")))
                else:
                    self.batch_ok += 1
            except Exception as e:
                self.batch_fail += 1
                self.failed_list.append((name, str(e) or e.__class__.__name__))
            time.sleep(0.05)
        GLib.idle_add(self._finish_batch, total)

    # ---------- 收尾 ----------

    def _finish_batch(self, total):
        self.prog_bar.set_fraction(1.0)
        act_zh = "安装" if self.action == "install" else "卸载"
        act_en = "install" if self.action == "install" else "uninstall"
        if self.cancelled:
            msg = self._t("已取消：取消前完成 %d 个" % self.batch_ok,
                          "Cancelled: %d finished before cancelling" % self.batch_ok)
            if self.batch_fail:
                msg += self._t("，失败 %d 个" % self.batch_fail,
                               ", %d failed" % self.batch_fail)
        elif self.batch_fail:
            msg = self._t("%s结束：成功 %d 个，失败 %d 个" % (act_zh, self.batch_ok,
                                                            self.batch_fail),
                          "%s finished: %d ok, %d failed"
                          % (act_en.capitalize(), self.batch_ok, self.batch_fail))
        else:
            msg = self._t("✓ %s完成：成功 %d 个" % (act_zh, self.batch_ok),
                          "✓ %s done: %d ok" % (act_en.capitalize(), self.batch_ok))
        self.prog_label.set_text(msg)

        details = []
        for ver, why in self.failed_list[:8]:
            details.append("· %s：%s" % (ver, why))
        if len(self.failed_list) > 8:
            details.append(self._t("…另有 %d 个失败项"
                                   % (len(self.failed_list) - 8),
                                   "…and %d more failed" % (len(self.failed_list) - 8)))
        if self.batch_ok:
            details.append(self._t("建议完全退出并重启 Steam 以刷新兼容层列表。",
                                   "Fully restart Steam so the list refreshes."))
        self.detail_label.set_text("\n".join(details))
        self.phase = "done"
        self.hint.set_text("")
        self._sync_buttons()



class FlatpakInstallWindow(Gtk.Window):
    """安装 Flatpak 应用：勾选 → 安装 → 进度 → 结果，全部在一个窗口里。"""

    def __init__(self, parent=None):
        super().__init__(title=fl("install_flatpak_apps_gui"))
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(620, 520)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT if parent else Gtk.WindowPosition.CENTER)
        if parent:
            self.set_transient_for(parent)
        self.set_deletable(True)

        self.proc = None          # 当前 flatpak 进程（供取消时 terminate）
        self.proc_pgid = None     # 进程组 id（start_new_session 后 = pid）
        self.phase = "select"     # select / running / done
        self.cancelled = False
        self.installed, self._fp_install_err = _fp_installed_ids()
        self._fp_search_err = ""
        self.queue = []           # 待安装的 (id, desk_name, cat, addon)
        self.queue_total = 0
        self.done_count = 0
        self.fail_count = 0
        self.failed = []
        self.last_inner = 0
        self.last_error = ""      # 最近一条可读的错误（来自 flatpak stderr）
        self.error_lines = []     # 收集到的错误行，失败时展示
        self._search_gen = 0      # 搜索代数：丢弃过期的远端搜索结果
        # 勾选状态不能只存在复选框里：列表每次重建都会销毁旧行，
        # 搜索/翻查一次就丢光。用 {app_id: meta} 常驻保存。
        self.picked = {}

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # 顶部标题
        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        head.set_margin_top(14); head.set_margin_bottom(8)
        head.set_margin_start(16); head.set_margin_end(16)
        title = Gtk.Label()
        title.set_markup(f"<span size='large'><b>{fl('install_flatpak_apps_gui')}</b></span>")
        title.set_xalign(0)
        head.pack_start(title, True, True, 0)

        # 搜索框放右上角：先在内置清单里匹配（秒出），匹配不到再查 flathub。
        # 这样常用应用不用等网络，冷门应用也能找到并直接勾选安装。
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_width_chars(20)
        self.search_entry.set_placeholder_text(
            "搜索应用" if get_lang() != "en" else "Search apps")
        self.search_entry.connect("search-changed", self._on_search_changed)
        head.pack_end(self.search_entry, False, False, 0)
        outer.pack_start(head, False, False, 0)

        # 说明
        self.hint = Gtk.Label()
        self.hint.set_xalign(0)
        self.hint.set_line_wrap(True)
        self.hint.set_margin_start(16); self.hint.set_margin_end(16)
        self.hint.set_margin_bottom(8)
        self.hint.get_style_context().add_class("dash-card-desc")
        outer.pack_start(self.hint, False, False, 0)

        # 主体：可切换的 勾选页 / 进度页
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(160)
        self.stack.set_margin_start(16); self.stack.set_margin_end(16)
        outer.pack_start(self.stack, True, True, 0)

        self.stack.add_named(self._build_select_page(), "select")
        self.stack.add_named(self._build_progress_page(), "progress")

        # 底部按钮：只保留一个主按钮，按状态变化
        #   · 选择页      → 「安装」（有勾选才可点）；未勾选时隐藏，避免出现无意义的按钮
        #   · 安装中      → 「取消」（真正终止 flatpak）
        #   · 安装结束    → 「完成」（关窗）
        # 不再同时摆「否/确定」两个按钮：那个「否」在选择页上等于「关窗」、
        # 在结果页上又和「确定」重复，纯属噪音。
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_row.set_margin_top(10); btn_row.set_margin_bottom(14)
        btn_row.set_margin_start(16); btn_row.set_margin_end(16)
        self.main_btn = Gtk.Button(label=self._lbl("install"))
        self.main_btn.get_style_context().add_class("suggested-action")
        self.main_btn.connect("clicked", self._on_main_clicked)
        btn_row.pack_end(self.main_btn, False, False, 0)
        outer.pack_start(btn_row, False, False, 0)

        self.add(outer)
        self._refresh_select_page()
        self.show_all()
        self.present()
        self._sync_buttons()
        # 关闭窗口（delete-event / destroy）时终止当前 proc，与「取消」按钮一致。
        self.connect("delete-event", self._on_close_kill)
        self.connect("destroy", self._on_close_destroy)

    def _on_close_kill(self, *_a):
        try:
            self._kill_proc()
        except Exception:
            pass
        return False  # 继续正常关闭

    def _on_close_destroy(self, *_a):
        try:
            self._kill_proc()
        except Exception:
            pass
        return False

    def _lbl(self, key):
        m = {
            "install": ("安装", "Install"),
            "cancel": ("取消", "Cancel"),
            "done": ("完成", "Done"),
            "back": ("返回列表", "Back to list"),
        }
        zh, en = m[key]
        return en if get_lang() == "en" else zh

    def _sync_buttons(self):
        """按当前阶段（self.phase）决定主按钮的文字与可用性。

        用显式的 phase 而不是读 stack 页名，是因为结果页/取消页仍复用 progress
        那个布局，只看页名分不出「正在装」和「装完了」。
        """
        phase = getattr(self, "phase", "select")
        # 搜索框只在勾选页有意义（安装中/结果页还留着会让人以为能搜）
        try:
            self.search_entry.set_visible(phase == "select")
        except Exception:
            pass
        if phase == "select":
            n = len(self._selected())
            # 没勾选任何应用时，按钮没有可执行的动作，直接隐藏
            self.main_btn.set_visible(n > 0)
            self.main_btn.set_sensitive(n > 0)
            self.main_btn.set_label(self._lbl("install"))
        elif phase == "running":
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("cancel"))
        else:  # done
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            # 装完不关窗，回勾选页可以接着装别的
            self.main_btn.set_label(self._lbl("back"))

    def _on_main_clicked(self, *_a):
        phase = getattr(self, "phase", "select")
        if phase == "select":
            self._start_install()
        elif phase == "running":
            # 安装中 → 真正终止 flatpak 进程；随后由 _on_app_done 收尾
            self.cancelled = True
            self.detail_label.set_text("正在取消…" if get_lang() != "en" else "Cancelling…")
            self._kill_proc()
        else:
            # 结果页「返回列表」：重新扫描并回到勾选页，可以接着装别的
            self._back_to_select()

    def _back_to_select(self):
        """安装结束/取消后回到勾选页（与卸载窗口同名方法一致）。"""
        self.phase = "select"
        self.stack.set_visible_child_name("select")
        self.prog_bar.set_fraction(0)
        self.prog_label.set_text("")
        self.detail_label.set_text("")
        self.cancelled = False
        # 装完的应用已从列表消失，勾选也一并清掉，避免下次误装
        self.picked = {}
        # 清掉搜索词再刷新：刚装好的应用本来就已从列表移除，
        # 若搜索词还停在它上面，回去只会看到「没有匹配的未安装应用」
        try:
            self.search_entry.set_text("")
        except Exception:
            pass
        self._refresh_select_page()
        self._sync_buttons()

    def _build_select_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sw.add(self.list_box)
        box.pack_start(sw, True, True, 0)
        return box

    def _build_progress_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_valign(Gtk.Align.CENTER)
        self.prog_label = Gtk.Label(label="")
        self.prog_label.set_xalign(0)
        self.prog_label.set_line_wrap(True)
        self.prog_label.get_style_context().add_class("dash-card-title")
        box.pack_start(self.prog_label, False, False, 0)

        self.prog_bar = Gtk.ProgressBar()
        self.prog_bar.set_show_text(False)
        box.pack_start(self.prog_bar, False, False, 0)

        self.detail_label = Gtk.Label(label="")
        self.detail_label.set_xalign(0)
        self.detail_label.set_line_wrap(True)
        self.detail_label.get_style_context().add_class("dash-card-desc")
        box.pack_start(self.detail_label, False, False, 0)
        return box

    def _refresh_select_page(self):
        """重绘列表：尊重当前搜索词（空则显示全部未安装应用）。"""
        q = ""
        try:
            q = self.search_entry.get_text().strip()
        except Exception:
            pass
        self._render_list(q)

    def _on_search_changed(self, entry):
        """输入变化时刷新列表：先本地匹配，本地没有结果再查远端。"""
        self._render_list(entry.get_text().strip())

    def _local_matches(self, q):
        """在内置清单里按名称/分组/ID 模糊匹配。"""
        ql = q.lower()
        out = []
        for item in FLATPAK_CATALOG:
            title, cands, cat, desk, addon, group = item
            hay = f"{title} {group} {' '.join(cands)}".lower()
            if ql in hay:
                out.append(item)
        return out

    def _remote_search(self, q):  # returns (rows, err)
        """本地没有结果时用 flatpak search 查远端，返回 ([(id, name)], err)。"""
        try:
            r = subprocess.run(["flatpak", "search", "--columns=application,name", q],
                               capture_output=True, text=True, timeout=20)
        except FileNotFoundError:
            return [], "flatpak 命令未安装"
        except Exception as e:
            return [], str(e)
        if r.returncode != 0:
            err = (r.stderr or "").strip() or ("flatpak search 退出码 %d" % r.returncode)
            return [], err
        rows, seen = [], set()
        for line in r.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            app_id, name = parts[0].strip(), parts[1].strip()
            if not app_id or app_id in seen:
                continue
            seen.add(app_id)
            rows.append((app_id, name))
            if len(rows) >= 20:
                break
        return rows, ""

    def _render_list(self, q=""):
        """按查询词重绘列表；q 为空则显示全部未安装应用。"""
        self._search_gen += 1
        for ch in list(self.list_box.get_children()):
            self.list_box.remove(ch)
        self.installed, err = _fp_installed_ids()  # render
        self._fp_install_err = err
        if err:
            lbl = Gtk.Label()
            lbl.set_xalign(0)
            lbl.set_text(t("fp_query_fail") + (" " + err if err else ""))
            lbl.get_style_context().add_class("dash-card-desc")
            self.list_box.pack_start(lbl, False, False, 0)
            self.list_box.show_all()
            return
        if not q:
            self._render_catalog_rows(FLATPAK_CATALOG)
            return
        locals_ = self._local_matches(q)
        if locals_:
            self._render_catalog_rows(locals_)
            return
        status = Gtk.Label()
        status.set_xalign(0)
        status.set_text("本地清单无匹配，正在搜索 flathub…"
                        if get_lang() != "en" else
                        "No local match, searching flathub…")
        status.get_style_context().add_class("dash-card-desc")
        self.list_box.pack_start(status, False, False, 0)
        self.list_box.show_all()

        gen = self._search_gen

        def do_remote():
            rows, err = self._remote_search(q)  # thread
            GLib.idle_add(self._render_remote_rows, q, rows, err, gen)
            return False

        threading.Thread(target=do_remote, daemon=True).start()

    def _render_catalog_rows(self, items):
        shown = 0
        for title, cands, cat, desk, addon, group in items:
            if any(c in self.installed for c in cands):
                continue
            self._add_row(title, group, (_fp_pick_id(cands, self.installed), desk, cat, addon))
            shown += 1
        if shown == 0:
            lbl = Gtk.Label()
            lbl.set_text("没有匹配的未安装应用。" if get_lang() != "en"
                         else "No matching apps that are not installed.")
            lbl.set_margin_top(20)
            self.list_box.pack_start(lbl, False, False, 0)
        self.list_box.show_all()
        self._restore_checks()
        self._update_hint()

    def _render_remote_rows(self, q, rows, err=None, gen=None):
        try:
            if self.search_entry.get_text().strip() != q:
                return False
        except Exception:
            pass
        # search-changed 可能被触发两次（set_text 排队的 + 显式发出的），
        # 两份结果都会回到这里；只认最新一代，否则后到的结果会把用户
        # 刚勾上的选项连同整页一起重建掉。
        if gen is not None and gen != self._search_gen:
            return False
        for ch in list(self.list_box.get_children()):
            self.list_box.remove(ch)
        if err:
            # 查询失败 ≠ 「flathub 也没找到」，必须显示真实错误。
            lbl = Gtk.Label()
            lbl.set_xalign(0)
            lbl.set_line_wrap(True)
            lbl.set_text(t("fp_search_fail", err=err))
            lbl.get_style_context().add_class("dash-card-desc")
            self.list_box.pack_start(lbl, False, False, 0)
            self.list_box.show_all()
            self._update_hint()
            return False
        rows = [(i, n) for i, n in rows if i not in self.installed]
        if not rows:
            lbl = Gtk.Label()
            lbl.set_text("flathub 上也没有找到匹配的应用。" if get_lang() != "en"
                         else "Nothing matching on flathub either.")
            lbl.set_margin_top(20)
            self.list_box.pack_start(lbl, False, False, 0)
        else:
            for app_id, name in rows:
                self._add_row(name, "在线搜索", (app_id, name, "Utility", None))
        self.list_box.show_all()
        self._restore_checks()
        self._update_hint()
        return False

    def _add_row(self, title, group, meta):
        """加一行复选框；meta = (app_id, desk_name, cat, addon)。"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cb = Gtk.CheckButton()
        cb._fp_meta = meta
        text = Gtk.Label()
        text.set_markup(f"<b>{GLib.markup_escape_text(title)}</b>  "
                        f"<span size='small'>{GLib.markup_escape_text(group)}</span>")
        text.set_xalign(0)
        text.set_line_wrap(True)
        row.pack_start(cb, False, False, 0)
        row.pack_start(text, True, True, 0)
        eb = Gtk.EventBox()
        eb.add(row)
        eb.connect("button-press-event",
                   lambda _w, _e, c=cb: (c.set_active(not c.get_active()), True)[1])
        cb.connect("toggled", self._on_row_toggled, cb)
        self.list_box.pack_start(eb, False, False, 0)


    def _walk_checkbuttons(self):
        """遍历 list_box 里所有 CheckButton（它们被包在 EventBox>Box 里）。"""
        found = []

        def rec(w):
            if isinstance(w, Gtk.CheckButton):
                found.append(w)
                return
            if hasattr(w, "get_children"):
                for c in w.get_children():
                    rec(c)

        for ch in self.list_box.get_children():
            rec(ch)
        return found

    def _on_row_toggled(self, cb, *_a):
        """复选框变化 → 更新常驻的 picked，再刷新按钮/提示。"""
        meta = getattr(cb, "_fp_meta", None)
        if meta:
            try:
                if cb.get_active():
                    self.picked[meta[0]] = meta
                else:
                    self.picked.pop(meta[0], None)
            except Exception:
                pass
        self._update_hint()

    def _selected(self):
        """已勾选的应用（跨搜索/重绘保留，取自 picked 而不是当前可见行）。"""
        return list(getattr(self, "picked", {}).values())

    def _restore_checks(self):
        """重绘后把 picked 里的应用重新勾上（勾选框随旧行销毁了）。"""
        picked = getattr(self, "picked", None)
        if not picked:
            return
        for cb in self._walk_checkbuttons():
            try:
                if cb._fp_meta[0] in picked and not cb.get_active():
                    cb.set_active(True)
            except Exception:
                pass

    def _update_hint(self):
        n = len(self._selected())
        if get_lang() == "en":
            self.hint.set_text(f"{n} app(s) selected. Installed apps are not listed.")
        else:
            self.hint.set_text(f"已选择 {n} 个应用；已安装的不会列出。")
        # 勾选数量变化会影响主按钮是否该出现
        try:
            self._sync_buttons()
        except Exception:
            pass
    def _kill_proc(self):
        p = self.proc
        if not p:
            return
        # Popen 用了 start_new_session=True，killpg 整组才能连 flatpak 派生的
        # 子进程一起终止；单 terminate 主进程常留孤儿。
        pgid = getattr(self, "proc_pgid", None)
        if pgid:
            try:
                os.killpg(pgid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        try:
            p.terminate()
        except Exception:
            pass
        GLib.timeout_add(300, self._force_kill, p)

    def _force_kill(self, p):
        pgid = getattr(self, "proc_pgid", None)
        if pgid:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        try:
            if p.poll() is None:
                p.kill()
        except Exception:
            pass
        return False

    def _start_install(self):
        sel = self._selected()
        if not sel:
            return
        # _add_row 存的 meta 已经是 (app_id, desk, cat, addon) —— 挑 ID 的工作
        # 在渲染列表时就做完了。这里若再按候选列表解包，会把字符串当字符序列遍历，
        # 得到的是第一个字符（就是结果页那个 "c"），并把 desk/cat 顺序弄反。
        self.queue = []
        for app_id, desk, cat, addon in sel:
            # 主包先入队；附加包（如 Fcitx 5 中文插件）作为独立队列项，
            # 不再依赖桌面快捷方式写成功才安装，也不再是 fire-and-forget。
            self.queue.append((app_id, desk, cat, addon, False))
            if addon:
                self.queue.append((addon, None, None, None, True))
        self.queue_total = len(self.queue)
        self.done_count = self.fail_count = 0
        self.failed = []
        self.last_inner = 0
        self.cancelled = False

        self.phase = "running"
        self.stack.set_visible_child_name("progress")
        self._sync_buttons()
        self.prog_bar.set_fraction(0)
        self._next_app()

    def _next_app(self):
        if self.cancelled:
            self._finish(cancelled=True)
            return
        if not self.queue:
            self._finish(cancelled=False)
            return

        app_id, desk, cat, addon, is_addon = self.queue.pop(0)
        self.cur = (app_id, desk, cat, addon, is_addon)
        idx = self.done_count + self.fail_count + 1
        if is_addon:
            label = (f"Installing add-on {idx}/{self.queue_total}: {app_id}"
                     if get_lang() == "en" else f"正在安装附加包 {idx}/{self.queue_total}：{app_id}")
        else:
            label = (f"Installing {idx}/{self.queue_total}: {app_id}"
                     if get_lang() == "en" else f"正在安装 {idx}/{self.queue_total}：{app_id}")
        self.prog_label.set_text(label)
        self.last_inner = 0
        argv = ["flatpak", "install", "-y", "flathub", app_id]
        _fp_run_async(argv, self._on_line, lambda rc: self._on_app_done(rc), owner=self)
        # Popen 已由 worker 挂在 self.proc 上；保留 timeout 兜旧兼容。
        GLib.timeout_add(120, self._grab_proc)

    def _grab_proc(self):
        # Popen 现在由 worker 直接挂在窗口实例上（owner=self），不再读全局 last_proc。
        self.proc = getattr(self, "proc", None)  # instance-bound
        return False

    def _on_line(self, line):
        parsed = _fp_progress_parse(line)
        if not parsed:
            # 非进度行：flatpak 的报错（「错误： 未在远程仓库…」等）就藏在这里。
            # 原来直接 return 丢弃，失败时用户只能看到一个空白的失败提示。
            self._note_output(line)
            return False
        step, steps, pct, rate = parsed
        inner = _fp_fold_pct(step, steps, pct)
        if inner < self.last_inner:
            inner = self.last_inner
        self.last_inner = inner

        overall = int(((self.done_count + self.fail_count) * 100 + inner) / max(1, self.queue_total))
        overall = min(overall, 100)
        self.prog_bar.set_fraction(overall / 100.0)
        # 进度条内的文字已关掉，百分比统一显示在下方这一行；
        # 多应用时用整体百分比（含已完成的应用），比单应用百分比更准确
        self.detail_label.set_text(f"{overall}%" + (f"  {rate}" if rate else ""))
        return False

    def _note_output(self, line):
        """收集值得展示的输出行（错误/警告），供失败时报告原因。"""
        t = (line or "").strip()
        if not t:
            return
        # flatpak 的进度帧用 \r 刷新，去掉控制字符后判断
        if "\r" in t:
            t = t.split("\r")[-1].strip()
        low = t.lower()
        important = (
            t.startswith("错误") or t.startswith("error") or
            "错误：" in t or "失败" in low or "failed" in low or
            t.startswith("警告") or t.startswith("warning") or
            "not found" in low or "no such" in low or
            "permission" in low or "denied" in low
        )
        if important:
            self.last_error = t
            self.error_lines.append(t)
            if len(self.error_lines) > 20:
                self.error_lines = self.error_lines[-20:]

    def _on_app_done(self, rc):  # addon aware
        app_id, desk, cat, addon, is_addon = self.cur
        if rc == 0:
            self.done_count += 1
            # 桌面快捷方式失败不影响安装成功，也不再决定附加包是否安装。
            if not is_addon and desk:
                _fp_write_shortcut(desk, cat, app_id)
        else:
            self.fail_count += 1
            self.failed.append(app_id)
            # 附加包失败也要输出错误（写入 error_lines，结果页能看到原因）。
            if is_addon:
                self._note_output(
                    ("Add-on install failed: " if get_lang() == "en" else "附加包安装失败：") + app_id)
        self._next_app()
        return False

    def _failure_details(self):
        """失败时给出「哪个应用 + 为什么」。"""
        if not self.failed:
            return ""
        zh = get_lang() != "en"
        parts = []
        for app_id in self.failed:
            parts.append(f"· {app_id}")
        # 附上 flatpak 真实报错（最常见的是 ID 不存在、网络不通、磁盘满）
        if self.error_lines:
            # 去重，保留顺序，最多 3 条，太长会撑爆窗口
            seen, uniq = set(), []
            for line in self.error_lines:
                if line in seen:
                    continue
                seen.add(line)
                uniq.append(line)
            reason = "\n".join(uniq[-3:])
            parts.append("")
            parts.append(("原因：" if zh else "Reason:"))
            parts.append(reason)
        return "\n".join(parts)

    def _finish(self, cancelled):
        self.prog_bar.set_fraction(1.0 if not cancelled else self.prog_bar.get_fraction())
        if cancelled:
            if get_lang() == "en":
                self.prog_label.set_text("Cancelled")
                self.detail_label.set_text(f"Completed {self.done_count} before cancelling.")
            else:
                self.prog_label.set_text("已取消")
                self.detail_label.set_text(f"取消前已完成 {self.done_count} 个。")
        else:
            if self.fail_count == 0:
                msg = (f"✓ Install complete: {self.done_count} succeeded" if get_lang() == "en"
                       else f"✓ 安装完成：成功 {self.done_count} 个")
            elif self.done_count:
                msg = (f"Install finished: {self.done_count} succeeded, {self.fail_count} failed"
                       if get_lang() == "en" else
                       f"安装结束：成功 {self.done_count} 个，失败 {self.fail_count} 个")
            else:
                msg = (f"✗ Install failed: {self.fail_count}" if get_lang() == "en"
                       else f"✗ 安装失败：{self.fail_count} 个")
            self.prog_label.set_text(msg)
            self.detail_label.set_text(self._failure_details())
            self.prog_bar.set_fraction(1.0)
        # 结果页：主按钮变成「返回列表」，点它回到勾选页继续装
        self.phase = "done"
        self.stack.set_visible_child_name("progress")
        self._sync_buttons()


class FlatpakUninstallWindow(Gtk.Window):
    """卸载 Flatpak 应用：勾选 → 卸载 → 进度 → 结果（含数据目录清理询问）。"""

    def __init__(self, parent=None):
        super().__init__(title=fl("uninstall_other_flatpak_apps"))
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(600, 500)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT if parent else Gtk.WindowPosition.CENTER)
        if parent:
            self.set_transient_for(parent)
        self.proc = None
        self.phase = "select"     # select / running / askdata / done
        self.cancelled = False
        self.queue = []
        self.queue_total = 0
        self.done_count = 0
        self.fail_count = 0
        self.failed = []
        self.data_dirs = []
        self.last_inner = 0
        self.last_error = ""
        self.error_lines = []

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        head.set_margin_top(14); head.set_margin_bottom(8)
        head.set_margin_start(16); head.set_margin_end(16)
        title = Gtk.Label()
        title.set_markup(f"<span size='large'><b>{fl('uninstall_other_flatpak_apps')}</b></span>")
        title.set_xalign(0)
        head.pack_start(title, True, True, 0)
        outer.pack_start(head, False, False, 0)

        self.hint = Gtk.Label()
        self.hint.set_xalign(0); self.hint.set_line_wrap(True)
        self.hint.set_margin_start(16); self.hint.set_margin_end(16); self.hint.set_margin_bottom(8)
        self.hint.get_style_context().add_class("dash-card-desc")
        outer.pack_start(self.hint, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(160)
        self.stack.set_margin_start(16); self.stack.set_margin_end(16)
        outer.pack_start(self.stack, True, True, 0)
        self.stack.add_named(self._build_select_page(), "select")
        self.stack.add_named(self._build_progress_page(), "progress")

        # 底部按钮：只保留一个主按钮，随阶段变化
        #   选择页 → 「卸载」（有勾选才显示）
        #   卸载中 → 「取消」（真正终止 flatpak）
        #   结果页 → 「完成」（关窗）
        #   数据询问 → 额外露出「保留」按钮
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_row.set_margin_top(10); btn_row.set_margin_bottom(14)
        btn_row.set_margin_start(16); btn_row.set_margin_end(16)
        self.keep_btn = Gtk.Button(label=self._lbl("keep"))
        self.keep_btn.connect("clicked", lambda *_a: self.destroy())
        self.main_btn = Gtk.Button(label=self._lbl("uninstall"))
        self.main_btn.get_style_context().add_class("suggested-action")
        self.main_btn.connect("clicked", self._on_main_clicked)
        btn_row.pack_end(self.main_btn, False, False, 0)
        btn_row.pack_end(self.keep_btn, False, False, 0)
        outer.pack_start(btn_row, False, False, 0)

        self.add(outer)
        self._refresh_select_page()
        self.show_all()
        self.present()
        self.keep_btn.set_visible(False)
        self._sync_buttons()
        # 关闭窗口即终止当前 proc，与「取消」按钮一致。
        self.connect("delete-event", self._on_close_kill)  # uninstall
        self.connect("destroy", self._on_close_destroy)

    def _on_close_kill(self, *_a):
        try:
            self._kill_proc()
        except Exception:
            pass
        return False

    def _on_close_destroy(self, *_a):
        try:
            self._kill_proc()
        except Exception:
            pass
        return False

    def _lbl(self, key):
        m = {
            "uninstall": ("卸载", "Uninstall"),
            "cancel": ("取消", "Cancel"),
            "done": ("完成", "Done"),
            "back": ("返回列表", "Back to list"),
            "keep": ("保留", "Keep"),
            "delete": ("删除数据", "Delete data"),
        }
        zh, en = m[key]
        return en if get_lang() == "en" else zh

    def _sync_buttons(self):
        """按 self.phase 决定按钮；用显式阶段而不是 stack 页名，
        因为结果页/数据询问页都复用 progress 那个布局。"""
        phase = getattr(self, "phase", "select")
        if phase == "select":
            n = len(self._selected())
            self.main_btn.set_visible(n > 0)
            self.main_btn.set_sensitive(n > 0)
            self.main_btn.set_label(self._lbl("uninstall"))
            self.keep_btn.set_visible(False)
        elif phase == "running":
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("cancel"))
            self.keep_btn.set_visible(False)
        elif phase == "askdata":
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("delete"))
            self.keep_btn.set_visible(True)
        else:  # done
            self.main_btn.set_visible(True)
            self.main_btn.set_sensitive(True)
            self.main_btn.set_label(self._lbl("back"))
            self.keep_btn.set_visible(False)

    def _on_main_clicked(self, *_a):
        phase = getattr(self, "phase", "select")
        if phase == "select":
            self._start_uninstall()
        elif phase == "running":
            self.cancelled = True
            self.detail_label.set_text("正在取消…" if get_lang() != "en" else "Cancelling…")
            self._kill_proc()
        elif phase == "askdata":
            self._do_cleanup()
        else:
            # 结果页「返回列表」：重新扫描并回到勾选页，可以接着卸别的
            self._back_to_select()

    def _back_to_select(self):
        """卸载结束/取消后回到勾选页，可以接着卸别的（与安装窗口装完回列表一致）。"""
        self.phase = "select"
        self.stack.set_visible_child_name("select")
        self.prog_bar.set_fraction(0)
        self.prog_label.set_text("")
        self.detail_label.set_text("")
        self.cancelled = False
        self._refresh_select_page()
        self._sync_buttons()

    def _build_select_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sw.add(self.list_box)
        box.pack_start(sw, True, True, 0)
        return box

    def _build_progress_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_valign(Gtk.Align.CENTER)
        self.prog_label = Gtk.Label(label="")
        self.prog_label.set_xalign(0); self.prog_label.set_line_wrap(True)
        box.pack_start(self.prog_label, False, False, 0)
        self.prog_bar = Gtk.ProgressBar()
        self.prog_bar.set_show_text(False)
        box.pack_start(self.prog_bar, False, False, 0)
        self.detail_label = Gtk.Label(label="")
        self.detail_label.set_xalign(0); self.detail_label.set_line_wrap(True)
        self.detail_label.get_style_context().add_class("dash-card-desc")
        box.pack_start(self.detail_label, False, False, 0)
        return box

    def _refresh_select_page(self):  # err-aware
        for ch in list(self.list_box.get_children()):
            self.list_box.remove(ch)
        rows = []
        query_err = ""
        try:
            r = subprocess.run(["flatpak", "list", "--app", "--columns=application,name"],
                               capture_output=True, text=True, timeout=15)
            if r.returncode != 0:
                query_err = (r.stderr or "").strip() or ("flatpak list 退出码 %d" % r.returncode)
            else:
                rows = [l.split("\t") for l in r.stdout.splitlines() if l.strip()]
        except FileNotFoundError:
            query_err = "flatpak 命令未安装"
        except Exception as e:
            query_err = str(e)
        if query_err:
            lbl = Gtk.Label()
            lbl.set_xalign(0)
            lbl.set_line_wrap(True)
            lbl.set_text(t("fp_query_fail") + " " + query_err)
            lbl.set_margin_top(20)
            self.list_box.pack_start(lbl, False, False, 0)
            self.list_box.show_all()
            self._update_hint()
            return
        shown = 0
        for parts in rows:
            app_id = parts[0].strip()
            app_name = parts[1].strip() if len(parts) > 1 else app_id
            if app_id in FLATPAK_EXCLUDE:
                continue
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            cb = Gtk.CheckButton()
            cb._fp_app = app_id
            text = Gtk.Label()
            text.set_markup(f"<b>{GLib.markup_escape_text(app_name)}</b>  "
                            f"<span size='small'>{GLib.markup_escape_text(app_id)}</span>")
            text.set_xalign(0); text.set_line_wrap(True)
            row.pack_start(cb, False, False, 0)
            row.pack_start(text, True, True, 0)
            eb = Gtk.EventBox()
            eb.add(row)
            eb.connect("button-press-event",
                       lambda _w, _e, c=cb: (c.set_active(not c.get_active()), True)[1])
            cb.connect("toggled", lambda *_a: self._update_hint())
            self.list_box.pack_start(eb, False, False, 0)
            shown += 1
        if shown == 0:
            lbl = Gtk.Label(label="没有可卸载的 Flatpak 应用。" if get_lang() != "en"
                            else "No Flatpak apps available to uninstall.")
            lbl.set_margin_top(20)
            self.list_box.pack_start(lbl, False, False, 0)
        # 必须显式 show_all：初次显示是靠窗口的 show_all() 一起带出来的，
        # 但「返回列表」时窗口早已显示过，之后新建的行默认是隐藏的 ——
        # 不调用这一句，返回列表后看到的就是一片空白。
        self.list_box.show_all()
        self._update_hint()

    def _walk_checkbuttons(self):
        found = []

        def rec(w):
            if isinstance(w, Gtk.CheckButton):
                found.append(w)
                return
            if hasattr(w, "get_children"):
                for c in w.get_children():
                    rec(c)

        for ch in self.list_box.get_children():
            rec(ch)
        return found

    def _selected(self):
        return [cb._fp_app for cb in self._walk_checkbuttons() if cb.get_active()]

    def _update_hint(self):
        n = len(self._selected())
        self.hint.set_text(f"{n} selected." if get_lang() == "en" else f"已选择 {n} 个应用。")
        # 勾选数量决定主按钮该不该出现（与安装窗口一致）
        try:
            self._sync_buttons()
        except Exception:
            pass
    def _kill_proc(self):
        p = self.proc
        if not p:
            return
        # Popen 用了 start_new_session=True，killpg 整组才能连 flatpak 派生的
        # 子进程一起终止；单 terminate 主进程常留孤儿。
        pgid = getattr(self, "proc_pgid", None)
        if pgid:
            try:
                os.killpg(pgid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        try:
            p.terminate()
        except Exception:
            pass
        GLib.timeout_add(300, self._force_kill, p)

    def _force_kill(self, p):
        pgid = getattr(self, "proc_pgid", None)
        if pgid:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        try:
            if p.poll() is None:
                p.kill()
        except Exception:
            pass
        return False
    def _start_uninstall(self):
        sel = self._selected()
        if not sel:
            return
        self.queue = list(sel)
        self.queue_total = len(self.queue)
        self.done_count = self.fail_count = 0
        self.failed = []
        self.data_dirs = []
        self.last_inner = 0
        self.cancelled = False
        self.phase = "running"
        self.stack.set_visible_child_name("progress")
        self._sync_buttons()
        self.prog_bar.set_fraction(0)
        self._next_app()

    def _next_app(self):
        if self.cancelled:
            self._finish(True); return
        if not self.queue:
            self._finish(False); return
        app_id = self.queue.pop(0)
        self.cur = app_id
        idx = self.done_count + self.fail_count + 1
        self.prog_label.set_text(f"Uninstalling {idx}/{self.queue_total}: {app_id}"
                                 if get_lang() == "en" else
                                 f"正在卸载 {idx}/{self.queue_total}：{app_id}")
        self.last_inner = 0
        # FIX-GUI: uninstall owner=self
        _fp_run_async(["flatpak", "uninstall", "-y", app_id], self._on_line,
                      lambda rc: self._on_app_done(rc), owner=self)
        GLib.timeout_add(120, self._grab_proc)

    def _grab_proc(self):
        # Popen 现在由 worker 直接挂在窗口实例上（owner=self），不再读全局 last_proc。
        self.proc = getattr(self, "proc", None)  # instance-bound
        return False

    def _note_output(self, line):
        """收集 flatpak 的错误行，供失败时展示原因。"""
        t = (line or "").strip()
        if not t:
            return
        if "\r" in t:
            t = t.split("\r")[-1].strip()
        low = t.lower()
        important = (
            t.startswith("错误") or t.startswith("error") or
            "错误：" in t or "失败" in low or "failed" in low or
            t.startswith("警告") or t.startswith("warning") or
            "not found" in low or "no such" in low or
            "permission" in low or "denied" in low
        )
        if important:
            self.last_error = t
            self.error_lines.append(t)
            if len(self.error_lines) > 20:
                self.error_lines = self.error_lines[-20:]

    def _on_line(self, line):
        parsed = _fp_progress_parse(line)
        if not parsed:
            self._note_output(line)
            return False
        step, steps, pct, rate = parsed
        inner = _fp_fold_pct(step, steps, pct)
        if inner < self.last_inner:
            inner = self.last_inner
        self.last_inner = inner
        overall = int(((self.done_count + self.fail_count) * 100 + inner) / max(1, self.queue_total))
        overall = min(overall, 100)
        self.prog_bar.set_fraction(overall / 100.0)
        self.detail_label.set_text(f"{overall}%" + (f"  {rate}" if rate else ""))
        return False

    def _on_app_done(self, rc):
        app_id = self.cur
        if rc == 0:
            self.done_count += 1
            _fp_remove_shortcuts(app_id)
            d = os.path.join(os.path.expanduser("~"), ".var", "app", app_id)
            if os.path.isdir(d):
                self.data_dirs.append(d)
        else:
            self.fail_count += 1
            self.failed.append(app_id)
        self._next_app()
        return False

    def _failure_details(self):
        if not self.failed:
            return ""
        zh = get_lang() != "en"
        parts = [f"· {a}" for a in self.failed]
        if self.error_lines:
            seen, uniq = set(), []
            for line in self.error_lines:
                if line in seen:
                    continue
                seen.add(line)
                uniq.append(line)
            parts.append("")
            parts.append("原因：" if zh else "Reason:")
            parts.append("\n".join(uniq[-3:]))
        return "\n".join(parts)

    def _finish(self, cancelled):
        if cancelled:
            self.prog_label.set_text("已取消" if get_lang() != "en" else "Cancelled")
            self.detail_label.set_text(
                f"取消前已完成 {self.done_count} 个。" if get_lang() != "en"
                else f"Completed {self.done_count} before cancelling.")
        else:
            if self.fail_count == 0:
                msg = (f"✓ Uninstall complete: {self.done_count} succeeded" if get_lang() == "en"
                       else f"✓ 卸载完成：成功 {self.done_count} 个")
            elif self.done_count:
                msg = (f"Uninstall finished: {self.done_count} succeeded, {self.fail_count} failed"
                       if get_lang() == "en" else
                       f"卸载结束：成功 {self.done_count} 个，失败 {self.fail_count} 个")
            else:
                msg = (f"✗ Uninstall failed: {self.fail_count}" if get_lang() == "en"
                       else f"✗ 卸载失败：{self.fail_count} 个")
            self.prog_label.set_text(msg)
            if self.failed:
                self.detail_label.set_text(self._failure_details())
            else:
                self.detail_label.set_text("")
            self.prog_bar.set_fraction(1.0)

        # 有残留数据 → 在同一窗口里问，不再弹第二个窗口
        if not cancelled and self.data_dirs:
            self._ask_data_cleanup()
            return
        # 结果页：主按钮是「返回列表」，点了可以继续卸别的（不再直接关窗）
        self.phase = "done"
        self.stack.set_visible_child_name("progress")
        self._sync_buttons()

    def _ask_data_cleanup(self):
        """把「是否删除本地数据」做成窗口的一部分，而不是另开一个对话框。"""
        self.prog_label.set_text(
            "是否删除本地数据？" if get_lang() != "en" else "Delete local data?")
        names = ", ".join(os.path.basename(d) for d in self.data_dirs)
        self.detail_label.set_text(
            (f"以下应用仍留有数据：{names}\n选择「保留」则下次重装设置还在。")
            if get_lang() != "en" else
            f"These apps still have local data: {names}\nChoosing Keep preserves settings for a reinstall.")
        # 切到专门的询问页：主按钮「删除数据」、次按钮「保留」（保留 = 关窗）
        self.phase = "askdata"
        self.stack.set_visible_child_name("progress")
        self._sync_buttons()

    def _do_cleanup(self, *_a):
        ok_n = bad_n = 0
        for d in self.data_dirs:
            try:
                shutil.rmtree(d)
                ok_n += 1
            except Exception:
                bad_n += 1
        msg = (f"已删除 {ok_n} 个数据目录" + (f"，{bad_n} 个失败" if bad_n else "")
               if get_lang() != "en" else
               f"Deleted {ok_n} data director(ies)" + (f", {bad_n} failed" if bad_n else ""))
        self.prog_label.set_text(msg)
        self.detail_label.set_text("")
        # 清理完也回到「返回列表」，与普通结果页一致
        self.phase = "done"
        self.stack.set_visible_child_name("progress")
        self._sync_buttons()


class UpdateCheckWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=t("check_update"))
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(*UPDATE_SPLASH_SIZE)
        self.set_size_request(*UPDATE_SPLASH_SIZE)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_deletable(False)
        self.set_resizable(False)
        # 启动闪屏不抢任务栏；真正的任务栏项留给随后出现的 MainWindow
        try:
            self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
            self.set_skip_taskbar_hint(True)
        except Exception:
            pass
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(20); vbox.set_margin_bottom(20)
        vbox.set_margin_start(20); vbox.set_margin_end(20)
        self.add(vbox)
        self.label = Gtk.Label(label=t("checking_update"))
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_line_wrap(True)
        vbox.pack_start(self.label, True, True, 0)
        self.button = None
        self._action_buttons = []
        self.vbox = vbox
        self.show_all()
        GLib.timeout_add(200, self.perform_check)

    def perform_check(self):
        def check_thread():
            # 任何异常（sync/get_remote_version 内部抛出的、线程调度问题）都必须
            # 让 on_check_done 被调用；否则非 deletable 的闪屏会永久卡住启动。
            remote_version = None
            try:
                sync_emoji_icons()
                remote_version = get_remote_version()
            except Exception as e:
                print(f"更新检查线程异常: {e}")
                remote_version = None
            try:
                GLib.idle_add(self.on_check_done, remote_version)
            except Exception as e:
                print(f"回主线程失败，兜底进入主界面: {e}")
                GLib.idle_add(self.on_check_done, None)  # always
        threading.Thread(target=check_thread, daemon=True).start()
        return False

    def on_check_done(self, remote_version):
        if remote_version is None:
            # 用带说明的文案，明确告诉用户可以点按钮进入主界面；
            # 按钮必须 visible + sensitive，否则窗口 deletable=False 会卡死。
            self.label.set_text(t("check_fail_button"))
            if self.button is None:
                self.button = Gtk.Button(label=t("enter_main"))
                self.button.connect("clicked", self.on_button_clicked)
                self.vbox.pack_start(self.button, False, False, 0)
            self.button.set_sensitive(True)
            self.button.set_visible(True)
            self.button.show()
            return
        if compare_versions(remote_version, VERSION) <= 0:
            self.label.set_text(t("already_latest", ver=VERSION))
            if self.button is not None:
                self.button.hide()
            GLib.timeout_add(300, self.auto_enter_main)
            return
        self.label.set_text(
            t("found_new_big", ver=remote_version)
            + ("\n当前版本: v" if get_lang() == "zh" else "\nCurrent: v")
            + VERSION
        )
        if self.button is not None:
            self.button.hide()
        self.show_update_prompt(remote_version)

    def _enter_main(self):
        """先映射主窗口，再关掉更新检查窗。

        旧逻辑是 self.destroy() 再 show_main_window()：在 KDE Plasma（Steam Deck
        桌面模式）上，最后一个应用窗被销毁时任务栏会立刻摘掉图标，随后新建的
        MainWindow 经常不再显示任务栏项。必须先让 MainWindow 出现在任务栏里。
        """
        show_main_window()

    def auto_enter_main(self):
        self._enter_main()
        return False

    def _clear_action_buttons(self):
        for btn in list(getattr(self, "_action_buttons", []) or []):
            try:
                btn.destroy()
            except Exception:
                pass
        self._action_buttons = []
        if self.button is not None:
            try:
                self.button.hide()
            except Exception:
                pass

    def show_update_prompt(self, remote_version):
        """发现新版本后仍留在本窗口提问/更新，避免再弹一个不同尺寸的对话框。"""
        self._clear_action_buttons()
        self.label.set_text(
            t("found_new_big", ver=remote_version)
            + "\n"
            + t("update_prompt", cur=VERSION, remote=remote_version)
        )
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_row.set_halign(Gtk.Align.CENTER)
        yes_btn = Gtk.Button(label=t("yes"))
        no_btn = Gtk.Button(label=t("no"))
        yes_btn.connect("clicked", lambda *_: self._on_update_yes(remote_version))
        no_btn.connect("clicked", lambda *_: self._enter_main())
        btn_row.pack_start(yes_btn, False, False, 0)
        btn_row.pack_start(no_btn, False, False, 0)
        self.vbox.pack_start(btn_row, False, False, 0)
        self._action_buttons = [btn_row, yes_btn, no_btn]
        self.set_default_size(*UPDATE_SPLASH_SIZE)
        self.resize(*UPDATE_SPLASH_SIZE)
        btn_row.show_all()
        try:
            self.present()
        except Exception:
            pass

    def _on_update_yes(self, remote_version):
        self._clear_action_buttons()
        self.label.set_text(t("updating") + "\n" + t("updating_hint"))
        self.set_default_size(*UPDATE_SPLASH_SIZE)
        self.resize(*UPDATE_SPLASH_SIZE)
        # 成功会重启进程；失败回调里会 show_main_window()
        _perform_update_in_window(self, remote_version)

    def on_button_clicked(self, button):
        self._enter_main()

def show_main_window():
    # 关掉仍存活的更新检查闪屏（可能已 hide），避免残留无任务栏对话框窗
    for w in list(Gtk.Window.list_toplevels()):
        try:
            if isinstance(w, UpdateCheckWindow):
                w.destroy()
        except Exception:
            pass
    window = MainWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    try:
        window.present()
    except Exception:
        pass
    # Gtk.Stack may reset visible child on first show_all if switched in __init__;
    # re-select default category after the window is mapped so about content is visible.
    def _open_default():
        try:
            window.open_category("support")
        except Exception:
            pass
        return False
    GLib.idle_add(_open_default)
    GLib.idle_add(ensure_desktop_shortcut)
    GLib.idle_add(ensure_vte_installed)
    return window

def main():
    # 统一 WM_CLASS，便于 Plasma 任务栏与桌面 StartupWMClass 对上号
    try:
        GLib.set_prgname("steamdeck-toolbox")
        Gdk.set_program_class("Steamdeck-toolbox")
    except Exception:
        pass
    # 关键顺序：必须在 apply_app_css 改写 GTK prefer-dark 之前，
    # 先记录系统真实的配色方案，否则“跟随系统”会读到被自己改过的值。
    reset_system_theme_cache()
    # 启动时应用用户上次选择的语言与主题
    set_lang(load_lang_pref())
    apply_app_css(load_theme_pref())
    # 回调里的异常默认只打到 stderr，从桌面启动时用户完全看不到。
    # 装在 Gtk.main() 之前，保证任何一次点击失败都有日志和提示框。
    install_excepthook()
    UpdateCheckWindow()
    Gtk.main()

if __name__ == "__main__":
    main()
