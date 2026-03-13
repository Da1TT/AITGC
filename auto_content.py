import os
import json
import re
from openai import OpenAI
from datetime import datetime

# ==========================================
# TechGuide Global - AI 内容全自动生成脚本 (SEO 终极版)
# 包含：长文生成 + HTML单页渲染 + Sitemap.xml自动更新
# ==========================================

# 1. 配置 AI API
api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE", "https://api.moonshot.cn/v1") 

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

# 2. 撰写提示词 (要求 AI 输出包含正文的完整 JSON)
prompt = """
You are an expert tech blogger and SEO specialist. 
Write a comprehensive, highly engaging tech blog post (at least 400 words) about a trending AI tool, AI automation strategy, or ChatGPT prompt engineering.
Output ONLY a valid JSON object with the following structure:
{
  "title": "A catchy, SEO-friendly title",
  "category": "One word: TOOLS, MONEY, PROMPTS, or NEWS",
  "description": "Two sentences explaining why this matters to the reader.",
  "read_time": "e.g., 4 min",
  "content": "The full article body formatted in valid HTML. Use <h2> for subheadings, <p> for paragraphs, and <ul> for lists. Do NOT include <html> or <body> tags, just the inner content. Make it highly readable."
}
"""

def clean_json_response(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

def update_sitemap(url_path):
    """自动更新网站地图，帮助 Google 快速收录"""
    sitemap_file = 'sitemap.xml'
    base_url = "https://techguidechina.com"
    full_url = f"{base_url}/{url_path}"
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    new_url_node = f"""
    <url>
        <loc>{full_url}</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>"""

    if not os.path.exists(sitemap_file):
        # 如果不存在，创建新的 sitemap
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>{new_url_node}
</urlset>"""
    else:
        # 如果存在，插入新的 URL 节点
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            content = f.read()
        sitemap_content = content.replace('</urlset>', f'{new_url_node}\n</urlset>')

    with open(sitemap_file, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"✅ Sitemap 已更新: 增加了 {full_url}")

try:
    print(f"[{datetime.now()}] 正在呼叫 Kimi AI 生成深度长文...")
    
    # 3. 请求 AI
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that outputs ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    raw_content = response.choices[0].message.content
    cleaned_content = clean_json_response(raw_content)
    data = json.loads(cleaned_content)
    
    print(f"成功生成文章: {data['title']}")

    # 4. 生成独立的 HTML 文章页面
    safe_title = "".join([c if c.isalnum() else "-" for c in data['title'].lower()])
    safe_title = re.sub(r'-+', '-', safe_title).strip('-')
    file_name = f"{safe_title}.html"
    
    os.makedirs('articles', exist_ok=True)
    
    article_page_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} - TechGuide Global</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ dark: '#020617', primary: '#3b82f6' }} }} }} }}
    </script>
    <style>
        body {{ font-family: 'Inter', system-ui, sans-serif; }}
        .article-body h2 {{ font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-top: 2.5rem; margin-bottom: 1rem; }}
        .article-body h3 {{ font-size: 1.4rem; font-weight: 700; color: #f1f5f9; margin-top: 2rem; margin-bottom: 0.8rem; }}
        .article-body p {{ margin-bottom: 1.5rem; font-size: 1.125rem; line-height: 1.8; color: #cbd5e1; }}
        .article-body ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1.5rem; color: #cbd5e1; }}
        .article-body li {{ margin-bottom: 0.5rem; }}
        .article-body strong {{ color: #ffffff; }}
        .article-body a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid #3b82f6; transition: border-color 0.2s; }}
        .article-body a:hover {{ border-color: #93c5fd; }}
    </style>
</head>
<body class="bg-dark text-slate-300 min-h-screen flex flex-col">
    <nav class="border-b border-white/5 p-6 bg-dark/95 backdrop-blur-xl sticky top-0 z-50">
        <div class="max-w-4xl mx-auto flex items-center justify-between">
            <a href="../index.html" class="text-slate-400 hover:text-white transition-colors flex items-center gap-2 font-medium">
                <i data-lucide="arrow-left" class="w-4 h-4"></i> Back to TechGuide
            </a>
            <button class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors">
                Subscribe
            </button>
        </div>
    </nav>
    <main class="max-w-3xl mx-auto px-6 py-12 w-full flex-grow">
        <div class="mb-12 pb-8 border-b border-slate-800">
            <span class="text-primary font-bold text-xs tracking-widest uppercase bg-primary/10 px-3 py-1.5 rounded-full">{data['category']}</span>
            <h1 class="text-4xl md:text-5xl font-extrabold text-white mt-6 mb-6 leading-[1.2]">{data['title']}</h1>
            <div class="text-slate-400 text-sm flex items-center gap-6 font-medium">
                <span class="flex items-center gap-2"><i data-lucide="calendar" class="w-4 h-4 text-slate-500"></i> {datetime.now().strftime('%B %d, %Y')}</span>
                <span class="flex items-center gap-2"><i data-lucide="clock" class="w-4 h-4 text-slate-500"></i> {data['read_time']} read</span>
            </div>
        </div>
        
        <!-- 自动插入一张随机的科技感配图 -->
        <div class="mb-10 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
            <img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=800&auto=format&fit=crop" alt="AI Technology" class="w-full h-auto object-cover opacity-80 hover:opacity-100 transition-opacity">
        </div>

        <article class="article-body">
            {data['content']}
        </article>
        
        <!-- 文章底部的行动号召 (CTA) 预留位 -->
        <div class="mt-16 p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center">
            <h3 class="text-2xl font-bold text-white mb-3">Want more strategies like this?</h3>
            <p class="text-slate-400 mb-6">Join our newsletter to get the latest AI tools and automation guides delivered to your inbox.</p>
            <a href="../index.html" class="inline-block bg-white text-dark font-bold px-6 py-3 rounded-xl hover:bg-slate-200 transition-colors">Return to Home</a>
        </div>
    </main>
    <footer class="border-t border-white/5 py-8 text-center text-slate-600 text-sm bg-[#010409]">
        &copy; 2024 TechGuide Global. All rights reserved.
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""

    with open(f"articles/{file_name}", "w", encoding='utf-8') as f:
        f.write(article_page_html)
    print(f"✅ 独立文章页面已生成: articles/{file_name}")

    # 5. 更新 sitemap.xml
    update_sitemap(f"articles/{file_name}")

    # 6. 构建插入主页的 HTML 卡片
    new_article_html = f"""
                    <!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d')} -->
                    <a href="articles/{file_name}" class="block bg-slate-900/50 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-slate-600 transition-all duration-300 group">
                        <article class="flex flex-col sm:flex-row gap-6">
                            <div class="w-full sm:w-56 h-40 rounded-xl bg-gradient-to-br from-blue-900 to-slate-800 flex-shrink-0 flex items-center justify-center shadow-lg relative overflow-hidden">
                                <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=400&auto=format&fit=crop')] bg-cover bg-center opacity-40 mix-blend-overlay group-hover:scale-110 transition-transform duration-700"></div>
                                <i data-lucide="cpu" class="w-10 h-10 text-white/60 relative z-10"></i>
                            </div>
                            <div class="flex flex-col justify-center flex-grow py-1">
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-[10px] font-bold text-slate-400 px-2 py-0.5 bg-slate-800 rounded-md uppercase">{data['category']}</span>
                                    <span class="text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded-md">NEW</span>
                                </div>
                                <h3 class="text-xl font-bold text-white group-hover:text-primary transition-colors leading-tight">{data['title']}</h3>
                                <p class="text-sm text-slate-400 mt-2 line-clamp-2">{data['description']}</p>
                                <div class="mt-4 text-[11px] text-slate-500 font-medium tracking-wide flex items-center gap-4">
                                    <span>{data['read_time']} READ</span>
                                </div>
                            </div>
                        </article>
                    </a>"""

    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    if anchor in html_content:
        updated_html = html_content.replace(anchor, f"{anchor}\n{new_article_html}")
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print("✅ 主页 index.html 已更新！")
    else:
        print("❌ 错误：在 index.html 中找不到锚点标记。")

except Exception as e:
    print(f"💥 运行失败: {str(e)}")
