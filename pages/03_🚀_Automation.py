import streamlit as st
from style_manager import apply_pro_style
import streamlit.components.v1 as components
import json
import urllib.parse
import re
from engine_manager import render_sidebar

# ===========================
# 1. 页面配置
# ===========================
st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()

st.title("Automation Central (Pro V17)")
st.caption("Auto-Detect & Data Receiver (自动接收数据 + 智能状态检测)")

# ===========================
# 2. 🟢 核心修复：自动接收上游数据
# ===========================
# 逻辑：检查是否有来自 Page 01 或 02 的新数据 (final_solutions)
incoming_data = ""

if "final_solutions" in st.session_state and st.session_state.final_solutions:
    raw_data = st.session_state.final_solutions
    
    # 如果是列表（通常是列表），就合并成字符串
    if isinstance(raw_data, list):
        incoming_data = "\n\n".join(raw_data)
    else:
        incoming_data = str(raw_data)

# 如果 session 里没有数据，尝试读取一下缓存（防止手滑刷新丢数据）
if not incoming_data:
    incoming_data = st.session_state.get("auto_input_cache", "")

# ===========================
# 3. 界面布局
# ===========================
col_opt1, col_opt2 = st.columns([2, 1])
with col_opt1:
    target_platform = st.selectbox(
        "Target AI Platform", 
        ["ChatGPT (Specialized)", "Midjourney Web", "Universal"],
        index=0, 
        help="ChatGPT 模式包含针对性的 DOM 检测逻辑"
    )

# 输入框：自动填入接收到的数据
# 注意：这里我们不使用 key 来绑定值，而是直接用 value，避免状态冲突
user_input = st.text_area(
    "Prompt Queue", 
    value=incoming_data, 
    height=350, 
    placeholder="等待投递数据..."
)

# 当用户手动修改输入框时，我们可以更新一下缓存（可选）
if user_input != incoming_data:
    st.session_state.auto_input_cache = user_input

# ===========================
# 4. 选项与操作
# ===========================
st.divider()
col_check, col_btn = st.columns([1, 2])
with col_check:
    need_white_bg = st.checkbox("Production Mode: Auto White Background", value=False)

# ===========================
# 5. 生成脚本逻辑 (保留 V16 发送按钮检测)
# ===========================
with col_btn:
    if st.button("Generate Script (Smart Wait)", type="primary", use_container_width=True):
        # --- A. 任务解析 ---
        task_list = []
        if user_input:
            if "###" in user_input:
                raw_tasks = [t.strip() for t in user_input.split("###") if len(t.strip()) > 2]
            else:
                # 正则匹配 **Option 1:** 或 **方案1：**
                blocks = re.split(r'\*\*.*?(?:Option|方案|Scheme).*?[\d]+[:：].*?\*\*', user_input)
                # 过滤掉太短的碎片
                raw_tasks = []
                # 重新通过原始文本行来抓取完整 Prompt (正则分割有时会吞掉前缀)
                # 简单粗暴法：按双换行分割，然后清理空行
                lines = user_input.split('\n\n')
                for line in lines:
                    clean_line = line.strip()
                    if len(clean_line) > 5:
                        # 去掉可能存在的 **Option X:** 前缀，只保留核心 Prompt
                        # 但为了保留 ChatGPT 的上下文，保留前缀也是可以的，这里选择保留原样
                        clean_line = clean_line.replace("(Invalid API Key - Raw Data Used)", "").strip()
                        raw_tasks.append(clean_line)
                
            if need_white_bg:
                for t in raw_tasks:
                    task_list.append(t)
                    task_list.append("Generate a white background version of the image above")
            else:
                task_list = raw_tasks

        # --- B. 脚本构建 ---
        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))
            
            # JS 核心代码 (V16 逻辑：检测 Send 按钮)
            js_code = f"""(async function() {{
                console.clear();
                console.log("%c 🚀 自动化脚本 V17 已启动 ", "background: #222; color: #bada55; font-size: 16px");
                
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
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

                function getInputBox() {{
                    const ids = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]'];
                    for (let selector of ids) {{
                        let el = document.querySelector(selector);
                        if (el) return el;
                    }}
                    return null;
                }}

                function getSendBtn() {{
                    return document.querySelector('[data-testid="send-button"]') || 
                           document.querySelector('button[aria-label="Send prompt"]');
                }}

                // 核心：只要没有发送按钮，或者按钮是灰的，就认为是在忙
                function isBusy() {{
                    const sendBtn = getSendBtn();
                    const stopBtn = document.querySelector('[aria-label="Stop generating"]') || document.querySelector('[data-testid="stop-button"]');
                    if (stopBtn) return true;
                    if (!sendBtn) return true;
                    if (sendBtn.disabled) return true;
                    return false;
                }}

                showStatus("🚀 脚本就绪，任务数: " + tasks.length, "#444444"); 
                
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) {{ showStatus("🛑 已停止", "#ef4444"); break; }}
                    
                    showStatus("✍️ 正在输入: " + (i+1) + "/" + tasks.length, "#3b82f6");
                    
                    let box = getInputBox();
                    if (!box) {{ 
                        showStatus("❌ 找不到输入框，尝试重试...", "#ef4444"); 
                        await new Promise(r => setTimeout(r, 2000));
                        box = getInputBox();
                        if(!box) {{ alert("脚本无法定位输入框，请刷新页面"); break; }}
                    }}
                    
                    box.focus();
                    if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                        box.innerHTML = ""; 
                        box.innerText = tasks[i]; 
                    }} else {{
                        box.value = tasks[i];
                    }}
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    await new Promise(r => setTimeout(r, 1000)); 

                    let sendBtn = getSendBtn();
                    if (sendBtn && !sendBtn.disabled) {{
                        sendBtn.click();
                    }} else {{
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', bubbles: true }}));
                    }}
                    
                    if (i < tasks.length - 1) {{
                        showStatus("⏳ 等待服务器响应...", "#f59e0b");
                        await new Promise(r => setTimeout(r, 5000));
                        
                        let waitSec = 0;
                        while(true) {{
                            if (window.kill) break;
                            if (isBusy()) {{
                                showStatus("🎨 正在绘图 (" + waitSec + "s)...", "#6366f1");
                                await new Promise(r => setTimeout(r, 1000));
                                waitSec++;
                                if (waitSec > 600) break; // 10分钟超时
                            }} else {{
                                break; 
                            }}
                        }}
                        
                        for (let s = 5; s > 0; s--) {{
                            if (window.kill) break;
                            showStatus("✅ 完成. 冷却中: " + s + "s", "#10b981");
                            await new Promise(r => setTimeout(r, 1000));
                        }}
                    }}
                }}
                if(!window.kill) showStatus("🎉 所有任务执行完毕！", "#15803d");
            }})();"""

            js_val = json.dumps(js_code)
            components.html(f"""
            <script>
                const text = {js_val};
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(text).catch(err => console.log('Auto-copy failed'));
                }}
            </script>
            """, height=0)

            st.success(f"已生成 {len(task_list)} 条指令，脚本已复制到剪贴板！")
            st.code(js_code, language="javascript")
            
        else:
            st.error("队列为空，无法生成脚本")

# 底部清空按钮
if st.button("Clear Queue"):
    st.session_state.final_solutions = []
    st.session_state.auto_input_cache = ""
    st.rerun()
