import requests
import re
from typing import Tuple, Optional
import json

def fetch_infoq_data(id_value: str, alias: str) -> Tuple[Optional[str], str, str]:
    """获取 InfoQ 热门文章"""
    # InfoQ 直接访问返回 451，尝试使用 API 或 RSS
    
    # 尝试 1: InfoQ API
    api_url = "https://www.infoq.cn/public/v1/article/getList"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.infoq.cn/",
    }
    
    try:
        # 尝试 API
        params = {"size": 25, "type": 1}  # type=1 可能是热门文章
        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        items = []
        seen_urls = set()
        
        # 解析 API 响应
        articles = data.get("data", [])
        for article in articles[:25]:
            if isinstance(article, dict):
                title = article.get("article_title") or article.get("title")
                article_id = article.get("article_id") or article.get("id")
                
                if title and article_id:
                    link = f"https://www.infoq.cn/article/{article_id}"
                    
                    if link not in seen_urls:
                        items.append({
                            "title": title.strip(),
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
            print(f"请求 {id_value} 失败: API 未返回有效数据")
            return None, id_value, alias
            
    except Exception as e:
        # 如果 API 失败，尝试 RSS
        try:
            rss_url = "https://www.infoq.cn/feed"
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            items = []
            seen_urls = set()
            
            for item in root.findall('.//item')[:25]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    link = link_elem.text
                    
                    if title and link and link not in seen_urls:
                        items.append({
                            "title": title.strip(),
                            "url": link,
                            "mobileUrl": link
                        })
                        seen_urls.add(link)
            
            if items:
                result = {
                    "status": "success",
                    "items": items
                }
                print(f"获取 {id_value} 成功（RSS数据）- 抓取到 {len(items)} 条")
                return json.dumps(result, ensure_ascii=False), id_value, alias
                
        except Exception as e2:
            pass
        
        print(f"请求 {id_value} 失败: {e}")
        return None, id_value, alias
