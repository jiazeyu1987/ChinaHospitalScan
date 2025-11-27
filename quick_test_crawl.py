import asyncio
import sys
import os

async def test_crawl():
    """快速测试爬虫功能"""
    print("🧪 快速测试爬虫数据库写入...")

    # 导入爬虫模块
    from crawl import fallback_crawl_procurement_links

    # 使用一个简单的测试URL
    test_url = "https://httpbin.org/html"

    print(f"测试URL: {test_url}")
    print(f"工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.executable}")

    try:
        # 运行爬虫
        result = await fallback_crawl_procurement_links(test_url, max_depth=1, max_pages=3)

        print(f"\n✅ 爬虫完成:")
        print(f"  Base URL: {result['base_url']}")
        print(f"  Total URLs: {result['total_urls']}")
        print(f"  New/Updated: {result['new_or_updated']}")
        print(f"  DB Path: {result['db_path']}")

    except Exception as e:
        print(f"❌ 爬虫失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crawl())