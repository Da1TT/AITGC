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

def generate_new_topics(client, count=6):
    """Use AI to generate fresh trending topics for blog articles.
    This ensures we never run out of topics and can adapt to current trends.
    """
    print(f"🤖 Generating {count} fresh trending topics using AI...")
    
    prompt = f"""Generate {count} trending, useful blog post topics about AI tools, AI business, AI monetization, and practical AI guides for digital entrepreneurs.

Rules for good topics:
1. Topics should be specific, actionable, and answer real questions people have
2. Mix between: AI Tools, AI Business/Monetization, AI Strategies
3. Include some topics related to current AI trends and new opportunities
4. Each topic should be 5-15 words, clear and specific
5. Avoid overly broad topics like "AI is changing everything"
6. Focus on topics people actually search for and want to read about

Output ONLY a valid JSON array of strings, no extra text. Example:
["AI tools for SEO automation", "Monetizing AI art with Midjourney", ...]
"""
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "You are an expert content strategist for a tech blog. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                timeout=60.0
            )
            raw_content = response.choices[0].message.content
            cleaned_content = clean_json_response(raw_content)
            topics = json.loads(cleaned_content)
            print(f"✅ Generated {len(topics)} fresh topics:")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
            return topics
        except Exception as e:
            print(f"⚠️ Topic generation attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    
    # If AI generation fails, fall back to backup topics
    print("❌ All topic generation attempts failed, using backup topics")
    backup_topics = [
        "AI tools for SEO automation",
        "Monetizing AI art for passive income",
        "ChatGPT prompt engineering for copywriting",
        "AI video tools for YouTube Shorts",
        "No-code AI app building for beginners",
        "AI for social media growth"
    ]
    return backup_topics[:count]

def clean_json_response(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    # Remove any text before the first { and after the last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    # Fix trailing commas before closing brackets
    text = re.sub(r',\s*([}\]])', r'\1', text)
    # Fix unescaped double quotes inside string content
    # This handles the common case where AI outputs HTML without escaping quotes in JSON
    text = fix_unescaped_quotes(text)
    return text

def fix_unescaped_quotes(text):
    """Fix common JSON issue: unescaped double quotes inside strings."""
    # Strategy: find string openings and closings, escape quotes that are inside
    result = []
    in_string = False
    i = 0
    n = len(text)
    while i < n:
        char = text[i]
        if char == '"' and (i == 0 or text[i-1] != '\\'):
            if in_string:
                # End of string
                in_string = False
            else:
                # Start of string
                in_string = True
            result.append(char)
        elif char == '"' and in_string and i > 0 and text[i-1] != '\\':
            # Unescaped quote inside string - escape it
            result.append('\\"')
        else:
            result.append(char)
        i += 1
    return ''.join(result)

MAX_RETRIES = 3
DAILY_GENERATE_COUNT = 2  # Generate 2 high-quality articles per day (was 6) - quality over quantity for AdSense
MAX_ARTICLES_ON_HOMEPAGE = 30  # Keep homepage fast loading, only show latest 30 articles
all_new_cards_html = ""

# Get list of existing articles to avoid regenerating the same topic
def topic_already_generated(topic, articles_dir='articles'):
    """Check if topic has already been generated (by comparing safe filenames)"""
    safe_title = "".join([c if c.isalnum() or c in '-_' else "-" for c in topic.lower()])
    safe_title = re.sub(r'-+', '-', safe_title).strip('-')
    # Check for any file starting with this (variations in title are okay)
    if not os.path.exists(articles_dir):
        return False
    for filename in os.listdir(articles_dir):
        if filename.endswith('.html') and filename.startswith(safe_title[:20]):
            return True
    return False

# Generate fresh trending topics using AI (never runs out!)
generate_topics = generate_new_topics(client, count=DAILY_GENERATE_COUNT * 3)

# Filter out any that already exist (just to be safe)
generate_topics = [t for t in generate_topics if not topic_already_generated(t)]
if len(generate_topics) == 0:
    print("⚠️ All generated topics already exist, trying backup topics...")
    backup_topics = [
        "AI tools for SEO automation",
        "Monetizing AI art for passive income",
        "ChatGPT prompt engineering for copywriting",
        "AI video tools for YouTube Shorts",
        "No-code AI app building for beginners",
        "AI for social media growth"
    ]
    generate_topics = [t for t in backup_topics if not topic_already_generated(t)][:DAILY_GENERATE_COUNT]
    if len(generate_topics) == 0:
        print("❌ All backup topics also exist, exiting")
        sys.exit(1)
    print(f"✅ Using {len(generate_topics)} backup topics")

print(f"🎯 Generating {len(generate_topics)} articles today")

for index, topic in enumerate(generate_topics):
    print(f"\n🚀 Generating Article {index + 1}/{len(generate_topics)}: [{topic}]")

    prompt = f"""
You are a veteran tech blogger with 10+ years of experience. Write a comprehensive, in-depth blog post STRICTLY about: "{topic}".

=== WRITING RULES - FOLLOW THESE EXACTLY TO MEET GOOGLE ADSENSE STANDARDS ===
1. WORD COUNT: Minimum 1500 words, target 1800-2500 words. Longer, comprehensive content ranks better and meets AdSense requirements.
2. DEPTH & VALUE: 
   - Cover the topic comprehensively, don't just scratch the surface
   - Include actionable steps readers can actually follow
   - Add specific examples, tool recommendations, and practical tips
   - Share common mistakes to avoid
   - Include pro tips from real-world experience
3. TONE: Conversational, personal, opinionated. Use "I" and "you" frequently. Share personal experiences and anecdotes.
4. VARIETY: Mix short sentences (3-5 words) with long ones. Vary paragraph length (1-5 sentences). This creates "burstiness" that avoids AI detection.
5. FORBIDDEN AI CLICHES: Never use any of these:
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
6. STRUCTURE:
   - Start with a hook: share a quick personal observation or story
   - Break into at least 6-8 subheadings with <h2> tags
   - Include at least two bullet-point or numbered lists
   - Add a section about common mistakes or challenges
   - Include a step-by-step guide or actionable framework
   - End with a conclusion that gives a clear takeaway or recommendation
   - Add specific examples, tool names, pricing estimates, and results you can expect
7. ORIGINALITY: Write unique content that hasn't been written the same way a thousand times before. Add your unique "voice" and perspective.

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
            try:
                data = json.loads(cleaned_content)
                print(f"✅ Success: {data['title']}")
                break
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse attempt {attempt + 1} failed: {e}")
                # Try one more aggressive cleaning - extract content manually if possible
                import traceback
                traceback.print_exc()
                if attempt == MAX_RETRIES - 1:
                    print(f"❌ Skipping article {index + 1} due to JSON parsing failure.")
                time.sleep(5)
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                print(f"❌ Skipping article {index + 1} due to network/parsing failure.")
            time.sleep(5)

    if not data:
        print(f"⚠️ Skipping article {index + 1} — moving to next topic")
        continue

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
        .article-body h2 {{ font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-top: 2.5rem; margin-bottom: 1rem; clear: both; }}
        .article-body h3 {{ font-size: 1.4rem; font-weight: 700; color: #f1f5f9; margin-top: 2rem; margin-bottom: 0.8rem; clear: both; }}
        .article-body p {{ margin-bottom: 1.5rem; font-size: 1.125rem; line-height: 1.8; color: #94a3b8; }}
        .article-body ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1.5rem; color: #94a3b8; clear: both; }}
        .article-body li {{ margin-bottom: 0.75rem; line-height: 1.7; }}
        .article-body strong {{ color: #e2e8f0; }}
        .article-body a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid #3b82f6; }}
        .article-image-fallback {{ background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); }}
    </style>
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8746884888217292"
         crossorigin="anonymous"></script>
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
                © 2026 TechGuide China. All rights reserved.
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
        print("⏳ Sleeping 15 seconds to prevent API Rate Limits...\n")
        time.sleep(15)

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
    
    print(f"\n🎉 ALL {len(generate_topics)} ARTICLES INJECTED SUCCESSFULLY. Homepage kept at {len(trimmed_cards)} articles maximum.")
else:
    print("❌ No articles were successfully generated, exiting without modifying homepage")
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

# ==========================================
# Auto-update Free AI Learning Resources section
# Adds one new free resource every day
# ==========================================
def generate_new_free_resource(client):
    """Generate one new free AI learning resource to add to the directory daily."""
    print("\n🤖 Generating one new free AI learning resource for today...")
    
    prompt = """Generate one high-quality free AI learning resource that's available online.

Output ONLY a valid JSON object with this structure:
{
  "title": "Name of the course/resource",
  "provider": "Who provides it (e.g., Coursera, YouTube, GitHub)",
  "description": "Brief description (1-2 sentences) about what you learn",
  "category": "Category (Machine Learning / Deep Learning / NLP / Generative AI / Business)",
  "url": "The official URL",
  "icon": "lucide icon name from this list: graduation-cap, book-open, youtube, github, code, video, book, compass, pen-tool"
}

Choose a different resource than the common ones already listed (ChatGPT, Andrew Ng, Hugging Face, Kaggle are already there). Pick something valuable but less commonly known."""
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "You are an expert curator of AI learning resources. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                timeout=60.0
            )
            raw_content = response.choices[0].message.content
            cleaned_content = clean_json_response(raw_content)
            resource = json.loads(cleaned_content)
            print(f"✅ Generated new free resource: {resource['title']} by {resource['provider']}")
            return resource
        except Exception as e:
            print(f"⚠️ Resource generation attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    
    return None

# ==========================================
# Auto-update AI Deals & Discounts section
# Adds one new deal every week (on Sunday)
# ==========================================
def generate_new_deal(client):
    """Generate one new AI tool deal/discount to add to the deals section weekly."""
    print("\n🤖 Generating one new AI tool deal for this week...")
    
    prompt = """Generate one popular AI tool that has a current discount or good pricing plan.

Output ONLY a valid JSON object with this structure:
{
  "tool_name": "Name of the AI tool",
  "description": "What it does, 1-2 sentences",
  "category": "Category (Content Writing / Image Generation / Productivity / Development / Video / Audio)",
  "price": "Current price (e.g., $12/month)",
  "original_price": "Original price if discounted, or empty string if no discount",
  "url": "Official website URL",
  "icon": "lucide icon name from this list: gift, paintbrush, brain, message-square, code, image, video, audio, file-text, calculator",
  "badge": "Badge text like BEST FOR ART, POPULAR, etc."
}

Pick a different tool than the ones already listed (ChatGPT, Midjourney, Claude, Notion are already there)."""
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "You are an expert curator of AI tool deals. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                timeout=60.0
            )
            raw_content = response.choices[0].message.content
            cleaned_content = clean_json_response(raw_content)
            deal = json.loads(cleaned_content)
            print(f"✅ Generated new deal: {deal['tool_name']} at {deal['price']}")
            return deal
        except Exception as e:
            print(f"⚠️ Deal generation attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    
    return None

# ==========================================
# Auto-update schedule:
# - Every day: add 1 new free resource
# - Every Sunday: add 1 new deal
# ==========================================
today = datetime.now()
# Add one new free resource every day
new_resource = generate_new_free_resource(client)
if new_resource:
    # We'll need to manually rebuild the full page since it's static HTML
    # For now, just log it - you can manually add it to the HTML
    print(f"\n📝 New free resource generated: {new_resource['title']} - add it to index.html #free-resources section")

# Add one new deal only on Sundays
if today.weekday() == 6:  # 6 = Sunday
    new_deal = generate_new_deal(client)
    if new_deal:
        print(f"\n🎉 New deal generated: {new_deal['tool_name']} - add it to index.html #ai-deals section")
