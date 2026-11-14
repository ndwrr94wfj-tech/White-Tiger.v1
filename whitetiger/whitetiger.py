#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =========================================================================== #
#   W H I T E T I G E R   ::   v1.0
#   osint · csint · pentest multitool
#
#   run:   python3 whitetiger.py
#   flags: --no-anim --calm --no-color --fast --rain --glitch --no-glitch
#          --fps=N --theme=NAME --layout=auto|boxes|flat
#          --module N --list --selftest
#   single file · stdlib only · python 3.8+
# =========================================================================== #

from __future__ import annotations

import base64
import bz2
import configparser
import csv
import difflib
import gzip
import hashlib
import hmac
import html as htmlmod
import importlib.util
import ipaddress
import json
import lzma
import math
import os
import platform
import random
import re
import shutil
import socket
import ssl
import statistics
import string
import struct
import subprocess
import sys
import tarfile
import textwrap
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

if sys.version_info < (3, 8):
    sys.exit("needs python 3.8+")

IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"

VERSION = "1.0"
AUTHOR = "@azerkash"
ROOT = r"C:\WhiteTiger-Tools" if IS_WIN else "~/WhiteTiger-Tools"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

TTY = sys.stdout.isatty()
COLOR = TTY and not os.environ.get("NO_COLOR")

ESC = "\033["
RESET = ESC + "0m" if COLOR else ""
BOLD = ESC + "1m" if COLOR else ""
DIM = ESC + "2m" if COLOR else ""
HIDE_CUR = ESC + "?25l"
SHOW_CUR = ESC + "?25h"
CLEAR = ESC + "2J" + ESC + "H"
SAVE, REST = ESC + "s", ESC + "u"
H = "\x1b"

STRIP = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def fg(c):
    if not COLOR or c is None:
        return ""
    return f"{ESC}38;2;{c[0]};{c[1]};{c[2]}m"


def bg(c):
    if not COLOR or c is None:
        return ""
    return f"{ESC}48;2;{c[0]};{c[1]};{c[2]}m"


def lerp(a, b, t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def scale(c, k):
    return (max(0, min(255, int(c[0] * k))), max(0, min(255, int(c[1] * k))),
            max(0, min(255, int(c[2] * k))))


def vis_len(s):
    if not COLOR or H not in s:
        return len(s)
    return len(STRIP.sub("", s))


def trunc(s, w):
    if vis_len(s) <= w:
        return s
    out, n, i = [], 0, 0
    while i < len(s) and n < w:
        if s[i] == H:
            k = s.find("m", i)
            if k < 0:
                break
            out.append(s[i:k + 1])
            i = k + 1
            continue
        out.append(s[i])
        i += 1
        n += 1
    return "".join(out) + RESET


def pad(s, w):
    v = vis_len(s)
    if v == w:
        return s
    if v < w:
        return s + " " * (w - v)
    return trunc(s, w)


def center_line(s, w=None):
    """centre a single line inside width w (defaults to terminal width)"""
    w = w or tw()
    v = vis_len(s)
    if v >= w:
        return trunc(s, w)
    left = (w - v) // 2
    return " " * left + s + " " * max(0, w - v - left)


def clear():
    if TTY:
        os.write(1, CLEAR.encode())


def tw(default=110):
    try:
        return shutil.get_terminal_size((default, 34)).columns
    except Exception:
        return default


def th_(default=34):
    try:
        return shutil.get_terminal_size((110, default)).lines
    except Exception:
        return default


def out_path(name):
    return os.path.join(os.getcwd(), name)


def setup_console():
    if IS_WIN:
        os.system("")
        try:
            os.system("chcp 65001 > nul")
        except Exception:
            pass
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    urllib.request.install_opener(
        urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx)))
    try:
        os.write(1, f"{ESC}]0;WhiteTiger\007".encode())
    except Exception:
        pass


def bell():
    try:
        os.write(1, b"\a")
    except Exception:
        pass


def fmt_dur(sec):
    sec = int(sec)
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    if d:
        return f"{d}d{h:02d}:{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def human(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024.0
    return f"{n:.1f} PB"


def safe_name(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)[:80]


def safe_extract(obj, dest):
    try:
        obj.extractall(dest, filter="data")
    except TypeError:
        obj.extractall(dest)


# --------------------------------------------------------------------------- #
#  themes
# --------------------------------------------------------------------------- #
THEMES = {
    "ice": {"label": "Ice Tiger",
            "grad": [(0.00, (30, 90, 170)), (0.22, (90, 190, 255)), (0.45, (240, 252, 255)),
                     (0.62, (255, 255, 255)), (0.82, (110, 180, 240)), (1.00, (25, 75, 150))],
            "glow": (255, 255, 255), "accent": (120, 225, 255), "key": (185, 240, 255),
            "text": (220, 238, 255), "border": (70, 130, 185), "dim": (95, 115, 135)},
    "blood": {"label": "Blood Moon",
              "grad": [(0.00, (70, 6, 14)), (0.22, (200, 40, 45)), (0.45, (255, 200, 180)),
                       (0.62, (255, 245, 235)), (0.82, (215, 55, 50)), (1.00, (75, 8, 16))],
              "glow": (255, 250, 245), "accent": (255, 95, 80), "key": (255, 175, 155),
              "text": (250, 228, 218), "border": (170, 45, 45), "dim": (145, 100, 100)},
    "matrix": {"label": "Matrix",
               "grad": [(0.00, (5, 55, 20)), (0.22, (40, 200, 90)), (0.45, (200, 255, 210)),
                        (0.62, (235, 255, 240)), (0.82, (60, 210, 110)), (1.00, (8, 60, 25))],
               "glow": (245, 255, 245), "accent": (90, 255, 140), "key": (175, 255, 195),
               "text": (205, 250, 215), "border": (35, 150, 75), "dim": (85, 135, 98)},
    "vapor": {"label": "Vaporwave",
              "grad": [(0.00, (60, 20, 120)), (0.22, (170, 60, 220)), (0.45, (255, 150, 230)),
                       (0.62, (255, 240, 255)), (0.82, (90, 220, 255)), (1.00, (45, 15, 100))],
              "glow": (255, 250, 255), "accent": (255, 130, 240), "key": (190, 180, 255),
              "text": (240, 225, 255), "border": (140, 80, 200), "dim": (130, 110, 160)},
    "amber": {"label": "Amber CRT",
              "grad": [(0.00, (70, 40, 0)), (0.25, (220, 140, 20)), (0.50, (255, 220, 150)),
                       (0.72, (255, 245, 210)), (1.00, (90, 50, 0))],
              "glow": (255, 245, 215), "accent": (255, 185, 60), "key": (255, 215, 130),
              "text": (250, 232, 200), "border": (185, 120, 25), "dim": (140, 105, 55)},
    "cyan": {"label": "Cyber Cyan",
             "grad": [(0.00, (0, 55, 65)), (0.25, (0, 200, 220)), (0.50, (180, 255, 255)),
                      (0.72, (240, 255, 255)), (1.00, (0, 70, 85))],
             "glow": (240, 255, 255), "accent": (0, 235, 255), "key": (140, 245, 255),
             "text": (210, 245, 250), "border": (0, 150, 175), "dim": (85, 130, 140)},
    "mono": {"label": "Mono",
             "grad": [(0.00, (55, 55, 55)), (0.30, (170, 170, 170)), (0.55, (255, 255, 255)),
                      (0.80, (150, 150, 150)), (1.00, (50, 50, 50))],
             "glow": (255, 255, 255), "accent": (230, 230, 230), "key": (255, 255, 255),
             "text": (210, 210, 210), "border": (120, 120, 120), "dim": (105, 105, 105)},
    "rust": {"label": "Oxide",
             "grad": [(0.00, (60, 25, 10)), (0.25, (200, 90, 35)), (0.50, (255, 200, 150)),
                      (0.72, (255, 245, 230)), (1.00, (70, 30, 15))],
             "glow": (255, 240, 225), "accent": (255, 140, 70), "key": (255, 195, 140),
             "text": (250, 225, 205), "border": (175, 80, 35), "dim": (140, 105, 85)},
    "nord": {"label": "Nord",
             "grad": [(0.00, (40, 50, 65)), (0.28, (110, 140, 175)), (0.52, (215, 230, 245)),
                      (0.74, (240, 248, 255)), (1.00, (45, 55, 72))],
             "glow": (240, 248, 255), "accent": (140, 190, 230), "key": (190, 220, 245),
             "text": (225, 235, 245), "border": (90, 115, 150), "dim": (120, 135, 155)},
    "sakura": {"label": "Sakura",
               "grad": [(0.00, (85, 35, 60)), (0.26, (230, 130, 175)), (0.52, (255, 220, 235)),
                        (0.74, (255, 250, 252)), (1.00, (95, 40, 70))],
               "glow": (255, 248, 252), "accent": (255, 155, 200), "key": (255, 200, 225),
               "text": (252, 230, 242), "border": (200, 100, 150), "dim": (155, 115, 135)},
    "toxic": {"label": "Toxic",
              "grad": [(0.00, (20, 55, 20)), (0.26, (140, 240, 60)), (0.52, (230, 255, 190)),
                       (0.74, (250, 255, 240)), (1.00, (25, 65, 25))],
              "glow": (250, 255, 240), "accent": (170, 255, 90), "key": (215, 255, 160),
              "text": (225, 250, 205), "border": (95, 180, 45), "dim": (105, 140, 90)},
}

SETTINGS = {"anim": True, "boot": True, "glow": True, "notify": True,
            "theme": "ice", "fps": 30, "live_typing": True, "compact": False,
            "layout": "auto", "rain": False, "glitch": True, "flash": True,
            "truecolor": True, "stripes": True, "sweep": True}
TH = THEMES["ice"]

_RAW = r"""
__      __.__    .__  __       ___________.__
/  \    /  \  |__ |__|/  |_  ___\__    ___/|__| ____   ___________
\   \/\/   /  |  \|  \   __\/ __ \|    |   |  |/ ___\_/ __ \_  __ \
 \        /|   Y  \  ||  | \  ___/|    |   |  / /_/  >  ___/|  | \/
  \__/\  / |___|  /__||__|  \___  >____|   |__\___  / \___  >__|
       \/       \/              \/           /_____/      \/
"""
BANNER = [l.rstrip() for l in _RAW.strip("\n").split("\n")]
BANNER_W = max(len(l) for l in BANNER)


def banner_mode():
    if SETTINGS["compact"] or tw() < BANNER_W + 6:
        return "compact"
    return "full"


def block_h():
    n = 1 if banner_mode() == "compact" else len(BANNER)
    return n + 4


# --------------------------------------------------------------------------- #
#  output primitives
# --------------------------------------------------------------------------- #
def ok(m):
    print(f"  {fg(TH['accent'])}[+]{RESET} {fg(TH['text'])}{m}{RESET}")


def bad(m):
    print(f"  {fg(TH['dim'])}[-]{RESET} {fg(TH['dim'])}{m}{RESET}")


def wrn(m):
    print(f"  {fg((255, 200, 110))}[!]{RESET} {fg(TH['text'])}{m}{RESET}")


def inf(m):
    print(f"  {fg(TH['key'])}[*]{RESET} {fg(TH['text'])}{m}{RESET}")


def hit(m):
    print(f"  {fg((140, 255, 190))}[>]{RESET} {fg(TH['text'])}{m}{RESET}")


SEV_COLORS = {"critical": (255, 70, 70), "high": (255, 140, 60), "medium": (255, 210, 90),
              "low": (150, 210, 255), "info": (140, 150, 165)}


def sev_tag(sev):
    c = SEV_COLORS.get(sev, TH["dim"])
    if SETTINGS["flash"] and sev in ("critical", "high"):
        k = 0.70 + 0.30 * (1 + math.sin(FXS.t() * 5.0)) / 2
        c = scale(c, k)
    return f"{fg(c)}[{sev.upper():<8}]{RESET}"


def kv(k, v, w=24):
    print(f"    {fg(TH['dim'])}{k:<{w}}{RESET}{fg(TH['text'])}{str(v)[:170]}{RESET}")


def rule(title=""):
    print(f"  {fg(TH['border'])}{'─' * max(0, min(tw() - 6, 76))}{RESET}")
    if title:
        print(f"  {fg(TH['accent'])}{BOLD}{title}{RESET}")


def ask(label, default=""):
    d = f" {fg(TH['dim'])}[{default}]{RESET}" if default else ""
    try:
        v = input(f"  {fg(TH['key'])}{label}{RESET}{d} {fg(TH['accent'])}>{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return v or default


def pause(msg="press ENTER to return..."):
    try:
        input(f"  {fg(TH['dim'])}{msg}{RESET}")
    except (EOFError, KeyboardInterrupt):
        print()


def key_pressed():
    try:
        if IS_WIN:
            import msvcrt
            return msvcrt.kbhit()
        import select
        return bool(select.select([sys.stdin], [], [], 0)[0])
    except Exception:
        return False


def drain_key():
    try:
        if IS_WIN:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        else:
            import select
            while select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.read(1)
    except Exception:
        pass


REPORTS = []


def save_json(name, data):
    try:
        with open(out_path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        inf(f"saved -> {name}")
        REPORTS.append(name)
    except Exception as e:
        bad(f"save failed: {e}")


# --------------------------------------------------------------------------- #
#  FX — animation engine
# --------------------------------------------------------------------------- #
RAIN_GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎ0123456789#$%&@"
GLITCH_CHARS = "▓▒░█▚▞#@%&$?*"
STRIPE_CHARS = "▏▎▍▌▋▊▉"


class FX:
    def __init__(self):
        self.t0 = time.time()
        self.flash = 0.0
        self.rain = None
        self.burst = 0.0

    def t(self):
        return time.time() - self.t0

    def ping(self, sec=0.4):
        self.flash = time.time() + sec

    def burst_now(self):
        self.burst = time.time() + 0.30

    def in_burst(self):
        return time.time() < self.burst


FXS = FX()


class MatrixRain:
    def __init__(self, w, h):
        self.w, self.h = max(1, w), max(1, h)
        self.drops = [random.randrange(-self.h, 0) for _ in range(self.w)]
        self.spd = [random.choice((1, 1, 2, 3)) for _ in range(self.w)]
        self.trail = [random.randrange(4, 12) for _ in range(self.w)]

    def step(self):
        for i in range(self.w):
            self.drops[i] += self.spd[i]
            if self.drops[i] > self.h + random.randrange(0, 14):
                self.drops[i] = random.randrange(-10, 0)
                self.spd[i] = random.choice((1, 1, 2, 3))
                self.trail[i] = random.randrange(4, 12)

    def render(self, th):
        grid = [[" "] * self.w for _ in range(self.h)]
        for x in range(self.w):
            head = self.drops[x]
            for k in range(self.trail[x]):
                y = head - k
                if 0 <= y < self.h:
                    grid[y][x] = RAIN_GLYPHS[(x * 7 + y * 3 + int(FXS.t() * 6)) %
                                             len(RAIN_GLYPHS)]
        rows = []
        for y in range(self.h):
            chars, cols = [], []
            for x in range(self.w):
                ch = grid[y][x]
                if ch == " ":
                    chars.append(" ")
                    cols.append(th["dim"])
                else:
                    d = self.drops[x] - y
                    f = max(0.0, 1.0 - d / max(1, self.trail[x]))
                    chars.append(ch)
                    cols.append(lerp(th["border"], th["glow"], f ** 1.6))
            rows.append(paint(chars, cols))
        return rows


# --------------------------------------------------------------------------- #
#  progress
# --------------------------------------------------------------------------- #
BLOCKS = "▁▂▃▄▅▆▇█"
SPARKS = "▁▂▃▄▅▆▇█"


class Progress:
    def __init__(self, total, label="working", width=26):
        self.total = max(1, total)
        self.n = 0
        self.label = label
        self.w = width
        self.t0 = time.time()
        self.live = False
        self.samples = deque(maxlen=48)

    def _rate(self):
        if len(self.samples) > 1:
            dt = self.samples[-1][0] - self.samples[0][0]
            dn = self.samples[-1][1] - self.samples[0][1]
            if dt > 0.2 and dn > 0:
                return dn / dt
        el = time.time() - self.t0
        return self.n / el if el > 0.05 and self.n else 0.0

    def _eta(self, rate):
        if rate <= 0:
            return "--"
        return fmt_dur((self.total - self.n) / rate)

    def _draw(self):
        frac = self.n / self.total
        fill = int(self.w * frac)
        chars, cols = [], []
        for x in range(self.w):
            if x < fill:
                chars.append("█")
                cols.append(lerp(TH["accent"], TH["key"], x / max(1, self.w - 1)))
            elif x == fill:
                chars.append("▌")
                cols.append(TH["glow"])
            else:
                chars.append("░")
                cols.append(TH["dim"])
        sh = int((FXS.t() * 22.0) % (self.w + 8)) - 4
        for x in range(max(0, sh - 3), min(self.w, sh + 4)):
            cols[x] = lerp(cols[x], TH["glow"], 0.55)
        rate = self._rate()
        lat = list(LIVE["lat"])[-10:]
        spark = "".join(SPARKS[min(7, int(min(1.0, v / 130.0) * 8))] for v in lat)
        sys.stdout.write(
            f"\r  {fg(TH['key'])}{self.label[:13]:<13}{RESET}{paint(chars, cols)} "
            f"{fg(TH['text'])}{self.n}/{self.total}{RESET} "
            f"{fg(TH['dim'])}{rate:5.1f}/s eta {self._eta(rate)}{RESET} "
            f"{fg(TH['border'])}{spark}{RESET}  ")
        sys.stdout.flush()
        self.live = True

    def update(self, n=1):
        self.n += n
        self.samples.append((time.time(), self.n))
        self._draw()

    def line(self):
        sys.stdout.write("\r" + " " * max(1, tw() - 2) + "\r")
        sys.stdout.flush()
        self.live = False

    def done(self, msg=None):
        if self.live:
            self.line()
        if msg:
            ok(msg)


def spin(msg, seconds=0.6):
    frames = "|/-\\" if IS_WIN else "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r  {fg(TH['accent'])}{frames[i % len(frames)]}{RESET} "
                         f"{fg(TH['dim'])}{msg}{RESET}   ")
        sys.stdout.flush()
        i += 1
        time.sleep(0.05)
    sys.stdout.write("\r" + " " * max(1, tw() - 2) + "\r")
    sys.stdout.flush()


# --------------------------------------------------------------------------- #
#  network core
# --------------------------------------------------------------------------- #
def http_get(url, timeout=10, headers=None, method="GET", max_bytes=None, retries=2):
    hdrs = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
    if headers:
        hdrs.update(headers)
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read(max_bytes) if max_bytes else r.read()
                return r.getcode(), data, {k.lower(): v for k, v in r.getheaders()}
        except urllib.error.HTTPError as e:
            try:
                data = e.read(max_bytes) if max_bytes else e.read()
            except Exception:
                data = b""
            try:
                h = {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
            except Exception:
                h = {}
            return e.code, data, h
        except Exception:
            if attempt < retries:
                time.sleep(0.3)
    return None, b"", {}


def http_post(url, payload=None, headers=None, timeout=15, raw=None, ctype=None):
    body = raw if raw is not None else (json.dumps(payload).encode()
                                        if payload is not None else b"")
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    hdrs["Content-Type"] = ctype or "application/json"
    if headers:
        hdrs.update(headers)
    try:
        req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read(), {k.lower(): v for k, v in r.getheaders()}
    except urllib.error.HTTPError as e:
        try:
            d = e.read()
        except Exception:
            d = b""
        return e.code, d, {}
    except Exception:
        return None, b"", {}


def http_raw(host, port, request, timeout=8, tls=False):
    """send a raw HTTP request over a socket and return the raw reply"""
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        if tls:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=host)
        s.settimeout(timeout)
        s.sendall(request)
        data = b""
        while len(data) < 200000:
            try:
                chunk = s.recv(8192)
            except Exception:
                break
            if not chunk:
                break
            data += chunk
        s.close()
        return data
    except Exception:
        return b""


def multipart(fields, files):
    b = "----WT" + str(random.randint(10 ** 8, 10 ** 9))
    body = b""
    for k, v in fields.items():
        body += (f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                 f"{v}\r\n").encode()
    for k, (fn, data, ct) in files.items():
        body += (f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; "
                 f"filename=\"{fn}\"\r\nContent-Type: {ct}\r\n\r\n").encode()
        body += data + b"\r\n"
    body += f"--{b}--\r\n".encode()
    return body, f"multipart/form-data; boundary={b}"


def jload(body):
    try:
        return json.loads(body.decode("utf-8", "replace"))
    except Exception:
        return None


def get_json(url, timeout=12, headers=None):
    st, body, _ = http_get(url, timeout=timeout, headers=headers)
    return jload(body) if st == 200 else None


DOH = ["https://dns.google/resolve?name={}&type={}",
       "https://cloudflare-dns.com/dns-query?name={}&type={}",
       "https://dns.quad9.net:5053/dns-query?name={}&type={}",
       "https://doh.opendns.com/dns-query?name={}&type={}"]


def doh(name, rtype="A", want_status=False):
    for tpl in DOH:
        st, body, _ = http_get(tpl.format(urllib.parse.quote(name), rtype),
                               timeout=6, headers={"Accept": "application/dns-json"})
        if st is None:
            continue
        d = jload(body)
        if d is None:
            continue
        recs = [a.get("data", "") for a in d.get("Answer", []) if a.get("data")]
        if want_status:
            return recs, d.get("Status", 0)
        return recs
    return ([], None) if want_status else []


def dns_all(domain):
    out = {}
    for t in ("A", "AAAA", "MX", "NS", "TXT", "SOA", "CAA", "SRV", "DS", "PTR"):
        r = doh(domain, t)
        if r:
            out[t] = r
    return out


def strip_tags(s):
    if s is None:
        return ""
    return htmlmod.unescape(re.sub(r"<[^>]+>", " ", s)).strip()


def resolve(host):
    try:
        return socket.gethostbyname(host)
    except Exception:
        return None


def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None


def cname_of(host):
    try:
        cmd = (["nslookup", "-type=CNAME", host] if IS_WIN
               else ["dig", "+short", "CNAME", host])
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             timeout=6).stdout.decode("utf-8", "replace")
        m = re.search(r"canonical name = (\S+)", out)
        if m:
            return m.group(1).rstrip(".")
        lines = [l for l in out.strip().splitlines() if l.strip()]
        if lines:
            return lines[0].rstrip(".")
    except Exception:
        pass
    return None


SERVICES = {20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
            67: "dhcp", 69: "tftp", 80: "http", 88: "kerberos", 110: "pop3", 111: "rpcbind",
            123: "ntp", 135: "msrpc", 137: "netbios-ns", 138: "netbios-dgm",
            139: "netbios-ssn", 143: "imap", 161: "snmp", 162: "snmptrap", 179: "bgp",
            389: "ldap", 443: "https", 445: "smb", 465: "smtps", 500: "isakmp", 514: "syslog",
            515: "lpd", 548: "afp", 554: "rtsp", 587: "smtp-sub", 623: "ipmi", 631: "ipp",
            636: "ldaps", 873: "rsync", 902: "vmware", 989: "ftps-data", 990: "ftps",
            993: "imaps", 995: "pop3s", 1025: "nfs-or-iis", 1080: "socks", 1194: "openvpn",
            1433: "mssql", 1521: "oracle", 1701: "l2tp", 1723: "pptp", 1883: "mqtt",
            2049: "nfs", 2082: "cpanel", 2181: "zookeeper", 2222: "ssh-alt", 2375: "docker",
            2376: "docker-tls", 3000: "dev-http", 3128: "squid", 3260: "iscsi", 3306: "mysql",
            3389: "rdp", 3478: "stun", 4000: "icq", 4369: "epmd", 4444: "msf", 4505: "salt",
            4506: "salt", 5000: "dev-http", 5060: "sip", 5222: "xmpp", 5269: "xmpp-server",
            5353: "mdns", 5432: "postgres", 5555: "adb", 5601: "kibana", 5672: "amqp",
            5900: "vnc", 5938: "teamviewer", 5984: "couchdb", 6000: "x11", 6379: "redis",
            6443: "k8s-api", 7001: "weblogic", 7077: "spark", 8000: "http-alt",
            8008: "http-alt", 8009: "ajp", 8010: "http-alt", 8042: "http-alt", 8069: "odoo",
            8080: "http-proxy", 8081: "http-alt", 8086: "influxdb", 8088: "http-alt",
            8090: "http-alt", 8123: "clickhouse", 8161: "activemq", 8200: "vault",
            8443: "https-alt", 8500: "consul", 8529: "arangodb", 8834: "nessus",
            8888: "http-alt", 8983: "solr", 9000: "http-alt", 9001: "tor-orc",
            9042: "cassandra", 9090: "http-alt", 9092: "kafka", 9100: "printer",
            9200: "elasticsearch", 9300: "es-transport", 9418: "git", 9443: "https-alt",
            9600: "http-alt", 10000: "webmin", 10250: "kubelet", 11211: "memcached",
            15672: "rabbitmq-mgmt", 27017: "mongodb", 27018: "mongodb",
            28017: "mongodb-web", 50000: "db2", 50070: "hadoop", 61616: "activemq"}

HTTP_PORTS = {80, 81, 88, 3000, 5000, 8000, 8008, 8080, 8081, 8088, 8888, 9000, 9090, 10000}
TLS_PORTS = {443, 465, 636, 853, 990, 993, 995, 8443, 9443}
TOP_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 587, 993, 995, 1433, 3306, 3389,
             5432, 5900, 6379, 8000, 8080, 8443, 9200, 11211, 27017]
TOP_1000_EXTRA = sorted({p for p in SERVICES} | {
    1, 7, 9, 13, 17, 19, 37, 42, 49, 70, 79, 81, 82, 83, 84, 85, 89, 90, 99, 100, 106, 109,
    119, 125, 133, 144, 146, 155, 156, 158, 161, 163, 177, 194, 199, 211, 212, 213, 220, 256,
    259, 264, 280, 301, 306, 311, 340, 366, 389, 406, 407, 416, 417, 425, 427, 443, 444, 458,
    464, 465, 481, 497, 500, 512, 513, 518, 520, 523, 524, 525, 530, 531, 532, 533, 540, 543,
    544, 546, 547, 548, 554, 555, 556, 563, 587, 593, 604, 616, 617, 625, 631, 636, 646, 648,
    666, 667, 668, 683, 687, 691, 700, 705, 711, 714, 720, 722, 726, 749, 765, 777, 783, 787,
    800, 801, 808, 843, 873, 880, 888, 898, 900, 901, 902, 903, 911, 912, 981, 987, 990, 992,
    993, 995, 999, 1000, 1001, 1002, 1007, 1009, 1010, 1011, 1021, 1022, 1023, 1024, 1026,
    1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041,
    1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056,
    1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071,
    1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086,
    1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100})


def parse_ports(spec):
    p = set()
    spec = spec.replace(" ", "")
    if spec.lower() in ("top", "default"):
        return sorted(TOP_PORTS)
    if spec.lower() in ("all", "full", "1-65535"):
        return list(range(1, 65536))
    if spec.lower() in ("top1000", "1000"):
        return sorted(set(TOP_PORTS) | set(TOP_1000_EXTRA))
    for part in spec.split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            p.update(range(int(a), int(b) + 1))
        else:
            p.add(int(part))
    return sorted(x for x in p if 0 < x < 65536)


def grab_banner(sock, host, port):
    try:
        sock.settimeout(1.6)
        if port in TLS_PORTS:
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with ctx.wrap_socket(sock, server_hostname=host) as ss:
                    c = ss.cipher()
                    ver = ss.version() or "?"
                    return f"tls {ver} {c[0] if c else ''}".strip()
            except Exception:
                return "tls (handshake failed)"
        if port in HTTP_PORTS:
            sock.sendall(f"GET / HTTP/1.1\r\nHost: {host}\r\n"
                         f"User-Agent: {UA}\r\nAccept: */*\r\nConnection: close\r\n\r\n"
                         .encode())
        elif port == 6379:
            sock.sendall(b"PING\r\n")
        elif port == 11211:
            sock.sendall(b"version\r\n")
        elif port in (25, 587):
            sock.sendall(b"EHLO whitetiger.local\r\n")
        data = b""
        while len(data) < 4096:
            try:
                chunk = sock.recv(2048)
            except Exception:
                break
            if not chunk:
                break
            data += chunk
            if port not in HTTP_PORTS:
                break
        txt = data.decode("utf-8", "replace").replace("\r", "")
        m = re.search(r"(?im)^server:\s*(.+)$", txt)
        srv = m.group(1).strip()[:90] if m else ""
        m = re.search(r"(?im)^x-powered-by:\s*(.+)$", txt)
        pw = m.group(1).strip()[:50] if m else ""
        m = re.search(r"<title>(.*?)</title>", txt, re.S | re.I)
        title = strip_tags(m.group(1))[:60] if m else ""
        if port in HTTP_PORTS:
            bits = [b for b in (srv, pw, title) if b]
            return "http · " + " | ".join(bits) if bits else "http"
        return txt.strip().split("\n")[0][:110]
    except Exception:
        return ""


def probe_port(host, port, timeout=1.0, banner=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        if s.connect_ex((host, port)) != 0:
            return False, ""
        return True, (grab_banner(s, host, port) if banner else "")
    except Exception:
        return False, ""
    finally:
        try:
            s.close()
        except Exception:
            pass


def udp_probe(host, port, payload, timeout=1.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(payload, (host, port))
        data, _ = s.recvfrom(4096)
        return data
    except Exception:
        return None
    finally:
        try:
            s.close()
        except Exception:
            pass


CAs = ("Let's Encrypt", "ISRG", "DigiCert", "Sectigo", "Comodo", "GlobalSign", "GoDaddy",
       "Google Trust", "Amazon", "Cloudflare", "ZeroSSL", "Microsoft", "Apple", "Entrust",
       "GeoTrust", "RapidSSL", "Thawte", "Certum", "Buypass", "Actalis", "TrustAsia")


def tls_info(host, port=443):
    out = {}
    try:
        pem = ssl.get_server_certificate((host, port), timeout=7)
        der = base64.b64decode("".join(pem.splitlines()[1:-1]))
    except Exception:
        return out
    names = set()
    for f in re.findall(rb"[a-z0-9*][a-z0-9*.\-]{2,60}\.[a-z]{2,12}", der):
        s = f.decode("latin-1")
        if not s.startswith("."):
            names.add(s)
    out["sans"] = sorted(names)[:14]
    dates = re.findall(rb"(\d{12}Z)", der)
    if dates:
        out["dates"] = [d.decode() for d in dates[:3]]
    txt = der.decode("latin-1")
    for ca in CAs:
        if ca in txt:
            out.setdefault("issuer", ca)
    if len(der) > 8:
        out["serial"] = der[4:12].hex()
    return out


def tls_chain(host, port=443):
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=8) as s:
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                cert = ss.getpeercert()
                return {"version": ss.version(), "cipher": (ss.cipher() or ("?",))[0],
                        "subject": dict(x[0] for x in cert.get("subject", [])),
                        "issuer": dict(x[0] for x in cert.get("issuer", [])),
                        "not_before": cert.get("notBefore"),
                        "not_after": cert.get("notAfter")}
    except Exception:
        return {}


def ping_once(host, timeout_ms=1000):
    if IS_WIN:
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), host]
    elif IS_MAC:
        cmd = ["ping", "-c", "1", "-W", str(timeout_ms), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(max(1, timeout_ms // 1000)), host]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           timeout=timeout_ms / 1000 + 3)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    m = re.search(r"time[=<]\s*([\d.]+)\s*ms", r.stdout.decode("utf-8", "replace"), re.I)
    return float(m.group(1)) if m else 0.0


def parse_range(spec):
    spec = spec.strip()
    if "/" in spec:
        try:
            net = ipaddress.ip_network(spec, strict=False)
            hosts = list(net.hosts())
            return [str(h) for h in (hosts if len(hosts) <= 4096 else hosts[:4096])]
        except Exception:
            return [spec]
    if "-" in spec:
        a, b = [x.strip() for x in spec.split("-", 1)]
        if b.isdigit() and "." in a:
            base = a.rsplit(".", 1)[0]
            return [f"{base}.{i}" for i in range(int(a.rsplit(".", 1)[1]), int(b) + 1)]
        try:
            s, e = int(ipaddress.ip_address(a)), int(ipaddress.ip_address(b))
            return [str(ipaddress.ip_address(i)) for i in range(s, e + 1)][:4096]
        except Exception:
            return [a]
    return [spec]


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def arp_table():
    try:
        out = subprocess.run(["arp", "-a"], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL,
                             timeout=5).stdout.decode("utf-8", "replace")
    except Exception:
        return []
    found = []
    for line in out.splitlines():
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)\D+?"
                      r"([0-9a-fA-F]{1,2}(?:[:\-][0-9a-fA-F]{1,2}){5})", line)
        if m:
            found.append((m.group(1), m.group(2)))
    return found


def entropy(data):
    if not data:
        return 0.0
    counts = [0] * 256
    for b in (data if isinstance(data, (bytes, bytearray)) else data.encode()):
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def qs_params(url):
    q = urllib.parse.urlparse(url).query
    return [(k, v) for k, v in urllib.parse.parse_qsl(q, keep_blank_values=True)]


def set_param(url, key, val):
    p = urllib.parse.urlparse(url)
    pairs = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    out = [(k, val if k == key else v) for k, v in pairs]
    if not any(k == key for k, _ in pairs):
        out.append((key, val))
    return urllib.parse.urlunparse(
        (p.scheme, p.netloc, p.path, p.params, urllib.parse.urlencode(out), p.fragment))


def similarity(a, b):
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a[:4000], b[:4000]).quick_ratio()


# =========================================================================== #
#  LIVE RENDERER
# =========================================================================== #
START_TS = time.time()
_LOCK = threading.RLock()
AMBIENT = {"on": False, "anchor": 0, "w": 0, "h": 0}
LIVE = {"lat": deque(maxlen=64), "net": None, "msg": "idle",
        "jobs": 0, "hits": 0, "runs": 0, "frames": 0, "ms": 0.0, "radar": 0}

_GRAD_CACHE = {}
_ESC_CACHE = {}
_HOST_CACHE = {"host": "", "ip": "", "t": 0.0, "tag": ""}

TIPS = [
    "tip: type a module number, or /word to filter",
    "tip: [S] settings · [T] theme · [R] random · [H] help",
    "tip: --rain turns on the matrix backdrop",
    "tip: --calm freezes the glow, --no-anim kills the intro",
    "tip: --no-color pipes cleanly into files",
    "tip: --selftest verifies every helper resolves",
    "tip: drop .py files with a MODULES list in ./plugins",
    "tip: the equaliser is driven by live latency",
    "tip: 100 modules · keyless sources · zero dependencies",
    "tip: PHONE ORACLE gives timezone + carrier",
    "tip: MAIL XRAY lists the sites an address is registered on",
    "tip: module 96 turns every report into one html page",
]


def anim_t():
    return FXS.t()


def host_info():
    now = time.time()
    tag = f"{socket.gethostname()}|{local_ip()}"
    if tag != _HOST_CACHE["tag"] or now - _HOST_CACHE["t"] > 30:
        _HOST_CACHE["host"] = socket.gethostname()[:20]
        _HOST_CACHE["ip"] = local_ip()
        _HOST_CACHE["tag"] = tag
        _HOST_CACHE["t"] = now
    return _HOST_CACHE["host"], _HOST_CACHE["ip"]


def block_w():
    return max(20, tw() - 2)


def qcol(c):
    return (c[0] & 0xF8, c[1] & 0xF8, c[2] & 0xF8)


def esc(c):
    if c is None:
        return ""
    e = _ESC_CACHE.get(c)
    if e is None:
        e = fg(c)
        _ESC_CACHE[c] = e
    return e


def paint(chars, cols):
    if not chars:
        return RESET
    out, last, run = [], None, []
    for ch, col in zip(chars, cols):
        col = qcol(col)
        if col != last:
            if run:
                out.append(esc(last))
                out.append("".join(run))
                run = []
            last = col
        run.append(ch)
    if run:
        out.append(esc(last))
        out.append("".join(run))
    out.append(RESET)
    return "".join(out)


def make_gradient(w, stops):
    def f(x):
        if w <= 1:
            return stops[-1][1]
        t = x / (w - 1)
        for i in range(len(stops) - 1):
            a, ca = stops[i]
            b, cb = stops[i + 1]
            if a <= t <= b:
                k = 0.0 if b == a else (t - a) / (b - a)
                return lerp(ca, cb, k)
        return stops[-1][1]
    return f


def grad_for(th, w):
    key = (th["label"], w)
    g = _GRAD_CACHE.get(key)
    if g is None:
        g = make_gradient(w, th["grad"])
        _GRAD_CACHE[key] = g
    return g


def emit(s):
    try:
        os.write(1, s.encode("utf-8", "replace"))
    except Exception:
        try:
            sys.stdout.write(s)
            sys.stdout.flush()
        except Exception:
            pass


def metrics_loop():
    targets = [("1.1.1.1", 53), ("8.8.8.8", 53), ("9.9.9.9", 53)]
    while True:
        got = False
        for host, port in targets:
            t0 = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.2)
            try:
                s.connect((host, port))
                ms = (time.time() - t0) * 1000
                with _LOCK:
                    LIVE["lat"].append(ms)
                    LIVE["net"] = True
                got = True
                break
            except Exception:
                pass
            finally:
                try:
                    s.close()
                except Exception:
                    pass
        if not got:
            with _LOCK:
                LIVE["net"] = False
        time.sleep(3.5)


def brand_bar(th, w, t):
    host, ip = host_info()
    clock = time.strftime("%H:%M:%S")
    up = fmt_dur(time.time() - START_TS)
    net = LIVE["net"]
    beat = 0.6 + 0.4 * (1 + math.sin(t * 4.4)) / 2
    if net is True:
        dot, nc = "●", (130, 255, 160)
    elif net is False:
        dot, nc = "●", (255, 120, 120)
    else:
        dot, nc = "○", th["dim"]
    lat = f"{LIVE['lat'][-1]:.0f}ms" if LIVE["lat"] else "--"
    brandcol = scale(th["accent"], 0.55 + 0.45 * beat)
    rec = f"{fg(scale((255, 90, 90), 0.30 + 0.70 * beat))}◉{RESET}"
    line = (f"{rec} {fg(brandcol)}{BOLD}W H I T E T I G E R{RESET} "
            f"{fg(th['dim'])}v{VERSION}{RESET}   {fg(nc)}{dot}{RESET} "
            f"{fg(th['dim'])}{lat} · {up} · {clock} · {host} · {ip}{RESET}")
    return center_line(line, w)


def sparkle_mask(w, h, t, rate=0.010):
    """deterministic twinkling dots over a w x h field"""
    out = set()
    frame = int(t * 9)
    for y in range(h):
        for x in range(w):
            v = (x * 31 + y * 17 + frame * 13) % 997
            if v < int(997 * rate):
                out.add((x, y))
    return out


def banner_rows(th, w, t):
    if banner_mode() == "compact":
        text = "W H I T E T I G E R"
        grad = grad_for(th, len(text))
        shine = (t * 26.0) % (len(text) + 24) - 12
        chars, cols = [], []
        for i, ch in enumerate(text):
            col = grad(int((i + t * 12.0) % len(text)))
            d = abs(i - shine)
            if d < 6:
                col = lerp(col, th["glow"], (1 - d / 6) ** 2 * 0.92)
            chars.append(ch)
            cols.append(col)
        rows = [center_line("  " + paint(chars, cols), w)]
        while len(rows) < len(BANNER):
            rows.append("")
        return rows

    grad = grad_for(th, BANNER_W)
    pulse = 0.72 + 0.28 * (1 + math.sin(t * 1.9)) / 2
    aura = 0.55 + 0.45 * (1 + math.sin(t * 2.6)) / 2
    shine = (t * 34.0) % (BANNER_W + 70) - 35
    scan = (t * 6.5) % (len(BANNER) + 5) - 2.5
    stripe = (t * 46.0) % (BANNER_W + 90) - 45
    sparks = sparkle_mask(BANNER_W, len(BANNER), t)
    burst = FXS.in_burst()
    gz = SETTINGS["glitch"] and (burst or int(t * 0.9) % 11 == 0)
    rows = []
    for ri, raw in enumerate(BANNER):
        chars, cols = [], []
        boost = 1.0
        if abs(ri - scan) < 1.3:
            boost = 1.0 + (1 - abs(ri - scan) / 1.3) * 0.60
        for x in range(BANNER_W):
            ch = raw[x] if x < len(raw) else " "
            col = grad(int((x + t * 15.0 + ri * 3.0) % BANNER_W))
            col = scale(col, pulse * boost * (0.86 + 0.14 * aura))
            if SETTINGS["stripes"]:
                d = abs((x - stripe) - ri * 3)
                if d < 5:
                    col = lerp(col, th["glow"], (1 - d / 5) ** 1.4 * 0.85)
            d = abs(x - shine)
            if d < 15:
                col = lerp(col, th["glow"], (1 - d / 15) ** 2 * 0.95)
            if (x, ri) in sparks and ch != " ":
                col = lerp(col, th["glow"], 0.9)
                if random.random() < 0.35:
                    ch = random.choice("·+*✦")
            if gz and ch != " " and random.random() < 0.02:
                ch = random.choice(GLITCH_CHARS)
                col = th["accent"]
            chars.append(ch)
            cols.append(col)
        rows.append(center_line(paint(chars, cols), w))
    return rows


def equalizer(th, w, t):
    n = max(10, min(w - 8, 72))
    lat = list(LIVE["lat"])[-n:]
    out = []
    for i in range(n):
        if i < len(lat):
            lvl = 0.20 + 0.80 * min(1.0, lat[i] / 105.0)
        else:
            lvl = 0.42 + 0.34 * (1 + math.sin(t * 1.6 + i * 0.42)) / 2
        lvl *= 0.58 + 0.42 * (1 + math.sin(t * 3.1 + i * 0.27)) / 2
        lvl = max(0.0, min(1.0, lvl))
        idx = int(lvl * (len(BLOCKS) - 1))
        col = lerp(th["border"], th["accent"], idx / (len(BLOCKS) - 1))
        out.append(fg(col) + BLOCKS[idx])
    return center_line("".join(out) + RESET, w)


def status_bar(th, w, t):
    lat = LIVE["lat"]
    avg = sum(lat) / len(lat) if lat else 0
    load = min(1.0, avg / 140.0)
    lw = 10
    lf = int(load * lw)
    loadcol = lerp(th["accent"], (255, 110, 110), load)
    loadbar = f"{fg(loadcol)}{'█' * lf}{fg(th['dim'])}{'░' * (lw - lf)}{RESET}"
    radar_txt = f" {fg(th['accent'])}◜◝◞◟{RESET}" if LIVE["radar"] else ""
    bits = [
        f"{fg(th['dim'])}{th['label']}{RESET}",
        f"{fg(th['dim'])}runs{RESET} {fg(th['text'])}{LIVE['runs']}{RESET}",
        f"{fg(th['dim'])}hits{RESET} {fg(th['text'])}{LIVE['hits']}{RESET}",
        f"{fg(th['dim'])}net{RESET} {loadbar}",
        f"{fg(th['dim'])}{LIVE['msg'][:14]}{RESET}",
        f"{fg(th['dim'])}{LIVE['ms']:.0f}ms{RESET}",
    ]
    return center_line(" · ".join(bits) + radar_txt, w)


def ticker(th, w, t):
    msg = TIPS[int(t / 6.0) % len(TIPS)]
    lat = list(LIVE["lat"])[-14:]
    spark = "".join(SPARKS[max(0, min(7, int(min(1.0, v / 120.0) * 8)))] for v in lat)
    line = f"{fg(th['dim'])}{msg}{RESET}  {fg(th['border'])}{spark}{RESET}"
    return center_line(trunc(line, max(20, w - 6)), w)


def rain_rows(th, w, h):
    if FXS.rain is None or FXS.rain.w != w or FXS.rain.h != h:
        FXS.rain = MatrixRain(w, h)
    FXS.rain.step()
    return FXS.rain.render(th)


def live_block(th):
    w = block_w()
    t = anim_t()
    if SETTINGS["rain"] and tw() >= 92:
        rows = rain_rows(th, w - 4, len(BANNER))
        lines = [brand_bar(th, w, t)]
        lines += [center_line(r, w) for r in rows]
        lines.append(equalizer(th, w, t))
        lines.append(status_bar(th, w, t))
        lines.append(ticker(th, w, t))
        while len(lines) < block_h():
            lines.append("")
        return [pad(l, w) for l in lines[:block_h()]]
    lines = [brand_bar(th, w, t)]
    lines += banner_rows(th, w, t)
    lines.append(equalizer(th, w, t))
    lines.append(status_bar(th, w, t))
    lines.append(ticker(th, w, t))
    while len(lines) < block_h():
        lines.append("")
    return [pad(l, w) for l in lines[:block_h()]]


# --------------------------------------------------------------------------- #
#  menu layout (centred)
# --------------------------------------------------------------------------- #
def split_categories(maxh):
    boxes = []
    for title, items in CATEGORIES:
        if not items:
            boxes.append((title, []))
            continue
        parts = max(1, math.ceil(len(items) / maxh))
        size = math.ceil(len(items) / parts)
        for i in range(0, len(items), size):
            chunk = items[i:i + size]
            label = title if i == 0 else f"{title} {i // size + 1}"
            boxes.append((label, chunk))
    return boxes


def menu_width():
    names = [n for _, n, _, _ in ALL_MODULES] or ["module"]
    return max(6 + len(n) for n in names) + 4


def build_box(title, items, w, th, phase, maxh, sweep):
    inner = w - 2

    def body(c, v):
        return (f"{fg(th['border'])}│{RESET} {c}" + " " * max(0, inner - 1 - v) +
                f"{fg(th['border'])}│{RESET}")

    tcol = lerp(th["border"], th["accent"], 0.5 + 0.5 * math.sin(phase))
    dash = max(0, w - 7 - len(title))
    lines = [f"{fg(tcol)}┌─[ {fg(th['key'])}{title}{fg(tcol)} ]" +
             "─" * dash + "┐" + RESET]
    for i, (n, name, _, _) in enumerate(items):
        hot = SETTINGS["sweep"] and (i == sweep % max(1, len(items)))
        ncol = th["glow"] if hot else th["key"]
        tcol2 = th["glow"] if hot else th["text"]
        lines.append(body(f"{fg(ncol)}[{n:03d}]{RESET} {fg(tcol2)}{name}{RESET}",
                          6 + len(name)))
    for _ in range(maxh - len(items)):
        lines.append(body("", 0))
    lines.append(f"{fg(tcol)}└" + "─" * inner + "┘" + RESET)
    return lines


def render_boxes(th, boxes, cols, w, maxh):
    phase = anim_t() * 0.9
    sweep = int(anim_t() * 3.2)
    rendered = [build_box(t, items, w, th, phase, maxh, sweep) for t, items in boxes]
    out = []
    for i in range(0, len(rendered), cols):
        group = rendered[i:i + cols]
        while len(group) < cols:
            group.append([" " * w] * (maxh + 2))
        for y in range(maxh + 2):
            out.append(center_line("  ".join(g[y] for g in group), tw()))
    return out


def render_flat(th, budget):
    names = [n for _, n, _, _ in ALL_MODULES] or ["module"]
    cw = max(6 + len(n) for n in names) + 3
    cols = 1
    for c in range(6, 0, -1):
        if c * cw > tw() - 2:
            continue
        h = sum(1 + math.ceil(len(items) / c) + 1
                for _, items in CATEGORIES if items)
        if h <= budget:
            cols = c
            break
    out = []
    for title, items in CATEGORIES:
        if not items:
            continue
        out.append(center_line(f"{fg(th['key'])}{BOLD}· {title.upper()} ·{RESET}"))
        per = math.ceil(len(items) / cols)
        for i in range(per):
            row = []
            for c in range(cols):
                idx = c * per + i
                if idx < len(items):
                    n, name, _, _ = items[idx]
                    row.append(f"{fg(th['key'])}[{n:03d}]{RESET} "
                               f"{fg(th['text'])}{name:<{cw - 7}}{RESET}")
                else:
                    row.append(" " * (cw - 1))
            out.append(center_line("".join(row)))
        out.append("")
    return out


def build_menu(th, budget):
    if SETTINGS["layout"] == "flat":
        return render_flat(th, budget)
    if SETTINGS["layout"] == "boxes":
        w = menu_width()
        cols = max(1, min(4, (tw() - 2) // (w + 2)))
        maxh = max(3, budget // 2 - 2)
        return render_boxes(th, split_categories(maxh), cols, w, maxh)
    w = menu_width()
    for maxh in range(18, 3, -1):
        boxes = split_categories(maxh)
        for cols in (4, 3, 2, 1):
            if cols * (w + 2) > tw() - 2:
                continue
            rows = math.ceil(len(boxes) / cols)
            if rows * (maxh + 2) <= budget:
                return render_boxes(th, boxes, cols, w, maxh)
    return render_flat(th, budget)


def shell_prompt(th):
    caret = "▊" if (time.time() * 2) % 2 < 1 else "▏"
    line = (f"{fg(th['dim'])}┌─({fg(th['key'])}admin{fg(th['dim'])}@"
            f"{fg(th['key'])}whitetiger{fg(th['dim'])})─[{fg(th['text'])}{ROOT}"
            f"{fg(th['dim'])}]\n{fg(th['accent'])}{BOLD}└λ{RESET}{fg(th['key'])}{caret}{RESET} ")
    return line


def hint_bar(th):
    keys = [("H", "help"), ("S", "set"), ("T", "theme"), ("R", "rand"),
            ("B", "batch"), ("Q", "quit")]
    return "   ".join(f"{fg(th['key'])}[{k}]{RESET}{fg(th['dim'])}{l}{RESET}"
                      for k, l in keys)


def screen_lines(th):
    head = live_block(th) + ["", center_line(hint_bar(th)), ""]
    prompt = shell_prompt(th)
    tail = ["", prompt]
    budget = max(4, th_() - len(head) - len(tail))
    body = build_menu(th, budget)
    if len(body) > budget:
        body = body[:budget]
    return head + body + tail


def draw_screen(th, animate=True):
    clear()
    lines = screen_lines(th)
    last = len(lines) - 1
    for i, l in enumerate(lines):
        if i == last:
            sys.stdout.write(l)
        else:
            sys.stdout.write(l + "\n")
            if animate and SETTINGS["anim"] and i < block_h() + 3:
                time.sleep(0.004)
    sys.stdout.flush()
    AMBIENT["anchor"] = last
    AMBIENT["w"] = tw()
    AMBIENT["h"] = th_()


def redraw_live():
    if not TTY or not AMBIENT["on"] or AMBIENT["anchor"] <= 0:
        return
    if tw() != AMBIENT["w"] or th_() != AMBIENT["h"]:
        redraw_full()
        return
    anchor = AMBIENT["anchor"]
    if anchor >= th_():
        redraw_full()
        return
    t0 = time.time()
    block = live_block(TH)
    if len(block) > anchor:
        return
    buf = [SAVE, f"{ESC}{anchor}A{ESC}1G"]
    for line in block:
        buf.append(line)
        buf.append("\n")
    down = anchor - len(block)
    if down > 0:
        buf.append(f"{ESC}{down}B")
    elif down < 0:
        buf.append(f"{ESC}{-down}A")
    buf.append(REST)
    emit("".join(buf))
    LIVE["ms"] = (time.time() - t0) * 1000
    LIVE["frames"] += 1


def redraw_full():
    AMBIENT["w"] = tw()
    AMBIENT["h"] = th_()
    lines = screen_lines(TH)
    clear()
    for i, l in enumerate(lines):
        sys.stdout.write(l + ("\n" if i < len(lines) - 1 else ""))
    sys.stdout.flush()
    AMBIENT["anchor"] = len(lines) - 1
    LIVE["frames"] += 1


def ambient_loop():
    while True:
        budget = 1.0 / max(5, SETTINGS["fps"])
        t0 = time.time()
        try:
            if AMBIENT["on"] and SETTINGS["glow"] and TTY:
                with _LOCK:
                    if AMBIENT["on"]:
                        redraw_live()
        except Exception:
            pass
        time.sleep(max(0.002, budget - (time.time() - t0)))


def intro_banner(th):
    if not SETTINGS["anim"] or not TTY or tw() < BANNER_W + 6:
        return
    h = len(BANNER)
    print("\n" * h, end="")
    emit(f"{ESC}{h}A")
    grad = grad_for(th, BANNER_W)
    pad = max(0, (tw() - BANNER_W) // 2)
    for p in range(0, BANNER_W + 4):
        rows = []
        for line in BANNER:
            chars, cols = [], []
            for x in range(BANNER_W):
                ch = line[x] if x < len(line) else " "
                if x >= p:
                    ch = " "
                col = grad(x)
                d = x - (p - 1)
                if 0 <= d < 4:
                    col = lerp(col, th["glow"], 0.95 - d * 0.22)
                chars.append(ch)
                cols.append(col)
            rows.append(" " * pad + paint(chars, cols))
        emit("\n".join(rows) + "\n")
        emit(f"{ESC}{h}A")
        time.sleep(0.009)
    emit(f"{ESC}{h}B")


def slide(th, seconds=0.26):
    """fast horizontal wipe used when a module launches"""
    if not SETTINGS["anim"] or not TTY:
        return
    w, h = tw(), min(th_() - 1, 20)
    steps = 7
    for s in range(steps):
        buf = [f"{ESC}1;1H"]
        edge = int((w + 10) * (s + 1) / steps)
        for y in range(h):
            col = lerp(th["accent"], th["glow"], (s + 1) / steps)
            buf.append(f"{fg(col)}{'▚' * min(w, edge)}{RESET}")
            if y < h - 1:
                buf.append("\n")
        emit("".join(buf))
        time.sleep(seconds / steps)


def type_text(text, color, delay=0.016):
    for ch in text:
        sys.stdout.write(fg(color) + ch + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def boot_sequence(th):
    steps = ["initialising whitetiger core", "loading module registry (100)",
             "probing network stack", "starting fx engine", "warming colour pipeline",
             "arming live metrics", "mounting plugin loader"]
    for msg in steps:
        sys.stdout.write(f"  {fg(th['accent'])}[ ok ]{RESET} {fg(th['text'])}{msg}{RESET}")
        for _ in range(3):
            sys.stdout.write(f"{fg(th['dim'])}.{RESET}")
            sys.stdout.flush()
            time.sleep(0.02)
        print()
        time.sleep(0.02)
    time.sleep(0.06)


# =========================================================================== #
#  PENTESTING
# =========================================================================== #

def mod_ghost_sweep():
    host = ask("host / ip", "127.0.0.1")
    spec = ask("ports (top / top1000 / list)", "top")
    ip = resolve(host) or host
    inf(f"target {host} -> {ip}")
    try:
        ports = parse_ports(spec)
    except Exception:
        bad("bad port spec")
        return
    rep = {"host": host, "ip": ip, "open": [], "started": time.time()}
    t0 = time.time()
    LIVE["radar"] = 1
    pg = Progress(len(ports), "scanning")
    with ThreadPoolExecutor(max_workers=120) as ex:
        futs = {ex.submit(probe_port, ip, p, 1.3): p for p in ports}
        for fut in as_completed(futs):
            pg.update()
            p = futs[fut]
            try:
                is_open, banner = fut.result()
            except Exception:
                continue
            if not is_open:
                continue
            e = {"port": p, "service": SERVICES.get(p, "unknown"), "banner": banner}
            pg.line()
            ok(f"{p:<6} {e['service']:<14} {banner}")
            LIVE["hits"] += 1
            FXS.ping(0.15)
            if p in TLS_PORTS:
                ti = tls_info(ip, p)
                e["tls"] = ti
                if ti.get("issuer"):
                    kv("tls issuer", ti["issuer"])
                if ti.get("sans"):
                    kv("tls sans", ", ".join(ti["sans"][:8]))
            elif p in HTTP_PORTS:
                st, body, hdrs = http_get(f"http://{ip}:{p}/", timeout=7)
                e["http"] = {"status": st, "server": hdrs.get("server", ""),
                             "powered_by": hdrs.get("x-powered-by", "")}
                m = re.search(rb"<title>(.*?)</title>", body, re.S | re.I)
                if m:
                    e["http"]["title"] = strip_tags(
                        m.group(1).decode("utf-8", "replace"))[:80]
                for k in ("status", "server", "powered_by", "title"):
                    if e["http"].get(k):
                        kv(k, e["http"][k])
            rep["open"].append(e)
    pg.done()
    LIVE["radar"] = 0
    for scheme in ("https", "http"):
        st, body, _ = http_get(f"{scheme}://{host}/robots.txt", timeout=6)
        if st == 200 and body:
            rep["robots"] = body.decode("utf-8", "replace")[:2000]
            inf(f"robots.txt found ({len(body)} bytes)")
            break
    print()
    rule()
    risk = sum(1 for e in rep["open"] if e["service"] in
               ("telnet", "ftp", "smb", "rdp", "mongodb", "redis", "memcached", "mysql"))
    inf(f"{len(rep['open'])} open · {risk} legacy/risky · {time.time() - t0:.2f}s")
    rep["elapsed"] = time.time() - t0
    save_json(f"wt_scan_{safe_name(host)}.json", rep)


BANNER_SIGS = [
    (r"vsftpd 2\.3\.4", "critical", "vsftpd 2.3.4 backdoor (CVE-2011-2523)"),
    (r"ProFTPD 1\.3\.3c", "high", "ProFTPD 1.3.3c backdoor (CVE-2010-4221)"),
    (r"UnrealIRCd.*3\.2\.8\.1", "high", "UnrealIRCd 3.2.8.1 trojaned"),
    (r"OpenSSH[_ ]([0-7])\.", "medium", "OpenSSH < 8.x (CVE-2018-15473)"),
    (r"OpenSSH[_ ]8\.[0-7]", "low", "OpenSSH 8.x outdated"),
    (r"Apache/2\.2", "medium", "Apache 2.2.x EOL"),
    (r"Apache/2\.4\.(?:[0-3]\d|4[0-9])\b", "low", "Apache 2.4.x outdated"),
    (r"nginx/1\.(?:[0-9]|1[0-7])\.", "low", "nginx < 1.18"),
    (r"Microsoft-IIS/6", "high", "IIS 6.0 EOL"),
    (r"Microsoft-IIS/7", "medium", "IIS 7.x outdated"),
    (r"Microsoft-IIS/(8|10\.0)", "low", "IIS legacy branch"),
    (r"OpenSSL/1\.0", "medium", "OpenSSL 1.0.x EOL"),
    (r"OpenSSL/1\.1\.1[a-z]?\b", "low", "OpenSSL 1.1.1 branch"),
    (r"PHP/5", "medium", "PHP 5 EOL"),
    (r"PHP/7\.[0-3]", "low", "PHP 7.x outdated"),
    (r"MiniServ", "low", "Webmin (CVE-2019-15107)"),
    (r"Exim 4\.(8[0-9]|9[0-1])", "medium", "Exim outdated (CVE-2019-10149)"),
    (r"MySQL.*5\.[0-6]", "low", "MySQL 5.x EOL"),
    (r"MariaDB", "info", "MariaDB exposed"),
    (r"lighttpd/1\.[0-4]", "low", "lighttpd outdated"),
    (r"Jetty\((\d)\.", "low", "Jetty exposed"),
    (r"Tomcat/([1-8])\.", "low", "Tomcat outdated"),
    (r"CUPS/(1\.)", "low", "CUPS 1.x (CVE-2024-47176 chain)"),
    (r"VNC.*3\.([3-7])", "low", "VNC legacy auth"),
    (r"Pure-FTPd", "info", "Pure-FTPd exposed"),
    (r"Postfix", "info", "Postfix exposed"),
    (r"Dovecot", "info", "Dovecot exposed"),
    (r"Redis", "medium", "Redis reachable"),
]

SEC_HEADERS = [("strict-transport-security", "HSTS"),
               ("content-security-policy", "CSP"),
               ("x-frame-options", "X-Frame-Options"),
               ("x-content-type-options", "X-Content-Type-Options"),
               ("referrer-policy", "Referrer-Policy"),
               ("permissions-policy", "Permissions-Policy"),
               ("cross-origin-opener-policy", "COOP"),
               ("cross-origin-resource-policy", "CORP"),
               ("cross-origin-embedder-policy", "COEP")]


def _sock_line(f):
    return f.readline().decode("utf-8", "replace").rstrip()


def _cmd(sock, f, line):
    if line:
        sock.sendall((line + "\r\n").encode())
    out = _sock_line(f)
    while len(out) > 3 and out[3] == "-":
        out = _sock_line(f)
    return out


def check_service(host, port, banner):
    f_ = [(sev, msg) for pat, sev, msg in BANNER_SIGS
          if banner and re.search(pat, banner, re.I)]
    if port == 21:
        try:
            s = socket.create_connection((host, 21), timeout=6)
            fh = s.makefile("rb")
            _sock_line(fh)
            _cmd(s, fh, "USER anonymous")
            if _cmd(s, fh, "PASS anon@wt.local").startswith("230"):
                f_.append(("medium", "anonymous FTP allowed"))
            s.close()
        except Exception:
            pass
    if port == 6379:
        try:
            s = socket.create_connection((host, 6379), timeout=5)
            s.sendall(b"PING\r\n")
            if b"PONG" in s.recv(64):
                f_.append(("high", "Redis no-auth"))
            s.close()
        except Exception:
            pass
    if port == 11211:
        try:
            s = socket.create_connection((host, 11211), timeout=5)
            s.sendall(b"stats\r\n")
            if b"STAT" in s.recv(512):
                f_.append(("medium", "memcached exposed"))
            s.close()
        except Exception:
            pass
    if port == 9200:
        st, body, _ = http_get(f"http://{host}:9200/", timeout=6)
        if st == 200 and b"cluster_name" in body:
            f_.append(("medium", "Elasticsearch no-auth"))
    if port == 2375:
        if http_get(f"http://{host}:2375/version", timeout=6)[0] == 200:
            f_.append(("high", "Docker API unauthenticated"))
    if port == 5900:
        try:
            s = socket.create_connection((host, 5900), timeout=5)
            if b"RFB" in s.recv(32):
                f_.append(("info", "VNC reachable"))
            s.close()
        except Exception:
            pass
    if port == 27017:
        try:
            doc = b"\x13\x00\x00\x00\x10isMaster\x00\x01\x00\x00\x00\x00"
            body = b"\x00\x00\x00\x00admin.$cmd\x00\x00\x00\x00\x00\xff\xff\xff\xff" + doc
            s = socket.create_connection((host, 27017), timeout=5)
            s.sendall(struct.pack("<iiii", 16 + len(body), 1, 0, 2004) + body)
            if s.recv(512):
                f_.append(("medium", "MongoDB responding"))
            s.close()
        except Exception:
            pass
    if port == 23:
        f_.append(("medium", "Telnet plaintext"))
    if port == 3389:
        try:
            s = socket.create_connection((host, 3389), timeout=5)
            s.sendall(b"\x03\x00\x00\x13\x0e\xe0\x00\x00\x00\x00\x00\x01\x00\x08\x00"
                      b"\x03\x00\x00\x00")
            if s.recv(64):
                f_.append(("info", "RDP handshake ok — check BlueKeep/CVE-2019-0708"))
            s.close()
        except Exception:
            pass
    if port == 445:
        try:
            s = socket.create_connection((host, 445), timeout=5)
            s.sendall(b"\x00\x00\x00\x85\xffSMB\x72\x00\x00\x00\x00\x18\x53\xc8\x00\x00"
                      b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00"
                      b"\x00\x62\x00\x02NT LM 0.12\x00\x02SMB 2.002\x00\x02SMB 2.1\x00")
            d = s.recv(256)
            if b"SMB" in d:
                f_.append(("info", "SMB negotiated — check MS17-010 / signing"))
            s.close()
        except Exception:
            pass
    if port == 6443:
        f_.append(("info", "Kubernetes API — check anonymous auth"))
    if port == 10250:
        st, body, _ = http_get(f"https://{host}:10250/pods", timeout=6)
        if st == 200:
            f_.append(("high", "kubelet /pods readable"))
    if port == 2049:
        f_.append(("info", "NFS — try showmount -e"))
    if port in HTTP_PORTS:
        st, body, hdrs = http_get(f"http://{host}:{port}/", timeout=7)
        if hdrs.get("server"):
            f_.append(("info", f"server: {hdrs['server']}"))
        if b"Index of /" in body:
            f_.append(("low", "directory listing on"))
        ck = hdrs.get("set-cookie", "")
        if ck and "secure" not in ck.lower():
            f_.append(("low", "cookie without Secure flag"))
        if ck and "httponly" not in ck.lower():
            f_.append(("low", "cookie without HttpOnly flag"))
    return f_


def mod_vuln_lens():
    host = ask("host / ip", "127.0.0.1")
    spec = ask("ports", "21,22,23,80,443,3306,3389,445,5432,5900,6379,11211,27017,"
                        "9200,2375,6443,10250,2049")
    ip = resolve(host) or host
    try:
        ports = parse_ports(spec)
    except Exception:
        bad("bad port spec")
        return
    total, score = 0, 0
    weights = {"critical": 10, "high": 6, "medium": 3, "low": 1, "info": 0}
    LIVE["radar"] = 1
    for p in ports:
        is_open, banner = probe_port(ip, p, 1.3)
        if not is_open:
            continue
        print()
        inf(f"{p}/{SERVICES.get(p, 'unknown')}" +
            (f"  {fg(TH['dim'])}{banner}{RESET}" if banner else ""))
        for sev, msg in check_service(ip, p, banner):
            total += 1
            score += weights.get(sev, 0)
            LIVE["hits"] += 1
            FXS.ping(0.2)
            print(f"    {sev_tag(sev)} {fg(TH['text'])}{msg}{RESET}")
    LIVE["radar"] = 0
    print()
    rule("SECURITY HEADERS (https)")
    st, body, hdrs = http_get(f"https://{host}/", timeout=10)
    if st:
        missing = []
        for h, label in SEC_HEADERS:
            if hdrs.get(h):
                ok(label)
            else:
                missing.append(label)
        if missing:
            wrn("missing: " + ", ".join(missing))
        if hdrs.get("server"):
            kv("server", hdrs["server"])
    print()
    rule()
    grade = ("A" if score <= 3 else "B" if score <= 8 else "C" if score <= 16
             else "D" if score <= 28 else "F")
    inf(f"{total} finding(s) · risk score {score} · grade {grade}")
    save_json(f"wt_vuln_{safe_name(host)}.json",
              {"host": host, "findings": total, "score": score, "grade": grade})


def mod_port_storm():
    host = ask("host / ip", "127.0.0.1")
    spec = ask("ports (top / top1000 / 1-1024)", "top1000")
    workers = int(ask("threads", "400") or 400)
    timeout = float(ask("timeout", "1.0") or 1.0)
    ip = resolve(host) or host
    try:
        ports = parse_ports(spec)
    except Exception:
        bad("bad port spec")
        return
    inf(f"scanning {len(ports)} ports on {ip}")
    t0, n = time.time(), 0
    LIVE["radar"] = 1
    pg = Progress(len(ports), "probing")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(probe_port, ip, p, timeout): p for p in ports}
        for fut in as_completed(futs):
            pg.update()
            if fut.result()[0]:
                n += 1
                LIVE["hits"] += 1
                p = futs[fut]
                pg.line()
                ok(f"{p:<6} {SERVICES.get(p, '')}")
    pg.done()
    LIVE["radar"] = 0
    inf(f"{n} open · {time.time() - t0:.2f}s")


def mod_banner_xray():
    host = ask("host / ip", "127.0.0.1")
    ip = resolve(host) or host
    kv("target", f"{host} ({ip})")
    for p in TOP_PORTS:
        is_open, banner = probe_port(ip, p, 1.0)
        if not is_open:
            continue
        print()
        rule(f"{p}/{SERVICES.get(p, 'unknown')}")
        if banner:
            kv("banner", banner)
        if p in TLS_PORTS:
            ti = tls_info(ip, p)
            for k, v in ti.items():
                kv("tls " + k, ", ".join(v) if isinstance(v, list) else v)
            ch = tls_chain(ip, p)
            for k in ("version", "cipher", "not_after"):
                if ch.get(k):
                    kv("handshake " + k, ch[k])
        if p in HTTP_PORTS:
            st, body, hdrs = http_get(f"http://{ip}:{p}/", timeout=8)
            kv("http status", st)
            for h in ("server", "x-powered-by", "content-type", "via", "set-cookie",
                      "x-generator", "x-aspnet-version", "x-drupal-cache"):
                if hdrs.get(h):
                    kv(h, hdrs[h][:120])
            m = re.search(rb"<title>(.*?)</title>", body, re.S | re.I)
            if m:
                kv("title", strip_tags(m.group(1).decode("utf-8", "replace"))[:80])
            st2, _, hdrs2 = http_get(f"http://{ip}:{p}/", timeout=8, method="OPTIONS")
            if hdrs2.get("allow"):
                kv("allowed methods", hdrs2["allow"])
        if p == 22 and banner:
            m = re.search(r"SSH-[\d.]+-(\S+)", banner)
            if m:
                kv("ssh software", m.group(1))
        if p == 3306 and banner:
            m = re.search(r"([\d]+\.[\d]+\.[\d]+[\w.\-]*)", banner)
            if m:
                kv("mysql version", m.group(1))


def mod_echo_pulse():
    hosts = parse_range(ask("ip / range", "127.0.0.1"))
    tmo = int(ask("timeout ms", "1000") or 1000)
    inf(f"pinging {len(hosts)} host(s)")
    alive, times = 0, []
    pg = Progress(len(hosts), "pinging")
    with ThreadPoolExecutor(max_workers=48) as ex:
        futs = {ex.submit(ping_once, h, tmo): h for h in hosts}
        for fut in as_completed(futs):
            pg.update()
            h = futs[fut]
            ms = fut.result()
            if ms is not None:
                alive += 1
                times.append(ms)
                pg.line()
                ok(f"{h:<16} {ms:>7.1f} ms  {reverse_dns(h) or ''}")
    pg.done()
    if times:
        kv("min / avg / max",
           f"{min(times):.1f} / {sum(times) / len(times):.1f} / {max(times):.1f} ms")
        kv("jitter (stdev)", f"{statistics.pstdev(times):.1f} ms" if len(times) > 1 else "-")
    inf(f"{alive}/{len(hosts)} responded")


def mod_net_hound():
    spec = ask("subnet", local_ip().rsplit(".", 1)[0] + ".0/24")
    hosts = parse_range(spec)
    inf(f"probing {len(hosts)} addresses")
    live = {}
    for ip, mac in arp_table():
        if ip in hosts:
            live.setdefault(ip, {"mac": mac, "how": []})
            live[ip]["how"].append("arp")

    def probe(ip):
        if ping_once(ip, 700) is not None:
            return ip, "icmp"
        for p in (80, 443, 22, 445, 3389, 8080):
            if probe_port(ip, p, 0.6, banner=False)[0]:
                return ip, f"tcp/{p}"
        return None

    pg = Progress(len(hosts), "sweeping")
    with ThreadPoolExecutor(max_workers=96) as ex:
        for r in ex.map(probe, hosts):
            pg.update()
            if r:
                live.setdefault(r[0], {"mac": "", "how": []})
                live[r[0]]["how"].append(r[1])
    pg.done()
    for ip in sorted(live, key=lambda x: tuple(int(o) for o in x.split("."))):
        ok(f"{ip:<16} {(reverse_dns(ip) or '-'):<30} {(live[ip]['mac'] or '-'):<18} "
           f"{','.join(sorted(set(live[ip]['how'])))}")
    print()
    inf(f"{len(live)} live host(s)")


COMMON_PATHS = [
    "robots.txt", "sitemap.xml", "sitemap_index.xml", "security.txt",
    ".well-known/security.txt", "favicon.ico", "humans.txt", "crossdomain.xml", "ads.txt",
    "manifest.json", "admin", "admin/", "administrator", "login", "signin", "register",
    "dashboard", "api", "api/v1", "api/v2", "api/docs", "api/swagger.json", "swagger.json",
    "swagger-ui.html", "openapi.json", "graphql", "graphiql", "api/graphql", "rest", "rpc",
    ".git/HEAD", ".git/config", ".svn/entries", ".hg/", ".env", ".env.local",
    ".env.production", ".env.backup", ".htaccess", ".htpasswd", "web.config", "config.php",
    "configuration.php", "backup", "backups", "backup.zip", "backup.tar.gz", "db.sql",
    "dump.sql", "site.zip", "uploads", "upload", "files", "media", "static", "assets",
    "images", "img", "css", "js", "phpinfo.php", "info.php", "test", "test.php", "dev",
    "staging", "beta", "wp-admin", "wp-login.php", "wp-json/wp/v2/users", "wp-content",
    "xmlrpc.php", "server-status", "server-info", "status", "health", "healthz", "metrics",
    "actuator", "actuator/health", "actuator/env", "actuator/beans", "debug", "console",
    "jmx-console", "manager/html", "web-console", "cpanel", "plesk", "phpmyadmin", "pma",
    "adminer.php", "dbadmin", "docker-compose.yml", "Dockerfile", "package.json",
    "composer.json", "composer.lock", "yarn.lock", "Gemfile", "requirements.txt",
    "readme.md", "README.md", "CHANGELOG.md", "LICENSE", "VERSION", "index.php",
    "index.html", "home", "main", "portal", "cgi-bin/", "scripts/", "includes/", "lib/",
    "src/", "vendor/", "node_modules/", "log", "logs", "error.log", "access.log",
    "debug.log", "application.log", "old", "new", "tmp", "temp", "cache", "private",
    "public", "internal", "docs/", "doc/", "wiki/", "help/", "support/", "faq",
    "about", "contact", "privacy", "terms", "careers", "jobs", "team", "news", "press",
    "feed", "rss", "atom.xml", "feed.xml", "rss.xml", "search", "find", "query",
    "v1/", "v2/", "v3/", "api/v3", "api/v4", "api/internal", "api/private", "api/admin",
    "api/user", "api/users", "api/login", "api/token", "api/health", "api/status",
    "api/version", "api/config", "api/keys", "api/metrics", "api/debug",
    "graphql/console", "graphql/schema", "graphql/playground", "__graphql",
    "storage/", "data/", "db/", "sql/", "backup.sql", "db_backup.sql", "database.sql",
    "app.db", "data.db", "db.sqlite3", "sqlite.db", "dump.sql.gz", "export.sql",
    "export.csv", "users.csv", "contacts.csv", "report.pdf", "invoice.pdf",
    "id_rsa", "id_rsa.pub", "known_hosts", "authorized_keys", ".ssh/", ".aws/credentials",
    ".npmrc", ".pypirc", ".netrc", ".bash_history", ".zsh_history", ".profile", ".bashrc",
    "Makefile", "makefile", "Gruntfile.js", "gulpfile.js", "webpack.config.js",
    "tsconfig.json", "babel.config.js", ".babelrc", ".eslintrc", ".prettierrc",
    "phpunit.xml", "jest.config.js", "pytest.ini", "setup.py", "pyproject.toml",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.xml",
    "terraform.tfstate", "serverless.yml", "netlify.toml", "vercel.json", "now.json",
    "Procfile", "app.yaml", "firebase.json", "ansible.cfg", "inventory.ini",
    "admin/login", "admin/index.php", "admin/config.php", "user/login", "user/register",
    "account/login", "accounts/login", "auth/login", "oauth/token", "oauth/authorize",
    "sso/login", "saml/metadata", "certs/", "cert.pem", "key.pem", "chain.pem",
    "fullchain.pem", "privkey.pem", "server.crt", "server.key", "ca.crt",
    "ping", "ping.php", "version", "version.json", "version.txt", "build.txt",
    "changelog", "release-notes", "upgrade", "install", "setup", "setup.php",
    "install.php", "installer", "wizard", "migrate", "seed", "cron", "cron.php",
    "task", "tasks", "queue", "worker", "jobs", "schedule", "scheduler",
    "webhook", "webhooks", "callback", "notify", "notification", "notifications",
    "upload.php", "uploads/", "download", "downloads/", "export", "import",
    "report", "reports", "stats", "statistics", "analytics", "charts", "graph",
    "monitor", "monitoring", "healthcheck", "health-check", "readiness", "liveness",
    "debug/pprof", "debug/vars", "_cat/indices", "_cluster/health", "_nodes",
    "api/v1/status", "api/v1/health", "api/v1/version", "api/v1/config",
]

FUZZ_EXTS = ["", ".php", ".html", ".htm", ".txt", ".json", ".xml", ".bak", ".old",
             ".zip", ".tar.gz", ".sql", ".js", ".css", ".env", ".yml", ".yaml", ".log",
             ".conf", ".config", ".ini", ".swp", ".save", ".orig", ".tmp"]


def mod_path_ripper():
    base = ask("base url", "https://example.com")
    if "://" not in base:
        base = "https://" + base
    base = base.rstrip("/")
    words = ask("wordlist ('default' / comma list / file path)", "default")
    exts = ask("extensions ('none' / comma list)", "")
    threads = int(ask("threads", "32") or 32)
    if os.path.isfile(words):
        try:
            with open(words, "r", encoding="utf-8", errors="replace") as f:
                paths = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except Exception as e:
            bad(f"read failed: {e}")
            return
    elif words.strip().lower() in ("default", ""):
        paths = list(COMMON_PATHS)
    else:
        paths = [w.strip() for w in words.split(",") if w.strip()]
    if exts.strip():
        ex = [e.strip() if e.strip().startswith(".") else "." + e.strip()
              for e in exts.split(",") if e.strip()]
        paths = dedupe([p + e for p in paths for e in ex if p])
    inf(f"fuzzing {len(paths)} paths on {base}")
    found = []

    def probe(p):
        st, body, hdrs = http_get(f"{base}/{p}", timeout=8, retries=0)
        if st is None:
            return None
        return p, st, len(body), hdrs.get("location", "")

    pg = Progress(len(paths), "fuzzing")
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for r in ex.map(probe, paths):
            pg.update()
            if not r:
                continue
            p, st, ln, loc = r
            if st in (200, 201, 204, 301, 302, 307, 308, 401, 403, 405, 500):
                sev = "high" if st == 200 and any(
                    k in p for k in (".env", ".git", "backup", "sql", "config", ".ssh",
                                     "id_rsa", "credentials", ".aws")) else \
                    "medium" if st in (200, 401, 403) else "info"
                found.append((p, st, ln, loc, sev))
                if sev != "info":
                    LIVE["hits"] += 1
                    FXS.ping(0.1)
                pg.line()
                print(f"  {sev_tag(sev)} {fg(TH['text'])}{st:<4}{RESET} "
                      f"{fg(TH['key'])}{p:<46}{RESET} {fg(TH['dim'])}{ln} B {loc[:40]}{RESET}")
    pg.done()
    print()
    inf(f"{len(found)} path(s) responded")
    save_json("wt_fuzz.json",
              [{"path": p, "status": s, "len": l, "loc": d, "sev": v}
               for p, s, l, d, v in found])


def mod_http_autopsy():
    url = ask("url", "https://example.com")
    if "://" not in url:
        url = "https://" + url
    host = urllib.parse.urlparse(url).netloc
    inf(f"auditing {host}")
    st, body, hdrs = http_get(url, timeout=15, max_bytes=800000)
    if st is None:
        bad("unreachable")
        return
    print()
    rule("BASELINE")
    kv("status", st)
    kv("server", hdrs.get("server", "-"))
    kv("content-type", hdrs.get("content-type", "-"))
    kv("size", f"{len(body):,} bytes")
    print()
    rule("REDIRECT CHAIN")
    seen, cur, hops = set(), url, 0
    while cur and hops < 8 and cur not in seen:
        seen.add(cur)
        s2, _, h2 = http_get(cur, timeout=10, retries=0)
        loc = h2.get("location", "")
        kv(f"hop {hops}", f"{s2} {cur[:60]}")
        if loc and s2 and 300 <= s2 < 400:
            cur = urllib.parse.urljoin(cur, loc)
            hops += 1
        else:
            break
    if not cur.startswith("https://"):
        wrn("does not terminate on https")
    print()
    rule("ALLOWED METHODS")
    s3, _, h3 = http_get(url, timeout=10, method="OPTIONS")
    kv("allow", h3.get("allow", "-"))
    for m in ("PUT", "DELETE", "TRACE", "PATCH"):
        s4, _, _ = http_get(url, timeout=8, method=m, retries=0)
        if s4 and s4 < 400:
            wrn(f"{m} accepted ({s4})")
    print()
    rule("SECURITY HEADERS")
    missing = [lbl for h, lbl in SEC_HEADERS if not hdrs.get(h)]
    for h, lbl in SEC_HEADERS:
        if hdrs.get(h):
            ok(f"{lbl}: {hdrs[h][:80]}")
    if missing:
        wrn("missing: " + ", ".join(missing))
    print()
    rule("CORS")
    _, _, hc = http_get(url, timeout=10, headers={"Origin": "https://evil.example"})
    acao = hc.get("access-control-allow-origin", "")
    if not acao:
        bad("no CORS headers")
    elif acao == "*":
        wrn("wildcard origin (*)")
    elif "evil.example" in acao:
        kv("reflects origin", acao)
    acc = hc.get("access-control-allow-credentials", "")
    if acao and acc.lower() == "true":
        wrn("credentials allowed" + (" with wildcard -> broad" if acao == "*" else ""))
    _, _, hn = http_get(url, timeout=10, headers={"Origin": "null"})
    if hn.get("access-control-allow-origin", "") == "null":
        wrn("null origin accepted")
    print()
    rule("COOKIES")
    raw = hdrs.get("set-cookie", "")
    if raw:
        for c in re.split(r",\s*(?=[A-Za-z0-9_\-]+=)", raw):
            kv("cookie", c[:110])
            low = c.lower()
            for flag, sev in (("secure", "low"), ("httponly", "low"),
                              ("samesite", "medium")):
                if flag not in low:
                    print(f"    {sev_tag(sev)} missing {flag}")
    else:
        bad("no cookies set")
    print()
    rule("MISC FILES")
    for p, label in (("robots.txt", "robots"), ("sitemap.xml", "sitemap"),
                     (".well-known/security.txt", "security.txt")):
        s5, b5, _ = http_get(f"{url.rstrip('/')}/{p}", timeout=8, retries=0)
        if s5 == 200 and b5:
            hit(f"{label} found ({len(b5)} bytes)")
            if p == "robots.txt":
                for line in b5.decode("utf-8", "replace").splitlines()[:12]:
                    if line.strip():
                        bad("   " + line.strip()[:80])
        else:
            bad(f"{label} absent")
    save_json(f"wt_audit_{safe_name(host)}.json",
              {"url": url, "status": st, "headers": hdrs, "missing_headers": missing})


def mod_tls_teardown():
    host = ask("hostname", "example.com")
    port = int(ask("port", "443") or 443)
    inf(f"tls audit {host}:{port}")
    print()
    rule("CERTIFICATE")
    ti = tls_info(host, port)
    if not ti:
        bad("no handshake")
        return
    for k, v in ti.items():
        kv(k, ", ".join(v) if isinstance(v, list) else v)
    print()
    rule("HANDSHAKE")
    ch = tls_chain(host, port)
    for k, v in ch.items():
        kv(k, str(v)[:110])
    print()
    rule("PROTOCOL SUPPORT")
    versions = []
    if hasattr(ssl, "TLSVersion"):
        versions = [("TLSv1.0", ssl.TLSVersion.TLSv1), ("TLSv1.1", ssl.TLSVersion.TLSv1_1),
                    ("TLSv1.2", ssl.TLSVersion.TLSv1_2), ("TLSv1.3", ssl.TLSVersion.TLSv1_3)]
    for name, ver in versions:
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.minimum_version = ver
            ctx.maximum_version = ver
            with socket.create_connection((host, port), timeout=6) as s:
                with ctx.wrap_socket(s, server_hostname=host) as ss:
                    c = ss.cipher()
                    ok(f"{name}  {c[0] if c else '-'}  {c[1] if c else ''}")
                    if name in ("TLSv1.0", "TLSv1.1"):
                        wrn(f"  {name} is deprecated")
        except Exception:
            bad(f"{name}  unsupported")
    print()
    rule("CIPHER ENUMERATION")
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=8) as s:
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                for c in (ss.shared_ciphers() or [])[:20]:
                    kv(c[0], f"{c[1]} · {c[2]} bit")
    except Exception:
        bad("could not enumerate")
    print()
    rule("HSTS")
    st, _, hdrs = http_get(f"https://{host}/", timeout=10)
    hsts = hdrs.get("strict-transport-security", "")
    if hsts:
        kv("hsts", hsts)
        m = re.search(r"max-age=(\d+)", hsts)
        if m and int(m.group(1)) < 15552000:
            wrn("max-age below 180 days")
        if "includesubdomains" not in hsts.lower():
            wrn("missing includeSubDomains")
        if "preload" not in hsts.lower():
            wrn("not preloaded")
    else:
        wrn("HSTS absent")


TAKEOVER_SIGS = [
    ("github.io", "There isn't a GitHub Pages site here"),
    ("herokudns", "No such app"), ("herokuapp", "No such app"),
    ("s3.amazonaws.com", "NoSuchBucket"), ("cloudfront.net", "Bad Request"),
    ("azurewebsites.net", "Error 404 - Web app not found"),
    ("trafficmanager.net", "Not Found"), ("fastly.net", "Fastly error: unknown domain"),
    ("netlify.app", "Not Found - Request ID"), ("netlify.com", "Not Found - Request ID"),
    ("vercel.app", "The deployment could not be found"), ("surge.sh", "project not found"),
    ("bitbucket.io", "Repository not found"), ("readthedocs.io", "unknown to Read the Docs"),
    ("zendesk.com", "Help Center Closed"), ("statuspage.io", "Status page not found"),
    ("ghost.io", "Domain error"), ("pantheonsite.io", "The gods are wise"),
    ("tumblr.com", "There's nothing here"), ("wordpress.com", "Do you want to register"),
    ("shopify.com", "Sorry, this shop is currently unavailable"),
    ("myshopify.com", "Sorry, this shop is currently unavailable"),
    ("webflow.io", "The page you are looking for doesn't exist"),
    ("cargo.site", "404 Not Found"), ("fly.dev", "404 Not Found"),
    ("render.com", "not found"), ("ngrok.io", "Tunnel"),
    ("intercom.help", "This page is reserved"),
    ("helpscoutdocs.com", "No settings were found"),
    ("teamwork.com", "Oops - We didn't find your site"),
    ("agilecrm.com", "Sorry, this page is no longer available"),
    ("airtable.com", "not found"), ("anima.io", "not found"),
    ("bitly.com", "bitly"), ("brightcove.com", "404"),
    ("cargocollective.com", "404"), ("co.uk", "Not Found"),
    ("desk.com", "Sorry, we couldn't find that page"),
    ("feedpress.me", "The feed has not been found"),
    ("freshdesk.com", "Page Not Found"), ("getresponse.com", "Page not found"),
    ("hatenablog.com", "404 Blog Not Found"),
    ("instapage.com", "Page Not Found"), ("kajabi.com", "Not Found"),
    ("launchrock.com", "Couldn't find the page"), ("landingi.com", "not found"),
    ("mailchimp.com", "404"), ("mystrikingly.com", "page not found"),
    ("pingdom.com", "This page has moved"),
    ("squarespace.com", "No site found"), ("strikingly.com", "page not found"),
    ("tave.com", "404"), ("tictail.com", "not found"),
    ("uberflip.com", "Non-hub domain"), ("unbounce.com", "The requested URL was not found"),
    ("uservoice.com", "This UserVoice subdomain is currently available"),
    ("vend.com", "not found"), ("wpengine.com", "not found"),
]


def mod_dangling_hook():
    domain = ask("domain", "example.com")
    subs = set()
    if ask("hunt subdomains first? (y/n)", "y").lower().startswith("y"):
        spin("collecting subdomains")
        for fn in (crtsh, certspotter, otx_passive, hackertarget_hosts):
            try:
                subs |= fn(domain)
            except Exception:
                pass
    raw = ask("or paste extra subdomains (comma separated)", "")
    for s in raw.split(","):
        if s.strip():
            subs.add(s.strip().lower())
    if not subs:
        bad("no subdomains to test")
        return
    inf(f"checking {len(subs)} host(s) for dangling cnames")
    findings = 0
    pg = Progress(len(subs), "checking")
    for s in sorted(subs):
        pg.update()
        cn = cname_of(s)
        if not cn:
            continue
        st, body, _ = http_get(f"http://{s}/", timeout=8, retries=0)
        text = body.decode("utf-8", "replace")[:4000] if body else ""
        badged = False
        for needle, sig in TAKEOVER_SIGS:
            if needle in cn.lower() and sig.lower() in text.lower():
                findings += 1
                LIVE["hits"] += 1
                FXS.ping(0.25)
                pg.line()
                print(f"  {sev_tag('high')} {fg(TH['text'])}{s}{RESET}")
                kv("cname", cn)
                kv("service", needle)
                badged = True
        pg.line()
        if not badged:
            print(f"  {fg(TH['dim'])}  {s} -> {cn}{RESET}")
    pg.done()
    inf(f"{findings} potential takeover(s)")


SQLI_PAYLOADS = ["'", "\"", "')", "';-- -", "' OR '1'='1", "' OR 1=1-- -",
                 "1' AND SLEEP(2)-- -", "\" AND SLEEP(2)-- -", "'))-- -",
                 "') OR ('1'='1", "\\", "'||'", "1 AND 1=1", "1 AND 1=2"]

SQL_ERRORS = [
    r"SQL syntax.*MySQL", r"Warning.*\Wmysqli?_", r"PostgreSQL.*ERROR",
    r"ORA-\d{5}", r"Microsoft OLE DB Provider for SQL Server",
    r"ODBC SQL Server Driver", r"SQLite/JDBCDriver", r"SQLite\.Exception",
    r"System\.Data\.SQLite\.SQLiteException", r"valid MySQL result",
    r"MySqlClient\.", r"Unclosed quotation mark",
    r"quoted string not properly terminated", r"org\.hibernate",
    r"SQLServer JDBC Driver", r"Dynamic SQL Error", r"Unknown column",
    r"Column count doesn't match", r"Microsoft Access Driver",
    r"JET Database Engine", r"Access Database Engine", r"pg_query\(\)",
    r"pg_exec\(\)", r"supplied argument is not a valid MySQL",
    r"Invalid query", r"MySQLSyntaxErrorException", r"PSQLException",
]


def mod_injector():
    url = ask("url with params", "https://example.com/item?id=1")
    if "://" not in url:
        url = "https://" + url
    params = qs_params(url)
    if not params:
        bad("no query parameters in url")
        return
    st0, body0, _ = http_get(url, timeout=12)
    if st0 is None:
        bad("unreachable")
        return
    base_len = len(body0)
    inf(f"testing {len(params)} parameter(s) with {len(SQLI_PAYLOADS)} payloads")
    findings = 0
    for key, val in params:
        for pay in SQLI_PAYLOADS:
            test = set_param(url, key, (val or "1") + pay)
            t0 = time.time()
            st, body, _ = http_get(test, timeout=20, retries=0)
            dt = time.time() - t0
            text = body.decode("utf-8", "replace")[:200000]
            err = None
            for pat in SQL_ERRORS:
                m = re.search(pat, text, re.I)
                if m:
                    err = strip_tags(m.group(0))[:90]
                    break
            if err:
                findings += 1
                LIVE["hits"] += 1
                FXS.ping(0.2)
                print(f"  {sev_tag('high')} {key}  payload={pay!r}")
                kv("error", err)
                break
            if "SLEEP" in pay.upper() and dt > 1.8:
                findings += 1
                LIVE["hits"] += 1
                print(f"  {sev_tag('high')} {key}  time-based blind ({dt:.2f}s)")
                kv("payload", pay)
                break
            if abs(len(text) - base_len) > max(40, base_len * 0.05):
                wrn(f"  {key}  length delta {len(text) - base_len:+d} on {pay!r}")
    print()
    rule("SUMMARY")
    inf(f"{findings} confirmed injection point(s)")
    if not findings:
        bad("no errors — try a different parameter or a deeper payload set")


def mod_reflect():
    url = ask("url with params", "https://example.com/search?q=test")
    if "://" not in url:
        url = "https://" + url
    marker = "wt" + "".join(random.choice(string.ascii_lowercase) for _ in range(6))
    params = qs_params(url)
    if params:
        inf(f"reflection test on {len(params)} parameter(s)")
        for key, val in params:
            for pay in (marker, f"{marker}'\"<>", f"{marker}<b>",
                        f"<script>{marker}</script>"):
                st, body, _ = http_get(set_param(url, key, pay), timeout=12, retries=0)
                text = body.decode("utf-8", "replace")
                if marker in text:
                    idx = text.find(marker)
                    ctx = strip_tags(text[max(0, idx - 40):idx + 60]).replace("\n", " ")
                    if "<" in pay and pay in text:
                        print(f"  {sev_tag('high')} {key}  UNENCODED reflection")
                    else:
                        print(f"  {sev_tag('medium')} {key}  reflected (encoded)")
                    kv("context", ctx[:110])
                    LIVE["hits"] += 1
                    break
    print()
    rule("OPEN REDIRECT")
    targets = ["https://evil.example", "//evil.example", "https:evil.example",
               "///evil.example", "https://evil.example/wt"]
    keys = ["url", "redirect", "redirect_uri", "redirect_url", "next", "return",
            "returnTo", "return_to", "dest", "destination", "continue", "target",
            "to", "out", "link", "goto", "r", "u", "ref"]
    found = 0
    for k in keys:
        for t in targets:
            st, _, hdrs = http_get(set_param(url, k, t), timeout=10, retries=0)
            loc = hdrs.get("location", "")
            if "evil.example" in loc:
                found += 1
                LIVE["hits"] += 1
                print(f"  {sev_tag('medium')} {k}={t}  ->  {loc[:80]}")
                break
    if not found:
        bad("no open redirect on common parameter names")
    print()
    rule("HEADER INJECTION")
    for pay in ("%0d%0aWT-Inject:1", "%0aWT-Inject:1"):
        st, _, hdrs = http_get(set_param(url, "q", pay), timeout=10, retries=0)
        if hdrs.get("wt-inject"):
            print(f"  {sev_tag('medium')} CRLF header injection via q")


def mod_cors_breaker():
    url = ask("url", "https://example.com/api/me")
    if "://" not in url:
        url = "https://" + url
    p = urllib.parse.urlparse(url)
    root = p.netloc.split(":")[0]
    origins = ["https://evil.example", "null", f"https://{root}.evil.example",
               f"https://evil{root}", f"http://{root}", f"https://sub.{root}",
               "https://" + root.upper()]
    inf(f"probing {len(origins)} origin variants")
    worst = "info"
    for o in origins:
        st, body, hdrs = http_get(url, timeout=12, retries=0, headers={"Origin": o})
        acao = hdrs.get("access-control-allow-origin", "")
        acc = hdrs.get("access-control-allow-credentials", "").lower()
        if not acao:
            print(f"  {fg(TH['dim'])}-  {o:<34} no ACAO{RESET}")
            continue
        sev = "info"
        if acao == "*" and acc == "true":
            sev = "medium"
        elif acao == o and acc == "true":
            sev = "high"
        elif acao == o:
            sev = "low"
        elif acao == "null":
            sev = "medium"
        print(f"  {sev_tag(sev)} {o:<34} -> {acao}")
        order = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        if order.get(sev, 0) > order.get(worst, 0):
            worst = sev
        if acao == o and acc == "true":
            LIVE["hits"] += 1
    print()
    inf(f"worst finding: {worst}")
    if worst in ("high", "critical"):
        wrn("arbitrary origin reflected WITH credentials — readable cross-site data")


BUCKET_SUFFIXES = [
    ("s3", "http://{n}.s3.amazonaws.com/"),
    ("s3-region", "http://{n}.s3.us-east-1.amazonaws.com/"),
    ("s3-website", "http://{n}.s3-website-us-east-1.amazonaws.com/"),
    ("s3-legacy", "http://s3.amazonaws.com/{n}/"),
    ("gcs", "http://storage.googleapis.com/{n}/"),
    ("gcs-alt", "http://{n}.storage.googleapis.com/"),
    ("azure-blob", "http://{n}.blob.core.windows.net/"),
    ("azure-web", "http://{n}.azurewebsites.net/"),
    ("digitalocean", "http://{n}.nyc3.digitaloceanspaces.com/"),
    ("linode", "http://{n}.us-east-1.linodeobjects.com/"),
    ("wasabi", "http://s3.us-east-1.wasabisys.com/{n}/"),
    ("backblaze", "http://f000.backblazeb2.com/file/{n}/"),
    ("alibaba", "http://{n}.oss-cn-hangzhou.aliyuncs.com/"),
]


def mod_bucket_dive():
    base = ask("domain / project name (e.g. acme or acme.com)", "example")
    words = ask("extra words (comma list, blank for none)", "")
    stems = {base, base.split(".")[0], base.replace(".", "-"), base.replace(".", "")}
    for w in words.split(","):
        if w.strip():
            stems.add(w.strip())
    stems |= {s + sfx for s in list(stems) for sfx in
              ("-dev", "-prod", "-staging", "-test", "-backup", "-assets", "-static",
               "-media", "-data", "-files", "-uploads", "-public", "-private", "-cdn",
               "-logs", "-archive", "-old", "-new", "-beta")}
    inf(f"{len(stems)} names x {len(BUCKET_SUFFIXES)} providers")
    found = []

    def probe(args):
        name, label, tpl = args
        url = tpl.format(n=name)
        st, body, hdrs = http_get(url, timeout=8, retries=0)
        if st in (200, 403):
            listing = b"<ListBucketResult" in body or b"<EnumerationResults" in body
            return name, label, url, st, listing
        return None

    jobs = [(n, lbl, tpl) for n in stems for lbl, tpl in BUCKET_SUFFIXES]
    pg = Progress(len(jobs), "probing")
    with ThreadPoolExecutor(max_workers=40) as ex:
        for r in ex.map(probe, jobs):
            pg.update()
            if not r:
                continue
            name, label, url, st, listing = r
            found.append(r)
            LIVE["hits"] += 1
            sev = "high" if (listing and st == 200) else "medium" if st == 200 else "low"
            pg.line()
            print(f"  {sev_tag(sev)} {label:<14} {st}  {url[:70]}")
            if listing:
                hit("     -> PUBLIC LISTING (directory readable)")
    pg.done()
    print()
    inf(f"{len(found)} bucket(s) exist · {sum(1 for f in found if f[4])} publicly listable")
    save_json("wt_buckets.json",
              [{"name": n, "provider": l, "url": u, "status": s, "listing": ls}
               for n, l, u, s, ls in found])


WAF_SIGS = [
    ("cloudflare", [("server", r"cloudflare"), ("cf-ray", ""), ("__cfduid", "")]),
    ("akamai", [("server", r"AkamaiGHost"), ("x-akamai", "")]),
    ("aws-waf", [("x-amzn-requestid", ""), ("x-amz-cf-id", "")]),
    ("imperva", [("x-iinfo", ""), ("visid_incap", "")]),
    ("sucuri", [("x-sucuri-id", ""), ("server", r"Sucuri")]),
    ("f5-bigip", [("server", r"BigIP"), ("x-wa-info", "")]),
    ("barracuda", [("server", r"Barracuda"), ("barra_counter_session", "")]),
    ("fortiweb", [("server", r"FortiWeb")]),
    ("citrix-netscaler", [("via", r"NS-CACHE"), ("cookie", r"citrix_ns_id")]),
    ("fastly", [("x-served-by", r"cache"), ("x-fastly", "")]),
    ("varnish", [("via", r"varnish"), ("x-varnish", "")]),
    ("nginx", [("server", r"nginx")]),
    ("wordfence", [("server", r"Wordfence")]),
    ("modsecurity", [("server", r"mod_security")]),
    ("edgecast", [("server", r"ECAcc")]),
    ("stackpath", [("server", r"StackPath")]),
]

CDN_HINTS = [("cloudflare", r"cloudflare"), ("akamai", r"akamai|edgesuite"),
             ("fastly", r"fastly"), ("cloudfront", r"cloudfront"),
             ("azure-cdn", r"azureedge|azurefd"), ("google", r"googlehosted"),
             ("bunny", r"bunnycdn"), ("keycdn", r"keycdn"), ("stackpath", r"stackpath"),
             ("incapsula", r"incapula|imperva"), ("sucuri", r"sucuri")]


def mod_shield_probe():
    url = ask("url", "https://example.com")
    if "://" not in url:
        url = "https://" + url
    inf(f"detecting waf/cdn in front of {url}")
    st, body, hdrs = http_get(url, timeout=12)
    if st is None:
        bad("unreachable")
        return
    blob = " ".join(f"{k}:{v}" for k, v in hdrs.items()) + " " + \
        body.decode("utf-8", "replace")[:4000]
    print()
    rule("PASSIVE FINGERPRINT")
    found = 0
    for name, sigs in WAF_SIGS:
        for h, pat in sigs:
            hay = hdrs.get("set-cookie", "") if h.startswith("cookie") else hdrs.get(h, "")
            if not pat and hay:
                hit(f"{name}  (header {h})")
                found += 1
                break
            if pat and re.search(pat, hay, re.I):
                hit(f"{name}  (header {h} ~ /{pat}/)")
                found += 1
                break
    for name, pat in CDN_HINTS:
        if re.search(pat, blob, re.I):
            wrn(f"cdn hint: {name}")
            found += 1
    if not found:
        bad("no obvious waf/cdn signature")
    print()
    rule("ACTIVE PROBE")
    probes = [("xss", "/?wt=<script>alert(1)</script>"),
              ("sqli", "/?wt=1'%20OR%20'1'='1"),
              ("traversal", "/?wt=../../../../etc/passwd"),
              ("rce", "/?wt=;cat%20/etc/passwd"),
              ("badmethod", "/?wt=1%20UNION%20SELECT%201,2,3")]
    for label, q in probes:
        s2, b2, h2 = http_get(url.rstrip("/") + q, timeout=12, retries=0)
        flags = []
        if s2 in (403, 406, 419, 429, 501, 503):
            flags.append(f"blocked ({s2})")
        if b2 and re.search(rb"access denied|forbidden|blocked|attention required|"
                            rb"captcha|incapsula|cloudflare|mod_security|"
                            rb"not acceptable|request rejected", b2, re.I):
            flags.append("block page body")
        if h2.get("x-cache") or h2.get("x-served-by"):
            flags.append("edge cache present")
        print(f"  {sev_tag('info' if not flags else 'medium')} {label:<12} "
              f"{s2}  {' · '.join(flags) or 'passes through'}")


def mod_cms_skeleton():
    url = ask("url", "https://example.com")
    if "://" not in url:
        url = "https://" + url
    url = url.rstrip("/")
    inf("cms deep scan")
    hits = 0
    print()
    rule("WORDPRESS")
    st, body, _ = http_get(url + "/wp-json/wp/v2/users", timeout=12, retries=0)
    if st == 200:
        users = jload(body)
        if isinstance(users, list):
            hit(f"/wp-json/wp/v2/users exposes {len(users)} user(s)")
            for u in users[:10]:
                kv(u.get("slug", "?"), f"id={u.get('id')} name={u.get('name','')[:40]}")
            hits += 1
    st, body, _ = http_get(url + "/wp-login.php", timeout=12, retries=0)
    if st == 200 and b"wp-login" in body:
        hit("wp-login.php present")
        hits += 1
    st, body, _ = http_get(url + "/readme.html", timeout=12, retries=0)
    if st == 200:
        m = re.search(rb"Version\s*([\d.]+)", body)
        hit(f"readme.html -> wordpress {m.group(1).decode() if m else '?'}")
    for p in ("/xmlrpc.php", "/wp-cron.php", "/wp-content/debug.log",
              "/wp-content/uploads/", "/wp-config.php.bak", "/.wp-config.php.swp"):
        s2, _, _ = http_get(url + p, timeout=8, retries=0)
        if s2 == 200:
            hit(p)
            hits += 1
    print()
    rule("DRUPAL")
    for p, label in (("/CHANGELOG.txt", "changelog"), ("/core/CHANGELOG.txt", "core"),
                     ("/user/login", "login"), ("/user/register", "register"),
                     ("/admin/", "admin"), ("/sites/default/settings.php", "settings"),
                     ("/core/install.php", "installer")):
        s2, b2, _ = http_get(url + p, timeout=8, retries=0)
        if s2 == 200:
            m = re.search(rb"Drupal\s*([\d.]+)", b2 or b"")
            hit(f"{label}: {p}" + (f"  v{m.group(1).decode()}" if m else ""))
            hits += 1
    print()
    rule("JOOMLA")
    for p, label in (("/administrator/", "admin"), ("/language/en-GB/en-GB.xml", "version"),
                     ("/configuration.php-dist", "config dist"),
                     ("/components/", "components"), ("/modules/", "modules")):
        s2, b2, _ = http_get(url + p, timeout=8, retries=0)
        if s2 == 200:
            m = re.search(rb"<version>([\d.]+)", b2 or b"")
            hit(f"{label}: {p}" + (f"  v{m.group(1).decode()}" if m else ""))
            hits += 1
    print()
    rule("GENERIC")
    st, body, hdrs = http_get(url, timeout=12)
    blob = body.decode("utf-8", "replace").lower() if body else ""
    for needle, lbl in (("wp-content", "WordPress"), ("drupal", "Drupal"),
                        ("joomla", "Joomla"), ("magento", "Magento"),
                        ("shopify", "Shopify"), ("__next_data__", "Next.js"),
                        ("_nuxt", "Nuxt"), ("ghost", "Ghost"),
                        ("squarespace", "Squarespace"), ("wix.com", "Wix"),
                        ("webflow", "Webflow"), ("hubspot", "HubSpot"),
                        ("typo3", "TYPO3"), ("concrete5", "Concrete5"),
                        ("craftcms", "Craft CMS"), ("strapi", "Strapi")):
        if needle in blob:
            print(f"  {sev_tag('info')} cms/stack: {lbl}")
            hits += 1
    print()
    inf(f"{hits} indicator(s) found")


PARAM_WORDS = [
    "id", "page", "p", "q", "s", "search", "query", "keyword", "term", "name", "user",
    "username", "email", "pass", "password", "token", "key", "api_key", "apikey",
    "secret", "auth", "session", "sid", "uid", "gid", "pid", "tid", "type", "cat",
    "category", "tag", "sort", "order", "dir", "direction", "limit", "offset", "start",
    "end", "from", "to", "date", "year", "month", "day", "lang", "locale", "country",
    "region", "city", "zip", "code", "ref", "referer", "referrer", "source", "src",
    "url", "uri", "link", "href", "path", "file", "filename", "folder", "doc",
    "document", "download", "upload", "action", "do", "op", "mode", "view", "format",
    "output", "callback", "json", "xml", "debug", "test", "dev", "admin",
    "redirect", "next", "return", "continue", "dest", "target", "goto", "out",
    "filter", "where", "field", "fields", "select", "order_by", "group", "having",
    "join", "table", "db", "schema", "column", "row", "index", "item", "product",
    "cart", "sku", "price", "min", "max", "size", "color", "brand", "model", "version",
    "v", "ver", "build", "rev", "status", "state", "step", "stage", "level", "role",
    "perm", "scope", "client", "app", "platform", "os", "device", "ua", "ip", "host",
    "domain", "sub", "alias", "slug", "title", "body", "content", "text", "msg",
    "message", "note", "comment", "reply", "parent", "child", "root", "node", "tree",
    "include", "require", "template", "tpl", "theme", "skin", "layout", "render",
    "cache", "nocache", "fresh", "force", "reload", "reset", "clear", "flush",
    "nonce", "csrf", "xsrf", "_token", "sig", "signature", "hash", "checksum",
    "expires", "ttl", "timeout", "delay", "wait", "retry", "attempt", "count", "num",
    "n", "per_page", "perpage", "pagesize", "page_size", "batch", "chunk", "cursor",
]


def mod_param_hunt():
    url = ask("url (with at least one param)", "https://example.com/page?id=1")
    if "://" not in url:
        url = "https://" + url
    wordfile = ask("param wordlist ('default' / file / comma list)", "default")
    threads = int(ask("threads", "20") or 20)
    if os.path.isfile(wordfile):
        with open(wordfile, "r", encoding="utf-8", errors="replace") as f:
            words = [l.strip() for l in f if l.strip()]
    elif wordfile.strip().lower() in ("default", ""):
        words = PARAM_WORDS
    else:
        words = [w.strip() for w in wordfile.split(",") if w.strip()]
    st0, body0, _ = http_get(url, timeout=12)
    if st0 is None:
        bad("unreachable")
        return
    ref = len(body0)
    inf(f"testing {len(words)} parameter names against a {ref} byte baseline")
    found = []

    def probe(w):
        st, body, _ = http_get(set_param(url, w, "wt" + str(random.randint(100, 999))),
                               timeout=10, retries=0)
        if st is None:
            return None
        return w, st, len(body), len(body) != ref

    pg = Progress(len(words), "probing")
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for r in ex.map(probe, words):
            pg.update()
            if not r:
                continue
            w, st, ln, diff = r
            if diff or st != st0:
                found.append((w, st, ln, st != st0))
                LIVE["hits"] += 1
                pg.line()
                print(f"  {sev_tag('medium')} {w:<20} status={st} len={ln} "
                      f"delta={ln - ref:+d}")
    pg.done()
    print()
    inf(f"{len(found)} parameter(s) change the response")
    if found:
        save_json("wt_params.json", [{"param": w, "status": s, "len": l}
                                     for w, s, l, _ in found])


UDP_PROBES = [
    (53, "dns", "dns"), (123, "ntp", "ntp"), (161, "snmp", "snmp"),
    (137, "netbios-ns", "netbios"), (69, "tftp", "tftp"), (5353, "mdns", "mdns"),
    (1900, "ssdp", "ssdp"), (500, "isakmp", "isakmp"), (4500, "ipsec-nat-t", "isakmp"),
    (1434, "mssql-browser", "mssql"), (3702, "ws-discovery", "wsd"),
    (5355, "llmnr", "llmnr"),
]


def _udp_payload(kind, host):
    if kind == "dns":
        q = b"".join(bytes([len(p)]) + p.encode() for p in "example.com".split("."))
        return struct.pack(">HHHHHH", random.randint(1, 65535), 0x0100, 1, 0, 0, 0) + \
            q + b"\x00" + struct.pack(">HH", 1, 1)
    if kind == "ntp":
        return b"\x1b" + b"\x00" * 47
    if kind == "snmp":
        return bytes.fromhex(
            "302602010004067075626c6963a019020400000001020100020100300b300906052b0601"
            "0201000500")
    if kind == "netbios":
        return bytes.fromhex("a2480000000100000000000020434b4141414141414141414141414141414141"
                             "4141414141414141410000210001")
    if kind == "tftp":
        return b"\x00\x01" + b"test" + b"\x00" + b"octet\x00"
    if kind == "mdns":
        q = b"".join(bytes([len(p)]) + p.encode()
                     for p in "_services._dns-sd._udp.local".split("."))
        return struct.pack(">HHHHHH", 0, 0, 1, 0, 0, 0) + q + b"\x00" + \
            struct.pack(">HH", 12, 1)
    if kind == "ssdp":
        return (b"M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n"
                b"MAN: \"ssdp:discover\"\r\nMX: 1\r\nST: ssdp:all\r\n\r\n")
    if kind == "isakmp":
        return bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000"
                             "0110020000000000000000000000000000000000000000000000000000000000"
                             "0000000000000000")
    if kind == "mssql":
        return b"\x02"
    if kind == "wsd":
        return (b"<?xml version=\"1.0\"?><e:Envelope xmlns:e=\"http://www.w3.org/2003/05/"
                b"soap/envelope/\"><e:Body><d:Probe xmlns:d=\"http://schemas.xmlsoap.org/ws/"
                b"2005/08/discovery\"><d:Types>d:Device</d:Types></d:Probe></e:Body>"
                b"</e:Envelope>")
    if kind == "llmnr":
        q = b"".join(bytes([len(p)]) + p.encode() for p in host.split("."))
        return struct.pack(">HHHHHH", 0, 0, 1, 0, 0, 0) + q + b"\x00" + \
            struct.pack(">HH", 1, 1)
    return b"\x00"


def mod_udp_echo():
    host = ask("host / ip", "127.0.0.1")
    ip = resolve(host) or host
    inf(f"probing {len(UDP_PROBES)} udp services on {ip}")
    found = 0
    for port, label, kind in UDP_PROBES:
        data = udp_probe(ip, port, _udp_payload(kind, ip), timeout=2.0)
        if not data:
            print(f"  {fg(TH['dim'])}-  {port:<6} {label:<16} no reply{RESET}")
            continue
        found += 1
        LIVE["hits"] += 1
        print(f"  {sev_tag('info')} {port:<6} {label:<16} {len(data)} bytes")
        kv("  raw", data[:80].hex())
        if kind == "ntp" and len(data) > 43:
            kv("  stratum", data[1])
            kv("  refid", data[12:16].decode("latin-1", "replace"))
            tx = struct.unpack(">I", data[40:44])[0]
            if tx:
                kv("  transmit", datetime.fromtimestamp(tx - 2208988800, timezone.utc)
                   .strftime("%Y-%m-%d %H:%M:%SZ"))
        if kind == "snmp" and b"public" in data:
            kv("  community", "public accepted")
        if kind == "netbios" and len(data) > 72:
            name = data[56:72].decode("latin-1", "replace").strip()
            if name:
                kv("  netbios name", name)
    print()
    inf(f"{found} udp service(s) responding")


def mod_shell_door():
    host = ask("host / ip", "127.0.0.1")
    ip = resolve(host) or host
    print()
    rule("SSH (22)")
    try:
        s = socket.create_connection((ip, 22), timeout=6)
        banner = s.recv(256).decode("utf-8", "replace").strip()
        kv("banner", banner)
        m = re.search(r"SSH-([\d.]+)-(\S+)", banner)
        if m:
            kv("protocol", m.group(1))
            kv("software", m.group(2))
            if m.group(1) == "1.99" or m.group(1).startswith("1"):
                wrn("SSHv1 still offered")
        s.sendall(b"SSH-2.0-WT_Scanner\r\n")
        s.settimeout(2.5)
        try:
            pkt = s.recv(4096)
            kv("kex reply", f"{len(pkt)} bytes")
            algos = re.findall(rb"[a-z0-9@.\-]{4,40}", pkt[20:])
            names = [a.decode() for a in algos if b"-" in a or b"@" in a]
            if names:
                kv("offered", ", ".join(names[:18])[:160])
                for weak in ("diffie-hellman-group1-sha1", "diffie-hellman-group14-sha1",
                             "ssh-rsa", "3des-cbc", "arcfour"):
                    if any(weak in n for n in names):
                        wrn(f"weak algorithm: {weak}")
        except Exception:
            pass
        s.close()
    except Exception:
        bad("no ssh on 22")
    print()
    rule("SMB (445)")
    try:
        s = socket.create_connection((ip, 445), timeout=6)
        s.sendall(b"\x00\x00\x00\x85\xffSMB\x72\x00\x00\x00\x00\x18\x53\xc8\x00\x00"
                  b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00"
                  b"\x00\x62\x00\x02NT LM 0.12\x00\x02SMB 2.002\x00\x02SMB 2.1\x00")
        d = s.recv(1024)
        if b"SMB" in d:
            dialects = re.findall(rb"SMB [\d.]+", d)
            kv("dialects", ", ".join(x.decode() for x in dialects) or "SMB1 only")
            if b"SMB 1.0" in d or b"NT LM 0.12" in d:
                wrn("SMB1 offered — check MS17-010 (EternalBlue)")
            if b"SMB 3" in d:
                hit("SMB3 supported")
        s.close()
    except Exception:
        bad("no smb on 445")
    print()
    rule("RDP (3389)")
    try:
        s = socket.create_connection((ip, 3389), timeout=6)
        s.sendall(b"\x03\x00\x00\x13\x0e\xe0\x00\x00\x00\x00\x00\x01\x00\x08\x00"
                  b"\x03\x00\x00\x00")
        d = s.recv(256)
        if d[:2] == b"\x03\x00":
            kv("x.224", "connect-confirm received")
            if len(d) > 11 and d[11] == 0x02:
                kv("rdp negotiated", "ok — check NLA / BlueKeep on pre-2019 builds")
        s.close()
    except Exception:
        bad("no rdp on 3389")
    print()
    rule("FTP (21)")
    try:
        s = socket.create_connection((ip, 21), timeout=6)
        fh = s.makefile("rb")
        kv("banner", _sock_line(fh))
        s.sendall(b"FEAT\r\n")
        for _ in range(12):
            line = _sock_line(fh)
            if line.startswith("211"):
                break
            kv("feat", line)
        s.sendall(b"SYST\r\n")
        kv("syst", _sock_line(fh))
        s.sendall(b"QUIT\r\n")
        s.close()
    except Exception:
        bad("no ftp on 21")


def mod_mirror_ip():
    ip = ask("ip address (or hostname)", "")
    if not ip:
        return
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", ip):
        ip = resolve(ip) or ip
    kv("target", ip)
    kv("ptr", reverse_dns(ip) or "none")
    print()
    rule("HACKERTARGET REVERSE IP")
    st, body, _ = http_get(
        f"https://api.hackertarget.com/reverseiplookup/?q={ip}", timeout=25)
    if st == 200 and body and b"error" not in body.lower():
        hosts = [h.strip() for h in body.decode().splitlines() if h.strip()]
        kv("hosts", len(hosts))
        for h in hosts[:60]:
            hit(h)
            LIVE["hits"] += 1
    else:
        bad("no data (rate limited?)")
    print()
    rule("BGP / ANNOUNCEMENT")
    d = get_json(f"https://api.bgpview.io/ip/{ip}", timeout=15)
    for pfx in ((d or {}).get("data") or {}).get("prefixes", [])[:3]:
        kv("prefix", pfx.get("prefix"))
        kv("  asn", f"AS{(pfx.get('asn') or {}).get('asn')} "
                   f"{(pfx.get('asn') or {}).get('name', '')}")
        kv("  desc", (pfx.get("description") or "")[:90])


# ------------------------- NEW PENTEST (21-26) ---------------------------- #
def _spnego_ntlmssp():
    ntlm = (b"NTLMSSP\x00" + struct.pack("<I", 1) + struct.pack("<I", 0xE2088237) +
            b"\x00" * 16)
    oid = bytes.fromhex("2b06010401823702020a")

    def tlv(tag, payload):
        return bytes([tag, len(payload)]) + payload

    mech_list = tlv(0x30, tlv(0x06, oid))
    neg_init = tlv(0x30, tlv(0xA0, mech_list) + tlv(0xA2, tlv(0x04, ntlm)))
    return tlv(0x60, tlv(0x06, bytes.fromhex("2b0601050502")) + tlv(0xA0, neg_init))


def _smb2_header(cmd, mid, sid=0, tid=0, credits=1):
    return (b"\xfeSMB" + struct.pack("<H", 64) + struct.pack("<H", credits) +
            struct.pack("<I", 0) + struct.pack("<H", cmd) + struct.pack("<H", 1) +
            struct.pack("<I", 0) + struct.pack("<Q", mid) + struct.pack("<I", 0) +
            struct.pack("<I", 0) + struct.pack("<Q", sid) + struct.pack("<Q", tid))


def _smb2_negociate():
    body = (struct.pack("<H", 36) + struct.pack("<H", 1) + struct.pack("<I", 0) +
            struct.pack("<H", 0) + struct.pack("<H", 0) + struct.pack("<I", 0) +
            struct.pack("<Q", 0) + struct.pack("<Q", 0) +
            b"\x00\x00" + b"\x02\x02" + b"\x10\x02" + b"\x22\x02" + b"\x00\x03" +
            b"\x11\x03" + b"\x02\x02" + b"\x00" * 16 + struct.pack("<I", 0))
    return _smb2_header(0, 1) + body



def mod_smb_null():
    host = ask("host / ip", "127.0.0.1")
    ip = resolve(host) or host
    port = int(ask("port", "445") or 445)
    kv("target", f"{host} ({ip}:{port})")
    print()
    rule("SMB NEGOTIATE")
    try:
        s = socket.create_connection((ip, port), timeout=7)
        # classic SMB1 negotiate (dialects)
        neg1 = (b"\x00\x00\x00\x85\xffSMB\x72\x00\x00\x00\x00\x18\x53\xc8\x00\x00"
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00"
                b"\x00\x62\x00\x02NT LM 0.12\x00\x02SMB 2.002\x00\x02SMB 2.1\x00")
        s.sendall(neg1)
        d = s.recv(1024)
        if not d:
            bad("no response")
            s.close()
            return
        if b"SMB" in d:
            ok("SMB protocol detected")
            dialects = re.findall(rb"SMB [\d.]+", d)
            if dialects:
                kv("dialects", ", ".join(x.decode() for x in dialects))
            if b"SMB 1" in d or b"NT LM 0.12" in d:
                wrn("SMB1 / NT LM still offered — MS17-010 / EternalBlue risk")
            if b"SMB 2" in d or b"SMB 3" in d:
                hit("SMB2/3 supported")
        # try pure SMB2 negotiate
        try:
            s2 = socket.create_connection((ip, port), timeout=6)
            pkt = b"\x00\x00" + struct.pack(">H", len(_smb2_negociate())) + _smb2_negociate()
            s2.sendall(pkt)
            r2 = s2.recv(2048)
            if r2 and b"\xfeSMB" in r2:
                ok("SMB2 negotiate successful")
                # dialect
                if len(r2) > 72:
                    dialect = struct.unpack_from("<H", r2, 72)[0] if len(r2) > 73 else 0
                    kv("smb2 dialect", hex(dialect))
            s2.close()
        except Exception:
            pass
        s.close()
    except Exception as e:
        bad(f"connection failed: {e}")
        return

    print()
    rule("NULL SESSION (anonymous)")
    # Very basic null session probe via IPC$ style (SMB1 Session Setup AndX)
    try:
        s = socket.create_connection((ip, port), timeout=6)
        # SMB_COM_SESSION_SETUP_ANDX with empty user/pass (null)
        # This is a simplified probe; real null session is more involved
        null_setup = (
            b"\x00\x00\x00\x48\xffSMB\x73\x00\x00\x00\x00\x18\x07\xc8\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x0c\xff\x00\x00\x00\x04\x11\x0a\x00\x00\x00\x00"
            b"\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xd4\x00\x00\x00"
            b"\x00\x00\x00\x00"  # empty user / domain / etc
        )
        s.sendall(null_setup)
        r = s.recv(1024)
        if r and len(r) > 9:
            status = struct.unpack_from("<I", r, 9)[0] if len(r) > 12 else 0
            if status == 0:
                hit("null session accepted (status 0)")
                LIVE["hits"] += 1
                FXS.ping()
            else:
                kv("session setup status", hex(status))
                if status in (0xc000006d, 0xc0000064):  # STATUS_LOGON_FAILURE / no such user
                    inf("null session rejected (expected on modern hosts)")
                else:
                    inf(f"response received (status {hex(status)})")
        s.close()
    except Exception as e:
        bad(f"null session probe failed: {e}")

    print()
    rule("SIGNING / SECURITY NOTES")
    inf("check message signing requirement and guest access separately")
    inf("use tools like crackmapexec / smbmap for deeper null session enumeration")
    save_json(f"wt_smb_{safe_name(host)}.json", {"host": host, "ip": ip, "port": port})

def mod_smuggler():
    host = ask("host", "example.com")
    port = int(ask("port", "443") or 443)
    path = ask("path", "/")
    tls = port in TLS_VARIANTS if (TLS_VARIANTS := TLS_PORTS) else port == 443
    inf(f"CL/TE desync probes against {host}:{port}{path}")

    def req(headers, body, label):
        raw = (f"POST {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {UA}\r\n"
               f"Connection: keep-alive\r\n" + headers + "\r\n" + body).encode()
        t0 = time.time()
        data = http_raw(host, port, raw, timeout=9, tls=tls)
        dt = time.time() - t0
        status = data.split(b"\r\n", 1)[0].decode("latin-1", "replace") if data else "-"
        print(f"  {sev_tag('info')} {label:<14} {status[:40]:<40} {dt:.2f}s")
        return data, dt

    # baseline
    req("Content-Length: 6\r\n", "x=1&y", "baseline")
    print()
    rule("CL.TE")
    data, dt = req("Content-Length: 6\r\nTransfer-Encoding: chunked\r\n",
                   "0\r\n\r\nG", "cl.te")
    if dt > 4.5:
        wrn("  CL.TE timeout — front-end uses CL, back-end uses TE (likely)")
    print()
    rule("TE.CL")
    data, dt = req("Content-Length: 4\r\nTransfer-Encoding: chunked\r\n",
                   "5c\r\nGPOST / HTTP/1.1\r\nHost: x\r\n\r\n0\r\n\r\n", "te.cl")
    if dt > 4.5:
        wrn("  TE.CL timeout — front-end uses TE, back-end uses CL (likely)")
    print()
    rule("TE.TE OBFUSCATION")
    for hdr, label in (("Transfer-Encoding: xchunked\r\nTransfer-Encoding: chunked\r\n",
                        "xchunked"),
                       ("Transfer-Encoding: chunked\r\nTransfer-Encoding: identity\r\n",
                        "double-te"),
                       ("Transfer-Encoding : chunked\r\n", "space-colon"),
                       ("Transfer-encoding: chunked\r\n", "lowercase")):
        data, dt = req("Content-Length: 6\r\n" + hdr, "0\r\n\r\nX", label)
        if dt > 4.5:
            wrn(f"  {label}: desync behaviour observed")
    print()
    rule("DUPLICATE CL")
    data, dt = req("Content-Length: 6\r\nContent-Length: 11\r\n", "x=1&y", "dup-cl")
    if dt > 4.5:
        wrn("  duplicate Content-Length caused a stall")
    print()
    inf("timeouts above ~4.5s on a fast host are the strongest signal")


SSRF_PAYLOADS = [
    ("http://127.0.0.1", "loopback"),
    ("http://127.0.0.1:22", "loopback ssh"),
    ("http://localhost", "localhost"),
    ("http://[::1]", "ipv6 loopback"),
    ("http://169.254.169.254/latest/meta-data/", "aws metadata"),
    ("http://metadata.google.internal/computeMetadata/v1/", "gcp metadata"),
    ("http://169.254.169.254/metadata/instance?api-version=2021-02-01", "azure metadata"),
    ("http://0.0.0.0", "zero"),
    ("//127.0.0.1", "scheme relative"),
]


def mod_ssrf():
    url = ask("url with params", "https://example.com/fetch?url=http://x")
    if "://" not in url:
        url = "https://" + url
    params = qs_params(url)
    if not params:
        bad("no query parameters")
        return
    st0, body0, _ = http_get(url, timeout=12)
    base = body0.decode("utf-8", "replace") if body0 else ""
    inf(f"probing {len(params)} parameter(s) x {len(SSRF_PAYLOADS)} payloads")
    found = 0
    for key, val in params:
        for payload, label in SSRF_PAYLOADS:
            t0 = time.time()
            st, body, _ = http_get(set_param(url, key, payload), timeout=14, retries=0)
            dt = time.time() - t0
            text = body.decode("utf-8", "replace") if body else ""
            signals = []
            if st is None:
                signals.append("timeout/drop")
            elif st >= 500:
                signals.append(f"server error {st}")
            if re.search(r"(?i)ssh-2\.0|root:|daemon:|ami-id|instance-id|"
                         r"computeMetadata|project-id|meta-data", text):
                signals.append("internal content leaked")
            if text and similarity(text, base) < 0.6:
                signals.append("response diverges")
            if dt > 3.0:
                signals.append(f"slow {dt:.1f}s")
            if signals:
                found += 1
                LIVE["hits"] += 1
                print(f"  {sev_tag('medium')} {key}={label}")
                for s in signals:
                    bad("     " + s)
    print()
    inf(f"{found} candidate(s)")
    if not found:
        bad("no SSRF signal — parameter may not be a fetcher")


BACKUP_SUFFIXES = [
    ".bak", ".backup", ".old", ".orig", ".save", ".swp", ".swo", "~", ".copy", ".tmp",
    ".1", ".2", ".inc", ".dist", ".sample", ".example", ".txt", ".zip", ".tar.gz",
    ".sql", ".sql.gz", ".dump", ".gz", ".rar", ".7z",
]
BACKUP_BASES = [
    "index.php", "index.html", "index", "config.php", "config", "configuration.php",
    "settings.php", "wp-config.php", "web.config", "app.config", "database.yml",
    ".env", "env", "db.php", "db", "conn.php", "connect.php", "main.php", "admin.php",
    "login.php", "backup", "db", "dump", "site", "www", "public_html", "data", "export",
]


def mod_backup_hunter():
    base = ask("base url", "https://example.com")
    if "://" not in base:
        base = "https://" + base
    base = base.rstrip("/")
    inf("establishing a soft-404 baseline")
    st404, b404, _ = http_get(f"{base}/wt-not-a-real-file-{random.randint(1000,9999)}.xyz",
                              timeout=10, retries=0)
    ref = b404.decode("utf-8", "replace") if b404 else ""
    kv("soft-404 status", st404)
    kv("soft-404 size", len(ref))
    candidates = []
    for b in BACKUP_BASES:
        for s in BACKUP_SUFFIXES:
            candidates.append(b + s)
    for d in ("backup", "backups", "old", "bak", "archive", "db", "sql", "dump", "export"):
        for f in ("", ".zip", ".tar.gz", ".sql", ".rar", ".7z"):
            candidates.append(d + "/" + d + f if f else d + "/")
    candidates = dedupe(candidates)
    inf(f"testing {len(candidates)} candidate(s)")
    found = []

    def probe(p):
        st, body, hdrs = http_get(f"{base}/{p}", timeout=9, retries=0)
        if st is None or st != 200:
            return None
        txt = body.decode("utf-8", "replace", "ignore")
        if ref and similarity(txt, ref) > 0.93:
            return None
        return p, st, len(body), hdrs.get("content-type", "")

    pg = Progress(len(candidates), "hunting")
    with ThreadPoolExecutor(max_workers=32) as ex:
        for r in ex.map(probe, candidates):
            pg.update()
            if not r:
                continue
            p, st, ln, ct = r
            found.append(r)
            LIVE["hits"] += 1
            FXS.ping(0.1)
            pg.line()
            sev = "high" if re.search(r"\.(sql|dump|env|zip|tar\.gz|rar|7z)$", p) else "medium"
            print(f"  {sev_tag(sev)} {p:<38} {ln:>9,} B  {ct[:34]}")
    pg.done()
    print()
    inf(f"{len(found)} backup-like file(s) that differ from the 404 page")
    if found:
        save_json("wt_backups.json", [{"path": p, "size": l} for p, _, l, _ in found])


API_WORDS = ["api", "api/v1", "api/v2", "api/v3", "api/v4", "api/docs", "api/doc",
             "api/swagger", "api/swagger.json", "api/openapi.json", "api/schema",
             "api/graphql", "api/rest", "api/rpc", "api/json", "api/public",
             "api/private", "api/internal", "api/admin", "api/user", "api/users",
             "api/me", "api/account", "api/auth", "api/login", "api/token", "api/keys",
             "api/status", "api/health", "api/version", "api/config", "api/metrics",
             "api/debug", "graphql", "graphiql", "swagger", "swagger.json",
             "swagger-ui.html", "openapi.json", "rest", "rpc", "json", "jsonrpc",
             "v1", "v2", "v3", "rest/v1", "api.php", "api.asp", "api.aspx", "api.jsp",
             "api/index.php", "api/v1/users", "api/v1/items", "api/v1/products"]
API_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


def mod_api_mapper():
    base = ask("base url", "https://example.com")
    if "://" not in base:
        base = "https://" + base
    base = base.rstrip("/")
    inf(f"mapping {len(API_WORDS)} api roots")
    hits = []
    pg = Progress(len(API_WORDS), "mapping")
    for w in API_WORDS:
        pg.update()
        st, body, hdrs = http_get(f"{base}/{w}", timeout=9, retries=0)
        if st is None:
            continue
        ct = hdrs.get("content-type", "")
        is_json = "json" in ct.lower() or (body and body.lstrip()[:1] in (b"{", b"["))
        if st in (200, 401, 403, 405) and (is_json or st != 200):
            hits.append((w, st, ct, len(body)))
            LIVE["hits"] += 1
            pg.line()
            print(f"  {sev_tag('medium' if is_json else 'info')} {w:<28} {st}  "
                  f"{ct[:34]} {len(body)} B")
    pg.done()
    print()
    if not hits:
        bad("no api roots answered")
        return
    rule("METHOD MATRIX")
    for w, _, _, _ in hits[:6]:
        row = []
        for m in API_METHODS:
            st, _, _ = http_get(f"{base}/{w}", timeout=8, method=m, retries=0)
            row.append(f"{m}:{st if st else '-'}")
        kv(w, "  ".join(row))
    print()
    inf(f"{len(hits)} api root(s) responding")
    save_json("wt_api.json", [{"path": w, "status": s, "ctype": c} for w, s, c, _ in hits])


SNMP_COMMUNITIES = ["public", "private", "cisco", "admin", "snmp", "monitor", "default",
                    "readonly", "readwrite", "secret", "router", "switch", "internal",
                    "cable-docsis", "MGMT", "guest", "Public", "Private"]


def _ber_len(n):
    if n < 128:
        return bytes([n])
    out = b""
    while n:
        out = bytes([n & 0xFF]) + out
        n >>= 8
    return bytes([0x80 | len(out)]) + out


def _ber(tag, payload):
    return bytes([tag]) + _ber_len(len(payload)) + payload


def _snmp_get(community, oid):
    parts = [int(x) for x in oid.strip(".").split(".")]
    oid_enc = _ber(0x06, bytes([parts[0] * 40 + parts[1]]) +
                   b"".join(_ber(0x02, bytes([p])) if p > 127 else bytes([p])
                            for p in parts[2:]))
    varbind = _ber(0x30, oid_enc + _ber(0x05, b""))
    vbl = _ber(0x30, varbind)
    pdu = _ber(0xA0, _ber(0x02, bytes([random.randint(1, 127)])) +
               _ber(0x02, b"\x00") + _ber(0x02, b"\x00") + vbl)
    return _ber(0x30, _ber(0x02, b"\x01") + _ber(0x04, community.encode()) + pdu)


SNMP_OIDS = [("1.3.6.1.2.1.1.1.0", "sysDescr"),
             ("1.3.6.1.2.1.1.3.0", "sysUpTime"),
             ("1.3.6.1.2.1.1.5.0", "sysName"),
             ("1.3.6.1.2.1.1.6.0", "sysLocation"),
             ("1.3.6.1.2.1.1.4.0", "sysContact"),
             ("1.3.6.1.2.1.4.20.1.1", "ipAdEntAddr")]


def mod_snmp_walk():
    host = ask("host / ip", "127.0.0.1")
    ip = resolve(host) or host
    inf(f"testing {len(SNMP_COMMUNITIES)} community strings on {ip}:161")
    good = []
    for c in SNMP_COMMUNITIES:
        data = udp_probe(ip, 161, _snmp_get(c, "1.3.6.1.2.1.1.1.0"), timeout=2.0)
        if data and len(data) > 20:
            good.append(c)
            LIVE["hits"] += 1
            ok(f"community accepted: {c}")
    if not good:
        bad("no community string accepted")
        return
    print()
    rule("WALK")
    for oid, label in SNMP_OIDS:
        data = udp_probe(ip, 161, _snmp_get(good[0], oid), timeout=2.0)
        if not data:
            continue
        text = re.sub(rb"[^\x20-\x7e]+", b" ", data).decode("latin-1", "replace").strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            kv(label, text[:150])
    print()
    inf("accepted communities: " + ", ".join(good))


# =========================================================================== #
#  OSINT
# =========================================================================== #

def ddg(query, limit=20):
    st, body, _ = http_get("https://html.duckduckgo.com/html/?q=" +
                           urllib.parse.quote(query),
                           timeout=14, headers={"Referer": "https://duckduckgo.com/"})
    if not body:
        return []
    out = []
    for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                         body.decode("utf-8", "replace"), re.S):
        href = m.group(1)
        if "uddg=" in href:
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
        out.append((strip_tags(m.group(2)), htmlmod.unescape(href)))
        if len(out) >= limit:
            break
    return out


def mojeek(query, limit=20):
    st, body, _ = http_get("https://www.mojeek.com/search?q=" + urllib.parse.quote(query),
                           timeout=14)
    if not body:
        return []
    out = []
    for m in re.finditer(r'<a[^>]+class="ob"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                         body.decode("utf-8", "replace"), re.S):
        out.append((strip_tags(m.group(2)), m.group(1)))
        if len(out) >= limit:
            break
    if not out:
        for m in re.finditer(r'<a href="(https?://[^"]+)"[^>]*>(.*?)</a>',
                             body.decode("utf-8", "replace"), re.S):
            t = strip_tags(m.group(2))
            if t and "mojeek" not in m.group(1):
                out.append((t, m.group(1)))
            if len(out) >= limit:
                break
    return out


def searx(query, limit=20):
    insts = ["https://searx.be", "https://search.bus-hit.me", "https://searxng.site",
             "https://priv.au", "https://baresearch.org"]
    for base in insts:
        d = get_json(f"{base}/search?q={urllib.parse.quote(query)}&format=json",
                     timeout=14)
        if not d or not d.get("results"):
            continue
        return [(r.get("title", ""), r.get("url", "")) for r in d["results"][:limit]]
    return []


DORK_PRESETS = [
    ("pdf documents", 'site:{d} ext:pdf'),
    ("config files", 'site:{d} ext:env OR ext:ini OR ext:cfg OR ext:yml OR ext:yaml'),
    ("open directories", 'site:{d} intitle:"index of"'),
    ("login / admin panels", 'site:{d} (inurl:login OR inurl:admin OR inurl:signin)'),
    ("api keys in js", 'site:{d} ext:js ("api_key" OR "apikey" OR "token" OR "secret")'),
    ("backups", 'site:{d} (ext:bak OR ext:old OR ext:zip OR ext:tar.gz OR ext:sql.gz)'),
    ("sql dumps", 'site:{d} ext:sql'),
    ("subdomains", 'site:*.{d} -www'),
    ("cloud leaks", 'site:{d} ("drive.google.com" OR "s3.amazonaws.com" OR '
                    '"blob.core.windows.net")'),
    ("pastebin", '"{d}" site:pastebin.com'),
    ("github", '"{d}" site:github.com'),
    ("gitlab", '"{d}" site:gitlab.com'),
    ("error pages", 'site:{d} ("sql syntax" OR "stack trace" OR "fatal error" OR "Warning:")'),
    ("phpinfo", 'site:{d} ext:php intitle:phpinfo'),
    ("dotfiles", 'site:{d} (inurl:".env" OR inurl:".git")'),
    ("uploads dirs", 'site:{d} intitle:"index of" (uploads OR images OR img OR files)'),
    ("emails", 'site:{d} ("@{d}" OR "mailto")'),
    ("swagger / api docs", 'site:{d} (inurl:swagger OR inurl:api-docs OR '
                           'intitle:"api documentation")'),
    ("exposed jenkins", 'site:{d} inurl:"/jenkins" OR intitle:"Dashboard [Jenkins]"'),
    ("grafana / kibana", 'site:{d} (intitle:"Grafana" OR intitle:"Kibana")'),
    ("wordpress files", 'site:{d} (inurl:wp-content OR inurl:wp-includes)'),
    ("gitlab / bitbucket", 'site:{d} (inurl:gitlab OR inurl:bitbucket)'),
    ("reverse proxy pages", 'site:{d} (intitle:"Traefik" OR intitle:"404 Page not found")'),
    ("log files", 'site:{d} ext:log'),
    ("xml / json leaks", 'site:{d} (ext:json OR ext:xml) intext:password'),
    ("admin by title", 'intitle:"{d}" inurl:admin'),
    ("s3 buckets", '"s3.amazonaws.com/{d}" OR "{d}.s3.amazonaws.com"'),
    ("google drive", 'site:drive.google.com "{d}"'),
    ("trello / notion", 'site:{d} (trello.com OR notion.so)'),
    ("jira", 'site:{d} inurl:jira OR intitle:"Jira"'),
    ("confluence", 'site:{d} inurl:confluence OR intitle:"Confluence"'),
    ("ftp links", 'site:{d} "ftp://"'),
    ("telnet / ssh banners", '"{d}" "SSH-2.0" OR "220 "'),
    ("directory listing root", 'site:{d} "Parent Directory"'),
    ("password files", 'site:{d} (inurl:passwd OR inurl:shadow OR inurl:.htpasswd)'),
    ("database files", 'site:{d} (ext:mdb OR ext:sqlite OR ext:db OR ext:dbf)'),
    ("key files", 'site:{d} (ext:pem OR ext:key OR ext:p12 OR ext:pfx OR ext:jks)'),
    ("ci configs", 'site:{d} (.gitlab-ci.yml OR Jenkinsfile OR .travis.yml OR '
                   'circleci OR .github/workflows)'),
    ("terraform state", 'site:{d} terraform.tfstate'),
    ("docker files", 'site:{d} (Dockerfile OR docker-compose.yml)'),
    ("kubernetes", 'site:{d} (kubeconfig OR deployment.yaml OR service.yaml)'),
    ("graphql", 'site:{d} (graphql OR graphiql)'),
    ("elasticsearch", 'site:{d} "_cluster/health" OR "cluster_name"'),
    ("kibana dashboards", 'site:{d} inurl:app/kibana'),
    ("wordpress users", 'site:{d} inurl:author'),
    ("feed leaks", 'site:{d} (ext:rss OR ext:atom OR inurl:feed)'),
    ("robots disallow", 'site:{d} inurl:robots.txt "Disallow"'),
    ("sitemap", 'site:{d} inurl:sitemap.xml'),
    ("old versions", 'site:{d} (inurl:v1 OR inurl:v2 OR inurl:old OR inurl:legacy)'),
    ("staging subdomain", 'site:{d} (inurl:staging OR inurl:test OR inurl:dev)'),
    ("credentials", 'site:{d} ("username" OR "password" OR "login") ext:txt'),
    ("csv exports", 'site:{d} ext:csv'),
    ("xls exports", 'site:{d} (ext:xls OR ext:xlsx)'),
    ("doc leaks", 'site:{d} (ext:doc OR ext:docx OR ext:ppt OR ext:pptx)'),
    ("invoice / receipt", 'site:{d} (intitle:invoice OR intitle:receipt)'),
    ("error logs stack", 'site:{d} "Traceback (most recent call last)"'),
    ("django debug", 'site:{d} ("DisallowedHost" OR "DEBUG = True")'),
    ("laravel debug", 'site:{d} ("Whoops" OR "Laravel")'),
    ("spring boot actuator", 'site:{d} inurl:actuator'),
    ("tomcat manager", 'site:{d} inurl:manager/html'),
    ("cpanel", 'site:{d} inurl:2082 OR inurl:2083 OR inurl:cpanel'),
    ("webmail", 'site:{d} (inurl:webmail OR inurl:roundcube OR inurl:squirrelmail)'),
]


def mod_dork_cannon():
    domain = ask("domain", "example.com")
    print()
    for i, (n, _) in enumerate(DORK_PRESETS, 1):
        print(f"    {fg(TH['key'])}[{i:>2}]{RESET} {fg(TH['text'])}{n}{RESET}")
    print()
    pick = ask("preset number / 'all' / raw query", "1")
    queries = []
    if pick.lower() == "all":
        queries = [(n, t.format(d=domain)) for n, t in DORK_PRESETS]
    elif pick.isdigit() and 1 <= int(pick) <= len(DORK_PRESETS):
        queries = [(DORK_PRESETS[int(pick) - 1][0],
                    DORK_PRESETS[int(pick) - 1][1].format(d=domain))]
    else:
        queries = [("custom", pick)]
    for name, q in queries:
        print()
        rule(name.upper())
        inf("dork: " + q)
        for lbl, base in (("google", "https://www.google.com/search?q="),
                          ("bing", "https://www.bing.com/search?q="),
                          ("ddg", "https://duckduckgo.com/?q=")):
            kv(lbl, base + urllib.parse.quote(q), 8)
        if len(queries) == 1 and ask("run it now? (y/n)", "y").lower().startswith("y"):
            spin("querying search engines")
            res = ddg(q) or mojeek(q)
            if not res:
                bad("no results (engines may be rate limiting)")
            for t, u in res:
                print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:72]}{RESET}")
                print(f"      {fg(TH['dim'])}{u[:104]}{RESET}")
            if res:
                save_json(f"wt_dork_{safe_name(domain)}.json",
                          [{"title": t, "url": u} for t, u in res])


def mod_omni_search():
    q = ask("query")
    if not q:
        return
    for engine, fn in (("duckduckgo", ddg), ("mojeek", mojeek), ("searx", searx)):
        print()
        rule(engine.upper())
        try:
            res = fn(q, 12)
        except Exception:
            res = []
        if not res:
            bad("nothing returned")
        for t, u in res:
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:72]}{RESET}")
            print(f"      {fg(TH['dim'])}{u[:104]}{RESET}")


SITES = [
    {"n": "GitHub", "u": "https://api.github.com/users/{}", "k": "json", "f": [
        ("name", "name"), ("bio", "bio"), ("company", "company"), ("location", "location"),
        ("blog", "blog"), ("followers", "followers"), ("public_repos", "public_repos"),
        ("created", "created_at"), ("id", "id")]},
    {"n": "GitLab", "u": "https://gitlab.com/api/v4/users?username={}", "k": "json",
     "list": True, "f": [("name", "name"), ("state", "state"), ("created", "created_at")]},
    {"n": "Codeberg", "u": "https://codeberg.org/api/v1/users/{}", "k": "json",
     "f": [("full name", "full_name"), ("location", "location"), ("created", "created")]},
    {"n": "Bitbucket", "u": "https://api.bitbucket.org/2.0/users/{}", "k": "json",
     "f": [("display name", "display_name"), ("created", "created_on"), ("type", "type")]},
    {"n": "Launchpad", "u": "https://api.launchpad.net/1.0/~{}", "k": "json",
     "f": [("name", "display_name"), ("karma", "karma"), ("created", "date_created")]},
    {"n": "Sourcehut", "u": "https://meta.sr.ht/~{}.json", "k": "json",
     "f": [("name", "name"), ("created", "created")]},
    {"n": "Replit", "u": "https://replit.com/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "CodePen", "u": "https://codepen.io/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "StackOverflow",
     "u": "https://api.stackexchange.com/2.3/users?inname={}&site=stackoverflow",
     "k": "json", "sub": "items", "list": True,
     "f": [("reputation", "reputation"), ("link", "link"), ("created", "creation_date")]},
    {"n": "HackerNews", "u": "https://hacker-news.firebaseio.com/v0/user/{}.json",
     "k": "json", "f": [("karma", "karma"), ("created", "created"), ("about", "about")]},
    {"n": "Dev.to", "u": "https://dev.to/api/users/by_username?url={}", "k": "json",
     "f": [("name", "name"), ("summary", "summary"), ("joined", "joined_at")]},
    {"n": "Codeforces", "u": "https://codeforces.com/api/user.info?handles={}", "k": "json",
     "sub": "result", "list": True,
     "f": [("rank", "rank"), ("rating", "rating"), ("max rating", "maxRating"),
           ("country", "country")]},
    {"n": "CodeWars", "u": "https://www.codewars.com/api/v1/users/{}", "k": "json",
     "f": [("name", "name"), ("clan", "clan"), ("rank", "ranks.overall.name"),
           ("honor", "honor")]},
    {"n": "HackerRank",
     "u": "https://www.hackerrank.com/rest/contests/master/hackers/{}/profile",
     "k": "json", "sub": "model",
     "f": [("name", "name"), ("country", "country"), ("school", "school"),
           ("level", "level")]},
    {"n": "LeetCode", "u": "https://leetcode.com/graphql", "k": "post",
     "body": {"query": "query($u:String!){matchedUser(username:$u){username "
                       "profile{realName aboutMe ranking reputation}}}",
              "variables": {"u": "{u}"}},
     "f": [("name", "data.matchedUser.profile.realName"),
           ("about", "data.matchedUser.profile.aboutMe"),
           ("rank", "data.matchedUser.profile.ranking"),
           ("reputation", "data.matchedUser.profile.reputation")]},
    {"n": "TryHackMe", "u": "https://tryhackme.com/p/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")], "nf": ["not found", "404"]},
    {"n": "HackTheBox", "u": "https://app.hackthebox.com/users/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Exercism", "u": "https://exercism.org/profiles/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")], "nf": ["page not found"]},
    {"n": "CodeChef", "u": "https://www.codechef.com/users/{}", "k": "status",
     "f": [("title", "og:title")], "nf": ["user not found"]},
    {"n": "AtCoder", "u": "https://atcoder.jp/users/{}", "k": "status",
     "f": [("title", "og:title")], "nf": ["not found"]},
    {"n": "GeeksforGeeks", "u": "https://www.geeksforgeeks.org/user/{}/", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "DockerHub", "u": "https://hub.docker.com/v2/users/{}/", "k": "json",
     "f": [("name", "full_name"), ("company", "company"), ("location", "location"),
           ("joined", "date_joined")]},
    {"n": "npm", "u": "https://registry.npmjs.org/-/user/org.couchdb.user:{}", "k": "json",
     "f": [("name", "name"), ("email", "email")]},
    {"n": "Crates.io", "u": "https://crates.io/api/v1/users/{}", "k": "json",
     "f": [("name", "name"), ("url", "url")]},
    {"n": "PyPI", "u": "https://pypi.org/user/{}/", "k": "status",
     "f": [("title", "og:title")], "nf": ["page not found"]},
    {"n": "Keybase", "u": "https://keybase.io/_/api/1.0/user/lookup.json?username={}",
     "k": "json", "sub": "them.0",
     "f": [("full name", "profile.full_name"), ("bio", "profile.bio"),
           ("location", "profile.location")]},
    {"n": "Reddit", "u": "https://www.reddit.com/user/{}/about.json", "k": "json",
     "sub": "data",
     "f": [("karma", "total_karma"), ("created", "created_utc"), ("verified", "verified")]},
    {"n": "Bluesky",
     "u": "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={}.bsky.social",
     "k": "json", "f": [("handle", "handle"), ("bio", "description"),
                        ("followers", "followersCount"), ("created", "createdAt")]},
    {"n": "Mastodon", "u": "https://mastodon.social/api/v1/accounts/lookup?acct={}",
     "k": "json", "f": [("display name", "display_name"), ("note", "note"),
                        ("followers", "followers_count"), ("created", "created_at")]},
    {"n": "FxTwitter", "u": "https://api.fxtwitter.com/{}", "k": "json", "sub": "user",
     "f": [("name", "name"), ("bio", "description"), ("followers", "followers"),
           ("following", "following"), ("tweets", "tweets"), ("joined", "joined")]},
    {"n": "Telegram", "u": "https://t.me/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Instagram", "u": "https://www.instagram.com/{}/", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Threads", "u": "https://www.threads.net/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "TikTok", "u": "https://www.tiktok.com/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")],
     "nf": ["couldn't find this account"]},
    {"n": "Pinterest", "u": "https://www.pinterest.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "VK", "u": "https://vk.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Truth Social", "u": "https://truthsocial.com/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Minds", "u": "https://www.minds.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Rumble", "u": "https://rumble.com/user/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Odysee", "u": "https://odysee.com/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Kick", "u": "https://kick.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Twitch", "u": "https://api.ivr.fi/v2/twitch/user?login={}", "k": "json",
     "list": True,
     "f": [("display name", "displayName"), ("id", "id"), ("created", "createdAt"),
           ("followers", "followers")]},
    {"n": "Steam", "u": "https://steamcommunity.com/id/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Roblox", "u": "https://www.roblox.com/user.aspx?username={}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Snapchat", "u": "https://www.snapchat.com/add/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Medium", "u": "https://medium.com/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")], "nf": ["404"]},
    {"n": "Substack", "u": "https://{}.substack.com", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "SoundCloud", "u": "https://soundcloud.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Bandcamp", "u": "https://bandcamp.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Mixcloud", "u": "https://www.mixcloud.com/{}/", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Last.fm", "u": "https://www.last.fm/user/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Spotify", "u": "https://open.spotify.com/user/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Vimeo", "u": "https://vimeo.com/api/v2/{}/info.json", "k": "json",
     "f": [("name", "display_name"), ("bio", "bio"), ("url", "profile_url")]},
    {"n": "Behance", "u": "https://www.behance.net/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Dribbble", "u": "https://dribbble.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "DeviantArt", "u": "https://www.deviantart.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "ArtStation", "u": "https://www.artstation.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Flickr", "u": "https://www.flickr.com/people/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "500px", "u": "https://500px.com/p/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Unsplash", "u": "https://unsplash.com/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Imgur", "u": "https://imgur.com/user/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Goodreads", "u": "https://www.goodreads.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Wattpad", "u": "https://www.wattpad.com/user/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Letterboxd", "u": "https://letterboxd.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Trakt", "u": "https://trakt.tv/users/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "MyAnimeList", "u": "https://myanimelist.net/profile/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "AniList", "u": "https://graphql.anilist.co", "k": "graphql",
     "f": [("name", "data.User.name"), ("about", "data.User.about"),
           ("created", "data.User.createdAt")]},
    {"n": "Lichess", "u": "https://lichess.org/api/user/{}", "k": "json",
     "f": [("username", "username"), ("title", "title"), ("created", "createdAt")]},
    {"n": "Chess.com", "u": "https://api.chess.com/pub/player/{}", "k": "json",
     "f": [("name", "name"), ("country", "country"), ("joined", "joined")]},
    {"n": "Duolingo", "u": "https://www.duolingo.com/2017-06-30/users?username={}",
     "k": "json", "sub": "users", "list": True,
     "f": [("name", "name"), ("streak", "streak"), ("created", "createdAt")]},
    {"n": "Kaggle", "u": "https://www.kaggle.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Patreon", "u": "https://www.patreon.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Ko-fi", "u": "https://ko-fi.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "BuyMeACoffee", "u": "https://www.buymeacoffee.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Gumroad", "u": "https://{}.gumroad.com", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Fiverr", "u": "https://www.fiverr.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "ProductHunt", "u": "https://www.producthunt.com/@{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "PayPal.me", "u": "https://www.paypal.com/paypalme/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Venmo", "u": "https://account.venmo.com/u/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "TradingView", "u": "https://www.tradingview.com/u/{}/", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Linktree", "u": "https://linktr.ee/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "About.me", "u": "https://about.me/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "SlideShare", "u": "https://www.slideshare.net/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Scribd", "u": "https://www.scribd.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Issuu", "u": "https://issuu.com/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "HackerEarth", "u": "https://www.hackerearth.com/@{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "TopCoder", "u": "https://www.topcoder.com/members/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "BitcoinTalk", "u": "https://bitcointalk.org/index.php?action=profile;u={}",
     "k": "status", "f": [("title", "og:title")]},
    {"n": "RubyGems", "u": "https://rubygems.org/profiles/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Packagist", "u": "https://packagist.org/packages/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "NuGet", "u": "https://www.nuget.org/profiles/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "HuggingFace", "u": "https://huggingface.co/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "OpenStreetMap", "u": "https://www.openstreetmap.org/user/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Strava", "u": "https://www.strava.com/athletes/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Untappd", "u": "https://untappd.com/user/{}", "k": "status",
     "f": [("title", "og:title"), ("bio", "og:description")]},
    {"n": "Xbox", "u": "https://xboxgamertag.com/search/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "PSNProfiles", "u": "https://psnprofiles.com/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "MinecraftUUID", "u": "https://api.mojang.com/users/profiles/minecraft/{}",
     "k": "json", "f": [("name", "name"), ("uuid", "id")]},
    {"n": "Speedrun", "u": "https://www.speedrun.com/user/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "BoardGameGeek", "u": "https://boardgamegeek.com/user/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Discogs", "u": "https://www.discogs.com/user/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "ReverbNation", "u": "https://www.reverbnation.com/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Flipboard", "u": "https://flipboard.com/@{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Trello", "u": "https://trello.com/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Notion", "u": "https://notion.so/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Beacons", "u": "https://beacons.ai/{}", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Carrd", "u": "https://{}.carrd.co", "k": "status",
     "f": [("title", "og:title")]},
    {"n": "Gitbook", "u": "https://{}.gitbook.io", "k": "status",
     "f": [("title", "og:title")]},
]


def dig(d, path):
    cur = d
    for part in str(path).split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except Exception:
                return None
        elif isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
        if cur is None:
            return None
    return cur


def _subst(o, user):
    if isinstance(o, str):
        return o.replace("{u}", user)
    if isinstance(o, dict):
        return {k: _subst(v, user) for k, v in o.items()}
    if isinstance(o, list):
        return [_subst(v, user) for v in o]
    return o


def check_site(site, user):
    kind = site.get("k", "json")
    if kind == "graphql":
        st, body, _ = http_post("https://graphql.anilist.co", {
            "query": "query($n:String){User(name:$n){name about createdAt siteUrl}}",
            "variables": {"n": user}}, timeout=14)
    elif kind == "post":
        st, body, _ = http_post(site["u"], _subst(site["body"], user), timeout=14,
                                headers={"Referer": "https://leetcode.com/"})
    else:
        st, body, _ = http_get(site["u"].format(user), timeout=13, max_bytes=250000,
                               headers={"Accept": "application/json, text/html"})
    if st is None:
        return None, {}
    if st == 404:
        return False, {}
    if st in (403, 429, 503):
        return None, {}
    if st not in (200, 201):
        return None, {}
    info = {}
    if kind in ("json", "graphql", "post"):
        d = jload(body)
        if not d:
            return None, {}
        if site.get("sub"):
            d = dig(d, site["sub"])
        if site.get("list"):
            d = d[0] if isinstance(d, list) and d else {}
        if not d:
            return False, {}
        for label, path in site.get("f", []):
            v = dig(d, path)
            if isinstance(v, (str, int, float)) and str(v) not in ("", "None"):
                info[label] = str(v)[:140]
        if not info:
            return False, {}
        return True, info
    html = body.decode("utf-8", "replace")
    for marker in site.get("nf", []):
        if marker.lower() in html.lower():
            return False, {}
    for label, prop in site.get("f", []):
        m = re.search(r'<meta[^>]+(?:property|name)=["\']' + re.escape(prop) +
                      r'["\'][^>]*content=["\']([^"\']*)', html, re.I)
        if m:
            v = htmlmod.unescape(m.group(1)).strip()
            if v:
                info[label] = v[:140]
    if not info:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        if m:
            t = strip_tags(m.group(1))[:120]
            if t and "404" not in t:
                info["title"] = t
            else:
                return False, {}
    return True, info


def mod_handle_trace():
    user = ask("username")
    if not user:
        return
    inf(f"hunting {user} across {len(SITES)} platforms")
    hits, misses, errs = [], [], 0
    pg = Progress(len(SITES), "hunting")
    with ThreadPoolExecutor(max_workers=32) as ex:
        futs = {ex.submit(check_site, s, user): s for s in SITES}
        for fut in as_completed(futs):
            pg.update()
            site = futs[fut]
            try:
                found, info = fut.result()
            except Exception:
                errs += 1
                continue
            if found is True:
                hits.append({"site": site["n"], "info": info})
                LIVE["hits"] += 1
                FXS.ping(0.08)
                pg.line()
                url = (site["n"].lower() + ".com" if site.get("k") in ("graphql", "post")
                       else site["u"].format(user))
                ok(f"{site['n']:<16} {url}")
                for k, v in list(info.items())[:5]:
                    if k not in ("id",):
                        print(f"       {fg(TH['dim'])}{k}: {str(v)[:88]}{RESET}")
            elif found is False:
                misses.append(site["n"])
            else:
                errs += 1
    pg.done()
    inf(f"{len(hits)} hit(s) · {len(misses)} miss · {errs} inconclusive")
    if misses:
        bad("not found: " + ", ".join(sorted(misses)[:60]))
    if hits:
        save_json(f"wt_user_{safe_name(user)}.json", hits)


DISPOSABLE = {"mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com",
              "trashmail.com", "yopmail.com", "sharklasers.com", "getnada.com",
              "maildrop.cc", "temp-mail.org", "dispostable.com", "fakeinbox.com",
              "mohmal.com", "1secmail.com", "mail.tm", "mail.gw", "inboxes.com",
              "tempmail.lol", "emailondeck.com", "guerrillamailblock.com", "grr.la",
              "spam4.me", "tempr.email", "mytemp.email", "burnermail.io",
              "mailnesia.com", "mailsac.com", "harakirimail.com", "mailcatch.com"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def mx_records(domain):
    out = []
    for rec in doh(domain, "MX"):
        parts = rec.split()
        if len(parts) >= 2:
            out.append(parts[-1].rstrip("."))
    return out


def provider_of(mx):
    j = " ".join(mx).lower()
    for k, lbl in [("google", "Google Workspace"), ("outlook", "Microsoft 365"),
                   ("zoho", "Zoho"), ("yandex", "Yandex"), ("proton", "Proton"),
                   ("icloud", "Apple iCloud"), ("mimecast", "Mimecast"),
                   ("pphosted", "Proofpoint"), ("secureserver", "GoDaddy"),
                   ("hostinger", "Hostinger"), ("ionos", "IONOS"), ("mailgun", "Mailgun"),
                   ("sendgrid", "SendGrid"), ("amazonses", "Amazon SES"),
                   ("fastmail", "Fastmail"), ("qq.com", "Tencent"), ("163.com", "NetEase"),
                   ("mail.ru", "Mail.ru"), ("gandi", "Gandi"), ("ovh", "OVH"),
                   ("titan", "Titan"), ("rackspace", "Rackspace"), ("barracuda", "Barracuda"),
                   ("messagingengine", "Fastmail"), ("improvmx", "ImprovMX"),
                   ("forwardemail", "ForwardEmail"), ("cloudflare", "Cloudflare Email")]:
        if k in j:
            return lbl
    return "unknown / self-hosted"


def gravatar(email):
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    d = get_json(f"https://gravatar.com/{h}.json", timeout=10)
    return (d.get("entry", [{}])[0] if d and d.get("entry") else None), h


def dnsbl(ip):
    rev = ".".join(reversed(ip.split(".")))
    hits = []
    for zone, label in (("zen.spamhaus.org", "Spamhaus"), ("bl.spamcop.net", "SpamCop"),
                        ("b.barracudacentral.org", "Barracuda"),
                        ("dnsbl.sorbs.net", "SORBS"),
                        ("ubl.unsubscore.com", "Lashback"),
                        ("cbl.abuseat.org", "CBL"),
                        ("dnsbl-1.uceprotect.net", "UCEPROTECT-1"),
                        ("psbl.surriel.com", "PSBL")):
        if doh(f"{rev}.{zone}", "A"):
            hits.append(label)
    return hits


def _p_firefox(email):
    st, b, _ = http_post("https://api.accounts.firefox.com/v1/account/status",
                         {"email": email}, timeout=12)
    d = jload(b) or {}
    if "exists" in d:
        return bool(d["exists"]), "mozilla / firefox account"
    return None, ""


def _p_microsoft(email):
    st, b, _ = http_post("https://login.microsoftonline.com/common/GetCredentialType",
                         {"Username": email, "isOtherIdpSupported": True,
                          "checkPhones": False, "isRemoteNGCSupported": True,
                          "isCookieBannerShown": False, "isFidoSupported": True},
                         timeout=12,
                         headers={"Origin": "https://login.microsoftonline.com"})
    d = jload(b) or {}
    if "IfExistsResult" in d:
        code = d["IfExistsResult"]
        return code == 0, f"GetCredentialType IfExistsResult={code}"
    return None, ""


def _p_wordpress(email):
    st, b, _ = http_get("https://public-api.wordpress.com/rest/v1.1/users/" +
                        urllib.parse.quote(email) + "/auth-options", timeout=12)
    if st == 200:
        return True, "wordpress.com account"
    if st == 404:
        return False, ""
    return None, ""


def _p_imgur(email):
    st, b, _ = http_get("https://api.imgur.com/account/v1/accounts/" +
                        urllib.parse.quote(email) +
                        "?client_id=546c25a59c58ad7", timeout=12)
    if st == 200:
        d = jload(b) or {}
        return True, f"imgur (user={d.get('url', '?')})"
    if st == 404:
        return False, ""
    return None, ""


def _p_duolingo(email):
    st, b, _ = http_get("https://www.duolingo.com/2017-06-30/users?email=" +
                        urllib.parse.quote(email), timeout=15)
    d = jload(b) or {}
    users = d.get("users") or []
    if users:
        return True, f"duolingo (id={users[0].get('id', '?')})"
    if st == 200:
        return False, ""
    return None, ""


def _p_pinterest(email):
    url = ("https://www.pinterest.com/resource/EmailExistsResource/get/"
           "?source_url=%2F&data=%7B%22options%22%3A%7B%22email%22%3A%22" +
           urllib.parse.quote(email) + "%22%7D%7D")
    st, b, _ = http_get(url, timeout=15, headers={"Accept": "application/json"})
    d = jload(b) or {}
    try:
        val = d["resource_response"]["data"]
        if isinstance(val, bool):
            return val, "pinterest"
        if isinstance(val, dict) and "exists" in val:
            return bool(val["exists"]), "pinterest"
    except Exception:
        pass
    return None, ""


def _p_adobe(email):
    st, b, _ = http_get("https://auth.services.adobe.com/signup/v2/webexists"
                        "?username=" + urllib.parse.quote(email), timeout=15)
    d = jload(b) or {}
    if "emailExists" in d:
        return bool(d["emailExists"]), "adobe account"
    if d.get("status") == 200:
        return True, "adobe account"
    if st == 404:
        return False, ""
    return None, ""


def _p_spotify(email):
    st, b, _ = http_get("https://www.spotify.com/api/signup/valid/username"
                        "?username=" + urllib.parse.quote(email), timeout=15)
    d = jload(b) or {}
    r = str(d.get("result", "")).lower()
    if r in ("ok", "valid"):
        return False, "spotify (username free -> not registered)"
    if r:
        return True, "spotify (username taken -> registered)"
    return None, ""


def _p_twitter(email):
    st, b, _ = http_get("https://api.twitter.com/i/users/email_available.json"
                        "?email=" + urllib.parse.quote(email), timeout=15)
    d = jload(b) or {}
    if "valid" in d:
        return (not d["valid"]), "x / twitter"
    return None, ""


def _p_pornhub(email):
    st, b, _ = http_get("https://www.pornhub.com/api/v2/user/check_username"
                        "?username=" + urllib.parse.quote(email), timeout=15)
    d = jload(b) or {}
    if d.get("username") is not None or "valid" in d:
        taken = bool(d.get("username")) or not d.get("valid", True)
        return taken, "pornhub"
    return None, ""


def _p_codecademy(email):
    st, b, _ = http_get("https://www.codecademy.com/api/v1/users?email=" +
                        urllib.parse.quote(email), timeout=15)
    d = jload(b) or {}
    if isinstance(d, dict) and "users" in d:
        return bool(d["users"]), "codecademy"
    return None, ""


def _p_snapchat(email):
    st, b, _ = http_get("https://accounts.snapchat.com/accounts/get_username_suggestions"
                        "?requested_username=&email=" + urllib.parse.quote(email),
                        timeout=15)
    d = jload(b) or {}
    if "signup_username" in d or "requested_username" in d:
        return bool(d.get("signup_username")), "snapchat"
    return None, ""


def _p_envato(email):
    st, b, _ = http_get("https://account.envato.com/api/v1/check_username?username=" +
                        urllib.parse.quote(email), timeout=15)
    d = jload(b) or {}
    if "available" in d:
        return (not d["available"]), "envato"
    return None, ""


def _p_discord(email):
    st, b, _ = http_post("https://discord.com/api/v9/auth/register", {
        "email": email, "username": "wt" + hashlib.md5(email.encode()).hexdigest()[:8],
        "password": "Wt!1234567890", "captcha_key": None, "consent": True}, timeout=15)
    d = jload(b) or {}
    if d.get("token"):
        return False, "discord (register succeeded -> not registered)"
    errs = json.dumps(d.get("errors", d)).lower()
    if "already" in errs or "registered" in errs or "email" in errs:
        return True, "discord (email already registered)"
    return None, ""


def _p_gravatar(email):
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    d = get_json(f"https://gravatar.com/{h}.json", timeout=12)
    return bool(d and d.get("entry")), "gravatar profile"


def _p_hibp(email):
    st, b, _ = http_get("https://haveibeenpwned.com/api/v3/breachedaccount/" +
                        urllib.parse.quote(email) + "?truncateResponse=true",
                        timeout=20, headers={"user-agent": "whitetiger/1.0"})
    if st == 200:
        d = jload(b) or []
        return True, f"breached in {len(d)} breach(es)"
    if st == 404:
        return False, "hibp: no breaches"
    if st == 429:
        return None, "hibp: rate limited"
    return None, ""


SIGNUP_PROBES = [
    ("Microsoft", _p_microsoft), ("Mozilla", _p_firefox),
    ("WordPress.com", _p_wordpress), ("Imgur", _p_imgur),
    ("Duolingo", _p_duolingo), ("Pinterest", _p_pinterest),
    ("Adobe", _p_adobe), ("Spotify", _p_spotify), ("X / Twitter", _p_twitter),
    ("Pornhub", _p_pornhub), ("Codecademy", _p_codecademy),
    ("Snapchat", _p_snapchat), ("Envato", _p_envato), ("Discord", _p_discord),
    ("Gravatar", _p_gravatar), ("HIBP", _p_hibp),
]


def signup_probe(email, show_negatives=True):
    out = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fn, email): name for name, fn in SIGNUP_PROBES}
        for fut in as_completed(futs):
            name = futs[fut]
            try:
                verdict, detail = fut.result()
            except Exception:
                verdict, detail = None, ""
            out.append((name, verdict, detail))
    order = {n: i for i, (n, _) in enumerate(SIGNUP_PROBES)}
    out.sort(key=lambda x: (0 if x[1] is True else 1 if x[1] is None else 2,
                            order.get(x[0], 99)))
    for name, verdict, detail in out:
        if verdict is True:
            print(f"  {sev_tag('medium')} {name:<15} REGISTERED   "
                  f"{fg(TH['dim'])}{detail}{RESET}")
            LIVE["hits"] += 1
        elif verdict is None:
            if show_negatives:
                print(f"  {fg(TH['dim'])}  {name:<15} unknown      {detail}{RESET}")
        elif show_negatives:
            print(f"  {fg(TH['dim'])}  {name:<15} not present{RESET}")
    return out


def emailrep(email):
    st, b, _ = http_get("https://emailrep.io/" + urllib.parse.quote(email), timeout=15,
                        headers={"User-Agent": "whitetiger/1.0",
                                 "Accept": "application/json"})
    if st != 200:
        return None
    return jload(b)


def mod_mail_xray():
    email = ask("email address")
    if not email or not EMAIL_RE.fullmatch(email):
        bad("invalid syntax")
        return
    local, domain = email.split("@")
    kv("address", email.lower())
    kv("local part", local)
    kv("domain", domain)
    mxs = mx_records(domain)
    kv("mx", ", ".join(mxs) if mxs else "NONE — cannot receive mail")
    kv("provider", provider_of(mxs))
    kv("disposable", "yes" if domain in DISPOSABLE else "no")

    prof, gh = gravatar(email)
    print()
    rule("GRAVATAR")
    if prof:
        LIVE["hits"] += 1
        for k in ("displayName", "name", "aboutMe", "currentLocation", "job_title",
                  "company", "pronouns"):
            if prof.get(k):
                kv(k, str(prof[k])[:140])
        for acc in (prof.get("accounts") or [])[:15]:
            kv(acc.get("shortname", "link"), acc.get("url", "")[:100])
        kv("avatar", f"https://www.gravatar.com/avatar/{gh}")
    else:
        bad("no gravatar profile")
        kv("avatar hash", gh)

    print()
    rule("REPUTATION (emailrep)")
    er = emailrep(email)
    if er:
        kv("reputation", er.get("reputation"))
        kv("suspicious", er.get("suspicious"))
        kv("references", er.get("references"))
        kv("blacklisted", er.get("blacklisted"))
        det = er.get("details") or {}
        for k in ("deliverable", "domain_exists", "valid_mx", "spoofable",
                  "spf_strict", "dmarc_enforced", "free_provider", "disposable",
                  "accept_all", "first_seen", "last_seen"):
            if det.get(k) not in (None, [], ""):
                v = det[k]
                kv(k, ", ".join(str(x) for x in v) if isinstance(v, list) else str(v)[:150])
        profs = det.get("profiles") or er.get("profiles") or []
        if profs:
            print()
            hit("profiles seen on:")
            for p in profs[:25]:
                print(f"    {fg(TH['text'])}· {str(p)[:110]}{RESET}")
            LIVE["hits"] += len(profs)
    else:
        bad("emailrep unreachable / rate limited")

    print()
    rule("WHERE THEY ARE SIGNED IN (live account probes)")
    signup_probe(email)

    print()
    rule("BREACHES (xposedornot)")
    d = get_json("https://api.xposedornot.com/v1/breach-analytics?email=" +
                 urllib.parse.quote(email), timeout=20)
    bl = ((d.get("ExposedBreaches") or {}).get("breaches_details") or
          d.get("breaches")) if d else None
    if bl:
        LIVE["hits"] += len(bl)
        kv("breaches found", len(bl))
        for b in bl[:25]:
            if isinstance(b, dict):
                print(f"    {fg((255,140,120))}·{RESET} {fg(TH['text'])}"
                      f"{str(b.get('breach','?'))[:38]:<38}{RESET} "
                      f"{fg(TH['dim'])}{b.get('xposed_date','')} · "
                      f"{str(b.get('xposed_data',''))[:44]}{RESET}")
            else:
                print(f"    {fg((255,140,120))}·{RESET} {fg(TH['text'])}{b}{RESET}")
    else:
        bad("no breach data (or clean)")

    recs = dns_all(domain)
    print()
    rule("DOMAIN DNS")
    for t, vals in recs.items():
        for v in vals[:5]:
            kv(t, v[:120])
    kv("spf", "present" if any("v=spf1" in t for t in recs.get("TXT", [])) else "MISSING")
    kv("dmarc", "present" if doh("_dmarc." + domain, "TXT") else "MISSING")

    print()
    rule("SEARCH")
    for t, u in ddg(f'"{email}"', 6):
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:70]}{RESET}")
        print(f"      {fg(TH['dim'])}{u[:100]}{RESET}")
    save_json(f"wt_email_{safe_name(domain)}.json",
              {"email": email, "mx": mxs, "dns": recs})


def smtp_verify(mx, email, timeout=12):
    try:
        s = socket.create_connection((mx, 25), timeout=timeout)
    except Exception as e:
        return None, f"connect failed ({e})"
    fh = s.makefile("rb")
    try:
        _sock_line(fh)
        _cmd(s, fh, "EHLO wt.local")
        _cmd(s, fh, "MAIL FROM:<check@wt.local>")
        code = _cmd(s, fh, f"RCPT TO:<{email}>")
        _cmd(s, fh, "QUIT")
        return code[:3], code
    except Exception as e:
        return None, f"error ({e})"
    finally:
        try:
            s.close()
        except Exception:
            pass


def mod_mail_validate():
    email = ask("email address")
    if not email or not EMAIL_RE.fullmatch(email):
        bad("invalid syntax")
        return
    local, domain = email.split("@")
    ok("syntax valid")
    kv("normalised", email.lower())
    mxs = mx_records(domain)
    if not mxs:
        bad("no mx — domain cannot receive mail")
    else:
        kv("mx", ", ".join(mxs))
        kv("provider", provider_of(mxs))
    kv("disposable", "yes" if domain in DISPOSABLE else "no")
    recs = dns_all(domain)
    print()
    rule("DNS")
    for t, vals in recs.items():
        for v in vals[:6]:
            kv(t, v[:120])
    kv("spf", "present" if any("v=spf1" in t for t in recs.get("TXT", [])) else "MISSING")
    kv("dmarc", "present" if doh("_dmarc." + domain, "TXT") else "MISSING")
    prof, gh = gravatar(email)
    kv("gravatar", "profile exists" if prof else "none")
    ips = recs.get("A", [])
    if ips:
        print()
        rule("MAIL HOST")
        for ip in ips[:3]:
            kv("ip", ip)
            kv("  ptr", reverse_dns(ip) or "none")
            kv("  dnsbl", ", ".join(dnsbl(ip)) or "clean")
    if mxs and ask("smtp mailbox probe? (y/n)", "y").lower().startswith("y"):
        inf(f"-> {mxs[0]}:25")
        code, raw = smtp_verify(mxs[0], email)
        if code is None:
            bad(raw)
        elif code.startswith("250"):
            ok(f"mailbox accepted · {raw}")
            LIVE["hits"] += 1
        elif code.startswith("5"):
            bad(f"mailbox rejected · {raw}")
        else:
            wrn(f"inconclusive · {raw}")


def mod_mail_forge():
    first = ask("first name", "john").lower()
    last = ask("last name", "doe").lower()
    domain = ask("domain", "example.com").lower()
    fi, li = first[0], last[0]
    patterns = [
        "{f}", "{l}", "{f}{l}", "{f}.{l}", "{f}_{l}", "{f}-{l}",
        "{l}{f}", "{l}.{f}", "{l}_{f}", "{l}-{f}",
        "{f}{l0}", "{f}.{l0}", "{f}{fi}{l}", "{fi}{l}", "{fi}.{l}",
        "{f}{li}", "{f}.{li}", "{f}{l}{li}", "{l}{fi}", "{l}.{fi}",
        "{fi}{li}", "{fi}.{li}", "{fi}_{li}", "{f}_{l0}", "{f}-{l0}",
        "{f}{l}1", "{f}.{l}.{li}", "info", "contact", "hello", "admin", "mail",
        "office", "sales", "support", "team", "hr", "accounts", "billing",
        "help", "webmaster", "postmaster", "noreply", "no-reply", "jobs", "careers",
    ]
    cands = []
    for p in patterns:
        try:
            addr = p.format(f=first, l=last, fi=fi, li=li, l0=last[:1]) + "@" + domain
        except Exception:
            continue
        if addr not in cands:
            cands.append(addr)
    inf(f"{len(cands)} candidate address(es)")
    for c in cands:
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{c}{RESET}")
    mxs = mx_records(domain)
    if not mxs:
        bad("no mx for that domain — cannot verify")
        return
    if not ask("verify with smtp? (y/n)", "y").lower().startswith("y"):
        return
    print()
    inf(f"probing {mxs[0]}:25")
    valid = []
    pg = Progress(len(cands), "verifying")
    for c in cands:
        pg.update()
        code, raw = smtp_verify(mxs[0], c)
        if code and code.startswith("250"):
            valid.append(c)
            LIVE["hits"] += 1
            pg.line()
            ok(c)
    pg.done()
    inf(f"{len(valid)} valid mailbox(es)")
    if valid:
        save_json(f"wt_perm_{safe_name(domain)}.json", valid)


def mod_ip_oracle():
    target = ask("ip or hostname")
    if not target:
        return
    ip = resolve(target)
    if not ip:
        bad("could not resolve")
        return
    kv("input", target)
    kv("ip", ip)
    try:
        a = ipaddress.ip_address(ip)
        kv("type", f"IPv{a.version} · {'private' if a.is_private else 'public'}")
    except Exception:
        pass
    kv("ptr", reverse_dns(ip) or "none")
    print()
    rule("SHODAN INTERNETDB")
    sd = get_json(f"https://internetdb.shodan.io/{ip}", timeout=12)
    if sd and sd.get("ip"):
        kv("open ports", ", ".join(str(p) for p in sd.get("open_ports", [])) or "none")
        kv("hostnames", ", ".join(sd.get("hostnames", [])[:6]) or "none")
        kv("tags", ", ".join(sd.get("tags", [])) or "none")
        vulns = sd.get("vulns") or []
        if vulns:
            kv("vulns", ", ".join(vulns[:12]))
            LIVE["hits"] += len(vulns)
    else:
        bad("no shodan data")
    print()
    rule("GREYNOISE")
    gn = get_json(f"https://api.greynoise.io/v3/community/{ip}", timeout=12)
    if gn and gn.get("ip"):
        kv("classification", gn.get("classification"))
        kv("name", gn.get("name"))
        kv("last_seen", gn.get("last_seen"))
    else:
        bad("no greynoise data")
    print()
    rule("BGP / ASN")
    bg = get_json(f"https://api.bgpview.io/ip/{ip}", timeout=12)
    if bg and bg.get("data"):
        for pfx in (bg["data"].get("prefixes") or [])[:3]:
            kv("prefix", pfx.get("prefix"))
            kv("  asn", f"AS{pfx.get('asn', {}).get('asn')} "
                       f"{pfx.get('asn', {}).get('name', '')}")
            kv("  desc", (pfx.get("description") or "")[:80])
    else:
        bad("no bgp data")
    print()
    rule("REGISTRY (RDAP)")
    rd = get_json(f"https://rdap.org/ip/{ip}", timeout=14)
    if rd:
        kv("handle", rd.get("handle"))
        kv("name", rd.get("name"))
        kv("country", rd.get("country"))
        for e in rd.get("entities") or []:
            for item in ((e.get("vcardArray") or [None, []])[1] or []):
                try:
                    if item[0] == "email":
                        kv("abuse email", str(item[3])[:60])
                except Exception:
                    pass
    else:
        bad("no rdap data")
    print()
    rule("GEOLOCATION")
    geo = get_json(f"https://ipwho.is/{ip}", timeout=10)
    if geo and geo.get("success"):
        kv("country", f"{geo.get('country')} ({geo.get('country_code')})")
        kv("city", geo.get("city"))
        kv("coords", f"{geo.get('latitude')}, {geo.get('longitude')}")
        kv("timezone", (geo.get("timezone") or {}).get("id"))
        c = geo.get("connection") or {}
        kv("isp", c.get("isp"))
        kv("asn", c.get("asn"))
    else:
        bad("no geo data")
    print()
    rule("REPUTATION")
    kv("dnsbl", ", ".join(dnsbl(ip)) or "clean")
    print()
    rule("REVERSE IP")
    st, body, _ = http_get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}",
                           timeout=20)
    if st == 200 and body and b"error" not in body.lower():
        hosts = [h.strip() for h in body.decode().splitlines() if h.strip()]
        kv("hosts", len(hosts))
        for h in hosts[:25]:
            hit(h)
    print()
    rule("QUICK PORT SCAN")
    with ThreadPoolExecutor(max_workers=25) as ex:
        for p, r in zip(TOP_PORTS, ex.map(lambda p: probe_port(ip, p, 0.8), TOP_PORTS)):
            if r[0]:
                ok(f"{p:<6} {SERVICES.get(p, '')}  {r[1]}")


def crtsh(domain):
    d = get_json(f"https://crt.sh/?q=%25.{urllib.parse.quote(domain)}&output=json",
                 timeout=35)
    subs = set()
    for e in d or []:
        for n in str(e.get("name_value", "")).split("\n"):
            n = n.strip().lower().lstrip("*.")
            if n.endswith(domain) and "@" not in n:
                subs.add(n)
    return subs


def certspotter(domain):
    d = get_json(f"https://api.certspotter.com/v1/issuances?domain={domain}"
                 f"&include_subdomains=true&expand=dns_names", timeout=25)
    subs = set()
    for e in d or []:
        for n in e.get("dns_names", []):
            n = str(n).lower().lstrip("*.")
            if n.endswith(domain):
                subs.add(n)
    return subs


def hackertarget_hosts(domain):
    st, body, _ = http_get(f"https://api.hackertarget.com/hostsearch/?q={domain}",
                           timeout=20)
    subs = set()
    if st == 200 and body and b"error" not in body.lower():
        for line in body.decode("utf-8", "replace").splitlines():
            if "," in line:
                subs.add(line.split(",")[0].strip().lower())
    return subs


def otx_passive(domain):
    d = get_json(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns",
                 timeout=20)
    subs = set()
    for e in (d or {}).get("passive_dns", []):
        h = str(e.get("hostname", "")).lower()
        if h.endswith(domain):
            subs.add(h)
    return subs


def urlscan_domains(domain):
    d = get_json(f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=100",
                 timeout=20)
    subs = set()
    for r in (d or {}).get("results", []):
        h = str((r.get("page") or {}).get("domain", "")).lower()
        if h.endswith(domain):
            subs.add(h)
    return subs


def anubis_subs(domain):
    d = get_json(f"https://jldc.me/anubis/subdomains/{domain}", timeout=20)
    return {s.lower() for s in (d or []) if isinstance(s, str) and s.endswith(domain)}


def rapiddns(domain):
    st, body, _ = http_get(f"https://rapiddns.io/subdomain/{domain}?full=1", timeout=25)
    if not body:
        return set()
    html = body.decode("utf-8", "replace")
    return {m.lower() for m in re.findall(
        r">([a-z0-9_\-.*]+\.%s)<" % re.escape(domain), html, re.I)
        if "@" not in m}


def threatminer_subs(domain):
    d = get_json(f"https://api.threatminer.org/v2/domain.php?q={domain}&rt=2", timeout=20)
    return {str(s).lower() for s in ((d or {}).get("results") or [])
            if isinstance(s, str) and s.endswith(domain)}


def wayback_urls(domain, limit=200):
    d = get_json(f"http://web.archive.org/cdx/search/cdx?url=*.{domain}&output=json"
                 f"&limit={limit}&collapse=urlkey&fl=original", timeout=30)
    out = []
    for row in (d or [])[1:]:
        if row:
            out.append(row[0])
    return out


SUBDOMAIN_WORDS = ["www", "mail", "ftp", "webmail", "smtp", "pop", "ns1", "ns2", "ns3",
                   "dev", "staging", "stage", "test", "testing", "qa", "uat", "pre",
                   "preprod", "prod", "api", "api2", "api-v2", "app", "apps", "portal",
                   "admin", "administrator", "cpanel", "whm", "webdisk", "dashboard",
                   "panel", "blog", "shop", "store", "cdn", "static", "assets", "img",
                   "images", "media", "files", "download", "downloads", "upload",
                   "uploads", "docs", "doc", "wiki", "support", "help", "helpdesk",
                   "status", "monitor", "metrics", "grafana", "kibana", "elastic",
                   "logs", "log", "db", "database", "mysql", "postgres", "redis",
                   "mongo", "cache", "vpn", "remote", "rdp", "ssh", "git", "gitlab",
                   "github", "jenkins", "ci", "cd", "build", "deploy", "docker", "k8s",
                   "kube", "internal", "intranet", "extranet", "partner", "partners",
                   "client", "clients", "vendor", "vendors", "hr", "finance", "legal",
                   "sales", "marketing", "crm", "erp", "sso", "auth", "login", "id",
                   "identity", "accounts", "billing", "pay", "payments", "checkout",
                   "mobile", "m", "wap", "old", "new", "beta", "alpha", "demo", "sandbox",
                   "lab", "labs", "research", "dev1", "dev2", "web1", "web2", "jira",
                   "confluence", "nexus", "artifactory", "sonar", "sentry", "stats",
                   "analytics", "vault", "consul", "kafka", "zookeeper", "solr",
                   "rabbit", "mq", "queue", "worker", "cron", "scheduler", "proxy",
                   "gw", "gateway", "lb", "edge", "origin", "backend", "frontend",
                   "web", "srv", "vm", "host", "node1", "node2", "us", "eu", "asia"]


def mod_sub_spider():
    domain = ask("domain", "example.com").lower().strip()
    inf("querying every passive source in parallel...")
    sources = [("crt.sh", crtsh), ("certspotter", certspotter),
               ("hackertarget", hackertarget_hosts), ("alienvault otx", otx_passive),
               ("urlscan.io", urlscan_domains), ("anubis", anubis_subs),
               ("rapiddns", rapiddns), ("threatminer", threatminer_subs)]
    all_subs = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fn, domain): name for name, fn in sources}
        for fut in as_completed(futs):
            name = futs[fut]
            try:
                found = fut.result()
            except Exception:
                found = set()
            print()
            inf(f"{name}: {len(found)} subdomain(s)")
            for s in sorted(found)[:30]:
                hit(s)
            for s in found:
                all_subs.setdefault(s, []).append(name)
    if ask("also brute force a wordlist? (y/n)", "y").lower().startswith("y"):
        inf(f"brute forcing {len(SUBDOMAIN_WORDS)} names")
        pg = Progress(len(SUBDOMAIN_WORDS), "brute")
        with ThreadPoolExecutor(max_workers=48) as ex:
            futs = {ex.submit(resolve, f"{w}.{domain}"): w for w in SUBDOMAIN_WORDS}
            for fut in as_completed(futs):
                pg.update()
                if fut.result():
                    all_subs.setdefault(f"{futs[fut]}.{domain}", []).append("brute")
        pg.done()
    subs = sorted(all_subs)
    print()
    rule()
    inf(f"{len(subs)} unique subdomain(s)")
    if subs and ask("resolve them all to ip? (y/n)", "y").lower().startswith("y"):
        print()
        with ThreadPoolExecutor(max_workers=32) as ex:
            for s, ip in zip(subs[:300], ex.map(resolve, subs[:300])):
                if ip:
                    ok(f"{s:<44} {ip:<16} {reverse_dns(ip) or ''}")
    if ask("pull historical urls from wayback? (y/n)", "y").lower().startswith("y"):
        print()
        spin("querying wayback machine")
        urls = wayback_urls(domain)
        inf(f"{len(urls)} archived url(s)")
        interesting = [u for u in urls if re.search(
            r"\.(pdf|sql|bak|zip|env|json|xml|txt|log|csv|gz|tar|conf|old)(\?|$)", u, re.I)]
        for u in interesting[:40]:
            hit(u)
    save_json(f"wt_subs_{safe_name(domain)}.json",
              {"subdomains": subs, "sources": {k: v for k, v in all_subs.items()}})


def mod_domain_oracle():
    domain = (ask("domain", "example.com").lower()
              .replace("https://", "").replace("http://", "").strip("/"))
    inf(f"deep scan of {domain}")
    recs = dns_all(domain)
    print()
    rule("DNS")
    if not recs:
        bad("no records")
    for t, vals in recs.items():
        for v in vals[:8]:
            kv(t, v[:130])
    print()
    rule("REGISTRY (RDAP)")
    rd = get_json(f"https://rdap.org/domain/{domain}", timeout=15)
    if rd:
        kv("handle", rd.get("handle"))
        for e in (rd.get("events") or []):
            kv("date " + str(e.get("eventAction")), str(e.get("eventDate", ""))[:10])
        for n in (rd.get("nameservers") or [])[:6]:
            kv("nameserver", str(n.get("ldhName", "")).lower())
        for e in rd.get("entities") or []:
            roles = ",".join(e.get("roles") or [])
            for item in ((e.get("vcardArray") or [None, []])[1] or []):
                try:
                    if item[0] == "fn":
                        kv(f"contact ({roles})", str(item[3])[:60])
                    elif item[0] == "email":
                        kv(f"email ({roles})", str(item[3])[:60])
                except Exception:
                    pass
    else:
        bad("no rdap data")
    print()
    rule("MAIL SECURITY")
    kv("spf", "present" if any("v=spf1" in t for t in recs.get("TXT", [])) else "MISSING")
    kv("dmarc", "present" if doh("_dmarc." + domain, "TXT") else "MISSING")
    for sel in ("default", "google", "selector1", "selector2", "k1", "mail", "dkim", "s1"):
        if doh(f"{sel}._domainkey.{domain}", "TXT"):
            kv("dkim", f"selector '{sel}' found")
            break
    kv("mx", ", ".join(mx_records(domain)) or "none")
    ips = recs.get("A", []) + recs.get("AAAA", [])
    if ips:
        print()
        rule("HOSTING")
        for ip in ips[:4]:
            geo = get_json(f"https://ipwho.is/{ip}", timeout=8)
            if geo and geo.get("success"):
                kv(ip, f"{geo.get('country')} · "
                       f"{(geo.get('connection') or {}).get('isp')}")
            else:
                kv(ip, reverse_dns(ip) or "no ptr")
    print()
    rule("TLS CERTIFICATE")
    ti = tls_info(domain, 443)
    if ti:
        for k, v in ti.items():
            kv("tls " + k, ", ".join(v) if isinstance(v, list) else v)
    else:
        bad("no tls on :443")
    print()
    rule("WEB + SECURITY HEADERS")
    st, body, hdrs = http_get(f"https://{domain}/", timeout=12)
    if st:
        kv("status", st)
        for h in ("server", "x-powered-by", "content-type", "via"):
            if hdrs.get(h):
                kv(h, hdrs[h][:100])
        missing = [lbl for h, lbl in SEC_HEADERS if not hdrs.get(h)]
        kv("security headers",
           "all present" if not missing else "missing: " + ", ".join(missing))
        m = re.search(rb"<title>(.*?)</title>", body, re.S | re.I)
        if m:
            kv("title", strip_tags(m.group(1).decode("utf-8", "replace"))[:80])
    print()
    inf("subdomain sweep...")
    subs = set()
    for fn in (crtsh, certspotter, otx_passive, urlscan_domains, anubis_subs):
        try:
            subs |= fn(domain)
        except Exception:
            pass
    inf(f"{len(subs)} subdomain(s) found")
    for s in sorted(subs)[:50]:
        hit(s)
    save_json(f"wt_domain_{safe_name(domain)}.json",
              {"dns": recs, "subdomains": sorted(subs)})


TECH_SIGS = [("wp-content", "WordPress"), ("/sites/default/files", "Drupal"),
             ("cdn.shopify", "Shopify"), ("__next_data__", "Next.js"), ("_nuxt", "Nuxt"),
             ("/static/js/main.", "React build"), ("jquery", "jQuery"),
             ("bootstrap", "Bootstrap"), ("tailwind", "Tailwind"),
             ("googletagmanager", "Google Tag Manager"), ("gtag(", "Google Analytics"),
             ("fbq(", "Meta Pixel"), ("hotjar", "Hotjar"), ("clarity.ms", "MS Clarity"),
             ("recaptcha", "reCAPTCHA"), ("hcaptcha", "hCaptcha"),
             ("cloudflare", "Cloudflare"), ("svelte", "Svelte"), ("angular", "Angular"),
             ("vue", "Vue.js"), ("drupal-settings-json", "Drupal"), ("joomla", "Joomla"),
             ("magento", "Magento"), ("wix.com", "Wix"), ("squarespace", "Squarespace"),
             ("webflow", "Webflow"), ("ghost.org", "Ghost"), ("hubspot", "HubSpot")]

SOCIAL_RE = re.compile(r"https?://(?:www\.)?(?:twitter\.com|x\.com|facebook\.com|"
                       r"instagram\.com|linkedin\.com|github\.com|youtube\.com|tiktok\.com|"
                       r"t\.me|discord\.gg|reddit\.com|pinterest\.com|threads\.net|"
                       r"bsky\.app|mastodon\.[a-z]+)/[^\s\"'<>)\]]*", re.I)
PHONE_TEL_RE = re.compile(r"tel:([+\d\s\-().]{7,22})", re.I)
SECRET_RE = re.compile(r"(?:api[_-]?key|apikey|secret|token|access[_-]?key)['\"]?\s*[:=]\s*"
                       r"['\"]([A-Za-z0-9_\-]{12,80})['\"]", re.I)


def mod_page_xray():
    url = ask("url", "https://example.com")
    if "://" not in url:
        url = "https://" + url
    inf("deep scraping...")
    st, body, hdrs = http_get(url, timeout=18, max_bytes=2_500_000)
    if st is None:
        bad("unreachable")
        return
    html = body.decode("utf-8", "replace")

    def rx(p):
        m = re.search(p, html, re.S | re.I)
        return htmlmod.unescape(m.group(1)).strip() if m else ""

    kv("url", url)
    kv("status", st)
    kv("size", f"{len(body):,} bytes")
    print()
    rule("PAGE META")
    for lbl, p in (("title", r"<title[^>]*>(.*?)</title>"),
                   ("description",
                    r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)'),
                   ("keywords",
                    r'<meta[^>]+name=["\']keywords["\'][^>]*content=["\']([^"\']*)'),
                   ("author", r'<meta[^>]+name=["\']author["\'][^>]*content=["\']([^"\']*)'),
                   ("generator",
                    r'<meta[^>]+name=["\']generator["\'][^>]*content=["\']([^"\']*)')):
        v = rx(p)
        if v:
            kv(lbl, v[:150])
    print()
    rule("CONTACTS + SOCIALS")
    emails = sorted(set(EMAIL_RE.findall(html)))
    for e in emails[:20]:
        hit(e)
        LIVE["hits"] += 1
    for p in sorted(set(p.strip() for p in PHONE_TEL_RE.findall(html)))[:10]:
        hit("phone " + p)
    socials = sorted(set(SOCIAL_RE.findall(html)))
    for s in socials[:20]:
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{s[:110]}{RESET}")
    print()
    rule("TECH FINGERPRINT")
    tech = set()
    for h, lbl in (("server", "server"), ("x-powered-by", "powered by"),
                   ("x-generator", "generator"), ("cf-ray", "Cloudflare"),
                   ("x-amz-cf-id", "CloudFront"), ("x-vercel-id", "Vercel"),
                   ("x-served-by", "Fastly"), ("x-nf-request-id", "Netlify")):
        if hdrs.get(h):
            tech.add(f"{lbl}: {hdrs[h]}")
    low = html.lower()
    for needle, lbl in TECH_SIGS:
        if needle in low:
            tech.add(lbl)
    for t in sorted(tech):
        kv("·", t[:110])
    print()
    rule("SECURITY HEADERS")
    missing = [lbl for h, lbl in SEC_HEADERS if not hdrs.get(h)]
    if missing:
        wrn("missing: " + ", ".join(missing))
    else:
        ok("all present")
    print()
    rule("ANALYTICS / TRACKING IDS")
    for pat, lbl in ((r"UA-\d{4,10}-\d{1,4}", "Google Analytics UA"),
                     (r"G-[A-Z0-9]{8,12}", "GA4"),
                     (r"GTM-[A-Z0-9]{5,8}", "Google Tag Manager"),
                     (r"fbq\('init',\s*'(\d{10,20})'", "Meta Pixel"),
                     (r"ca-pub-(\d{10,20})", "AdSense")):
        for f in list(set(re.findall(pat, html)))[:4]:
            kv(lbl, str(f)[:60])
    print()
    rule("ASSETS")
    js = sorted(set(re.findall(r'<script[^>]+src=["\']([^"\']+)', html, re.I)))
    css = sorted(set(re.findall(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)', html, re.I)))
    kv("js files", len(js))
    kv("css files", len(css))
    for s in js[:8]:
        bad("  " + s[:100])
    print()
    rule("POSSIBLE SECRETS IN MARKUP")
    for m in list(set(SECRET_RE.findall(html)))[:10]:
        hit(m)
    print()
    rule("HTML COMMENTS")
    for c in re.findall(r"<!--(.*?)-->", html, re.S)[:8]:
        c = strip_tags(c).strip()
        if len(c) > 3:
            bad("  " + c[:110])
    print()
    rule("WAYBACK")
    host = urllib.parse.urlparse(url).netloc
    wb = get_json(f"http://archive.org/wayback/available?url={host}", timeout=15)
    if wb and (wb.get("archived_snapshots") or {}).get("closest"):
        kv("last snapshot", wb["archived_snapshots"]["closest"].get("timestamp", ""))
    else:
        bad("no wayback snapshot")
    save_json(f"wt_page_{safe_name(host)}.json",
              {"url": url, "emails": emails, "socials": socials, "tech": sorted(tech)})


def mod_cert_archive():
    host = ask("hostname", "example.com")
    inf("live handshake...")
    ti = tls_info(host, 443)
    if not ti:
        bad("no tls on :443")
    else:
        rule("LIVE CERTIFICATE")
        for k, v in ti.items():
            kv(k, ", ".join(v) if isinstance(v, list) else v)
    print()
    inf("certificate transparency logs...")
    d = get_json(f"https://crt.sh/?q={urllib.parse.quote(host)}&output=json", timeout=35)
    seen = set()
    if d:
        for e in d[:40]:
            key = (e.get("issuer_name", ""), e.get("not_before", "")[:10])
            if key in seen:
                continue
            seen.add(key)
            print()
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}"
                  f"{e.get('not_before','')[:10]} -> {e.get('not_after','')[:10]}{RESET}")
            print(f"      {fg(TH['dim'])}issuer: {str(e.get('issuer_name',''))[:90]}{RESET}")
            names = str(e.get("name_value", "")).split("\n")[:6]
            print(f"      {fg(TH['dim'])}sans: "
                  f"{', '.join(n.strip() for n in names)[:120]}{RESET}")
    else:
        bad("crt.sh returned nothing")
    print()
    rule("RELATED HOSTS FROM CERT LOGS")
    subs = crtsh(host)
    for s in sorted(subs)[:40]:
        hit(s)
    inf(f"{len(subs)} name(s)")


def _axfr_query(domain):
    qid = random.randint(1, 65535)
    header = struct.pack(">HHHHHH", qid, 0, 1, 0, 0, 0)
    q = b"".join(bytes([len(p)]) + p.encode() for p in domain.split(".")) + b"\x00"
    return header + q + struct.pack(">HH", 252, 1)


def mod_dns_omni():
    domain = ask("domain", "example.com")
    inf("querying all record types")
    recs = dns_all(domain)
    for t, vals in recs.items():
        print()
        rule(t)
        for v in vals[:12]:
            kv("·", v[:140])
    if not recs:
        bad("no records returned")
    print()
    rule("REVERSE LOOKUPS")
    for ip in (recs.get("A", []) or [])[:5]:
        kv(ip, reverse_dns(ip) or "no ptr")
    print()
    rule("ZONE TRANSFER ATTEMPT (AXFR)")
    nss = [n.rstrip(".") for n in recs.get("NS", [])]
    for ns in nss[:3]:
        ip = resolve(ns)
        if not ip:
            continue
        try:
            s = socket.create_connection((ip, 53), timeout=6)
            s.sendall(_axfr_query(domain))
            data = b""
            s.settimeout(4)
            while True:
                try:
                    c = s.recv(4096)
                except Exception:
                    break
                if not c:
                    break
                data += c
            s.close()
            if data:
                names = sorted(set(re.findall(
                    rb"([a-z0-9_\-\.]+\.%s)" % re.escape(domain.encode()), data, re.I)))
                inf(f"{ns}: {len(names)} name(s) in transfer")
                for n in names[:40]:
                    hit(n.decode())
                if names:
                    break
        except Exception:
            pass
    print()
    rule("DNSSEC / CAA")
    kv("caa", ", ".join(recs.get("CAA", [])) or "none")
    ds = doh(domain, "DS")
    kv("dnssec ds", "present" if ds else "not found")
    print()
    rule("COMMON SUBDOMAIN HITS")
    with ThreadPoolExecutor(max_workers=30) as ex:
        futs = {ex.submit(resolve, f"{w}.{domain}"): w for w in SUBDOMAIN_WORDS[:60]}
        for fut in as_completed(futs):
            ip = fut.result()
            if ip:
                hit(f"{futs[fut]}.{domain:<34} {ip}")


CALLING_CODES = {
    "1": "United States / Canada", "7": "Russia / Kazakhstan", "20": "Egypt",
    "27": "South Africa", "30": "Greece", "31": "Netherlands", "32": "Belgium",
    "33": "France", "34": "Spain", "36": "Hungary", "39": "Italy",
    "40": "Romania", "41": "Switzerland", "43": "Austria", "44": "United Kingdom",
    "45": "Denmark", "46": "Sweden", "47": "Norway", "48": "Poland", "49": "Germany",
    "51": "Peru", "52": "Mexico", "53": "Cuba", "54": "Argentina", "55": "Brazil",
    "56": "Chile", "57": "Colombia", "58": "Venezuela", "60": "Malaysia",
    "61": "Australia", "62": "Indonesia", "63": "Philippines", "64": "New Zealand",
    "65": "Singapore", "66": "Thailand", "81": "Japan", "82": "South Korea",
    "84": "Vietnam", "86": "China", "90": "Turkey", "91": "India", "92": "Pakistan",
    "93": "Afghanistan", "94": "Sri Lanka", "95": "Myanmar", "98": "Iran",
    "212": "Morocco", "213": "Algeria", "216": "Tunisia", "218": "Libya",
    "220": "Gambia", "221": "Senegal", "233": "Ghana", "234": "Nigeria",
    "254": "Kenya", "255": "Tanzania", "256": "Uganda", "260": "Zambia",
    "263": "Zimbabwe", "264": "Namibia", "265": "Malawi", "351": "Portugal",
    "352": "Luxembourg", "353": "Ireland", "354": "Iceland", "355": "Albania",
    "356": "Malta", "357": "Cyprus", "358": "Finland", "359": "Bulgaria",
    "370": "Lithuania", "371": "Latvia", "372": "Estonia", "373": "Moldova",
    "374": "Armenia", "375": "Belarus", "376": "Andorra", "377": "Monaco",
    "378": "San Marino", "380": "Ukraine", "381": "Serbia", "382": "Montenegro",
    "383": "Kosovo", "385": "Croatia", "386": "Slovenia", "387": "Bosnia",
    "389": "North Macedonia", "420": "Czechia", "421": "Slovakia",
    "423": "Liechtenstein", "500": "Falkland Islands", "501": "Belize",
    "502": "Guatemala", "503": "El Salvador", "504": "Honduras", "505": "Nicaragua",
    "506": "Costa Rica", "507": "Panama", "591": "Bolivia", "592": "Guyana",
    "593": "Ecuador", "595": "Paraguay", "598": "Uruguay", "673": "Brunei",
    "855": "Cambodia", "856": "Laos", "880": "Bangladesh", "886": "Taiwan",
    "960": "Maldives", "961": "Lebanon", "962": "Jordan", "963": "Syria",
    "964": "Iraq", "965": "Kuwait", "966": "Saudi Arabia", "967": "Yemen",
    "968": "Oman", "970": "Palestine", "971": "UAE", "972": "Israel",
    "973": "Bahrain", "974": "Qatar", "975": "Bhutan", "976": "Mongolia",
    "977": "Nepal", "992": "Tajikistan", "993": "Turkmenistan",
    "994": "Azerbaijan", "995": "Georgia", "996": "Kyrgyzstan", "998": "Uzbekistan",
}

TZ_FALLBACK = {
    "1": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"],
    "44": ["Europe/London"], "33": ["Europe/Paris"], "49": ["Europe/Berlin"],
    "39": ["Europe/Rome"], "34": ["Europe/Madrid"], "31": ["Europe/Amsterdam"],
    "32": ["Europe/Brussels"], "41": ["Europe/Zurich"], "43": ["Europe/Vienna"],
    "48": ["Europe/Warsaw"], "46": ["Europe/Stockholm"], "47": ["Europe/Oslo"],
    "45": ["Europe/Copenhagen"], "358": ["Europe/Helsinki"], "353": ["Europe/Dublin"],
    "351": ["Europe/Lisbon"], "30": ["Europe/Athens"], "90": ["Europe/Istanbul"],
    "7": ["Europe/Moscow"], "380": ["Europe/Kyiv"], "420": ["Europe/Prague"],
    "61": ["Australia/Sydney", "Australia/Perth"], "64": ["Pacific/Auckland"],
    "81": ["Asia/Tokyo"], "82": ["Asia/Seoul"], "86": ["Asia/Shanghai"],
    "886": ["Asia/Taipei"], "65": ["Asia/Singapore"], "60": ["Asia/Kuala_Lumpur"],
    "62": ["Asia/Jakarta"], "63": ["Asia/Manila"], "66": ["Asia/Bangkok"],
    "84": ["Asia/Ho_Chi_Minh"], "91": ["Asia/Kolkata"], "92": ["Asia/Karachi"],
    "880": ["Asia/Dhaka"], "971": ["Asia/Dubai"], "966": ["Asia/Riyadh"],
    "972": ["Asia/Jerusalem"], "20": ["Africa/Cairo"], "27": ["Africa/Johannesburg"],
    "234": ["Africa/Lagos"], "254": ["Africa/Nairobi"], "212": ["Africa/Casablanca"],
    "55": ["America/Sao_Paulo"], "52": ["America/Mexico_City"],
    "54": ["America/Argentina/Buenos_Aires"], "56": ["America/Santiago"],
    "57": ["America/Bogota"], "51": ["America/Lima"],
}

TZ_OFFSETS = {
    "Europe/London": 0, "Europe/Dublin": 0, "Europe/Lisbon": 0, "UTC": 0,
    "Europe/Paris": 1, "Europe/Berlin": 1, "Europe/Rome": 1, "Europe/Madrid": 1,
    "Europe/Amsterdam": 1, "Europe/Brussels": 1, "Europe/Zurich": 1, "Europe/Vienna": 1,
    "Europe/Warsaw": 1, "Europe/Stockholm": 1, "Europe/Oslo": 1, "Europe/Copenhagen": 1,
    "Europe/Prague": 1, "Europe/Athens": 2, "Europe/Helsinki": 2,
    "Europe/Bucharest": 2, "Europe/Kyiv": 2, "Europe/Istanbul": 3, "Europe/Moscow": 3,
    "Asia/Jerusalem": 2, "Asia/Dubai": 4, "Asia/Karachi": 5, "Asia/Kolkata": 5.5,
    "Asia/Dhaka": 6, "Asia/Bangkok": 7, "Asia/Jakarta": 7, "Asia/Singapore": 8,
    "Asia/Shanghai": 8, "Asia/Taipei": 8, "Asia/Manila": 8, "Asia/Tokyo": 9,
    "Asia/Seoul": 9, "Australia/Sydney": 10, "Australia/Perth": 8,
    "Pacific/Auckland": 12, "Africa/Cairo": 2, "Africa/Lagos": 1,
    "Africa/Johannesburg": 2, "Africa/Nairobi": 3, "Africa/Casablanca": 1,
    "America/Sao_Paulo": -3, "America/Argentina/Buenos_Aires": -3,
    "America/New_York": -5, "America/Chicago": -6, "America/Denver": -7,
    "America/Los_Angeles": -8, "America/Mexico_City": -6, "America/Bogota": -5,
    "America/Lima": -5, "America/Santiago": -3,
}

TOLL_FREE = {"800", "833", "844", "855", "866", "877", "888", "889"}

MOBILE_HINTS = {
    "44": lambda n: n.startswith("7"), "33": lambda n: n.startswith(("6", "7")),
    "49": lambda n: n.startswith(("15", "16", "17")),
    "39": lambda n: n.startswith("3"), "34": lambda n: n.startswith(("6", "7")),
    "31": lambda n: n.startswith("6"), "32": lambda n: n.startswith("4"),
    "48": lambda n: n.startswith(("5", "6", "7", "8")),
    "46": lambda n: n.startswith("7"), "47": lambda n: n.startswith(("4", "9")),
    "45": lambda n: True, "351": lambda n: n.startswith(("9", "6")),
    "353": lambda n: n.startswith(("8", "9")), "30": lambda n: n.startswith("69"),
    "90": lambda n: n.startswith("5"), "7": lambda n: n.startswith("9"),
    "380": lambda n: n.startswith(("5", "6", "7", "9")),
    "91": lambda n: n.startswith(("6", "7", "8", "9")),
    "86": lambda n: n.startswith("1"), "81": lambda n: n.startswith(("7", "8", "9")),
    "82": lambda n: n.startswith("1"), "61": lambda n: n.startswith("4"),
    "64": lambda n: n.startswith("2"), "65": lambda n: n.startswith(("8", "9")),
    "60": lambda n: n.startswith("1"), "62": lambda n: n.startswith("8"),
    "63": lambda n: n.startswith("9"),
    "84": lambda n: n.startswith(("3", "5", "7", "8", "9")),
    "55": lambda n: n.startswith(("6", "7", "8", "9")),
    "52": lambda n: n.startswith("1"), "54": lambda n: n.startswith("9"),
    "27": lambda n: n.startswith(("6", "7", "8")),
    "234": lambda n: n.startswith(("7", "8", "9")),
}


def cc_from_e164(digits):
    for n in (3, 2, 1):
        if len(digits) > n and digits[:n] in CALLING_CODES:
            return digits[:n]
    return digits[:2] if len(digits) > 2 else digits


def tz_now(tzname):
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(tzname)).strftime("%H:%M:%S %Z")
    except Exception:
        pass
    if tzname in TZ_OFFSETS:
        h = TZ_OFFSETS[tzname]
        u = datetime.now(timezone.utc) + timedelta(hours=h)
        sign = "+" if h >= 0 else "-"
        hh, mm = divmod(int(abs(h) * 60), 60)
        return f"{u.strftime('%H:%M:%S')} {sign}{hh:02d}{mm:02d}"
    return "?"


def mod_phone_oracle():
    raw = ask("phone number (with country code, e.g. +14158586273)")
    if not raw:
        return
    digits = re.sub(r"[^\d+]", "", raw).lstrip("+")
    if digits.startswith("00"):
        digits = digits[2:]
    if not digits.isdigit():
        bad("no digits found")
        return
    e164 = "+" + digits
    cc = cc_from_e164(digits)
    national = digits[len(cc):]
    country = CALLING_CODES.get(cc, "unknown calling code")

    print()
    rule("FORMAT")
    kv("input", raw)
    kv("e164", e164)
    kv("country calling code", f"+{cc}")
    kv("country", country)
    kv("national number", national)
    kv("digits", len(digits))
    if 8 <= len(national) <= 12:
        ok("length plausible")
    else:
        wrn(f"national part is {len(national)} digits — verify")

    print()
    rule("NUMBER TYPE")
    if cc == "1":
        npa = national[:3]
        if npa in TOLL_FREE:
            kv("type", "toll free (NANPA)")
        elif npa.startswith("9"):
            kv("type", "premium rate (NANPA)")
        elif npa[:1] in "2345":
            kv("type", "landline-ish NPA")
        elif npa[:1] in "6789":
            kv("type", "mobile / VoIP-ish NPA")
        else:
            kv("type", "unknown NPA")
        kv("nanpa area code", npa)
        kv("exchange", national[3:6])
        kv("line", national[6:])
    else:
        hint = MOBILE_HINTS.get(cc)
        if hint:
            try:
                kv("type", "mobile (heuristic)" if hint(national)
                   else "fixed line (heuristic)")
            except Exception:
                pass
        else:
            kv("type", "undetermined")

    print()
    rule("TIMEZONE(S)")
    tzs = list(TZ_FALLBACK.get(cc, []))
    meta = get_json(f"https://restcountries.com/v3.1/callingcode/{cc}", timeout=15)
    if isinstance(meta, dict):
        meta = [meta]
    if isinstance(meta, list) and meta:
        m0 = meta[0]
        for t in (m0.get("timezones") or []):
            if t not in tzs:
                tzs.append(t)
        kv("country (api)", (m0.get("name") or {}).get("common", country))
        kv("region", f"{m0.get('region')} / {m0.get('subregion')}")
        kv("capital", ", ".join(m0.get("capital") or []) or "-")
        langs = ", ".join((m0.get("languages") or {}).values())
        kv("languages", langs[:120] or "-")
        cur = m0.get("currencies") or {}
        if cur:
            k = list(cur)[0]
            kv("currency", f"{k} {cur[k].get('name', '')} ({cur[k].get('symbol', '')})")
        latlng = m0.get("latlng") or []
        if latlng:
            kv("centroid", f"{latlng[0]}, {latlng[1]}")
    else:
        bad("restcountries unreachable — using offline table")
    if tzs:
        for tz in tzs[:8]:
            kv(tz, tz_now(tz))
        if len(tzs) > 8:
            bad(f"  ... {len(tzs) - 8} more")
    else:
        bad("no timezone known for this calling code")

    print()
    rule("CARRIER / OPERATOR")
    got = False
    d = get_json(f"https://api.veriphone.io/v2/verify?phone={urllib.parse.quote(e164)}",
                 timeout=15)
    if d and d.get("carrier") is not None:
        kv("source", "veriphone")
        kv("carrier", d.get("carrier") or "-")
        kv("line type", d.get("phone_type") or "-")
        kv("valid", d.get("phone_valid"))
        kv("region", d.get("phone_region") or d.get("country") or "-")
        got = True
    d2 = get_json(f"https://api.numlookupapi.com/v1/validate/{urllib.parse.quote(e164)}",
                  timeout=15)
    if d2 and (d2.get("carrier") or d2.get("line_type")):
        kv("source", "numlookupapi")
        kv("carrier", d2.get("carrier") or "-")
        kv("line type", d2.get("line_type") or "-")
        kv("location", d2.get("location") or "-")
        got = True
    if not got:
        bad("no keyless carrier API answered — falling back to search")
        for t, u in ddg(f'"{e164}" carrier OR operator', 6):
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:70]}{RESET}")
            print(f"      {fg(TH['dim'])}{u[:100]}{RESET}")

    print()
    rule("HANDLE / MESSENGER LINKS")
    kv("whatsapp", f"https://wa.me/{digits}")
    kv("telegram", f"https://t.me/+{digits}")
    kv("viber", f"viber://chat?number=%2B{digits}")
    kv("signal", f"https://signal.me/#p/+{digits}")
    kv("skype", f"skype:+{digits}")

    print()
    rule("REVERSE LOOKUP ENGINES")
    kv("truecaller", f"https://www.truecaller.com/search/{cc}/{digits}")
    kv("sync.me", f"https://sync.me/search/?number={e164}")
    kv("numlookup", f"https://www.numlookup.com/?number={digits}")
    kv("whitepages", f"https://www.whitepages.com/phone/{digits}")
    kv("spytox", f"https://www.spytox.com/phone/{digits}")

    print()
    rule("LIVE SEARCH")
    for t, u in ddg('"' + e164 + '"', 10):
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:70]}{RESET}")
        print(f"      {fg(TH['dim'])}{u[:100]}{RESET}")

    save_json(f"wt_phone_{safe_name(digits)}.json",
              {"e164": e164, "cc": cc, "country": country, "timezones": tzs})


def mod_insta_lens():
    user = ask("username (no @)").lstrip("@")
    if not user:
        return
    d = get_json("https://www.instagram.com/api/v1/users/web_profile_info/?username=" +
                 user, timeout=15, headers={"x-ig-app-id": "936619743392459",
                                            "Accept": "*/*",
                                            "Referer": f"https://www.instagram.com/{user}/"})
    u = (((d or {}).get("data") or {}).get("user")) or {}
    if not u:
        st, body, _ = http_get(f"https://www.instagram.com/{user}/", timeout=15)
        html = body.decode("utf-8", "replace") if body else ""
        m = re.search(r'<meta property="og:description" content="([^"]*)"', html)
        if m:
            t = htmlmod.unescape(m.group(1))
            mm = re.match(r"([\d.,KM]+)\s+Followers,\s+([\d.,KM]+)\s+Following,\s+"
                          r"([\d.,KM]+)\s+Posts", t)
            if mm:
                kv("followers", mm.group(1))
                kv("following", mm.group(2))
                kv("posts", mm.group(3))
            kv("raw", t[:150])
        else:
            bad("no data (login wall or rate limit)")
        return
    kv("full name", u.get("full_name") or "-")
    kv("verified", "yes" if u.get("is_verified") else "no")
    kv("private", "yes" if u.get("is_private") else "no")
    kv("business", "yes" if u.get("is_business_account") else "no")
    kv("category", u.get("category_name") or "-")
    kv("user id", u.get("id"))
    kv("followers", (u.get("edge_followed_by") or {}).get("count"))
    kv("following", (u.get("edge_follow") or {}).get("count"))
    kv("posts", (u.get("edge_owner_to_timeline_media") or {}).get("count"))
    if u.get("biography"):
        kv("bio", u["biography"].replace("\n", " ")[:200])
    if u.get("external_url"):
        kv("external url", u["external_url"][:120])
    if u.get("business_email"):
        kv("business email", u["business_email"])
    if u.get("business_phone_number"):
        kv("business phone", u["business_phone_number"])
    print()
    edges = (u.get("edge_owner_to_timeline_media") or {}).get("edges") or []
    if edges:
        rule("RECENT POSTS")
        for e in edges[:6]:
            n = e.get("node") or {}
            ce = (n.get("edge_media_to_caption") or {}).get("edges") or []
            cap = (ce[0].get("node") or {}).get("text", "")[:70].replace("\n", "") if ce else ""
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}"
                  f"likes {n.get('edge_liked_by', {}).get('count','-')} · "
                  f"comments {n.get('edge_media_to_comment', {}).get('count','-')} · "
                  f"{cap}{RESET}")


def mod_chain_watch():
    addr = ask("btc / eth / ltc / doge / sol address")
    if not addr:
        return
    if re.fullmatch(r"^(bc1[a-z0-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})$", addr):
        inf("bitcoin")
        d = get_json(f"https://blockstream.info/api/address/{addr}", timeout=15)
        if d:
            rule("BLOCKSTREAM")
            cs = d.get("chain_stats") or {}
            ms = d.get("mempool_stats") or {}
            kv("confirmed balance", f"{cs.get('funded_txo_sum', 0) / 1e8:.8f} BTC")
            kv("tx count", cs.get("tx_count", 0))
            kv("mempool pending", ms.get("tx_count", 0))
        else:
            bad("no data")
    elif re.fullmatch(r"0x[a-fA-F0-9]{40}", addr):
        inf("ethereum")
        d = get_json(f"https://eth.blockscout.com/api/v2/addresses/{addr}", timeout=15)
        if d:
            rule("BLOCKSCOUT")
            kv("balance", f"{int(d.get('coin_balance', 0)) / 1e18:.8f} ETH")
            kv("txs", d.get("transactions_count"))
            kv("contract", "yes" if d.get("is_contract") else "no")
        e = get_json(f"https://api.ethplorer.io/getAddressInfo/{addr}?apiKey=freekey",
                     timeout=15)
        if e and e.get("ETH"):
            rule("ETHPLORER")
            kv("balance", f"{e['ETH'].get('balance', 0):.8f} ETH")
            kv("txs", e.get("countTxs", 0))
            for t in (e.get("tokens") or [])[:12]:
                ti = t.get("tokenInfo") or {}
                kv(ti.get("symbol", "?"),
                   f"{t.get('balance', 0) / (10 ** int(ti.get('decimals', 18))):.6f}")
        else:
            bad("ethplorer gave nothing")
    elif re.fullmatch(r"^(ltc1[a-z0-9]{25,62}|[LM3][a-km-zA-HJ-NP-Z1-9]{25,34})$", addr):
        inf("litecoin")
        d = get_json(f"https://litecoinspace.org/api/address/{addr}", timeout=15)
        if d:
            rule("LITECOINSPACE")
            cs = d.get("chain_stats") or {}
            kv("balance", f"{cs.get('funded_txo_sum', 0) / 1e8:.8f} LTC")
            kv("txs", cs.get("tx_count", 0))
        else:
            bad("no data")
    elif re.fullmatch(r"^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{32,44}$", addr):
        inf("dogecoin")
        d = get_json(f"https://dogechain.info/api/v1/address/balance/{addr}", timeout=15)
        if d and d.get("success"):
            rule("DOGECHAIN")
            kv("balance", f"{d.get('balance', 0):.8f} DOGE")
        else:
            bad("no data")
    elif re.fullmatch(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", addr):
        inf("solana")
        st, body, _ = http_post("https://api.mainnet-beta.solana.com",
                                {"jsonrpc": "2.0", "id": 1,
                                 "method": "getBalance", "params": [addr]}, timeout=15)
        d = jload(body)
        if d and d.get("result"):
            rule("SOLANA RPC")
            kv("sol", f"{d['result'].get('value', 0) / 1e9:.9f}")
        else:
            bad("no data")
    else:
        bad("unrecognised address format")


def mod_leak_lens():
    q = ask("email or domain")
    if not q:
        return
    inf(f"checking {q}")
    if "@" in q:
        d = get_json("https://api.xposedornot.com/v1/breach-analytics?email=" +
                     urllib.parse.quote(q), timeout=20)
        if d:
            kv("breach score",
               ((d.get("BreachMetrics") or {}).get("risk") or {}).get("risk_label", "?"))
            details = (d.get("ExposedBreaches") or {}).get("breaches_details") or []
            kv("breaches", len(details))
            LIVE["hits"] += len(details)
            for b in details[:25]:
                print(f"    {fg((255,140,120))}·{RESET} "
                      f"{fg(TH['text'])}{str(b.get('breach','?'))[:40]}{RESET}"
                      f"  {fg(TH['dim'])}{b.get('xposed_date','')} · "
                      f"{str(b.get('xposed_data',''))[:44]}{RESET}")
            if not details:
                bad("not found in any tracked breach")
        else:
            bad("xposedornot gave nothing")
    print()
    rule("PASTE / LEAK SEARCH")
    for site in ("pastebin.com", "ghostbin.com", "rentry.co", "controlc.com"):
        for t, u in ddg(f'site:{site} "{q}"', 4):
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:66]}{RESET}")
            print(f"      {fg(TH['dim'])}{u[:100]}{RESET}")
    print()
    rule("SEARCH")
    for t, u in ddg(f'"{q}" leak breach', 8):
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:70]}{RESET}")
        print(f"      {fg(TH['dim'])}{u[:100]}{RESET}")


def mod_git_excavate():
    user = ask("github username").lstrip("@")
    if not user:
        return
    inf(f"profiling {user}")
    prof = get_json(f"https://api.github.com/users/{user}", timeout=15)
    if not prof or prof.get("message") == "Not Found":
        bad("user not found")
        return
    for k in ("login", "name", "company", "blog", "location", "email", "bio",
              "twitter_username", "public_repos", "followers", "following",
              "created_at", "id", "type", "hireable"):
        if prof.get(k) not in (None, ""):
            kv(k, prof[k])
    print()
    rule("REPOSITORIES (top by stars)")
    repos = get_json(f"https://api.github.com/users/{user}/repos?per_page=100&sort=updated",
                     timeout=20) or []
    langs = {}
    for r in repos:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    for r in sorted(repos, key=lambda x: -(x.get("stargazers_count") or 0))[:12]:
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{r['name'][:40]:<40}{RESET} "
              f"{fg(TH['dim'])}★{r.get('stargazers_count', 0)} ⑂{r.get('forks_count', 0)} "
              f"{r.get('language') or '-'}{RESET}")
    if langs:
        print()
        rule("LANGUAGE PROFILE")
        for l, n in sorted(langs.items(), key=lambda x: -x[1])[:12]:
            kv(l, f"{'█' * min(30, n * 2)} {n}")
    print()
    rule("RECENT PUBLIC EVENTS")
    ev = get_json(f"https://api.github.com/users/{user}/events/public?per_page=30",
                  timeout=15) or []
    emails = set()
    for e in ev[:15]:
        repo = (e.get("repo") or {}).get("name", "")
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{e.get('type','')[:24]:<24}"
              f"{RESET} {fg(TH['dim'])}{repo}{RESET}")
        for cc in ((e.get("payload") or {}).get("commits") or []):
            a = (cc.get("author") or {})
            if a.get("email"):
                emails.add(f"{a.get('name','?')} <{a['email']}>")
    if emails:
        print()
        rule("COMMITTER IDENTITIES")
        for e in sorted(emails)[:20]:
            hit(e)
    print()
    rule("ORGS")
    orgs = get_json(f"https://api.github.com/users/{user}/orgs", timeout=15)
    if isinstance(orgs, list) and orgs:
        kv("orgs", ", ".join(o.get("login", "") for o in orgs[:12]))
    save_json(f"wt_gh_{safe_name(user)}.json",
              {"profile": prof, "repos": [r.get("name") for r in repos]})


def mod_social_xray():
    for i, lbl in enumerate(["telegram channel / user", "discord invite",
                             "youtube channel / video", "x / twitter", "mastodon",
                             "bluesky", "reddit", "threads"], 1):
        print(f"    {fg(TH['key'])}[{i}]{RESET} {fg(TH['text'])}{lbl}{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        h = ask("telegram handle (no @)").lstrip("@")
        st, body, _ = http_get(f"https://t.me/{h}", timeout=15)
        html = body.decode("utf-8", "replace")
        for prop in ("og:title", "og:description", "og:url"):
            m = re.search(r'<meta[^>]+property=["\']' + prop +
                          r'["\'][^>]*content=["\']([^"\']*)', html, re.I)
            if m:
                kv(prop, htmlmod.unescape(m.group(1))[:150])
        m = re.search(r'tgme_page_extra">([^<]+)', html)
        if m:
            kv("members / subscribers", strip_tags(m.group(1)))
    elif pick == "2":
        inv = ask("discord invite code").split("/")[-1]
        d = get_json(f"https://discord.com/api/v10/invites/{inv}?with_counts=true",
                     timeout=15)
        if not d or d.get("message"):
            bad("invalid or expired invite")
            return
        g = d.get("guild") or {}
        kv("guild", g.get("name"))
        kv("guild id", g.get("id"))
        kv("members", d.get("approximate_member_count"))
        kv("online", d.get("approximate_presence_count"))
        kv("inviter", (d.get("inviter") or {}).get("username"))
    elif pick == "3":
        h = ask("channel handle or video url")
        if h.startswith("http"):
            st, body, _ = http_get(
                f"https://www.youtube.com/oembed?url={urllib.parse.quote(h)}&format=json",
                timeout=15)
            j = jload(body) or {}
            for k in ("title", "author_name", "author_url"):
                if j.get(k):
                    kv(k, j[k])
            return
        st, body, _ = http_get(f"https://www.youtube.com/@{h.lstrip('@')}", timeout=15)
        html = body.decode("utf-8", "replace")
        for prop in ("og:title", "og:description"):
            m = re.search(r'<meta[^>]+property=["\']' + prop +
                          r'["\'][^>]*content=["\']([^"\']*)', html, re.I)
            if m:
                kv(prop, htmlmod.unescape(m.group(1))[:180])
        m = re.search(r'"subscriberCountText":\{"simpleText":"([^"]+)"', html)
        if m:
            kv("subscribers", m.group(1))
    elif pick == "4":
        h = ask("handle (no @)").lstrip("@")
        d = get_json(f"https://api.fxtwitter.com/{h}", timeout=15)
        u = (d or {}).get("user") or {}
        if not u:
            bad("not found")
            return
        for k in ("name", "screen_name", "description", "location", "url", "followers",
                  "following", "tweets", "joined"):
            if u.get(k) is not None:
                kv(k, str(u[k])[:150])
    elif pick == "5":
        h = ask("handle@instance.tld")
        if "@" not in h:
            bad("expected user@instance")
            return
        u, inst = h.split("@", 1)
        d = get_json(f"https://{inst}/api/v1/accounts/lookup?acct={u}", timeout=15)
        if not d:
            bad("not found")
            return
        for k in ("display_name", "note", "followers_count", "statuses_count", "created_at"):
            if d.get(k) is not None:
                kv(k, strip_tags(str(d[k]))[:180])
    elif pick == "6":
        h = ask("handle (no @, .bsky.social assumed)").lstrip("@")
        if "." not in h:
            h += ".bsky.social"
        d = get_json("https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor=" +
                     h, timeout=15)
        if not d:
            bad("not found")
            return
        for k in ("handle", "displayName", "description", "followersCount", "createdAt"):
            if d.get(k) is not None:
                kv(k, str(d[k])[:180])
    elif pick == "7":
        h = ask("reddit username (no u/)").lstrip("u/")
        d = get_json(f"https://www.reddit.com/user/{h}/about.json", timeout=15)
        data = (d or {}).get("data") or {}
        if not data:
            bad("not found")
            return
        for k in ("name", "total_karma", "link_karma", "comment_karma", "created_utc"):
            if data.get(k) is not None:
                v = data[k]
                if k == "created_utc" and isinstance(v, (int, float)):
                    v = datetime.fromtimestamp(v, timezone.utc).strftime("%Y-%m-%d")
                kv(k, str(v)[:150])
    else:
        h = ask("threads handle (no @)").lstrip("@")
        st, body, _ = http_get(f"https://www.threads.net/@{h}", timeout=15)
        html = body.decode("utf-8", "replace")
        for prop in ("og:title", "og:description"):
            m = re.search(r'<meta[^>]+property=["\']' + prop +
                          r'["\'][^>]*content=["\']([^"\']*)', html, re.I)
            if m:
                kv(prop, htmlmod.unescape(m.group(1))[:180])


def mod_avatar_lens():
    email = ask("email address")
    if not email:
        return
    prof, gh = gravatar(email)
    kv("md5 hash", gh)
    kv("avatar url", f"https://www.gravatar.com/avatar/{gh}")
    kv("profile url", f"https://gravatar.com/{gh}")
    if not prof:
        bad("no gravatar profile registered")
    else:
        rule("PROFILE")
        for k in ("displayName", "name", "aboutMe", "currentLocation", "job_title",
                  "company", "pronouns"):
            if prof.get(k):
                kv(k, str(prof[k])[:180])
        for acc in (prof.get("accounts") or []):
            kv(acc.get("shortname", "account"),
               f"{acc.get('username','')} {acc.get('url','')}"[:120])
    if ask("render avatar as ascii art? (y/n)", "y").lower().startswith("y"):
        spin("fetching avatar")
        st, data, _ = http_get(f"https://www.gravatar.com/avatar/{gh}?s=200&d=404",
                               timeout=15)
        if st == 200 and data:
            try:
                print()
                render_ascii(png_load(data), cols=64)
            except Exception as e:
                bad(f"render failed: {e}")
        else:
            bad("no avatar image")


OUI_TABLE = {
    "000C29": "VMware", "005056": "VMware", "001C14": "VMware",
    "080027": "VirtualBox", "0A0027": "VirtualBox", "525400": "QEMU/KVM",
    "00163E": "Xen", "00155D": "Microsoft Hyper-V", "000D3A": "Microsoft",
    "0017FA": "Microsoft", "00125A": "Microsoft", "281878": "Microsoft",
    "0003FF": "Microsoft", "7C1E52": "Microsoft", "C83F26": "Microsoft",
    "001B63": "Apple", "0017F2": "Apple", "001E52": "Apple", "002332": "Apple",
    "3C0754": "Apple", "A45E60": "Apple", "F0DBF8": "Apple", "9C207B": "Apple",
    "B827EB": "Raspberry Pi", "DCA632": "Raspberry Pi", "E45F01": "Raspberry Pi",
    "2CCF67": "Raspberry Pi", "001A11": "Google", "3C5AB4": "Google",
    "F4F5E8": "Google", "546009": "Google", "DC4F22": "Espressif",
    "240AC4": "Espressif", "5CCF7F": "Espressif", "A020A6": "Espressif",
    "CC50E3": "Espressif", "B4E62D": "Espressif", "84F3EB": "Espressif",
    "001CC0": "Intel", "001E64": "Intel", "34E12D": "Intel", "8086F2": "Intel",
    "A0A8CD": "Intel", "E4A471": "Intel", "001B21": "Intel", "001517": "Intel",
    "0013E8": "Intel", "0012F0": "Intel", "000E0C": "Intel", "001111": "Intel",
    "00AA00": "Intel", "001B77": "Intel", "0024D7": "Intel", "00270E": "Intel",
    "5CE0C5": "Intel", "7CB27D": "Intel", "001E37": "Hewlett-Packard",
    "001B78": "Hewlett-Packard", "002481": "Hewlett-Packard", "3C4A92": "Hewlett-Packard",
    "9457A5": "Hewlett-Packard", "0018FE": "Hewlett-Packard",
    "001A4B": "Hewlett-Packard", "001CC4": "Hewlett-Packard",
    "001F29": "Hewlett-Packard", "0025B3": "Hewlett-Packard",
    "3464A9": "Hewlett-Packard", "002219": "Dell", "14FEB5": "Dell", "1866DA": "Dell",
    "18A99B": "Dell", "246E96": "Dell", "3417EB": "Dell", "44A842": "Dell",
    "5CF9DD": "Dell", "782BCB": "Dell", "B8AC6F": "Dell", "BC305B": "Dell",
    "C81F66": "Dell", "D067E5": "Dell", "F8B156": "Dell", "F8BC12": "Dell",
    "001349": "Cisco", "001A30": "Cisco", "001B0C": "Cisco", "001E13": "Cisco",
    "002155": "Cisco", "0024C4": "Cisco", "0026CB": "Cisco", "189C5D": "Cisco",
    "1CE85D": "Cisco", "2C3F38": "Cisco", "3C0E23": "Cisco", "4C776D": "Cisco",
    "588D09": "Cisco", "6C2056": "Cisco", "70DB98": "Cisco", "8C604F": "Cisco",
    "A46C2A": "Cisco", "B000B4": "Cisco", "C067AF": "Cisco", "D4A02A": "Cisco",
    "E05FB9": "Cisco", "F02929": "Cisco", "F4CFE2": "Cisco",
    "00000C": "Cisco", "000142": "Cisco", "000143": "Cisco", "000163": "Cisco",
    "000164": "Cisco", "000196": "Cisco", "000197": "Cisco", "0001C7": "Cisco",
    "0001C9": "Cisco", "000216": "Cisco", "000217": "Cisco", "00023D": "Cisco",
    "00024A": "Cisco", "00024B": "Cisco", "00027D": "Cisco", "00027E": "Cisco",
    "0002B3": "Cisco", "0002B9": "Cisco", "0002BA": "Cisco", "0002FC": "Cisco",
    "0002FD": "Cisco", "000332": "Cisco", "000347": "Cisco", "00036B": "Cisco",
    "00036C": "Cisco", "000383": "Cisco", "00039F": "Cisco", "0003A0": "Cisco",
    "0003E3": "Cisco", "0003E4": "Cisco", "0003FD": "Cisco", "0003FE": "Cisco",
    "000427": "Cisco", "000428": "Cisco", "00044D": "Cisco", "00044E": "Cisco",
    "00046D": "Cisco", "00046E": "Cisco", "00049A": "Cisco", "00049B": "Cisco",
    "0004C0": "Cisco", "0004C1": "Cisco", "0004DD": "Cisco", "0004DE": "Cisco",
    "000500": "Cisco", "000501": "Cisco", "000531": "Cisco", "000532": "Cisco",
    "00055E": "Cisco", "00055F": "Cisco", "000573": "Cisco", "000574": "Cisco",
    "00059A": "Cisco", "00059B": "Cisco", "0005DC": "Cisco", "0005DD": "Cisco",
    "000628": "Cisco", "00062A": "Cisco", "000652": "Cisco", "000653": "Cisco",
    "00065B": "Cisco", "00067C": "Cisco", "00067D": "Cisco", "0006C1": "Cisco",
    "0006D6": "Cisco", "0006D7": "Cisco", "0006F6": "Cisco", "0006F7": "Cisco",
}


def oui_lookup(mac):
    clean = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(clean) < 6:
        return None
    return OUI_TABLE.get(clean[:6])


def mod_oui_oracle():
    mac = ask("mac address (any separator)")
    clean = re.sub(r"[^0-9a-fA-F]", "", mac)
    if len(clean) < 6:
        bad("too short")
        return
    clean = clean[:12].upper()
    oui = ":".join(clean[i:i + 2] for i in range(0, len(clean), 2))
    kv("normalised", oui)
    kv("oui", oui[:8])
    if len(clean) == 12:
        kv("local bit",
           "set (locally administered)" if int(clean[1], 16) & 2 else "clear (global)")
        kv("multicast", "yes" if int(clean[1], 16) & 1 else "no")
    local = oui_lookup(clean)
    if local:
        ok(f"vendor (offline table): {local}")
    st, body, _ = http_get(f"https://api.macvendors.com/{oui[:8]}", timeout=12)
    if st == 200:
        ok(f"vendor (online): {body.decode('utf-8', 'replace').strip()}")
    elif not local:
        bad("vendor unknown or rate limited")


def mod_asn_map():
    q = ask("asn number or ip / domain")
    if not q:
        return
    if re.fullmatch(r"AS?\d+", q, re.I):
        asn = re.sub(r"[^\d]", "", q)
    else:
        ip = resolve(q) or q
        kv("resolved", ip)
        d = get_json(f"https://api.bgpview.io/ip/{ip}", timeout=15)
        prefixes = ((d or {}).get("data") or {}).get("prefixes") or []
        if not prefixes:
            bad("no asn data")
            return
        asn = str(prefixes[0].get("asn", {}).get("asn"))
    kv("asn", f"AS{asn}")
    d = get_json(f"https://api.bgpview.io/asn/{asn}", timeout=15)
    data = (d or {}).get("data") or {}
    for k in ("name", "description_full", "country_code", "website"):
        if data.get(k):
            kv(k, str(data[k])[:150])
    print()
    rule("ANNOUNCED PREFIXES (v4)")
    p = get_json(f"https://api.bgpview.io/asn/{asn}/prefixes", timeout=20)
    v4 = ((p or {}).get("data") or {}).get("ipv4_prefixes") or []
    for x in v4[:40]:
        print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{str(x.get('prefix')):<20}{RESET} "
              f"{fg(TH['dim'])}{str(x.get('name'))[:44]}{RESET}")
    kv("total v4 prefixes", len(v4))
    print()
    rule("PEERS")
    pr = get_json(f"https://api.bgpview.io/asn/{asn}/peers", timeout=20)
    peers = ((pr or {}).get("data") or {}).get("ipv4_peers") or []
    for x in peers[:15]:
        kv(f"AS{x.get('asn')}", f"{x.get('name','')}"[:90])
    kv("total peers", len(peers))


def mod_wayback_vault():
    domain = ask("domain or url", "example.com")
    domain = domain.replace("https://", "").replace("http://", "").strip("/")
    inf("querying the wayback machine")
    d = get_json("http://web.archive.org/cdx/search/cdx?url=" +
                 urllib.parse.quote(domain) +
                 "&output=json&limit=400&collapse=urlkey&fl=original,timestamp,statuscode",
                 timeout=40)
    if not d or len(d) < 2:
        bad("no snapshots")
        return
    rows = d[1:]
    kv("snapshots", len(rows))
    kv("earliest", rows[0][1][:8] if len(rows[0]) > 1 else "-")
    kv("latest", rows[-1][1][:8] if len(rows[-1]) > 1 else "-")
    print()
    rule("INTERESTING FILES")
    pat = re.compile(r"\.(pdf|sql|bak|zip|rar|tar|gz|env|json|xml|txt|log|csv|conf|old|"
                     r"doc|docx|xls|xlsx|key|pem)(\?|$)", re.I)
    interesting = [r for r in rows if pat.search(r[0])]
    for r in interesting[:40]:
        hit(f"{r[1][:8]}  {r[0][:96]}")
    kv("matching", len(interesting))
    print()
    rule("SAMPLE URLS")
    for r in rows[:30]:
        print(f"    {fg(TH['dim'])}{r[1][:8]}  {r[0][:100]}{RESET}")
    save_json(f"wt_wayback_{safe_name(domain)}.json",
              [{"url": r[0], "ts": r[1] if len(r) > 1 else ""} for r in rows])


def typosquats(domain):
    name, _, tld = domain.partition(".")
    out = set()
    letters = string.ascii_lowercase
    for i in range(len(name)):
        out.add(name[:i] + name[i + 1:])
        out.add(name[:i] + name[i] + name[i:])
        for c in letters:
            out.add(name[:i] + c + name[i + 1:])
            out.add(name[:i] + c + name[i:])
        if i < len(name) - 1:
            out.add(name[:i] + name[i + 1] + name[i] + name[i + 2:])
    for i in range(1, len(name)):
        out.add(name[:i] + "-" + name[i:])
    out.add(name + "s")
    for t in ("com", "net", "org", "io", "co", "dev", "app", "xyz", "info", "biz"):
        if t != tld:
            out.add(f"{name}.{t}")
    return sorted(x for x in out if x and x != domain)


def mod_typo_trap():
    domain = ask("domain", "example.com").lower()
    perms = typosquats(domain)
    inf(f"{len(perms)} permutation(s) generated")
    pg = Progress(len(perms), "resolving")
    registered = []
    with ThreadPoolExecutor(max_workers=48) as ex:
        futs = {ex.submit(resolve, p): p for p in perms}
        for fut in as_completed(futs):
            pg.update()
            ip = fut.result()
            if ip:
                registered.append((futs[fut], ip))
                LIVE["hits"] += 1
    pg.done()
    print()
    rule("REGISTERED PERMUTATIONS")
    for p, ip in sorted(registered):
        hit(f"{p:<40} {ip}")
    inf(f"{len(registered)} registered · {len(perms) - len(registered)} free")
    save_json(f"wt_typo_{safe_name(domain)}.json",
              [{"domain": p, "ip": ip} for p, ip in registered])


def mod_stack_pivot():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}favicon hash pivot{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}analytics / adsense id pivot{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}http headers pivot{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        url = ask("site url", "https://example.com")
        if "://" not in url:
            url = "https://" + url
        st, data, _ = http_get(url.rstrip("/") + "/favicon.ico", timeout=15)
        if st != 200 or not data:
            bad("no favicon")
            return
        kv("size", f"{len(data)} bytes")
        kv("md5", hashlib.md5(data).hexdigest())
        b64 = base64.encodebytes(data).decode().replace("\n", "")
        hmm = hashlib.md5(b64.encode()).hexdigest()
        kv("b64 md5 (shodan)", hmm)
        print()
        kv("shodan", f"https://www.shodan.io/search?query=http.favicon.hash:{hmm}"[:120])
        q64 = base64.b64encode(f'icon_hash="{hmm}"'.encode()).decode()
        kv("fofa", f"https://en.fofa.info/result?qbase64={q64}"[:120])
    elif pick == "2":
        ident = ask("ga4 / ua / adsense id")
        for q in (f'"{ident}"', f'"{ident}" -site:google.com'):
            print()
            rule(q)
            for t, u in ddg(q, 8):
                print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:70]}{RESET}")
                print(f"      {fg(TH['dim'])}{u[:100]}{RESET}")
    else:
        url = ask("url", "https://example.com")
        if "://" not in url:
            url = "https://" + url
        st, body, hdrs = http_get(url, timeout=15)
        for k, v in sorted(hdrs.items()):
            if k.startswith("x-") or k in ("server", "via"):
                kv(k, v[:110])
                for t, u in ddg(f'"{v}"', 3):
                    print(f"      {fg(TH['dim'])}-> {t[:60]} {u[:70]}{RESET}")


def mod_whois_deep():
    q = ask("domain or ip", "example.com")
    if not q:
        return
    inf(f"rdap + whois for {q}")
    kind = "ip" if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", q) else "domain"
    print()
    rule("RDAP (structured)")
    d = get_json(f"https://rdap.org/{kind}/{q}", timeout=18)
    if d:
        kv("handle", d.get("handle"))
        kv("ldhName", d.get("ldhName"))
        kv("status", ", ".join(d.get("status") or []))
        for e in (d.get("events") or []):
            kv("event " + str(e.get("eventAction")), str(e.get("eventDate", ""))[:19])
        for n in (d.get("nameservers") or []):
            kv("nameserver", str(n.get("ldhName", "")).lower())
        for e in d.get("entities") or []:
            roles = ",".join(e.get("roles") or [])
            for item in ((e.get("vcardArray") or [None, []])[1] or []):
                try:
                    if item[0] in ("fn", "email", "tel"):
                        val = item[3] if not isinstance(item[3], list) else \
                            " ".join(str(x) for x in item[3] if x)
                        kv(f"{roles} {item[0]}", str(val)[:90])
                except Exception:
                    pass
    else:
        bad("no rdap data")
    print()
    rule("HACKERTARGET WHOIS")
    st, body, _ = http_get(f"https://api.hackertarget.com/whois/?q={q}", timeout=25)
    if st == 200 and body and b"error" not in body.lower():
        for line in body.decode("utf-8", "replace").splitlines()[:60]:
            if line.strip():
                print(f"    {fg(TH['text'])}{line[:118]}{RESET}")
    else:
        bad("whois lookup failed")
    print()
    rule("TYPOSQUAT / RELATED")
    if kind == "domain":
        perms = typosquats(q)[:40]
        pg = Progress(len(perms), "resolving")
        with ThreadPoolExecutor(max_workers=32) as ex:
            for p, ip in zip(perms, ex.map(resolve, perms)):
                pg.update()
                if ip:
                    pg.line()
                    print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{p:<36}{RESET} "
                          f"{fg(TH['dim'])}{ip}{RESET}")
        pg.done()


def mod_paste_diver():
    q = ask("email / domain / username / phrase")
    if not q:
        return
    inf(f"hunting pastes for {q}")
    d = get_json(f"https://psbdmp.ws/api/v3/search/{urllib.parse.quote(q)}", timeout=20)
    if isinstance(d, dict) and d.get("data"):
        rule("PSBDMP")
        for p in d["data"][:25]:
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}"
                  f"{str(p.get('time',''))[:16]}{RESET}  "
                  f"{fg(TH['dim'])}https://pastebin.com/{p.get('id','')}{RESET}")
        LIVE["hits"] += len(d["data"])
    else:
        bad("psbdmp returned nothing")
    print()
    for site in ("pastebin.com", "ghostbin.com", "rentry.co", "controlc.com",
                 "justpaste.it", "paste.ee", "dpaste.org"):
        res = ddg(f'site:{site} "{q}"', 3)
        if res:
            rule(site.upper())
            for t, u in res:
                print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{t[:66]}{RESET}")
                print(f"      {fg(TH['dim'])}{u[:100]}{RESET}")


def mod_geo_lens():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}coordinates -> address{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}address -> coordinates{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}ip -> location + maps{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        raw = ask("lat,lon", "48.8584,2.2945")
        m = re.match(r"\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)", raw)
        if not m:
            bad("expected lat,lon")
            return
        lat, lon = m.group(1), m.group(2)
        d = get_json("https://nominatim.openstreetmap.org/reverse?format=json&lat=" +
                     lat + "&lon=" + lon + "&zoom=18&addressdetails=1", timeout=15,
                     headers={"User-Agent": "whitetiger/1.0"})
        if d:
            kv("display name", d.get("display_name", "")[:180])
            for k, v in (d.get("address") or {}).items():
                kv(k, v)
        else:
            bad("no reverse geocode")
        print()
        kv("google maps", f"https://maps.google.com/?q={lat},{lon}")
        kv("osm", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}")
    elif pick == "2":
        addr = ask("address", "Eiffel Tower, Paris")
        d = get_json("https://nominatim.openstreetmap.org/search?format=json&limit=5&q=" +
                     urllib.parse.quote(addr), timeout=15,
                     headers={"User-Agent": "whitetiger/1.0"})
        if not d:
            bad("no results")
            return
        for r in d:
            print()
            kv("display", r.get("display_name", "")[:180])
            kv("coords", f"{r.get('lat')}, {r.get('lon')}")
            kv("maps", f"https://maps.google.com/?q={r.get('lat')},{r.get('lon')}")
    else:
        ip = ask("ip or hostname")
        if not ip:
            return
        ip = resolve(ip) or ip
        geo = get_json(f"https://ipwho.is/{ip}", timeout=12)
        if not geo or not geo.get("success"):
            bad("no geo data")
            return
        for k in ("country", "country_code", "region", "city", "postal", "latitude",
                  "longitude"):
            if geo.get(k) is not None:
                kv(k, geo.get(k))
        c = geo.get("connection") or {}
        kv("isp", c.get("isp"))
        lat, lon = geo.get("latitude"), geo.get("longitude")
        print()
        kv("maps", f"https://maps.google.com/?q={lat},{lon}")
        ss = get_json(f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}", timeout=12)
        if ss and ss.get("results"):
            for k in ("sunrise", "sunset"):
                kv(k, ss["results"].get(k))
        tz = get_json("https://timeapi.io/api/TimeZone/coordinate?latitude=" +
                      str(lat) + "&longitude=" + str(lon), timeout=12)
        if tz:
            kv("timezone", tz.get("timeZone"))


PACKAGE_REGISTRIES = [
    ("npm", "https://registry.npmjs.org/{}", "json"),
    ("pypi", "https://pypi.org/pypi/{}/json", "json"),
    ("crates", "https://crates.io/api/v1/crates/{}", "json"),
    ("rubygems", "https://rubygems.org/api/v1/gems/{}.json", "json"),
    ("packagist", "https://repo.packagist.org/p2/{}.json", "json"),
    ("nuget", "https://api.nuget.org/v3-flatcontainer/{}/index.json", "json"),
    ("docker", "https://hub.docker.com/v2/repositories/library/{}/", "json"),
]


def mod_supply_watch():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}package lookup across registries{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}typosquat check a package name{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        name = ask("package name", "requests")
        for reg, tpl, kind in PACKAGE_REGISTRIES:
            st, body, _ = http_get(tpl.format(urllib.parse.quote(name)), timeout=12,
                                   retries=0)
            if st == 200:
                info = []
                d = jload(body)
                if isinstance(d, dict):
                    if "dist-tags" in d:
                        info.append("latest " + str((d.get("dist-tags") or {})
                                                    .get("latest", "?")))
                    if d.get("info"):
                        info.append("version " + str((d["info"] or {}).get("version", "?")))
                    if d.get("crate"):
                        info.append("version " + str((d["crate"] or {})
                                                     .get("max_version", "?")))
                    if d.get("description"):
                        info.append(str(d["description"])[:70])
                print(f"  {sev_tag('info')} {reg:<12} EXISTS  {' · '.join(info)[:90]}")
                LIVE["hits"] += 1
            else:
                print(f"  {fg(TH['dim'])}-  {reg:<12} not found ({st}){RESET}")
    else:
        name = ask("package name", "requests")
        print()
        perms = typosquats(name.replace("-", "") + ".com")
        perms = [p.split(".")[0] for p in perms if "." in p]
        perms = dedupe([p for p in perms if p and p != name])[:60]
        inf(f"checking {len(perms)} typosquat candidates")
        for reg, tpl, kind in (PACKAGE_REGISTRIES[0], PACKAGE_REGISTRIES[1],
                               PACKAGE_REGISTRIES[2]):
            for p in perms:
                st, _, _ = http_get(tpl.format(urllib.parse.quote(p)), timeout=8,
                                    retries=0)
                if st == 200:
                    print(f"  {sev_tag('low')} {reg:<8} {p} exists")
                    LIVE["hits"] += 1


def mod_feed_wire():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}parse an rss / atom feed{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}threat intel feed digest{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        url = ask("feed url", "https://feeds.bbci.co.uk/news/rss.xml")
        st, body, _ = http_get(url, timeout=20, max_bytes=3_000_000)
        if not body:
            bad("unreachable")
            return
        try:
            root = ET.fromstring(body)
        except Exception as e:
            bad(f"xml parse failed: {e}")
            return
        n = 0
        for it in root.iter("item"):
            n += 1
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            print(f"  {fg(TH['key'])}·{RESET} {fg(TH['text'])}{title[:80]}{RESET}")
            print(f"    {fg(TH['dim'])}{link[:90]}{RESET}")
            if n >= 25:
                break
        inf(f"{n} item(s)")
    else:
        feeds = [("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
                 ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
                 ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
                 ("SANS ISC", "https://isc.sans.edu/rssfeed.xml")]
        for name, url in feeds:
            st, body, _ = http_get(url, timeout=20, max_bytes=2_000_000)
            if not body:
                continue
            try:
                root = ET.fromstring(body)
            except Exception:
                continue
            print()
            rule(name.upper())
            for i, it in enumerate(root.iter("item")):
                if i >= 5:
                    break
                title = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                print(f"  {fg(TH['key'])}·{RESET} {fg(TH['text'])}{title[:84]}{RESET}")
                if link:
                    print(f"    {fg(TH['dim'])}{link[:96]}{RESET}")


# ------------------------- NEW OSINT (56-58) ------------------------------ #
def mod_code_hunt():
    target = ask("domain or github org", "example.com")
    if not target:
        return
    inf(f"searching github code for '{target}'")
    queries = [f'"{target}"', f'"@{target}"', f'"{target}" password',
               f'"{target}" api_key', f'"{target}" secret']
    found = 0
    for q in queries:
        d = get_json("https://api.github.com/search/code?q=" + urllib.parse.quote(q) +
                     "&per_page=10", timeout=25)
        items = (d or {}).get("items") or []
        if not items:
            print(f"  {fg(TH['dim'])}- {q}{RESET}")
            continue
        print()
        rule(q)
        for it in items[:8]:
            repo = (it.get("repository") or {}).get("full_name", "")
            print(f"  {sev_tag('info')} {fg(TH['text'])}{it.get('path','')[:70]}{RESET}")
            print(f"      {fg(TH['dim'])}{repo}{RESET}")
            found += 1
            LIVE["hits"] += 1
    print()
    inf(f"{found} code hit(s) (unauthenticated github search is heavily rate limited)")


def mod_urlscan_lens():
    q = ask("domain / ip / url")
    if not q:
        return
    inf(f"urlscan.io search: {q}")
    d = get_json("https://urlscan.io/api/v1/search/?q=" + urllib.parse.quote(q) +
                 "&size=50", timeout=25)
    res = (d or {}).get("results") or []
    if not res:
        bad("no scans")
        return
    kv("scans", (d or {}).get("total", len(res)))
    for r in res[:25]:
        page = r.get("page") or {}
        task = r.get("task") or {}
        print()
        print(f"  {fg(TH['key'])}·{RESET} {fg(TH['text'])}{page.get('url','')[:90]}{RESET}")
        kv("  domain", page.get("domain"))
        kv("  ip", page.get("ip"))
        kv("  server", page.get("server"))
        kv("  asn", page.get("asnname"))
        kv("  scanned", str(task.get("time", ""))[:19])
        if r.get("_id"):
            kv("  result", f"https://urlscan.io/result/{r['_id']}/")
        if r.get("screenshot"):
            kv("  screenshot", r["screenshot"][:100])


def mod_reddit_scope():
    user = ask("reddit username (no u/)").lstrip("u/")
    if not user:
        return
    inf(f"profiling u/{user}")
    d = get_json(f"https://www.reddit.com/user/{user}/about.json", timeout=15)
    data = (d or {}).get("data") or {}
    if not data:
        bad("user not found")
        return
    for k in ("name", "total_karma", "link_karma", "comment_karma", "is_mod",
              "is_gold", "verified", "created_utc"):
        if data.get(k) is not None:
            v = data[k]
            if k == "created_utc" and isinstance(v, (int, float)):
                v = datetime.fromtimestamp(v, timezone.utc).strftime("%Y-%m-%d")
            kv(k, str(v)[:120])
    if data.get("subreddit"):
        kv("profile sub", (data["subreddit"] or {}).get("public_description", "")[:140])
    for kind in ("submitted", "comments"):
        print()
        rule(kind.upper())
        j = get_json(f"https://www.reddit.com/user/{user}/{kind}.json?limit=15", timeout=20)
        children = (((j or {}).get("data") or {}).get("children")) or []
        if not children:
            bad("none")
            continue
        for c in children:
            cd = c.get("data") or {}
            title = cd.get("title") or cd.get("body") or ""
            print(f"  {fg(TH['key'])}·{RESET} {fg(TH['text'])}"
                  f"{str(title).replace(chr(10),' ')[:84]}{RESET}")
            kv("  sub", cd.get("subreddit"))
            kv("  when", datetime.fromtimestamp(cd.get("created_utc", 0), timezone.utc)
               .strftime("%Y-%m-%d %H:%M"))


# =========================================================================== #
#  CSINT
# =========================================================================== #

COMMON_WORDS = [
    "password", "123456", "12345678", "123456789", "12345", "qwerty", "abc123", "monkey",
    "letmein", "dragon", "111111", "baseball", "iloveyou", "trustno1", "sunshine", "master",
    "welcome", "shadow", "ashley", "football", "jesus", "michael", "ninja", "mustang",
    "password1", "password123", "admin", "administrator", "root", "toor", "guest", "test",
    "test123", "changeme", "secret", "secretkey", "jwt", "jwtsecret", "supersecret",
    "mysecret", "dev", "development", "production", "staging", "default", "superman",
    "batman", "starwars", "princess", "flower", "hello", "hello123", "charlie", "donald",
    "freedom", "whatever", "qwerty123", "qwertyuiop", "1q2w3e4r", "1qaz2wsx", "zaq12wsx",
    "asdfgh", "asdfghjkl", "zxcvbnm", "passw0rd", "p@ssword", "p@ssw0rd", "P@ssw0rd",
    "P@ssw0rd123", "Summer2024", "Summer2025", "Winter2024", "Spring2024",
    "January", "February", "company", "company123", "corp", "corporate", "office", "work",
    "login", "access", "letmein123", "welcome1", "welcome123", "admin123", "root123",
    "changeme123", "abc123456", "abcdef", "1234", "1234567", "000000", "696969", "121212",
    "7777777", "55555", "888888", "987654321", "159753", "123123", "112233", "102030",
    "qazwsx", "asdasd", "qweqwe", "1q2w3e", "qwerty1", "qwerty12", "pass", "pass123",
    "temppass", "temporary", "initial", "changeme1", "NewPassword", "newpass", "reset",
    "apikey", "api_key", "token", "auth", "authorization", "bearer", "signing", "signature",
    "hmac", "sha256", "md5", "crypto", "encryption", "key", "private", "public", "ssl",
    "tls", "https", "server", "client", "database", "mysql", "postgres", "redis", "mongo",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github",
    "trello", "slack", "discord", "telegram", "facebook", "google", "microsoft", "apple",
    "amazon", "netflix", "spotify", "twitter", "instagram", "linkedin", "youtube",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "october", "november", "december", "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday", "spring", "summer", "autumn", "winter",
    "mysecretkey", "supersecretkey", "topsecret", "verysecret", "hunter2",
    "correcthorsebatterystaple", "letmein1", "abc", "xyz", "testtest", "demo", "demo123",
]


def hash_algos():
    algos = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256",
             "blake2b", "blake2s", "ripemd160"]
    out = [a for a in algos if a in hashlib.algorithms_available]
    if "md4" in hashlib.algorithms_available:
        out.insert(1, "md4")
    return out


def mod_hash_breaker():
    h = ask("hash or plaintext")
    if not h:
        return
    kinds = {8: "CRC32 / adler32", 16: "MySQL half / DES crypt", 32: "MD5 / NTLM / MD4",
             40: "SHA-1 / RIPEMD-160", 56: "SHA-224",
             64: "SHA-256 / SHA3-256 / BLAKE2s", 96: "SHA-384",
             128: "SHA-512 / SHA3-512 / BLAKE2b", 60: "bcrypt"}
    is_hash = bool(re.fullmatch(r"[a-fA-F0-9]+", h)) and len(h) in kinds
    if is_hash:
        kv("length", len(h))
        kv("likely", kinds[len(h)])
        if len(h) == 32:
            kv("also could be", "NTLM (windows), MD4")
        print()
        rule("IDENTIFY BY RECOMPUTING KNOWN VALUES")
        for word in ("", "password", "123456", "admin"):
            for a in hash_algos():
                try:
                    if hashlib.new(a, word.encode()).hexdigest().lower() == h.lower():
                        hit(f"{a}({word!r}) matches")
                        LIVE["hits"] += 1
                except Exception:
                    pass
    else:
        kv("input", h)
        for name in hash_algos():
            try:
                kv(name, hashlib.new(name, h.encode()).hexdigest())
            except Exception:
                pass
        kv("crc32", f"{zlib.crc32(h.encode()) & 0xFFFFFFFF:08x}")
        kv("base64", base64.b64encode(h.encode()).decode())
        return
    if not ask("try to crack against a wordlist? (y/n)", "y").lower().startswith("y"):
        return
    words = list(COMMON_WORDS)
    target = h.lower()
    inf(f"testing {len(words)} candidates x {len(hash_algos())} algorithms + rules")
    algos = hash_algos()
    found = False
    pg = Progress(len(words), "cracking")
    for w in words:
        pg.update()
        variants = {w, w.lower(), w.upper(), w.capitalize(), w + "1", w + "123", w + "!",
                    w.replace("a", "@").replace("o", "0"), w[::-1],
                    w + "2024", w + "2025", w + "2026"}
        for v in variants:
            for a in algos:
                try:
                    if hashlib.new(a, v.encode()).hexdigest() == target:
                        found = True
                        pg.line()
                        ok(f"CRACKED: {v}  ({a})")
                        LIVE["hits"] += 1
                        break
                except Exception:
                    pass
            if found:
                break
        if found:
            break
    pg.done()
    if not found:
        bad("not in wordlist")


def mod_jwt_lab():
    tok = ask("jwt")
    if not tok:
        return
    parts = tok.split(".")
    if len(parts) < 2:
        bad("not a jwt")
        return
    kv("segments", len(parts))

    def b64d(s):
        s += "=" * (-len(s) % 4)
        return base64.urlsafe_b64decode(s)

    for i, name in enumerate(("header", "payload", "signature")):
        if i >= len(parts):
            break
        print()
        rule(name.upper())
        if name == "signature":
            try:
                kv("hex", b64d(parts[i]).hex()[:120])
            except Exception:
                bad("undecodable")
            continue
        try:
            d = json.loads(b64d(parts[i]).decode("utf-8", "replace"))
            print(json.dumps(d, indent=2)[:2000])
        except Exception:
            bad("undecodable segment")
    print()
    rule("ANALYSIS")
    hdr, pl = {}, {}
    try:
        hdr = json.loads(b64d(parts[0]).decode("utf-8", "replace"))
        alg = hdr.get("alg", "?")
        kv("alg", alg)
        if alg.lower() == "none":
            wrn("alg=none -> signature not verified by many libs")
        if alg.startswith("HS"):
            hit("HMAC — try cracking with a weak secret")
        if hdr.get("jku"):
            kv("jku", hdr["jku"])
        if hdr.get("kid"):
            kv("kid", hdr["kid"])
            wrn("kid may be injectable")
    except Exception:
        pass
    try:
        pl = json.loads(b64d(parts[1]).decode("utf-8", "replace"))
        now = time.time()
        if "exp" in pl:
            ts = int(pl["exp"])
            when = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
            kv("expires", when + (" EXPIRED" if ts < now else
                                  f" (valid {fmt_dur(ts - now)})"))
        for c in ("iss", "aud", "sub", "scope", "roles", "email", "admin", "role"):
            if c in pl:
                kv(c, str(pl[c])[:120])
    except Exception:
        pass
    print()
    rule("CRACK HMAC SECRET")
    if ask("brute force a weak secret? (y/n)", "y").lower().startswith("y"):
        alg = hdr.get("alg", "HS256")
        digest = {"HS256": "sha256", "HS384": "sha384", "HS512": "sha512"}.get(alg, "sha256")
        signing = (parts[0] + "." + parts[1]).encode()
        sig = b64d(parts[2]) if len(parts) > 2 else b""
        for w in COMMON_WORDS:
            for v in {w, w.lower(), w.upper()}:
                if hmac.new(v.encode(), signing, digest).digest() == sig:
                    ok(f"SECRET: {v}")
                    LIVE["hits"] += 1
                    return
        bad("secret not in built-in wordlist")
    print()
    rule("FORGE")
    if ask("forge a token? (y/n)", "y").lower().startswith("y"):
        secret = ask("secret (blank for alg=none)", "")
        claims = dict(pl) if pl else {"sub": "admin", "iat": int(time.time()),
                                      "exp": int(time.time()) + 86400}

        def b(o):
            return base64.urlsafe_b64encode(
                json.dumps(o, separators=(",", ":")).encode()).rstrip(b"=").decode()

        if secret:
            h = {"alg": "HS256", "typ": "JWT"}
            msg = f"{b(h)}.{b(claims)}"
            sig = base64.urlsafe_b64encode(
                hmac.new(secret.encode(), msg.encode(), "sha256").digest()
            ).rstrip(b"=").decode()
            print(f"    {fg(TH['accent'])}{msg}.{sig}{RESET}")
        else:
            print(f"    {fg(TH['accent'])}{b({'alg': 'none', 'typ': 'JWT'})}.{b(claims)}.{RESET}")


MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.",
         "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.",
         "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-",
         "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..", "0": "-----",
         "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....",
         "6": "-....", "7": "--...", "8": "---..", "9": "----.", ".": ".-.-.-",
         ",": "--..--", "?": "..--..", "!": "-.-.--", "/": "-..-."}

ROT13 = str.maketrans(
    string.ascii_letters,
    string.ascii_lowercase[13:] + string.ascii_lowercase[:13] +
    string.ascii_uppercase[13:] + string.ascii_uppercase[:13])


def mod_codec_deck():
    data = ask("text or encoded value")
    if not data:
        return
    print()
    rule("ENCODE")
    enc = [
        ("base64", lambda d: base64.b64encode(d.encode()).decode()),
        ("base64url", lambda d: base64.urlsafe_b64encode(d.encode()).decode().rstrip("=")),
        ("base32", lambda d: base64.b32encode(d.encode()).decode()),
        ("base85", lambda d: base64.b85encode(d.encode()).decode()),
        ("hex", lambda d: d.encode().hex()),
        ("binary", lambda d: " ".join(f"{b:08b}" for b in d.encode())),
        ("octal", lambda d: " ".join(f"{b:03o}" for b in d.encode())),
        ("url", lambda d: urllib.parse.quote(d)),
        ("html", lambda d: htmlmod.escape(d)),
        ("rot13", lambda d: d.translate(ROT13)),
        ("rot47", lambda d: "".join(
            chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in d)),
        ("atbash", lambda d: "".join(
            chr(ord("z") - (ord(c.lower()) - ord("a"))) if c.isalpha() else c for c in d)),
        ("morse", lambda d: " ".join(MORSE.get(c.upper(), "?") for c in d)),
        ("reverse", lambda d: d[::-1]),
        ("leetspeak", lambda d: d.translate(str.maketrans("aeiostAEIOST",
                                                          "431057431057"))),
        ("md5", lambda d: hashlib.md5(d.encode()).hexdigest()),
        ("sha1", lambda d: hashlib.sha1(d.encode()).hexdigest()),
        ("sha256", lambda d: hashlib.sha256(d.encode()).hexdigest()),
    ]
    for lbl, fn in enc:
        try:
            kv(lbl, str(fn(data))[:180])
        except Exception:
            pass
    print()
    rule("DECODE ATTEMPTS")
    dec = [
        ("base64", lambda d: base64.b64decode(d + "=" * (-len(d) % 4))
         .decode("utf-8", "replace")),
        ("base32", lambda d: base64.b32decode(d + "=" * (-len(d) % 8))
         .decode("utf-8", "replace")),
        ("base85", lambda d: base64.b85decode(d).decode("utf-8", "replace")),
        ("hex", lambda d: bytes.fromhex(re.sub(r"[^0-9a-fA-F]", "", d))
         .decode("utf-8", "replace")),
        ("url", lambda d: urllib.parse.unquote(d)),
        ("rot13", lambda d: d.translate(ROT13)),
        ("atbash", lambda d: "".join(
            chr(ord("z") - (ord(c.lower()) - ord("a"))) if c.isalpha() else c for c in d)),
        ("binary", lambda d: "".join(
            chr(int(b, 2)) for b in d.split() if re.fullmatch(r"[01]{8}", b))),
        ("morse", lambda d: "".join(
            {v: k for k, v in MORSE.items()}.get(t, "?") for t in d.split())),
    ]
    for lbl, fn in dec:
        try:
            r = fn(data)
            if r and r != data and all(31 < ord(c) < 127 or c in "\n\t" for c in r[:200]):
                kv(lbl, r[:180])
        except Exception:
            pass
    print()
    if re.fullmatch(r"[0-9a-fA-F]{32,128}", data):
        hit("input looks like a hash")


def mod_cve_oracle():
    q = ask("cve id or keyword")
    if not q:
        return
    if re.fullmatch(r"CVE-\d{4}-\d+", q, re.I):
        cid = q.upper()
        d = get_json(f"https://cve.circl.lu/api/cve/{cid}", timeout=20)
        if not d:
            bad("not found on circl")
        else:
            kv("id", d.get("id"))
            kv("published", str(d.get("Published", ""))[:19])
            kv("cvss", d.get("cvss"))
            kv("cwe", d.get("cwe"))
            print()
            rule("DESCRIPTION")
            for line in textwrap.wrap(d.get("summary", ""), 100)[:14]:
                print(f"    {fg(TH['text'])}{line}{RESET}")
            print()
            rule("REFERENCES")
            for r in (d.get("references") or [])[:12]:
                bad("  " + r[:110])
        epss = get_json(f"https://api.first.org/data/v1/epss?cve={cid}", timeout=15)
        if epss and epss.get("data"):
            e = epss["data"][0]
            print()
            rule("EPSS (exploit prediction)")
            kv("score", e.get("epss"))
            kv("percentile", e.get("percentile"))
        kev = get_json("https://www.cisa.gov/sites/default/files/feeds/"
                       "known_exploited_vulnerabilities.json", timeout=25)
        if kev:
            for v in kev.get("vulnerabilities", []):
                if v.get("cveID") == cid:
                    print()
                    rule("CISA KEV")
                    kv("vendor", v.get("vendorProject"))
                    kv("product", v.get("product"))
                    hit("ACTIVELY EXPLOITED IN THE WILD")
                    LIVE["hits"] += 1
                    break
    else:
        d = get_json("https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=" +
                     urllib.parse.quote(q) + "&resultsPerPage=20", timeout=30)
        vulns = (d or {}).get("vulnerabilities") or []
        if not vulns:
            bad("no results (nvd may rate limit)")
            return
        inf(f"{d.get('totalResults')} total · showing {len(vulns)}")
        for v in vulns:
            c = v.get("cve") or {}
            desc = ((c.get("descriptions") or [{}])[0]).get("value", "")
            score = None
            for m in (c.get("metrics") or {}).values():
                for x in m:
                    score = (x.get("cvssData") or {}).get("baseScore") or score
            print()
            print(f"    {fg(TH['key'])}{c.get('id')}{RESET}  "
                  f"{fg((255,140,60))}{score if score else '-'}{RESET}")
            for line in textwrap.wrap(desc, 96)[:4]:
                print(f"      {fg(TH['text'])}{line}{RESET}")


SECRET_PATTERNS = [
    ("AWS access key", r"\b(AKIA[0-9A-Z]{16})\b"),
    ("AWS secret-ish", r"\b([A-Za-z0-9/+=]{40})\b"),
    ("Google API key", r"\b(AIza[0-9A-Za-z\-_]{35})\b"),
    ("GitHub token", r"\b(gh[pousr]_[A-Za-z0-9]{36,255})\b"),
    ("GitLab token", r"\b(glpat-[A-Za-z0-9\-_]{20,})\b"),
    ("Slack token", r"\b(xox[baprs]-[A-Za-z0-9\-]{10,})\b"),
    ("Slack webhook", r"(https://hooks\.slack\.com/services/[A-Za-z0-9/]{40,})"),
    ("Stripe live", r"\b(sk_live_[0-9a-zA-Z]{24,})\b"),
    ("Stripe test", r"\b(sk_test_[0-9a-zA-Z]{24,})\b"),
    ("SendGrid", r"\b(SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43})\b"),
    ("Twilio", r"\b(SK[0-9a-fA-F]{32})\b"),
    ("NPM token", r"\b(npm_[A-Za-z0-9]{36})\b"),
    ("PyPI token", r"\b(pypi-[A-Za-z0-9_\-]{50,})\b"),
    ("Docker PAT", r"\b(dckr_pat_[A-Za-z0-9_\-]{20,})\b"),
    ("Private key", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ("JWT", r"\b(eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,})\b"),
    ("Basic auth url", r"\b([a-zA-Z]{3,10}://[^/\s:@]{3,20}:[^/\s:@]{3,20}@[^\s]+)"),
    ("Generic api key",
     r"(?:api[_-]?key|apikey)['\"]?\s*[:=]\s*['\"]([A-Za-z0-9_\-]{16,80})['\"]"),
    ("Generic secret",
     r"(?:secret|passwd|password|pwd)['\"]?\s*[:=]\s*['\"]([^'\"\s]{6,80})['\"]"),
    ("Bearer token", r"[Bb]earer\s+([A-Za-z0-9_\-\.]{20,})"),
    ("Mongo URI", r"(mongodb(?:\+srv)?://[^\s'\"]+)"),
    ("Postgres URI", r"(postgres(?:ql)?://[^\s'\"]+)"),
    ("Redis URI", r"(redis://[^\s'\"]+)"),
    ("S3 bucket", r"\b([a-z0-9.\-]{3,63}\.s3(?:[.\-][a-z0-9\-]+)?\.amazonaws\.com)\b"),
    ("Firebase", r"\b([a-z0-9\-]+\.firebaseio\.com)\b"),
    ("Supabase", r"(https://[a-z0-9]+\.supabase\.co)"),
    ("IP + port", r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5})\b"),
    ("Telegram bot", r"\b(\d{8,12}:AA[A-Za-z0-9_\-]{32,35})\b"),
    ("Discord webhook",
     r"(https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_\-]+)"),
    ("Terraform state", r"(terraform\.tfstate)"),
]


def scan_secrets(text):
    out = {}
    for label, pat in SECRET_PATTERNS:
        for m in re.finditer(pat, text):
            v = m.group(1) if m.groups() else m.group(0)
            if len(v) > 4:
                out.setdefault(label, set()).add(v[:200])
    return out


def mod_secret_sniffer():
    src = ask("url or file path", "https://example.com")
    if os.path.isfile(src):
        with open(src, "r", encoding="utf-8", errors="replace") as f:
            text = f.read(8_000_000)
        kv("file", os.path.abspath(src))
    else:
        if "://" not in src:
            src = "https://" + src
        st, body, _ = http_get(src, timeout=20, max_bytes=8_000_000)
        if st is None:
            bad("unreachable")
            return
        text = body.decode("utf-8", "replace")
        kv("url", src)
    kv("size", f"{len(text):,} chars")
    found = scan_secrets(text)
    print()
    if not found:
        bad("no secrets matched")
        return
    total = sum(len(v) for v in found.values())
    for label, vals in sorted(found.items()):
        rule(label)
        for v in sorted(vals)[:12]:
            hit(v)
            LIVE["hits"] += 1
    print()
    inf(f"{total} candidate secret(s)")
    save_json("wt_secrets.json", {k: sorted(v) for k, v in found.items()})


# -------------------- metadata / file analysis ----------------------------- #
MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "PNG image"), (b"\xff\xd8\xff", "JPEG image"),
    (b"GIF87a", "GIF image"), (b"GIF89a", "GIF image"), (b"%PDF", "PDF document"),
    (b"PK\x03\x04", "ZIP / office / jar"), (b"PK\x05\x06", "empty ZIP"),
    (b"Rar!\x1a\x07", "RAR archive"), (b"\x1f\x8b", "gzip stream"),
    (b"BZh", "bzip2 stream"), (b"\xfd7zXZ\x00", "xz stream"),
    (b"7z\xbc\xaf\x27\x1c", "7-zip archive"),
    (b"\xd0\xcf\x11\xe0", "OLE2 (legacy office)"),
    (b"SQLite format 3\x00", "SQLite database"), (b"OggS", "Ogg container"),
    (b"fLaC", "FLAC audio"), (b"ID3", "MP3 (ID3 tagged)"),
    (b"RIFF", "RIFF container"), (b"\x1a\x45\xdf\xa3", "Matroska/WebM"),
    (b"\x7fELF", "ELF binary"), (b"MZ", "Windows PE executable"),
    (b"\xca\xfe\xba\xbe", "Mach-O / Java class"),
    (b"-----BEGIN", "PEM (cert / key)"), (b"#!", "script with shebang"),
    (b"<?xml", "XML document"), (b"ustar", "tar archive"),
]

EXIF_KEYS = {
    0x0100: "image_width", 0x0101: "image_height", 0x0102: "bits_per_sample",
    0x0103: "compression", 0x010E: "description", 0x010F: "make", 0x0110: "model",
    0x0112: "orientation", 0x011A: "x_resolution", 0x011B: "y_resolution",
    0x0128: "resolution_unit", 0x0131: "software", 0x0132: "datetime",
    0x013B: "artist", 0x8298: "copyright", 0x829A: "exposure_time", 0x829D: "f_number",
    0x8822: "exposure_program", 0x8827: "iso", 0x9000: "exif_version",
    0x9003: "datetime_original", 0x9004: "datetime_digitized", 0x9201: "shutter_speed",
    0x9202: "aperture", 0x9204: "exposure_bias", 0x9207: "metering_mode", 0x9209: "flash",
    0x920A: "focal_length", 0x9286: "user_comment", 0x9290: "subsec_time",
    0xA001: "colorspace", 0xA002: "pixel_x", 0xA003: "pixel_y",
    0xA217: "sensing_method", 0xA300: "file_source", 0xA301: "scene_type",
    0xA401: "custom_rendered", 0xA402: "exposure_mode", 0xA403: "white_balance",
    0xA404: "digital_zoom", 0xA405: "focal_length_35mm", 0xA406: "scene_capture",
    0xA408: "contrast", 0xA409: "saturation", 0xA40A: "sharpness",
    0xA420: "image_unique_id", 0xA430: "owner_name", 0xA431: "serial_number",
    0xA434: "lens_model", 0xA435: "lens_serial",
}

GPS_KEYS = {0: "gps_version", 1: "gps_latitude_ref", 2: "gps_latitude",
            3: "gps_longitude_ref", 4: "gps_longitude", 5: "gps_altitude_ref",
            6: "gps_altitude", 7: "gps_timestamp", 12: "gps_speed_ref",
            13: "gps_speed", 29: "gps_datestamp"}

_FMT_SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8}


def _dec(raw, fmt, endian):
    code = {1: "B", 2: "c", 3: "H", 4: "I", 5: "II", 7: "B", 9: "i", 10: "ii"}.get(fmt)
    if code is None:
        return None
    try:
        size = struct.calcsize(code)
        n = max(1, len(raw) // size)
        vals = struct.unpack(endian + code * n, raw[:size * n])
        if code == "c":
            return b"".join(vals).decode("latin-1", "replace").strip("\x00").strip()
        if code in ("B", "H", "I", "i"):
            return vals[0] if len(vals) == 1 else list(vals)
        if code == "II":
            return [tuple(vals[i:i + 2]) for i in range(0, len(vals), 2)]
        return vals
    except Exception:
        return None


def _rat(v):
    if isinstance(v, (tuple, list)) and len(v) == 2:
        return v[0] / v[1] if v[1] else 0.0
    try:
        return float(v)
    except Exception:
        return 0.0


def dms(vals, ref):
    if not isinstance(vals, (list, tuple)) or len(vals) < 3:
        return None
    d, m, s = _rat(vals[0]), _rat(vals[1]), _rat(vals[2])
    v = d + m / 60.0 + s / 3600.0
    if str(ref).upper() in ("S", "W"):
        v = -v
    return round(v, 7)


def _read_ifd(data, off, endian, depth=0):
    out = {}
    if depth > 3 or off + 2 > len(data) or off <= 0:
        return out
    try:
        n = struct.unpack(endian + "H", data[off:off + 2])[0]
    except Exception:
        return out
    pos = off + 2
    for _ in range(min(n, 512)):
        if pos + 12 > len(data):
            break
        tag, fmt, cnt = struct.unpack(endian + "HHI", data[pos:pos + 8])
        size = _FMT_SIZES.get(fmt, 1) * cnt
        if size > 4:
            try:
                voff = struct.unpack(endian + "I", data[pos + 8:pos + 12])[0]
            except Exception:
                voff = 0
            raw = data[voff:voff + size]
        else:
            raw = data[pos + 8:pos + 8 + size]
        val = _dec(raw, fmt, endian)
        if val not in (None, "", b""):
            out[tag] = val
        pos += 12
    return out


def parse_exif(data):
    res = {"ifd0": {}, "exif": {}, "gps": {}, "raw_gps": {}}
    if data[:2] != b"\xff\xd8":
        return res
    i, app1, guard = 2, None, 0
    while i + 4 <= len(data) and guard < 8000:
        guard += 1
        if data[i] != 0xFF:
            i += 1
            continue
        mk = data[i + 1]
        if mk in (0xD8, 0x01) or 0xD0 <= mk <= 0xD7:
            i += 2
            continue
        if mk == 0xDA:
            break
        ln = int.from_bytes(data[i + 2:i + 4], "big")
        if ln < 2:
            break
        seg = data[i + 4:i + 2 + ln]
        if mk == 0xE1 and seg[:6] == b"Exif\x00\x00":
            app1 = seg[6:]
            break
        i += 2 + ln
    if app1 is None or len(app1) < 8:
        return res
    endian = "<" if app1[:2] == b"II" else ">" if app1[:2] == b"MM" else None
    if endian is None:
        return res
    try:
        ifd0_off = struct.unpack(endian + "I", app1[4:8])[0]
    except Exception:
        return res
    ifd0 = _read_ifd(app1, ifd0_off, endian)
    res["ifd0"] = {EXIF_KEYS.get(k, hex(k)): v for k, v in ifd0.items()}
    for tag, key in ((0x8769, "exif"), (0x8825, "gps")):
        sub_off = ifd0.get(tag)
        if isinstance(sub_off, int) and sub_off > 0:
            sub = _read_ifd(app1, sub_off, endian, 1)
            table = GPS_KEYS if key == "gps" else EXIF_KEYS
            res[key] = {table.get(k, hex(k)): v for k, v in sub.items()}
            if key == "gps":
                res["raw_gps"] = dict(sub)
    return res


def png_text(data):
    out = {}
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return out
    i, guard = 8, 0
    while i + 8 <= len(data) and guard < 20000:
        guard += 1
        ln = int.from_bytes(data[i:i + 4], "big")
        typ = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + ln]
        try:
            if typ == b"tEXt":
                k, _, v = body.partition(b"\x00")
                out[k.decode("latin-1", "replace")] = v.decode("utf-8", "replace")[:220]
            elif typ == b"iTXt":
                k, _, rest = body.partition(b"\x00")
                parts = rest.split(b"\x00", 2)
                out[k.decode("latin-1", "replace")] = (
                    parts[-1] or b"").decode("utf-8", "replace")[:220]
        except Exception:
            pass
        if typ == b"IEND":
            break
        i += 12 + ln
    return out


def pdf_info(data):
    out = {}
    if data[:4] != b"%PDF":
        return out
    for m in re.finditer(rb"/(Title|Author|Subject|Keywords|Creator|Producer|"
                         rb"CreationDate|ModDate)\s*\(([^)]{0,240})\)", data):
        out[m.group(1).decode()] = m.group(2).decode("latin-1", "replace")[:200]
    return out


def id3_tags(data):
    out = {}
    if data[:3] != b"ID3" or len(data) < 10:
        return out
    size = (((data[6] & 0x7F) << 21) | ((data[7] & 0x7F) << 14) |
            ((data[8] & 0x7F) << 7) | (data[9] & 0x7F))
    body = data[10:10 + size]
    frames = {"TIT2": "title", "TPE1": "artist", "TALB": "album", "TYER": "year",
              "TDRC": "year", "TCON": "genre", "TRCK": "track", "TCOM": "composer",
              "TPUB": "publisher", "COMM": "comment", "TSSE": "encoder"}
    i = 0
    while i + 10 <= len(body):
        fid = body[i:i + 4].decode("latin-1")
        fsz = int.from_bytes(body[i + 4:i + 8], "big")
        if fsz <= 0 or i + 10 + fsz > len(body):
            break
        raw = body[i + 10:i + 10 + fsz]
        if fid in frames:
            try:
                enc = raw[0]
                txt = raw[1:].decode(
                    {0: "latin-1", 1: "utf-16", 2: "utf-16-be", 3: "utf-8"}.get(
                        enc, "latin-1"), "replace")
                out.setdefault(frames[fid], txt.strip("\x00").strip()[:200])
            except Exception:
                pass
        i += 10 + fsz
    return out


OFFICE_TAGS = {"creator", "lastmodifiedby", "created", "modified", "title", "subject",
               "keywords", "description", "application", "company", "manager"}


def office_meta(path):
    out = {}
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            for name in ("docProps/core.xml", "docProps/app.xml"):
                if name not in names:
                    continue
                xml = z.read(name).decode("utf-8", "replace")
                for m in re.finditer(r"<([A-Za-z0-9:_]+)[^>]*>(.*?)</\1>", xml, re.S):
                    tag = m.group(1).split(":")[-1].lower()
                    if tag in OFFICE_TAGS:
                        out[tag] = htmlmod.unescape(m.group(2))[:200]
    except Exception:
        pass
    return out


def strip_jpeg(data):
    if data[:2] != b"\xff\xd8":
        return data
    out, i, guard = bytearray(b"\xff\xd8"), 2, 0
    while i + 4 <= len(data) and guard < 100000:
        guard += 1
        if data[i] != 0xFF:
            i += 1
            continue
        mk = data[i + 1]
        if mk == 0xDA:
            out += data[i:]
            break
        if mk in (0xD8, 0x01) or 0xD0 <= mk <= 0xD7:
            out += data[i:i + 2]
            i += 2
            continue
        ln = int.from_bytes(data[i + 2:i + 4], "big")
        if ln < 2:
            break
        if mk not in (0xE1, 0xED, 0xFE):
            out += data[i:i + 2 + ln]
        i += 2 + ln
    return bytes(out)


def strip_png(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return data
    out, i, guard = bytearray(data[:8]), 8, 0
    while i + 8 <= len(data) and guard < 20000:
        guard += 1
        ln = int.from_bytes(data[i:i + 4], "big")
        typ = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + ln]
        if typ not in (b"tEXt", b"zTXt", b"iTXt", b"tIME"):
            out += struct.pack(">I", ln) + typ + body + \
                struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF)
        if typ == b"IEND":
            break
        i += 12 + ln
    return bytes(out)


def strip_pdf(data):
    out = re.sub(rb"<x:xmpmeta.*?</x:xmpmeta>", b"", data, flags=re.S)
    for key in (b"Producer", b"Creator", b"CreationDate", b"ModDate", b"Author",
                b"Title", b"Subject", b"Keywords"):
        out = re.sub(rb"/" + key + rb"\s*\([^)]*\)", b"", out)
    return out


def mod_meta_xray():
    path = ask("file path", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    with open(path, "rb") as f:
        data = f.read(24_000_000)
    kv("file", os.path.abspath(path))
    kv("size", human(len(data)))
    kv("sha256", hashlib.sha256(data).hexdigest())
    for sig, label in MAGIC:
        if data.startswith(sig):
            kv("detected type", label)
            break
    low = path.lower()
    gps = None
    if data[:3] == b"\xff\xd8\xff" or low.endswith((".jpg", ".jpeg", ".tif", ".tiff")):
        print()
        rule("EXIF")
        ex = parse_exif(data)
        for section in ("ifd0", "exif"):
            for k, v in sorted(ex.get(section, {}).items()):
                kv(f"{section}.{k}", str(v)[:120])
        if not ex["ifd0"] and not ex["exif"]:
            bad("no exif block found")
        if ex.get("gps"):
            print()
            rule("GPS")
            for k, v in sorted(ex["gps"].items()):
                kv(k, str(v)[:120])
            raw = ex.get("raw_gps", {})
            lat = dms(raw.get(2), raw.get(1, ""))
            lon = dms(raw.get(4), raw.get(3, ""))
            if lat is not None and lon is not None:
                gps = (lat, lon)
                print()
                hit(f"{lat}, {lon}")
                kv("google maps", f"https://maps.google.com/?q={lat},{lon}")
                kv("osm", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}")
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        print()
        rule("PNG TEXT CHUNKS")
        t = png_text(data)
        for k, v in t.items():
            kv(k, v)
        if not t:
            bad("none")
    if data[:4] == b"%PDF":
        print()
        rule("PDF INFO")
        p = pdf_info(data)
        for k, v in p.items():
            kv(k, v)
        if not p:
            bad("no info dictionary")
        kv("pages", len(re.findall(rb"/Type\s*/Page[^s]", data)))
        kv("javascript", len(re.findall(rb"/JavaScript|/JS\b", data)))
    if data[:3] == b"ID3" or low.endswith(".mp3"):
        print()
        rule("ID3 TAGS")
        t = id3_tags(data)
        for k, v in t.items():
            kv(k, v)
        if not t:
            bad("no id3 tags")
    if low.endswith((".docx", ".xlsx", ".pptx", ".odt")):
        print()
        rule("OFFICE CORE PROPERTIES")
        m = office_meta(path)
        for k, v in m.items():
            kv(k, v)
        if not m:
            bad("no docProps/core.xml")
    if gps and ask("reverse geocode + timezone? (y/n)", "y").lower().startswith("y"):
        print()
        spin("geocoding")
        d = get_json("https://nominatim.openstreetmap.org/reverse?format=json&lat="
                     f"{gps[0]}&lon={gps[1]}&zoom=18&addressdetails=1", timeout=18,
                     headers={"User-Agent": "whitetiger/1.0"})
        if d:
            kv("address", d.get("display_name", "")[:190])
            for k, v in (d.get("address") or {}).items():
                kv("  " + k, v)
        tz = get_json(f"https://timeapi.io/api/TimeZone/coordinate?latitude={gps[0]}"
                      f"&longitude={gps[1]}", timeout=15)
        if tz:
            kv("timezone", tz.get("timeZone"))
            kv("local time", tz.get("currentLocalTime"))


def mod_meta_scrub():
    path = ask("file path", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    base, ext = os.path.splitext(path)
    dest = ask("output file", f"{base}_clean{ext or '.bin'}")
    d = os.path.dirname(os.path.abspath(dest))
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "rb") as f:
        data = f.read(48_000_000)
    if data[:3] == b"\xff\xd8\xff":
        out = strip_jpeg(data)
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        out = strip_png(data)
    elif data[:4] == b"%PDF":
        out = strip_pdf(data)
    else:
        out = data
    with open(dest, "wb") as f:
        f.write(out)
    kv("in ", f"{human(len(data)):>10}")
    kv("out", f"{human(len(out)):>10}")
    kv("removed", human(max(0, len(data) - len(out))))
    if out == data:
        wrn("nothing stripped")
    else:
        ok("written -> " + os.path.abspath(dest))


IOC_PATS = [("url", r"https?://[^\s\"'<>)\]]{6,160}"),
            ("email", r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
            ("ipv4", r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
            ("sha256", r"\b[a-fA-F0-9]{64}\b"), ("md5", r"\b[a-fA-F0-9]{32}\b"),
            ("cve", r"\bCVE-\d{4}-\d{4,7}\b"),
            ("winpath", r"[A-Za-z]:\\[^\s\"'<>|*?]{3,120}"),
            ("unixpath", r"/(?:usr|etc|var|opt|home|tmp|bin|sbin)/[\w./\-]{2,120}"),
            ("btc", r"\b(?:bc1[a-z0-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b"),
            ("eth", r"\b0x[a-fA-F0-9]{40}\b")]


def mod_file_autopsy():
    path = ask("file path", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    with open(path, "rb") as f:
        data = f.read(48_000_000)
    kv("file", os.path.abspath(path))
    kv("size", human(len(data)))
    kv("md5", hashlib.md5(data).hexdigest())
    kv("sha256", hashlib.sha256(data).hexdigest())
    kv("crc32", f"{zlib.crc32(data) & 0xFFFFFFFF:08x}")
    kv("entropy", f"{entropy(data):.4f} bits/byte")
    for sig, label in MAGIC:
        if data.startswith(sig):
            kv("type", label)
            break
    else:
        bad("unrecognised magic")
    print()
    rule("ENTROPY MAP (4 KiB blocks)")
    bs = 4096
    blocks = [data[i:i + bs] for i in range(0, min(len(data), bs * 96), bs)]
    row, cols = [], []
    for b in blocks:
        e = entropy(b)
        row.append(BLOCKS[min(7, int(e / 8 * 7.99))])
        cols.append(lerp((40, 90, 140), (255, 110, 90), e / 8.0))
    for i in range(0, len(row), 64):
        print("    " + paint(row[i:i + 64], cols[i:i + 64]))
    high = sum(1 for b in blocks if entropy(b) > 7.2)
    if high:
        wrn(f"{high}/{len(blocks)} blocks at >7.2 bits — packed region")
    print()
    rule("EMBEDDED SIGNATURES")
    for sig, label in MAGIC:
        idx = data.find(sig)
        if idx > 0:
            hit(f"0x{idx:08x}  {label}")
    print()
    rule("STRINGS")
    strs = re.findall(rb"[\x20-\x7e]{6,200}", data)
    interesting = [s.decode("latin-1") for s in strs
                   if re.search(rb"(?i)(pass|secret|token|key|http|user|admin|"
                                rb"config|flag|ctf)", s)]
    kv("total strings", len(strs))
    for s in interesting[:40]:
        print(f"    {fg(TH['text'])}{s[:118]}{RESET}")
    print()
    rule("INDICATORS")
    text = data.decode("latin-1", "replace")
    for label, pat in IOC_PATS:
        vals = sorted(set(re.findall(pat, text, re.I)))[:14]
        if vals:
            kv(label, ", ".join(vals)[:200])
    print()
    if data[:2] == b"MZ":
        rule("PE NOTES")
        if b"UPX" in data[:400000]:
            wrn("UPX packer detected")
        for dll in sorted(set(re.findall(rb"[\w\-]+\.dll", data[:2000000], re.I)))[:14]:
            kv("import", dll.decode("latin-1"))


def mod_cookie_lens():
    url = ask("url", "https://example.com")
    if "://" not in url:
        url = "https://" + url
    st, body, hdrs = http_get(url, timeout=15)
    if st is None:
        bad("unreachable")
        return
    raw = hdrs.get("set-cookie", "")
    if not raw:
        bad("no Set-Cookie header")
        return
    for c in re.split(r",\s*(?=[A-Za-z0-9_\-]+=)", raw):
        print()
        rule("COOKIE")
        parts = [p.strip() for p in c.split(";")]
        name_val = parts[0]
        kv("name=value", name_val[:120])
        attrs = {p.split("=", 1)[0].lower(): (p.split("=", 1)[1] if "=" in p else "")
                 for p in parts[1:]}
        for a in ("secure", "httponly", "samesite", "domain", "path", "max-age"):
            if a in attrs:
                kv(a, attrs[a] or "set")
            else:
                sev = {"secure": "medium", "httponly": "medium", "samesite": "high"}.get(a)
                if sev:
                    print(f"    {sev_tag(sev)} missing {a}")
        val = name_val.split("=", 1)[1] if "=" in name_val else ""
        if val.count(".") == 2 and val.startswith("eyJ"):
            hit("value looks like a JWT")
        if val:
            ent = entropy(val)
            kv("entropy", f"{ent:.2f} bits/char")
            if ent > 4.2:
                hit("high entropy — random session token")
            elif ent < 2.5:
                wrn("low entropy — possibly predictable")


def mod_mail_armor():
    domain = ask("domain", "example.com").lower()
    inf(f"analysing mail authentication for {domain}")
    txts = doh(domain, "TXT")
    print()
    rule("SPF")
    spf = [t for t in txts if "v=spf1" in t]
    if not spf:
        bad("no SPF record — spoofable")
    for s in spf:
        kv("record", s[:200])
        tail = s.rstrip()
        if tail.endswith("-all"):
            ok("hard fail (-all)")
        elif tail.endswith("~all"):
            wrn("soft fail (~all)")
        elif tail.endswith("+all"):
            wrn("+all — anything passes")
    print()
    rule("DMARC")
    dm = doh("_dmarc." + domain, "TXT")
    if not dm:
        bad("no DMARC record")
    for r in dm:
        kv("record", r[:250])
        if "p=none" in r:
            wrn("p=none — monitoring only")
    print()
    rule("DKIM SELECTORS")
    hits = 0
    for sel in ("default", "google", "selector1", "selector2", "k1", "s1", "mail",
                "dkim", "mandrill", "sendgrid", "amazonses"):
        rec = doh(f"{sel}._domainkey.{domain}", "TXT")
        if rec:
            hits += 1
            hit(f"{sel} -> {rec[0][:90]}")
    if not hits:
        bad("no common dkim selectors found")
    print()
    rule("OTHER")
    for rec, label in (("_mta-sts." + domain, "MTA-STS"),
                       ("_smtp._tls." + domain, "TLS-RPT")):
        r = doh(rec, "TXT")
        kv(label, r[0][:150] if r else "absent")
    print()
    kv("spf exists", "yes" if spf else "NO")
    kv("dmarc exists", "yes" if dm else "NO")
    if not dm or not spf:
        wrn("domain is likely spoofable")


def mod_gql_mapper():
    url = ask("graphql endpoint", "https://example.com/graphql")
    if "://" not in url:
        url = "https://" + url
    intro = {"query": "query{__schema{queryType{name} mutationType{name} "
                      "types{name kind fields{name args{name}}}}}"}
    st, body, _ = http_post(url, intro, timeout=25)
    kv("status", st)
    d = jload(body)
    if not d or "data" not in d:
        bad("introspection disabled or wrong endpoint")
        base = url.rsplit("/", 1)[0]
        for p in ("graphql", "graphiql", "api/graphql", "v1/graphql", "__graphql"):
            s2, b2, _ = http_post(f"{base}/{p}", {"query": "{__typename}"}, timeout=10)
            if s2 in (200, 400) and b2 and b'"data"' in b2:
                hit(f"{base}/{p}  ({s2})")
        return
    schema = d["data"]["__schema"]
    ok("introspection enabled")
    kv("query root", (schema.get("queryType") or {}).get("name"))
    kv("mutation root", (schema.get("mutationType") or {}).get("name"))
    types = [t for t in schema.get("types", []) if not t["name"].startswith("__")]
    kv("types", len(types))
    print()
    rule("QUERY FIELDS")
    for t in types:
        if t["name"] == (schema.get("queryType") or {}).get("name"):
            for f in (t.get("fields") or [])[:80]:
                args = ", ".join(a["name"] for a in (f.get("args") or []))
                print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{f['name']}"
                      f"{RESET}{fg(TH['dim'])}({args}){RESET}")
    print()
    rule("MUTATIONS")
    for t in types:
        if t["name"] == (schema.get("mutationType") or {}).get("name"):
            for f in (t.get("fields") or [])[:60]:
                print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{f['name']}{RESET}")
    print()
    rule("SECURITY NOTES")
    if (schema.get("mutationType") or {}).get("name"):
        hit("mutations exposed — check auth on writes")
    for t in types:
        for f in (t.get("fields") or []):
            if f["name"] in ("password", "passwordHash", "secret", "token", "isAdmin"):
                hit(f"{t['name']}.{f['name']}")
    save_json("wt_graphql.json", {"types": [t["name"] for t in types]})


def mod_stego_lab():
    path = ask("image path (png)", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    with open(path, "rb") as f:
        data = f.read(12_000_000)
    kv("file", os.path.abspath(path))
    kv("size", human(len(data)))
    print()
    rule("TRAILING DATA AFTER EOF")
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        i, last = 8, 8
        while i + 8 <= len(data):
            ln = int.from_bytes(data[i:i + 4], "big")
            typ = data[i + 4:i + 8]
            i += 12 + ln
            if typ == b"IEND":
                last = i
                break
        if len(data) > last:
            tail = data[last:]
            hit(f"{len(tail)} byte(s) appended after IEND")
            kv("tail preview", tail[:120].decode("latin-1", "replace"))
            if tail[:2] == b"PK":
                hit("tail looks like a ZIP")
            if ask("write tail to file? (y/n)", "y").startswith("y"):
                with open(path + ".tail", "wb") as f:
                    f.write(tail)
                ok("written")
        else:
            bad("no trailing data")
    elif data[:2] == b"\xff\xd8":
        idx = data.rfind(b"\xff\xd9")
        if idx >= 0 and idx + 2 < len(data):
            hit(f"{len(data) - idx - 2} byte(s) after JPEG EOI")
        else:
            bad("no trailing data")
    print()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return
    rule("PNG CHUNK MAP")
    i, chunks = 8, []
    while i + 8 <= len(data):
        ln = int.from_bytes(data[i:i + 4], "big")
        typ = data[i + 4:i + 8].decode("latin-1")
        chunks.append((typ, ln))
        i += 12 + ln
        if typ == "IEND":
            break
    for typ, ln in chunks:
        color = TH["dim"] if typ in ("IDAT", "IHDR", "IEND") else (255, 200, 110)
        print(f"    {fg(color)}{typ:<6}{RESET} {fg(TH['text'])}{ln:,} bytes{RESET}")
    print()
    if ask("extract LSB bit-plane? (y/n)", "y").lower().startswith("y"):
        try:
            w, h, rows = png_load(data)
        except Exception as e:
            bad(f"decode failed: {e}")
            return
        bits = []
        for row in rows:
            for px in row:
                for ch in px[:3]:
                    bits.append(ch & 1)
        bitstr = "".join(str(b) for b in bits[:80_000])
        chars = []
        for j in range(0, len(bitstr) - 8, 8):
            v = int(bitstr[j:j + 8], 2)
            if v == 0 and len(chars) > 4:
                break
            chars.append(chr(v) if 31 < v < 127 or v in (10, 13) else ".")
        text = "".join(chars)
        if len(text) > 8:
            hit("LSB leading bytes:")
            for line in textwrap.wrap(text[:600], 100)[:8]:
                print(f"      {fg(TH['text'])}{line}{RESET}")
        ones = sum(bits)
        kv("lsb balance", f"{100 * ones / max(1, len(bits)):.2f}% ones")


def mod_cipher_deck():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}caesar brute force{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}vigenere{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}rail fence{RESET}")
    print(f"    {fg(TH['key'])}[4]{RESET} {fg(TH['text'])}frequency analysis{RESET}")
    print()
    pick = ask("choice", "1")
    text = ask("ciphertext", "Khoor Zruog")
    if pick == "1":
        for shift in range(26):
            out = "".join(
                chr((ord(c) - 65 - shift) % 26 + 65) if c.isupper() else
                chr((ord(c) - 97 - shift) % 26 + 97) if c.islower() else c
                for c in text)
            print(f"    {fg(TH['key'])}rot{shift:<3}{RESET} {fg(TH['text'])}{out[:96]}{RESET}")
    elif pick == "2":
        key = ask("key", "lemon")
        ki, out = 0, []
        for c in text:
            if c.isalpha():
                k = ord(key[ki % len(key)].lower()) - 97
                base = 65 if c.isupper() else 97
                out.append(chr((ord(c) - base - k) % 26 + base))
                ki += 1
            else:
                out.append(c)
        kv("decrypted", "".join(out)[:200])
    elif pick == "3":
        for rails in range(2, 7):
            pattern = list(range(rails)) + list(range(rails - 2, 0, -1))
            n = len(text)
            idx = [pattern[i % len(pattern)] for i in range(n)]
            order = sorted(range(n), key=lambda i: (idx[i], i))
            out = [""] * n
            for pos, ch in zip(order, text):
                out[pos] = ch
            print(f"    {fg(TH['key'])}rails={rails}{RESET} {fg(TH['text'])}"
                  f"{''.join(out)[:90]}{RESET}")
    else:
        letters = [c.upper() for c in text if c.isalpha()]
        if not letters:
            bad("no letters")
            return
        counts = Counter(letters)
        total = len(letters)
        top = counts.most_common(1)[0][1]
        for ch, n in counts.most_common(26):
            bar = "█" * int(n / max(1, top) * 40)
            print(f"    {fg(TH['key'])}{ch}{RESET} {fg(TH['accent'])}{bar}{RESET} "
                  f"{fg(TH['dim'])}{n} ({100 * n / total:.1f}%){RESET}")
        ic = sum(n * (n - 1) for n in counts.values()) / max(1, total * (total - 1))
        kv("index of coincidence", f"{ic:.4f}")


def mod_archive_dive():
    path = ask("archive / office file path", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    dest = ask("extract to", os.path.splitext(path)[0] + "_extracted")
    lower = path.lower()
    print()
    if lower.endswith((".zip", ".jar", ".apk", ".docx", ".xlsx", ".pptx", ".epub")):
        try:
            with zipfile.ZipFile(path) as z:
                inf(f"{len(z.namelist())} entries")
                for i in z.infolist():
                    print(f"    {fg(TH['text'])}{i.filename[:80]:<80}{RESET} "
                          f"{fg(TH['dim'])}{i.file_size:>10,}{RESET}")
                if ask("extract all? (y/n)", "y").lower().startswith("y"):
                    safe_extract(z, dest)
                    ok("extracted -> " + os.path.abspath(dest))
                for name in z.namelist():
                    if name.endswith("docProps/core.xml"):
                        try:
                            xml = z.read(name).decode("utf-8", "replace")
                            for k in ("dc:creator", "cp:lastModifiedBy", "Company"):
                                m = re.search(r"<" + k + r"[^>]*>(.*?)</" + k + ">", xml)
                                if m:
                                    kv(k, htmlmod.unescape(m.group(1))[:120])
                        except Exception:
                            pass
        except Exception as e:
            bad(f"zip failed: {e}")
    elif tarfile.is_tarfile(path):
        try:
            with tarfile.open(path) as t:
                inf(f"{len(t.getmembers())} entries")
                for m in t.getmembers()[:200]:
                    print(f"    {fg(TH['text'])}{m.name[:80]:<80}{RESET} "
                          f"{fg(TH['dim'])}{m.size:>10,}{RESET}")
                if ask("extract all? (y/n)", "y").lower().startswith("y"):
                    safe_extract(t, dest)
                    ok("extracted -> " + os.path.abspath(dest))
        except Exception as e:
            bad(f"tar failed: {e}")
    else:
        for opener, label in ((gzip.open, "gzip"), (bz2.open, "bzip2"), (lzma.open, "xz")):
            try:
                with opener(path, "rb") as f:
                    data = f.read(20_000_000)
                out = os.path.splitext(path)[0] + "_out"
                with open(out, "wb") as f:
                    f.write(data)
                ok(f"{label} decompressed -> {out}")
                return
            except Exception:
                continue
        bad("unrecognised archive")


def mod_eml_parser():
    path = ask(".eml / raw header file path", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    with open(path, "rb") as f:
        raw = f.read(4_000_000)
    text = raw.decode("utf-8", "replace")
    head, _, body = text.partition("\n\n")
    print()
    rule("HEADERS")
    received = []
    for line in head.splitlines():
        if line.startswith((" ", "\t")):
            continue
        k, _, v = line.partition(":")
        k, v = k.strip().lower(), v.strip()
        if not k:
            continue
        if k == "received":
            received.append(v)
        else:
            kv(k, v[:150])
    print()
    if received:
        rule("RECEIVED CHAIN")
        for i, r in enumerate(received):
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{r[:150]}{RESET}")
            ipm = re.search(r"\[?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]?", r)
            if ipm:
                ip = ipm.group(1)
                kv(f"  hop {i}", f"{ip}  ptr={reverse_dns(ip) or '-'}")
    print()
    rule("AUTH RESULTS")
    for line in head.splitlines():
        low = line.lower()
        if low.startswith(("authentication-results", "received-spf", "dkim-signature")):
            kv(line.split(":", 1)[0], line.split(":", 1)[1].strip()[:170])
    print()
    urls = sorted(set(re.findall(r"https?://[^\s\"'<>)\]]{6,140}", text)))
    if urls:
        rule("URLS")
        for u in urls[:40]:
            hit(u[:130])
    print()
    rule("BODY PREVIEW")
    for line in re.sub(r"\n{3,}", "\n\n", body or head).splitlines()[:30]:
        print(f"    {fg(TH['text'])}{line[:118]}{RESET}")


def mod_time_shift():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}timestamp -> human{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}human -> timestamp{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        raw = ask("value (epoch seconds/ms/us/ns)", "")
        if not raw:
            return
        v = re.sub(r"[^\d.]", "", raw)
        try:
            f = float(v)
        except Exception:
            bad("not numeric")
            return
        for div, lbl in ((1e9, "nanoseconds"), (1e6, "microseconds"),
                         (1e3, "milliseconds"), (1, "seconds")):
            secs = f / div
            if not (0 < secs < 4e9):
                continue
            try:
                dt = datetime.fromtimestamp(secs, timezone.utc)
            except Exception:
                continue
            kv(lbl, dt.strftime("%Y-%m-%d %H:%M:%S UTC"))
            kv("  iso", dt.isoformat())
            kv("  relative", fmt_dur(abs(time.time() - secs)) +
               (" ago" if secs < time.time() else " ahead"))
            print()
    else:
        raw = ask("date string", "2024-01-31 12:00:00")
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
                    "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            except Exception:
                continue
            kv("format", fmt)
            kv("epoch (s)", int(dt.timestamp()))
            kv("epoch (ms)", int(dt.timestamp() * 1000))
            kv("iso", dt.isoformat())
            return
        bad("could not parse")


IDN_CONFUSABLES = {
    "a": ["а", "ɑ", "α"], "b": ["Ь", "ƅ"], "c": ["с", "ϲ"], "d": ["ԁ", "ⅾ"],
    "e": ["е", "℮"], "h": ["һ", "հ"], "i": ["і", "ı", "ⅰ"], "j": ["ј", "ϳ"],
    "k": ["κ", "к"], "l": ["ӏ", "ⅼ", "1"], "m": ["м", "ⅿ"], "n": ["п", "ո"],
    "o": ["о", "ο", "0"], "p": ["р", "ρ"], "q": ["ԛ", "զ"], "s": ["ѕ", "ś"],
    "t": ["т", "τ"], "u": ["υ", "ս"], "v": ["ν", "ⅴ"], "w": ["ԝ", "ω"],
    "x": ["х", "ⅹ"], "y": ["у", "γ"], "z": ["ᴢ", "ƶ"],
}


def mod_idn_lens():
    s = ask("domain or string to inspect", "examp1e.com")
    kv("input", s)
    try:
        kv("punycode", s.encode("idna").decode())
    except Exception:
        pass
    print()
    rule("CHARACTER BREAKDOWN")
    for i, ch in enumerate(s):
        cp = ord(ch)
        if cp > 126 or not ch.isalnum():
            print(f"    {fg(TH['key'])}[{i:>3}]{RESET} {fg(TH['text'])}{ch!r} "
                  f"U+{cp:04X}{RESET} "
                  f"{fg(TH['dim'])}{unicodedata.name(ch, '?')[:40]}{RESET}")
    print()
    rule("INVISIBLE / SUSPICIOUS")
    for label, ch, cp in (("zero-width space", "\u200b", 0x200B),
                          ("zero-width joiner", "\u200d", 0x200D),
                          ("zero-width non-joiner", "\u200c", 0x200C),
                          ("soft hyphen", "\u00ad", 0x00AD),
                          ("word joiner", "\u2060", 0x2060)):
        if ch in s:
            wrn(f"{label} present (U+{cp:04X})")
    print()
    rule("HOMOGLYPH RISK")
    for c in s.lower():
        if c in IDN_CONFUSABLES:
            print(f"    {fg(TH['key'])}{c}{RESET} could be one of: "
                  f"{fg(TH['text'])}{''.join(IDN_CONFUSABLES[c])}{RESET}")
    print()
    visual = s.replace("0", "o").replace("1", "l").replace("3", "e").replace("5", "s")
    kv("de-leeted", visual)
    if visual != s:
        inf("de-leeted form differs — homoglyph spoof likely")


def mod_hex_forge():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}hex dump a file{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}base converter{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}bit operations{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        path = ask("file path", "")
        if not os.path.isfile(path):
            bad("not found")
            return
        off = int(ask("start offset", "0") or 0)
        ln = int(ask("length", "512") or 512)
        with open(path, "rb") as f:
            f.seek(off)
            data = f.read(ln)
        print()
        for i in range(0, len(data), 16):
            chunk = data[i:i + 16]
            hexpart = " ".join(f"{b:02x}" for b in chunk)
            asc = "".join(chr(b) if 31 < b < 127 else "." for b in chunk)
            print(f"  {fg(TH['dim'])}{off + i:08x}{RESET}  "
                  f"{fg(TH['text'])}{hexpart:<47}{RESET}  {fg(TH['key'])}{asc}{RESET}")
    elif pick == "2":
        val = ask("value", "255")
        print()
        try:
            n = int(val, 0)
        except Exception:
            bad("not a number")
            return
        kv("decimal", n)
        kv("hex", hex(n))
        kv("octal", oct(n))
        kv("binary", bin(n))
        kv("base36", _tobase(n, 36))
        kv("bit length", n.bit_length())
    else:
        a = ask("value a", "0xF0")
        op = ask("op (and/or/xor/shl/shr/not)", "xor")
        b = ask("value b", "0x0F")
        try:
            x, y = int(a, 0), int(b, 0)
        except Exception:
            bad("bad numbers")
            return
        res = {"and": x & y, "or": x | y, "xor": x ^ y, "shl": x << y, "shr": x >> y,
               "not": ~x}.get(op.lower())
        if res is None:
            bad("unknown op")
            return
        kv("result", res)
        kv("hex", hex(res))
        kv("binary", bin(res))


def _tobase(n, b):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if n == 0:
        return "0"
    out, neg = "", n < 0
    n = abs(n)
    while n:
        n, r = divmod(n, b)
        out = digits[r] + out
    return ("-" if neg else "") + out


CARVE_SIGS = [
    (b"\xff\xd8\xff", b"\xff\xd9", "jpg", "JPEG image"),
    (b"\x89PNG\r\n\x1a\n", b"IEND\xaeB`\x82", "png", "PNG image"),
    (b"%PDF", b"%%EOF", "pdf", "PDF document"),
    (b"PK\x03\x04", b"PK\x05\x06", "zip", "ZIP archive"),
    (b"GIF89a", b"\x3b", "gif", "GIF image"),
    (b"Rar!\x1a\x07", None, "rar", "RAR archive"),
    (b"\x1f\x8b", None, "gz", "gzip stream"),
    (b"SQLite format 3\x00", None, "sqlite", "SQLite database"),
    (b"OggS", None, "ogg", "Ogg container"),
    (b"fLaC", None, "flac", "FLAC audio"),
    (b"ID3", None, "mp3", "MP3 audio"),
]


def mod_file_carver():
    path = ask("file to carve (disk image / blob)", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    outdir = ask("output folder", "wt_carved")
    os.makedirs(outdir, exist_ok=True)
    with open(path, "rb") as f:
        data = f.read(64_000_000)
    kv("file", os.path.abspath(path))
    kv("size", human(len(data)))
    total = 0
    for sig, term, ext, label in CARVE_SIGS:
        start, count = 0, 0
        while True:
            i = data.find(sig, start)
            if i < 0 or count >= 40:
                break
            if term:
                j = data.find(term, i)
                end = j + len(term) if j >= 0 else min(len(data), i + 8_000_000)
            else:
                end = min(len(data), i + 4_000_000)
            blob = data[i:end]
            if len(blob) < 64:
                start = i + 1
                continue
            dest = os.path.join(outdir, f"carved_{count:03d}_{i:x}.{ext}")
            try:
                with open(dest, "wb") as f:
                    f.write(blob)
                print(f"  {sev_tag('info')} {label:<18} offset 0x{i:x} "
                      f"{human(len(blob))}")
                count += 1
                total += 1
                LIVE["hits"] += 1
            except Exception:
                pass
            start = i + 1
    print()
    inf(f"{total} object(s) carved into {os.path.abspath(outdir)}")


def mod_qr_lens():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}decode a qr image{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}generate a qr{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        path = ask("image path (png/jpg)", "")
        if not os.path.isfile(path):
            bad("not found")
            return
        with open(path, "rb") as f:
            blob = f.read(6_000_000)
        ct = "image/png" if path.lower().endswith(".png") else "image/jpeg"
        body, ctype = multipart({}, {"file": (os.path.basename(path), blob, ct)})
        st, resp, _ = http_post("https://api.qrserver.com/v1/read-qr-code/", raw=body,
                                ctype=ctype, timeout=25)
        d = jload(resp)
        if not d:
            bad("decode service failed")
            return
        for item in d:
            for sym in item.get("symbol", []):
                if sym.get("data"):
                    hit("decoded:")
                    for line in str(sym["data"]).splitlines()[:20]:
                        print(f"    {fg(TH['text'])}{line[:110]}{RESET}")
                    LIVE["hits"] += 1
                else:
                    bad(f"error: {sym.get('error')}")
    else:
        data = ask("text or url to encode")
        if not data:
            return
        spin("rendering qr code")
        url = ("https://api.qrserver.com/v1/create-qr-code/?format=png&margin=0&size="
               f"180x180&data={urllib.parse.quote(data)}")
        st, body, _ = http_get(url, timeout=20)
        if st != 200 or not body:
            bad("qr service unreachable")
            return
        try:
            w, h, rows = png_load(body)
        except Exception as e:
            bad(f"decode failed: {e}")
            return
        step = max(1, w // 70)
        print()
        for y in range(0, max(1, h - step), step * 2):
            line = []
            for x in range(0, w, step):
                top = sum(rows[y][x]) / 3 < 128
                bot = sum(rows[min(h - 1, y + step)][x]) / 3 < 128
                tc = (10, 10, 10) if top else (250, 250, 250)
                bc = (10, 10, 10) if bot else (250, 250, 250)
                line.append(f"{fg(tc)}{bg(bc)}▀")
            print("  " + "".join(line) + RESET)
        print()
        inf(f"encoded {len(data)} chars")


# ------------------------- NEW CSINT (79-82) ------------------------------- #
def mod_binary_diff():
    a = ask("first file", "")
    b = ask("second file", "")
    if not (os.path.isfile(a) and os.path.isfile(b)):
        bad("both paths must exist")
        return
    with open(a, "rb") as f:
        da = f.read(16_000_000)
    with open(b, "rb") as f:
        db = f.read(16_000_000)
    kv("a", f"{os.path.basename(a)}  {human(len(da))}")
    kv("b", f"{os.path.basename(b)}  {human(len(db))}")
    kv("length delta", f"{len(db) - len(da):+d}")
    if da == db:
        ok("files are byte-identical")
        return
    diffs = [i for i in range(min(len(da), len(db))) if da[i] != db[i]]
    kv("differing bytes", len(diffs))
    if diffs:
        kv("first offset", f"0x{diffs[0]:08x}")
        kv("last offset", f"0x{diffs[-1]:08x}")
    print()
    rule("WINDOWS")
    for off in diffs[:20]:
        lo = max(0, off - 6)
        win_a = da[lo:off + 7].hex(" ")
        win_b = db[lo:off + 7].hex(" ")
        print(f"  {fg(TH['dim'])}0x{off:08x}{RESET}")
        print(f"    {fg((255,140,120))}a{RESET} {win_a}")
        print(f"    {fg((140,255,190))}b{RESET} {win_b}")
    if len(diffs) > 20:
        bad(f"  ... {len(diffs) - 20} more")


def mod_crypto_oracle():
    data = ask("input string")
    if not data:
        return
    kv("input", data[:120])
    kv("length", len(data))
    kv("entropy", f"{entropy(data):.3f} bits/char")
    print()
    rule("DIGESTS")
    for a in hash_algos():
        try:
            kv(a, hashlib.new(a, data.encode()).hexdigest())
        except Exception:
            pass
    kv("crc32", f"{zlib.crc32(data.encode()) & 0xFFFFFFFF:08x}")
    kv("adler32", f"{zlib.adler32(data.encode()) & 0xFFFFFFFF:08x}")
    print()
    rule("HMAC")
    key = ask("hmac key (blank to skip)", "")
    if key:
        for a in ("md5", "sha1", "sha256", "sha512"):
            kv(f"hmac-{a}", hmac.new(key.encode(), data.encode(), a).hexdigest())
    print()
    rule("KDF")
    salt = os.urandom(16)
    kv("salt", salt.hex())
    for iters in (1, 1000, 10000):
        kv(f"pbkdf2-sha256/{iters}",
           hashlib.pbkdf2_hmac("sha256", data.encode(), salt, iters, 32).hex()[:64])
    try:
        kv("scrypt", hashlib.scrypt(data.encode(), salt=salt, n=2 ** 14, r=8, p=1,
                                    dklen=32).hex())
    except Exception:
        pass
    print()
    rule("ENCODINGS")
    kv("base64", base64.b64encode(data.encode()).decode())
    kv("base32", base64.b32encode(data.encode()).decode())
    kv("hex", data.encode().hex())
    kv("url", urllib.parse.quote(data))


def mod_key_lens():
    path = ask("key / cert file path (pem, pub, asc)", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    with open(path, "rb") as f:
        raw = f.read(2_000_000)
    text = raw.decode("utf-8", "replace")
    kv("file", os.path.abspath(path))
    kv("size", human(len(raw)))
    print()
    blocks = re.findall(r"-----BEGIN ([A-Z0-9 ]+)-----(.*?)-----END \1-----", text, re.S)
    if not blocks:
        bad("no PEM armour found")
        return
    for label, body in blocks:
        rule(label)
        try:
            der = base64.b64decode(re.sub(r"\s", "", body))
        except Exception:
            bad("undecodable body")
            continue
        kv("der size", f"{len(der)} bytes")
        kv("md5 fp", hashlib.md5(der).hexdigest())
        kv("sha256 fp", hashlib.sha256(der).hexdigest())
        if "RSA" in label:
            bits = None
            m = re.search(rb"\x02\x82(..)", der)
            if m:
                bits = (int.from_bytes(m.group(1), "big") - 1) * 8
            if bits:
                kv("approx bits", bits)
                if bits < 2048:
                    wrn("key shorter than 2048 bits")
        if "EC" in label:
            kv("curve hint", "EC key — inspect the OID")
            for curve, oid in (("prime256v1", b"\x2a\x86\x48\xce\x3d\x03\x01\x07"),
                               ("secp384r1", b"\x2b\x81\x04\x00\x22"),
                               ("secp521r1", b"\x2b\x81\x04\x00\x23"),
                               ("ed25519", b"\x2b\x65\x70")):
                if oid in der:
                    kv("curve", curve)
        if "PGP" in label:
            for line in text.splitlines():
                if line.startswith(("Comment:", "Version:", "Hash:")):
                    kv("armour header", line[:100])
    print()
    if "PRIVATE KEY" in text:
        hit("contains private material")
    if "BEGIN CERTIFICATE" in text:
        hit("contains a certificate")


def mod_image_forensics():
    path = ask("jpeg / png path", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    with open(path, "rb") as f:
        data = f.read(24_000_000)
    kv("file", os.path.abspath(path))
    kv("size", human(len(data)))
    if data[:2] != b"\xff\xd8":
        bad("not a jpeg (png handled by the stego module)")
        return
    print()
    rule("SEGMENTS")
    i, guard = 2, 0
    qtables = 0
    sof = None
    while i + 4 <= len(data) and guard < 20000:
        guard += 1
        if data[i] != 0xFF:
            i += 1
            continue
        mk = data[i + 1]
        if mk == 0xDA:
            kv("scan data starts", f"0x{i:08x}")
            break
        if mk in (0xD8, 0x01) or 0xD0 <= mk <= 0xD7:
            i += 2
            continue
        ln = int.from_bytes(data[i + 2:i + 4], "big")
        if ln < 2:
            break
        seg = data[i + 4:i + 2 + ln]
        if mk == 0xDB:
            qtables += 1
            kv(f"dqt #{qtables}", f"offset 0x{i:08x} len {ln}")
            vals = [b for b in seg[1:17]]
            kv("  first 16 coefficients", " ".join(str(v) for v in vals))
            if len(set(vals)) > 12:
                wrn("  table looks high-quality / not recompressed")
            else:
                inf("  table looks quantised (possible recompression)")
        elif mk in (0xC0, 0xC1, 0xC2):
            sof = mk
            h = int.from_bytes(seg[1:3], "big")
            w = int.from_bytes(seg[3:5], "big")
            comps = seg[5]
            kv("frame", f"{w}x{h} {comps} component(s) "
                        f"{'progressive' if mk == 0xC2 else 'baseline'}")
        elif mk == 0xFE:
            kv("comment", seg[:160].decode("latin-1", "replace"))
        elif mk == 0xE0:
            kv("jfif", seg[:14].decode("latin-1", "replace").strip())
        elif 0xE1 <= mk <= 0xEF:
            kv(f"app{mk - 0xE0}", seg[:90].decode("latin-1", "replace").replace("\n", " "))
        i += 2 + ln
    print()
    rule("ASSESSMENT")
    kv("quantisation tables", qtables)
    if qtables > 1:
        wrn("multiple quantisation tables — possible double compression / editor save")
    if sof:
        kv("frame type", "progressive" if sof == 0xC2 else "baseline")
    thumbs = len(re.findall(rb"Thumbnail", data))
    kv("thumbnail markers", thumbs)
    if thumbs:
        inf("embedded exif thumbnail present — try extracting it")
    print()
    rule("TRAILING DATA")
    idx = data.rfind(b"\xff\xd9")
    if idx >= 0 and idx + 2 < len(data):
        hit(f"{len(data) - idx - 2} byte(s) after EOI")
        kv("tail preview", data[idx + 2:idx + 122].decode("latin-1", "replace"))
    else:
        bad("clean end of image")


# -------------------------------- png -------------------------------------- #
def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unpack_bits(line, w, bd):
    if bd == 8:
        return list(line[:w])
    out = []
    per = 8 // bd
    for x in range(w):
        b = line[x // per]
        shift = 8 - bd * (x % per + 1)
        out.append((b >> shift) & ((1 << bd) - 1))
    return out


def png_load(buf):
    if buf[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a png")
    i, idat, w, h, bd, ct, plte = 8, b"", 0, 0, 8, 2, None
    while i + 8 <= len(buf):
        ln = int.from_bytes(buf[i:i + 4], "big")
        typ = buf[i + 4:i + 8]
        body = buf[i + 8:i + 8 + ln]
        if typ == b"IHDR":
            w = int.from_bytes(body[0:4], "big")
            h = int.from_bytes(body[4:8], "big")
            bd = body[8]
            ct = body[9]
            if body[12] != 0:
                raise ValueError("interlaced png unsupported")
        elif typ == b"PLTE":
            plte = body
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        i += 12 + ln
    if bd == 16:
        bd = 8
    raw = zlib.decompress(idat)
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    stride = (w * ch * bd + 7) // 8
    bpp = max(1, ch * bd // 8)
    prev = bytearray(stride)
    rows = []
    pos = 0
    for _y in range(h):
        ft = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        if ft == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif ft == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif ft == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                c = prev[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + _paeth(a, prev[x], c)) & 255
        if ct == 3:
            mx = (1 << bd) - 1
            row = []
            for v in _unpack_bits(line, w, bd):
                k = int(v * 255 / mx) * 3
                if plte and k + 2 < len(plte):
                    row.append((plte[k], plte[k + 1], plte[k + 2]))
                else:
                    row.append((0, 0, 0))
        elif ct in (0, 4):
            mx = (1 << bd) - 1
            row = [(v * 255 // mx,) * 3 for v in _unpack_bits(line, w, bd)]
        elif ct == 2:
            row = [(line[x * 3], line[x * 3 + 1], line[x * 3 + 2]) for x in range(w)]
        else:
            row = [(line[x * 4], line[x * 4 + 1], line[x * 4 + 2]) for x in range(w)]
        rows.append(row)
        prev = line
    return w, h, rows


def render_ascii(img, cols=64, ramp=" .:-=+*#%@"):
    w, h, rows = img
    if w == 0 or h == 0:
        return
    step = max(1, w // cols)
    for y in range(0, h, step * 2):
        line = []
        for x in range(0, w, step):
            r, g, b = rows[y][x]
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            col = lerp((20, 30, 45), TH["accent"], lum) if SETTINGS["truecolor"] \
                else TH["accent"]
            line.append(fg(col) + ramp[int(lum * (len(ramp) - 1))])
        print("  " + "".join(line) + RESET)


# =========================================================================== #
#  UTILITIES
# =========================================================================== #

class Mailbox:
    PROVIDERS = ["mail.tm", "mail.gw", "tempmail.lol", "guerrillamail"]

    def __init__(self):
        self.provider = None
        self.address = None
        self.token = None
        self.sid = None
        self.base = None

    def _mailtm(self, base):
        d = get_json(base + "/domains", timeout=12)
        doms = [x.get("domain") for x in (d or {}).get("hydra:member", []) if x.get("domain")]
        doms = [x for x in doms if "private" not in x]
        for _ in range(3):
            if not doms:
                break
            login = "wt" + "".join(random.choice(string.ascii_lowercase + string.digits)
                                   for _ in range(10))
            pwd = "".join(random.choice(string.ascii_letters + string.digits)
                          for _ in range(20))
            addr = f"{login}@{random.choice(doms)}"
            st, _, _ = http_post(base + "/accounts", {"address": addr, "password": pwd},
                                 timeout=12)
            if st not in (200, 201):
                continue
            st2, body2, _ = http_post(base + "/token", {"address": addr, "password": pwd},
                                      timeout=12)
            tok = (jload(body2) or {}).get("token") if st2 == 200 else None
            if tok:
                self.token, self.address, self.base = tok, addr, base
                return True
        return False

    def _tempmail_lol(self):
        st, body, _ = http_post("https://api.tempmail.lol/v2/inbox/create", {}, timeout=15)
        d = jload(body) if st in (200, 201) else None
        if d and d.get("address") and d.get("token"):
            self.address, self.token = d["address"], d["token"]
            return True
        return False

    def _guerrilla(self):
        st, body, _ = http_get(
            "https://api.guerrillamail.com/ajax.php?f=get_email_address&lang=en", timeout=15)
        d = jload(body)
        if d and d.get("email_addr"):
            self.address = d["email_addr"]
            self.sid = d.get("sid_token")
            return True
        return False

    def create(self):
        for name in self.PROVIDERS:
            try:
                if name == "mail.tm" and self._mailtm("https://api.mail.tm"):
                    self.provider = name
                    return True
                if name == "mail.gw" and self._mailtm("https://api.mail.gw"):
                    self.provider = name
                    return True
                if name == "tempmail.lol" and self._tempmail_lol():
                    self.provider = name
                    return True
                if name == "guerrillamail" and self._guerrilla():
                    self.provider = name
                    return True
            except Exception:
                continue
        return False

    def inbox(self):
        try:
            if self.provider in ("mail.tm", "mail.gw"):
                st, body, _ = http_get(self.base + "/messages", timeout=15,
                                       headers={"Authorization": "Bearer " + self.token,
                                                "Accept": "application/json"})
                if st != 200:
                    return []
                items = (jload(body) or {}).get("hydra:member", [])
                return [{"id": m.get("id"),
                         "from": (m.get("from") or {}).get("address", "?"),
                         "subject": m.get("subject") or "(no subject)",
                         "date": str(m.get("createdAt", ""))[:19].replace("T", " ")}
                        for m in items]
            if self.provider == "tempmail.lol":
                st, body, _ = http_get("https://api.tempmail.lol/v2/inbox?token=" + self.token,
                                       timeout=15)
                d = jload(body) or {}
                return [{"id": m.get("id") or m.get("date"), "from": m.get("from", "?"),
                         "subject": m.get("subject") or "(no subject)",
                         "date": str(m.get("date", ""))[:19]}
                        for m in d.get("emails", [])]
            st, body, _ = http_get("https://api.guerrillamail.com/ajax.php?f=check_email"
                                   f"&sid_token={self.sid}&seq=0", timeout=15)
            d = jload(body) or {}
            return [{"id": m.get("mail_id"), "from": m.get("mail_from", "?"),
                     "subject": m.get("mail_subject") or "(no subject)",
                     "date": str(m.get("mail_timestamp", ""))}
                    for m in d.get("list", [])]
        except Exception:
            return []

    def read(self, mid):
        try:
            if self.provider in ("mail.tm", "mail.gw"):
                st, body, _ = http_get(f"{self.base}/messages/{mid}", timeout=15,
                                       headers={"Authorization": "Bearer " + self.token,
                                                "Accept": "application/json"})
                if st != 200:
                    return None
                d = jload(body) or {}
                txt = d.get("text") or ""
                if not txt and d.get("html"):
                    raw = d["html"]
                    raw = raw[0] if isinstance(raw, list) else raw
                    txt = strip_tags(re.sub(r"<(br|/p|/div|/tr)[^>]*>", "\n", raw))
                return {"from": (d.get("from") or {}).get("address", "?"),
                        "subject": d.get("subject") or "(no subject)",
                        "date": str(d.get("createdAt", ""))[:19].replace("T", " "),
                        "text": txt}
            if self.provider == "tempmail.lol":
                st, body, _ = http_get("https://api.tempmail.lol/v2/inbox?token=" + self.token,
                                       timeout=15)
                for m in (jload(body) or {}).get("emails", []):
                    if str(m.get("id") or m.get("date")) == str(mid):
                        return {"from": m.get("from", "?"), "subject": m.get("subject", "?"),
                                "date": str(m.get("date", ""))[:19],
                                "text": m.get("body") or strip_tags(m.get("html") or "")}
                return None
            st, body, _ = http_get("https://api.guerrillamail.com/ajax.php?f=fetch_email"
                                   f"&sid_token={self.sid}&email_id={mid}", timeout=15)
            d = jload(body) or {}
            body_txt = d.get("mail_body") or ""
            return {"from": d.get("mail_from", "?"), "subject": d.get("mail_subject", "?"),
                    "date": str(d.get("mail_timestamp", "")),
                    "text": strip_tags(body_txt) if body_txt else ""}
        except Exception:
            return None


def mod_temp_mail():
    box = Mailbox()
    spin("provisioning inbox (trying 4 providers)")
    if not box.create():
        bad("every provider failed — check your connection")
        return
    ok(f"live via {box.provider}")
    print()
    print(f"  {fg(TH['accent'])}{BOLD}  {box.address}{RESET}")
    print()
    print(f"  {fg(TH['dim'])}[R] refresh   [W] watch   [O] open   [N] new   [Q] back{RESET}\n")
    seen, msgs = set(), []

    def refresh():
        m = box.inbox()
        if not m:
            bad("inbox empty — mail something to the address above")
            return m
        for i, x in enumerate(m, 1):
            new = x["id"] not in seen
            tag = f"{fg((140,255,190))}NEW{RESET}" if new else f"{fg(TH['dim'])} --{RESET}"
            print(f"  {fg(TH['key'])}[{i:>2}]{RESET} {tag} "
                  f"{fg(TH['text'])}{x['from'][:34]:<34}{RESET}"
                  f"{fg(TH['dim'])}{x['date'][:16]}{RESET}")
            print(f"        {fg(TH['text'])}{x['subject'][:82]}{RESET}")
        if any(x["id"] not in seen for x in m) and SETTINGS["notify"]:
            bell()
            FXS.ping()
        for x in m:
            seen.add(x["id"])
        return m

    while True:
        try:
            cmd = input(f"  {fg(TH['accent'])}mail>{RESET} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if cmd in ("q", "back", ""):
            return
        if cmd in ("r", "refresh"):
            print()
            msgs = refresh()
            print()
        elif cmd in ("w", "watch"):
            print()
            inf("watching — press any key to stop")
            for x in box.inbox():
                seen.add(x["id"])
            start = time.time()
            while time.time() - start < 300:
                if key_pressed():
                    drain_key()
                    break
                time.sleep(3.5)
                for x in box.inbox():
                    if x["id"] not in seen:
                        seen.add(x["id"])
                        bell()
                        print(f"\n  {fg((140,255,190))}━━ NEW MAIL ━━{RESET}")
                        kv("from", x["from"])
                        kv("subject", x["subject"])
            print()
        elif cmd in ("o", "open"):
            if not msgs:
                msgs = box.inbox()
            if not msgs:
                bad("nothing to open")
                continue
            pick = ask(f"number 1-{len(msgs)}", "1")
            try:
                m = msgs[int(pick) - 1]
            except Exception:
                bad("bad selection")
                continue
            full = box.read(m["id"])
            print()
            rule("MESSAGE")
            if not full:
                bad("could not load body")
                continue
            kv("from", full["from"])
            kv("subject", full["subject"])
            print()
            for line in re.sub(r"\n{3,}", "\n\n", full["text"] or "(empty)").splitlines()[:40]:
                print(f"    {fg(TH['text'])}{line[:112]}{RESET}")
            print()
        elif cmd in ("n", "new"):
            if box.create():
                seen, msgs = set(), []
                ok("new address ready")
                print(f"\n  {fg(TH['accent'])}{BOLD}  {box.address}{RESET}\n")
            else:
                bad("could not create")
        else:
            print(f"  {fg(TH['dim'])}use R / W / O / N / Q{RESET}")


def mod_site_mirror():
    url = ask("page url", "https://example.com")
    if "://" not in url:
        url = "https://" + url
    outdir = ask("output folder", "wt_mirror")
    limit = int(ask("max files", "120") or 120)
    st, body, _ = http_get(url, timeout=15)
    if st is None:
        bad("unreachable")
        return
    ok(f"fetched ({st}) {len(body):,} bytes")
    os.makedirs(outdir, exist_ok=True)
    text = body.decode("utf-8", "replace")
    targets = [urllib.parse.urljoin(url, h) for h in
               re.findall(r'(?:src|href)\s*=\s*["\']([^"\'>]+)["\']', text, re.I)
               if not h.startswith(("data:", "mailto:", "javascript:"))]
    targets += [urllib.parse.urljoin(url, m) for m in
                re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", text, re.I)]
    seen, saved, total = set(), 0, 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        jobs = {}
        for t in targets:
            if t in seen:
                continue
            seen.add(t)
            jobs[ex.submit(http_get, t, 15, None, "GET", 6_000_000)] = t
            if len(jobs) >= limit:
                break
        for fut in as_completed(jobs):
            t = jobs[fut]
            try:
                s3, data, _ = fut.result()
            except Exception:
                continue
            if s3 != 200 or not data:
                continue
            p = urllib.parse.urlparse(t)
            rel = p.netloc.replace(":", "_") + p.path
            if rel.endswith("/") or not os.path.splitext(rel)[1]:
                rel += "/index.html"
            dest = os.path.join(outdir, rel.lstrip("/\\"))
            try:
                d = os.path.dirname(dest)
                if d:
                    os.makedirs(d, exist_ok=True)
                with open(dest, "wb") as f:
                    f.write(data)
                saved += 1
                total += len(data)
                ok(f"{len(data):>9,} B  {rel}")
            except Exception:
                pass
    print()
    inf(f"{saved} file(s) · {total / 1024:.1f} KB")


def mod_qr_forge():
    mod_qr_lens()


def mod_ascii_lens():
    path = ask("image path (png; jpeg via PIL)")
    if not os.path.isfile(path):
        bad("not found")
        return
    cols = int(ask("output columns", "90") or 90)
    img = None
    if path.lower().endswith(".png"):
        with open(path, "rb") as f:
            try:
                img = png_load(f.read(12_000_000))
            except Exception as e:
                bad(f"png decode failed: {e}")
    if img is None:
        try:
            from PIL import Image  # type: ignore
            im = Image.open(path).convert("RGB")
            im.thumbnail((cols, cols))
            img = (im.width, im.height,
                   [[im.getpixel((x, y)) for x in range(im.width)]
                    for y in range(im.height)])
            ok("decoded with PIL")
        except Exception:
            bad("needs a png, or install pillow")
            return
    print()
    render_ascii(img, cols=cols)


def mod_pass_forge():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}generate a password{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}generate a passphrase{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}score a password{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        n = int(ask("count", "5") or 5)
        ln = int(ask("length", "24") or 24)
        sets = [string.ascii_lowercase, string.ascii_uppercase, string.digits,
                "!@#$%^&*()-_=+[]{};:,.?"]
        pool = "".join(sets)
        for _ in range(n):
            pw = ""
            for _ in range(400):
                pw = "".join(random.choice(pool) for _ in range(ln))
                if all(any(c in s for c in pw) for s in sets):
                    break
            print(f"    {fg(TH['accent'])}{pw}{RESET}  "
                  f"{fg(TH['dim'])}{ln * math.log2(len(pool)):.1f} bits{RESET}")
    elif pick == "2":
        n = int(ask("words", "4") or 4)
        sep = ask("separator", "-") or "-"
        words = [w for w in COMMON_WORDS if w.isalpha() and len(w) > 3]
        for _ in range(int(ask("count", "5") or 5)):
            pw = sep.join(random.choice(words) for _ in range(n)) + str(random.randint(0, 99))
            print(f"    {fg(TH['accent'])}{pw}{RESET}  "
                  f"{fg(TH['dim'])}{n * math.log2(len(words)):.1f} bits{RESET}")
    else:
        pw = ask("password")
        if not pw:
            return
        pools = 0
        for pat, n in ((r"[a-z]", 26), (r"[A-Z]", 26), (r"\d", 10), (r"[^A-Za-z0-9]", 33)):
            if re.search(pat, pw):
                pools += n
        bits = len(pw) * math.log2(pools) if pools else 0
        kv("length", len(pw))
        kv("charset size", pools)
        kv("entropy", f"{bits:.1f} bits")
        kv("shannon", f"{entropy(pw):.2f} bits/char")
        if bits < 40:
            bad("weak — aim for 60+ bits")
        elif bits < 60:
            wrn("acceptable but short")
        elif bits < 90:
            ok("strong")
        else:
            ok("very strong")
        print()
        kv("md5", hashlib.md5(pw.encode()).hexdigest())
        kv("sha256", hashlib.sha256(pw.encode()).hexdigest())


def mod_net_kit():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}my public ip + geo{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}traceroute{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}dns resolver benchmark{RESET}")
    print(f"    {fg(TH['key'])}[4]{RESET} {fg(TH['text'])}local network info{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        for url in ("https://api.ipify.org?format=json", "https://ifconfig.co/json"):
            d = get_json(url, timeout=12)
            if d:
                for k, v in d.items():
                    kv(k, str(v)[:120])
                break
        kv("local ip", local_ip())
    elif pick == "2":
        target = ask("host", "1.1.1.1")
        cmd = (["tracert", "-h", "20", "-w", "900", target] if IS_WIN
               else ["traceroute", "-m", "20", "-w", "1", target])
        try:
            r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=120)
            for line in r.stdout.decode("utf-8", "replace").splitlines()[:40]:
                print(f"    {fg(TH['text'])}{line[:120]}{RESET}")
        except Exception as e:
            bad(f"failed: {e}")
    elif pick == "3":
        resolvers = [("google", "8.8.8.8"), ("cloudflare", "1.1.1.1"), ("quad9", "9.9.9.9"),
                     ("opendns", "208.67.222.222"), ("adguard", "94.140.14.14")]
        name = ask("domain to resolve", "example.com")
        results = []
        for label, ip in resolvers:
            times = []
            for _ in range(3):
                t0 = time.time()
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(2)
                    q = struct.pack(">HHHHHH", random.randint(1, 65535), 0x0100, 1, 0, 0, 0)
                    q += b"".join(bytes([len(p)]) + p.encode()
                                  for p in name.split(".")) + b"\x00"
                    q += struct.pack(">HH", 1, 1)
                    s.sendto(q, (ip, 53))
                    s.recvfrom(512)
                    s.close()
                    times.append((time.time() - t0) * 1000)
                except Exception:
                    pass
            if times:
                results.append((label, min(times)))
        for label, ms in sorted(results, key=lambda x: x[1]):
            kv(label, f"{'█' * max(1, int(ms / 5))} {ms:.1f} ms")
        if not results:
            bad("all resolvers unreachable")
    else:
        kv("hostname", socket.gethostname())
        kv("local ip", local_ip())
        kv("platform", platform.platform())
        print()
        rule("ARP TABLE")
        for ip, mac in arp_table()[:40]:
            kv(ip, f"{mac}  {oui_lookup(mac) or ''}")


def mod_system_lens():
    kv("whitetiger", f"v{VERSION}")
    kv("python", sys.version.split()[0])
    kv("platform", platform.platform())
    kv("cores", os.cpu_count())
    kv("terminal", f"{tw()}x{th_()}")
    kv("colour", "on" if COLOR else "off")
    print()
    rule("MEMORY")
    try:
        if IS_WIN:
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong),
                            ("c", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong),
                            ("e", ctypes.c_ulonglong)]
            m = MS()
            m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            kv("total", f"{m.ullTotalPhys / 1e9:.1f} GB")
            kv("available", f"{m.ullAvailPhys / 1e9:.1f} GB")
            kv("load", f"{m.dwMemoryLoad}%")
        else:
            with open("/proc/meminfo") as f:
                info = dict(l.split(":") for l in f.read().splitlines())
            tot = int(info["MemTotal"].split()[0]) / 1e6
            avail = int(info["MemAvailable"].split()[0]) / 1e6
            kv("total", f"{tot:.1f} GB")
            kv("available", f"{avail:.1f} GB")
    except Exception:
        bad("memory info unavailable")
    print()
    rule("ENVIRONMENT (secrets masked)")
    for k in sorted(os.environ)[:40]:
        v = os.environ[k]
        if re.search(r"(?i)(key|token|secret|pass)", k) and len(v) > 8:
            v = v[:6] + "..." + v[-4:]
        kv(k, v[:90])
    print()
    rule("SESSION")
    kv("uptime", fmt_dur(time.time() - START_TS))
    kv("frames rendered", LIVE["frames"])
    kv("reports written", len(REPORTS))


def mod_text_lab():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}word / char stats{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}diff two texts{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}extract iocs{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        text = ask("text")
        kv("chars", len(text))
        kv("words", len(text.split()))
        kv("lines", text.count("\n") + 1)
        kv("entropy", f"{entropy(text):.3f} bits/char")
        print()
        rule("TOP WORDS")
        for w, n in Counter(re.findall(r"[A-Za-z']{3,}", text.lower())).most_common(25):
            kv(w, n)
    elif pick == "2":
        a = ask("first text")
        b = ask("second text")
        for line in difflib.unified_diff(a.splitlines(), b.splitlines(),
                                         "first", "second", lineterm=""):
            col = (140, 255, 190) if line.startswith("+") else \
                (255, 140, 120) if line.startswith("-") else TH["dim"]
            print(f"    {fg(col)}{line[:118]}{RESET}")
    else:
        text = ask("text")
        pats = [("ipv4", r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
                ("domain", r"\b(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b"),
                ("url", r"https?://[^\s\"'<>)\]]+"),
                ("md5", r"\b[a-fA-F0-9]{32}\b"),
                ("sha256", r"\b[a-fA-F0-9]{64}\b"),
                ("email", EMAIL_RE.pattern),
                ("mac", r"\b(?:[0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2}\b")]
        for label, pat in pats:
            vals = sorted(set(re.findall(pat, text, re.I)))
            if vals:
                rule(label.upper())
                for v in vals[:25]:
                    hit(v)


def mod_data_lens():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}explore json{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}explore csv{RESET}")
    print()
    pick = ask("choice", "1")
    path = ask("file path", "")
    if not os.path.isfile(path):
        bad("not found")
        return
    if pick == "1":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            try:
                d = json.load(f)
            except Exception as e:
                bad(f"json parse: {e}")
                return

        def walk(o, prefix="", depth=0):
            if depth > 4:
                return
            if isinstance(o, dict):
                for k, v in list(o.items())[:40]:
                    if isinstance(v, (dict, list)):
                        print(f"    {fg(TH['key'])}{prefix}{k}{RESET} "
                              f"{fg(TH['dim'])}<{type(v).__name__} len={len(v)}>{RESET}")
                        walk(v, prefix + k + ".", depth + 1)
                    else:
                        kv(prefix + k, str(v)[:100])
            elif isinstance(o, list):
                for i, v in enumerate(o[:10]):
                    walk(v, prefix + f"[{i}].", depth + 1)
        walk(d)
    else:
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            rows = list(csv.reader(f))
        if not rows:
            bad("empty")
            return
        kv("rows", len(rows))
        kv("columns", len(rows[0]))
        kv("header", ", ".join(rows[0])[:160])
        print()
        for row in rows[1:9]:
            print(f"    {fg(TH['text'])}{' | '.join(row)[:150]}{RESET}")


def mod_id_forge():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}uuid v4{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}sortable id{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}nanoid{RESET}")
    print()
    pick = ask("choice", "1")
    n = int(ask("count", "5") or 5)
    if pick == "1":
        for _ in range(n):
            b = bytearray(os.urandom(16))
            b[6] = (b[6] & 0x0F) | 0x40
            b[8] = (b[8] & 0x3F) | 0x80
            h = b.hex()
            print(f"    {fg(TH['accent'])}{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-"
                  f"{h[20:]}{RESET}")
    elif pick == "2":
        for _ in range(n):
            ms = int(time.time() * 1000)
            v = (ms << 80) | (7 << 76) | random.getrandbits(74)
            h = f"{v:032x}"
            print(f"    {fg(TH['accent'])}{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-"
                  f"{h[20:]}{RESET}")
    else:
        alpha = string.ascii_letters + string.digits + "_-"
        for _ in range(n):
            print(f"    {fg(TH['accent'])}"
                  f"{''.join(random.choice(alpha) for _ in range(21))}{RESET}")


def mod_unit_shift():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}data sizes{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}time durations{RESET}")
    print(f"    {fg(TH['key'])}[3]{RESET} {fg(TH['text'])}number bases{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        v = float(ask("bytes", "1500000") or 1500000)
        for u, d in (("KB", 1e3), ("KiB", 1024), ("MB", 1e6), ("MiB", 1048576),
                     ("GB", 1e9), ("GiB", 1073741824)):
            kv(u, f"{v / d:.4f}")
    elif pick == "2":
        v = float(ask("seconds", "3600") or 3600)
        kv("minutes", v / 60)
        kv("hours", v / 3600)
        kv("days", v / 86400)
        kv("human", fmt_dur(v))
        kv("ms", v * 1000)
    else:
        val = ask("value", "0xff")
        try:
            n = int(val, 0)
        except Exception:
            bad("bad number")
            return
        for b in (2, 8, 10, 16, 36):
            kv(f"base{b}", _tobase(n, b))


def mod_vault():
    path = os.path.join(os.getcwd(), "wt_vault.json")
    pw = ask("vault password", "hunter2")
    print()
    rule("VAULT: " + path)
    if not os.path.isfile(path):
        data = {}
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                blob = json.load(f)
            raw = base64.b64decode(blob["data"])
            key = hashlib.pbkdf2_hmac("sha256", pw.encode(),
                                      base64.b64decode(blob["salt"]), 120_000, 32)
            data = json.loads(bytes(a ^ key[i % 32] for i, a in enumerate(raw))
                              .decode("utf-8"))
            ok(f"{len(data)} entry/entries")
        except Exception:
            bad("wrong password or corrupt vault")
            return
    for k in sorted(data):
        print(f"    {fg(TH['key'])}{k:<24}{RESET} {fg(TH['text'])}"
              f"{str(data[k])[:80]}{RESET}")
    print()
    print(f"  {fg(TH['dim'])}[A] add  [D] delete  [S] save  [Q] quit{RESET}")
    while True:
        try:
            c = input(f"  {fg(TH['accent'])}vault>{RESET} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if c in ("q", ""):
            break
        if c == "a":
            k = ask("key")
            if k:
                data[k] = ask("value")
        elif c == "d":
            data.pop(ask("key"), None)
        elif c == "s":
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 120_000, 32)
            raw = json.dumps(data).encode()
            enc = bytes(a ^ key[i % 32] for i, a in enumerate(raw))
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"salt": base64.b64encode(salt).decode(),
                           "data": base64.b64encode(enc).decode()}, f)
            ok("saved")


def mod_batch_runner():
    spec = ask("module numbers (comma list)", "3,7,23")
    nums = [int(p.strip()) for p in spec.split(",") if p.strip().isdigit()]
    if not nums:
        bad("nothing to run")
        return
    for n in nums:
        target = [m for m in ALL_MODULES if m[0] == n]
        if not target:
            bad(f"no module {n}")
            continue
        name, fn = target[0][1], target[0][3]
        print()
        rule(f"[{n:03d}] {name}")
        LIVE["runs"] += 1
        try:
            fn()
        except KeyboardInterrupt:
            wrn("interrupted")
        except Exception as e:
            bad(f"{type(e).__name__}: {e}")


def mod_report_forge():
    files = [f for f in os.listdir(os.getcwd()) if f.startswith("wt_") and
             f.endswith(".json")]
    if not files:
        bad("no wt_*.json reports in this folder")
        return
    inf(f"{len(files)} report(s) found")
    out = "wt_report.html"
    rows = []
    for fn in sorted(files):
        try:
            with open(fn, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        body = f"{len(d)} items" if isinstance(d, list) else \
            ", ".join(f"{k}={str(v)[:40]}" for k, v in list(d.items())[:6]) \
            if isinstance(d, dict) else str(d)[:120]
        rows.append((fn, body))
    html = ["<!doctype html><meta charset=utf-8>", "<title>WhiteTiger report</title>",
            "<style>body{background:#0b0f14;color:#d8e6f5;font:13px/1.5 ui-monospace,"
            "monospace;padding:24px}h1{color:#78e1ff}table{border-collapse:collapse;"
            "width:100%}td,th{border:1px solid #1e2a38;padding:6px 10px}"
            "th{background:#111a24;color:#b9f0ff}a{color:#8cffbe}</style>",
            f"<h1>WhiteTiger v{VERSION} report</h1>",
            f"<p>{len(rows)} file(s)</p>",
            "<table><tr><th>file</th><th>summary</th><th>size</th></tr>"]
    for fn, body in rows:
        html.append(f"<tr><td><a href='{urllib.parse.quote(fn)}'>{fn}</a></td>"
                    f"<td>{htmlmod.escape(body)}</td>"
                    f"<td>{human(os.path.getsize(fn))}</td></tr>")
    html.append("</table>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    ok(f"written -> {os.path.abspath(out)}")


PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".whitetiger_profile.json")


def mod_profiles():
    print(f"  {fg(TH['dim'])}[S] save as profile  [L] load  [Q] quit{RESET}")
    c = ask("action", "s").lower()
    if c == "s":
        name = ask("profile name", "default")
        store = {}
        if os.path.isfile(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                    store = json.load(f)
            except Exception:
                store = {}
        store[name] = dict(SETTINGS)
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
        ok(f"saved '{name}'")
    elif c == "l":
        if not os.path.isfile(PROFILE_PATH):
            bad("no profiles saved")
            return
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            store = json.load(f)
        for name in store:
            print(f"    {fg(TH['key'])}·{RESET} {fg(TH['text'])}{name}{RESET}")
        pick = ask("profile", "default")
        if pick in store:
            SETTINGS.update(store[pick])
            ok("loaded")
        else:
            bad("unknown profile")


def mod_timer():
    print(f"    {fg(TH['key'])}[1]{RESET} {fg(TH['text'])}stopwatch{RESET}")
    print(f"    {fg(TH['key'])}[2]{RESET} {fg(TH['text'])}countdown{RESET}")
    print()
    pick = ask("choice", "1")
    if pick == "1":
        inf("running — press ENTER to stop")
        t0 = time.time()
        laps = []
        while not key_pressed():
            el = time.time() - t0
            sys.stdout.write(f"\r  {fg(TH['accent'])}{fmt_dur(el)}.{int(el * 100) % 100:02d}"
                             f"{RESET}   ")
            sys.stdout.flush()
            time.sleep(0.05)
        drain_key()
        total = time.time() - t0
        print()
        kv("elapsed", f"{total:.2f}s")
        kv("human", fmt_dur(total))
    else:
        secs = int(ask("seconds", "60") or 60)
        inf(f"counting down {secs}s — ctrl-c to abort")
        try:
            while secs > 0:
                sys.stdout.write(f"\r  {fg(TH['accent'])}{fmt_dur(secs)}{RESET}   ")
                sys.stdout.flush()
                time.sleep(1)
                secs -= 1
            print()
            bell()
            ok("done")
        except KeyboardInterrupt:
            print()
            wrn("aborted")


def mod_palette():
    inf("theme preview — [1-9] switch, [Q] back")
    print()
    for i, (key, th) in enumerate(THEMES.items(), 1):
        grad = grad_for(th, 40)
        swatch = "".join(fg(grad(x)) + "█" for x in range(40)) + RESET
        mark = " <" if key == SETTINGS["theme"] else ""
        print(f"  {fg(th['key'])}[{i:>2}]{RESET} {fg(th['text'])}{th['label']:<12}{RESET}"
              f" {swatch}{mark}")
        print(f"      {fg(th['dim'])}accent {th['accent']}  key {th['key']}  "
              f"border {th['border']}{RESET}")
    print()
    pick = ask("choice", "")
    keys = list(THEMES)
    if pick.isdigit() and 1 <= int(pick) <= len(keys):
        SETTINGS["theme"] = keys[int(pick) - 1]
        ok(f"theme -> {THEMES[SETTINGS['theme']]['label']}")


def mod_notes():
    path = os.path.join(os.getcwd(), "wt_notes.txt")
    print(f"  {fg(TH['dim'])}scratchpad: {path}{RESET}")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f.read().splitlines()[-25:]:
                print(f"    {fg(TH['text'])}{line[:110]}{RESET}")
    print()
    print(f"  {fg(TH['dim'])}[A] append  [C] clear  [Q] back{RESET}")
    c = ask("action", "a").lower()
    if c == "a":
        line = ask("note")
        if line:
            with open(path, "a", encoding="utf-8") as f:
                f.write(time.strftime("[%Y-%m-%d %H:%M] ") + line + "\n")
            ok("appended")
    elif c == "c":
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        ok("cleared")


# --------------------------------------------------------------------------- #
#  plugins
# --------------------------------------------------------------------------- #
PLUGIN_MODULES = []
ALL_MODULES = []


def load_plugins():
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, "plugins")
    if not os.path.isdir(d):
        return []
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location("wtp_" + fn[:-3],
                                                          os.path.join(d, fn))
            if not spec or not spec.loader:
                continue
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            for item in getattr(m, "MODULES", []):
                if not isinstance(item, (tuple, list)):
                    continue
                if len(item) == 4:
                    item = item[1:]
                if len(item) != 3 or not callable(item[2]):
                    continue
                out.append((str(item[0]), str(item[1]), item[2]))
        except Exception as e:
            print(f"  {fg(TH['dim'])}plugin {fn} failed: {e}{RESET}")
    return out


# --------------------------------------------------------------------------- #
#  registry
# --------------------------------------------------------------------------- #
MODULES = [
    (1, "GHOST SWEEP", "ports, banners, tls, json report", mod_ghost_sweep),
    (2, "VULN LENS", "cves, unauth services, risk grade", mod_vuln_lens),
    (3, "PORT STORM", "threaded connect scan", mod_port_storm),
    (4, "BANNER XRAY", "service fingerprint", mod_banner_xray),
    (5, "ECHO PULSE", "icmp sweep, latency, jitter", mod_echo_pulse),
    (6, "NET HOUND", "arp + icmp + tcp discovery", mod_net_hound),
    (7, "PATH RIPPER", "web path fuzzer", mod_path_ripper),
    (8, "HTTP AUTOPSY", "redirects, methods, cors, cookies", mod_http_autopsy),
    (9, "TLS TEARDOWN", "protocols, ciphers, chain, hsts", mod_tls_teardown),
    (10, "DANGLING HOOK", "subdomain takeover", mod_dangling_hook),
    (11, "INJECTOR", "sql injection prober", mod_injector),
    (12, "REFLECT", "xss + open redirect", mod_reflect),
    (13, "CORS BREAKER", "origin reflection", mod_cors_breaker),
    (14, "BUCKET DIVE", "cloud bucket finder", mod_bucket_dive),
    (15, "SHIELD PROBE", "waf + cdn detector", mod_shield_probe),
    (16, "CMS SKELETON", "cms deep scan", mod_cms_skeleton),
    (17, "PARAM HUNT", "hidden parameter discovery", mod_param_hunt),
    (18, "UDP ECHO", "udp service prober", mod_udp_echo),
    (19, "SHELL DOOR", "ssh / smb / rdp / ftp enum", mod_shell_door),
    (20, "MIRROR IP", "reverse ip + bgp", mod_mirror_ip),
    (21, "SMUGGLER", "http request smuggling", mod_smuggler),
    (22, "SSRF PROBE", "server side request forgery", mod_ssrf),
    (23, "BACKUP HUNTER", "backup + config brute", mod_backup_hunter),
    (24, "API MAPPER", "api roots + method matrix", mod_api_mapper),
    (25, "SMB NULL", "smb2 negotiate + null session", mod_smb_null),
    (26, "SNMP WALK", "community sweep + oid tree", mod_snmp_walk),

    (27, "DORK CANNON", "60 dorks x 3 engines", mod_dork_cannon),
    (28, "OMNI SEARCH", "ddg + mojeek + searx", mod_omni_search),
    (29, "HANDLE TRACE", "140 platforms, api first", mod_handle_trace),
    (30, "MAIL XRAY", "mx, gravatar, signups, breaches", mod_mail_xray),
    (31, "MAIL VALIDATE", "spf, dmarc, dnsbl, smtp", mod_mail_validate),
    (32, "MAIL FORGE", "permutator + smtp verify", mod_mail_forge),
    (33, "IP ORACLE", "shodan, greynoise, bgp, rdap", mod_ip_oracle),
    (34, "DOMAIN ORACLE", "dns, rdap, tls, subs", mod_domain_oracle),
    (35, "SUB SPIDER", "8 passive sources + brute", mod_sub_spider),
    (36, "PAGE XRAY", "metas, secrets, tech, socials", mod_page_xray),
    (37, "CERT ARCHIVE", "ct logs, issuers, sans", mod_cert_archive),
    (38, "DNS OMNI", "all records + axfr + dnssec", mod_dns_omni),
    (39, "PHONE ORACLE", "tz, carrier, operator, type", mod_phone_oracle),
    (40, "INSTA LENS", "instagram profile", mod_insta_lens),
    (41, "CHAIN WATCH", "btc, eth, ltc, doge, sol", mod_chain_watch),
    (42, "LEAK LENS", "breaches + paste search", mod_leak_lens),
    (43, "GIT EXCAVATE", "repos, emails, orgs", mod_git_excavate),
    (44, "SOCIAL XRAY", "telegram, discord, x, bsky", mod_social_xray),
    (45, "AVATAR LENS", "gravatar + ascii", mod_avatar_lens),
    (46, "OUI ORACLE", "mac vendor", mod_oui_oracle),
    (47, "ASN MAP", "prefixes + peers", mod_asn_map),
    (48, "WAYBACK VAULT", "snapshots + leaked files", mod_wayback_vault),
    (49, "TYPO TRAP", "typosquat registration", mod_typo_trap),
    (50, "STACK PIVOT", "favicon, ga id, headers", mod_stack_pivot),
    (51, "WHOIS DEEP", "rdap + whois + typos", mod_whois_deep),
    (52, "PASTE DIVER", "psbdmp + paste sites", mod_paste_diver),
    (53, "GEO LENS", "coords, geocode, tz", mod_geo_lens),
    (54, "SUPPLY WATCH", "npm, pypi, crates, docker", mod_supply_watch),
    (55, "FEED WIRE", "rss + threat digest", mod_feed_wire),
    (56, "CODE HUNT", "github code search", mod_code_hunt),
    (57, "URLSCAN LENS", "urlscan.io results", mod_urlscan_lens),
    (58, "REDDIT SCOPE", "posts + comments", mod_reddit_scope),

    (59, "HASH BREAKER", "identify, hash, rules crack", mod_hash_breaker),
    (60, "JWT LAB", "decode, claims, crack, forge", mod_jwt_lab),
    (61, "CODEC DECK", "20+ codecs both ways", mod_codec_deck),
    (62, "CVE ORACLE", "circl + epss + cisa kev", mod_cve_oracle),
    (63, "SECRET SNIFFER", "30 patterns", mod_secret_sniffer),
    (64, "META XRAY", "exif, gps, png, pdf, id3", mod_meta_xray),
    (65, "META SCRUB", "strip metadata", mod_meta_scrub),
    (66, "FILE AUTOPSY", "magic, entropy, strings, iocs", mod_file_autopsy),
    (67, "COOKIE LENS", "flags, entropy, jwt detect", mod_cookie_lens),
    (68, "MAIL ARMOR", "spf, dmarc, dkim, spoofing", mod_mail_armor),
    (69, "GQL MAPPER", "introspection + notes", mod_gql_mapper),
    (70, "STEGO LAB", "trailing data, chunks, lsb", mod_stego_lab),
    (71, "CIPHER DECK", "caesar, vigenere, rail, ic", mod_cipher_deck),
    (72, "ARCHIVE DIVE", "zip/tar/gz + office meta", mod_archive_dive),
    (73, "EML PARSER", "received chain, auth, urls", mod_eml_parser),
    (74, "TIME SHIFT", "epoch conversions", mod_time_shift),
    (75, "IDN LENS", "punycode, zero-width, homoglyph", mod_idn_lens),
    (76, "HEX FORGE", "hex dump, base convert, bit ops", mod_hex_forge),
    (77, "FILE CARVER", "jpg/png/pdf/zip carving", mod_file_carver),
    (78, "QR LENS", "qr decode + terminal gen", mod_qr_lens),
    (79, "BINARY DIFF", "byte level file diff", mod_binary_diff),
    (80, "CRYPTO ORACLE", "hashes, hmac, kdf, encodings", mod_crypto_oracle),
    (81, "KEY LENS", "pem + pgp key inspect", mod_key_lens),
    (82, "IMAGE FORENSICS", "quantisation + recompression", mod_image_forensics),

    (83, "TEMP MAIL", "4 providers, live bell", mod_temp_mail),
    (84, "SITE MIRROR", "mirror page assets", mod_site_mirror),
    (85, "QR FORGE", "qr -> terminal", mod_qr_forge),
    (86, "PASS FORGE", "generate, passphrase, score", mod_pass_forge),
    (87, "NET KIT", "public ip, traceroute, dns bench", mod_net_kit),
    (88, "ASCII LENS", "truecolor png render", mod_ascii_lens),
    (89, "SYSTEM LENS", "cpu, mem, env", mod_system_lens),
    (90, "TEXT LAB", "stats, diff, ioc extract", mod_text_lab),
    (91, "DATA LENS", "json + csv walker", mod_data_lens),
    (92, "ID FORGE", "uuid, sortable, nanoid", mod_id_forge),
    (93, "UNIT SHIFT", "sizes, time, bases", mod_unit_shift),
    (94, "VAULT", "pbkdf2 xor note store", mod_vault),
    (95, "BATCH RUNNER", "run several modules", mod_batch_runner),
    (96, "REPORT FORGE", "merge reports to html", mod_report_forge),
    (97, "PROFILES", "save / load profiles", mod_profiles),
    (98, "TIMER", "stopwatch + countdown", mod_timer),
    (99, "PALETTE", "theme preview + swatches", mod_palette),
    (100, "NOTES", "quick scratchpad", mod_notes),
]


def rebuild():
    global ALL_MODULES, CATEGORIES
    ALL_MODULES = MODULES + PLUGIN_MODULES
    CATEGORIES = [("PENTESTING", [m for m in MODULES if m[0] <= 26]),
                  ("OSINT", [m for m in MODULES if 27 <= m[0] <= 58]),
                  ("CSINT", [m for m in MODULES if 59 <= m[0] <= 82]),
                  ("UTILITIES", [m for m in MODULES if m[0] >= 83]),
                  ("PLUGINS", list(PLUGIN_MODULES))]


CATEGORIES = []
rebuild()


# --------------------------------------------------------------------------- #
#  control flow
# --------------------------------------------------------------------------- #
def run_module(mod, th):
    name, desc, fn = mod[1], mod[2], mod[3]
    AMBIENT["on"] = False
    time.sleep(0.03)
    slide(th)
    clear()
    print(center_line(brand_bar(th, block_w(), anim_t())))
    print()
    print(center_line(f"{fg(th['accent'])}{BOLD}▸ {name} ◂{RESET}"))
    print(center_line(f"{fg(th['dim'])}{desc}{RESET}"))
    print()
    LIVE["runs"] += 1
    LIVE["msg"] = name.split()[0].lower()
    FXS.burst_now()
    t0 = time.time()
    try:
        fn()
    except KeyboardInterrupt:
        print()
        wrn("interrupted")
    except Exception as e:
        bad(f"{type(e).__name__}: {e}")
        if os.environ.get("WT_TRACE"):
            import traceback
            traceback.print_exc()
    print()
    print(f"  {fg(th['dim'])}finished in {time.time() - t0:.2f}s{RESET}")
    LIVE["msg"] = "idle"
    pause()


def show_help(th):
    clear()
    print(center_line(brand_bar(th, block_w(), anim_t())))
    print()
    print(center_line(f"{fg(th['accent'])}{BOLD}HELP{RESET}"))
    print()
    for l in [f"{len(MODULES)} modules — type a number, or /word to filter",
              "h help · s settings · t theme · r random · b batch · q quit",
              "everything is stdlib only, no pip installs",
              "json reports land in the folder you launched from",
              "module 96 merges every report into one html page",
              "drop .py files with a MODULES list into ./plugins",
              "--calm freezes glow · --no-anim kills the intro",
              "--no-color pipes cleanly · --selftest verifies helpers",
              "WT_TRACE=1 shows python tracebacks"]:
        print(center_line(f"{fg(TH['dim'])}·{RESET} {fg(TH['text'])}{l}{RESET}"))
    print()
    pause()


def show_version(th):
    clear()
    print(center_line(brand_bar(th, block_w(), anim_t())))
    print()
    print(center_line(f"{fg(th['accent'])}{BOLD}WHITETIGER{RESET} "
                      f"{fg(th['dim'])}v{VERSION}{RESET}"))
    print(center_line(f"{fg(th['dim'])}python {sys.version.split()[0]} · "
                      f"{tw()}x{th_()} · {sys.platform}{RESET}"))
    print()
    print(center_line(f"{fg(TH['text'])}{len(MODULES)} modules · "
                      f"zero dependencies{RESET}"))
    print()
    pause()


def show_credits(th):
    clear()
    print(center_line(brand_bar(th, block_w(), anim_t())))
    print()
    for l in banner_rows(th, block_w(), anim_t()):
        print(l)
    print()
    print(center_line(f"{fg(TH['dim'])}built by {RESET}"
                      f"{fg(TH['key'])}{BOLD}{AUTHOR}{RESET}"))
    print(center_line(f"{fg(TH['dim'])}v{VERSION} · stdlib only · no tracking{RESET}"))
    print()
    pause()


def search_modules(term):
    t = term.lower()
    return [m for m in ALL_MODULES if t in m[1].lower() or t in m[2].lower()]


def settings_screen():
    global TH
    while True:
        th = THEMES[SETTINGS["theme"]]
        clear()
        print(center_line(brand_bar(th, block_w(), anim_t())))
        print()
        print(center_line(f"{fg(th['accent'])}{BOLD}SETTINGS{RESET}"))
        print()
        opts = [("1", "boot sequence", SETTINGS["boot"]),
                ("2", "intro animation", SETTINGS["anim"]),
                ("3", "ambient engine", SETTINGS["glow"]),
                ("4", "temp mail bell", SETTINGS["notify"]),
                ("5", "live redraw", SETTINGS["live_typing"]),
                ("6", "compact banner", SETTINGS["compact"]),
                ("7", "matrix rain", SETTINGS["rain"]),
                ("8", "banner glitch", SETTINGS["glitch"]),
                ("9", "severity pulse", SETTINGS["flash"]),
                ("A", "stripe sweep", SETTINGS["stripes"]),
                ("B", "menu sweep", SETTINGS["sweep"]),
                ("C", "truecolor ascii", SETTINGS["truecolor"]),
                ("D", "fps", SETTINGS["fps"]),
                ("E", "layout", SETTINGS["layout"]),
                ("F", "theme", th["label"])]
        for k, lbl, val in opts:
            print(center_line(
                f"{fg(th['key'])}[{k}]{RESET} {fg(th['text'])}{lbl:<20}{RESET}"
                f"{fg(th['accent'])}"
                f"{'ON' if val is True else 'OFF' if val is False else val}{RESET}"))
        print()
        print(center_line(f"{fg(th['key'])}[Z]{RESET} {fg(th['text'])}back{RESET}"))
        print()
        try:
            c = input(f"  {fg(th['accent'])}> {RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if c == "1":
            SETTINGS["boot"] = not SETTINGS["boot"]
        elif c == "2":
            SETTINGS["anim"] = not SETTINGS["anim"]
        elif c == "3":
            SETTINGS["glow"] = not SETTINGS["glow"]
        elif c == "4":
            SETTINGS["notify"] = not SETTINGS["notify"]
        elif c == "5":
            SETTINGS["live_typing"] = not SETTINGS["live_typing"]
        elif c == "6":
            SETTINGS["compact"] = not SETTINGS["compact"]
        elif c == "7":
            SETTINGS["rain"] = not SETTINGS["rain"]
        elif c == "8":
            SETTINGS["glitch"] = not SETTINGS["glitch"]
        elif c == "9":
            SETTINGS["flash"] = not SETTINGS["flash"]
        elif c == "a":
            SETTINGS["stripes"] = not SETTINGS["stripes"]
        elif c == "b":
            SETTINGS["sweep"] = not SETTINGS["sweep"]
        elif c == "c":
            SETTINGS["truecolor"] = not SETTINGS["truecolor"]
        elif c == "d":
            try:
                SETTINGS["fps"] = max(5, min(60, int(ask("fps", str(SETTINGS["fps"])))))
            except Exception:
                pass
        elif c == "e":
            o = ["auto", "boxes", "flat"]
            SETTINGS["layout"] = o[(o.index(SETTINGS["layout"]) + 1) % len(o)]
        elif c == "f":
            names = list(THEMES)
            SETTINGS["theme"] = names[(names.index(SETTINGS["theme"]) + 1) % len(names)]
        elif c in ("z", "back", ""):
            TH = THEMES[SETTINGS["theme"]]
            return


def goodbye(th):
    print()
    print(center_line(f"{fg(th['accent'])}{BOLD}white tiger{RESET} "
                      f"{fg(th['dim'])}closing...{RESET}"))
    print(center_line(f"{fg(th['dim'])}{fmt_dur(time.time() - START_TS)} · "
                      f"{LIVE['runs']} run(s) · {LIVE['hits']} finding(s){RESET}"))
    print()


def main_loop():
    global TH
    draw_screen(TH, animate=True)
    while True:
        sys.stdout.flush()
        AMBIENT["on"] = SETTINGS["glow"] and TTY and SETTINGS["live_typing"]
        if TTY:
            os.write(1, SHOW_CUR.encode())
        try:
            raw = input("")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        finally:
            if TTY:
                os.write(1, HIDE_CUR.encode())
        AMBIENT["on"] = False
        time.sleep(0.03)
        cmd = raw.strip()
        if not cmd:
            draw_screen(TH, animate=False)
            continue
        low = cmd.lower()
        if low in ("q", "quit", "exit"):
            goodbye(TH)
            break
        if low in ("h", "help"):
            show_help(TH)
        elif low in ("v", "version"):
            show_version(TH)
        elif low in ("c", "credits"):
            show_credits(TH)
        elif low in ("s", "settings"):
            settings_screen()
            TH = THEMES[SETTINGS["theme"]]
        elif low in ("b", "batch"):
            mod_batch_runner()
        elif low in ("t", "theme"):
            names = list(THEMES)
            SETTINGS["theme"] = names[(names.index(SETTINGS["theme"]) + 1) % len(names)]
            TH = THEMES[SETTINGS["theme"]]
        elif low in ("r", "random"):
            run_module(MODULES[random.randrange(len(MODULES))], TH)
        elif cmd.startswith("/"):
            matches = search_modules(cmd[1:])
            if not matches:
                bad(f"no module matches '{cmd[1:]}'")
            else:
                print()
                inf(f"{len(matches)} match(es)")
                for n, name, desc, _ in matches:
                    print(f"    {fg(TH['key'])}[{n:03d}]{RESET} {fg(TH['text'])}{name}"
                          f"{RESET} {fg(TH['dim'])}— {desc}{RESET}")
                print()
                pick = ask("run which? (enter to skip)", "")
                if pick.isdigit() and any(m[0] == int(pick) for m in ALL_MODULES):
                    run_module([m for m in ALL_MODULES if m[0] == int(pick)][0], TH)
                else:
                    draw_screen(TH, animate=False)
                    continue
        elif cmd.isdigit() and any(m[0] == int(cmd) for m in ALL_MODULES):
            run_module([m for m in ALL_MODULES if m[0] == int(cmd)][0], TH)
        else:
            print(f"  {fg(TH['dim'])}unknown '{cmd}' — [H] for help{RESET}")
            time.sleep(0.4)
        TH = THEMES[SETTINGS["theme"]]
        draw_screen(TH, animate=False)


def main():
    global TH, COLOR, RESET, BOLD, PLUGIN_MODULES

    args = sys.argv[1:]
    for arg in args:
        if arg == "--no-anim":
            SETTINGS["anim"] = False
            SETTINGS["boot"] = False
        elif arg == "--calm":
            SETTINGS["glow"] = False
            SETTINGS["flash"] = False
            SETTINGS["stripes"] = False
            SETTINGS["sweep"] = False
        elif arg == "--no-color":
            COLOR = False
            RESET = ""
            BOLD = ""
            _ESC_CACHE.clear()
        elif arg == "--fast":
            SETTINGS["anim"] = False
            SETTINGS["fps"] = 40
        elif arg == "--rain":
            SETTINGS["rain"] = True
        elif arg == "--glitch":
            SETTINGS["glitch"] = True
        elif arg == "--no-glitch":
            SETTINGS["glitch"] = False
        elif arg.startswith("--fps="):
            try:
                SETTINGS["fps"] = max(5, min(60, int(arg.split("=", 1)[1])))
            except Exception:
                pass
        elif arg.startswith("--theme="):
            name = arg.split("=", 1)[1]
            if name in THEMES:
                SETTINGS["theme"] = name
        elif arg.startswith("--layout="):
            SETTINGS["layout"] = arg.split("=", 1)[1]
        elif arg == "--list":
            for n, name, desc, _ in MODULES:
                print(f"{n:>3}  {name:<18} {desc}")
            return
        elif arg == "--selftest":
            req = ["png_load", "render_ascii", "parse_exif", "dms", "strip_jpeg",
                   "strip_png", "strip_pdf", "MAGIC", "EXIF_KEYS", "GPS_KEYS",
                   "signup_probe", "CALLING_CODES", "TZ_FALLBACK", "mod_meta_xray",
                   "mod_meta_scrub", "mod_file_autopsy", "mod_phone_oracle",
                   "safe_extract", "png_text", "pdf_info", "id3_tags", "office_meta",
                   "_read_ifd", "center_line", "block_h", "banner_mode",
                   "_spnego_ntlmssp", "_smb2_negociate", "_ber", "_snmp_get"]
            miss = [r for r in req if r not in globals()]
            broken = [f"{n} {nm}" for n, nm, _, fn in MODULES if not callable(fn)]
            print(f"modules={len(MODULES)} helpers_missing={len(miss)} "
                  f"broken={len(broken)}")
            for m in miss:
                print("  MISSING HELPER:", m)
            for b in broken:
                print("  BROKEN MODULE:", b)
            print("OK" if not miss and not broken else "FAILED")
            return
        elif arg in ("-h", "--help"):
            print(__doc__ or "see --list")
            return

    setup_console()
    TH = THEMES[SETTINGS["theme"]]

    PLUGIN_MODULES = load_plugins()
    if PLUGIN_MODULES:
        base = len(MODULES)
        PLUGIN_MODULES = [(base + i, it[0], it[1], it[2])
                          for i, it in enumerate(PLUGIN_MODULES, 1)]
    rebuild()

    if "--module" in args:
        try:
            n = int(args[args.index("--module") + 1])
        except Exception:
            n = 1
        target = [m for m in ALL_MODULES if m[0] == n]
        if target:
            run_module(target[0], TH)
        else:
            print(f"no module numbered {n}")
        return

    if TTY:
        os.write(1, HIDE_CUR.encode())
    clear()
    if SETTINGS["boot"] and SETTINGS["anim"] and TTY:
        boot_sequence(TH)
        clear()
    intro_banner(TH)
    if TTY:
        print(center_line(f"{fg(TH['key'])}built by {AUTHOR}{RESET}"))
        print(center_line(f"{fg(TH['dim'])}{len(MODULES)} modules · "
                          f"stdlib only{RESET}"))
        print()
    try:
        main_loop()
    except KeyboardInterrupt:
        print()
        goodbye(TH)
    finally:
        AMBIENT["on"] = False
        if TTY:
            os.write(1, (SHOW_CUR + RESET).encode())
        sys.stdout.flush()


if __name__ == "__main__":
    threading.Thread(target=ambient_loop, daemon=True).start()
    threading.Thread(target=metrics_loop, daemon=True).start()
    main()
