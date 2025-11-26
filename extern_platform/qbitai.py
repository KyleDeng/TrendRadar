import requests
import re
from typing import Tuple, Optional
import json

def fetch_qbitai_data(id_value: str, alias: str) -> Tuple[Optional[str], str, str]:
    """获取量子位最新文章"""
    url = "https://www.qbitai.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        items = []
        seen_urls = set()
        
        # 匹配文章链接: https://www.qbitai.com/2025/11/数字.html
        # 同时提取标题
        pattern = r'<a[^>]*href="(https://www\.qbitai\.com/\d{4}/\d{2}/\d+\.html)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        
        for link, title in matches[:25]:
            title = title.strip()
            if link not in seen_urls and title:
                items.append({
                    "title": title,
                    "url": link,
                    "mobileUrl": link
                })
                seen_urls.add(link)
        
        # 如果上面的正则没匹配到，尝试更宽松的模式
        if not items:
            pattern2 = r'href="(/\d{4}/\d{2}/\d+\.html)"[^>]*>([^<]+)</a>'
            matches2 = re.findall(pattern2, html)
            for path, title in matches2[:25]:
                link = f"https://www.qbitai.com{path}"
                title = title.strip()
                if link not in seen_urls and title:
                    items.append({
                        "title": title,
                        "url": link,
                        "mobileUrl": link
                    })
                    seen_urls.add(link)
        
        if items:
            result = {
                "status": "success",
                "items": items
            }
            print(f"获取 {id_value} 成功（最新数据）- 抓取到 {len(items)} 条")
            return json.dumps(result, ensure_ascii=False), id_value, alias
        else:
            print(f"请求 {id_value} 失败: 未找到有效文章")
            return None, id_value, alias
            
    except Exception as e:
        print(f"请求 {id_value} 失败: {e}")
        return None, id_value, alias
