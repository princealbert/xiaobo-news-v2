#!/usr/bin/env python3
"""
Web 应用自动化测试 - Playwright 版本（修复版）
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
import time

BASE_URL = "https://xiaobo-news-v2.vercel.app"
REPORT_FILE = "/Users/albert/documents/茉莉空间/report/daily_test_{}.md".format(
    datetime.now().strftime("%Y%m%d")
)

def run_tests():
    results = {"passed": 0, "failed": 0, "tests": []}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 测试性能（使用 performance timing）
        start_time = time.time()
        page.goto(BASE_URL, timeout=30000)
        page.wait_for_load_state("networkidle")
        load_time = (time.time() - start_time) * 1000
        
        # 测试 8: 页面性能（修复版）
        try:
            assert load_time < 10000, f"加载时间过长：{load_time:.0f}ms"
            results["tests"].append({"name": "页面性能", "status": f"✅ 通过 ({load_time:.0f}ms)"})
            results["passed"] += 1
        except Exception as e:
            results["tests"].append({"name": "页面性能", "status": "❌ 失败", "error": str(e)})
            results["failed"] += 1
        
        browser.close()
    
    return results

if __name__ == '__main__':
    results = run_tests()
    print(f"✅ 通过：{results['passed']}, ❌ 失败：{results['failed']}")
