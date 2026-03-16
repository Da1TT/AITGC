import os
import json
import re
import sys
import time
import urllib.parse
from openai import OpenAI
from datetime import datetime

# ==========================================
# TechGuide - Ultimate Automation Engine
# Generating 10 articles, Anti-AI Cliches, Dynamic Unique Images
# ==========================================

api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE")

# Fix GitHub Actions empty string bug
if not api_base or api_base.strip() == "":
    api_base = "https://api.moonshot.cn/v1"

if not api_key:
    print("❌ FATAL: AI_API_KEY not found in GitHub Secrets!")
    sys.exit(1)

print(f"🔍 [Diagnostic] Using API Base: {api_base}")

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

niche_topics = [
    "AI tools for SEO automation and rapid Google ranking",
    "Monetizing AI art and Midjourney for passive income",
    "Advanced ChatGPT prompt engineering for high-converting copywriting",
    "AI video creation tools for automated YouTube Shorts",
    "No-code AI app building and SaaS development for beginners",
    "Harnessing AI for social media management and viral growth",
    "AI voice cloning tools and audio monetization strategies",
    "Top AI productivity hacks for digital entrepreneurs",
    "Using AI models like Claude 3 for data analysis and finance",
    "How to start and scale an AI Automation Agency (AIAA)"
]

def clean_json_response(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

MAX_RETRIES = 3
all_cards_html = ""

for index, topic in enumerate(niche_topics):
    print(f"\n🚀 Generating Article {index + 1}/10: [{topic}]")

    prompt = f"""
You are a veteran tech blogger and software reviewer. Your writing style is highly conversational, opinionated, and engaging.
Write a comprehensive tech blog post (at least 450 words) strictly about: "{topic}".

CRITICAL HUMAN-WRITING RULES:
1. NEVER use AI cliches like "In today's fast-paced digital world", "Unlock the power", "Revolutionize", "Game-changer", "Delve into", or "Landscape".
2. Use varied sentence lengths (burstiness). Write like a real human speaking directly to the reader, using "I" and "you".
3. Include specific examples, hypothetical numbers, or practical steps to make it grounded.

Output ONLY a valid JSON object with the following structure:
{{
  "title": "A highly clickable, human-sounding title (avoid colons if possible)",
  "category": "One word: TOOLS, STRATEGY, or MONEY",
  "description": "Two sentences explaining the value of the guide, written in a punchy hook style.",
  "read_time": "e.g., 5 min",
  "image_prompt": "A highly detailed prompt for an AI image generator describing a realistic, high-tech cover photo for this article (e.g., 'A sleek futuristic glowing microchip on a dark modern wood desk, cinematic lighting, photorealistic')",
  "content": "The full article body formatted in valid HTML. Use <h2> for subheadings, <p> for paragraphs, and <ul> for lists. Do NOT include <html> or <body> tags, just the inner content."
}}
"""

    data = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                timeout=60.0
            )

            raw_content = response.choices[0].message.content
            cleaned_content = clean_json_response(raw_content)
            data = json.loads(cleaned_content)
            print(f"✅ Success: {data['title']}")
            break

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                print(f"❌ Skipping article {index + 1} due to network failure.")
            time.sleep(5)

    if data:
        date_str = datetime.now().strftime('%b %d')

        # Real-time unique image generation
        image_desc = data.get('image_prompt', 'high tech futuristic abstract background')
        encoded_image_prompt = urllib.parse.quote(image_desc)
        random_image = f"https://image.pollinations.ai/prompt/{encoded_image_prompt}?width=800&height=500&nologo=true"

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
        © 2024 TechGuide Global. All rights reserved.
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""

        with open(f"articles/{file_name}", "w", encoding='utf-8') as f:
            f.write(article_page_html)

        new_article_html = f"""
<!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->
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

        all_cards_html += new_article_html + "\n"
        print("⏳ Sleeping 8 seconds to prevent API Rate Limits...\n")
        time.sleep(8)

if all_cards_html:
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    if anchor in html_content:
        updated_html = html_content.replace(anchor, f"{anchor}\n{all_cards_html}")
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print("\n🎉 ALL 10 ARTICLES INJECTED SUCCESSFULLY.")
    else:
        print("\n❌ FATAL: Anchor <!-- AI_ARTICLE_ANCHOR --> not found in index.html!")
        sys.exit(1)
else:
    sys.exit(1)
