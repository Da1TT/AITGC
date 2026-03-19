import os
import json
import re
import sys
import time
import urllib.parse
from openai import OpenAI
from datetime import datetime

# ==========================================
# TechGuide - Ultimate Automation Engine v2
# Improvements:
# - More human-like writing, minimal AI traces
# - Stable image hosting (Unsplash + fallback)
# - Longer, more comprehensive articles
# - Better structure for SEO
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

# Expanded topic list for continuous generation
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
    "How to start and scale an AI Automation Agency (AIAA)",
    "Best free AI image generators compared in 2024",
    "How to use AI to write blog posts faster without losing quality",
    "Building an email list with AI content automation",
    "AI keyword research tools that actually save time",
    "How to create and sell AI prompts online for profit",
    "Top AI Chrome extensions every developer should use",
    "Using AI for competitive analysis in digital marketing",
    "How to price AI automation services for clients",
    "AI content detection tools and how they work",
    "Passive income with AI: real examples that work today",
    "SEO mistakes AI tools can automatically fix for you",
    "How to train custom AI models for your business",
    "AI web design tools that generate complete websites",
    "Using AI to find low-competition keywords for blogs",
    "How to start a AI newsletter and monetize it",
    "Best AI tools for content rewriting and paraphrasing",
    "Legal issues to consider when using AI for content",
    "How to outsource content creation with AI effectively",
    "AI vs human writers: when to use which in 2024",
    "Case study: how I grew a blog to 10k visits with AI content"
]

def clean_json_response(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

MAX_RETRIES = 3
MAX_ARTICLES_ON_HOMEPAGE = 30  # Keep homepage fast loading, only show latest 30 articles
all_new_cards_html = ""

for index, topic in enumerate(niche_topics[:10]):  # Still generate 10 per run
    print(f"\n🚀 Generating Article {index + 1}/10: [{topic}]")

    prompt = f"""
You are a veteran tech blogger with 10+ years of experience. Write a comprehensive, in-depth blog post STRICTLY about: "{topic}".

=== WRITING RULES - FOLLOW THESE EXACTLY TO AVOID AI DETECTION ===
1. WORD COUNT: Minimum 800 words, target 1000-1200 words. Longer = better for SEO.
2. TONE: Conversational, personal, opinionated. Use "I" and "you" frequently. Share personal experiences and anecdotes.
3. VARIETY: Mix short sentences (3-5 words) with long ones. Vary paragraph length (1-5 sentences). This creates "burstiness" that avoids AI detection.
4. FORBIDDEN AI CLICHES: Never use any of these:
   - "In today's fast-paced digital world"
   - "Unlock the power of"
   - "Revolutionize your"
   - "Game-changer"
   - "Delve into"
   - "Landscape"
   - "In this article"
   - "Stay tuned"
   - "Without further ado"
   - "Hope you enjoy"
5. STRUCTURE:
   - Start with a hook: share a quick personal observation or story
   - Break into at least 4-6 subheadings with <h2> tags
   - Include at least one bullet-point list
   - End with a conclusion that gives a clear takeaway or recommendation
   - Add specific examples, tool names, and approximate numbers
6. ORIGINALITY: Write unique content that hasn't been written the same way a thousand times before. Add your unique "voice".

=== OUTPUT FORMAT ===
Output ONLY a valid JSON object with NO extra text before or after. Use this exact structure:
{{
  "title": "A highly clickable, human-sounding title (6-10 words, avoid colons if possible)",
  "category": "One word: TOOLS, STRATEGY, or MONEY",
  "description": "Two punchy sentences that hook readers to click, explain the value clearly",
  "read_time": "estimated read time in minutes, e.g., 8 min",
  "image_keywords": "1-3 keywords for this article topic, separated by commas (for unsplash image search)",
  "content": "The full article body in valid HTML. Use <h2> for main subheadings, <h3> if needed, <p> for paragraphs, <ul>/<li> for lists. Do NOT include <html> or <body> tags."
}}
"""

    data = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "You are an experienced tech blogger writing for humans. Output ONLY valid JSON with no extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                timeout=120.0
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

        # Use Picsum Photos for stable image hosting - reliable CDN that works globally
        # Fallback to a solid colored background if no image
        image_keywords = data.get('image_keywords', topic.split(',')[0])
        # Get random image from Picsum based on seed = hash(image_keywords)
        seed = sum(ord(c) for c in image_keywords) % 1000
        random_image = f"https://picsum.photos/seed/{seed}/800/500"


        # If still fails, CSS gradient background will show
        safe_title = "".join([c if c.isalnum() or c in '-_' else "-" for c in data['title'].lower()])
        safe_title = re.sub(r'-+', '-', safe_title).strip('-')
        file_name = f"{safe_title}.html"

        os.makedirs('articles', exist_ok=True)

        article_page_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} - TechGuide China</title>
    <meta name="description" content="{data['description']}">
    <!-- OpenGraph tags for social sharing -->
    <meta property="og:title" content="{data['title']} - TechGuide China">
    <meta property="og:description" content="{data['description']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://techguidechina.com/articles/{file_name}">
    <meta property="og:image" content="{random_image}">
    <meta name="twitter:card" content="summary_large_image">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ dark: '#020617', primary: '#3b82f6' }} }} }} }}
    </script>
    <style>
        body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
        .article-body h2 {{ font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-top: 2.5rem; margin-bottom: 1rem; }}
        .article-body h3 {{ font-size: 1.4rem; font-weight: 700; color: #f1f5f9; margin-top: 2rem; margin-bottom: 0.8rem; }}
        .article-body p {{ margin-bottom: 1.5rem; font-size: 1.125rem; line-height: 1.8; color: #94a3b8; }}
        .article-body ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1.5rem; color: #94a3b8; }}
        .article-body li {{ margin-bottom: 0.75rem; line-height: 1.7; }}
        .article-body strong {{ color: #e2e8f0; }}
        .article-body a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid #3b82f6; }}
        .article-image-fallback {{ background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); }}
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

        <div class="mb-12 rounded-2xl overflow-hidden shadow-2xl shadow-black/50 border border-white/5 article-image-fallback">
            <img src="{random_image}" alt="{data['title']}" class="w-full h-auto object-cover opacity-90" onerror="this.style.display='none'">
        </div>

        <article class="article-body">
            {data['content']}
        </article>
    </main>
    <footer class="border-t border-white/5 py-12 px-6 bg-[#010409]">
        <div class="max-w-3xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="font-bold text-white text-sm">TechGuide China</span>
                    </div>
                    <p class="text-slate-500 text-xs">
                        Your complete directory of AI tools and practical guides for digital entrepreneurs.
                    </p>
                </div>
                <div class="flex items-center gap-6">
                    <a href="/" class="text-slate-400 hover:text-white transition-colors text-sm">Home</a>
                    <a href="/about" class="text-slate-400 hover:text-white transition-colors text-sm">About</a>
                    <a href="/privacy" class="text-slate-400 hover:text-white transition-colors text-sm">Privacy</a>
                    <a href="/terms" class="text-slate-400 hover:text-white transition-colors text-sm">Terms</a>
                </div>
            </div>
            <div class="mt-8 pt-8 border-t border-white/5 text-center text-slate-600 text-xs">
                © 2024 TechGuide China. All rights reserved.
            </div>
        </div>
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""

        with open(f"articles/{file_name}", "w", encoding='utf-8') as f:
            f.write(article_page_html)

        new_article_html = f"""
<!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->
<a href="articles/{file_name}" class="article-card block bg-slate-900/50 hover:bg-slate-800/80 p-6 rounded-2xl border border-slate-800 hover:border-primary/50 transition-all duration-300 group shadow-xl shadow-black/25 hover:-translate-y-2">
    <article class="flex flex-col sm:flex-row gap-6">
        <div class="w-full sm:w-56 h-40 rounded-xl bg-slate-800 flex-shrink-0 relative overflow-hidden shadow-xl article-image-fallback">
            <img src="{random_image}" alt="{data['title']}" loading="lazy" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-in-out" onerror="this.style.display='none'">
            <div class="absolute inset-0 bg-gradient-to-t from-dark/80 via-transparent to-transparent"></div>
        </div>
        <div class="flex flex-col justify-center flex-grow py-1">
            <div class="flex items-center gap-2 mb-3">
                <span class="text-[10px] font-bold text-primary px-2 py-0.5 bg-primary/10 rounded-md uppercase">{data['category']}</span>
                <span class="text-[10px] text-emerald-400 font-medium flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>NEW</span>
            </div>
            <h3 class="text-xl font-bold text-slate-100 group-hover:text-primary transition-colors leading-tight">{data['title']}</h3>
            <p class="text-sm text-slate-400 mt-3 line-clamp-2">{data['description']}</p>
            <div class="mt-5 text-[11px] text-slate-500 font-medium tracking-wide flex items-center gap-4">
                <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-3.5 h-3.5"></i> {date_str}</span>
                <span class="flex items-center gap-1"><i data-lucide="clock" class="w-3.5 h-3.5"></i> {data['read_time']} READ</span>
            </div>
        </div>
    </article>
</a>"""

        all_new_cards_html += new_article_html + "\n"
        print("⏳ Sleeping 10 seconds to prevent API Rate Limits...\n")
        time.sleep(10)

if all_new_cards_html:
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract existing article cards after anchor to keep homepage trimmed
    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    if anchor not in html_content:
        print("\n❌ FATAL: Anchor <!-- AI_ARTICLE_ANCHOR --> not found in index.html!")
        sys.exit(1)
    
    # Split into before anchor and after anchor
    parts = html_content.split(anchor, 1)
    before_anchor = parts[0] + anchor + "\n"
    
    # Get all existing article cards after anchor
    existing_cards = parts[1]
    
    # Count how many existing articles we have, keep only the latest MAX_ARTICLES_ON_HOMEPAGE
    # Split by article-card boundary - each card ends with </a>
    card_pattern = '</a>\n'
    all_existing_cards = [card + '</a>\n' for card in existing_cards.split(card_pattern) if card.strip()]
    
    # Combine new cards + existing cards, then truncate to keep only latest MAX_ARTICLES_ON_HOMEPAGE
    # Newest articles go first (already the case - new ones are added to top)
    combined_cards = all_new_cards_html + ''.join(all_existing_cards)
    all_combined_cards = [card + '</a>\n' for card in combined_cards.split(card_pattern) if card.strip()]
    
    # Trim to max articles
    if len(all_combined_cards) > MAX_ARTICLES_ON_HOMEPAGE:
        trimmed_cards = all_combined_cards[:MAX_ARTICLES_ON_HOMEPAGE]
        print(f"\n✂️  Trimmed homepage from {len(all_combined_cards)} to {len(trimmed_cards)} articles (max {MAX_ARTICLES_ON_HOMEPAGE}) for faster loading")
    else:
        trimmed_cards = all_combined_cards
    
    final_html = before_anchor + ''.join(trimmed_cards)
    if len(parts) > 2:
        # In case there's content after the cards
        final_html += parts[2]
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"\n🎉 ALL 10 ARTICLES INJECTED SUCCESSFULLY. Homepage kept at {len(trimmed_cards)} articles maximum.")
else:
    sys.exit(1)


# ==========================================
# Auto-generate sitemap.xml with all articles
# ==========================================
def generate_sitemap(base_url="https://techguidechina.com"):
    """Generate sitemap.xml including all articles, about, privacy, terms pages."""
    sitemap_template = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""
    
    url_entries = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Add homepage
    url_entries.append(f"""  <url>
    <loc>{base_url}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.00</priority>
  </url>""")
    
    # Add static pages
    static_pages = [
        ("about", "monthly", 0.8),
        ("privacy", "monthly", 0.8), 
        ("terms", "monthly", 0.8),
    ]
    
    for page, changefreq, priority in static_pages:
        url_entries.append(f"""  <url>
    <loc>{base_url}/{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority:.2f}</priority>
  </url>""")
    
    # Add all articles from articles directory
    articles_dir = 'articles'
    if os.path.exists(articles_dir):
        article_files = [f for f in os.listdir(articles_dir) if f.endswith('.html')]
        print(f"\n🗺️  Generating sitemap with {len(article_files)} articles...")
        
        for article_file in article_files:
            # Get file modification time
            file_path = os.path.join(articles_dir, article_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            lastmod = mtime.strftime('%Y-%m-%d')
            
            url = f"{base_url}/articles/{article_file}"
            url_entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.60</priority>
  </url>""")
    
    urls_str = "\n".join(url_entries)
    sitemap_content = sitemap_template.format(urls=urls_str)
    
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    
    print(f"✅ sitemap.xml generated: {len(url_entries)} total URLs")

# Generate sitemap after all articles are created
generate_sitemap()
