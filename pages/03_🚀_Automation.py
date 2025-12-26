import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
import re
from engine_manager import render_sidebar
from style_manager import apply_pro_style

# ===========================
# 1. 页面配置与样式
# ===========================
st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()

st.title("🚀 Automation Central")
st.caption("最后一步：将方案转换为浏览器自动化脚本 (RPA Script)")

# ===========================
# 2. 自动桥接逻辑 (Auto-Bridge)
# ===========================
# 检测是否有上游页面传来的数据
incoming_data = ""
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    # 将列表转换为文本字符串，用换行符分隔
    raw_list = st.session_state.final_solutions
    if isinstance(raw_list, list):
        incoming_data = "\n\n".join(raw_list)
    else:
        incoming_data = str(raw_list)

# ===========================
# 3. 控制台区域
# ===========================
col_opt1, col_opt2 = st.columns([3, 1])
with col_opt1:
    target_platform = st.selectbox(
        "目标 AI 平台 (Target Platform)", 
        ["Universal (通用模式 - 推荐)", "Gemini", "ChatGPT", "Midjourney Web"],
        help="通用模式能适配大多数聊天窗口"
    )

with col_opt2:
    st.write("") # 布局占位
    if st.button("🗑️ 清空队列", use_container_width=True):
        st.session_state.final_solutions = []
        st.rerun()

# 文本输入区 (自动填充)
user_input = st.text_area(
    "待执行任务队列 (Task Queue)", 
    value=incoming_data, 
    height=300, 
    placeholder="等待数据输入...\n或者你可以手动粘贴：\n**方案1：** ...\n**方案2：** ...",
    help="在这里可以手动微调 Prompt，脚本将严格按照这里的文本执行。"
)

st.divider()

# ===========================
# 4. 脚本生成核心 (JS Generator)
# ===========================
c_gen, c_tips = st.columns([2, 1])

with c_gen:
    need_white_bg = st.checkbox("生产模式：自动追加白底指令 (White BG)", value=False)
    
    if st.button("✨ 生成自动化脚本 (Generate JS Script)", type="primary", use_container_width=True):
        if not user_input.strip():
            st.warning("队列为空，无法生成脚本")
        else:
            # --- A. 任务解析 (Parsing) ---
            task_list = []
            
            # 1. 尝试用 **方案N：** 进行分割
            # 正则逻辑：匹配 "**方案" + 数字 + "：" 或 ":"
            if "**方案" in user_input:
                blocks = re.split(r'\*\*方案\d+[：:]', user_input)
                # 过滤掉空的切片，并清理首尾
                raw_tasks = [b.strip() for b in blocks if len(b.strip()) > 5]
            else:
                # 2. 兜底逻辑：如果不是标准格式，按空行分割
                raw_tasks = [t.strip() for t in user_input.split("\n\n") if t.strip()]

            # 处理白底需求
            for t in raw_tasks:
                # 去掉可能残留的 markdown 符号
                clean_t = t.replace("**", "").strip()
                task_list.append(clean_t)
                if need_white_bg:
                    task_list.append("Generate a white background version of the image above")

            # --- B. 构建 JS 代码 (Injection Core) ---
            if task_list:
                encoded_data = urllib.parse.quote(json.dumps(task_list))
                
                # 这是一个高度优化的自动化脚本，能适配大多数 DOM 结构
                js_code = f"""(async function() {{
                    window.kill = false;
                    const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                    
                    // --- UI Helper: 创建状态条 ---
                    function showStatus(text, color = "#1e293b") {{
                        let el = document.getElementById('magic-status-bar');
                        if (!el) {{
                            el = document.createElement('div');
                            el.id = 'magic-status-bar';
                            el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:10px 20px; border-radius:30px; font-family:sans-serif; font-size:14px; font-weight:bold; color:#fff; box-shadow:0 10px 25px rgba(0,0,0,0.2); transition: all 0.3s;";
                            document.body.appendChild(el);
                        }}
                        el.textContent = text;
                        el.style.backgroundColor = color;
                    }}

                    // --- DOM Finder: 寻找输入框 ---
                    function getInputBox() {{
                        // 1. 优先找可编辑 DIV (常见于现代 AI 网页)
                        let divBox = document.querySelector('div[role="textbox"][contenteditable="true"]');
                        if (divBox) return divBox;
                        // 2. 其次找 Textarea
                        return document.querySelector('#prompt-textarea, textarea, [placeholder*="Enter"], [placeholder*="Message"]');
                    }}

                    // --- DOM Finder: 寻找发送按钮 ---
                    function getSendBtn() {{
                        // 策略：找aria-label含Send的，或者SVG图标
                        let btn = document.querySelector('button[aria-label*="Send"], button[aria-label*="发送"], button[data-testid="send-button"]');
                        if (btn && !btn.disabled) return btn;
                        return null; // 找不到则依赖回车事件(未实现，通常按钮都能找到)
                    }}

                    showStatus("🚀 脚本就绪，任务数: " + tasks.length, "#444444"); 
                    
                    for (let i = 0; i < tasks.length; i++) {{
                        if (window.kill) {{ showStatus("🛑 已停止", "#ef4444"); break; }}
                        
                        showStatus("✍️ 正在输入: " + (i+1) + "/" + tasks.length, "#2563eb");
                        
                        let box = getInputBox();
                        if (!box) {{ showStatus("❌ 找不到输入框 (请点击输入框后重试)", "#ef4444"); break; }}
                        
                        box.focus();
                        // 模拟输入
                        if (box.tagName === 'DIV') {{ box.innerText = tasks[i]; }} 
                        else {{ box.value = tasks[i]; }}
                        
                        // 触发 React/Vue 事件绑定
                        box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        await new Promise(r => setTimeout(r, 800)); // 等待 UI 响应
                        
                        let sendBtn = getSendBtn();
                        if (sendBtn) {{
                            sendBtn.click();
                        }} else {{
                            // 兜底：尝试模拟回车 (视情况而定)
                            showStatus("⚠️ 找不到按钮，请手动点击发送", "#eab308");
                        }}
                        
                        // --- 等待生成结束 (简单倒计时逻辑) ---
                        if (i < tasks.length - 1) {{
                            let waitTime = 60; // 默认每张图给 60秒 生成时间
                            for (let s = waitTime; s > 0; s--) {{
                                if (window.kill) break;
                                showStatus("⏳ 等待生成: " + s + "s", "#059669");
                                await new Promise(r => setTimeout(r, 1000));
                            }}
                        }}
                    }}
                    if(!window.kill) showStatus("🎉 所有任务已执行完毕！", "#16a34a");
                }})();"""

                # 自动复制到剪贴板的 Hack
                js_val = json.dumps(js_code)
                components.html(f"""
                <script>
                    const text = {js_val};
                    navigator.clipboard.writeText(text).catch(err => console.error('Auto-copy failed', err));
                </script>
                """, height=0)

                st.success(f"已生成 {len(task_list)} 条指令！代码已复制到剪贴板。")
                st.code(js_code, language="javascript")
                st.caption("提示：在 AI 网页按 F12 打开控制台 (Console)，粘贴代码并回车即可。")

with c_tips:
    st.info("""
    **使用说明:**
    1. 确保左侧输入框内有 Prompt 内容。
    2. 点击 **Generate JS Script**。
    3. 代码会自动复制。
    4. 打开 ChatGPT/Midjourney 网页。
    5. 按 **F12** -> 点击 **Console** 标签。
    6. **Ctrl+V** 粘贴 -> **Enter** 回车。
    """)
