import os
import sys
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

if not api_key:
    print("❌ 严重错误：找不到 AI_API_KEY。请检查 GitHub Secrets 设置！")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

# 2. 撰写提示词
prompt = """
You are an expert tech blogger for TechGuide Global. 
Generate a new, engaging short article snippet about a trending AI tool or an AI money-making strategy.
The tone should be professional and exciting for a global audience.
You MUST output ONLY a valid JSON object with the following structure:
{
  "title": "A catchy, SEO-friendly title",
  "category": "One word: TOOLS, MONEY, or NEWS",
  "description": "Two sentences explaining why this matters.",
  "read_time": "e.g., 4 min"
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
    
    print(f"✅ 成功生成文章: {data['title']}")

    # 4. 构建插入网站的 HTML 代码块 (修复了括号渲染问题)
    new_article_html = f"""
                    <!-- AI Generated Article: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
                    <article class="bg-card p-5 rounded-2xl border border-slate-800 hover:border-slate-600 transition-all flex flex-col sm:flex-row gap-5 cursor-pointer group">
                        <div class="w-full sm:w-48 h-32 rounded-xl bg-gradient-to-br from-blue-600 to-purple-700 flex-shrink-0 flex items-center justify-center">
                            <i data-lucide="zap" class="w-10 h-10 text-white/40"></i>
                        </div>
                        <div class="flex flex-col justify-center flex-grow">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-[10px] font-bold text-primary px-2 py-0.5 bg-primary/10 rounded-full">{data['category']}</span>
                                <span class="text-[10px] text-slate-500">NEW ARTICLE</span>
                            </div>
                            <h3 class="text-lg font-bold text-white group-hover:text-primary transition-colors">{data['title']}</h3>
                            <p class="text-sm text-slate-400 mt-1 line-clamp-2">{data['description']}</p>
                            <div class="mt-3 text-[10px] text-slate-500 uppercase tracking-widest">{data['read_time']} READ</div>
                        </div>
                    </article>"""

    # 5. 读取 index.html 并寻找锚点插入内容
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    
    if anchor in html_content:
        updated_html = html_content.replace(anchor, f"{anchor}\n{new_article_html}")
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print("🎉 写入 index.html 成功！")
    else:
        print("❌ 错误：在 index.html 中找不到投递标记 <!-- AI_ARTICLE_ANCHOR -->")
        print("请检查你的 index.html 中是否包含这行精确的注释。")
        sys.exit(1) # 找不到锚点，抛出错误中止任务

except Exception as e:
    print(f"❌ 运行失败: {str(e)}")
    sys.exit(1) # API或JSON解析失败，抛出错误中止任务
