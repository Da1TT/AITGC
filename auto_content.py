import os
import json
from openai import OpenAI
from datetime import datetime

# ==========================================
# TechGuideChina - 全自动内容生成脚本
# ==========================================

api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE", "https://api.moonshot.cn/v1") 

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

prompt = """
You are an expert tech blogger and SEO specialist. 
Write a short, engaging snippet for a new blog post about a trending AI tool, AI automation strategy, or making money with AI.
Output ONLY a valid JSON object with the following keys:
"title": string, Catchy title.
"category": string, 1-2 words.
"description": string, 2 sentences max.
"read_time": string, e.g., "3 min".
"""

try:
    print("正在呼叫 Kimi 生成内容...")
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "You must output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={ "type": "json_object" },
        temperature=0.7
    )
    
    data = json.loads(response.choices[0].message.content)
    print(f"成功生成文章: {data['title']}")

    new_article_html = f"""
                    <!-- AI Auto Generated Article -->
                    <article class="bg-card p-5 rounded-2xl border border-slate-800 hover:border-slate-600 transition-colors flex flex-col sm:flex-row gap-5 cursor-pointer group">
                        <div class="w-full sm:w-48 h-32 rounded-xl bg-slate-800 flex-shrink-0 overflow-hidden relative">
                            <div class="absolute inset-0 bg-gradient-to-tr from-blue-900 to-slate-800 flex items-center justify-center">
                                <i data-lucide="zap" class="w-10 h-10 text-slate-500 opacity-50"></i>
                            </div>
                        </div>
                        <div class="flex flex-col justify-between flex-grow">
                            <div>
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-xs font-semibold text-primary uppercase tracking-wider">{data['category']}</span>
                                    <span class="text-xs text-slate-500">· Today</span>
                                </div>
                                <h3 class="text-lg font-bold text-white group-hover:text-primary transition-colors leading-tight mb-2">{data['title']}</h3>
                                <p class="text-sm text-slate-400 line-clamp-2">{data['description']}</p>
                            </div>
                            <div class="mt-3 text-xs text-slate-500">{data['read_time']} read</div>
                        </div>
                    </article>
"""

    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    if anchor in html_content:
        html_content = html_content.replace(anchor, f"{anchor}\n{new_article_html}")
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("成功更新 index.html！")
    else:
        print("错误：在 index.html 中找不到锚点 <!-- AI_ARTICLE_ANCHOR -->")

except Exception as e:
    print(f"发生错误: {e}")
