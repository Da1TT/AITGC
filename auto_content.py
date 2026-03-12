import os
import sys
import json
import re
from openai import OpenAI
from datetime import datetime

# ==========================================
# TechGuide Global 2.0 - 独立文章页面生成器
# ==========================================

api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE", "https://api.moonshot.cn/v1") 

if not api_key:
    print("❌ 错误：找不到 AI_API_KEY。")
    sys.exit(1)

client = OpenAI(api_key=api_key, base_url=api_base)

# 告诉 AI 不仅要写摘要，还要写一篇完整的 HTML 文章
prompt = """
You are a top-tier tech blogger for TechGuide Global. 
Generate a comprehensive, engaging article about a trending AI tool or an AI money-making strategy.
The tone should be professional, actionable, and exciting.
You MUST output ONLY a valid JSON object with the following structure:
{
  "title": "A catchy, SEO-friendly title",
  "slug": "a-url-friendly-version-of-the-title-with-hyphens",
  "category": "TOOLS or MONEY or NEWS",
  "description": "Two sentences summarizing the article.",
  "read_time": "e.g., 4 min",
  "content": "The full article body in HTML format. Use <h2>, <p>, <ul>, <li>, <strong> tags for styling. DO NOT use double quotes inside HTML attributes (use single quotes). Make it at least 4 paragraphs."
}
"""

def clean_json_response(text):
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    return text.strip()

try:
    print(f"[{datetime.now()}] 正在呼叫 Kimi AI 创作深度长文...")
    
    # 降低 temperature 让 JSON 格式更稳定
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "You are an API that only returns valid JSON objects."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6 
    )
    
    raw_content = response.choices[0].message.content
    cleaned_content = clean_json_response(raw_content)
    data = json.loads(cleaned_content)
    
    title = data['title']
    slug = data['slug'].lower().replace(' ', '-')
    
    print(f"✅ 成功生成文章大纲: {title}")

    # ==========================================
    # 1. 生成独立的 HTML 文章页面
    # ==========================================
    articles_dir = "articles"
    os.makedirs(articles_dir, exist_ok=True) # 确保存在 articles 文件夹
    
    article_filename = f"{articles_dir}/{slug}.html"
    
    # 文章页面的 HTML 模板 (包含正文排版插件)
    full_article_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - TechGuide</title>
    <!-- 引入 Tailwind 和 文本排版插件(typography) 让文章自动变得漂亮 -->
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ dark: '#0f172a', primary: '#3b82f6' }} }} }} }}
    </script>
    <style>body {{ font-family: system-ui, -apple-system, sans-serif; }}</style>
</head>
<body class="bg-dark text-slate-300 min-h-screen flex flex-col">
    <!-- 简易导航 -->
    <nav class="sticky top-0 z-50 bg-dark/90 backdrop-blur-md border-b border-slate-800">
        <div class="max-w-4xl mx-auto px-4 h-16 flex items-center">
            <a href="../index.html" class="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
                <i data-lucide="arrow-left" class="w-5 h-5"></i> Back to Home
            </a>
        </div>
    </nav>

    <!-- 文章正文区域 -->
    <main class="max-w-3xl mx-auto px-4 py-12 w-full flex-grow">
        <div class="mb-8">
            <span class="text-xs font-bold text-primary px-3 py-1 bg-primary/10 rounded-full uppercase tracking-wider">{data['category']}</span>
            <h1 class="text-4xl md:text-5xl font-extrabold text-white mt-6 mb-4 leading-tight">{title}</h1>
            <div class="flex items-center gap-4 text-sm text-slate-500">
                <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-4 h-4"></i> {datetime.now().strftime('%B %d, %Y')}</span>
                <span class="flex items-center gap-1"><i data-lucide="clock" class="w-4 h-4"></i> {data['read_time']} read</span>
            </div>
        </div>

        <!-- 广告占位 -->
        <div class="w-full h-24 bg-slate-800/50 rounded-xl border border-slate-700 flex items-center justify-center text-slate-500 mb-10">
            AdSense Content Banner
        </div>

        <!-- 文章主体 (使用 prose 类自动排版) -->
        <article class="prose prose-invert prose-lg prose-blue max-w-none prose-headings:text-white prose-a:text-primary hover:prose-a:text-blue-400">
            {data['content']}
        </article>
    </main>

    <footer class="py-8 border-t border-slate-800 text-center text-sm text-slate-500">
        &copy; 2024 TechGuide Global.
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""

    # 将文章保存为独立网页
    with open(article_filename, 'w', encoding='utf-8') as f:
        f.write(full_article_html)
    print(f"📝 独立文章页面创建成功: {article_filename}")


    # ==========================================
    # 2. 更新主页 index.html (插入可点击的链接卡片)
    # ==========================================
    new_card_html = f"""
                    <!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d')} -->
                    <a href="{article_filename}" class="block hover-card bg-card p-5 rounded-2xl border border-slate-800 group">
                        <article class="flex flex-col sm:flex-row gap-5">
                            <div class="w-full sm:w-48 h-32 rounded-xl bg-gradient-to-br from-blue-600 to-purple-700 flex-shrink-0 flex items-center justify-center relative overflow-hidden">
                                <i data-lucide="sparkles" class="w-10 h-10 text-white/50 group-hover:scale-125 transition-transform duration-500"></i>
                            </div>
                            <div class="flex flex-col justify-center flex-grow">
                                <div class="flex items-center gap-2 mb-1">
                                    <span class="text-[10px] font-bold text-primary px-2 py-0.5 bg-primary/10 rounded-full">{data['category']}</span>
                                    <span class="text-[10px] text-green-400 font-medium">● NEW</span>
                                </div>
                                <h3 class="text-lg font-bold text-white group-hover:text-primary transition-colors">{title}</h3>
                                <p class="text-sm text-slate-400 mt-2 line-clamp-2">{data['description']}</p>
                                <div class="mt-3 text-[10px] text-slate-500 uppercase tracking-widest flex items-center gap-1">
                                    <i data-lucide="book-open" class="w-3 h-3"></i> {data['read_time']} READ
                                </div>
                            </div>
                        </article>
                    </a>"""

    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    
    if anchor in html_content:
        updated_html = html_content.replace(anchor, f"{anchor}\n{new_card_html}")
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print("🎉 主页更新成功！")
    else:
        print("❌ 错误：找不到 <!-- AI_ARTICLE_ANCHOR -->")
        sys.exit(1)

except Exception as e:
    print(f"❌ 运行失败: {str(e)}")
    sys.exit(1)
