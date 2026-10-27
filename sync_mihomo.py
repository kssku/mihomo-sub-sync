#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mihomo 订阅每日同步（GitHub Actions 版）
原青龙两个脚本合并：抓链接 + 下载 + 校验 + 写回本仓库。

与青龙版差异：
- 无本地代理（127.0.0.1:7890 云端不存在），只走直连
- 无 NAS 路径，结果写进仓库根目录 clash_proxies_latest.yaml
- 不写 mihomo config.yaml
"""

import json
import os
import re
import sys
import time
import subprocess

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://tg.i-c-a.su/json/fproxies?limit=1"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(OUT_DIR, "clash_proxies_latest.yaml")
ARCHIVE_DIR = os.path.join(OUT_DIR, "archive")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def curl_get(url, timeout=25, max_retries=3):
    for attempt in range(1, max_retries + 1):
        cmd = [
            "curl", "-sSL", "-k",
            "--connect-timeout", "15",
            "--max-time", str(timeout),
            "--retry", "2", "--retry-delay", "3",
            "-H", "User-Agent: " + USER_AGENT,
            url,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout + 15)
            if result.returncode == 0 and result.stdout:
                return True, result.stdout.decode("utf-8", errors="ignore")
            print("  curl 返回码 %s (尝试 %d/%d)" % (result.returncode, attempt, max_retries))
        except Exception as exc:
            print("  curl 异常 (尝试 %d/%d): %s" % (attempt, max_retries, exc))
        if attempt < max_retries:
            time.sleep(4)
    return False, None


def _extract_link(text):
    base = re.search(r"https://sub\.danhu\.(?:dpdns\.org|ddns-ip\.net)/", text)
    path = re.search(r"paste/(?:TG@)?[\w@\-]+/", text)
    if base and path:
        return base.group(0) + path.group(0) + "clash"
    full = re.search(r"https://sub\.danhu\.[^\s\"'<>]+clash", text)
    return full.group(0) if full else None


def extract_sub_link_from_json(json_text):
    try:
        data = json.loads(json_text)
    except Exception:
        return None

    if isinstance(data, dict) and "messages" in data:
        for msg in data["messages"]:
            for field in ("message", "text", "content", "description"):
                txt = msg.get(field)
                if txt and isinstance(txt, str) and len(txt) > 50:
                    link = _extract_link(txt)
                    if link:
                        return link

    def find_text(obj):
        if isinstance(obj, dict):
            for key in ("message", "text", "content", "description"):
                if key in obj and isinstance(obj[key], str) and len(obj[key]) > 50:
                    return obj[key]
            for value in obj.values():
                found = find_text(value)
                if found:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = find_text(item)
                if found:
                    return found
        return None

    text = find_text(data)
    return _extract_link(text) if text else None


def download_file(url, save_path):
    print("下载订阅文件...")
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
        resp = session.get(url, timeout=(15, 120), verify=False, stream=True)
        if resp.status_code != 200:
            print("下载失败，状态码 %s" % resp.status_code)
            return False
        with open(save_path, "wb") as handle:
            for chunk in resp.iter_content(8192):
                handle.write(chunk)
        size_kb = os.path.getsize(save_path) / 1024
        print("下载成功，%.1f KB" % size_kb)
        return True
    except Exception as exc:
        print("下载异常: %s" % exc)
        return False


def is_valid_yaml(file_path):
    try:
        import yaml
        with open(file_path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return isinstance(data, dict) and ("proxies" in data or "proxy-providers" in data)
    except Exception:
        return False


def main():
    print("=" * 60)
    print("Mihomo 订阅同步（云端版）")
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    print("获取最新帖子 JSON...")
    ok, text = curl_get(API_URL)
    if not ok or not text:
        print("无法获取 JSON")
        return 1

    sub_url = extract_sub_link_from_json(text)
    if not sub_url:
        print("未能提取订阅链接")
        return 1
    print("订阅链接: %s" % sub_url)

    tmp_path = OUT_FILE + ".tmp"
    if not download_file(sub_url, tmp_path):
        return 1

    if not is_valid_yaml(tmp_path):
        print("文件不是有效的 Mihomo 配置，放弃写入")
        os.remove(tmp_path)
        return 1
    print("YAML 校验通过")

    os.replace(tmp_path, OUT_FILE)
    print("已写入 %s" % OUT_FILE)

    today = time.strftime("%Y%m%d")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_path = os.path.join(ARCHIVE_DIR, "clash_" + today + ".yaml")
    with open(OUT_FILE, "rb") as src, open(archive_path, "wb") as dst:
        dst.write(src.read())
    print("已归档 %s" % archive_path)

    cutoff = time.time() - 7 * 86400
    for name in os.listdir(ARCHIVE_DIR):
        fp = os.path.join(ARCHIVE_DIR, name)
        if os.path.isfile(fp) and os.path.getmtime(fp) < cutoff:
            os.remove(fp)
            print("清理旧归档 %s" % name)

    print("完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
