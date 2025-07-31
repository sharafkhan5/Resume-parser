# 🧠 Resume Parser & Company Matcher

A powerful **Tkinter-based desktop app** that parses resumes either manually or from PDF files, matches them with companies based on required skills, and provides **intelligent suggestions and resume improvement tips**.

---

## 🔍 Features

- 📝 Manual Resume Form OR 📄 PDF Resume Parser
- 📊 Company Matching System based on skill relevance
- 🌑 Light/Dark Theme Toggle
- 📥 CSV Import for Company Data
- 📌 Tips for Resume Improvement
- ✅ Skill Matching Score
- 🔐 Masked Phone Numbers for Privacy
- 📚 PDF Text Extraction with `pdfplumber`
- 💡 User-Friendly GUI using Tkinter

---

## 🖼️ Preview

| Manual Entry Form | PDF Upload | Company Matches |
|-------------------|------------|------------------|
| ![Manual](docs/manual_form.png) | ![PDF](docs/pdf_input.png) | ![Matches](docs/matches.png) |

---

## 🚀 Getting Started

### 🔧 Requirements

- Python 3.7+
- `pdfplumber`
- `pandas`
- `tkinter` (comes with Python)

Install required packages:

```bash
pip install pdfplumber pandas
```

---

## ▶️ How to Run

```bash
python miniproject.py
```

---

## 🏢 Company CSV Format

To import your own company dataset, prepare a CSV with the following columns:

- Company Name
- Designation
- Salary Range
- Skills (comma-separated)

Example:
```csv
Company Name,Designation,Salary Range,Skills
Tech Innovators,Software Engineer,$60,000-$80,000,Python, Java, Leadership
```

---

## 🎯 How Matching Works

- Uses approximate string matching (`difflib`) to compare skills.
- Computes a matching score out of 100.
- If score > 60%, full salary is shown; else "Ask HR".

---

## 💡 Resume Tips Engine

- Suggests adding skills or certifications if few/missing.
- Gives a basic resume quality verdict.

---

## ✨ Highlights

- Clean UI with Tkinter + ttk themes
- PDF parsing with `pdfplumber`
- Smart company matching logic

---

## 🧑‍💻 Author

Mohammed Husain Farhan  
🔗 [LinkedIn](https://www.linkedin.com/in/mohammed-husain-farhan/)  
🔗 [GitHub](https://github.com/HusainFarhan)

---

## 📜 License

This project is open-source and free to use for educational and personal use.
