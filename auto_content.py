import os
import json
import re
import sys
import time
from openai import OpenAI
from datetime import datetime
import random

# ==========================================
# TechGuide - 自动化发文引擎 (重试增强 + 高级UI适配)
# ==========================================

api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE")

# 修复 GitHub Actions 传递空字符串的 Bug
if not api_base or api_base.strip() == "":
    api_base = "https://api.moonshot.cn/v1"

if not api_key:
    print("❌ 致命错误：找不到 AI_API_KEY，请检查 GitHub Secrets 配置！")
    sys.exit(1)

print(f"🔍 [网络诊断] 当前使用的 API 节点地址: {api_base}")

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

prompt = """
You are an expert tech blogger and SEO specialist. 
Write a comprehensive, highly engaging tech blog post (at least 400 words) about a trending AI tool, AI automation strategy, or prompt engineering.
Output ONLY a valid JSON object with the following structure:
{
  "title": "A catchy, SEO-friendly title (e.g., Mastering AI Voice Cloning...)",
  "category": "One word: TOOLS, STRATEGY, or MONEY",
  "description": "Two sentences explaining the value of the guide.",
  "read_time": "e.g., 7 min",
  "content": "The full article body formatted in valid HTML. Use <h2> for subheadings, <p> for paragraphs, and <ul> for lists. Do NOT include <html> or <body> tags, just the inner content. Make it highly readable."
}
"""

def clean_json_response(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

image_pool = [
    "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1684369175836-e8f000305f24?q=80&w=600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1696258686454-60082b2c33e2?q=80&w=600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1655635643532-fa9ba2648cbe?q=80&w=600&auto=format&fit=crop"
]

MAX_RETRIES = 3
data = None

# 加入企业级重试机制，抵抗网络波动
for attempt in range(MAX_RETRIES):
    try:
        print(f"[{datetime.now()}] 正在呼叫 AI 撰写深度长文 (第 {attempt + 1} 次尝试)...")
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            timeout=45.0  # 增加超时时间
        )
        
        raw_content = response.choices[0].message.content
        cleaned_content = clean_json_response(raw_content)
        data = json.loads(cleaned_content)
        print(f"✅ 成功生成文章: {data['title']}")
        break  # 成功则跳出循环
        
    except Exception as e:
        print(f"⚠️ 第 {attempt + 1} 次请求失败: {e}")
        if attempt == MAX_RETRIES - 1:
            print("❌ 达到最大重试次数，网络彻底断开。请检查你的 API_BASE 网址是否已失效。")
            sys.exit(1)
        time.sleep(5) # 失败后等待 5 秒再重试

# 如果数据正常，开始构建网页
if data:
    date_str = datetime.now().strftime('%b %d')
    random_image = random.choice(image_pool)

    # 1. 生成独立的 HTML 文章页面 (适配你的 Dark Mode 风格)
    safe_title = "".join([c if c.isalnum() else "-" for c in data['title'].lower()])
    safe_title = re.sub(r'-+', '-', safe_title).strip('-')
    file_name = f"{safe_title}.html"
    
    os.makedirs('articles', exist_ok=True)
    
    article_page_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} - TechGuide</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ dark: '#020617', primary: '#3b82f6' }} }} }} }}
    </script>
    <style>
        body {{ font-family: 'Inter', system-ui, sans-serif; }}
        .article-body h2 {{ font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-top: 2.5rem; margin-bottom: 1rem; }}
        .article-body h3 {{ font-size: 1.4rem; font-weight: 700; color: #f1f5f9; margin-top: 2rem; margin-bottom: 0.8rem; }}
        .article-body p {{ margin-bottom: 1.5rem; font-size: 1.125rem; line-height: 1.8; color: #94a3b8; }}
        .article-body ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1.5rem; color: #94a3b8; }}
        .article-body li {{ margin-bottom: 0.5rem; }}
        .article-body strong {{ color: #e2e8f0; }}
        .article-body a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid #3b82f6; }}
    </style>
</head>
<body class="bg-dark text-slate-300 min-h-screen flex flex-col">
    <nav class="border-b border-white/5 p-6 bg-dark/95 backdrop-blur-xl sticky top-0 z-50">
        <div class="max-w-4xl mx-auto flex items-center">
            <a href="../index.html" class="text-slate-400 hover:text-white transition-colors flex items-center gap-2 font-medium">
                <i data-lucide="arrow-left" class="w-4 h-4"></i> Back to Home
            </a>
        </div>
    </nav>
    <main class="max-w-3xl mx-auto px-6 py-12 w-full flex-grow">
        <div class="mb-12 pb-8 border-b border-slate-800/50">
            <span class="text-primary font-bold text-xs tracking-widest uppercase bg-primary/10 px-3 py-1.5 rounded-full">{data['category']}</span>
            <h1 class="text-4xl md:text-5xl font-extrabold text-white mt-6 mb-6 leading-[1.2]">{data['title']}</h1>
            <div class="text-slate-500 text-sm flex items-center gap-6 font-medium">
                <span class="flex items-center gap-2"><i data-lucide="calendar" class="w-4 h-4 text-slate-600"></i> {date_str}</span>
                <span class="flex items-center gap-2"><i data-lucide="clock" class="w-4 h-4 text-slate-600"></i> {data['read_time']} read</span>
            </div>
        </div>
        
        <div class="mb-12 rounded-2xl overflow-hidden shadow-2xl shadow-black/50 border border-white/5">
            <img src="{random_image}" alt="Article Cover" class="w-full h-auto object-cover opacity-90">
        </div>

        <article class="article-body">
            {data['content']}
        </article>
    </main>
    <footer class="border-t border-white/5 py-8 text-center text-slate-600 text-sm bg-[#010409]">
        &copy; 2024 TechGuide Global. All rights reserved.
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""

    with open(f"articles/{file_name}", "w", encoding='utf-8') as f:
        f.write(article_page_html)
    print(f"📄 独立文章页面已生成: articles/{file_name}")


    # 2. 深度定制 HTML，1:1 复刻你最新的 <a href...> 优美卡片结构
    new_article_html = f"""
                    <!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d')} -->
                    <a href="articles/{file_name}" class="block bg-slate-900/50 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-primary/50 transition-all duration-300 group shadow-lg shadow-black/20 hover:-translate-y-1">
                        <article class="flex flex-col sm:flex-row gap-6">
                            <div class="w-full sm:w-56 h-40 rounded-xl bg-slate-800 flex-shrink-0 relative overflow-hidden shadow-lg">
                                <img src="{random_image}" alt="{data['title']}" loading="lazy" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-in-out">
                                <div class="absolute inset-0 bg-gradient-to-t from-dark/80 via-transparent to-transparent"></div>
                            </div>
                            <div class="flex flex-col justify-center flex-grow py-1">
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-[10px] font-bold text-primary px-2 py-0.5 bg-primary/10 rounded-md uppercase">{data['category']}</span>
                                    <span class="text-[10px] text-emerald-400 font-medium flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>NEW</span>
                                </div>
                                <h3 class="text-xl font-bold text-slate-100 group-hover:text-primary transition-colors leading-tight">{data['title']}</h3>
                                <p class="text-sm text-slate-400 mt-2 line-clamp-2">{data['description']}</p>
                                <div class="mt-4 text-[11px] text-slate-500 font-medium tracking-wide flex items-center gap-4">
                                    <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-3.5 h-3.5"></i> {date_str}</span>
                                    <span class="flex items-center gap-1"><i data-lucide="clock" class="w-3.5 h-3.5"></i> {data['read_time']} READ</span>
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
        print("🚀 完美！新文章已无缝注入网站主页。")
    else:
        print("❌ 错误：在 index.html 中找不到锚点 <!-- AI_ARTICLE_ANCHOR -->！")
        sys.exit(1)
