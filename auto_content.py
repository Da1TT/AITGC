import os
import sys
import json
import re
import time
import random
from openai import OpenAI
from datetime import datetime

# ==========================================
# TechGuide Global 3.0 - 批量深度文章生成器 (带配图版)
# ==========================================

api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE")

if not api_base or api_base.strip() == "":
    api_base = "https://api.moonshot.cn/v1"

if not api_key:
    print("❌ 错误：找不到 AI_API_KEY。")
    sys.exit(1)

client = OpenAI(api_key=api_key, base_url=api_base)

# 话题池
topics_pool = [
    "How to make passive income with AI art and Midjourney",
    "Best AI tools for automated YouTube Shorts creation",
    "ChatGPT prompt engineering for high-converting copywriting",
    "Starting an AI Automation Agency (AIAA) for beginners",
    "Top AI tools for SEO and ranking on Google fast",
    "How to use AI to write code even if you are not a programmer",
    "The ultimate guide to AI voice cloning and monetization",
    "Building no-code apps using AI website builders",
    "How to use Claude 3 for data analysis and finance",
    "Automating social media management with AI agents"
]
random.shuffle(topics_pool)

def clean_json_response(text):
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    return text.strip()

with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

anchor = "<!-- AI_ARTICLE_ANCHOR -->"
if anchor not in html_content:
    print("❌ 错误：找不到 <!-- AI_ARTICLE_ANCHOR -->")
    sys.exit(1)

articles_dir = "articles"
os.makedirs(articles_dir, exist_ok=True)

success_count = 0

for i in range(10):
    current_topic = topics_pool[i]
    print(f"\n[{datetime.now()}] 🚀 正在生成第 {i+1}/10 篇文章: {current_topic}")
    
    prompt = f"""
    You are a top-tier tech blogger for TechGuide Global. 
    Generate a comprehensive, engaging article specifically about: {current_topic}.
    The tone should be professional, actionable, and exciting.
    You MUST output ONLY a valid JSON object with the following structure:
    {{
      "title": "A catchy, SEO-friendly title",
      "slug": "a-url-friendly-version-of-the-title-with-hyphens",
      "category": "TOOLS or MONEY or NEWS",
      "description": "Two sentences summarizing the article.",
      "read_time": "e.g., 5 min",
      "content": "The full article body in HTML format. Use <h2>, <p>, <ul>, <li>, <strong> tags for styling. DO NOT use double quotes inside HTML attributes. Make it at least 5 paragraphs."
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "You are an API that only returns valid JSON objects."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7 
        )
        
        raw_content = response.choices[0].message.content
        cleaned_content = clean_json_response(raw_content)
        data = json.loads(cleaned_content)
        
        title = data['title']
        slug = data['slug'].lower().replace(' ', '-')
        article_filename = f"{articles_dir}/{slug}.html"
        
        # 智能配图 URL (基于 slug 生成唯一的随机图片)
        cover_image_url = f"https://picsum.photos/seed/{slug}/1200/600"
        thumbnail_url = f"https://picsum.photos/seed/{slug}/600/400"
        
        # 1. 构建独立的 HTML 文章页面 (顶部加入了宽幅超大配图)
        full_article_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - TechGuide Global</title>
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ dark: '#020617', primary: '#3b82f6' }} }} }} }}
    </script>
    <style>body {{ font-family: system-ui, -apple-system, sans-serif; }}</style>
</head>
<body class="bg-dark text-slate-300 min-h-screen flex flex-col">
    <nav class="sticky top-0 z-50 bg-dark/90 backdrop-blur-md border-b border-slate-800">
        <div class="max-w-4xl mx-auto px-4 h-16 flex items-center">
            <a href="../index.html" class="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
                <i data-lucide="arrow-left" class="w-5 h-5"></i> Back to Home
            </a>
        </div>
    </nav>
    <main class="max-w-3xl mx-auto px-4 py-12 w-full flex-grow">
        <div class="mb-8">
            <span class="text-xs font-bold text-primary px-3 py-1 bg-primary/10 rounded-full uppercase tracking-wider">{data['category']}</span>
            <h1 class="text-4xl md:text-5xl font-extrabold text-white mt-6 mb-4 leading-tight">{title}</h1>
            <div class="flex items-center gap-4 text-sm text-slate-500 mb-8">
                <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-4 h-4"></i> {datetime.now().strftime('%B %d, %Y')}</span>
                <span class="flex items-center gap-1"><i data-lucide="clock" class="w-4 h-4"></i> {data['read_time']} read</span>
            </div>
            
            <!-- 插入文章头图 -->
            <img src="{cover_image_url}" alt="{title}" class="w-full h-[300px] md:h-[400px] object-cover rounded-3xl mb-10 shadow-2xl shadow-black/50">
        </div>
        
        <div class="w-full h-24 bg-slate-800/30 border border-slate-700/50 rounded-xl flex items-center justify-center text-slate-500 mb-10">
            AdSense Content Banner
        </div>
        <article class="prose prose-invert prose-lg prose-blue max-w-none prose-headings:text-white prose-a:text-primary hover:prose-a:text-blue-400">
            {data['content']}
        </article>
    </main>
    <footer class="py-8 border-t border-slate-800 text-center text-sm text-slate-500">
        &copy; 2024 TechGuide Global. All rights reserved.
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""

        with open(article_filename, 'w', encoding='utf-8') as f:
            f.write(full_article_html)
            
        # 2. 构建主页的文章卡片 (带有缩略图)
        new_card_html = f"""
                    <!-- AI Generated Article -->
                    <a href="{article_filename}" class="block bg-slate-900/50 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-primary/50 transition-all duration-300 group shadow-lg shadow-black/20 hover:-translate-y-1">
                        <article class="flex flex-col sm:flex-row gap-6">
                            <!-- 带有图片的缩略图区域 -->
                            <div class="w-full sm:w-56 h-40 rounded-xl bg-slate-800 flex-shrink-0 relative overflow-hidden shadow-lg">
                                <img src="{thumbnail_url}" alt="{title}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-in-out">
                                <div class="absolute inset-0 bg-gradient-to-t from-dark/80 via-transparent to-transparent"></div>
                            </div>
                            
                            <div class="flex flex-col justify-center flex-grow py-1">
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-[10px] font-bold text-primary px-2 py-0.5 bg-primary/10 rounded-md uppercase">{data['category']}</span>
                                    <span class="text-[10px] text-emerald-400 font-medium flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>NEW</span>
                                </div>
                                <h3 class="text-xl font-bold text-slate-100 group-hover:text-primary transition-colors leading-tight">{title}</h3>
                                <p class="text-sm text-slate-400 mt-2 line-clamp-2">{data['description']}</p>
                                <div class="mt-4 text-[11px] text-slate-500 font-medium tracking-wide flex items-center gap-4">
                                    <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-3.5 h-3.5"></i> {datetime.now().strftime('%b %d')}</span>
                                    <span class="flex items-center gap-1"><i data-lucide="clock" class="w-3.5 h-3.5"></i> {data['read_time']} READ</span>
                                </div>
                            </div>
                        </article>
                    </a>"""
        
        html_content = html_content.replace(anchor, f"{anchor}\n{new_card_html}")
        print(f"✅ 第 {i+1} 篇生成成功: {title}")
        success_count += 1
        
        if i < 9:
            print("⏳ 等待 5 秒以防 API 频率受限...")
            time.sleep(5)

    except Exception as e:
        print(f"❌ 第 {i+1} 篇生成失败，跳过: {str(e)}")
        continue

if success_count > 0:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n🎉 批量任务完成！成功生成并插入 {success_count} 篇文章。")
else:
    print("\n❌ 批量生成全部失败。")
    sys.exit(1)
