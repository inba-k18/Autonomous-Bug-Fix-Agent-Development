import os
import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Append project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import UPLOADS_DIR, TESTS_DIR, REPORTS_DIR, GEMINI_API_KEY
from bug_detection.bug_detector import BugDetector
from rag.retriever import RAGRetriever
from ai.langchain_pipeline import AILangChainPipeline
from ai.code_fixer import CodeFixer
from testing.test_generator import TestGenerator
from testing.test_runner import TestRunner
from reports.txt_report import TXTReportGenerator
from reports.html_report import HTMLReportGenerator
from reports.pdf_report import PDFReportGenerator
from utils.helpers import save_file

# ==============================================================================
# STREAMLIT PAGE CONFIG & CUSTOM CSS
# ==============================================================================
st.set_page_config(
    page_title="Autonomous Bug Fix & TDD Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark glassmorphism, metric badges, diff highlighting
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    /* Header Gradient Banner */
    .header-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .header-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
    }

    /* Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-val.green { color: #4ade80; }
    .metric-val.red { color: #f87171; }
    .metric-val.orange { color: #fb923c; }

    /* Side-by-Side Diff Table */
    .diff-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Consolas', monospace;
        font-size: 0.85rem;
        background-color: #0f172a;
        border-radius: 8px;
        overflow: hidden;
    }
    .diff-table td {
        padding: 4px 8px;
        white-space: pre-wrap;
        word-break: break-all;
    }
    .diff-equal { background-color: transparent; color: #cbd5e1; }
    .diff-added { background-color: rgba(34, 197, 94, 0.2); color: #86efac; }
    .diff-removed { background-color: rgba(239, 68, 68, 0.2); color: #fca5a5; }
    .diff-modified { background-color: rgba(234, 179, 8, 0.2); color: #fde047; }
    
    .line-no {
        color: #64748b;
        text-align: right;
        user-select: none;
        width: 40px;
        border-right: 1px solid #334155;
        padding-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files_cache" not in st.session_state:
    st.session_state.uploaded_files_cache = {}

# ==============================================================================
# SIDEBAR CONTROL PANEL
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/code-fork.png", width=64)
    st.title("TDD Agent Control")
    
    # API Key Configuration
    st.subheader("🔑 Gemini API Settings")
    user_api_key = st.text_input(
        "Google Gemini API Key",
        value=GEMINI_API_KEY,
        type="password",
        help="Enter your Google Gemini API Key or configure it in .env file."
    )
    
    if user_api_key:
        st.success("✔ API Key Configured")
    else:
        st.warning("⚠️ Running in Static Mode (No API Key)")

    st.markdown("---")
    
    # File Uploader
    st.subheader("📁 Upload Source Code")
    uploaded_files = st.file_uploader(
        "Choose Python (.py) file(s)",
        type=["py"],
        accept_multiple_files=True,
        help="Drag and drop one or more Python files for automated analysis and TDD fixing."
    )
    
    st.markdown("---")
    
    # Vector DB Control
    st.subheader("📚 RAG Knowledge Base")
    if st.button("🔄 Reindex Knowledge Base"):
        with st.spinner("Indexing Python documentation into ChromaDB..."):
            retriever = RAGRetriever(api_key=user_api_key)
            retriever.vector_manager.build_or_load_vector_store(force_rebuild=True)
            st.success("Vector Store updated!")

# ==============================================================================
# MAIN PAGE HEADER
# ==============================================================================
st.markdown("""
<div class="header-container">
    <div class="header-title">Autonomous Bug Fix & Test-Driven Development (TDD) Agent</div>
    <div class="header-subtitle">
        AI-Powered Python Code Analysis, RAG Documentation Retrieval, Automated Refactoring & Pytest Coverage Execution
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# PROCESSING LOGIC ON FILE UPLOAD
# ==============================================================================
if uploaded_files:
    # Select active file if multi-file uploaded
    selected_filename = st.selectbox(
        "Select Active File to Analyze:",
        options=[f.name for f in uploaded_files]
    )
    
    active_file = next(f for f in uploaded_files if f.name == selected_filename)
    original_code_bytes = active_file.getvalue()
    original_code = original_code_bytes.decode("utf-8", errors="ignore")
    
    # Save uploaded file to uploads directory
    original_filepath = UPLOADS_DIR / active_file.name
    save_file(original_filepath, original_code)

    # Trigger analysis pipeline if file changed or not yet analyzed
    if (st.session_state.analysis_data is None or 
        st.session_state.analysis_data.get("original_filename") != active_file.name):
        
        with st.spinner(f"Analyzing {active_file.name} (AST, Security, RAG, Pytest)..."):
            # 1. Run Bug Detection
            bug_detector = BugDetector(original_code)
            bug_report = bug_detector.run_all_checks()

            # 2. Retrieve RAG Context
            retriever = RAGRetriever(api_key=user_api_key)
            rag_context = retriever.retrieve_context_for_bugs(bug_report, original_code)

            # 3. AI Bug Fixing & Refactoring
            ai_pipeline = AILangChainPipeline(api_key=user_api_key)
            ai_response = ai_pipeline.run_bug_fix_chain(
                original_code=original_code,
                bug_report=str(bug_report["issues"]),
                rag_context=rag_context
            )

            # 4. Save Fixed Code & Compute Diff
            code_fixer = CodeFixer(original_filepath)
            fix_results = code_fixer.process_ai_response(original_code, ai_response)

            # 5. Generate TDD Pytest Suite
            test_gen = TestGenerator(code_fixer.fixed_filepath, api_key=user_api_key)
            test_results_data = test_gen.generate_and_save_tests(fix_results["fixed_code"])

            # 6. Execute Pytest Suite
            test_runner = TestRunner(
                test_filepath=Path(test_results_data["test_filepath"]),
                target_source_filepath=Path(fix_results["fixed_filepath"])
            )
            pytest_execution = test_runner.execute_tests()

            # Store aggregated result in session_state
            st.session_state.analysis_data = {
                "project_name": "Autonomous TDD Agent Project",
                "original_filename": active_file.name,
                "original_filepath": str(original_filepath),
                "original_code": original_code,
                "fixed_filename": fix_results["fixed_filename"],
                "fixed_filepath": fix_results["fixed_filepath"],
                "fixed_code": fix_results["fixed_code"],
                "explanations": fix_results["explanations"],
                "diff_stats": fix_results["diff_stats"],
                "diff_records": fix_results["diff_records"],
                "bug_report": bug_report,
                "rag_context": rag_context,
                "test_filename": test_results_data["test_filename"],
                "test_filepath": test_results_data["test_filepath"],
                "test_code": test_results_data["test_code"],
                "test_results": pytest_execution
            }

            st.success("Analysis and TDD processing complete!")

    data = st.session_state.analysis_data

    # ==============================================================================
    # TABBED INTERFACE LAYOUT
    # ==============================================================================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard Overview",
        "🔍 Bug Detection & RAG",
        "🔄 Side-by-Side Code Diff",
        "🧪 TDD & Pytest Execution",
        "📈 Visualizations",
        "💬 RAG Code Chat",
        "📄 Reports & Export"
    ])

    # ------------------------------------------------------------------------------
    # TAB 1: DASHBOARD OVERVIEW
    # ------------------------------------------------------------------------------
    with tab1:
        st.subheader("📌 Analysis Summary & Key Metrics")
        
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        
        total_bugs = data["bug_report"]["total_issues"]
        crit_bugs = data["bug_report"]["severity_counts"].get("Critical", 0) + data["bug_report"]["severity_counts"].get("High", 0)
        passed_tests = data["test_results"]["passed_count"]
        total_tests = data["test_results"]["total_count"]
        cov_pct = data["test_results"]["coverage_pct"]
        exec_time = data["test_results"]["execution_time_seconds"]

        with m_col1:
            st.markdown(f'<div class="metric-card"><div>Total Issues</div><div class="metric-val {"red" if total_bugs > 0 else "green"}">{total_bugs}</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="metric-card"><div>High/Critical Risks</div><div class="metric-val {"red" if crit_bugs > 0 else "green"}">{crit_bugs}</div></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="metric-card"><div>Pytest Status</div><div class="metric-val {"green" if data["test_results"]["success"] else "red"}">{passed_tests}/{total_tests}</div></div>', unsafe_allow_html=True)
        with m_col4:
            st.markdown(f'<div class="metric-card"><div>Code Coverage</div><div class="metric-val green">{cov_pct}%</div></div>', unsafe_allow_html=True)
        with m_col5:
            st.markdown(f'<div class="metric-card"><div>Execution Time</div><div class="metric-val">{exec_time}s</div></div>', unsafe_allow_html=True)

        st.markdown("### 📄 Uploaded Source Code Preview")
        st.code(data["original_code"], language="python", line_numbers=True)

    # ------------------------------------------------------------------------------
    # TAB 2: BUG DETECTION & RAG CONTEXT
    # ------------------------------------------------------------------------------
    with tab2:
        st.subheader("🚨 Detected Code Smells & Bugs")
        
        issues = data["bug_report"]["issues"]
        if issues:
            for issue in issues:
                sev = issue.get("severity", "Low")
                icon = "🔴" if sev in ("Critical", "High") else ("🟠" if sev == "Medium" else "🔵")
                with st.expander(f"{icon} Line {issue.get('line', '?')} - [{sev}] {issue.get('type', 'Issue')}"):
                    st.write(f"**Category:** {issue.get('category')}")
                    st.write(f"**Description:** {issue.get('message')}")
                    if issue.get("snippet"):
                        st.code(issue.get("snippet"), language="python")
        else:
            st.success("🎉 No bugs or code quality issues detected by static analysis!")

        st.markdown("---")
        st.subheader("📚 Retrieved RAG Documentation Context")
        st.info("The following Python documentation chunks were retrieved to assist Gemini in fixing detected bugs:")
        st.text_area("RAG Context Blocks", value=data["rag_context"], height=250)

        st.markdown("---")
        st.subheader("🤖 Gemini AI Explanation & Refactoring Recommendation")
        st.markdown(data["explanations"])

    # ------------------------------------------------------------------------------
    # TAB 3: SIDE-BY-SIDE CODE DIFF
    # ------------------------------------------------------------------------------
    with tab3:
        st.subheader("🔄 Original Code vs Fixed Code Comparison")
        
        stats = data["diff_stats"]
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        d_col1.metric("Lines Added", f"+{stats['added']}")
        d_col2.metric("Lines Removed", f"-{stats['removed']}")
        d_col3.metric("Lines Modified", stats['modified'])
        d_col4.metric("Total Changes", stats['total_changes'])

        # Display side-by-side diff table
        diff_html = '<table class="diff-table"><thead><tr><th style="width:50%;">Original Code</th><th style="width:50%;">Fixed Code</th></tr></thead><tbody>'
        
        for rec in data["diff_records"]:
            cls = f"diff-{rec['type']}"
            orig_no = f"{rec['orig_line_no']}" if rec['orig_line_no'] else ""
            fixed_no = f"{rec['fixed_line_no']}" if rec['fixed_line_no'] else ""
            
            diff_html += f"""
            <tr class="{cls}">
                <td><span class="line-no">{orig_no}</span> {rec['orig']}</td>
                <td><span class="line-no">{fixed_no}</span> {rec['fixed']}</td>
            </tr>
            """
        diff_html += '</tbody></table>'
        
        st.markdown(diff_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label=f"📥 Download Corrected File ({data['fixed_filename']})",
            data=data["fixed_code"],
            file_name=data["fixed_filename"],
            mime="text/x-python"
        )

    # ------------------------------------------------------------------------------
    # TAB 4: TDD & PYTEST EXECUTION
    # ------------------------------------------------------------------------------
    with tab4:
        st.subheader("🧪 TDD Automated Unit Test Suite")
        
        t_res = data["test_results"]
        if t_res["success"]:
            st.success(f"✔ All {t_res['passed_count']} Pytest Unit Tests Passed Successfully!")
        else:
            st.error(f"✘ {t_res['failed_count']} Test(s) Failed out of {t_res['total_count']}.")

        st.progress(t_res["coverage_pct"] / 100.0, text=f"Code Coverage: {t_res['coverage_pct']}%")

        st.markdown("### Generated Pytest Code")
        st.code(data["test_code"], language="python", line_numbers=True)

        st.download_button(
            label=f"📥 Download Test File ({data['test_filename']})",
            data=data["test_code"],
            file_name=data["test_filename"],
            mime="text/x-python"
        )

        st.markdown("### Pytest Execution Logs")
        st.text_area("Console Output", value=t_res["stdout"], height=250)

    # ------------------------------------------------------------------------------
    # TAB 5: VISUALIZATIONS
    # ------------------------------------------------------------------------------
    with tab5:
        st.subheader("📈 Interactive Project Analytics")
        
        c_col1, c_col2 = st.columns(2)
        
        # Chart 1: Bug Severity Distribution
        with c_col1:
            sev_counts = data["bug_report"]["severity_counts"]
            fig_sev = px.pie(
                names=list(sev_counts.keys()),
                values=list(sev_counts.values()),
                title="Bug Severity Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_sev, use_container_width=True)

        # Chart 2: Bug Category Breakdown
        with c_col2:
            cat_counts = data["bug_report"]["category_counts"]
            if cat_counts:
                fig_cat = px.bar(
                    x=list(cat_counts.keys()),
                    y=list(cat_counts.values()),
                    title="Bugs by Category",
                    labels={"x": "Category", "y": "Count"},
                    color=list(cat_counts.keys())
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No bug categories to plot.")

        # Chart 3: Coverage & Test Outcome Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data["test_results"]["coverage_pct"],
            title={'text': "Test Coverage Percentage"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#38bdf8"},
                'steps': [
                    {'range': [0, 50], 'color': "#7f1d1d"},
                    {'range': [50, 80], 'color': "#7c2d12"},
                    {'range': [80, 100], 'color': "#14532d"}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ------------------------------------------------------------------------------
    # TAB 6: RAG CODE CHAT INTERFACE
    # ------------------------------------------------------------------------------
    with tab6:
        st.subheader("💬 Interactive RAG Code Assistant")
        st.caption("Ask questions about your uploaded code or Python best practices.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_query = st.chat_input("Ask a question about the code or bug fixes...")
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Consulting code & RAG vector store..."):
                    ai_pipeline = AILangChainPipeline(api_key=user_api_key)
                    answer = ai_pipeline.run_chat_chain(
                        question=user_query,
                        code_snippet=data["fixed_code"],
                        rag_context=data["rag_context"]
                    )
                    st.write(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # ------------------------------------------------------------------------------
    # TAB 7: REPORTS & EXPORT
    # ------------------------------------------------------------------------------
    with tab7:
        st.subheader("📄 Generate & Download Analysis Reports")
        
        # Generate all 3 report formats
        txt_path = TXTReportGenerator.generate(data)
        html_path = HTMLReportGenerator.generate(data)
        pdf_path = PDFReportGenerator.generate(data)

        r_col1, r_col2, r_col3 = st.columns(3)
        
        with r_col1:
            st.download_button(
                label="📥 Download Plain Text (.txt) Report",
                data=txt_path.read_text(encoding="utf-8"),
                file_name="TDD_Report.txt",
                mime="text/plain"
            )
        with r_col2:
            st.download_button(
                label="📥 Download HTML (.html) Report",
                data=html_path.read_text(encoding="utf-8"),
                file_name="TDD_Report.html",
                mime="text/html"
            )
        with r_col3:
            st.download_button(
                label="📥 Download PDF (.pdf) Report",
                data=pdf_path.read_bytes(),
                file_name="TDD_Report.pdf",
                mime="application/pdf"
            )

        st.markdown("---")
        st.markdown("### Report Preview (TXT format)")
        st.text_area("Report Content", value=txt_path.read_text(encoding="utf-8"), height=400)

else:
    # Empty State when no file uploaded
    st.info("👆 Please upload a Python (.py) file in the sidebar to begin analysis and TDD fixing.")

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
---
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    Autonomous Bug Fix & Test-Driven Development (TDD) Agent • Built with Streamlit, LangChain, Gemini API, ChromaDB & Pytest
</div>
""", unsafe_allow_html=True)
