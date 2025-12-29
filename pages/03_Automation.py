import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
import re
import os
import sys

# ===========================
# 0. 基础设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import render_sidebar, init_data
from style_manager import apply_pro_style

st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()
init_data()

# ===========================
# 1. 数据同步
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

default_text = "\n\n".join(st.session_state.global_queue) if st.session_state.global_queue else ""

# ===========================
# 2. 界面布局
# ===========================
st.markdown("## Automation Central")
st.caption("🚀 Universal Script (v18.0 - TrustedHTML & Button Lock)")

col_opt1, col_opt2 = st.columns([3, 1])
with col_opt1:
    target_platform = st.selectbox(
        "Target Platform",
        ["Universal (Auto-Detect)", "Midjourney/Discord", "ChatGPT", "Gemini", "Claude"],
        help="Universal mode adapts to the website automatically."
    )
with col_opt2:
    if st.button("Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

user_input = st.text_area(
    "Task Queue", 
    value=default_text, 
    height=350, 
    key="main_input_area",
    placeholder="Tasks from Studio will appear here..."
)

# 数据回写
if user_input != default_text:
    st.session_state.global_queue = [t for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 3. 核心脚本生成 (🔥 万能融合版 🔥)
# ===========================
if st.button("⚡ Generate Universal Script", type="primary", use_container_width=True):
    
    # --- A. 简单粗暴的任务解析 ---
    task_list = []
    if user_input:
        # 只要有内容，就按行或者按块切分，兼容性最强
        if "###" in user_input:
            task_list = [t.strip() for t in user_input.split("###") if len(t.strip()) > 2]
        else:
            # 优先找 "**方案" 这种头
            blocks = re.split(r'\*\*.*?(?:方案|Scheme|Option|Task).*?[\d]+[:：].*?\*\*', user_input)
            if len(blocks) < 2:
                # 没头？那就按换行切
                task_list = [t.strip() for t in user_input.split('\n') if t.strip()]
            else:
                task_list = [b.strip() for b in blocks if len(b.strip()) > 5]

    # --- B. 脚本构造 ---
    if task_list:
        encoded_data = urllib.parse.quote(json.dumps(task_list))
        
        js_code = f"""(async function() {{
            console.clear();
            console.log("%c 🚀 Universal Automation v18 ", "background: #222; color: #00ff00; font-size: 14px");
            window.kill = false;
            
            const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
            
            // 🔥 1. 安全的状态条 (TrustedHTML Fix) 🔥
            // 使用 createElement 而不是 innerHTML，Gemini 不会报错
            function showStatus(text, color = "#1e293b", subText = "") {{
                let el = document.getElementById('magic-status-bar');
                if (!el) {{
                    el = document.createElement('div');
                    el.id = 'magic-status-bar';
                    el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:12px 24px; border-radius:12px; font-family:sans-serif; font-size:14px; font-weight:bold; box-shadow:0 10px 30px rgba(0,0,0,0.3); transition: all 0.2s; display: flex; flex-direction: column; align-items: center; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(8px);";
                    document.body.appendChild(el);
                }}
                
                el.textContent = ''; // 清空
                
                let mainSpan = document.createElement('span');
                mainSpan.textContent = text;
                el.appendChild(mainSpan);
                
                if (subText) {{
                    let subSpan = document.createElement('span');
                    subSpan.textContent = subText;
                    subSpan.style.cssText = "font-size: 11px; opacity: 0.8; margin-top: 4px; font-weight: normal;";
                    el.appendChild(subSpan);
                }}
                
                el.style.backgroundColor = color;
                el.style.color = "#fff";
            }}

            // 🔥 2. 万能输入框定位 (覆盖所有主流平台) 🔥
            function getInputBox() {{
                const selectors = [
                    '#prompt-textarea',           // ChatGPT / MJ Alpha
                    'div[contenteditable="true"]', // Gemini / Claude / Discord
                    'textarea[data-id="root"]',    // Other LLMs
                    'textarea',                    // Generic
                    'input[type="text"]'           // Fallback
                ];
                for (let s of selectors) {{
                    let el = document.querySelector(s);
                    if (el) return el;
                }}
                return null;
            }}

            // 🔥 3. 万能发送按钮定位 🔥
            function getSendBtn() {{
                // 策略A: 找 aria-label (最准)
                let explicitBtn = document.querySelector('button[aria-label*="Send"], button[aria-label*="发送"], button[aria-label*="Prompt"]');
                if (explicitBtn && !explicitBtn.disabled) return explicitBtn;
                
                // 策略B: 找图标/svg (针对 Gemini/Claude)
                let iconBtns = Array.from(document.querySelectorAll('button'));
                return iconBtns.find(b => {{
                    // 排除掉停止按钮
                    if (b.querySelector('svg') || b.querySelector('img') || b.querySelector('mat-icon')) {{
                        let label = (b.ariaLabel || "").toLowerCase();
                        let html = b.innerHTML.toLowerCase();
                        if (label.includes('stop') || label.includes('停止')) return false;
                        if (html.includes('path d="M0 0h24v24H0z"')) return false; // stop icon path check
                        // 如果按钮是蓝色的或者位置在右下角，大概率是发送
                        return !b.disabled;
                    }}
                    return false;
                }});
            }}

            // 🔥 4. 核心：死锁状态检测 (Button Lock) 🔥
            // 返回 true 表示忙碌 (Busy)，返回 false 表示空闲 (Idle)
            function isSystemBusy() {{
                // A. 找停止按钮 (绝对铁证)
                const stopSelectors = [
                    '[aria-label="Stop generating"]',
                    'button[aria-label="Stop"]',
                    '.stop-button',
                    '[data-testid="stop-button"]'
                ];
                for (let s of stopSelectors) {{
                    if (document.querySelector(s)) return true; // 发现停止按钮 -> 忙
                }}

                // B. 检查发送按钮状态
                const sendBtn = getSendBtn();
                if (!sendBtn) return true; // 连发送按钮都找不到 -> 忙 (可能在加载)
                if (sendBtn.disabled) return true; // 发送按钮变灰 -> 忙
                
                // C. 文本检测 (针对 Discord 这种没有明显按钮变化的)
                // 检查最后一条消息是否包含进度条或 Waiting
                const msgs = document.querySelectorAll('li[class*="message"]');
                if (msgs.length > 0) {{
                    const lastText = msgs[msgs.length - 1].innerText;
                    if (lastText.includes('Waiting to start') || lastText.includes('(fast)') || lastText.includes('%')) return true;
                }}

                return false; // 一切正常 -> 空闲
            }}

            // --- 主循环 ---
            showStatus("🚀 Script Ready", "#222", tasks.length + " tasks loaded");
            
            for (let i = 0; i < tasks.length; i++) {{
                if (window.kill) {{ showStatus("🛑 Stopped", "#ef4444"); break; }}
                
                // 1. 找坑位
                let box = getInputBox();
                if (!box) {{ 
                    showStatus("🔍 Searching Input...", "#f59e0b");
                    await new Promise(r => setTimeout(r, 2000));
                    box = getInputBox();
                    if (!box) {{ showStatus("❌ No Input Found", "#ef4444"); break; }}
                }}
                
                // 2. 填弹药
                showStatus("✍️ Writing Task " + (i+1), "#3b82f6", (i+1)+"/"+tasks.length);
                box.focus();
                
                // 兼容性输入法
                if (document.execCommand) {{
                    document.execCommand('insertText', false, tasks[i]); 
                }} else {{
                    box.value = tasks[i]; 
                    box.innerText = tasks[i];
                }}
                
                // 触发事件 (唤醒 React)
                box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                await new Promise(r => setTimeout(r, 1000));

                // 3. 扣扳机 (发送)
                let sendBtn = getSendBtn();
                if (sendBtn) {{
                    sendBtn.click();
                }} else {{
                    box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                }}
                
                // 4. 🔥 鹰眼防抢跑逻辑 🔥
                showStatus("⏳ Sent... Locking", "#64748b");
                // 强制等 5 秒，让子弹飞一会儿 (防止网络卡顿还没出现停止按钮)
                await new Promise(r => setTimeout(r, 5000));

                if (i < tasks.length - 1) {{
                    let idleStreak = 0;
                    let maxWait = 900; // 15分钟超时
                    
                    while (true) {{
                        if (window.kill) break;
                        
                        if (isSystemBusy()) {{
                            // 只要发现忙，计数器归零，死等
                            idleStreak = 0;
                            showStatus("🎨 Generating...", "#7c3aed", "System is busy");
                            await new Promise(r => setTimeout(r, 1000));
                        }} else {{
                            // 发现空闲，开始累积信用
                            idleStreak++;
                            let remaining = 10 - idleStreak; // 目标：连续 10 秒空闲
                            
                            if (remaining > 0) {{
                                showStatus("✅ Verifying...", "#10b981", "Confirming in " + remaining + "s");
                                await new Promise(r => setTimeout(r, 1000));
                            }} else {{
                                // 连续 10 秒没动静，才敢放行
                                showStatus("🍵 Cooldown Finished", "#059669", "Next task...");
                                await new Promise(r => setTimeout(r, 1000));
                                break; 
                            }}
                        }}
                    }}
                }}
            }}
            if(!window.kill) showStatus("🎉 All Done!", "#15803d");
        }})();"""

        # --- C. 自动复制 ---
        js_val = json.dumps(js_code)
        components.html(f"""
        <script>
            const text = {js_val};
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(text).catch(err => console.log('Copy failed'));
            }}
        </script>
        """, height=0)

        st.success(f"✅ Generated {len(task_list)} tasks. Code copied to clipboard!")
        with st.expander("Show Code", expanded=True):
            st.code(js_code, language="javascript")
        
    else:
        st.error("⚠️ Queue is empty.")
