import streamlit as st
import sys
import os
import re
import time

# Add parent directory to path so we can import pb
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pb.local_model import LocalClient
from pb import gsm

# Set Page Config
st.set_page_config(
    page_title="PromptBreeder Evolved Solver",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161a24 100%);
        color: #e2e8f0;
    }

    /* Main Title Styling */
    .title-gradient {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: linear-gradient(90deg, #ff7e5f 0%, #feb47b 50%, #86e3ce 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.2rem;
        letter-spacing: -0.05em;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Custom Cards */
    .premium-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 12px;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Prompt Display Card */
    .prompt-box {
        background-color: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #feb47b;
        border-radius: 8px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #cbd5e1;
        overflow-x: auto;
        white-space: pre-wrap;
        margin: 10px 0;
    }
    
    /* Code Output Box */
    .output-box {
        background-color: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        color: #e2e8f0;
        min-height: 250px;
        white-space: pre-wrap;
        line-height: 1.6;
    }
    
    /* Metrics Badge */
    .metric-badge {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #c084fc;
        margin-top: 8px;
    }

    .answer-badge {
        display: inline-block;
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 1.1rem;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .answer-badge-invalid {
        display: inline-block;
        background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 1.1rem;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }

    /* Gradient Divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
        margin: 24px 0;
    }

    /* Accent Pill */
    .pill {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# Best Evolved Task Prompt from generation_16.json (fitness = 0.75)
BEST_TASK_PROMPT = (
    "\"If you have 3 gold coins, 5 silver coins, and 30 dollars cash, how much\n"
    "money do you have in dollars?\" The advice was to break down the problem step by \n"
    "step:\n\n"
    "1. Calculate the value of the gold coins:\n"
    "   - Each gold coin is worth\n"
    "$50.\n"
    "   - You have 3 gold coins.\n"
    "   \\[\n"
    "   50 \\times 3 = 150 \\text{ \n"
    "dollars}\n"
    "   \\]\n\n"
    "2. Calculate the value of the silver coins:\n"
    "   - Each \n"
    "silver coin is worth $25.\n"
    "   - You have 5 silver coins.\n"
    "   \\[\n"
    "   25 \\times \n"
    "5 = 125 \\text{ dollars}\n"
    "   \\]\n\n"
    "3. Add the values together with the cash:\n"
    " \n"
    "- Cash amount: $30\n"
    "   \\[\n"
    "   150 + 125 + 30 = 305 \\text{ dollars}\n"
    "   \n"
    "\\]\n\n"
    "So, the total amount of money you have is $\\boxed{305}$ dollars."
)

# Header Section
st.markdown("<h1 class='title-gradient'>PromptBreeder Evolved Solver</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Trải nghiệm Task Prompt tối ưu nhất được tiến hóa qua 16 thế hệ của thuật toán PromptBreeder "
    "(Độ chính xác Fitness: <b>75%</b> trên tập dữ liệu GSM8K).</p>", 
    unsafe_allow_html=True
)

st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

# Sidebar configurations
with st.sidebar:
    st.markdown("Cấu hình Mô hình")
    
    ollama_model = st.text_input("Local Ollama Model", value="qwen2.5:1.5b", help="Tên mô hình chạy trong Ollama của bạn")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1, help="Nên để 0.0 để có kết quả chính xác và ổn định nhất")
    
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>CS410 - PromptBreeder Demo App</p>", unsafe_allow_html=True)

# Main Grid Layout
col_left, col_right = st.columns([1, 1])

with col_left:
    with st.container(border=True):
        st.subheader("Nhập Đề Bài (GSM8K Format)")
        st.write("Nhập đề bài toán đố tiểu học bằng tiếng Anh hoặc tiếng Việt dưới đây để giải:")
        
        # Pre-loaded GSM8K Examples
        st.markdown("Đề bài mẫu gợi ý (Click để chọn):")
        ex1 = "Weng earns $12 an hour for babysitting. Yesterday, she babysat for 5 hours. She spent $15 on lunch. How much money does she have left?"
        ex2 = "A school has 4 classes of 25 students each. If 20% of the students are absent today, how many students are present?"
        ex3 = "Kelsey brought 2/5 of a tray of 30 eggs. Stephanie brought half a tray of 30 eggs. Alayah brought 40 more eggs than Kelsey and Stephanie combined. How many eggs did they bring in total?"
        
        selected_example = st.selectbox(
            "Chọn một ví dụ...",
            ["(Tùy chỉnh)", "Ví dụ 1: Babysitting & Lunch", "Ví dụ 2: Học sinh vắng mặt", "Ví dụ 3: Khay trứng Alayah"],
            index=0
        )
        
        default_text = ""
        if selected_example == "Ví dụ 1: Babysitting & Lunch":
            default_text = ex1
        elif selected_example == "Ví dụ 2: Học sinh vắng mặt":
            default_text = ex2
        elif selected_example == "Ví dụ 3: Khay trứng Alayah":
            default_text = ex3
            
        user_input = st.text_area(
            "Đề bài toán:", 
            value=default_text if default_text else "A retail store sells notebooks for $3 each. If a student buys 5 notebooks and gets a 10% discount, how much does he pay in dollars?",
            height=150,
            placeholder="Nhập đề bài toán đố tại đây..."
        )
        
        btn_solve = st.button("GIẢI NGAY", use_container_width=True)

    # Active Task Prompt Expandable Container
    with st.expander("Xem chi tiết Evolved Task Prompt"):
        st.markdown("Dưới đây là cấu trúc Task Prompt tốt nhất thu được ở Generation 16:")
        st.markdown(f"<div class='prompt-box'>{BEST_TASK_PROMPT}</div>", unsafe_allow_html=True)

# Parse helper function (similar to GSM8K parser used in the original project)
def parse_and_format_answer(completion):
    # Standard format #### [answer]
    model_answer = gsm.gsm_extract_answer(completion)
    if model_answer != gsm.INVALID_ANS:
        return model_answer, "Định dạng #### [Answer]"
    
    # Fallback to last number
    numbers = re.findall(r"[-+]?\d*\.?\d+", completion)
    if numbers:
        last_num = numbers[-1].replace(",", "")
        return last_num, "Tìm số cuối cùng (Fallback)"
        
    return None, "Không tìm thấy"

with col_right:
    with st.container(border=True):
        st.subheader("Kết Quả So Sánh")
        
        if btn_solve:
            if not user_input.strip():
                st.warning("Vui lòng nhập đề bài!")
            else:
                with st.spinner("Mô hình đang suy nghĩ và tính toán..."):
                    try:
                        # Initialize local client
                        client = LocalClient(model_name=ollama_model)
                        
                        # 1. Run Optimized Prompt (Prompt + User Question)
                        opt_prompt = BEST_TASK_PROMPT + "\n\n" + user_input
                        
                        # Helper function to generate and measure duration
                        def generate_with_timing(prompt_text):
                            start = time.time()
                            res = client.generate(prompt_text, temperature=temperature)
                            elapsed = time.time() - start
                            return res[0].text, elapsed

                        # Use ThreadPoolExecutor to run both in parallel
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                            future_opt = executor.submit(generate_with_timing, opt_prompt)
                            future_base = executor.submit(generate_with_timing, user_input)
                            
                            res_opt, duration_opt = future_opt.result()
                            res_base, duration_base = future_base.result()
                        
                        # Display comparative tabs
                        tab1, tab2 = st.tabs(["Evolved Prompt", "Baseline"])
                        
                        with tab1:
                            st.markdown(f"Thời gian phản hồi: `{duration_opt:.2f}s`")
                            with st.container(border=True):
                                st.write(res_opt)
                        
                        with tab2:
                            st.markdown(f"Thời gian phản hồi:`{duration_base:.2f}s`")
                            with st.container(border=True):
                                st.write(res_base)
                        
                    except Exception as e:
                        st.error(f"Đã xảy ra lỗi khi kết nối tới Ollama: {str(e)}")
                        st.info("Vui lòng kiểm tra xem Ollama đã được khởi động và mô hình đã được tải thành công chưa.")
        else:
            st.info("Vui lòng nhập đề bài và nhấn 'GIẢI NGAY' để xem kết quả tính toán.")
