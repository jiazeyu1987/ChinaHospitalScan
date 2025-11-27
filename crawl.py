import asyncio
import datetime
import logging
import os
import re
import sqlite3
import sys
import time
from typing import Dict, Set, Any
from urllib.parse import urlparse, urljoin

# 配置爬虫专用日志器
crawler_logger = logging.getLogger('crawler')

# 如果还没有配置爬虫日志器，则进行配置
if not crawler_logger.handlers:
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    # 添加爬虫专用文件处理器
    crawler_file_handler = logging.FileHandler('logs/crawler.log', encoding='utf-8', mode='a')
    crawler_file_handler.setLevel(logging.DEBUG)
    crawler_file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    crawler_file_handler.setFormatter(crawler_file_formatter)

    # 添加控制台处理器
    crawler_console_handler = logging.StreamHandler()
    crawler_console_handler.setLevel(logging.INFO)
    crawler_console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    crawler_console_handler.setFormatter(crawler_console_formatter)

    crawler_logger.addHandler(crawler_file_handler)
    crawler_logger.addHandler(crawler_console_handler)
    crawler_logger.setLevel(logging.DEBUG)

    # 防止日志传播到根日志器，避免重复
    crawler_logger.propagate = False

import nest_asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import (
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
)
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import DomainFilter, ContentTypeFilter
from crawl4ai.deep_crawling import FilterChain

# Apply nest_asyncio to handle Windows asyncio limitations
if sys.platform == "win32":
    nest_asyncio.apply()


def clean_text_encoding(text: str) -> str:
    """
    清理文本中的字符编码问题，移除或替换无效字符
    """
    if not text:
        return text

    # 移除或替换常见的编码问题字符
    cleaned = text

    # 替换常见的无效字符
    invalid_chars = ['\uFFFD', '\x00', '\u200B', '\u200C', '\u200D', '\uFEFF']
    for char in invalid_chars:
        cleaned = cleaned.replace(char, '')

    # 处理连续的空白字符
    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()


# 默认关键词，可以被动态关键词覆盖
# 扩展默认关键词列表，提高匹配率，添加医院特定词汇
DEFAULT_KEYWORDS = (
    # 核心采购相关词汇
    "公告", "采购", "公开", "招标", "询价", "投标", "中标",
    "信息", "通知", "结果", "公示", "成交", "成交公告",
    "答疑", "变更", "澄清", "更正", "修改", "补充",

    # 招标流程相关
    "预审", "谈判", "竞争", "磋商", "单一来源", "邀请招标",
    "公开招标", "竞争性谈判", "询价采购", "竞争性磋商",

    # 意见征集相关
    "征求意见", "征求意见稿", "征集", "公示", "公示期",

    # 预算和计划相关
    "预算", "采购计划", "需求", "需求公示", "采购需求",

    # 结果和合同相关
    "合同", "合同公告", "履约", "验收", "评估",

    # 医院特定词汇
    "医疗", "药品", "器械", "设备", "耗材", "服务",
    "卫生", "医院", "疾控", "医保", "新农合",

    # 采购方式相关
    "招标采购", "询价采购", "谈判采购", "单一来源采购", "网上采购",

    # 金额和时间相关
    "万元", "元", "报价", "预算金额", "中标金额",
    "截止时间", "开标时间", "投标时间", "公示时间",

    # 其他相关词汇
    "供应商", "投标人", "中标人", "成交人", "项目", "项目编号"
)


def _has_keyword(text: str | None, keywords: tuple = None) -> bool:
    """
    判断链接文本是否包含任意一个目标关键词。

    Args:
        text: 要检查的文本
        keywords: 关键词元组，如果为None则使用默认关键词

    Returns:
        bool: 是否包含关键词
    """
    if not text:
        logging.debug(f"🔍 [KEYWORD_FILTER] 检查关键词: 文本为空")
        return False

    # 使用传入的关键词或默认关键词
    target_keywords = keywords or DEFAULT_KEYWORDS
    text_lower = text.lower()

    logging.info(f"🔍 [KEYWORD_FILTER] 开始关键词匹配检查")
    logging.info(f"   原始文本: '{text}'")
    logging.info(f"   文本长度: {len(text)} 字符")
    logging.info(f"   关键词数量: {len(target_keywords)} 个")

    matched_keywords = []
    for kw in target_keywords:
        if kw and kw.lower() in text_lower:
            matched_keywords.append(kw)
            logging.info(f"✅ [KEYWORD_FILTER] 匹配成功: 关键词 '{kw}' 在文本中找到")
        else:
            logging.debug(f"   - 未匹配关键词: '{kw}'")

    if matched_keywords:
        logging.info(f"🎯 [KEYWORD_FILTER] 最终匹配结果: 成功")
        logging.info(f"   匹配的关键词: {matched_keywords}")
        return True
    else:
        logging.info(f"❌ [KEYWORD_FILTER] 最终匹配结果: 失败")
        logging.info(f"   所有关键词均未匹配")
        return False


def _is_html_page(url: str, unlimited_mode: bool = False) -> bool:
    """
    判断URL是否为HTML页面。
    支持多种URL格式：.html/.htm/.shtml后缀、无后缀路径、动态参数等。
    过滤掉明显的静态资源（图片、CSS、JS 等）。

    在无限制模式下，放行所有同域URL。
    """
    try:
        logging.info(f"🔍 [INFO] _is_html_page called with url={url}, unlimited_mode={unlimited_mode}")

        # 强制检测无限制模式：如果是长海医院域名，自动应用无限制模式
        if "longhua.net" in url:
            forced_unlimited = True
            logging.info(f"🔥 [FORCE_UNLIMITED] 检测到长海医院域名，强制应用无限制模式: {url}")
            return True

        # 原有的无限制模式：放行所有URL
        if unlimited_mode:
            logging.info(f"🔥 [UNLIMITED_MODE] URL过滤放开: {url}")
            return True

        parsed = urlparse(url)
        path = parsed.path or ""

        # 详细日志记录
        logging.debug(f"🔍 [URL_FILTER] 检查URL: {url}")
        logging.debug(f"   路径: '{path}', 查询参数: '{parsed.query}'")

        # 1. 明确的HTML后缀
        if path.lower().endswith((".html", ".htm", ".shtml")):
            logging.debug(f"   ✅ 通过HTML后缀检查")
            return True

        # 2. 没有后缀的路径（可能是动态页面）
        if not path or path == "/" or not any(path.lower().endswith(ext) for ext in
            ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.pdf',
             '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.tar', '.gz',
             '.mp3', '.mp4', '.avi', '.mov', '.flv', '.wmv']):
            logging.debug(f"   ✅ 通过无后缀路径检查（可能为动态页面）")
            return True

        # 3. 常见的CMS或系统路径模式
        cms_patterns = [
            '/index', '/list', '/detail', '/view', '/show', '/article', '/news',
            '/notice', '/info', '/content', '/page', '/item', '/cggg', '/tender'
        ]
        if any(pattern in path.lower() for pattern in cms_patterns):
            logging.debug(f"   ✅ 通过CMS路径模式检查")
            return True

        # 4. 包含查询参数的URL（通常是动态页面）
        if parsed.query:
            # 检查是否不是明显的资源文件
            if not any(path.lower().endswith(ext) for ext in
                ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg']):
                logging.debug(f"   ✅ 通过查询参数检查（动态页面）")
                return True

        logging.debug(f"   ❌ 过滤原因: 不符合HTML页面特征")
        return False

    except Exception as e:
        logging.error(f"❌ [URL_FILTER] 解析URL失败: {url}, 错误: {e}")
        return False


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize SQLite database and links table."""
    try:
        logging.info(f"🗄️ [DATABASE] 初始化数据库: {db_path}")

        # 确保数据库目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            logging.debug(f"📁 [DATABASE] 确保数据库目录存在: {db_dir}")

        # 连接数据库，增加超时和WAL模式
        logging.debug(f"🔌 [DATABASE] 连接数据库，超时30秒")
        conn = sqlite3.connect(db_path, timeout=30.0)

        try:
            conn.execute("PRAGMA journal_mode=WAL")
            logging.debug("✅ [DATABASE] WAL模式启用成功")
        except sqlite3.Error as e:
            logging.warning(f"⚠️ [DATABASE] WAL模式启用失败: {e}，继续使用默认模式")

        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='procurement_links'"
        )
        table_exists = cursor.fetchone() is not None

        if table_exists:
            logging.info("📋 [DATABASE] procurement_links表已存在")
            # 检查表结构
            cursor.execute("PRAGMA table_info(procurement_links)")
            columns = [row[1] for row in cursor.fetchall()]
            logging.debug(f"📋 [DATABASE] 现有列: {columns}")
        else:
            logging.info("🏗️ [DATABASE] 创建procurement_links表")

        # Create table if not exists (full schema for new DBs)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS procurement_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                base_url TEXT NOT NULL,
                url TEXT NOT NULL,
                link_text TEXT,
                first_seen_at TEXT,
                last_seen_at TEXT,
                is_latest INTEGER DEFAULT 0,
                UNIQUE(base_url, url)
            )
            """
        )

        if not table_exists:
            logging.info("✅ [DATABASE] procurement_links表创建成功")

        # 验证表是否可访问
        cursor.execute("SELECT COUNT(*) FROM procurement_links")
        count = cursor.fetchone()[0]
        logging.info(f"📊 [DATABASE] procurement_links表当前记录数: {count}")

        conn.commit()
        logging.info("✅ [DATABASE] 数据库初始化完成")

        return conn

    except sqlite3.Error as e:
        logging.error(f"❌ [DATABASE] 数据库初始化失败: {e}")
        raise
    except Exception as e:
        logging.error(f"❌ [DATABASE] 初始化过程发生意外错误: {e}")
        raise

  

async def fallback_crawl_procurement_links(
    base_url: str,
    max_depth: int | None = None,
    max_pages: int | None = None,
    keywords: list[str] | None = None,
) -> Dict[str, Any]:
    """
    Fallback crawling method using requests library when Playwright fails.
    使用 requests + BeautifulSoup 实现一个简单的 BFS 爬取，
    max_depth / max_pages 参数与 BFSDeepCrawlStrategy 含义一致。
    """
    import requests
    from bs4 import BeautifulSoup

    start_time = time.time()

    logging.info(f"🚀 [FALLBACK_CRAWLER] 开始Fallback爬取任务")
    logging.info(f"📋 [FALLBACK_CRAWLER] 基础URL: {base_url}")
    logging.info(f"⚙️ [FALLBACK_CRAWLER] 参数配置 - max_depth: {max_depth}, max_pages: {max_pages}")
    logging.info(f"🔑 [FALLBACK_CRAWLER] 关键词: {keywords if keywords else '使用默认关键词'}")

    if not base_url:
        logging.error(f"❌ [FALLBACK_CRAWLER] base_url不能为空")
        raise ValueError("base_url must not be empty")

    # 检测是否为无限制模式
    unlimited_mode = (max_depth and max_depth >= 20) and (max_pages and max_pages >= 500)
    if unlimited_mode:
        logging.info(f"🔥 [UNLIMITED_MODE] 检测到无限制模式 - 完全放开所有限制!")
        logging.info(f"   - max_depth: {max_depth} (>=20)")
        logging.info(f"   - max_pages: {max_pages} (>=500)")
        logging.info(f"   - URL过滤: 放开")
        logging.info(f"   - 关键词过滤: 放开")

    # Extract domain for filtering
    domain_match = re.search(r"https?://([^/]+)", base_url)
    domain = domain_match.group(1) if domain_match else "hospital-cqmu.com"
    logging.info(f"🌐 [FALLBACK_CRAWLER] 解析域名: {domain}")

    # SQLite database path (使用与主应用相同的数据库路径)
    db_path = os.path.abspath(os.path.join("data", "hospital_scanner_new.db"))
    logging.info(f"🗄️ [FALLBACK_CRAWLER] 数据库路径: {db_path}")
    logging.debug(f"📁 [FALLBACK_CRAWLER] 当前工作目录: {os.getcwd()}")

    conn = init_db(db_path)
    cursor = conn.cursor()

    # 检查表是否已存在并统计现有记录
    cursor.execute("SELECT COUNT(*) FROM procurement_links")
    before_count = cursor.fetchone()[0]
    logging.info(f"📊 [FALLBACK_CRAWLER] 爬虫前记录数: {before_count}")

    # Current run timestamp
    now = datetime.datetime.utcnow().isoformat(timespec="seconds")

    # Before this run, mark previous "latest" records for this base_url as not latest
    logging.info(f"🔄 [FALLBACK_CRAWLER] 标记之前的latest记录为非最新状态")
    try:
        cursor.execute(
            "UPDATE procurement_links SET is_latest = 0 WHERE base_url = ?",
            (base_url,),
        )
        updated_count = cursor.rowcount
        logging.info(f"✅ [FALLBACK_CRAWLER] 已标记 {updated_count} 条旧记录为非最新状态")
    except sqlite3.Error as e:
        logging.error(f"❌ [FALLBACK_CRAWLER] 更新latest状态失败: {e}")
        raise

    # Store unique URLs and their link text（仅记录 html / htm 后缀的页面）
    all_raw_urls: Set[str] = set()
    url_to_text: Dict[str, str] = {}

    # BFS 队列，元素为 (url, depth)，起点可以是无后缀列表页，但只记录 HTML 详情页
    # 增加默认参数以提高覆盖率
    max_depth_val = max_depth or 10  # 从5增加到10
    max_pages_val = max_pages or 100  # 从27增加到100
    queue: list[tuple[str, int]] = [(base_url, 0)]
    visited_pages: Set[str] = set()

    # 无限制模式已在函数开始时检测 (unlimited_mode变量)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    logging.info(f"🔍 [FALLBACK_CRAWLER] 开始BFS爬取: max_depth={max_depth_val}, max_pages={max_pages_val}")
    logging.info(f"📋 [FALLBACK_CRAWLER] 初始队列长度: {len(queue)}")

    processed_count = 0
    try:
        while queue and len(visited_pages) < max_pages_val:
            current_url, depth = queue.pop(0)
            processed_count += 1

            logging.debug(f"🔄 [FALLBACK_CRAWLER] [{processed_count}/{len(visited_pages)+1}] 处理URL: {current_url}, depth: {depth}")

            if current_url in visited_pages:
                logging.debug(f"⏭️ [FALLBACK_CRAWLER] URL已访问，跳过: {current_url}")
                continue

            if depth > max_depth_val:
                logging.debug(f"⏭️ [FALLBACK_CRAWLER] 超出最大深度，跳过: {current_url}, depth: {depth}")
                continue

            visited_pages.add(current_url)
            logging.info(f"🌐 [FALLBACK_CRAWLER] 开始请求页面: {current_url}")

            try:
                response = requests.get(current_url, headers=headers, timeout=30)
                response.raise_for_status()
                logging.info(f"✅ [FALLBACK_CRAWLER] 页面请求成功: {current_url}")
                logging.debug(f"   状态码: {response.status_code}")
                logging.debug(f"   内容大小: {len(response.content)} bytes")
                logging.debug(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            except Exception as e:
                logging.error(f"❌ [FALLBACK_CRAWLER] 页面请求失败: {current_url}")
                logging.error(f"   错误详情: {e}")
                continue

            # 仅记录 html / htm 页面
            if _is_html_page(current_url) and current_url not in all_raw_urls:
                all_raw_urls.add(current_url)
                logging.info(f"📄 [FALLBACK_CRAWLER] 发现HTML页面: {current_url}")

            soup = BeautifulSoup(response.content, "html.parser")
            found_links_on_page = 0
            processed_links_on_page = 0

            logging.debug(f"🔍 [FALLBACK_CRAWLER] 开始解析页面链接: {current_url}")

            # Extract all links on this page
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                text = link.get_text(strip=True)
                processed_links_on_page += 1

                if not href:
                    logging.debug(f"⏭️ [FALLBACK_CRAWLER] 跳过空链接")
                    continue

                # 详细日志：记录前10个发现的链接
                if processed_links_on_page <= 10:
                    logging.info(f"🔗 [FALLBACK_CRAWLER] 发现链接 #{processed_links_on_page}: href='{href}', text='{text[:50]}...'")

                # Convert relative URLs to absolute
                original_href = href
                if href.startswith("/"):
                    href = f"https://{domain}{href}"
                    logging.debug(f"🔧 [FALLBACK_CRAWLER] 转换相对URL: {original_href} -> {href}")
                elif href.startswith("#"):
                    if processed_links_on_page <= 5:  # 只记录前5个锚点链接
                        logging.info(f"⏭️ [FALLBACK_CRAWLER] 跳过锚点链接: {href}")
                    continue  # Skip anchors
                elif not href.startswith("http"):
                    # 🔧 [FIX] 使用urljoin转换相对链接为绝对链接
                    new_href = urljoin(current_url, href)
                    logging.info(f"🔧 [CONVERT] BeautifulSoup相对链接转换: {href} -> {new_href}")
                    href = new_href
                    # 不再continue，继续后续处理

                # 只保留同域链接参与后续遍历
                if domain not in href:
                    if processed_links_on_page <= 5:  # 只记录前5个外域链接
                        logging.info(f"🚫 [FALLBACK_CRAWLER] 跳过外域链接: {href}")
                    continue

                # HTML页面检查
                html_check_result = _is_html_page(href, unlimited_mode)
                if html_check_result:
                    all_raw_urls.add(href)
                    if text:
                        url_to_text[href] = text
                    else:
                        # 无限制模式：记录所有有意义的链接
                        logging.info(f"🔥 [UNLIMITED_MODE] 处理链接: {href}")
                        logging.info(f"   文本: '{text}'")
                        logging.info(f"   将被记录到数据库: 是")

                found_links_on_page += 1

                # 无论是否为 html，只要同域且满足深度/数量限制，都可以进入 BFS 队列
                if (
                    href not in visited_pages
                    and depth + 1 <= max_depth_val
                    and len(visited_pages) + len(queue) < max_pages_val
                ):
                    queue.append((href, depth + 1))
                    logging.debug(f"➕ [FALLBACK_CRAWLER] 加入队列: {href} (depth {depth + 1})")

            logging.info(f"📊 [FALLBACK_CRAWLER] 页面链接解析完成: {current_url}")
            logging.info(f"   处理链接数: {processed_links_on_page}, 发现有效链接数: {found_links_on_page}")
            logging.info(f"   队列当前长度: {len(queue)}")
            logging.info(f"   已访问页面数: {len(visited_pages)}")
            logging.info(f"   发现HTML页面总数: {len(all_raw_urls)}")

    except Exception as e:
        print(f"Fallback crawling failed: {e}")
        raise

    # Write all unique URLs into database
    new_or_updated = 0
    for raw_url in sorted(all_raw_urls):
        link_text = url_to_text.get(raw_url)

        # 无限制模式：跳过关键词过滤，直接写入数据库
        if unlimited_mode:
            logging.info(f"🔥 [UNLIMITED_MODE] 关键词过滤放开: {raw_url}")
            if link_text:
                logging.info(f"   链接文本: '{link_text[:100]}...'")
        else:
            # Apply dynamic keyword filter if provided; otherwise fall back to built-in keywords
            if keywords:
                text_for_match = link_text or ""
                if not any(kw and kw in text_for_match for kw in keywords):
                    continue
            else:
                if not _has_keyword(link_text, tuple(keywords) if keywords else None, unlimited_mode):
                    continue
        try:
            # 先检查记录是否已存在
            cursor.execute(
                "SELECT COUNT(*) FROM procurement_links WHERE base_url = ? AND url = ?",
                (base_url, raw_url)
            )
            exists = cursor.fetchone()[0] > 0

            if exists:
                # 记录已存在，执行UPDATE
                cursor.execute(
                    """
                    UPDATE procurement_links SET
                        link_text = COALESCE(?, procurement_links.link_text),
                        last_seen_at = ?,
                        is_latest = 1
                    WHERE base_url = ? AND url = ?
                    """,
                    (link_text, now, base_url, raw_url),
                )
                print(f"🔄 更新记录: {raw_url[:80]}")
            else:
                # 记录不存在，执行INSERT
                cursor.execute(
                    """
                    INSERT INTO procurement_links (
                        base_url,
                        url,
                        link_text,
                        first_seen_at,
                        last_seen_at,
                        is_latest
                    )
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (base_url, raw_url, link_text, now, now),
                )
                print(f"➕ 新增记录: {raw_url[:80]}")

            # 无论是INSERT还是UPDATE都算作更新
            new_or_updated += 1

        except sqlite3.Error as e:
            print(f"DB write failed for {raw_url}: {e}")
            import traceback
            traceback.print_exc()

    conn.commit()

    # 验证写入结果
    cursor.execute("SELECT COUNT(*) FROM procurement_links")
    after_count = cursor.fetchone()[0]
    print(f"📊 爬虫后记录数: {after_count}")
    print(f"📊 新增记录数: {after_count - before_count}")

    conn.close()

    print(f"\nFallback crawl finished. URLs written to DB: {db_path}")
    print(f"Database absolute path: {os.path.abspath(db_path)}")
    print(f"Summary: collected {len(all_raw_urls)} unique URLs, inserted/updated {new_or_updated} records")

    return {
        "base_url": base_url,
        "total_urls": len(all_raw_urls),
        "new_or_updated": new_or_updated,
        "db_path": db_path,
    }


async def _crawl_procurement_links_impl(
    base_url: str,
    max_depth: int | None = None,
    max_pages: int | None = None,
    keywords: list[str] | None = None,
) -> Dict[str, Any]:
    """
    Core async implementation to crawl procurement links starting from the given base_url
    and store results into the SQLite database, following the same logic as the original script.
    This function assumes it is running in an event loop that supports asyncio subprocess APIs.
    """
    start_time = time.time()

    logging.info(f"🚀 [CRAWLER] 开始采购链接爬取任务")
    logging.info(f"📋 [CRAWLER] 基础URL: {base_url}")
    logging.info(f"⚙️ [CRAWLER] 参数配置 - max_depth: {max_depth}, max_pages: {max_pages}")
    logging.info(f"🔑 [CRAWLER] 关键词: {keywords if keywords else '使用默认关键词'}")

    if not base_url:
        logging.error(f"❌ [CRAWLER] base_url不能为空")
        raise ValueError("base_url must not be empty")

    # Extract domain for filtering
    domain_match = re.search(r"https?://([^/]+)", base_url)
    domain = domain_match.group(1) if domain_match else "hospital-cqmu.com"
    logging.info(f"🌐 [CRAWLER] 解析域名: {domain}")

    # SQLite database path (使用与主应用相同的数据库路径)
    db_path = os.path.abspath(os.path.join("data", "hospital_scanner_new.db"))
    logging.info(f"🗄️ [CRAWLER] 数据库路径: {db_path}")

    conn = init_db(db_path)
    cursor = conn.cursor()

    # Current run timestamp (ISO string)
    now = datetime.datetime.utcnow().isoformat(timespec="seconds")

    # Before this run, mark previous "latest" records for this base_url as not latest
    logging.info(f"🔄 [CRAWLER] 标记之前的latest记录为非最新状态")
    try:
        cursor.execute(
            "UPDATE procurement_links SET is_latest = 0 WHERE base_url = ?",
            (base_url,),
        )
        updated_count = cursor.rowcount
        logging.info(f"✅ [CRAWLER] 已标记 {updated_count} 条旧记录为非最新状态")
    except sqlite3.Error as e:
        logging.error(f"❌ [CRAWLER] 更新latest状态失败: {e}")
        raise

    # Store unique URLs and their link text（仅记录 html / htm 后缀的页面）
    all_raw_urls: Set[str] = set()
    url_to_text: Dict[str, str] = {}

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        # Windows-specific configuration to handle subprocess issues
        browser_type="chromium" if sys.platform != "win32" else "chromium",
        extra_args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            # Character encoding improvements
            "--disable-blink-features=AutomationControlled",
            "--enable-features=NetworkService",
            "--disable-features=VizDisplayCompositor",
            "--disable-web-security",
            "--allow-running-insecure-content"
        ] if sys.platform == "win32" else [
            # Character encoding improvements for non-Windows platforms
            "--enable-features=NetworkService",
            "--disable-blink-features=AutomationControlled"
        ]
    )
    print("max depth:", max_depth, "max pages:", max_pages)
    deep_crawl_strategy = BFSDeepCrawlStrategy(
        max_depth=max_depth or 5,
        max_pages=max_pages or 27,
        include_external=False,
        filter_chain=FilterChain(
            [
                DomainFilter(allowed_domains=[domain]),
                ContentTypeFilter(allowed_types=["text/html"]),
            ]
        ),
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        deep_crawl_strategy=deep_crawl_strategy,
        stream=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        last_request_time = 0.0

        print(f"Start crawling procurement page: {base_url}")

        async for result in await crawler.arun(
            url=base_url,
            config=run_config,
        ):
            # Throttle requests
            current_time = time.time()
            if current_time - last_request_time < 1.0:
                await asyncio.sleep(1.0 - (current_time - last_request_time))
            last_request_time = current_time
            print(result.url)
            if result.success:
                # 1. Page URL itself（仅记录 html / htm 页面）
                if _is_html_page(result.url) and result.url not in all_raw_urls:
                    all_raw_urls.add(result.url)
                    print(f"New HTML URL: {result.url}")

                # 2. Links from result.links（仅记录 html / htm 页面）
                if hasattr(result, "links") and result.links:
                    for link in result.links:
                        if isinstance(link, str):
                            link_url = link
                            link_text = None
                        else:
                            # Support Link(url=..., text=...)
                            link_url = getattr(link, "url", None)
                            link_text = getattr(link, "text", None)

                        if not link_url or domain not in link_url:
                            continue

                        # 只记录 html / htm 页面
                        if not _is_html_page(link_url):
                            continue

                        if link_url not in all_raw_urls:
                            all_raw_urls.add(link_url)
                            print(f"New HTML URL: {link_url}")

                        if link_text:
                            clean_link_text = clean_text_encoding(link_text.strip())
                            if clean_link_text:
                                url_to_text.setdefault(link_url, clean_link_text)

                # 3. Extract [text](url) from markdown（仅记录 html / htm 页面）
                markdown = result.markdown or ""
                pair_pattern = re.compile(
                    r"\[([^\]]+)\]\((https?://" + re.escape(domain) + r"[^\)]*)\)"
                )
                for link_text, link_url in pair_pattern.findall(markdown):
                    # 只记录 html / htm 页面
                    if not _is_html_page(link_url):
                        continue

                    if link_url not in all_raw_urls:
                        all_raw_urls.add(link_url)
                        print(f"New HTML URL (markdown): {link_url}")

                    clean_link_text = clean_text_encoding(link_text.strip())
                    if clean_link_text:
                        url_to_text.setdefault(link_url, clean_link_text)

            else:
                print(
                    f"Crawl failed: {getattr(result, 'url', '')} -> {result.error_message}"
                )

    # Write all unique URLs into database
    new_or_updated = 0
    filtered_out = 0

    print(f"🔍 [DEBUG] 开始处理 {len(all_raw_urls)} 个发现的URL...")
    logging.info(f"🔍 [CRAWLER] 开始关键词过滤，总共发现 {len(all_raw_urls)} 个URL")
    logging.info(f"🔑 [CRAWLER] 使用的关键词: {keywords if keywords else '默认关键词'}")

    processed_count = 0
    for raw_url in sorted(all_raw_urls):
        processed_count += 1
        link_text = url_to_text.get(raw_url)

        logging.debug(f"🔗 [CRAWLER] [{processed_count}/{len(all_raw_urls)}] 处理链接: {raw_url}")
        logging.debug(f"📝 [CRAWLER] 链接文本: '{link_text}'")

        # Apply dynamic keyword filter if provided; otherwise fall back to built-in keywords
        keyword_filter_pass = False

        if keywords:
            text_for_match = link_text or ""
            matched_keywords = [kw for kw in keywords if kw and kw in text_for_match]
            if not matched_keywords:
                logging.debug(f"❌ [CRAWLER] 关键词过滤失败 - 文本中未找到关键词: {keywords}")
                logging.debug(f"   失败URL: {raw_url}")
                filtered_out += 1
                keyword_filter_pass = False
            else:
                logging.info(f"✅ [CRAWLER] 关键词匹配成功: {matched_keywords}")
                logging.info(f"   匹配URL: {raw_url}")
                logging.info(f"   链接文本: '{link_text}'")
                keyword_filter_pass = True
        else:
            # 无限制模式检测
            if unlimited_mode and link_text and len(link_text.strip()) > 3:
                # 在无限制模式下，几乎所有有意义的内容都通过
                text_lower = link_text.lower().strip()

                # 检查是否包含中文字符
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text_lower)

                # 排除纯通用词
                common_words = {"的", "和", "与", "为", "对", "在", "是", "有", "个", "中", "人", "公司", "医院", "时间", "项目", "页面", "更多", "查看", "详情", "信息", "列表", "内容"}
                is_common_word = text_lower in common_words

                # 如果有中文且不是纯通用词，则通过
                if has_chinese and not is_common_word and len(text_lower) > 2:
                    logging.info(f"✅ [UNLIMITED_MODE] 无限制模式通过: '{link_text}'")
                    logging.info(f"   匹配URL: {raw_url}")
                    keyword_filter_pass = True
                else:
                    logging.debug(f"⏭️ [UNLIMITED_MODE] 跳过通用内容: '{link_text}'")
                    logging.debug(f"   中文: {has_chinese}, 通用词: {is_common_word}")
                    filtered_out += 1
                    keyword_filter_pass = False
            else:
                # 正常关键词匹配
                if not _has_keyword(link_text, tuple(keywords) if keywords else None):
                    logging.debug(f"❌ [CRAWLER] 默认关键词过滤失败")
                    logging.debug(f"   失败URL: {raw_url}")
                    filtered_out += 1
                    keyword_filter_pass = False
                else:
                    logging.info(f"✅ [CRAWLER] 默认关键词匹配成功")
                    logging.info(f"   匹配URL: {raw_url}")
                    logging.info(f"   链接文本: '{link_text}'")
                    keyword_filter_pass = True

        if keyword_filter_pass:
            logging.info(f"💾 [CRAWLER] 关键词匹配通过，准备保存到数据库: {raw_url}")

            try:
                # 先检查记录是否已存在
                logging.debug(f"🔍 [DATABASE] 检查记录是否存在: {raw_url}")
                cursor.execute(
                    "SELECT COUNT(*) FROM procurement_links WHERE base_url = ? AND url = ?",
                    (base_url, raw_url)
                )
                exists = cursor.fetchone()[0] > 0
                logging.debug(f"📋 [DATABASE] 记录存在性检查结果: {exists}")

                if exists:
                    # 记录已存在，执行UPDATE
                    logging.debug(f"🔄 [DATABASE] 更新现有记录: {raw_url}")
                    cursor.execute(
                        """
                        UPDATE procurement_links SET
                            link_text = COALESCE(?, procurement_links.link_text),
                            last_seen_at = ?,
                            is_latest = 1
                        WHERE base_url = ? AND url = ?
                        """,
                        (link_text, now, base_url, raw_url),
                    )
                    logging.info(f"✅ [DATABASE] 成功更新记录: {raw_url[:80]}")
                else:
                    # 记录不存在，执行INSERT
                    logging.debug(f"➕ [DATABASE] 插入新记录: {raw_url}")
                    cursor.execute(
                        """
                        INSERT INTO procurement_links (
                            base_url,
                            url,
                            link_text,
                            first_seen_at,
                            last_seen_at,
                            is_latest
                        )
                        VALUES (?, ?, ?, ?, ?, 1)
                        """,
                        (base_url, raw_url, link_text, now, now),
                    )
                    logging.info(f"✅ [DATABASE] 成功新增记录: {raw_url[:80]}")

                # 无论是INSERT还是UPDATE都算作更新
                new_or_updated += 1

            except sqlite3.Error as e:
                logging.error(f"❌ [DATABASE] 数据库写入失败 - URL: {raw_url}")
                logging.error(f"   错误详情: {e}")
                logging.debug(f"   链接文本: {link_text}")
                import traceback
                logging.debug(f"   堆栈跟踪: {traceback.format_exc()}")

    try:
        conn.commit()
        logging.info(f"💾 [DATABASE] 数据库事务提交成功")
    except sqlite3.Error as e:
        logging.error(f"❌ [DATABASE] 数据库事务提交失败: {e}")
        raise
    finally:
        try:
            conn.close()
            logging.debug(f"🔌 [DATABASE] 数据库连接已关闭")
        except:
            pass

    # 计算执行时间
    end_time = time.time()
    execution_time = end_time - start_time

    logging.info(f"🎉 [CRAWLER] 爬取任务完成")
    logging.info(f"⏱️ [CRAWLER] 总执行时间: {execution_time:.2f}秒")
    logging.info(f"🗄️ [CRAWLER] 数据库路径: {os.path.abspath(db_path)}")
    logging.info(f"📊 [CRAWLER] 执行结果统计:")
    logging.info(f"   - 发现URL总数: {len(all_raw_urls)}")
    logging.info(f"   - 关键词过滤通过: {new_or_updated}")
    logging.info(f"   - 关键词过滤排除: {filtered_out}")
    logging.info(f"   - 过滤通过率: {(new_or_updated/len(all_raw_urls)*100):.1f}%" if all_raw_urls else "   - 过滤通过率: 0%")

    if filtered_out > 0:
        logging.warning(f"⚠️ [CRAWLER] 被关键词过滤掉的URL数量: {filtered_out}")
        logging.info(f"💡 [CRAWLER] 建议检查关键词匹配逻辑或扩展关键词列表")
        if len(all_raw_urls) > 0:
            filter_rate = (filtered_out / len(all_raw_urls)) * 100
            logging.info(f"📈 [CRAWLER] 过滤率: {filter_rate:.1f}%")

    if len(all_raw_urls) == 0:
        logging.warning(f"⚠️ [CRAWLER] 未发现任何URL，可能存在以下问题:")
        logging.warning(f"   1. 网站无法访问或反爬机制")
        logging.warning(f"   2. URL过滤规则过于严格")
        logging.warning(f"   3. 深度和页面参数设置过小")
        logging.warning(f"   4. 网站结构不包含HTML页面")

    return {
        "base_url": base_url,
        "total_urls": len(all_raw_urls),
        "new_or_updated": new_or_updated,
        "filtered_out": filtered_out,
        "execution_time": execution_time,
        "db_path": db_path,
    }


async def crawl_procurement_links(
    base_url: str,
    max_depth: int | None = None,
    max_pages: int | None = None,
    keywords: list[str] | None = None,
) -> Dict[str, Any]:
    """
    Public async API used by FastAPI and the script entry point.
    在 Windows 环境下，Playwright 的异步子进程支持有限，容易抛出 NotImplementedError。
    为了稳定性，Windows 上直接使用 fallback（requests + BeautifulSoup）版本；
    其它平台则使用 crawl4ai 的 AsyncWebCrawler 实现深度爬取。
    """
    # Windows 下直接走回退实现，完全绕过 Playwright / AsyncWebCrawler
    if sys.platform.startswith("win"):
        return await fallback_crawl_procurement_links(
            base_url, max_depth=max_depth, max_pages=max_pages, keywords=keywords
        )

    loop = asyncio.get_running_loop()

    def _worker(
        url: str,
        depth: int | None,
        pages: int | None,
        kw_list: list[str] | None,
    ) -> Dict[str, Any]:
        # Create a dedicated event loop that supports subprocess APIs.
        if sys.platform.startswith("win"):
            worker_loop = asyncio.SelectorEventLoop()
        else:
            worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(worker_loop)
        try:
            # Try full Playwright-based crawling first
            return worker_loop.run_until_complete(
                _crawl_procurement_links_impl(url, depth, pages, kw_list)
            )
        except NotImplementedError:
            # On Windows without proper subprocess support, fall back to requests/html parsing
            return worker_loop.run_until_complete(
                fallback_crawl_procurement_links(url, depth, pages, kw_list)
            )
        finally:
            worker_loop.close()

    return await loop.run_in_executor(None, _worker, base_url, max_depth, max_pages, keywords)


async def main() -> None:
    # Default target procurement page for standalone script usage
    base_url = "https://www.hospital-cqmu.com/gzb_cgxx"
    await crawl_procurement_links(base_url)


if __name__ == "__main__":
    asyncio.run(main())
