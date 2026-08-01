# Autonomous Bug Fix Agent

The **Autonomous Bug Fix Agent** is an AI-powered application designed to automatically detect, analyze, and fix bugs in source code. Built using **Python, LangChain, Retrieval-Augmented Generation (RAG), and the Google Gemini API**, the system retrieves relevant programming documentation to generate accurate and context-aware bug fixes. Users can upload source code files, and the application identifies errors, explains the root cause, produces corrected code, and saves the fixed version as a new file. By combining large language models with RAG, the project delivers reliable and efficient debugging assistance while helping developers understand the changes made. This solution improves development productivity, reduces debugging time, enhances code quality, and serves as a practical tool for students, software developers, and programming enthusiasts.
# 🤖 Autonomous Bug Fix Agent

An AI-powered application that automatically detects, analyzes, and fixes bugs in source code using Retrieval-Augmented Generation (RAG), LangChain, and the Gemini API. The system references official Python documentation to generate accurate fixes, explain code changes, and save the corrected version as a new file.

## 🚀 Features

- Upload source code files
- Detect syntax and logical errors
- AI-powered bug analysis
- Automatic bug fixing
- RAG-based documentation retrieval
- Detailed explanation of fixes
- Save corrected code as a new file
- User-friendly interface

## 🛠️ Tech Stack

- Python
- LangChain
- Google Gemini API
- RAG (Retrieval-Augmented Generation)
- FAISS (Vector Database)
- Streamlit
- PyPDF / Documentation Loader

## 📂 Project Structure

```
Autonomous-Bug-Fix-Agent/
│── app.py
│── requirements.txt
│── .env
│── data/
│── docs/
│── vectorstore/
│── uploads/
│── fixed_code/
│── utils/
│── README.md
```

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Autonomous-Bug-Fix-Agent.git
cd Autonomous-Bug-Fix-Agent
```

2. Create a virtual environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure the Gemini API key

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

5. Run the application

```bash
streamlit run app.py
```

## 📖 How It Works

1. Upload a Python source code file.
2. The system analyzes the code for bugs.
3. Relevant documentation is retrieved using RAG.
4. Gemini generates corrected code and explains the fixes.
5. The fixed code is saved as a new file for download.

## 🎯 Use Cases

- Debugging Python applications
- Learning from AI-generated fixes
- Improving code quality
- Developer productivity
- Educational projects

## 📸 Screenshots

Add screenshots of the application interface here.

## 🔮 Future Enhancements

- Multi-language support
- GitHub repository integration
- Unit test generation
- Code optimization suggestions
- VS Code extension
- Docker deployment

## 🤝 Contributing

Contributions are welcome. Fork the repository, create a feature branch, commit your changes, and submit a pull request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Inba K**

B.Tech Artificial Intelligence and Data Science

GitHub: https://github.com/YOUR_USERNAME

---

⭐ If you found this project useful, consider giving it a star!
