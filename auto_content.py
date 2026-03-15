import os
import json
import re
import sys
from openai import OpenAI
from datetime import datetime
import random

# ==========================================
# TechGuide - 深度适配高级 UI 的自动发文脚本
# ==========================================

api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE", "https://api.moonshot.cn/v1") 

if not api_key:
    print("❌ 致命错误：找不到 AI_API_KEY，请检查 GitHub Secrets 配置！")
    sys.exit(1) # 强制向 GitHub 报告失败

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

prompt = """
You are an expert tech blogger and SEO specialist. 
Write a highly engaging snippet for a new blog post about a trending AI tool, AI automation strategy, or prompt engineering.
Output ONLY a valid JSON object with the following keys:
{
  "title": "A catchy, SEO-friendly title (e.g., Mastering AI Voice Cloning...)",
  "category": "One word: TOOLS, STRATEGY, or MONEY",
  "description": "Two sentences explaining the value of the guide.",
  "read_time": "e.g., 7 min"
}
"""

def clean_json_response(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

image_pool = [
    "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1684369175836-e8f000305f24?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1696258686454-60082b2c33e2?q=80&w=800&auto=format&fit=crop"
]

try:
    print(f"[{datetime.now()}] 正在呼叫 Kimi 撰写最新策略指南...")
    
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
    
    print(f"✅ 成功生成文章: {data['title']}")

    date_str = datetime.now().strftime('%b %d')
    random_image = random.choice(image_pool)

    new_article_html = f"""
                    <!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d')} -->
                    <div class="flex flex-col md:flex-row gap-6 p-6 bg-[#0f172a] rounded-2xl border border-slate-800 hover:border-slate-600 transition-all mb-6 group cursor-pointer">
                        <div class="w-full md:w-2/5 h-48 rounded-xl overflow-hidden flex-shrink-0 relative">
                            <img src="{random_image}" alt="{data['title']}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                            <div class="absolute inset-0 bg-gradient-to-t from-[#0f172a]/80 to-transparent md:hidden"></div>
                        </div>
                        <div class="w-full md:w-3/5 flex flex-col justify-center">
                            <div class="flex items-center gap-2 mb-3">
                                <span class="bg-blue-900/40 text-blue-400 text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">{data['category']}</span>
                                <span class="text-emerald-400 text-[10px] font-bold px-2 py-1 rounded bg-emerald-900/30 flex items-center gap-1">
                                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> NEW
                                </span>
                            </div>
                            <h3 class="text-xl font-bold text-white mb-3 group-hover:text-blue-400 transition-colors leading-tight">{data['title']}</h3>
                            <p class="text-slate-400 text-sm mb-5 line-clamp-2 leading-relaxed">{data['description']}</p>
                            <div class="flex items-center gap-5 text-xs text-slate-500 font-medium">
                                <span class="flex items-center gap-1.5"><i data-lucide="calendar" class="w-3.5 h-3.5"></i> {date_str}</span>
                                <span class="flex items-center gap-1.5"><i data-lucide="clock" class="w-3.5 h-3.5"></i> {data['read_time']} READ</span>
                            </div>
                        </div>
                    </div>"""

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
        print("请打开 index.html，在你想要插入文章的地方加入这行注释。")
        sys.exit(1) # 强制向 GitHub 报告失败

except Exception as e:
    print(f"💥 运行失败: {str(e)}")
    sys.exit(1) # 强制报错，防止 GitHub 掩盖问题
