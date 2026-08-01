# Autonomous Bug Fix & Test-Driven Development (TDD) Agent

An end-to-end, production-ready, AI-powered Python web application built with **Streamlit**, **LangChain**, **Google Gemini API**, **RAG (Retrieval-Augmented Generation)**, **ChromaDB**, and **Pytest**.

This system automatically analyzes Python source code using static analysis tools & AST, retrieves context from official Python documentation and best practices using RAG, prompts Google Gemini to explain and fix bugs, displays a side-by-side code diff, generates `pytest` test suites following TDD principles, executes tests with coverage reporting, and exports multi-format reports (PDF, HTML, TXT).

---

## 🌟 Key Features

1. **Python Code Upload**: Drag-and-drop single or multiple `.py` source files.
2. **Static & AST Analysis**: Detects syntax errors, division by zero, infinite loop risks, security vulnerabilities (`eval`, `exec`, hardcoded keys, shell injection), missing docstrings, long functions, duplicate functions, and PEP8 violations.
3. **RAG (Retrieval-Augmented Generation)**: Leverages ChromaDB vector store seeded with official Python guidelines, PEP8 standards, security rules, and error documentation.
4. **AI Bug Fixing & Refactoring**: Generates clean, bug-fixed code saved automatically as `uploads/{filename}_fixed.py` without modifying the original uploaded file.
5. **Side-by-Side Code Comparison**: Interactive diff viewer highlighting added, removed, and modified lines.
6. **Automated TDD Test Suite Generation**: Generates comprehensive `pytest` test cases under `tests/test_{filename}.py`.
7. **Automated Pytest Execution & Coverage**: Programmatically runs `pytest` and `pytest-cov`, displaying pass/fail badges, coverage percentage, and execution latency.
8. **Interactive Visualizations**: Plotly charts for bug severity distributions, category breakdowns, coverage gauges, and metrics.
9. **RAG Code Chatbot**: Interactive real-time chat interface to query your code and Python knowledge base.
10. **Multi-Format Report Export**: Download analysis reports in **PDF**, **HTML**, and **TXT** formats.

---

## 📁 Project Architecture

```
.
├── app.py                      # Main Streamlit Dashboard UI
├── config.py                   # System configuration & environment paths
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env.example                # Environment variables template
├── knowledge_base/             # RAG reference documentation
│   └── python_docs/
│       ├── pep8_guidelines.md
│       ├── python_errors.md
│       ├── security_best_practices.md
│       └── tdd_best_practices.md
├── rag/                        # Retrieval-Augmented Generation module
│   ├── embeddings.py           # Google Generative AI / HuggingFace embeddings
│   ├── vector_store.py         # ChromaDB / FAISS vector database wrapper
│   ├── retriever.py            # Context retriever
│   └── prompts.py              # Custom LangChain prompt templates
├── bug_detection/              # Static Code Analysis
│   ├── ast_analyzer.py         # AST parser for code smells & syntax errors
│   ├── security_checker.py     # Hardcoded secret & security scanner
│   ├── pep8_checker.py         # Formatting & PEP8 rule checker
│   └── bug_detector.py         # Bug analysis aggregator
├── ai/                         # Gemini & LangChain AI Engine
│   ├── gemini_agent.py         # Gemini API client wrapper
│   ├── langchain_pipeline.py   # LangChain RunnableSequence chains
│   └── code_fixer.py           # Refactoring parser & diff compute engine
├── testing/                    # TDD & Execution Engine
│   ├── test_generator.py       # Pytest suite builder
│   ├── test_runner.py          # Subprocess Pytest & Coverage runner
│   └── coverage.py             # Code coverage parser
├── reports/                    # Multi-format report generators
│   ├── txt_report.py           # Plain text report builder
│   ├── html_report.py          # Responsive HTML/CSS report builder
│   └── pdf_report.py           # PDF report generator using ReportLab
└── utils/                      # Utilities
    ├── helpers.py              # File manipulation & diff calculation
    └── logger.py               # Application logging setup
```

---

## 🚀 Quick Start & Installation

### 1. Clone & Navigate to Project Directory
```bash
cd "c:\Users\inbak\OneDrive\Desktop\new"
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`:
```bash
cp .env.example .env
```
Or input your API key directly in the Streamlit sidebar UI at runtime.

### 5. Launch Application
```bash
streamlit run app.py
```

---

## 🧪 Sample Buggy Code Testing

You can test the system by uploading a Python file containing intentional code smells, such as:

```python
import sys, os

def calculate_discount(price, count):
    # Bug 1: Division by zero risk
    average = price / count
    
    # Bug 2: Hardcoded secret
    api_key = "secret_12345_key"
    
    # Bug 3: Unsafe eval
    result = eval("price * count")
    
    # Bug 4: Infinite loop risk
    while True:
        print("processing")
        
    return average
```

The system will automatically detect the bugs, retrieve relevant Python documentation via RAG, rewrite the code safely into `uploads/sample_fixed.py`, generate pytest test cases under `tests/test_sample.py`, run `pytest`, and generate PDF/HTML/TXT reports!
