import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
import re
from engine_manager import render_sidebar
from style_manager import apply_pro_style

# ===========================
# 1. 页面配置
# ===========================
st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()

st.title("🚀 Automation Central (V3 Pro)")
st.caption("自动化脚本生成中心 - 增强兼容版")

# ===========================
# 2. 自动接收数据
# ===========================
incoming_data = ""
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    raw_list = st.session_state.final_solutions
    if isinstance(raw_list, list):
        incoming_data = "\n\n".join(raw_list)
    else:
        incoming_data = str(raw_list)

# ===========================
# 3. 界面布局
# ===========================
col_opt1, col_opt2 = st.columns([3, 1])
with col_opt1:
    st.info("💡 提示：此脚本适配 ChatGPT / Midjourney / Claude 网页版")

with col_opt2:
    if st.button("🗑️ 清空队列"):
        st.session_state.final_solutions = []
        st.rerun()

user_input = st.text_area(
    "任务队列 (Task Queue)", 
    value=incoming_data, 
    height=300,
    placeholder="等待生成数据..."
)

st.divider()

# ===========================
# 4. JS 脚本生成核心 (V3 强力版)
# ===========================
if st.button("✨ 生成强力脚本 (Generate V3 Script)", type="primary", use_container_width=True):
    if not user_input.strip():
        st.warning("队列为空")
    else:
        # A. 解析任务
        task_list = []
        if "**方案" in user_input:
            blocks = re.split(r'\*\*方案\d+[：:]', user_input)
            raw_tasks = [b.strip() for b in blocks if len(b.strip()) > 5]
        else:
            raw_tasks = [t.strip() for t in user_input.split("\n\n") if t.strip()]
        
        # 过滤
        task_list = [t.replace("**", "").strip() for t in raw_tasks]

        # B. 构建 JS
        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))
            
            # ⬇️⬇️⬇️ 核心 JS 逻辑更新 ⬇️⬇️⬇️
            js_code = f"""(async function() {{
                console.log("%c 🚀 纹身自动化脚本已启动 ", "background: #222; color: #bada55; font-size: 20px");
                
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
                // --- 1. 状态条 UI ---
                function showStatus(text, color = "#2563eb") {{
                    let el = document.getElementById('magic-status-bar');
                    if (!el) {{
                        el = document.createElement('div');
                        el.id = 'magic-status-bar';
                        el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:12px 24px; border-radius:8px; font-family:sans-serif; font-size:16px; font-weight:bold; color:#fff; box-shadow:0 10px 30px rgba(0,0,0,0.5); transition: all 0.3s; border: 1px solid rgba(255,255,255,0.2);";
                        document.body.appendChild(el);
                    }}
                    el.textContent = text;
                    el.style.backgroundColor = color;
                    console.log(">>> [Status]: " + text); // 同时打印到控制台
                }}

                // --- 2. 寻找输入框 (适配 ChatGPT 新版) ---
                function getInputBox() {{
                    // 策略A: ID精确定位
                    let box = document.getElementById('prompt-textarea');
                    if (box) return box;
                    
                    // 策略B: 属性定位
                    box = document.querySelector('[contenteditable="true"]');
                    if (box) return box;
                    
                    // 策略C: 标签定位
                    box = document.querySelector('textarea');
                    return box;
                }}

                // --- 3. 寻找发送按钮 ---
                function getSendBtn() {{
                    return document.querySelector('button[data-testid="send-button"]') || 
                           document.querySelector('button[aria-label="Send prompt"]') ||
                           document.querySelector('button[aria-label="发送"]');
                }}

                showStatus("✅ 脚本注入成功！准备执行 " + tasks.length + " 个任务...", "#10b981");
                await new Promise(r => setTimeout(r, 2000));

                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    
                    // --- 步骤A: 找框 ---
                    let box = getInputBox();
                    if (!box) {{ 
                        showStatus("❌ 找不到输入框！请手动点击一下网页里的输入框，脚本将在 3秒后 重试...", "#ef4444");
                        await new Promise(r => setTimeout(r, 3000));
                        box = getInputBox(); // 再试一次
                        if(!box) {{ alert("脚本无法自动找到输入框，请刷新页面重试"); break; }}
                    }}

                    // --- 步骤B: 填词 ---
                    showStatus("✍️ 正在输入第 " + (i+1) + " 个...", "#3b82f6");
                    box.focus();
                    
                    // 模拟 React 输入事件
                    if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                        box.innerHTML = ""; // 清空
                        box.innerText = tasks[i]; 
                    }} else {{
                        box.value = tasks[i];
                    }}
                    
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    await new Promise(r => setTimeout(r, 1000)); // 等待一下

                    // --- 步骤C: 发送 ---
                    let btn = getSendBtn();
                    if (btn) {{
                        btn.click();
                    }} else {{
                        // 如果找不到按钮，尝试模拟回车 (仅适用于某些网站)
                        showStatus("⚠️ 找不到发送按钮，尝试回车...", "#f59e0b");
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', bubbles: true }}));
                    }}

                    // --- 步骤D: 冷却倒计时 ---
                    if (i < tasks.length - 1) {{
                        let wait = 20; // 默认 20秒 间隔
                        for (let s = wait; s > 0; s--) {{
                            showStatus("⏳ 等待生成: " + s + "秒...", "#6b7280");
                            await new Promise(r => setTimeout(r, 1000));
                        }}
                    }}
                }}
                
                showStatus("🎉 全部任务完成！", "#10b981");

            }})();"""

            # 自动复制
            js_val = json.dumps(js_code)
            components.html(f"""
            <script>
                navigator.clipboard.writeText({js_val});
            </script>
            """, height=0)

            st.success("✅ 代码已生成并复制！(请去 ChatGPT 控制台粘贴)")
            st.code(js_code, language="javascript")
