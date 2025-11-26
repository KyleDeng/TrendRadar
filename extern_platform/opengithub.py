import requests
import re
from typing import Tuple, Optional
import json

def fetch_opengithub_data(id_value: str, alias: str) -> Tuple[Optional[str], str, str]:
    """获取 GitHub Trending 热门项目"""
    # OpenGithub 网站使用动态加载，改用 GitHub Trending
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        items = []
        seen_urls = set()
        
        # 使用更精确的匹配方式，提取仓库信息和描述
        # 匹配 <article> 标签，每个仓库都在一个 article 中
        article_pattern = r'<article[^>]*class="Box-row"[^>]*>(.*?)</article>'
        articles = re.findall(article_pattern, html, re.DOTALL)
        
        for article in articles[:25]:
            # 提取仓库链接
            repo_match = re.search(r'<h2[^>]*class="h3[^"]*lh-condensed[^"]*"[^>]*>.*?href="(/[^/]+/[^/"]+)"', article, re.DOTALL)
            if not repo_match:
                continue
                
            path = repo_match.group(1)
            
            # 过滤掉非仓库链接
            if (path.startswith('/trending') or 
                path.startswith('/features') or
                path.startswith('/solutions') or
                path.startswith('/resources') or
                path.startswith('/sponsors') or
                path.count('/') != 2):
                continue
            
            # 提取仓库名称
            parts = path.strip('/').split('/')
            if len(parts) != 2:
                continue
                
            repo_name = f"{parts[0]}/{parts[1]}"
            full_url = f"https://github.com{path}"
            
            # 提取描述信息
            desc_match = re.search(r'<p[^>]*class="[^"]*col-9[^"]*color-fg-muted[^"]*"[^>]*>\s*(.*?)\s*</p>', article, re.DOTALL)
            description = ""
            if desc_match:
                # 清理 HTML 标签和多余空白
                description = re.sub(r'<[^>]+>', '', desc_match.group(1))
                description = re.sub(r'\s+', ' ', description).strip()
                # 限制描述长度
                if len(description) > 150:
                    description = description[:147] + "..."
            
            # 组合标题：仓库名 - 描述
            if description:
                title = f"{repo_name} - {description}"
            else:
                title = repo_name
            
            if full_url not in seen_urls:
                items.append({
                    "title": title,
                    "url": full_url,
                    "mobileUrl": full_url
                })
                seen_urls.add(full_url)
        
        if items:
            result = {
                "status": "success",
                "items": items
            }
            print(f"获取 {id_value} 成功（最新数据）- 抓取到 {len(items)} 条")
            return json.dumps(result, ensure_ascii=False), id_value, alias
        else:
            print(f"请求 {id_value} 失败: 未找到有效项目")
            return None, id_value, alias
            
    except Exception as e:
        print(f"请求 {id_value} 失败: {e}")
        return None, id_value, alias
