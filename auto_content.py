import os
import json
import re
from openai import OpenAI
from datetime import datetime

# ==========================================
# TechGuide Global - AI 内容全自动生成脚本
# ==========================================

# 1. 配置 AI API
api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE", "https://api.moonshot.cn/v1") 

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

# 2. 撰写提示词 (全面升级：要求 AI 输出完整的长文)
prompt = """
You are an expert tech blogger and SEO specialist. 
Write a comprehensive, highly engaging tech blog post (at least 400 words) about a trending AI tool or AI money-making strategy.
Output ONLY a valid JSON object with the following structure:
{
  "title": "A catchy, SEO-friendly title",
  "category": "One word: TOOLS, MONEY, or NEWS",
  "description": "Two sentences explaining why this matters.",
  "read_time": "e.g., 4 min",
  "content": "The full article body formatted in valid HTML. Use <h2> for subheadings, <p> for paragraphs, and <ul> for lists. Do NOT include <html> or <body> tags, just the inner content."
}
"""

def clean_json_response(text):
    """移除可能存在的 Markdown 代码块标记"""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

try:
    print(f"[{datetime.now()}] 正在呼叫 Kimi AI 生成内容...")
    
    # 3. 请求 AI
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that outputs ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    
    raw_content = response.choices[0].message.content
    cleaned_content = clean_json_response(raw_content)
    data = json.loads(cleaned_content)
    
    print(f"成功生成文章: {data['title']}")

    # 4. 生成独立的 HTML 文章页面 (核心升级！)
    # 生成安全的文件名 (去掉特殊字符和空格)
    safe_title = "".join([c if c.isalnum() else "-" for c in data['title'].lower()])
    safe_title = re.sub(r'-+', '-', safe_title).strip('-')
    file_name = f"{safe_title}.html"
    
    # 创建 articles 文件夹用来存放文章
    os.makedirs('articles', exist_ok=True)
    
    # 自动生成美观的文章页面代码
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
        body {{ font-family: 'Inter', sans-serif; }}
        /* 针对 AI 生成的 HTML 注入样式 */
        .article-body h2 {{ font-size: 1.8rem; font-weight: bold; color: white; margin-top: 2rem; margin-bottom: 1rem; }}
        .article-body h3 {{ font-size: 1.4rem; font-weight: bold; color: white; margin-top: 1.5rem; margin-bottom: 0.8rem; }}
        .article-body p {{ margin-bottom: 1.2rem; font-size: 1.1rem; line-height: 1.7; }}
        .article-body ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1.2rem; }}
        .article-body strong {{ color: #e2e8f0; }}
        .article-body a {{ color: #3b82f6; text-decoration: underline; }}
    </style>
</head>
<body class="bg-dark text-slate-300 min-h-screen flex flex-col">
    <nav class="border-b border-white/5 p-6 bg-dark/80 backdrop-blur-xl sticky top-0">
        <div class="max-w-4xl mx-auto flex items-center">
            <a href="../index.html" class="text-slate-400 hover:text-white transition-colors flex items-center gap-2 font-medium">
                <i data-lucide="arrow-left" class="w-4 h-4"></i> Back to Home
            </a>
        </div>
    </nav>
    <main class="max-w-4xl mx-auto px-6 py-12 w-full flex-grow">
        <div class="mb-10 pb-10 border-b border-slate-800">
            <span class="text-primary font-bold text-sm tracking-widest uppercase bg-primary/10 px-3 py-1 rounded-full">{data['category']}</span>
            <h1 class="text-4xl md:text-5xl font-extrabold text-white mt-6 mb-6 leading-tight">{data['title']}</h1>
            <div class="text-slate-500 text-sm flex items-center gap-6 font-medium">
                <span class="flex items-center gap-2"><i data-lucide="calendar" class="w-4 h-4"></i> {datetime.now().strftime('%B %d, %Y')}</span>
                <span class="flex items-center gap-2"><i data-lucide="clock" class="w-4 h-4"></i> {data['read_time']} read</span>
            </div>
        </div>
        <article class="article-body text-slate-300">
            {data['content']}
        </article>
    </main>
    <footer class="border-t border-white/5 py-8 text-center text-slate-600 text-sm bg-slate-950">
        &copy; 2024 TechGuide Global. All rights reserved.
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""

    # 将文章写入单独的文件
    with open(f"articles/{file_name}", "w", encoding='utf-8') as f:
        f.write(article_page_html)
    print(f"独立文章页面已生成: articles/{file_name}")

    # 5. 构建插入主页的 HTML 卡片 (修复超链接指向真实的独立文章)
    new_article_html = f"""
                    <!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d')} -->
                    <a href="articles/{file_name}" class="block bg-slate-900/50 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-slate-600 transition-all duration-300 group">
                        <article class="flex flex-col sm:flex-row gap-6">
                            <div class="w-full sm:w-56 h-40 rounded-xl bg-gradient-to-br from-blue-600 to-purple-700 flex-shrink-0 flex items-center justify-center shadow-lg">
                                <i data-lucide="zap" class="w-10 h-10 text-white/40"></i>
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

    # 6. 读取 index.html 并寻找锚点插入内容
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    
    if anchor in html_content:
        updated_html = html_content.replace(anchor, f"{anchor}\n{new_article_html}")
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print("写入成功！")
    else:
        print("错误：在 index.html 中找不到锚点标记。")

except Exception as e:
    print(f"运行失败: {str(e)}")
