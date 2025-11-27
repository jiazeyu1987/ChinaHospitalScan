#!/usr/bin/env python3
"""
长海医院链接分析工具
专门用于分析长海医院网站的链接结构和内容
"""

import asyncio
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def analyze_longhua_links():
    """深入分析长海医院网站的链接"""
    base_url = "https://www.longhua.net/index/cggg.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print("🔍 开始分析长海医院链接结构")
    print(f"目标URL: {base_url}")
    print("="*80)

    try:
        # 请求页面
        print("📥 正在获取页面内容...")
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()

        print(f"✅ 页面请求成功")
        print(f"   状态码: {response.status_code}")
        print(f"   内容长度: {len(response.content)} bytes")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")

        # 解析HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # 查找所有链接
        all_links = soup.find_all("a", href=True)
        print(f"\n🔗 发现总链接数: {len(all_links)}")

        # 分析链接
        domain_links = []
        external_links = []
        js_links = []
        other_links = []

        html_extensions = ['.html', '.htm', '.shtml']

        for i, link in enumerate(all_links):
            href = link.get("href")
            text = link.get_text(strip=True)

            if not href:
                other_links.append((i+1, href, text, "空链接"))
                continue

            # URL分类
            if href.startswith("javascript:") or href.startswith("#"):
                js_links.append((i+1, href, text, "JS链接"))
            elif href.startswith("http"):
                if "longhua.net" in href:
                    domain_links.append((i+1, href, text, "同域链接"))
                else:
                    external_links.append((i+1, href, text, "外域链接"))
            else:
                domain_links.append((i+1, href, text, "相对链接"))

        print(f"\n📊 链接分类统计:")
        print(f"   同域链接: {len(domain_links)}")
        print(f"   外域链接: {len(external_links)}")
        print(f"   JS链接: {len(js_links)}")
        print(f"   其他链接: {len(other_links)}")

        # 详细分析同域链接
        print(f"\n🎯 同域链接详细分析 (前20个):")
        print("-"*80)

        html_count = 0
        html_links = []

        for i, (num, href, text, category) in enumerate(domain_links[:20]):
            # 转换为绝对URL
            if href.startswith("/"):
                absolute_href = f"https://www.longhua.net{href}"
            elif not href.startswith("http"):
                absolute_href = f"https://www.longhua.net/{href.lstrip('/')}"
            else:
                absolute_href = href

            # 检查是否为HTML页面
            parsed = urlparse(absolute_href)
            path = parsed.path or ""
            is_html = any(path.lower().endswith(ext) for ext in html_extensions) or not any(path.lower().endswith(ext) for ext in
                ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.pdf',
                 '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.tar', '.gz',
                 '.mp3', '.mp4', '.avi', '.mov', '.flv', '.wmv'])

            if is_html:
                html_count += 1
                html_links.append((num, href, text, category))

            # 关键词检查
            keywords = ["公告", "采购", "招标", "设备", "医疗", "器械", "中标", "结果"]
            matched_keywords = [kw for kw in keywords if kw.lower() in text.lower()]

            print(f"{num:2d}. {category}")
            print(f"     URL: {href}")
            print(f"     文本: {text[:100]}..." if len(text) > 100 else f"     文本: {text}")
            print(f"     HTML页面: {'✅' if is_html else '❌'}")
            print(f"     关键词匹配: {matched_keywords if matched_keywords else '❌ 无匹配'}")
            print()

        print(f"\n📈 同域HTML链接统计:")
        print(f"   HTML链接数: {html_count}")
        print(f"   非HTML链接数: {len(domain_links) - html_count}")

        # 输出所有HTML链接用于进一步分析
        print(f"\n🎯 所有同域HTML链接列表:")
        print("-"*80)
        for num, href, text, category in html_links:
            matched_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
            print(f"{num:2d}. {href} -> '{text}' (关键词: {matched_keywords})")

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_longhua_links()