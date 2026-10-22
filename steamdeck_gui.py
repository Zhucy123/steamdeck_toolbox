#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Force an English locale for this process so GTK's built-in strings
# (dialog buttons such as "OK"/"Cancel", file chooser labels, etc.) are English
# even when the system locale is Chinese. Must happen before GTK is initialised.
import os
for _var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
    os.environ[_var] = "en_US.UTF-8"
os.environ["LANGUAGE"] = "en_US:en"

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
# Version definition
# ============================================================================
VERSION = "1.9.4"
REPO_RAW_URL = "https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/steamdeck_gui.py"
REPO_URL = "https://github.com/Zhucy123/steamdeck_toolbox"
VERSION_CHECK_TIMEOUT = 10

# ============================================================================
# Embedded icons (base64; the script is self-contained and needs no external folder)
# Icon data comes from the repo's emoji_icons/; at runtime, custom files in emoji_icons/ next to the script take priority
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
# Global styles and utility functions
# ============================================================================
# ============================================================================
# Themes (dark / light)
# ============================================================================
# Color tables: same keys, different values; the CSS template injects them via {key} placeholders.
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

# CSS template: all colors come from the theme dicts above; dark and light share the same style structure
APP_CSS_TEMPLATE = """
/* =====================================================================
   Steam Deck style theme (switchable dark / light)
   Rounded cards + touch-friendly row height
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

/* ---------- Client-side decoration (CSD) ----------
   Without this, GTK draws the window frame/shadow using the SYSTEM theme.
   On a light system theme that shows up as a white strip above the header bar.
   Painting it with our own background colour makes the window edge match the app. */
decoration {{
    background-color: @sd_bg;
    border-radius: 12px;
    box-shadow: 0 0 0 1px @sd_border, 0 8px 24px {shadow};
}}
decoration:backdrop {{
    background-color: @sd_bg;
    box-shadow: 0 0 0 1px @sd_border, 0 4px 12px {shadow};
}}
/* Round the whole window (all four corners), and let the decoration radius show
   through instead of a square background that would clip the bottom corners. */
window.csd, window.csd:backdrop {{
    background-color: transparent;
    border-radius: 12px;
}}
window.csd > .titlebar, window.csd > headerbar, .titlebar {{
    background-color: @sd_bg;
    border: none;
    box-shadow: none;
    border-radius: 12px 12px 0 0;
}}
/* The bottom edge of the content area needs the same radius, otherwise the
   bottom-left / bottom-right corners render as sharp squares. */
window.csd > box, window.csd > .background {{
    border-radius: 0 0 12px 12px;
    background-color: transparent;
}}

/* ---------- Top header bar ---------- */
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

/* ---------- Search box ---------- */
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
/* In dark mode, prevent the default theme from painting the search box with a white background */
headerbar entry, headerbar entry.search {{ color: @sd_text; }}
headerbar entry text, headerbar entry.search text {{
    background-color: transparent;
    color: @sd_text;
}}

/* ---------- Left category sidebar ---------- */
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

/* ---------- Function list / search result list ---------- */
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

/* ---------- Rounded card container ---------- */
.card {{
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 12px;
}}

/* ---------- Page title ---------- */
#page-title {{ color: {title}; }}

/* ---------- Bottom status bar ---------- */
#bottom-bar {{
    background-image: linear-gradient(to bottom, {bottom_top}, {bottom_bottom});
    border-top: 1px solid @sd_border;
    padding: 6px 10px;
    /* Match the window's rounded bottom corners, otherwise the opaque bar
       paints over them and they render as sharp 90-degree squares. */
    border-radius: 0 0 12px 12px;
}}
#status-label {{ font-size: 11px; color: @sd_dim; }}
#task-timer {{ font-size: 11px; font-weight: bold; color: @sd_accent; }}

/* ---------- Normal buttons ---------- */
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

/* ---------- Text view ---------- */
textview, textview text {{ background-color: @sd_panel; color: @sd_text; caret-color: @sd_accent; }}
textview {{ border-radius: 10px; }}

/* ---------- Scrollbar ---------- */
scrollbar {{ background-color: transparent; border: none; }}
scrollbar slider {{
    background-color: {scrollbar};
    border-radius: 6px;
    min-width: 8px;
    min-height: 8px;
}}
scrollbar slider:hover {{ background-color: alpha(@sd_accent, 0.6); }}

/* ---------- Theme switch popover (only a Popover can follow the theme colors) ---------- */
popover, popover.background {{
    background-color: @sd_panel;
    border: 1px solid @sd_border;
    border-radius: 10px;
    box-shadow: 0 6px 18px {shadow};
}}
popover > box, popover.background > box {{ background-color: transparent; }}
/* Theme row buttons */
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

/* ---------- Dialogs (native MessageDialog for dangerous-operation confirmation, etc.) ---------- */
/* Native Adwaita dialogs have a light paper background but inherit the dark theme's text color,
   which causes "light text on a white background" after switching to light mode. Explicitly set the dialog background and text colors here. */
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
/* The dialog's own header bar is drawn by the system theme and shows up as a light
   strip above the message text on a light desktop theme. Paint it with our colours.
   GTK3 MessageDialog uses a .titlebar (not a headerbar element) for its CSD title area,
   so target both the class and the element, plus the generic titlebar rule below. */
dialog headerbar, messagedialog headerbar,
dialog > headerbar, messagedialog > headerbar,
.dialog headerbar, .message-dialog headerbar,
dialog .titlebar, messagedialog .titlebar,
.dialog .titlebar, .message-dialog .titlebar,
dialog > .titlebar, messagedialog > .titlebar,
window.dialog .titlebar, window.dialog > .titlebar,
.titlebar.dialog, .titlebar.message-dialog,
dialog.titlebar, messagedialog.titlebar {{
    background-image: none;
    background-color: @sd_bg_alt;
    border-bottom: 1px solid @sd_border;
    color: @sd_text;
    box-shadow: none;
    border-radius: 12px 12px 0 0;
}}
dialog headerbar .title, messagedialog headerbar .title,
dialog headerbar .subtitle, messagedialog headerbar .subtitle {{
    color: @sd_text;
}}
dialog headerbar button, messagedialog headerbar button {{
    background-image: none;
    background-color: {btn_ghost};
    border: 1px solid {btn_ghost_border};
    border-radius: 8px;
    color: @sd_text;
    box-shadow: none;
    text-shadow: none;
}}
dialog headerbar button:hover, messagedialog headerbar button:hover {{
    background-color: {titlebtn_hover};
}}
dialog headerbar button image, messagedialog headerbar button image {{
    color: @sd_text;
}}
/* Round the dialog itself so it matches the main window. */
dialog.csd, messagedialog.csd, dialog > decoration, messagedialog > decoration {{
    border-radius: 12px;
}}
dialog image, messagedialog image {{ color: @sd_accent; }}
dialog button, messagedialog button {{ color: @sd_text; }}
dialog button:active, messagedialog button:active,
dialog button.suggested-action, messagedialog button.suggested-action {{ color: {sel_text}; }}

/* ---------- Native popups: drop-down menus / tooltips / input-method candidate windows ---------- */
menu, .menu, .context-menu, menuitem, tooltip, tooltip.background {{
    color: @sd_text;
}}
menu, .menu, .context-menu {{ background-color: @sd_panel; border: 1px solid @sd_border; }}
menuitem {{ background-color: transparent; }}
menuitem:hover {{ background-color: alpha(@sd_accent, {alpha_accent_btn}); }}
tooltip.background {{ background-color: {panel_hi}; border: 1px solid @sd_border; }}
tooltip label {{ color: @sd_text; }}

/* ---------- Terminal ---------- */
vte-terminal {{ padding: 6px; }}
"""

def build_css(theme_name):
    """Generate the CSS text for the given theme name."""
    palette = THEME_LIGHT if theme_name == "light" else THEME_DARK
    return APP_CSS_TEMPLATE.format(**palette)

# Backward compatibility: if old code still references APP_CSS, default to the dark theme
APP_CSS = build_css("dark")

# ---------------------------------------------------------------------------
# Theme config: dark / light / follow system, persisted to ~/.config/steamdeck_toolbox/config.json
# ---------------------------------------------------------------------------
THEME_MODES = ("dark", "light", "system")
THEME_LABELS = {"dark": "Dark", "light": "Light", "system": "Follow System"}

_css_provider = None

def _config_path():
    return os.path.join(os.path.expanduser("~"), ".config", "steamdeck_toolbox", "config.json")

def load_theme_pref():
    """Load the user preference; defaults to follow system."""
    try:
        with open(_config_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        mode = data.get("theme", "system")
        return mode if mode in THEME_MODES else "system"
    except Exception:
        return "system"

def save_theme_pref(mode):
    """Save the theme preference; failure does not affect usage."""
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
        print(f"Failed to save theme setting: {e}")
        return False

# Snapshot of the system's real color scheme.
# Note: apply_app_css changes GTK's prefer-dark so native widgets follow suit;
# If the original system value is not recorded first, "Follow System" reads back the value we overwrote (self-pollution).
_system_theme = None

def _detect_system_theme():
    """Detect the system's real color scheme; returns dark or light. Call once at startup, before modifying GTK."""
    # 1) Prefer the desktop environment's color-scheme setting (the real "system theme" the user set)
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
                # color-scheme is 'prefer-dark' / 'default', etc.
                return "dark" if dark_pat in val else "light"
            # A gtk-theme name containing "dark" counts as a dark theme
            return "dark" if "dark" in val else "light"
        except Exception:
            continue
    # 2) Fallback: read GTK's prefer-dark
    try:
        settings = Gtk.Settings.get_default()
        if settings is not None:
            return "dark" if settings.get_property("gtk-application-prefer-dark-theme") else "light"
    except Exception:
        pass
    return "light"

def reset_system_theme_cache():
    """Re-detect the system color scheme (the user may have changed the theme)."""
    global _system_theme
    _system_theme = _detect_system_theme()
    return _system_theme

def resolve_theme_mode(mode):
    """Resolve "system" to the effective dark/light. Uses the startup snapshot to avoid self-pollution."""
    if mode in ("dark", "light"):
        return mode
    global _system_theme
    if _system_theme is None:
        reset_system_theme_cache()
    return _system_theme or "light"

def _gtk_theme_available(name):
    """Return True if the given GTK theme is installed (checked via common theme dirs)."""
    try:
        if not name:
            return False
        candidates = [
            os.path.join(os.path.expanduser("~"), ".themes", name),
            os.path.join(os.path.expanduser("~"), ".local", "share", "themes", name),
            f"/usr/share/themes/{name}",
        ]
        return any(os.path.isdir(p) for p in candidates)
    except Exception:
        return False

def apply_app_css(mode=None):
    """Apply the theme style; mode is dark/light/system, None means use the saved preference."""
    global _css_provider
    try:
        if mode is None:
            mode = load_theme_pref()
        resolved = resolve_theme_mode(mode)
        css = build_css(resolved)

        # Sync GTK's own dark preference so native widgets (dialogs, menus) match
        try:
            settings = Gtk.Settings.get_default()
            if settings is not None:
                settings.set_property("gtk-application-prefer-dark-theme", resolved == "dark")
                # Force client-side decorations so GTK (not KWin) paints the dialog title
                # area; otherwise KWin uses the light system colours and leaves a white strip
                # that our CSS cannot override.
                try:
                    settings.set_property("gtk-decoration-layout", "menu:minimize,maximize,close")
                    if settings.find_property("gtk-dialogs-use-header") is not None:
                        settings.set_property("gtk-dialogs-use-header", True)
                except Exception:
                    pass
                # The system GTK theme (e.g. "Breeze" on a light desktop) also paints the
                # client-side decoration frame. When the app runs in dark mode on a light
                # system theme, that frame shows up as a white strip above the header bar.
                # Switching the GTK theme to its dark variant keeps the window edge consistent.
                if resolved == "dark":
                    _orig_theme = settings.get_property("gtk-theme-name") or ""
                    if _orig_theme and "dark" not in _orig_theme.lower():
                        # Try the common dark variants of the current theme first
                        for cand in (f"{_orig_theme}-dark", f"{_orig_theme}-Dark",
                                     "Adwaita-dark", "Breeze-Dark"):
                            if _gtk_theme_available(cand):
                                settings.set_property("gtk-theme-name", cand)
                                break
        except Exception:
            pass

        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode('utf-8'))
        screen = Gdk.Screen.get_default()
        if screen is None:
            return
        # Remove the old provider first to avoid duplicated stacking that breaks the styles
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
        print(f"Failed to apply style: {e}")

def load_icon_pixbuf(name, size=24):
    """Prefer local icons under the script's emoji_icons/ directory; fall back to embedded icons."""
    if not name:
        return None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "emoji_icons", name)
    if os.path.exists(icon_path):
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, size, size)
        except Exception as e:
            print(f"Failed to load local icon {icon_path}: {e}")
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
            print(f"Failed to decode embedded icon {name}: {e}")
    return None

def version_tuple(v):
    out = []
    for part in str(v).split('.'):
        digits = re.sub(r'\D', '', part)
        out.append(int(digits) if digits else 0)
    # Strip trailing zeros so "1.7" and "1.7.0" are treated as the same version
    # (Without alignment, (1,7) < (1,7,0) misreads the same version as "newer", causing repeated update/downgrade prompts)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)

def compare_versions(a, b):
    ta, tb = version_tuple(a), version_tuple(b)
    # Zero-pad to equal length before comparing, avoiding misjudgment from different tuple lengths
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
    """Run a command in an available terminal emulator; returns whether it launched successfully."""
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

# Dangerous operations that require GUI-level confirmation (system-level changes with weak bash-side prompts)
# clover_install_or_reinstall writes to the EFI partition, replaces BOOTX64.EFI and modifies efibootmgr
# boot entries; a mistake can make the machine unbootable, so it must go through a confirmation dialog.
DANGEROUS_FUNCS = {"fix_boot", "fix_shared_disk", "uninstall_plugin_store", "clear_hosts_cache",
                   "clover_install_or_reinstall", "health_check"}

# Extra risk description per dangerous function (falls back to the generic text)
DANGEROUS_HINTS = {
    "clover_install_or_reinstall": "This will write Clover boot files to the EFI system partition, "
                                   "replace BOOTX64.EFI and modify EFI boot entries.\n"
                                   "Improper operation may make the device unbootable; make sure you understand the risks and have a backup.",
    "fix_boot": "This will modify the EFI boot order and set Clover as the first boot entry.",
    "fix_shared_disk": "This will modify /etc/fstab and the UDisks2 policy file to auto-mount the Windows partition.",
    "uninstall_plugin_store": "This will delete the installed plugin store and its plugin data.",
    "clear_hosts_cache": "This will modify the system /etc/hosts file (a backup is created automatically).",
    "health_check": "This will check the ESP partition, UEFI boot entries, Clover boot files and /etc/fstab.\n"
                    "The check is read-only; the system is only modified after you confirm a fix (fstab is backed up before modification).",
}
DEFAULT_DANGEROUS_HINT = "This will modify system boot, mount or system files; make sure you understand the risks."

# ============================================================================
# Embedded Bash script
# ============================================================================
BASH_SCRIPT = r'''#!/bin/bash
set -uo pipefail
TEMP_DIR="/tmp/steamdeck_toolbox"
cleanup_temp() { rm -rf "$TEMP_DIR" 2>/dev/null; }
# SteamOS read-only mode: automatically restore when the script exits (sudo -n non-interactive, to avoid hanging on a password prompt)
# Key point: only restore when the script itself disabled read-only mode.
# Otherwise, if the user manually set the system to writable (disabled), running any function would force it back to
# enabled on exit, overriding the user's own setting.
RO_READONLY_DISABLED_BY_US=0
restore_readonly() {
    command -v steamos-readonly &>/dev/null || return 0
    # The script never touched the read-only switch -> keep the user's original state, never enable it on our own
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
trap 'restore_readonly; cleanup_temp; exit 0' EXIT
trap 'echo -e "\n${YELLOW}User cancelled the operation, closing window.${NC}"; cleanup_temp; exit 0' INT TERM

PYTHON_CMD="python3"
command -v python3 &>/dev/null || PYTHON_CMD="python"
# Current user/group: do not hard-code deck; on devices with a non-deck user name the file ownership would be wrong
CURRENT_USER="${USER:-$(id -un)}"
CURRENT_GROUP="$(id -gn "$CURRENT_USER" 2>/dev/null || echo "$CURRENT_USER")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'; NC='\033[0m'

# Global download source: GitHub official only (no third-party mirrors).
# Usage: ${source prefix}${full GitHub URL}. The official prefix is an empty string,
# so the complete GitHub URL is used directly.
MIRRORS=(
    ""                          # GitHub official (empty prefix = use the original GitHub URL directly)
)
# Human-readable names, one-to-one with MIRRORS
MIRROR_LABELS=(
    "GitHub (official source)"
)


# Safely parse lsblk -P output (avoid eval injection); variable names match the lsblk fields
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
    read -n1 -p "Press Enter or A to confirm, any other key to cancel: " confirm < /dev/tty
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

install_flatpak_app() {
    local app_title="$1" desktop_name="$2" categories="$3"; shift 3
    local app_ids=("$@")
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Installing ${app_title} ════════════════${NC}"

    local already_installed=""
    for app_id in "${app_ids[@]}"; do
        flatpak info "$app_id" &>/dev/null && already_installed="$app_id" && break
    done
    if [ -n "$already_installed" ]; then
        echo -e "${GREEN}✓ ${app_title} is already installed (${already_installed}), no need to install again.${NC}"
        return 0
    fi

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    local available_id=""
    for app_id in "${app_ids[@]}"; do
        if timeout 10 flatpak remote-info flathub "$app_id" &>/dev/null; then
            available_id="$app_id"; break
        else
            echo -e "${YELLOW}${app_id} does not exist or the query timed out, trying the next one...${NC}"
        fi
    done
    [ -z "$available_id" ] && echo -e "${RED}✗ No installable package found for ${app_title}.${NC}" && return 1

    echo "Installing ${available_id} ..."
    if flatpak install flathub "$available_id" -y 2>/dev/null; then
        echo -e "${GREEN}✓ ${app_title} installed successfully${NC}"
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
        echo -e "${GREEN}✓ Desktop shortcut created${NC}"
    else
        echo -e "${RED}✗ Installation failed, please check your network or install manually.${NC}"
    fi
}

uninstall_flatpak_app() {
    local app_title="$1" desktop_name="$2"; shift 2
    local app_ids=("$@")
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Uninstalling ${app_title} ════════════════${NC}"
    local installed=""
    for pkg in "${app_ids[@]}"; do flatpak info "$pkg" &>/dev/null && installed="$pkg" && break; done
    [ -z "$installed" ] && echo -e "${YELLOW}No installed ${app_title} detected.${NC}" && return 0

    confirm_action || { echo "Uninstall cancelled."; return 0; }
    if flatpak uninstall "$installed" -y; then
        echo -e "${GREEN}✓ ${app_title} uninstalled${NC}"
        local desktop_dir="$HOME/Desktop"
        if [ -d "$desktop_dir" ]; then
            local deleted_any=false
            for f in "$desktop_dir"/*.desktop; do
                # When the Desktop directory is empty the glob does not expand; skip the literal to avoid basename returning "*.desktop"
                [ -e "$f" ] || continue
                local base=$(basename "$f")
                # Only two things count: (1) a .desktop whose name is exactly the display name / app ID
                #           (2) a file name containing the full app ID (dot or underscore form, e.g. com_qq_QQ.desktop)
                # Do not use ${installed//./_} for substring matching: com.qq.QQ would also delete
                # unrelated shortcuts such as com_qq_QQ_something.desktop.
                local id_us="${installed//./_}"
                if [ "$base" = "${desktop_name}.desktop" ] || [ "$base" = "${installed}.desktop" ] \
                   || [ "$base" = "${id_us}.desktop" ] || [ "$base" = "${installed//./-}.desktop" ]; then
                    rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ Desktop shortcut deleted: $base${NC}" && deleted_any=true
                fi
            done
            $deleted_any || echo -e "${YELLOW}No matching desktop shortcut found.${NC}"
        fi

        local data_dir="$HOME/.var/app/$installed"
        if [ -d "$data_dir" ]; then
            echo ""
            echo -e "${CYAN}Delete all settings and user data for this app?${NC}"
            confirm_action && rm -rf "$data_dir" && echo -e "${GREEN}✓ User data deleted${NC}" || echo -e "${YELLOW}User data kept.${NC}"
        fi
        echo ""
        echo -e "${GREEN}${app_title} uninstall finished.${NC}"
    else
        echo -e "${RED}✗ Uninstall failed${NC}"
    fi
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
    sudo swapoff /home/swapfile 2>/dev/null; sudo swapoff -a 2>/dev/null
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
        if sudo zramctl /dev/zram0 --reset 2>/dev/null; then
            echo -e "${GREEN}✓ ZRAM reset${NC}"
        else
            echo -e "${YELLOW}⚠️ ZRAM reset failed (the device may still be in use), try again after a reboot.${NC}"
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
    echo "  Running ntfsfix ..."
    if sudo ntfsfix "$device" 2>/dev/null; then echo -e "${GREEN}  ✓ Repair succeeded${NC}"; else echo -e "${RED}  ✗ Repair failed, please check the dmesg output${NC}"; sudo dmesg | grep -i ntfs | tail -5; fi
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
    # Only after confirming an NTFS partition exists is root access needed
    # ------------------------------------------------------------------
    if ! command -v ntfsfix &> /dev/null; then
        echo ""
        echo -e "${RED}Error: ntfsfix is not installed.${NC}"
        echo "Please install the ntfs-3g package:"
        echo "  sudo pacman -S ntfs-3g   (Arch/SteamOS)"
        echo "  sudo apt install ntfs-3g (Debian/Ubuntu)"
        return 1
    fi

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

    case $fix_choice in
        1)
            for idx in "${dirty_indices[@]}"; do
                fix_single_ntfs "${ntfs_devices[$idx]}" "${ntfs_mountpoints[$idx]}"
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
                fix_single_ntfs "${ntfs_devices[$target_idx]}" "${ntfs_mountpoints[$target_idx]}"
            done
            ;;
        3|*)
            echo "Operation cancelled."
            ;;
    esac

    _restore_readonly_after_fix
    echo ""
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

steamdeck_cache_manager() {
    # Without zenity the old code still called zenity to report an error, showing nothing at all; now write to standard output
    if ! command -v zenity &>/dev/null; then
        echo -e "${RED}✗ zenity not found, cannot open the cache manager. Please install it first: sudo pacman -S zenity${NC}"
        return 1
    fi
    mk_temp_dir

    # Collect the steamapps directory of every Steam library: the default library plus the others listed in libraryfolders.vdf.
    # The old implementation hard-coded only $HOME/.local/share/Steam/steamapps, so libraries on an SD card / second disk
    # never appeared in the list (on this machine the VDF really does contain /run/media/deck/Game/SteamLibrary).
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
        zenity --error --text="Steam library directory not found, please confirm Steam is installed and you have logged in at least once."
        return 1
    fi

    # Warn the user to quit Steam before deleting compatdata/shader cache, otherwise data in use may be corrupted
    local steam_running=0
    if pgrep -x steam >/dev/null 2>&1 || pgrep -x steamwebhelper >/dev/null 2>&1; then
        steam_running=1
        if ! zenity --question --title="Steam is running" \
            --text="Steam is detected running. Deleting compatibility data may damage Proton prefixes that are in use. It is recommended to quit Steam before cleaning. Continue anyway?" \
            --ok-label="Continue" --cancel-label="Cancel"; then
            return 0
        fi
    fi

    while true; do
        local choice
        # The first column of a radio list must contain one TRUE, otherwise pressing OK returns empty and the user thinks nothing happened
        choice=$(zenity --list --radiolist \
            --title="Steam Cache Manager" \
            --text="Please choose the cache type to clean" \
            --column="Select" --column="Type" --column="Description" \
            TRUE  "Shader cache" "shadercache, rebuilt automatically after deletion" \
            FALSE "Compatibility data" "compatdata, contains each game's Proton prefix" \
            --width=600 --height=240) || break
        [ -z "$choice" ] && break

        local cache_type title
        if [ "$choice" = "Shader cache" ]; then
            cache_type="shadercache"; title="Shader cache"
        else
            cache_type="compatdata"; title="Compatibility data"
        fi

        # Store in parallel arrays, to avoid joining game names into a |-separated string (names containing | would misalign parsing)
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
                [ -z "$game_name" ] && game_name="Unknown app"
                app_ids+=("$app_id"); app_names+=("$game_name")
                app_sizes+=("$size"); app_dirs+=("$dir")
            done
        done

        if [ ${#app_ids[@]} -eq 0 ]; then
            zenity --info --text="Nothing to clean was found for $title."
            continue
        fi

        local -a list_data=()
        local i
        for i in "${!app_ids[@]}"; do
            list_data+=("FALSE" "${app_ids[$i]}" "${app_names[$i]}" "${app_sizes[$i]}MB")
        done

        local selections
        # The ID column is hidden but used for matching on return: avoid matching by "display name" (breaks on duplicates / names containing |)
        selections=$(zenity --list --checklist \
            --title="Choose the $title to delete" \
            --text="${#app_ids[@]} item(s) in total, check multiple items and click OK." \
            --column="Select" --column="ID" --column="App name" --column="Size" \
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
            zenity --info --text="No valid items selected."
            continue
        fi

        # List the specific items and total size in the confirmation dialog so the user sees exactly what will be deleted
        local total_mb=0 label one_mb
        for i in "${!sel_dirs[@]}"; do
            label="${sel_labels[$i]}"
            # When du fails its output is empty, and using it directly in $(( )) raises an arithmetic syntax error; fall back to 0 first
            one_mb=$(du -sm "${sel_dirs[$i]}" 2>/dev/null | cut -f1)
            [[ "$one_mb" =~ ^[0-9]+$ ]] || one_mb=0
            total_mb=$((total_mb + one_mb))
        done
        local confirm_text="The following $title will be permanently deleted:"
        for label in "${sel_labels[@]}"; do
            confirm_text+=$'\n'"  • $label"
        done
        confirm_text+=$'\n\n'"${#sel_dirs[@]} item(s), about ${total_mb}MB, this cannot be undone."
        zenity --question --title="Confirm deletion" --text="$confirm_text" \
            --ok-label="Delete" --cancel-label="Cancel" || continue

        local deleted=0 failed=0
        for i in "${!sel_dirs[@]}"; do
            if rm -rf -- "${sel_dirs[$i]}" 2>/dev/null; then
                deleted=$((deleted + 1))
            else
                failed=$((failed + 1))
            fi
        done

        local result_text="Deletion complete."
        result_text+=$'\n'"Succeeded: $deleted item(s)"
        result_text+=$'\n'"Failed: $failed item(s)"
        [ "$failed" -gt 0 ] && result_text+=$'\n\n'"Failed items may be in use; quit Steam and try again."
        [ "$steam_running" -eq 1 ] && result_text+=$'\n'"It is recommended to restart Steam so the cache is rebuilt."
        zenity --info --text="$result_text"
    done
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

    # 1) An already mounted /esp or /boot/efi
    for mp in /esp /boot/efi; do
        dev=$(findmnt -n -o SOURCE -M "$mp" 2>/dev/null | grep '^/dev/' | head -1 || true)
        [ -n "$dev" ] || dev=$(mount 2>/dev/null | awk -v m="$mp" '$3 == m {print $1; exit}')
        if [ -n "$dev" ] && [ -b "$dev" ]; then ESP_DEV="$dev"; break; fi
    done
    # 2) Find by the EFI partition type GUID
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

# Check whether the Clover boot files exist on the ESP (decides whether "rebuild boot entries" makes sense)
# Return values: 0 = files exist; 1 = confirmed missing; 2 = cannot tell (permission/mount problem)
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
    local files_rc=$?
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

fix_shared_disk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Automatically mount Windows partitions ════════════════${NC}"
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

    echo "Step 2: Modify the UDisks2 permission file"
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

    echo "Step 3: Scanning Windows (NTFS) partitions (ignoring recovery partitions)..."
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

    echo "Step 4: Cleaning up mounts and fstab entries of non-Windows partitions under /run/media/deck/..."
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

    echo "Step 5: Mounting and writing to fstab..."
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
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g rw,exec,uid=1000,gid=1000,windows_names,nofail 0 0"
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
                    printf '%s\n' "UUID=$uuid $mount_point ntfs-3g rw,exec,uid=1000,gid=1000,windows_names,nofail 0 0"
                } > "$_tmp2" 2>/dev/null && chmod 644 "$_tmp2" 2>/dev/null \
                    && sudo cp "$_tmp2" /etc/fstab && rm -f "$_tmp2" \
                    && echo "  fstab entry added." \
                    || { rm -f "$_tmp2"; echo -e "${RED}  ✗ Failed to write fstab${NC}"; ((fail_count++)); }
            fi
        fi

        if mountpoint -q "$mount_point" 2>/dev/null; then
            echo "  Partition mounted at $mount_point"
        else
            if sudo systemctl daemon-reload 2>/dev/null; then :; fi
            if sudo mount "$mount_point" 2>/dev/null || sudo mount -U "$uuid" "$mount_point" 2>/dev/null; then
                echo -e "${GREEN}  ✓ Mounted successfully at $mount_point${NC}"
            else
                echo -e "${RED}  ✗ Mount failed, please check the dmesg output.${NC}"
                echo "  Recent NTFS-related dmesg errors:"
                sudo dmesg 2>/dev/null | grep -i ntfs | tail -5
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

# ============================================================================
# System health check: diagnose "missing disk / missing boot entry / mount failure" after a SteamOS update
# Read-only checks; no system configuration is modified unless the user explicitly chooses a repair item
# ============================================================================
# Dynamically detect the ESP partition (do not hard-code /dev/nvme0n1p1: eMMC is mmcblk0 and the partition number may not be 1)
detect_esp_partition() {
    local dev="" line
    ESP_DEV=""; ESP_DISK=""; ESP_PARTN=""; ESP_MOUNT=""
    # 1) A mounted /esp (SteamOS) or /boot/efi (Bazzite)
    #    Note: findmnt -M also returns systemd autofs "systemd-1"; filter to a real device starting with /dev/
    for mp in /esp /boot/efi; do
        dev=$(findmnt -n -o SOURCE -M "$mp" 2>/dev/null | grep '^/dev/' | head -1 || true)
        if [ -z "$dev" ]; then
            # Fallback: find the device for that mount point in the mount output
            dev=$(mount 2>/dev/null | awk -v m="$mp" '$3 == m {print $1; exit}')
        fi
        if [ -n "$dev" ] && [ -b "$dev" ]; then
            ESP_DEV="$dev"; ESP_MOUNT="$mp"; break
        fi
    done
    # 2) Find by the EFI partition type GUID (c12a7328-f81f-11d2-ba4b-00a0c93ec93b)
    if [ -z "$ESP_DEV" ]; then
        dev=$(lsblk -P -n -o PATH,PARTTYPE 2>/dev/null \
            | awk -F'"' '/PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b"/{print $2; exit}' || true)
        [ -n "$dev" ] && [ -b "$dev" ] && ESP_DEV="$dev"
    fi
    [ -n "$ESP_DEV" ] || return 1
    # Note: lsblk output may have leading/trailing spaces and must be trimmed, otherwise efibootmgr -p " 1" fails
    ESP_DISK="/dev/$(lsblk -n -o PKNAME "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')"
    ESP_PARTN=$(lsblk -n -o PARTN "$ESP_DEV" 2>/dev/null | head -1 | tr -d '[:space:]')
    [ -n "$ESP_PARTN" ] || ESP_PARTN=1
    return 0
}

# Check result accumulators
HC_TOTAL=0; HC_OK=0; HC_WARN=0; HC_FAIL=0
HC_FIXABLE=()      # Numbers of problems that can be fixed automatically
hc_result() {
    # $1=status ok/warn/fail  $2=title  $3=description  $4=fixable(1/0)  $5=repair function name
    HC_TOTAL=$((HC_TOTAL + 1))
    case "$1" in
        ok)   HC_OK=$((HC_OK + 1));   echo -e "  ${GREEN}[OK]${NC} $2";;
        warn) HC_WARN=$((HC_WARN + 1)); echo -e "  ${YELLOW}[Warning]${NC} $2";;
        fail) HC_FAIL=$((HC_FAIL + 1)); echo -e "  ${RED}[Error]${NC} $2";;
    esac
    [ -n "$3" ] && echo -e "         $3"
    if [ "${4:-0}" -eq 1 ] && [ -n "${5:-}" ]; then
        HC_FIXABLE+=("$1|$2|$5")
        echo -e "         ${CYAN}-> Can be handled with the Repair option below${NC}"
    fi
}

# ---------- Individual checks ----------
hc_check_esp() {
    echo -e "${CYAN}[1/6] ESP (EFI system partition)${NC}"
    if detect_esp_partition; then
        hc_result ok "ESP partition identified" "$ESP_DEV mounted at $ESP_MOUNT"
        # Free space check (Clover needs about 15MB)
        local avail
        avail=$(df --output=avail "$ESP_DEV" 2>/dev/null | tail -1 | tr -d ' ')
        if [[ "$avail" =~ ^[0-9]+$ ]]; then
            if [ "$avail" -ge 15000 ]; then
                hc_result ok "ESP free space is sufficient" "about $((avail / 1024))MB available"
            else
                hc_result warn "ESP free space is small" "only about $((avail / 1024))MB, installing Clover needs about 15MB"
            fi
        fi
        # EFI directory readability (root needed to list /esp/efi/EFI)
        if sudo -n ls "$ESP_MOUNT/efi/EFI" &>/dev/null || sudo -n ls "$ESP_MOUNT/EFI" &>/dev/null; then
            hc_result ok "ESP can be read normally" ""
        else
            hc_result warn "Cannot read the ESP contents (sudo required)" "please confirm sudo is available and try again"
        fi
    else
        hc_result fail "Cannot identify the ESP partition" "no mounted /esp found, and it could not be located by EFI partition type either"
    fi
    echo ""
}

hc_check_efi_entries() {
    echo -e "${CYAN}[2/6] UEFI boot entries${NC}"
    if ! command -v efibootmgr &>/dev/null; then
        hc_result fail "efibootmgr not found" "please install: sudo pacman -S efibootmgr"
        echo ""; return
    fi
    local efi_out
    efi_out=$(sudo -n efibootmgr 2>/dev/null || efibootmgr 2>/dev/null || true)
    if [ -z "$efi_out" ]; then
        hc_result fail "Cannot read the UEFI boot entries" "efibootmgr execution failed"
        echo ""; return
    fi
    # Clover boot entry
    if echo "$efi_out" | grep -qi "clover"; then
        local cl_num
        cl_num=$(echo "$efi_out" | grep -i "clover" | head -1 | grep -o 'Boot[0-9A-Fa-f]\{4\}' | head -1)
        hc_result ok "Clover boot entry exists" "$cl_num"
    else
        hc_result fail "Clover boot entry is missing" "common after a SteamOS update or firmware reset; it will be rebuilt from the ESP automatically" 1 "hc_repair_boot"
    fi
    # SteamOS boot entry
    if echo "$efi_out" | grep -qi "steamos\|steamcl"; then
        hc_result ok "SteamOS boot entry exists" ""
    else
        hc_result fail "SteamOS boot entry is missing" "will be rebuilt from the ESP (Clover is checked as well)" 1 "hc_repair_boot"
    fi
    # Windows boot entry (not required: Clover takes over)
    if echo "$efi_out" | grep -qi "windows"; then
        hc_result ok "Windows boot entry exists" ""
    else
        hc_result warn "Windows boot entry is missing (Clover takes over, usually normal)" "only needed to boot Windows directly from the firmware menu"
    fi
    # Boot order
    local order first
    order=$(echo "$efi_out" | grep "BootOrder" | cut -d: -f2 | tr -d ' ')
    first=$(echo "$order" | cut -d, -f1)
    if [ -n "$first" ] && echo "$efi_out" | grep -i "clover" | grep -q "Boot$first"; then
        hc_result ok "Clover is the first boot entry" "BootOrder: $order"
    else
        hc_result warn "Clover is not the first boot entry" "current order: ${order:-unknown}" 1 "hc_repair_boot"
    fi
    echo ""
}

hc_check_clover_files() {
    echo -e "${CYAN}[3/6] Clover boot file integrity${NC}"
    if [ -z "${ESP_DEV:-}" ]; then
        hc_result warn "Skipped: ESP not identified" ""
        echo ""; return
    fi
    # If the ESP is not mounted, mount it temporarily on a read-only directory to check its contents
    local tmp_mount="" efi_root=""
    if [ -z "${ESP_MOUNT:-}" ]; then
        tmp_mount=$(mktemp -d 2>/dev/null) || tmp_mount=""
        if [ -n "$tmp_mount" ] && sudo -n mount -o ro "$ESP_DEV" "$tmp_mount" 2>/dev/null; then
            ESP_MOUNT="$tmp_mount"
        else
            rmdir "$tmp_mount" 2>/dev/null
            hc_result warn "ESP is not mounted and cannot be mounted temporarily for the check" "please mount it first: sudo mount $ESP_DEV /mnt"
            echo ""; return
        fi
    fi
    # Locate the EFI directory: on different models/systems EFI may be at the ESP root or in an efi subdirectory
    # (the SteamOS Clover install script uses /esp/efi, but the boot path recorded by efibootmgr is \EFI\...
    #  relative to the ESP root, so both layouts may exist). Do not rely on a normal user's [ -d ] test --
    # /esp has permissions 700 root, a normal user can never see it, and the directory would be wrongly judged missing.
    efi_root=""
    local cand
    for cand in "$ESP_MOUNT/EFI" "$ESP_MOUNT/efi/EFI"; do
        if sudo -n ls "$cand" &>/dev/null; then
            efi_root="$cand"; break
        fi
    done

    if [ -z "$efi_root" ]; then
        # Then try the parent directory to tell "no permission" from "the directory really does not exist"
        if sudo -n ls "$ESP_MOUNT" &>/dev/null; then
            local top_list
            top_list=$(sudo -n ls "$ESP_MOUNT" 2>/dev/null || true)
            hc_result fail "No EFI boot directory found on the ESP" \
                "ESP root directory contents: $(echo "$top_list" | tr '\n' ' '). The boot files may have been removed by a SteamOS update; Clover needs to be reinstalled"
        else
            hc_result warn "Cannot read the EFI directory on the ESP (sudo password required)" \
                "Clover file check skipped this time; enter the password during the health check, or run manually: sudo ls $ESP_MOUNT"
        fi
        [ -n "$tmp_mount" ] && { sudo -n umount "$tmp_mount" 2>/dev/null; rmdir "$tmp_mount" 2>/dev/null; }
        echo ""; return
    fi
    hc_result ok "EFI directory located" "$efi_root"

    # List the actual contents for a more accurate judgement
    local efi_list
    efi_list=$(sudo -n ls "$efi_root" 2>/dev/null || true)

    # Clover main program
    if sudo -n test -f "$efi_root/clover/cloverx64.efi" 2>/dev/null; then
        hc_result ok "Clover EFI main program exists" "$efi_root/clover/cloverx64.efi"
    elif echo "$efi_list" | grep -qx "clover"; then
        hc_result fail "Clover directory exists but cloverx64.efi is missing" "boot files are incomplete, Clover needs to be reinstalled"
    else
        hc_result fail "Clover EFI main program is missing" "Clover needs to be reinstalled (Boot Management -> Install/Reinstall Clover)"
    fi
    # Clover config
    if sudo -n test -f "$efi_root/clover/config.plist" 2>/dev/null; then
        hc_result ok "Clover config file exists" ""
    elif echo "$efi_list" | grep -qx "clover"; then
        hc_result warn "Clover config file is missing" "reinstalling Clover restores the default config"
    fi
    # Whether BOOTX64.EFI is Clover (the original file should have been backed up as .orig)
    local boot_dir=""
    for cand in BOOT boot; do
        if echo "$efi_list" | grep -qx "$cand"; then boot_dir="$cand"; break; fi
    done
    if [ -n "$boot_dir" ]; then
        if sudo -n test -f "$efi_root/$boot_dir/BOOTX64.EFI" 2>/dev/null \
            || sudo -n test -f "$efi_root/$boot_dir/bootx64.efi" 2>/dev/null; then
            if sudo -n test -f "$efi_root/$boot_dir/BOOTX64.EFI.orig" 2>/dev/null \
                || sudo -n test -f "$efi_root/$boot_dir/bootx64.efi.orig" 2>/dev/null; then
                hc_result ok "BOOTX64.EFI is taken over by Clover" "the original file was backed up as .orig"
            else
                hc_result warn "No BOOTX64.EFI backup (.orig) found" "usually harmless as long as Clover still boots"
            fi
        else
            hc_result warn "bootx64.efi not found in the BOOT directory" ""
        fi
    fi
    # Unmount the temporary mount point
    if [ -n "$tmp_mount" ]; then
        sudo -n umount "$tmp_mount" 2>/dev/null
        rmdir "$tmp_mount" 2>/dev/null
    fi
    echo ""
}

hc_check_windows_partition() {
    echo -e "${CYAN}[4/6] Windows partitions${NC}"
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
        hc_result warn "No NTFS partition found" "if this really is a Windows dual-boot, check whether the disk is loose or the partition table is abnormal"
        echo ""; return
    fi
    if [ -n "$win_dev" ]; then
        hc_result ok "Windows partition exists" "$win_dev${win_mp:+ mounted at $win_mp}"
        if [ -n "$win_mp" ] && [ -d "$win_mp" ]; then
            hc_result ok "Windows partition is mounted" "$win_mp"
        else
            hc_result warn "Windows partition is not mounted" "it will be written to fstab for automatic mounting at boot" 1 "hc_repair_mount"
        fi
        # Check the real Windows file structure (confirm it is not an empty partition)
        local check_mp="$win_mp"
        if [ -z "$check_mp" ] || [ ! -d "$check_mp" ]; then
            for base in /run/media/*/"$nm" /media/*/"$nm"; do
                [ -d "$base" ] && check_mp="$base" && break
            done
        fi
        if [ -n "$check_mp" ] && [ -d "$check_mp" ]; then
            if [ -d "$check_mp/Windows" ] && { [ -d "$check_mp/Program Files" ] || [ -d "$check_mp/Users" ]; }; then
                hc_result ok "Windows system files are complete" "Windows/Program Files/Users detected"
            else
                hc_result warn "No Windows system files found in the partition" "it may be a pure data disk, or Windows has been deleted"
            fi
        fi
    else
        hc_result warn "No NTFS partition labeled Windows found" "it may be a pure data disk; if Windows is confirmed, check the partition label"
    fi
    echo ""
}

hc_check_fstab() {
    echo -e "${CYAN}[5/6] /etc/fstab mount configuration${NC}"
    if [ ! -f /etc/fstab ]; then
        hc_result fail "/etc/fstab not found" ""
        echo ""; return
    fi
    local bad=0 total=0
    while IFS= read -r line; do
        # Skip comments and blank lines
        case "$line" in ''|\#*) continue;; esac
        local dev mp rest uuid
        dev=$(echo "$line" | awk '{print $1}')
        mp=$(echo "$line" | awk '{print $2}')
        [ -z "$dev" ] && continue
        total=$((total + 1))
        # UUID= form: verify it can be found in blkid
        case "$dev" in
            UUID=*)
                uuid="${dev#UUID=}"
                if ! lsblk -P -n -o UUID 2>/dev/null | grep -q "UUID=\"$uuid\""; then
                    # /home/swapfile and the like are not partitions; check them separately
                    if [ "$dev" = "/home/swapfile" ] || echo "$dev" | grep -q "/"; then
                        :
                    else
                        echo -e "  ${RED}[Error]${NC} fstab entry points to a non-existent partition: $dev -> $mp"
                        bad=$((bad + 1))
                    fi
                fi
                ;;
            /home/swapfile)
                if [ ! -f /home/swapfile ]; then
                    echo -e "  ${RED}[Error]${NC} fstab references /home/swapfile but the file does not exist"
                    bad=$((bad + 1))
                fi
                ;;
        esac
    done < /etc/fstab
    if [ "$bad" -eq 0 ]; then
        hc_result ok "fstab entries are valid" "$total valid configuration(s) in total"
    else
        hc_result fail "fstab has $bad invalid entry/entries" "invalid entries can slow down boot or drop into rescue mode" 1 "hc_fix_fstab_invalid"
    fi
    # Check whether systemd reports mount failures
    local failed_units
    failed_units=$(systemctl list-units --state=failed --no-legend --plain 2>/dev/null | grep -cE '\.mount|\.swap' || true)
    if [ "${failed_units:-0}" -gt 0 ]; then
        hc_result fail "$failed_units mount unit(s) failed" "systemctl --failed shows the details"
    else
        hc_result ok "No failed mount units" ""
    fi
    echo ""
}

hc_check_system() {
    echo -e "${CYAN}[6/6] System and boot services${NC}"
    # SteamOS read-only mode
    if command -v steamos-readonly &>/dev/null; then
        local ro
        ro=$(steamos-readonly status 2>/dev/null || true)
        if echo "$ro" | grep -q "enabled"; then
            hc_result ok "SteamOS read-only mode is normal (enabled)" ""
        else
            hc_result warn "SteamOS read-only mode is disabled" "it usually restores itself when no files are changed; staying writable long-term risks being overwritten by updates"
        fi
    fi
    # clover-bootmanager service (the key to self-healing after a lost boot entry)
    local has_clover_svc=0
    if systemctl list-unit-files --no-legend --plain 2>/dev/null \
        | awk '$1 == "clover-bootmanager.service" {found=1} END {exit !found}'; then
        has_clover_svc=1
    fi
    if [ "$has_clover_svc" -eq 1 ]; then
        if systemctl is-enabled clover-bootmanager.service &>/dev/null; then
            hc_result ok "Clover boot guard service is enabled" "rebuilds lost boot entries automatically at boot"
        else
            hc_result fail "Clover boot guard service is not enabled" "when enabled it rebuilds boot entries automatically after updates" 1 "hc_fix_enable_service"
        fi
        if systemctl is-active clover-bootmanager.service &>/dev/null; then
            hc_result ok "Clover boot guard service is running" ""
        else
            hc_result warn "Clover boot guard service is not running" "it can be started manually"
        fi
    else
        hc_result warn "Clover boot guard service is not installed" "it is installed together with Clover"
    fi
    # Kernel and system version (to see whether an update just happened)
    hc_result ok "Current kernel version: $(uname -r)" ""
    local os_pretty
    os_pretty=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')
    hc_result ok "System version: ${os_pretty:-unknown}" ""
    echo ""
}

# ---------- Repair actions ----------



hc_fix_enable_service() {
    if sudo systemctl enable --now clover-bootmanager.service 2>/dev/null; then
        echo -e "${GREEN}✓ Clover boot guard service enabled${NC}"
        return 0
    fi
    echo -e "${RED}✗ Failed to enable, please run manually: sudo systemctl enable --now clover-bootmanager.service${NC}"
    return 1
}

hc_fix_fstab_invalid() {
    echo -e "${CYAN}Backing up /etc/fstab and commenting out invalid entries...${NC}"
    local backup="/etc/fstab.backup.$(date +%Y%m%d_%H%M%S)"
    if ! sudo cp /etc/fstab "$backup" 2>/dev/null; then
        echo -e "${RED}✗ Backup failed, aborted for safety${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Backed up to $backup${NC}"
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
                    echo "# [health check] partition does not exist, commented out: $line"
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
        echo -e "${YELLOW}No entries needed commenting out${NC}"
        return 0
    fi
    if sudo cp "$tmp" /etc/fstab; then
        rm -f "$tmp"
        sudo systemctl daemon-reload 2>/dev/null
        echo -e "${GREEN}✓ Commented out $changed invalid entry/entries (original file backed up at $backup)${NC}"
        return 0
    fi
    rm -f "$tmp"
    echo -e "${RED}✗ Write failed, /etc/fstab was not modified${NC}"
    return 1
}

# Interactive repair entry point
hc_run_fixes() {
    if [ ${#HC_FIXABLE[@]} -eq 0 ]; then
        echo -e "${GREEN}No problems that can be fixed automatically were found.${NC}"
        return 0
    fi
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}✗ Repair requires sudo permission, skipped${NC}"
        return 1
    fi
    echo -e "${YELLOW}════════════════ Starting the repair ════════════════${NC}"
    local item state title fn
    for item in "${HC_FIXABLE[@]}"; do
        state="${item%%|*}"
        title="${item#*|}"; title="${title%%|*}"
        fn="${item##*|}"
        echo ""
        echo -e "${CYAN}Repair: $title${NC}"
        case "$fn" in
            fix_boot)
                hc_repair_boot
                ;;
            fix_shared_disk)
                # "Repair shared drive" clears the screen and reopens an interactive UI; here its core action is executed directly
                hc_repair_mount
                ;;
            *)
                if declare -f "$fn" >/dev/null; then
                    "$fn"
                else
                    echo -e "${RED}Internal error: repair function $fn does not exist${NC}"
                fi
                ;;
        esac
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}This repair did not succeed, please check the messages above${NC}"
        fi
    done
    echo ""
    echo -e "${YELLOW}Tip: after repairing, run the health check again to confirm the result.${NC}"
}

# ---------------------------------------------------------------------------
# Boot repair inlined in the health check (reuses fix_boot's detection and rebuild logic, without reopening a separate UI)
# ---------------------------------------------------------------------------
hc_repair_boot() {
    if ! detect_esp_partition; then
        echo -e "${RED}✗ Cannot identify the ESP partition, repair aborted${NC}"
        return 1
    fi
    local efi_out
    efi_out=$(efibootmgr 2>/dev/null || true)
    local ro_fix_ok=0

    # 1) Clover boot entry
    if echo "$efi_out" | grep -qi "clover"; then
        echo -e "${CYAN}Clover boot entry already exists, skipping the rebuild${NC}"
    else
        echo -e "${CYAN}Rebuilding the Clover boot entry ($ESP_DISK partition $ESP_PARTN)...${NC}"
        # Clean up leftover entries with the same name
        local old
        for old in $(echo "$efi_out" | grep -i "clover" | grep -o 'Boot[0-9A-Fa-f]\{4\}' | sed 's/Boot//'); do
            sudo efibootmgr -b "$old" -B &>/dev/null || true
        done
        if sudo efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
            -L "Clover - GUI Boot Manager" -l '\EFI\clover\cloverx64.efi' &>/dev/null; then
            echo -e "${GREEN}✓ Clover boot entry rebuilt${NC}"
            ro_fix_ok=1
        else
            echo -e "${RED}✗ Failed to rebuild the Clover boot entry${NC}"
            echo -e "${YELLOW}  cloverx64.efi may be missing on the ESP, please use Install/Reinstall Clover${NC}"
            return 1
        fi
    fi

    # 2) SteamOS boot entry
    if echo "$efi_out" | grep -qi "steamos\|steamcl"; then
        echo -e "${CYAN}SteamOS boot entry already exists, skipping the rebuild${NC}"
    else
        echo -e "${CYAN}Rebuilding the SteamOS boot entry...${NC}"
        if sudo efibootmgr -c -d "$ESP_DISK" -p "$ESP_PARTN" \
            -L "SteamOS" -l '\EFI\steamos\steamcl.efi' &>/dev/null; then
            echo -e "${GREEN}✓ SteamOS boot entry rebuilt${NC}"
            ro_fix_ok=1
        else
            echo -e "${RED}✗ Failed to rebuild the SteamOS boot entry${NC}"
        fi
    fi

    # 3) Make Clover the first boot entry
    local cl
    cl=$(efibootmgr 2>/dev/null | grep -i "clover" | grep -o 'Boot[0-9A-Fa-f]\{4\}' | head -1 | sed 's/Boot//')
    if [ -n "$cl" ]; then
        local cur new
        cur=$(efibootmgr 2>/dev/null | grep "BootOrder" | cut -d: -f2 | tr -d ' ')
        new="$cl"
        if [ -n "$cur" ]; then
            new="$cl,$(echo "$cur" | tr ',' '\n' | grep -vx "$cl" | tr '\n' ',' | sed 's/,$//')"
        fi
        if [ "$cur" = "$new" ]; then
            echo -e "${CYAN}Clover is already the first boot entry, no adjustment needed${NC}"
        else
            echo -e "${CYAN}Adjusting the boot order: ${cur:-empty} -> $new${NC}"
            if sudo efibootmgr -o "$new" &>/dev/null; then
                echo -e "${GREEN}✓ Clover set as the first boot entry${NC}"
            else
                echo -e "${RED}✗ Failed to adjust the boot order${NC}"
                return 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠ Clover boot entry not found, cannot set the boot order${NC}"
    fi
    return 0
}

# ---------------------------------------------------------------------------
# Mount repair inlined in the health check: write the Windows (NTFS) partition into fstab for automatic mounting
# ---------------------------------------------------------------------------
hc_repair_mount() {
    echo -e "${CYAN}Configuring automatic mounting at boot for NTFS partitions...${NC}"
    # fstab must be backed up before writing: a broken fstab can make the next boot fail
    local backup="/etc/fstab.backup.$(date +%Y%m%d_%H%M%S)"
    if ! sudo cp /etc/fstab "$backup" 2>/dev/null; then
        echo -e "${RED}✗ Cannot back up /etc/fstab, modification aborted for safety${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ /etc/fstab backed up to $backup${NC}"
    local changed=0 failed=0
    local line nm fs lb mp uuid
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        nm=$(echo "$line" | sed -n 's/.*NAME="\([^"]*\)".*/\1/p')
        fs=$(echo "$line" | sed -n 's/.*FSTYPE="\([^"]*\)".*/\1/p')
        lb=$(echo "$line" | sed -n 's/.*LABEL="\([^"]*\)".*/\1/p')
        mp=$(echo "$line" | sed -n 's/.*MOUNTPOINT="\([^"]*\)".*/\1/p')
        uuid=$(echo "$line" | sed -n 's/.*UUID="\([^"]*\)".*/\1/p')
        case "$fs" in ntfs|fuseblk|ntfs3) ;; *) continue;; esac
        [ -n "$uuid" ] || continue
        # Skip if this UUID is already matched exactly in fstab
        if awk -v k="UUID=$uuid" '$1 == k {found=1} END {exit !found}' /etc/fstab 2>/dev/null; then
            echo -e "${CYAN}  $nm is already in fstab, skipping${NC}"
            continue
        fi
        # Decide the mount point: prefer the current mount point, otherwise /run/media/<user>/<label>
        local target="${mp:-}"
        if [ -z "$target" ] || [ "$target" = "None" ]; then
            target="/run/media/${CURRENT_USER}/${lb:-$nm}"
        fi
        echo -e "${CYAN}  Adding $nm (UUID=$uuid) -> $target${NC}"
        if echo "UUID=$uuid $target ntfs3 defaults,nofail,uid=1000,gid=1000 0 0" | sudo tee -a /etc/fstab >/dev/null; then
            changed=$((changed + 1))
        else
            failed=$((failed + 1))
        fi
    done < <(lsblk -P -n -o NAME,FSTYPE,LABEL,MOUNTPOINT,UUID 2>/dev/null)

    if [ "$changed" -gt 0 ]; then
        sudo systemctl daemon-reload 2>/dev/null
        echo -e "${GREEN}✓ Added $changed automatic mount entry/entries${NC}"
        echo -e "${CYAN}  Testing the mount now...${NC}"
        sudo mount -a 2>&1 | head -5 || true
    else
        echo -e "${CYAN}No mount entries need to be added${NC}"
    fi
    [ "$failed" -gt 0 ] && { echo -e "${RED}✗ $failed entry/entries failed to write${NC}"; return 1; }
    return 0
}

health_check() {
    mk_temp_dir
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║      SteamOS Health Check (post-update)       ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo "For troubleshooting the common issues after a SteamOS update: missing disk, missing boot entry, mount failure."
    echo "The checks are read-only; repairs are performed only after your confirmation."
    echo ""
    echo "Checking now; sudo permission is needed to read the EFI partition contents..."
    if ! sudo -v 2>/dev/null; then
        echo -e "${YELLOW}⚠ No sudo permission: some checks (ESP contents, boot entries) cannot be completed${NC}"
    fi
    echo ""
    echo -e "${CYAN}──────────────── Check results ────────────────${NC}"
    echo ""
    hc_check_esp
    hc_check_efi_entries
    hc_check_clover_files
    hc_check_windows_partition
    hc_check_fstab
    hc_check_system
    echo -e "${CYAN}──────────────── Summary ────────────────${NC}"
    echo -e "  $HC_TOTAL item(s) checked: ${GREEN}OK $HC_OK${NC} | ${YELLOW}Warning $HC_WARN${NC} | ${RED}Error $HC_FAIL${NC}"
    echo ""

    # The conclusion is based on the number of "fail" items, not "warn":
    # "warn" items are mostly environment differences (e.g. the Windows boot entry taken over by Clover, small ESP free space),
    # and do not mean boot or mounting is broken; the user should not be made to think the system is faulty.
    if [ "$HC_FAIL" -eq 0 ]; then
        if [ "$HC_WARN" -eq 0 ]; then
            echo -e "${GREEN}✅ Conclusion: the system is in good shape, no problems found.${NC}"
        else
            echo -e "${GREEN}✅ Conclusion: no errors found, boot and mounting are normal.${NC}"
            echo -e "${CYAN}   There are also $HC_WARN warning item(s), which are environment differences or optional optimizations and do not affect use (see the [Warning] items above).${NC}"
        fi
        if [ ${#HC_FIXABLE[@]} -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}${#HC_FIXABLE[@]} of them can be optimized automatically. Handle them now?${NC}"
            local ans
            if read -p "Press y to handle, any other key to skip: " -n 1 -r ans < /dev/tty 2>/dev/null; then
                echo ""
                if [[ "$ans" =~ ^[Yy]$ ]]; then
                    hc_run_fixes
                else
                    echo "Skipped. Run the health check again later to handle them."
                fi
            else
                echo -e "${YELLOW}Cannot read input (non-interactive environment), skipped.${NC}"
            fi
        fi
        echo ""
        return 0
    fi

    # Reaching here means there really are "fail" items, so prompt that action is needed
    echo -e "${RED}❌ Conclusion: $HC_FAIL error item(s) found, action is needed.${NC}"
    if [ ${#HC_FIXABLE[@]} -gt 0 ]; then
        echo -e "${YELLOW}${#HC_FIXABLE[@]} of them can be fixed automatically:${NC}"
        local item title
        for item in "${HC_FIXABLE[@]}"; do
            title="${item#*|}"; title="${title%%|*}"
            echo "   · $title"
        done
        local ans
        if read -p "Repair now? (y/N): " -n 1 -r ans < /dev/tty 2>/dev/null; then
            echo ""
            if [[ "$ans" =~ ^[Yy]$ ]]; then
                hc_run_fixes
            else
                echo "Repair skipped. Run the health check again later and choose repair."
            fi
        else
            echo -e "${YELLOW}Cannot read input (non-interactive environment), repair skipped.${NC}"
            echo "To repair, follow the 'can be fixed automatically' hints above and handle them manually."
        fi
    else
        echo -e "${YELLOW}The above errors need manual handling, please follow the hints of the [Error] items above.${NC}"
    fi
    echo ""
    echo -e "${CYAN}Common causes and suggestions:${NC}"
    echo "  · Clover boot entry disappeared after a SteamOS update -> rebuild it with Repair in this feature, or reinstall Clover"
    echo "  · Windows partitions no longer mount automatically -> run Repair shared drive"
    echo "  · Clover files on the ESP were overwritten -> reinstall Clover (Boot Management -> Install/Reinstall Clover)"
    echo "  · Completely unbootable / cannot enter the system -> rescue with a SteamOS recovery USB; this tool cannot handle that"
}

install_uu_accelerator() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install the UU accelerator plugin ════════════════${NC}"
    if curl -s uudeck.com | sudo sh; then
        echo -e "${GREEN}✓ UU accelerator plugin installed.${NC}"
    else
        echo -e "${RED}✗ Installation failed (the script returned an error code), please check your network and try again.${NC}"
        return 1
    fi
}

install_xunyou_accelerator() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install the Xunyou accelerator plugin ════════════════${NC}"
    if curl -s sd.xunyou.com | sudo sh; then
        echo -e "${GREEN}✓ Xunyou accelerator plugin installed.${NC}"
    else
        echo -e "${RED}✗ Installation failed (the script returned an error code), please check your network and try again.${NC}"
        return 1
    fi
}

install_qiyou_accelerator() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install the Qiyou accelerator plugin ════════════════${NC}"
    if curl -s sd.qiyou.cn | sudo sh; then
        echo -e "${GREEN}✓ Qiyou accelerator plugin installed.${NC}"
    else
        echo -e "${RED}✗ Installation failed (the script returned an error code), please check your network and try again.${NC}"
        return 1
    fi
}

install_asklink() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ AskLink remote assistance ════════════════${NC}"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}AskLink is installed.${NC}"
        echo -e "${YELLOW}Press Enter/A to uninstall, press any other key to keep it installed and exit.${NC}"
        read -p "Please choose: " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY == "" ]]; then
            echo -e "${CYAN}Uninstalling AskLink...${NC}"
            sudo rm -rf /opt/AskLink
            rm -f "$HOME/Desktop/AskLink.desktop"
            sudo rm -f /usr/share/applications/AskLink.desktop
            rm -f "$HOME/.local/share/applications/AskLink.desktop"
            if [ -d "$HOME/Documents/AskLink" ]; then
                rm -rf "$HOME/Documents/AskLink"
                echo -e "${CYAN}Deleted the config directory $HOME/Documents/AskLink${NC}"
            fi
            echo -e "${GREEN}✅ AskLink uninstalled.${NC}"
        else
            echo -e "${GREEN}Keeping AskLink installed.${NC}"
        fi
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
            sudo pacman -S --noconfirm dpkg
            if [ $? -ne 0 ]; then
                echo -e "${RED}Failed to install dpkg, please run manually: sudo pacman -S dpkg${NC}"
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
    if command -v wget &>/dev/null; then
        wget --show-progress "$ASKLINK_URL" -O "$FILENAME"
    else
        curl -L --fail --progress-bar "$ASKLINK_URL" -o "$FILENAME"
    fi
    if [ $? -ne 0 ] || [ ! -f "$FILENAME" ]; then
        echo -e "${RED}Download failed.${NC}"
        return 1
    fi

    echo -e "${CYAN}Installing...${NC}"
    sudo dpkg --force-depends -i "$FILENAME" 2>/dev/null

    rm -f "$FILENAME"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}✅ AskLink installed successfully!${NC}"
        local DESKTOP_FILE="$HOME/Desktop/AskLink.desktop"
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
    echo -e "${YELLOW}═══════Install/Update Watt Toolkit (Steam++) ═══════${NC}"
    echo ""

    local INSTALL_DIR="$HOME/Watt Toolkit"
    local DESKTOP_DIR="$HOME/Desktop"
    local DOWNLOAD_URL="https://github.com/BeyondDimension/SteamTools/releases/download/3.1.0/Steam%2B%2B_v3.1.0_linux_x64.tgz"
    local VERSION="3.1.0"

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
            echo -e "${YELLOW}An installation directory was detected, but the version number cannot be read.${NC}"
        fi
    else
        echo -e "${YELLOW}Watt Toolkit is not installed.${NC}"
    fi

    if $has_install; then
        if [ -n "$installed_version" ] && [ "$installed_version" = "$VERSION" ]; then
            echo -e "${GREEN}✅ Already the latest version ${installed_version}, no action needed.${NC}"
            return 0
        fi
        # Installed but a different version, or unreadable -> ask before downloading, to avoid a silent overwrite
        if [ -n "$installed_version" ]; then
            echo -e "${YELLOW}A new version ${VERSION} was detected (currently installed: ${installed_version}).${NC}"
        else
            echo -e "${YELLOW}Version ${VERSION} will be downloaded and installed again.${NC}"
        fi
        read -n1 -p "Press Enter or A to continue downloading and installing, any other key to cancel: " confirm < /dev/tty
        echo
        if [[ -n "$confirm" && ! "$confirm" =~ [Aa] ]]; then
            echo "Operation cancelled."
            return 0
        fi
    fi

    echo -e "${GREEN}Version to install: ${VERSION}${NC}"
    echo "Downloading ${DOWNLOAD_URL} ..."

    local temp_dir="/tmp/watt_toolkit_install"
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    cd "$temp_dir" || return 1

    local filename="Steam_v${VERSION}_linux_x64.tgz"
    curl -L --progress-bar -o "$filename" "$DOWNLOAD_URL"
    if [ $? -ne 0 ] || [ ! -f "$filename" ]; then
        echo -e "${RED}Download failed, please check your network and try again.${NC}"
        return 1
    fi

    echo -e "${CYAN}Extracting...${NC}"
    local temp_extract="$temp_dir/extracted"
    mkdir -p "$temp_extract"
    if ! tar -xzf "$filename" -C "$temp_extract"; then
        echo -e "${RED}Extraction failed.${NC}"
        rm -rf "$temp_dir"
        return 1
    fi

    local content_count=$(ls -1 "$temp_extract" | wc -l)
    local first_item=$(ls -1 "$temp_extract" | head -1)

    if [ -d "$INSTALL_DIR" ]; then
        echo "Old installation directory detected, deleting..."
        rm -rf "$INSTALL_DIR"
    fi
    mkdir -p "$INSTALL_DIR"

    if [ $content_count -eq 1 ] && [ -d "$temp_extract/$first_item" ]; then
        echo -e "${CYAN}Top-level directory detected, moving contents to $INSTALL_DIR ...${NC}"
        shopt -s dotglob
        mv "$temp_extract/$first_item"/* "$INSTALL_DIR/"
        shopt -u dotglob
        find "$temp_extract/$first_item" -maxdepth 1 -name ".*" ! -name "." ! -name ".." -exec mv {} "$INSTALL_DIR/" \;
        rm -rf "$temp_extract/$first_item"
    else
        echo -e "${CYAN}Moving all contents to $INSTALL_DIR ...${NC}"
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
        echo -e "${RED}Error: key files are missing, the installation may be incomplete.${NC}"
        echo "Please check the contents of $INSTALL_DIR."
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
    echo -e "${YELLOW}Usage tips:${NC}"
    echo "If acceleration reports an error, follow the steps below:"
    echo "  Network acceleration -> Acceleration settings -> Install certificate"
    echo ""
    echo "Please launch Watt Toolkit from the desktop."
}

watt_toolkit_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}══════════════ Uninstall Watt Toolkit ══════════════${NC}"
    local INSTALL_DIR="$HOME/Watt Toolkit"
    local DESKTOP_DIR="$HOME/Desktop"

    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Watt Toolkit is not installed.${NC}"
        return 0
    fi

    echo -e "${CYAN}Uninstalling Watt Toolkit...${NC}"
    echo "The following directory will be deleted: ${INSTALL_DIR}"
    echo "The desktop shortcut will be deleted: ${DESKTOP_DIR}/Watt_Toolkit.desktop"
    echo ""

    read -n1 -p "Press Enter or A to confirm uninstalling, any other key to cancel: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "Continuing the uninstall..."
    else
        echo "Uninstall cancelled."
        return 0
    fi

    if rm -rf "$INSTALL_DIR"; then
        echo -e "${GREEN}✓ Installation directory deleted${NC}"
    else
        echo -e "${RED}✗ Failed to delete the installation directory${NC}"
    fi

    if rm -f "${DESKTOP_DIR}/Watt_Toolkit.desktop"; then
        echo -e "${GREEN}✓ Desktop shortcut deleted${NC}"
    else
        echo -e "${RED}✗ Failed to delete the desktop shortcut${NC}"
    fi

    echo ""
    echo -e "${GREEN}✅ Watt Toolkit uninstalled.${NC}"
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

    echo "Running the uninstall..."
    sudo rm -rf "$HOME/homebrew"
    # Judge by whether the directory really disappeared (rm may also return 0 on partial failure)
    if [ -d "$HOME/homebrew" ]; then
        echo -e "${RED}✗ Failed to uninstall the Plugin Store, the directory still exists: $HOME/homebrew${NC}"
        echo -e "${YELLOW}  Please delete it manually: sudo rm -rf \"$HOME/homebrew\"${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ Plugin Store uninstalled${NC}"
    echo "To reinstall, use the 'Install Plugin Store' feature."
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
            --title="GE-Proton compatibility layer management" \
            --text="Please choose an action" \
            --column="Select" --column="Action" \
            FALSE "Install GE-Proton" \
            FALSE "Uninstall GE-Proton" \
            --width=400 --height=200 2>/dev/null)
        [ $? -eq 1 ] && return 0
        case "$choice" in
            "Install GE-Proton") ge_proton_install ;;
            "Uninstall GE-Proton") ge_proton_uninstall ;;
            *) return 0 ;;
        esac
    done
}

ge_proton_install() {
    (
        echo "10"; echo "# Fetching the version list, please wait..."
        sleep 0.5
        echo "50"; echo "# Connecting to the GitHub API..."
        sleep 0.5
        echo "100"
    ) | zenity --progress --pulsate --title="Loading" --text="Fetching the version list..." --width=400 2>/dev/null &
    ZENITY_PID=$!

    local all_versions=$(get_ge_proton_versions)

    kill $ZENITY_PID 2>/dev/null
    wait $ZENITY_PID 2>/dev/null

    [ -z "$all_versions" ] && {
        zenity --error --text="Cannot fetch the version list, please check your network." --width=400 2>/dev/null
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
        zenity --info --text="All GE-Proton versions are already installed!" --width=400 2>/dev/null
        return 0
    }

    local list_args=(
        --list --checklist
        --title="Install GE-Proton compatibility layer"
        --text="Please choose the version(s) to install (multiple allowed)\n${#available_versions[@]} version(s) available, installed versions excluded"
        --column="Select" --column="Version"
        --width=600 --height=500
        --ok-label="Install"
        --cancel-label="Back"
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
            zenity --warning --text="Please select at least one version." --width=300 2>/dev/null
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

    # Download from the GitHub official source only (no third-party mirrors).
    # The prefix is empty because download_url is already a complete https://github.com/... address.
    local mirror=""

    local pipe="/tmp/zenity_pipe_$$"
    mkfifo "$pipe"
    zenity --progress --pulsate --title="Install GE-Proton" --text="Getting ready..." --width=500 < "$pipe" &
    local zenity_pid=$!
    exec 3> "$pipe"

    for i in "${!versions[@]}"; do
        if ! kill -0 $zenity_pid 2>/dev/null; then
            echo "User cancelled the installation" >&2
            break
        fi

        local version="${versions[$i]}"
        local idx=$((i+1))
        echo "# Processing item $idx/$total: $version (preparing download...)" >&3

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
            echo "# Error: cannot get the download link for $version, skipping" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (cannot get the download link)"
            continue
        fi

        local full_url="${mirror}${download_url}"
        local temp_dir="/tmp/ge_proton_$$"
        mkdir -p "$temp_dir"
        cd "$temp_dir" || continue
        local filename="${version}.tar.gz"

        echo "# Processing item $idx/$total: $version (downloading...)" >&3
        curl -L -f -S --connect-timeout 30 --max-time 600 -o "$filename" "$full_url" 2> /tmp/curl_err_$$.log
        local curl_ret=$?
        if [ $curl_ret -ne 0 ]; then
            echo "# Download failed, error message:" >&3
            tail -n 5 /tmp/curl_err_$$.log >&3
            rm -f /tmp/curl_err_$$.log
            rm -f "$filename"
            cd /tmp && rm -rf "$temp_dir"
            ((failed_count++))
            failed_list="${failed_list}\n  $version (download failed)"
            continue
        fi
        rm -f /tmp/curl_err_$$.log

        # Extract to a temporary directory to verify integrity first, then move into compatibilitytools.d.
        # The problem with extracting straight into install_dir: when the download is truncated/corrupt, tar leaves
        # half a directory behind, and Steam loads this broken version as a usable compatibility layer.
        echo "# Processing item $idx/$total: $version (extracting...)" >&3
        local STAGE_DIR
        STAGE_DIR=$(mktemp -d "$install_dir/.stage.XXXXXX" 2>/dev/null) || STAGE_DIR=""
        if [ -z "$STAGE_DIR" ]; then
            echo "# Item $idx/$total: $version installation failed (cannot create the temporary directory)" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (cannot create the temporary directory)"
            rm -f "$filename"
            cd /tmp && rm -rf "$temp_dir"
            continue
        fi
        tar -xzf "$filename" -C "$STAGE_DIR"
        local tar_ret=$?

        rm -f "$filename"
        cd /tmp && rm -rf "$temp_dir"

        if [ $tar_ret -ne 0 ] || [ ! -d "$STAGE_DIR/$version" ]; then
            # Extraction failed: remove the half-finished output; never leave it in compatibilitytools.d
            rm -rf "$STAGE_DIR"
            echo "# Item $idx/$total: $version installation failed (archive corrupt or extraction interrupted)" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (extraction failed)"
            continue
        fi

        # Extraction succeeded: delete the old version directory and then move atomically, avoiding leftover mixed content
        rm -rf "${install_dir:?}/$version"
        if ! mv "$STAGE_DIR/$version" "$install_dir/$version"; then
            rm -rf "$STAGE_DIR"
            echo "# Item $idx/$total: $version installation failed (failed to move to the target directory)" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (move failed)"
            continue
        fi
        rm -rf "$STAGE_DIR"

        if [ -d "$install_dir/$version" ]; then
            echo "# Item $idx/$total: $version installed successfully" >&3
            ((success_count++))
        else
            echo "# Item $idx/$total: $version installation failed" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (install verification failed)"
        fi
    done

    if kill -0 $zenity_pid 2>/dev/null; then
        local result_msg="\n========== Installation complete ==========\nSucceeded: $success_count"
        if [ $failed_count -gt 0 ]; then
            result_msg+="\nFailed: $failed_count\nFailed versions:${failed_list}"
        fi
        if [ $success_count -gt 0 ]; then
            result_msg+="\n\nIt is recommended to restart Steam to refresh the compatibility layer list."
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
        zenity --info --text="No installed GE-Proton detected." --ok-label="Back" --width=400 2>/dev/null
        return 0
    }
    mapfile -t installed_array <<< "$installed_list"

    local list_args=(
        --list --checklist
        --title="Uninstall GE-Proton compatibility layer"
        --text="Please choose the version(s) to uninstall (multiple allowed)"
        --column="Select" --column="Version"
        --width=500 --height=350
        --ok-label="Uninstall"
        --cancel-label="Back"
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
    zenity --progress --pulsate --title="Uninstall GE-Proton" --text="Getting ready..." --width=500 < "$pipe" &
    local zenity_pid=$!
    exec 3> "$pipe"

    for i in "${!selected[@]}"; do
        if ! kill -0 $zenity_pid 2>/dev/null; then
            echo "User cancelled the uninstall" >&2
            break
        fi

        local version="${selected[$i]}"
        local idx=$((i+1))

        echo "# Processing item $idx/$total: $version ..." >&3

        if [ -d "$install_dir/$version" ]; then
            rm -rf "$install_dir/$version"
            if [ ! -d "$install_dir/$version" ]; then
                ((success++))
                echo "# Item $idx/$total: $version uninstalled" >&3
            else
                ((fail++))
                failed_list="${failed_list}\n  $version (deletion failed)"
                echo "# Item $idx/$total: $version uninstall failed" >&3
            fi
        else
            ((success++))
            echo "# Item $idx/$total: $version (directory does not exist, skipped)" >&3
        fi
        sleep 0.3
    done

    if kill -0 $zenity_pid 2>/dev/null; then
        local result_msg="\n========== Uninstall complete ==========\nSucceeded: $success"
        if [ $fail -gt 0 ]; then
            result_msg+="\nFailed: $fail\nFailed versions:${failed_list}"
        fi
        result_msg+="\n\nIt is recommended to restart Steam for the changes to take effect."
        echo "# $result_msg" >&3
        exec 3>&-
        wait $zenity_pid 2>/dev/null
    fi

    rm -f "$pipe"
}

clover_install_or_reinstall() {
    clear
    echo -e "${YELLOW}════════════════ Install/Reinstall Clover bootloader ════════════════${NC}"
    echo ""
    echo -e "${CYAN}This will install or reinstall the Clover graphical boot manager.${NC}"
    echo -e "${YELLOW}Important: configure the following in Windows first (when Windows already exists and this is the first bootloader install; skip this step when reinstalling):${NC}"
    echo "  1. Open Command Prompt or PowerShell as administrator"
    echo "  2. Run the command: bcdedit.exe -set \"{globalsettings}\" highestmode on"
    echo "  3. Run the command: reg add \"HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\TimeZoneInformation\" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f"
    echo ""

    echo "========================================="
    echo "   Steam Deck Clover install helper"
    echo "========================================="
    # Cloning here uses the git protocol; only the GitHub official source is supported.
    BASE_URL="https://github.com"

    REPO_FULL_PATH="ryanrudolfoba/SteamDeck-Clover-dualboot"
    REPO_URL="${BASE_URL}/${REPO_FULL_PATH}"
    TARGET_DIR="$HOME/SteamDeck-Clover-dualboot"

    if [ -d "$TARGET_DIR" ]; then
        echo -e "${YELLOW}The directory $TARGET_DIR already exists.${NC}"
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

    echo -e "${CYAN}Cloning the repository...${NC}"
    if ! git clone --progress --depth=1 "$REPO_URL" "$TARGET_DIR" 2>&1 | tee /tmp/clone_log.txt; then
        echo -e "${RED}Clone failed, please check your network or switch to another mirror.${NC}"
        rm -rf "$TARGET_DIR"
        read -p "Press Enter to return to the main menu..." < /dev/tty
        return 1
    fi

    echo -e "${GREEN}Clone complete.${NC}"
    cd "$TARGET_DIR" || { echo -e "${RED}Cannot enter the directory${NC}"; return 1; }

    echo -e "${CYAN}Generating the optimized install-Clover.sh...${NC}"
    cat > install-Clover.sh << 'CLOVER_SCRIPT_EOF'
#!/bin/bash
# Abort on failure: the old script had no set -e, so any failed intermediate step (cp/mount/efibootmgr) continued
# downwards, possibly leaving half a Clover install on the ESP while still printing "installation complete".
# Here -euo pipefail is added, and commands that are "allowed to fail" (grep probes, efibootmgr -B, umount) get
# an explicit `|| true` or are put inside if, see the comments below.
set -euo pipefail

clear

echo "Clover dual-boot installation script - for Steam Deck"
echo "Project URL: https://github.com/ryanrudolfoba/SteamDeck-Clover-dualboot"
echo "Author YT: 10MinuteSteamDeckGamer"
echo "Running preliminary checks..."

CLOVER=$(efibootmgr | grep -i Clover | colrm 9 | colrm 1 4 || true)
REFIND=$(efibootmgr | grep -i rEFInd | colrm 9 | colrm 1 4 || true)

# Detect the ESP dynamically instead of hard-coding /dev/nvme0n1p1:
#   Steam Deck has NVMe / eMMC (/dev/mmcblk0) / SATA (/dev/sda) variants,
#   and the partition number is not guaranteed to be 1 (on machines where Windows was installed before SteamOS the ESP may be p2/p3).
# Order: (1) a mounted /esp (SteamOS) or /boot/efi (Bazzite) -> (2) find by the EFI partition type GUID.
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

# Password handling:
#  - The old form fed the password into the pipe via `echo -e "$pw\n"`. The password is a shell variable, not an external command argument,
#    and in practice it is not visible in ps; but `echo -e` interprets backslashes, so a password containing `\` gets rewritten/truncated
#    (measured: 'p\cw' -> 'p'), causing sudo authentication to fail. Use printf '%s\n' to output it verbatim instead.
#  - Right after a successful verification, run `sudo -v` to obtain a timestamp, then use `sudo -n` everywhere, no more password feeding.
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

# Later everything uses sudo -n (the password is cached by sudo -v above); on failure abort directly instead of continuing to write EFI.
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
    # Note: this prints "not enough space", and the outer success check matches that keyword accordingly
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

# The Clover ISO is a plain HTTP download (not git). Only the GitHub official source is used.
# Note: this overrides the global MIRRORS variable (only within this inner script's scope).
CLOVER_GH_BASE="https://github.com/CloverHackyColor/CloverBootloader"
MIRRORS=(
    ""                            # GitHub official: empty prefix, use the complete GitHub URL directly
)
MIRROR_LABELS=(
    "GitHub (official source)"
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

# On extraction failure clean up the downloaded 7z and any leftover ISO, to avoid filling /home
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

# On mount failure clean up the temp directory, ISO and 7z together
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

# Any failed step during installation must unmount the ISO and clean up temporary files, leaving no half-ready environment.
# Note: `trap ... ERR` does **not** run on paths triggered by `exit 1` inside the script (leftover ISO observed),
# so cleanup is attached to the already installed EXIT hook above, using the ISO_MOUNTED flag to decide whether to unmount.
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

# Fix: the old efibootmgr -c hard-coded /dev/nvme0n1 -p 1. eMMC models use /dev/mmcblk0,
# SATA models use /dev/sda, and the ESP partition number is not necessarily 1. Use the dynamically detected ESP_DISK/ESP_PARTN,
# and keep the output visible (no longer discarded by &>/dev/null) so a failure can abort and roll back.
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

# BOOTX64 replacement: the backup must succeed before overwriting; any failure rolls back to the backup immediately.
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

# The following are add-ons that run after "the EFI is already written". Failures only warn, never abort:
# at this point Clover can already boot; aborting the whole run because a tool/SYSTEMD step failed would make the user think it was not installed.
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
    # Fix: after a pipe, $? is the exit code of tee, not of install-Clover.sh
    # (measured: `false | tee x.log; echo $?` prints 0). Take PIPESTATUS[0] explicitly here,
    # and temporarily enable pipefail as a fallback, so the check does not silently break if the outer set options change later.
    set -o pipefail
    ./install-Clover.sh 2>&1 | tee "$LOG_FILE"
    INSTALL_EXIT=${PIPESTATUS[0]}

    # Fix: the old check greps for "Not enough space on the ESP partition!", which does not exist
    # in this script at all (the inner script actually prints the Chinese phrase for "not enough space"), so it was dead code that never matched.
    if grep -q "Not enough space on the ESP partition" "$LOG_FILE" \
        || grep -q "not enough space" "$LOG_FILE"; then
        echo -e "${RED}Installation failed: not enough space on the ESP partition, please clean up and try again.${NC}"
        read -p "Press Enter to return to the main menu..." < /dev/tty
        return 1
    elif [ $INSTALL_EXIT -eq 0 ] && grep -q "Clover installation complete" "$LOG_FILE"; then
        echo -e "${GREEN}Clover installed/reinstalled successfully!${NC}"
    else
        echo -e "${RED}Installation/reinstallation failed, please check the output above.${NC}"
        read -p "Press Enter to return to the main menu..." < /dev/tty
        return 1
    fi

    SHORTCUT="$HOME/Desktop/Boot Configuration.desktop"
    if [ -f "$SHORTCUT" ]; then
        echo -e "${GREEN}Desktop shortcut \"Boot Configuration\" already exists, no need to create it.${NC}"
    else
        # Fix: the old heredoc was quoted (<< 'EOF') so variables were not expanded and Exec hard-coded /home/deck,
        # breaking the shortcut on machines whose user name is not deck. Here the quotes are removed so $HOME expands;
        # it has been confirmed this heredoc contains no other $ or backticks besides the paths.
        cat > "$SHORTCUT" << EOF
[Desktop Entry]
Type=Application
Name=Boot Configuration
Exec=konsole -e bash -c '$HOME/1Clover-tools/Clover-Toolbox.sh; read -p "Press Enter to close..." -n1'
Icon=kdiamond
Terminal=false
Categories=Utility;
EOF
        chmod +x "$SHORTCUT"
        echo -e "${GREEN}Desktop shortcut \"Boot Configuration\" created.${NC}"
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
	--title "Clover Toolbox - https://github.com/ryanrudolfoba/SteamDeck-clover-dualboot" \
	--column "Select" \
	--column "Option" \
	--column "Description - read carefully" \
	FALSE Status "Choose this when submitting a bug report" \
	FALSE Batocera "Choose the configuration for Batocera v39 (and newer) or v38 (and older)" \
	FALSE Theme "Choose a fixed theme or a random theme" \
	FALSE Timeout "Set the default timeout (1/5/10/15 seconds) before booting the default system" \
	FALSE Service "Disable/enable the Clover EFI entry and the systemd service" \
	FALSE DefaultBoot "Set the default operating system to boot" \
	FALSE NewLogo "Replace the BGRT boot logo" \
	FALSE RestoreLogo "Restore the default BGRT boot logo" \
	FALSE Resolution "Set the screen resolution (DeckHD or DeckSight screen mods)" \
	FALSE Custom "Replace the Clover EFI with the custom version that hides the OPTIONS button" \
	FALSE Uninstall "Uninstall Clover and revert all changes" \
	TRUE Exit "***** Exit the Clover Toolbox *****")

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
	--column "Option" --column "Description - read carefully" \
	FALSE v39 "Set the Clover configuration for Batocera v39 and newer" \
	FALSE v38 "Set the Clover configuration for Batocera v38 and older" \
	TRUE Exit "***** Exit the Clover Toolbox *****")

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
	--title "Clover Toolbox" --column "Select" --column "Option" --column "Description - read carefully" \
	FALSE 1 "Set the default timeout to 1 second" \
	FALSE 5 "Set the default timeout to 5 seconds" \
	FALSE 10 "Set the default timeout to 10 seconds" \
	FALSE 15 "Set the default timeout to 15 seconds" \
 	FALSE 60 "Set the default timeout to 60 seconds" \
	TRUE Exit "***** Exit the Clover Toolbox *****")

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
	--column "Select" --column "Option" --column "Description - read carefully" \
	FALSE Disable "Disable the Clover EFI entry and the systemd service" \
	FALSE Enable "Enable the Clover EFI entry and the systemd service" \
	TRUE Exit "***** Exit the Clover Toolbox *****")

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

elif [ "$Choice" == "DefaultBoot" ]
then
Boot_Choice=$(zenity --width 550 --height 300 --list --radiolist --multiple --title "Clover Toolbox" --column "Select" \
	--column "Option" --column "Description - read carefully" \
	FALSE Windows "Set Windows as the default boot system" \
	FALSE SteamOS "Set SteamOS as the default boot system" \
	FALSE Bazzite "Set Bazzite as the default boot system" \
	FALSE LastSystem "Set the last booted system as the default" \
	TRUE Exit "***** Exit the Clover Toolbox *****")

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

	elif [ "$Boot_Choice" == "LastSystem" ]
	then
		printf '%s\n' "$current_password" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>LastBootedVolume<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover Toolbox" --text "The last used system is now the default boot entry in Clover!" --width 425 --height 75
	fi

elif [ "$Choice" == "NewLogo" ]
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

elif [ "$Choice" == "RestoreLogo" ]
then
	printf '%s\n' "$current_password" | sudo -S rm $EFI_PATH/steamos/steamos.png &> /dev/null
	zenity --warning --title "Clover Toolbox" --text "The BGRT logo was restored to the default!" --width 400 --height 75

elif [ "$Choice" == "Resolution" ]
then
Resolution_Choice=$(zenity --width 550 --height 250 --list --radiolist --multiple --title "Clover Toolbox" \
	--column "Select" --column "Option" --column "Description - read carefully" \
	FALSE Default "Use the default screen resolution 1280x800" \
	FALSE DeckHD "Use the DeckHD screen resolution 1920x1200" \
	FALSE DeckSight "Use the DeckSight screen resolution 1920x1080" \
	TRUE Exit "***** Exit the Clover Toolbox *****")

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
	# Fix: before uninstalling, first confirm the files to restore all exist. Previously, when .orig was missing and mv failed,
	# the script continued with rm -rf $EFI_PATH/clover without any check, leaving a half-uninstalled state
	# ("Clover files deleted, Windows/BOOTX64 not restored") that may make the machine unbootable.
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

	# Fix: in the old logic, if any step failed and exited after disable, the system stayed writable.
	# An EXIT trap is used here to guarantee read-only mode is restored however the script exits.
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

	rm -f ~/Desktop/Boot Configuration.desktop

	zenity --warning --title "Clover Toolbox" --text "Clover was uninstalled and the Windows EFI entry is active again!" --width 600 --height 75
	exit
fi
done
TOOLBOX_EOF

    chmod +x ~/1Clover-tools/Clover-Toolbox.sh
    echo -e "${GREEN}✓ Updated Clover-Toolbox.sh to the translated version.${NC}"

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

    echo "Checking the latest version..."
    local REMOTE_VERSION=$(curl -s https://anydesk.com.cn/zhs/downloads/linux | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/^v//')
    if [ -z "$REMOTE_VERSION" ]; then
        echo -e "${YELLOW}Cannot get the version automatically, trying the default version 8.0.4${NC}"
        REMOTE_VERSION="8.0.4"
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
        if [ "$LOCAL_VERSION" = "$REMOTE_VERSION" ]; then
            echo -e "${GREEN}✅ Already the latest version ${LOCAL_VERSION}, no action needed.${NC}"
            return 0
        else
            echo -e "${YELLOW}New version ${REMOTE_VERSION} found (current: ${LOCAL_VERSION})${NC}"
            read -n1 -p "Press Enter or A to update, any other key to cancel: " confirm < /dev/tty
            echo
            if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
                TARGET_VERSION="$REMOTE_VERSION"
            else
                echo "Update cancelled."
                return 0
            fi
        fi
    else
        TARGET_VERSION="$REMOTE_VERSION"
    fi

    if [ -z "$TARGET_VERSION" ]; then
        echo "No target version specified, operation cancelled."
        return 0
    fi

    echo "Installing AnyDesk ${TARGET_VERSION}..."
    cd /tmp || return

    local URL="https://download.anydesk.com/linux/anydesk-${TARGET_VERSION}-amd64.tar.gz"
    local TARBALL="/tmp/anydesk-${TARGET_VERSION}.tar.gz"
    local EXTRACT_DIR="/tmp/anydesk-extract.$$"
    echo "Downloading..."

    # Download and extract the package to a temporary directory first, and only replace the old install after everything succeeded.
    # The old logic did rm -rf on the old directory before downloading, so a network failure left the user without a working AnyDesk.
    rm -f "$TARBALL"
    if ! wget -q --show-progress "$URL" -O "$TARBALL"; then
        echo -e "${RED}Download failed, please check your network and try again.${NC}"
        echo -e "${YELLOW}The existing AnyDesk installation (if any) was kept.${NC}"
        rm -f "$TARBALL"
        return 1
    fi
    rm -rf "$EXTRACT_DIR"; mkdir -p "$EXTRACT_DIR"
    if ! tar -xzf "$TARBALL" -C "$EXTRACT_DIR" --strip-components=1; then
        echo -e "${RED}✗ Extraction failed, installation aborted.${NC}"
        rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
        echo -e "${YELLOW}The existing AnyDesk installation (if any) was kept.${NC}"
        return 1
    fi
    if [ ! -x "$EXTRACT_DIR/anydesk" ]; then
        echo -e "${RED}✗ The package contents are incomplete (anydesk executable not found), installation aborted.${NC}"
        rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
        echo -e "${YELLOW}The existing AnyDesk installation (if any) was kept.${NC}"
        return 1
    fi

    rm -rf "$ANYDESK_INSTALL_DIR"
    mkdir -p "$ANYDESK_INSTALL_DIR"
    if ! cp -a "$EXTRACT_DIR"/. "$ANYDESK_INSTALL_DIR"/; then
        echo -e "${RED}✗ Failed to copy the installation files.${NC}"
        rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
        return 1
    fi
    rm -rf "$EXTRACT_DIR"; rm -f "$TARBALL"
    chmod +x "$ANYDESK_BIN" 2>/dev/null
    if [ ! -x "$ANYDESK_BIN" ]; then
        echo -e "${RED}✗ The installation files are incomplete (executable not found).${NC}"
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

    if $local_found; then
        rm -rf "$ANYDESK_INSTALL_DIR" && echo -e "${GREEN}✓ Local installation directory deleted${NC}"
        rm -f "$DESKTOP_FILE" && echo -e "${GREEN}✓ Local desktop shortcut deleted${NC}"
        rm -f "$BIN_LINK" && echo -e "${GREEN}✓ Command link deleted${NC}"
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
        fi
    fi

    echo ""
    echo -e "${GREEN}✅ AnyDesk uninstalled.${NC}"
}

install_todesk() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Install ToDesk ════════════════${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Important notice${NC}"
    echo "  The official ToDesk package cannot be installed directly; the current approach relies on a third-party maintained install script"
    echo "  (todesk.lanbai.top -> github.com/mclanbai/archtodesk)."
    echo "  That third-party script performs the following system-level changes:"
    echo "    · sudo steamos-readonly disable  (lifts the SteamOS read-only protection)"
    echo "    · sudo pacman-key --init / --populate  (rebuilds the pacman keyring)"
    echo "    · sudo pacman -S base-devel --noconfirm  (installs the whole compiler toolchain, large download)"
    echo "    · uninstalls and reinstalls the todesk / todesk-bin packages"
    echo "  In addition, that script hard-codes the user name as /home/deck, so it fails on devices with a non-deck user name."
    echo ""
    echo -e "${CYAN}This tool no longer runs that third-party script automatically.${NC}"
    echo "  Please choose one of the two options:"
    echo "    A. Manual install: review the script contents yourself, then run it"
    echo "       curl -L todesk.lanbai.top | less     # read it first"
    echo "    B. Open a terminal and run the installation manually (make sure you understand the changes above before running)"
    echo ""

    local ans
    if ! read -p "Press y to open the third-party script in a terminal (at your own risk), any other key to cancel: " -n 1 -r ans < /dev/tty; then
        echo ""
        echo "Operation cancelled."
        return 0
    fi
    echo ""
    if [[ ! "$ans" =~ ^[Yy]$ ]]; then
        echo "Operation cancelled."
        return 0
    fi

    # After explicit user confirmation: download the script locally for review first, then run it visibly
    local script_path="/tmp/steamdeck_toolbox_todesk_install.sh"
    if ! curl -fL --connect-timeout 20 --max-time 60 -o "$script_path" todesk.lanbai.top; then
        echo -e "${RED}✗ Failed to download the install script, please check your network and try again.${NC}"
        rm -f "$script_path"
        return 1
    fi
    if [ ! -s "$script_path" ]; then
        echo -e "${RED}✗ The downloaded content is empty, aborted.${NC}"
        rm -f "$script_path"
        return 1
    fi
    if ! bash -n "$script_path" 2>/dev/null; then
        echo -e "${RED}✗ The downloaded script has syntax errors, execution aborted.${NC}"
        echo -e "${YELLOW}  The script was kept at $script_path for inspection.${NC}"
        return 1
    fi

    echo -e "${CYAN}The script was downloaded to $script_path, contents below (please confirm before continuing):${NC}"
    echo "----------------------------------------"
    sed -n '1,80p' "$script_path"
    echo "----------------------------------------"
    local go
    if ! read -p "Press Enter or A to run the script, any other key to cancel: " -n 1 -r go < /dev/tty; then
        echo ""
        echo "Operation cancelled (the script is kept at $script_path)."
        return 0
    fi
    echo ""
    if [[ ! "$go" =~ ^[Aa]$ && -n "$go" ]]; then
        echo "Operation cancelled (the script is kept at $script_path)."
        return 0
    fi

    if bash "$script_path"; then
        echo -e "${GREEN}✓ ToDesk install script finished${NC}"
    else
        echo -e "${RED}✗ ToDesk install script failed, please check the output above.${NC}"
        echo -e "${YELLOW}  Script location: $script_path${NC}"
        return 1
    fi
}

install_wps_office() { install_flatpak_app "WPS Office" "WPS Office" "Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"; }
install_qq() { install_flatpak_app "QQ" "QQ" "Network;Chat" "com.qq.QQ" "com.tencent.qq"; }
install_wechat() { install_flatpak_app "WeChat" "WeChat" "Network;Chat" "com.tencent.WeChat" "com.qq.weixin"; }
install_qqmusic() { install_flatpak_app "QQ Music" "QQ Music" "Audio" "com.qq.QQmusic" "com.tencent.QQmusic"; }
install_baidunetdisk() { install_flatpak_app "Baidu Netdisk" "Baidu Netdisk" "Network;FileTransfer" "com.baidu.NetDisk" "com.baidu.pan"; }
install_edge() { install_flatpak_app "Microsoft Edge" "Microsoft Edge" "Network;WebBrowser" "com.microsoft.Edge"; }
install_chrome() { install_flatpak_app "Google Chrome" "Google Chrome" "Network;WebBrowser" "com.google.Chrome"; }

install_fcitx5() {
    if ! flatpak info org.fcitx.Fcitx5 &>/dev/null; then
        install_flatpak_app "Fcitx 5" "Fcitx 5" "Utility;Settings" "org.fcitx.Fcitx5"
    else
        echo -e "${GREEN}✓ Fcitx 5 main program installed${NC}"
    fi
    if ! flatpak info org.fcitx.Fcitx5.Addon.ChineseAddons &>/dev/null; then
        echo "Installing the Chinese input method add-on..."
        if flatpak install flathub org.fcitx.Fcitx5.Addon.ChineseAddons -y; then
            echo -e "${GREEN}✓ Chinese add-on installed${NC}"
        else
            echo -e "${RED}✗ Failed to install the Chinese add-on${NC}"
        fi
    else
        echo -e "${GREEN}✓ Chinese add-on already installed${NC}"
    fi
}
update_installed_apps() {
    mk_temp_dir; clear
    echo -e "${YELLOW}════════════════ Update all applications ════════════════${NC}"
    if flatpak update -y; then
        echo -e "${GREEN}✓ All applications updated${NC}"
    else
        echo -e "${RED}✗ Update failed, please check your network or the flatpak status.${NC}"
        return 1
    fi
}

uninstall_wps_office() { uninstall_flatpak_app "WPS Office" "WPS Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"; }
uninstall_qq() { uninstall_flatpak_app "QQ" "QQ" "com.qq.QQ" "com.tencent.qq"; }
uninstall_wechat() { uninstall_flatpak_app "WeChat" "WeChat" "com.tencent.WeChat" "com.qq.weixin"; }
uninstall_qqmusic() { uninstall_flatpak_app "QQ Music" "QQ Music" "com.qq.QQmusic" "com.tencent.QQmusic"; }
uninstall_baidunetdisk() { uninstall_flatpak_app "Baidu Netdisk" "Baidu Netdisk" "com.baidu.NetDisk" "com.baidu.pan"; }
uninstall_edge() { uninstall_flatpak_app "Microsoft Edge" "Microsoft Edge" "com.microsoft.Edge"; }
uninstall_chrome() { uninstall_flatpak_app "Google Chrome" "Google Chrome" "com.google.Chrome" "org.chromium.Chromium"; }
uninstall_fcitx5() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ Uninstall Fcitx 5 ════════════════${NC}"

    local MAIN_APP="org.fcitx.Fcitx5"
    local ADDON_APP="org.fcitx.Fcitx5.Addon.ChineseAddons"
    local DESKTOP_NAME="Fcitx 5"

    if ! flatpak info "$MAIN_APP" &>/dev/null; then
        echo -e "${YELLOW}Fcitx 5 main program is not installed.${NC}"
        if flatpak info "$ADDON_APP" &>/dev/null; then
            echo -e "${CYAN}The Chinese add-on is installed but the main program is missing, uninstall only the add-on?${NC}"
            read -n1 -p "Press Enter or A to confirm uninstalling the add-on, any other key to cancel: " confirm < /dev/tty
            echo
            if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
                flatpak uninstall "$ADDON_APP" -y 2>/dev/null && echo -e "${GREEN}✓ Chinese add-on uninstalled${NC}"
            else
                echo "Operation cancelled."
            fi
        fi
        return 0
    fi

    echo -e "${CYAN}Fcitx 5 main program detected as installed.${NC}"
    read -n1 -p "Press Enter or A to confirm uninstalling, any other key to cancel: " confirm < /dev/tty
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "Starting the uninstall..."
    else
        echo "Uninstall cancelled."
        return 0
    fi

    if flatpak info "$ADDON_APP" &>/dev/null; then
        echo "Uninstalling the Chinese add-on..."
        flatpak uninstall "$ADDON_APP" -y 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Chinese add-on uninstalled${NC}"
        else
            echo -e "${YELLOW}⚠️  Failed to uninstall the Chinese add-on (it may already be removed)${NC}"
        fi
    else
        echo -e "${YELLOW}Chinese add-on is not installed, skipping.${NC}"
    fi

    echo "Uninstalling the Fcitx 5 main program..."
    flatpak uninstall "$MAIN_APP" -y 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Fcitx 5 main program uninstalled${NC}"
    else
        echo -e "${RED}✗ Failed to uninstall the main program, please check the flatpak status.${NC}"
        return 1
    fi

    local desktop_dir="$HOME/Desktop"
    if [ -d "$desktop_dir" ]; then
        for f in "$desktop_dir/Fcitx 5.desktop" "$desktop_dir/org.fcitx.Fcitx5.desktop"; do
            if [ -f "$f" ]; then
                rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ Desktop shortcut deleted: $(basename "$f")${NC}"
            fi
        done
        find "$desktop_dir" -maxdepth 1 -name "*Fcitx*" -name "*.desktop" -exec rm -f {} \; 2>/dev/null
    fi

    echo ""
    echo -e "${GREEN}✅ Fcitx 5 and its related components uninstalled.${NC}"
}

uninstall_other_flatpak_apps() {
    if ! command -v zenity &>/dev/null; then
        echo "zenity not found, please run in a desktop environment."
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
            # Only match shortcuts whose file name is exactly the app ID (dot/underscore forms),
            # no substring matching, to avoid deleting unrelated .desktop files
            if [ "$base" = "${app_id}.desktop" ] || [ "$base" = "${id_us}.desktop" ]; then
                rm -f "$f" 2>/dev/null && echo "Desktop shortcut deleted: $base"
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
            zenity --info --text="There are no other installed Flatpak applications to uninstall." --width=400
            break
        fi

        local list_data=()
        for entry in "${installed_apps[@]}"; do
            IFS='|' read -r app_id app_name <<< "$entry"
            list_data+=("FALSE" "$app_name ($app_id)")
        done

        local selections
        selections=$(zenity --list --checklist \
            --title="Uninstall other Flatpak applications" \
            --text="Please choose the application(s) to uninstall (multiple allowed):" \
            --column="Select" --column="Application" \
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
            --text="Uninstall the selected applications?\n${#selected_ids[@]} item(s) in total." \
            --ok-label="Uninstall" --cancel-label="Cancel" 2>/dev/null || continue

        local total=${#selected_ids[@]}
        local success=0
        local fail=0
        local failed_list=""
        local data_dirs=()

        local pipe="/tmp/zenity_pipe_$$"
        mkfifo "$pipe"
        zenity --progress --pulsate --no-cancel --auto-close \
            --title="Uninstall applications" --text="Getting ready..." --width=500 < "$pipe" &
        local zenity_pid=$!
        exec 3> "$pipe"

        for i in "${!selected_ids[@]}"; do
            local app_id="${selected_ids[$i]}"
            local idx=$((i+1))

            echo "# Processing item $idx/$total: $app_id (uninstalling...)" >&3

            if flatpak uninstall "$app_id" -y &>/dev/null; then
                ((success++))
                _remove_shortcut "$app_id"
                local data_dir="$HOME/.var/app/$app_id"
                if [ -d "$data_dir" ]; then
                    data_dirs+=("$data_dir")
                fi
                echo "# Item $idx/$total: $app_id uninstalled successfully" >&3
            else
                ((fail++))
                failed_list+=" $app_id"
                echo "# Item $idx/$total: $app_id uninstall failed" >&3
            fi
            sleep 0.2
        done

        exec 3>&-
        wait $zenity_pid 2>/dev/null
        rm -f "$pipe"

        sleep 1.0

        local result_msg="Uninstall result:\nSucceeded: $success"
        if [ $fail -gt 0 ]; then
            result_msg+="\nFailed: $fail\nFailed IDs:${failed_list}"
        fi

        if [ ${#data_dirs[@]} -gt 0 ]; then
            local question_msg="$result_msg\n\nThe following application data directories still exist:"
            for d in "${data_dirs[@]}"; do
                question_msg+="\n  $d"
            done
            question_msg+="\n\nDelete these data directories?"

            if zenity --question --text="$question_msg" --width=600 \
                --ok-label="Delete data" --cancel-label="Keep" 2>/dev/null; then
                for d in "${data_dirs[@]}"; do
                    rm -rf "$d" && echo "Deleted $d"
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
        super().__init__(title=f"Running Task: {display_name}")
        self.set_default_size(760, 520)
        task_header = Gtk.HeaderBar()
        task_header.set_show_close_button(True)
        task_header.props.title = display_name
        task_header.props.subtitle = "Task running"
        # HeaderBar only draws a single Close button by default; minimize/maximize buttons must be added manually
        # (gtk-decoration-layout only applies to native system decorations, not to a custom HeaderBar)
        self._max_btn = Gtk.Button()
        self._max_btn.set_relief(Gtk.ReliefStyle.NONE)
        self._max_btn.set_tooltip_text("Maximize / Restore")
        self._max_btn_image = Gtk.Image.new_from_icon_name(
            "window-maximize-symbolic", Gtk.IconSize.BUTTON)
        self._max_btn.add(self._max_btn_image)
        self._max_btn.connect("clicked", self._on_maximize_clicked)
        task_header.pack_end(self._max_btn)
        self.set_titlebar(task_header)
        self._task_header = task_header
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_transient_for(parent)
        # Not modal anymore: modal windows get size-limited or cannot be maximized under some window managers,
        # and the task window is essentially a standalone terminal, so users need to resize it freely and switch to other windows to copy content.
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
            label = Gtk.Label(label="The task is running in an external terminal. Please check the terminal window that opened.")
            label.set_margin_top(20)
            label.set_margin_bottom(20)
            vbox.pack_start(label, True, True, 0)
            self.action_btn = Gtk.Button(label="Close")
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

            # Terminal context menu: Copy Selection / Copy All Output / Paste / Select All
            self.terminal.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            self.terminal.connect("button-press-event", self._on_terminal_button_press)
            # Keyboard shortcuts: Ctrl+Shift+C copy, Ctrl+Shift+V paste, Ctrl+Shift+A select all
            self.terminal.connect("key-press-event", self._on_terminal_key_press)

            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_margin_top(5)
            button_box.set_margin_bottom(5)
            button_box.set_margin_start(10)
            button_box.set_margin_end(10)
            self.timer_label = Gtk.Label(label="Running 0:00")
            self.timer_label.set_name("task-timer")
            button_box.pack_start(self.timer_label, False, False, 0)
            button_box.pack_start(Gtk.Label(), True, True, 0)

            # Copy button: copies the selection when there is one, otherwise copies all output
            self.copy_btn = Gtk.Button(label="Copy")
            self.copy_btn.set_tooltip_text("Copy the selected terminal content; copies all output when nothing is selected")
            self.copy_btn.connect("clicked", self.on_copy_clicked)
            button_box.pack_start(self.copy_btn, False, False, 0)

            self.action_btn = Gtk.Button(label="Cancel")
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
    # Copy button / context menu entry points
    # ------------------------------------------------------------------
    def _on_terminal_button_press(self, widget, event):
        # Right click (button 3) pops up the menu
        if event.button == 3:
            return self._show_terminal_menu(widget, event)
        return False

    def on_copy_clicked(self, button):
        """Copy the selection when there is one, otherwise copy all output, with brief feedback."""
        if self._terminal_has_selection():
            ok = self._copy_selection()
            msg = "Selection copied" if ok else "Copy failed"
        else:
            ok = self._copy_all_output()
            msg = "All output copied" if ok else "Nothing to copy"
        self._flash_copy_button(msg)

    def _on_terminal_key_press(self, widget, event):
        """Terminal keyboard shortcuts. Ctrl+C is left for interrupting the process; use Ctrl+Shift+C to copy."""
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
            print(f"Failed to handle shortcut: {e}")
        return False

    def _flash_copy_button(self, msg):
        try:
            old = self.copy_btn.get_label()
            self.copy_btn.set_label(msg)
            def restore():
                try:
                    self.copy_btn.set_label(old if old else "Copy")
                except Exception:
                    pass
                return False
            GLib.timeout_add(1500, restore)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Window maximize / restore
    # ------------------------------------------------------------------
    def _on_maximize_clicked(self, button):
        self.toggle_maximize()

    def toggle_maximize(self):
        """Maximize / restore the window and sync the button icon."""
        try:
            if self.is_maximized():
                self.unmaximize()
                icon = "window-maximize-symbolic"
            else:
                self.maximize()
                icon = "window-restore-symbolic"
            self._max_btn_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)
        except Exception as e:
            print(f"Failed to toggle window maximize: {e}")

    # ------------------------------------------------------------------
    # Terminal copy / paste
    # ------------------------------------------------------------------
    def _terminal_has_selection(self):
        try:
            return bool(self.terminal and self.terminal.get_has_selection())
        except Exception:
            return False

    def _copy_selection(self):
        """Copy the selected terminal text to the clipboard."""
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
                print(f"Copy failed: {e}")
                return False

    def _copy_all_output(self):
        """Copy the entire terminal content (including scrollback) to the clipboard."""
        if not self.terminal:
            return False
        text = ""
        # get_text_range_format returns a (text, attribute array) tuple, not a string; take item 0
        try:
            if hasattr(self.terminal, "get_text_range_format"):
                result = self.terminal.get_text_range_format(Vte.Format.TEXT, 0, 0, -1, -1)
                if isinstance(result, (tuple, list)) and result:
                    text = result[0] or ""
                elif isinstance(result, str):
                    text = result
        except Exception as e:
            print(f"get_text_range_format failed: {e}")
            text = ""
        if not text:
            # Fallback: select all and read the selected text
            try:
                self.terminal.select_all()
                text = self.terminal.get_text_selected(Vte.Format.TEXT) or ""
            except Exception as e:
                print(f"Failed to read terminal content: {e}")
                text = ""
        if not text:
            return False
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text, -1)
            clipboard.store()
            return True
        except Exception as e:
            print(f"Failed to write to clipboard: {e}")
            return False

    def _paste_to_terminal(self):
        if not self.terminal:
            return
        try:
            self.terminal.paste_clipboard()
        except Exception as e:
            print(f"Paste failed: {e}")

    def _show_terminal_menu(self, terminal, event):
        """Terminal context menu: Copy Selection / Copy All Output / Paste / Select All."""
        menu = Gtk.Menu()
        has_sel = self._terminal_has_selection()

        item_copy = Gtk.MenuItem(label="Copy Selection")
        item_copy.set_sensitive(has_sel)
        item_copy.connect("activate", lambda *_: self._copy_selection())
        menu.append(item_copy)

        item_copy_all = Gtk.MenuItem(label="Copy All Output")
        item_copy_all.connect("activate", lambda *_: self._copy_all_output())
        menu.append(item_copy_all)

        item_paste = Gtk.MenuItem(label="Paste")
        item_paste.connect("activate", lambda *_: self._paste_to_terminal())
        menu.append(item_paste)

        menu.append(Gtk.SeparatorMenuItem())

        item_sel_all = Gtk.MenuItem(label="Select All")
        item_sel_all.connect("activate", lambda *_: self.terminal.select_all())
        menu.append(item_sel_all)

        menu.show_all()
        # popup_at_pointer needs a real event window; prefer it on GTK 3.22+,
        # and fall back to the classic popup on failure (a null event window under some WMs/synthetic events triggers an assertion)
        try:
            menu.popup_at_pointer(event)
        except Exception:
            try:
                menu.popup(None, None, None, None, event.button if event else 0,
                           Gtk.get_current_event_time())
            except Exception as e:
                print(f"Failed to pop up context menu: {e}")
                return False
        return True

    def run_external(self, func_key):
        tmp_path = create_temp_script()
        cmd = f"bash {tmp_path} {func_key}; read -p 'Press Enter to close...' -n1"
        if not launch_terminal(cmd):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.NONE,
                                    text="No usable terminal emulator found")
            dlg.add_button("OK", Gtk.ResponseType.OK)
            dlg.format_secondary_text("Please install konsole or xterm and try again.")
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
            self.action_btn.set_label("Launch failed")
            self.action_btn.set_sensitive(True)
            return
        self.terminal.connect("child-exited", self.on_child_exited)

    def on_child_exited(self, terminal, status):
        GLib.idle_add(self.set_completed)

    def set_completed(self):
        self.completed = True
        self.action_btn.set_sensitive(True)
        self.action_btn.set_label("Done")
        try:
            self._task_header.props.subtitle = "Task completed"
        except Exception:
            pass

    def _tick(self):
        if self.completed:
            return False
        elapsed = int(time.time() - self.start_time)
        m, s = divmod(elapsed, 60)
        self.timer_label.set_text(f"Running {m}:{s:02d}")
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
        self.action_btn.set_label("Cancelling...")
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
        super().__init__(title="Steam Deck Toolbox")
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(950, 620)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.system_type = self.detect_system_type()
        self.task_window = None

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Steam Deck Toolbox"
        header.props.subtitle = f"v{VERSION}  ·  {self.system_type}"
        self.set_titlebar(header)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search all functions...")
        self.search_entry.set_width_chars(20)
        self.search_entry.connect("search-changed", self.on_search_changed)
        header.pack_end(self.search_entry)

        # Theme switch button (Dark / Light / Follow System)
        self.theme_button = Gtk.MenuButton()
        self.theme_button.set_tooltip_text("Switch dark / light mode")
        self.theme_button.set_relief(Gtk.ReliefStyle.NONE)
        self._theme_icon = Gtk.Image.new_from_icon_name("weather-clear-night-symbolic",
                                                        Gtk.IconSize.BUTTON)
        self.theme_button.add(self._theme_icon)
        header.pack_end(self.theme_button)
        self._build_theme_menu()

        self._current_page = "func"

        self.icon_map = {
            "Support & Maintenance": "pushpin.png", "Changelog": "clipboard_twemoji.png",
            "System Optimization": "hammer_wrench.png", "Software Installation": "package.png",
            "Network Tools": "globe.png", "Plugins": "game_controller.png",
            "Boot Management": "refresh.png", "Update & Uninstall": "inbox.png"
        }

        self.category_tree = {
            "Support & Maintenance": [],
            "Changelog": [],
            "System Optimization": [
                ("Adjust Virtual Memory", "adjust_swap"),
                ("Fix Disk Write Errors", "fix_disk_write_error"),
                ("Clean hosts Cache", "clear_hosts_cache"),
                ("Calibrate Device", [
                    ("Calibrate Joystick", "calibrate_joystick_stick"),
                    ("Calibrate Triggers", "calibrate_joystick_trigger")
                ]),
                ("Steam Cache Manager", "steamdeck_cache_manager"),
                ("GE-Proton Manager", "ge_proton_manager")
            ],
            "Software Installation": [
                ("AnyDesk", "install_anydesk"),
                ("ToDesk", "install_todesk"),
                ("AskLink Remote", "install_asklink"),
                ("WPS Office", "install_wps_office"),
                ("QQ", "install_qq"),
                ("WeChat", "install_wechat"),
                ("QQ Music", "install_qqmusic"),
                ("Baidu Netdisk", "install_baidunetdisk"),
                ("Edge Browser", "install_edge"),
                ("Google Chrome", "install_chrome"),
                ("Fcitx 5", "install_fcitx5")
            ],
            "Network Tools": [
                ("UU Accelerator Plugin", "install_uu_accelerator"),
                ("Xunyou Accelerator Plugin", "install_xunyou_accelerator"),
                ("Qiyou Accelerator Plugin", "install_qiyou_accelerator"),
                ("Watt Toolkit (Steam++)", [
                    ("Install", "watt_toolkit_install"),
                    ("Uninstall", "watt_toolkit_uninstall")
                ])
            ],
            "Plugins": [
                ("Install/Uninstall Plugin Store", [
                    ("Install Plugin Store", "install_plugin_store"),
                    ("Uninstall Plugin Store", "uninstall_plugin_store")
                ]),
                ("ToMoon Plugin", [
                    ("Install/Update ToMoon", "install_tomoon_install"),
                    ("Uninstall ToMoon", "install_tomoon_uninstall")
                ]),
                ("Freedeck Plugin", [
                    ("Install/Update Freedeck", "install_freedeck_install"),
                    ("Uninstall Freedeck", "install_freedeck_uninstall")
                ]),
                ("LSFG-VK Plugin", [
                    ("Install/Update LSFG-VK", "install_decky_lsfg_vk_install"),
                    ("Uninstall LSFG-VK", "install_decky_lsfg_vk_uninstall")
                ]),
                ("Framegen Plugin", [
                    ("Install/Update Framegen", "install_decky_framegen_install"),
                    ("Uninstall Framegen", "install_decky_framegen_uninstall")
                ])
            ],
            "Boot Management": [
                ("Install/Reinstall Clover", "clover_install_or_reinstall")
            ],
            "Update & Uninstall": [
                ("Update Installed Apps", "update_installed_apps"),
                ("Uninstall Installed Apps", [
                    ("Uninstall WPS Office", "uninstall_wps_office"),
                    ("Uninstall QQ", "uninstall_qq"),
                    ("Uninstall WeChat", "uninstall_wechat"),
                    ("Uninstall QQ Music", "uninstall_qqmusic"),
                    ("Uninstall Baidu Netdisk", "uninstall_baidunetdisk"),
                    ("Uninstall Edge Browser", "uninstall_edge"),
                    ("Uninstall Google Chrome", "uninstall_chrome"),
                    ("Uninstall AnyDesk", "uninstall_anydesk"),
                    ("Uninstall Fcitx 5", "uninstall_fcitx5"),
                    ("Uninstall Other Installed Apps", "uninstall_other_flatpak_apps")
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
        sidebar_title = Gtk.Label(label="Categories"); sidebar_title.set_halign(Gtk.Align.START)
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
        about_title = Gtk.Label(); about_title.set_name("page-title"); about_title.set_markup("<big><b>About This Tool</b></big>"); about_title.set_halign(Gtk.Align.START)
        about_box.pack_start(about_title, False, False, 0)
        about_textview = Gtk.TextView(); about_textview.set_editable(False); about_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        about_textview.set_left_margin(16); about_textview.set_right_margin(16); about_textview.set_top_margin(14); about_textview.set_bottom_margin(14)
        about_textview.get_style_context().add_class("card")
        about_text = f"""
Steam Deck Toolbox v{VERSION}
Made by Zhucy123
Release date: January 1, 2026
About: a toolbox designed for the Steam Deck, integrating system optimization, software installation, network tools and more.
Usage: click a category on the left to view its functions; the top search box searches across categories; clicking a function opens a separate task window.
https://github.com/Zhucy123/steamdeck_toolbox
"""
        about_textview.get_buffer().set_text(about_text)
        scrolled_about = Gtk.ScrolledWindow(); scrolled_about.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC); scrolled_about.set_vexpand(True); scrolled_about.add(about_textview)
        about_box.pack_start(scrolled_about, True, True, 0)
        self.stack.add_named(about_box, "about")

        changelog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        changelog_box.set_margin_top(20); changelog_box.set_margin_bottom(20); changelog_box.set_margin_start(20); changelog_box.set_margin_end(20)
        changelog_title = Gtk.Label(); changelog_title.set_name("page-title"); changelog_title.set_markup("<big><b>Changelog</b></big>"); changelog_title.set_halign(Gtk.Align.START)
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

        # Global search results page
        search_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        search_page.set_margin_top(20); search_page.set_margin_bottom(20); search_page.set_margin_start(20); search_page.set_margin_end(20)
        search_page.set_vexpand(True); search_page.set_valign(Gtk.Align.FILL)
        self.search_title = Gtk.Label(label=""); self.search_title.set_name("page-title"); self.search_title.set_halign(Gtk.Align.START)
        search_page.pack_start(self.search_title, False, False, 0)
        self.search_store = Gtk.ListStore(str, str, str)
        self.search_view = Gtk.TreeView(model=self.search_store)
        self.search_view.set_name("func-list")
        col_name = Gtk.TreeViewColumn("Function"); r_name = Gtk.CellRendererText(); r_name.set_property("ypad", 9); col_name.pack_start(r_name, True); col_name.add_attribute(r_name, "text", 0)
        col_cat = Gtk.TreeViewColumn("Category"); r_cat = Gtk.CellRendererText(); r_cat.set_property("ypad", 9); col_cat.pack_start(r_cat, True); col_cat.add_attribute(r_cat, "text", 1)
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
        help_btn = Gtk.Button(label="Help"); help_btn.get_style_context().add_class("suggested-action"); help_btn.connect("clicked", self.on_help_clicked); bottom_bar.pack_start(help_btn, False, False, 0)
        quit_btn = Gtk.Button(label="Quit"); quit_btn.get_style_context().add_class("destructive-action"); quit_btn.connect("clicked", lambda b: self.destroy()); bottom_bar.pack_start(quit_btn, False, False, 0)
        main_vbox.pack_start(bottom_bar, False, False, 0)
        self.update_status()

        self.func_map = {}
        self.build_func_map()

    # ------------------------------------------------------------------
    # Theme switching
    # ------------------------------------------------------------------
    def _build_theme_menu(self):
        """Build the theme drop-down menu (using a Popover so it follows the dark/light style; a native Gtk.Menu cannot be colored)."""
        current = load_theme_pref()
        popover = Gtk.Popover()
        popover.set_relative_to(self.theme_button)
        popover.set_position(Gtk.PositionType.BOTTOM)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_border_width(6)
        box.get_style_context().add_class("theme-popover")
        self._theme_items = {}
        # Not using RadioMenuItem: the native radio dot overlaps the text.
        # Use plain button rows with icon + text instead; the selected row gets a check icon and styling is fully controllable.
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
        """Switch the button icon according to the current mode.
        Icons showing the target you switch to are more intuitive; this shows the icon of the currently active theme.
        """
        resolved = resolve_theme_mode(mode)
        icons = {
            "dark": "weather-clear-night-symbolic",   # dark -> moon
            "light": "weather-clear-symbolic",        # light -> sun
        }
        name = icons.get(resolved, "weather-clear-night-symbolic")
        try:
            if self._theme_icon is not None:
                self._theme_icon.set_from_icon_name(name, Gtk.IconSize.BUTTON)
        except Exception:
            pass

    def on_theme_row_clicked(self, button, mode):
        """User clicked a theme row: apply and save immediately."""
        apply_app_css(mode)
        save_theme_pref(mode)
        self._refresh_theme_icon(mode)
        # Update the selection marker
        for m, (_row, chk) in self._theme_items.items():
            try:
                chk.set_opacity(1.0 if m == mode else 0.0)
            except Exception:
                pass
        # Close the popover
        try:
            popover = self.theme_button.get_popover()
            if popover is not None:
                popover.popdown()
        except Exception:
            pass

    def on_theme_selected(self, item, mode):
        """Legacy interface: user selects a theme."""
        if not item.get_active():
            return
        apply_app_css(mode)
        save_theme_pref(mode)
        self._refresh_theme_icon(mode)
        # Close the popover
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
        """Detect whether this is a "SteamOS + Windows" dual-boot system.

        Why multiple criteria are needed:
        1) Windows appears in the EFI boot entries -- the most direct check, but Clover removes/renames the Windows
           EFI boot entry when installed (booting moves to the Clover menu), so on dual-boot machines with Clover
           the word "Windows" is often invisible here, and relying only on this item misjudges it as "Single Boot".
        2) An NTFS partition labelled Windows exists -- no root needed, stable and reliable.
        3) The NTFS partition contains the Windows directory structure (Windows/Program Files/Users) --
           detectable even if the label was changed.
        4) A mounted NTFS partition has the same structure as above.
        Note: do not judge dual boot by the "Clover boot entry" alone -- a single-boot system with Clover also matches.
        Any one of 2/3/4 being true is enough to declare dual boot.
        """
        # ---- Criterion 1: Windows in the EFI boot entries ----
        if shutil.which("efibootmgr"):
            for cmd in (["sudo", "-n", "efibootmgr"], ["efibootmgr"]):
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        if re.search(r'(?i)windows', result.stdout):
                            return "Dual Boot"
                        break  # Valid output obtained; no need to try the next method
                except Exception:
                    continue

        # ---- Criteria 2/3: scan NTFS partitions (lsblk needs no root) ----
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
                    # Criterion 2: the partition label is literally Windows
                    if label.lower() == "windows":
                        return "Dual Boot"
                    ntfs_entries.append(fields)

                # Criteria 3/4: look for the Windows directory structure in the partition contents
                for fields in ntfs_entries:
                    name = fields.get("NAME") or ""
                    mountpoint = (fields.get("MOUNTPOINT") or "").strip()
                    candidates = []
                    if mountpoint and os.path.isdir(mountpoint):
                        candidates.append(mountpoint)
                    # For unmounted partitions, try the common udisks mount paths
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
                        # The Windows root has a Windows/ directory plus (Program Files or Users)
                        has_win_dir = os.path.isdir(os.path.join(path, "Windows"))
                        has_pf = os.path.isdir(os.path.join(path, "Program Files"))
                        has_users = os.path.isdir(os.path.join(path, "Users"))
                        if has_win_dir and (has_pf or has_users):
                            return "Dual Boot"
        except Exception:
            pass

        return "Single Boot"

    def on_category_activated(self, treeview, path, column):
        model = treeview.get_model(); iter_ = model.get_iter(path); category = model.get_value(iter_, 1)
        if self.search_entry.get_text().strip():
            self.search_entry.set_text("")
        if category == "Support & Maintenance":
            self._current_page = "about"
            self.stack.set_visible_child_name("about"); self.title_icon.set_visible(False); self.category_title.set_visible(False); return
        if category == "Changelog":
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
        if category == "System Optimization": title_text = f"<big><b>{category} [{self.system_type}]</b></big>"
        else: title_text = f"<big><b>{category}</b></big>"
        self.category_title.set_markup(title_text); self.category_title.set_visible(True)

        self.func_store.clear()
        items = list(self.category_tree.get(category, []))
        if category == "System Optimization" and self.system_type == "Dual Boot":
            items = items[:] + [("System Health Check", "health_check"),
                                ("Fix Boot", "fix_boot"),
                                ("Fix Shared Disk", "fix_shared_disk")]
            self.func_map["System Health Check"] = "health_check"
            self.func_map["Fix Boot"] = "fix_boot"
            self.func_map["Fix Shared Disk"] = "fix_shared_disk"

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
        if self.system_type == "Dual Boot":
            for name, key in (("System Health Check", "health_check"),
                              ("Fix Boot", "fix_boot"),
                              ("Fix Shared Disk", "fix_shared_disk")):
                if query in name.lower():
                    matches.append((name, "System Optimization", key))
        self.search_store.clear()
        for name, cat, key in matches:
            self.search_store.append([name, cat, key])
        if matches:
            self.search_title.set_markup(f"<big><b>Search Results ({len(matches)} items)</b></big>")
        else:
            self.search_title.set_markup("<big><b>Search Results (no matches)</b></big>")
        self.stack.set_visible_child_name("search")

    def on_search_row_activated(self, treeview, path, column):
        model = treeview.get_model(); iter_ = model.get_iter(path)
        func_name = model.get_value(iter_, 0)
        func_key = model.get_value(iter_, 2)
        self.run_function(func_name, func_key)

    def run_function(self, func_name, func_key):
        if func_key in DANGEROUS_FUNCS:
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.NONE,
                                    text=f"Confirm dangerous operation: {func_name}")
            dlg.add_button("No", Gtk.ResponseType.NO)
            dlg.add_button("Yes", Gtk.ResponseType.YES)
            dlg.format_secondary_text(DANGEROUS_HINTS.get(func_key, DEFAULT_DANGEROUS_HINT))
            # Default focus on No for dangerous operations, so pressing Enter by accident does not execute
            try:
                dlg.set_default_response(Gtk.ResponseType.NO)
            except Exception:
                pass
            response = dlg.run()
            dlg.destroy()
            if response != Gtk.ResponseType.YES:
                return

        if func_name in ("Steam Cache Manager", "GE-Proton Manager", "Uninstall Other Installed Apps"):
            self._run_standalone_script(func_key); return
        if func_name == "UU Accelerator Plugin":
            self.run_external_terminal(func_key); return

        if self.task_window: self.task_window.destroy()
        self.task_window = TaskWindow(self, func_key, func_name)

    def update_status(self):
        term = "Embedded Terminal" if VTE_AVAILABLE else "External Terminal"
        self.status_label.set_text(f"System: {self.system_type} | Terminal: {term} | Version: v{VERSION}")

    def display_changelog(self):
        changelog_content = """2026-10-22 (v1.9.4)
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
        # These features interact through zenity dialogs, so their output does not go to the embedded terminal.
        # If zenity is missing, the script only writes errors to the log and the user sees no feedback at all,
        # so check for it first and tell the user explicitly with a dialog when it is missing.
        if not shutil.which("zenity"):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.NONE,
                                    text="The zenity component is missing; this feature cannot run")
            dlg.add_button("OK", Gtk.ResponseType.OK)
            dlg.format_secondary_text(
                "This feature relies on zenity for its graphical selection dialogs.\n"
                "Please install it first and try again: sudo pacman -S zenity")
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
                                    text="Failed to start task")
            dlg.add_button("OK", Gtk.ResponseType.OK)
            dlg.format_secondary_text(f"{e}")
            dlg.run(); dlg.destroy()

    def run_external_terminal(self, func_key):
        tmp_path = create_temp_script()
        cmd = f"bash {tmp_path} {func_key}; read -p 'Press Enter to close...' -n1"
        if not launch_terminal(cmd):
            dlg = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.NONE,
                                    text="No usable terminal emulator found")
            dlg.add_button("OK", Gtk.ResponseType.OK)
            dlg.format_secondary_text("Please install konsole or xterm and try again.")
            dlg.run(); dlg.destroy()

    def on_help_clicked(self, button):
        help_dialog = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.NONE, text="Steam Deck Toolbox")
        help_dialog.add_button("OK", Gtk.ResponseType.OK)
        # Use a Label with markup so the X handle is a real clickable link.
        # format_secondary_text() cannot render hyperlinks.
        help_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        help_box.set_margin_start(12); help_box.set_margin_end(12)
        help_box.set_margin_top(4); help_box.set_margin_bottom(8)
        body = Gtk.Label()
        body.set_markup(
            "This tool integrates system optimization, software installation, network tools and more.\n"
            "Click a category on the left to show its function list on the right.\n"
            "Follow <a href=\"https://x.com/AlanWake2100\">AlanWake (@AlanWake2100)</a> on X for updates~")
        body.set_line_wrap(True)
        body.set_xalign(0.0)
        body.set_selectable(False)
        body.connect("activate-link", lambda lbl, uri: (Gtk.show_uri_on_window(help_dialog, uri, Gtk.get_current_event_time()), True)[1])
        help_box.pack_start(body, False, False, 0)
        help_box.show_all()
        help_dialog.get_message_area().pack_start(help_box, False, False, 0)
        help_dialog.run(); help_dialog.destroy()

def ensure_desktop_shortcut():
    script_path = os.path.abspath(sys.argv[0])
    desktop_dir = os.path.expanduser("~/Desktop")
    desktop_file = os.path.join(desktop_dir, "Deck Toolbox.desktop")
    if os.path.exists(desktop_file): return
    content = f"""[Desktop Entry]
Type=Application
Name=Deck Toolbox
Comment=Steam Deck Toolbox launcher
Exec={sys.executable} "{script_path}"
Icon=input-gamepad-symbolic
Terminal=false
StartupNotify=true
Categories=Utility;
"""
    try:
        with open(desktop_file, 'w') as f: f.write(content)
        os.chmod(desktop_file, 0o755)
    except Exception as e: print(f"Failed to create desktop shortcut: {e}")

def ensure_vte_installed():
    if VTE_AVAILABLE: return
    dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.NONE, "The VTE terminal component was not found.\nInstall it now? (Requires a sudo password; restart the program manually afterwards)")
    dialog.format_secondary_text("Clicking Yes disables read-only mode and installs vte3 automatically.")
    dialog.add_button("Yes", Gtk.ResponseType.YES); dialog.add_button("No", Gtk.ResponseType.NO)
    dialog.set_icon_name("input-gamepad-symbolic")
    response = dialog.run(); dialog.destroy()
    if response == Gtk.ResponseType.YES:
        install_cmd = (
            "if command -v steamos-readonly >/dev/null 2>&1; then "
            "sudo steamos-readonly disable || { echo '✗ Failed to disable read-only mode; run manually: sudo steamos-readonly disable'; read -n1; exit 1; }; "
            "fi; "
            "echo 'Initializing the pacman keyring (this may take a while)...'; "
            "sudo pacman-key --init || { echo '✗ Failed to initialize the pacman keyring'; read -n1; exit 1; }; "
            "sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null; sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null; "
            # Important: 889B5EBD... belongs to holo-keyring; the holo keyring must be imported as well,
            # otherwise the key is not in the local keyring and --lsign-key reports "cannot be signed locally".
            "echo 'Importing Arch official and SteamOS Holo keys...'; "
            "sudo pacman-key --populate archlinux || { echo '✗ Failed to populate the archlinux keyring'; read -n1; exit 1; }; "
            "if [ -f /usr/share/pacman/keyrings/holo.gpg ]; then "
            "sudo pacman-key --populate holo || { echo '✗ Failed to populate the holo keyring'; read -n1; exit 1; }; "
            "fi; "
            "echo 'Trusting the SteamOS packager key...'; "
            "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || { "
            "echo '⚠ Signing failed; retrying after refreshing the keyring...'; "
            "sudo pacman-key --refresh-keys 2>/dev/null; "
            "sudo pacman-key --populate archlinux holo 2>/dev/null; "
            "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || "
            "{ echo '✗ Failed to sign the key'; read -n1; exit 1; }; }; "
            "sudo pacman -Sy --noconfirm >/dev/null 2>&1; "
            "sudo pacman -S --needed --noconfirm vte3 || { echo '✗ Failed to install vte3; check your network or repositories'; read -n1; exit 1; }; "
            "pacman -Q vte3 >/dev/null 2>&1 || { echo '✗ Post-install verification of vte3 failed; restart the program and try again'; read -n1; exit 1; }; "
            "command -v steamos-readonly >/dev/null 2>&1 && sudo steamos-readonly enable 2>/dev/null || true; "
            "echo '✓ Installation complete. Please restart this program manually.'; read -n1"
        )
        if not launch_terminal(install_cmd):
            err = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.NONE,
                                    "No usable terminal emulator found")
            err.add_button("OK", Gtk.ResponseType.OK)
            err.format_secondary_text("Please open a terminal manually and run: sudo pacman -S --noconfirm vte3")
            err.run(); err.destroy()

def sync_emoji_icons():
    """Ensure an emoji_icons folder exists next to the script (extracted from embedded data; works offline and is easy to customize)."""
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
            print(f"Failed to write icon {icon_name}: {e}")

def get_remote_version():
    try:
        req = urllib.request.Request(REPO_RAW_URL, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=VERSION_CHECK_TIMEOUT) as response:
            content = response.read().decode('utf-8')
            match = re.search(r'^VERSION\s*=\s*["\']([0-9.]+)["\']', content, re.MULTILINE)
            if match: return match.group(1)
            match = re.search(r'VERSION\s*=\s*["\']([0-9.]+)["\']', content)
            if match: return match.group(1)
    except Exception as e: print(f"Update check failed: {e}")
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
                raise ValueError('Downloaded content validation failed (not a valid script file); update aborted')
            # Validate the syntax once more: if the remote file was corrupted, writing it in produces an unrunnable program
            compile(new_content, '<remote>', 'exec')
            current_path = os.path.abspath(sys.argv[0])
            backup_path = current_path + ".bak"
            try: shutil.copy2(current_path, backup_path)
            except: pass
            # Write a temp file first, then atomically replace: opening the script itself with 'w' truncates it first,
            # and any error/power loss during the write would leave the toolbox completely broken and unbootable.
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
    dialog.set_markup("<big><b>✅ Update Complete</b></big>")
    dialog.format_secondary_text(f"New version v{remote_version} has been downloaded.\nThe program will restart automatically...")
    def restart():
        dialog.destroy(); subprocess.Popen([sys.executable, sys.argv[0]]); Gtk.main_quit()
    GLib.timeout_add(500, restart)

def _update_dialog_error(dialog, error_msg):
    dialog.set_markup("<big><b>❌ Update Failed</b></big>")
    dialog.format_secondary_text(f"An error occurred during the update: {error_msg}\nPlease download the latest version manually from:\n{REPO_RAW_URL}")
    for btn in dialog.get_action_area().get_children(): btn.destroy()
    dialog.add_button("OK", Gtk.ResponseType.CLOSE)
    dialog.connect("response", lambda d, r: (dialog.destroy(), show_main_window()))
    dialog.show_all()

class UpdateCheckWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Check for Updates")
        self.set_icon_name("input-gamepad-symbolic"); self.set_default_size(400, 150); self.set_position(Gtk.WindowPosition.CENTER); self.set_deletable(False)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); vbox.set_margin_top(20); vbox.set_margin_bottom(20); vbox.set_margin_start(20); vbox.set_margin_end(20); self.add(vbox)
        self.label = Gtk.Label(label="Checking for updates..."); self.label.set_justify(Gtk.Justification.CENTER); vbox.pack_start(self.label, True, True, 0)
        self.button = None; self.vbox = vbox; self.show_all(); GLib.timeout_add(200, self.perform_check)

    def perform_check(self):
        def check_thread():
            sync_emoji_icons(); remote_version = get_remote_version(); GLib.idle_add(self.on_check_done, remote_version)
        threading.Thread(target=check_thread, daemon=True).start(); return False

    def on_check_done(self, remote_version):
        if remote_version is None:
            self.label.set_text("Update check failed. Please check your network connection.")
            if self.button is None:
                self.button = Gtk.Button(label="Enter Main Window"); self.button.connect("clicked", self.on_button_clicked); self.vbox.pack_start(self.button, False, False, 0)
            self.button.show(); return
        if compare_versions(remote_version, VERSION) <= 0:
            self.label.set_text(f"You are on the latest version (v{VERSION})")
            if self.button is not None: self.button.hide()
            GLib.timeout_add(300, self.auto_enter_main); return
        self.label.set_text(f"New version v{remote_version} found\nCurrent version: v{VERSION}")
        if self.button is not None: self.button.hide()
        self.show_update_prompt(remote_version)

    def auto_enter_main(self):
        self.destroy(); show_main_window(); return False

    def show_update_prompt(self, remote_version):
        self.destroy()
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.NONE, "New Version Found")
        dialog.set_default_size(400, 150); dialog.set_markup(f"<big><b>New version v{remote_version} found</b></big>")
        dialog.format_secondary_text(f"Current version: v{VERSION}\nLatest version: v{remote_version}\n\nUpdate now?")
        dialog.add_button("Yes", Gtk.ResponseType.YES); dialog.add_button("No", Gtk.ResponseType.NO); dialog.set_icon_name("input-gamepad-symbolic")
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            dialog.set_markup("<big><b>Updating...</b></big>"); dialog.format_secondary_text("Downloading the new version, please wait.")
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
    # Critical order: this must happen before apply_app_css rewrites GTK prefer-dark,
    # recording the real system color scheme first, otherwise "Follow System" reads back a value we changed ourselves.
    reset_system_theme_cache()

    # Apply the theme the user chose last time at startup (default: follow system)
    apply_app_css(load_theme_pref())
    update_win = UpdateCheckWindow(); Gtk.main()

if __name__ == "__main__":
    main()
