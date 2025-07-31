import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import difflib
import re

try:
    import pdfplumber
    pdf_ok = True
except ImportError:
    pdf_ok = False

class ResumeParserApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Resume Parser & Company Matcher")
        self.root.geometry("820x750")

        # Font variables for dynamic theme
        self.header_font = ("Segoe UI", 19, "bold")
        self.button_font = ("Segoe UI", 11, "bold")

        self.theme = "light"
        self.init_style()
        self.default_companies()
        self.company_df = pd.DataFrame(self.company_dataset)
        self.create_widgets()

    def init_style(self):
        self.style = ttk.Style()
        self.set_theme("light")

    def set_theme(self, theme):
        self.theme = theme
        self.colors = {
            "light": {"bg": "#f3f8fd", "fg": "#222", "section_fg": "#1976d2", "result_bg": "#e3f2fd", "txt_fg": "#191919",
                      "entry_bg": "#fff"},
            "dark":  {"bg": "#111827", "fg": "#fff", "section_fg": "#97cdf3", "result_bg": "#232b35", "txt_fg": "#fff",
                      "entry_bg": "#1c2632"},
        }[theme]
        c = self.colors
        self.root.configure(bg=c['bg'])
        self.style.configure("TFrame", background=c['bg'])
        self.style.configure("TLabel", background=c['bg'], foreground=c['fg'], font=("Segoe UI", 11))
        self.style.configure("Section.TLabel", foreground=c['section_fg'], background=c['bg'], font=("Segoe UI", 13, "bold"))
        self.style.configure("Status.TLabel", background=c['bg'], foreground="#ff4444", font=("Segoe UI", 11, "bold"))
        self.style.configure("TEntry", font=("Segoe UI", 11), fieldbackground=c["entry_bg"], background=c["entry_bg"])
        self.style.map("TButton",
                       background=[("active", "#1565C0"), ("!active", "#2d7fff")],
                       foreground=[("pressed", "#fff"), ("active", "#fff")])

        # Update fonts for header and buttons for the theme
        if self.theme == "light":
            self.header_font = ("Segoe UI", 19, "bold")
            self.button_font = ("Segoe UI", 11, "bold")
        else:
            self.header_font = ("Segoe UI", 19, "normal")
            self.button_font = ("Segoe UI", 11, "normal")
        self.style.configure("Action.TButton", font=self.button_font)
        try:
            self.header_label.config(font=self.header_font)
        except AttributeError:
            pass

    def toggle_theme(self):
        self.set_theme("dark" if self.theme == "light" else "light")
        self.update_text_style()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        # Header with dynamic font
        self.header_label = ttk.Label(main, text="Resume Parser + Company Matcher", font=self.header_font)
        self.header_label.pack(pady=(5, 16))

        # Input type selection
        input_type_frame = ttk.Frame(main)
        input_type_frame.pack(anchor="w", pady=(0, 10))
        ttk.Label(input_type_frame, text="Input Type:", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.input_type = tk.StringVar(value="manual")
        r1 = ttk.Radiobutton(input_type_frame, text="Manual", value="manual", variable=self.input_type, command=self.handle_input_type)
        r2 = ttk.Radiobutton(input_type_frame, text="PDF File", value="pdf", variable=self.input_type, command=self.handle_input_type)
        r1.grid(row=0, column=1)
        r2.grid(row=0, column=2)

        # Form container with stacked frames:
        form_container = ttk.Frame(main, style="TFrame")
        form_container.pack(fill="x", pady=(0, 8), padx=2)
        self.form_container = form_container

        # --- Manual form section ---
        manual_form = ttk.LabelFrame(form_container, text="Your Resume Details", padding=12)
        self.manual_form = manual_form
        self.fields = [
            ("Name", "name"), ("Current Address", "address"),
            ("Phone (10 digits)", "phone"), ("Email", "email"),
            ("Qualification", "qual"), ("Job Position", "position"),
            ("Skills (comma separated)", "skills"),
            ("Certifications (comma separated)", "certs"),
            ("Education", "education"),
            ("Languages (comma separated)", "langs"),
        ]
        self.entries = {}
        for i, (label, key) in enumerate(self.fields):
            ttk.Label(manual_form, text=label + ":").grid(row=i, column=0, sticky="e", pady=2, padx=3)
            entry = ttk.Entry(manual_form, width=37)
            entry.grid(row=i, column=1, sticky="w", pady=2, padx=(0, 3))
            self.entries[key] = entry
        manual_form.pack(fill="x")

        # --- PDF input section ---
        pdf_form = ttk.LabelFrame(form_container, text="Select PDF Resume", padding=12)
        self.pdf_form = pdf_form
        self.pdf_path = tk.StringVar(value="")
        pdf_controls = ttk.Frame(pdf_form)
        pdf_controls.pack(anchor="w", pady=4)
        self.pdf_label = ttk.Label(pdf_controls, text="", foreground="#e87633")
        self.pdf_label.pack(side="left", padx=(4, 5))
        self.btn_pdf = ttk.Button(pdf_controls, text="Select PDF", command=self.select_pdf)
        self.btn_pdf.pack(side="left")
        pdf_form.pack_forget()

        # --- Action buttons with ttk.Style ---
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=(0, 12))
        self.action_buttons = []  # Store for dynamic styling

        btn_parse = ttk.Button(btn_frame, text="Parse Resume", style="Action.TButton", command=self.parse_resume)
        btn_clear = ttk.Button(btn_frame, text="Clear", style="Action.TButton", command=self.clear_all)
        btn_help = ttk.Button(btn_frame, text="Help", style="Action.TButton", command=self.show_help)
        btn_theme = ttk.Button(btn_frame, text="Theme", style="Action.TButton", command=self.toggle_theme)
        btn_import = ttk.Button(btn_frame, text="Import Companies", style="Action.TButton", command=self.import_company_csv)

        self.action_buttons = [btn_parse, btn_clear, btn_help, btn_theme, btn_import]
        for idx, btn in enumerate(self.action_buttons):
            btn.grid(row=0, column=idx, padx=7)

        # --- Status / feedback ---
        self.status_var = tk.StringVar(value="")
        ttk.Label(main, textvariable=self.status_var, style="Status.TLabel").pack()

        # --- Parsed data section ---
        ttk.Label(main, text="Parsed Resume Data", style="Section.TLabel").pack(pady=(10, 2))
        self.parsed_text = tk.Text(main, height=7, font=("Segoe UI", 10), relief="groove", wrap="word",
                                   bd=0, padx=8, pady=4)
        self.parsed_text.pack(fill="x", padx=3)
        self.parsed_text.config(state="disabled")
        self.update_text_style()

        # --- Company results ---
        ttk.Label(main, text="Best Matching Companies", style="Section.TLabel").pack(pady=(14, 2))
        canvas = tk.Canvas(main, height=180, bg="#fcfcfc" if self.theme == "light" else "#151920", highlightthickness=1)
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        company_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=company_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=(4, 12))
        scrollbar.pack(side="right", fill="y")
        self.company_result_frame = company_frame
        company_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # --- Resume tips ---
        ttk.Label(main, text="Resume Feedback & Tips", style="Section.TLabel").pack(pady=(6, 1))
        self.tips_label = ttk.Label(main, text="", wraplength=650, background=self.colors['result_bg'], anchor="w", font=("Segoe UI", 10))
        self.tips_label.pack(fill="x", padx=7, ipady=3)

        self.handle_input_type()

    def update_text_style(self):
        c = self.colors
        if self.theme == "light":
            font = ("Segoe UI", 10, "bold")
        else:
            font = ("Segoe UI", 10, "normal")
        self.parsed_text.config(
            bg=c['result_bg'],
            fg=c['txt_fg'],
            insertbackground=c['txt_fg'],
            font=font
        )

    def show_help(self):
        msg = (
            "RESUME PARSER HELP\n"
            "- Choose Manual entry or PDF parsing.\n"
            "- Import company data as CSV (columns: Company Name, Designation, Salary Range, Skills)\n"
            "- See company suggestions ranked by skill match score.\n"
            "- Only the last 3 digits of your phone will be shown in results.\n"
            "- Use Theme to switch between light/dark mode.\n"
        )
        messagebox.showinfo("Help", msg)

    def clear_all(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.status_var.set("")
        self.parsed_text.config(state="normal")
        self.parsed_text.delete('1.0', tk.END)
        self.parsed_text.config(state="disabled")
        for widget in self.company_result_frame.winfo_children():
            widget.destroy()
        self.pdf_path.set("")
        self.pdf_label.config(text="")
        self.tips_label.config(text="")

    def handle_input_type(self):
        t = self.input_type.get()
        if t == "manual":
            self.manual_form.pack(fill="x")
            self.manual_form.lift()
            self.pdf_form.pack_forget()
        elif t == "pdf":
            self.pdf_form.pack(fill="x")
            self.pdf_form.lift()
            self.manual_form.pack_forget()
        else:
            self.manual_form.pack_forget()
            self.pdf_form.pack_forget()

    def select_pdf(self):
        if not pdf_ok:
            self.status_var.set("pdfplumber is not installed (pip install pdfplumber)")
            return
        path = filedialog.askopenfilename(title="Select Resume PDF", filetypes=[("PDF Files", "*.pdf")])
        self.pdf_path.set(path or "")
        self.pdf_label.config(text="Selected: " + (path.split("/")[-1] if path else ""))

    def default_companies(self):
        self.company_dataset = {
            'Company Name': [
                'Tech Innovators', 'Global Enterprises', 'Creative Solutions', 'Innovative Coders', 'Digital Soft',
                'Future Tech', 'Alpha Corp', 'Visionary Enterprises', 'Bright Horizons', 'Smart Solutions',
                'NextGen Tech', 'Prime Strategies', 'Global Vision', 'Tech Wizards', 'Digital Pioneers'
            ],
            'Designation': [
                'Project Manager', 'PR Manager', 'Team Leader', 'Time Mgmt Consultant', 'Leadership Coach',
                'Operations Manager', 'Marketing Specialist', 'Product Manager', 'HR Specialist', 'Business Analyst',
                'Software Engineer', 'Consultant', 'Marketing Manager', 'IT Specialist', 'Lead Developer'
            ],
            'Salary Range': [
                '$60,000-$80,000', '$50,000-$70,000', '$70,000-$90,000', '$55,000-$75,000', '$40,000-$60,000',
                '$50,000-$70,000', '$55,000-$75,000', '$60,000-$85,000', '$45,000-$65,000', '$55,000-$80,000',
                '$65,000-$95,000', '$50,000-$80,000', '$60,000-$85,000', '$70,000-$100,000', '$55,000-$75,000'
            ],
            'Skills': [
                'Project Management, Leadership, Time Management',
                'Public Relations, Effective Communication, Critical Thinking',
                'Teamwork, Leadership, Time Management',
                'Time Management, Leadership, Critical Thinking',
                'Leadership, Teamwork, Project Management',
                'Operations Management, Leadership, Teamwork',
                'Marketing, Effective Communication, Strategic Planning',
                'Product Management, Project Management, Leadership',
                'Human Resources, Team Management, Conflict Resolution',
                'Business Analysis, Strategic Planning, Communication',
                'Software Development, Java, Problem-Solving',
                'Consulting, Strategy, Leadership',
                'Marketing Strategy, Communication, Digital Marketing',
                'IT Support, Troubleshooting, Customer Service',
                'Software Development, Leadership, Agile'
            ]
        }

    def import_company_csv(self):
        path = filedialog.askopenfilename(title="Select Company CSV",
                                          filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
            req_cols = {'Company Name', 'Designation', 'Salary Range', 'Skills'}
            if not req_cols.issubset(df.columns):
                raise Exception()
            self.company_df = df
            self.status_var.set("Company list imported.")
        except Exception:
            self.status_var.set("CSV must have: Company Name, Designation, Salary Range, Skills")

    def parse_resume(self):
        self.status_var.set("")
        t = self.input_type.get()
        if t == "manual":
            vals = {k: self.entries[k].get().strip() for _, k in self.fields}
            missing = [label for label, k in self.fields if not vals[k] and k not in ["email"]]
            if missing:
                self.status_var.set(f"Fill required: {', '.join(missing)}")
                return
            if not (len(vals['phone']) == 10 and vals['phone'].isdigit()):
                self.status_var.set("Phone must be 10 digits")
                return
            if vals['email'] and not self.is_valid_email(vals['email']):
                self.status_var.set("Invalid email format")
                return
            pdata = (
                f"Name: {vals['name']}\n"
                f"Address: {vals['address']}\n"
                f"Phone: {self.mask_phone(vals['phone'])}\n"
                f"Email: {vals['email']}\n"
                f"Qualification: {vals['qual']}\n"
                f"Position: {vals['position']}\n"
                f"Skills: {vals['skills']}\n"
                f"Certifications: {vals['certs']}\n"
                f"Education: {vals['education']}\n"
                f"Languages: {vals['langs']}\n"
            )
            skills = [s.strip().lower() for s in vals['skills'].split(",") if s.strip()]
            certs = vals['certs'].strip()
            self.display_resume(pdata)
            self.show_company_matches(skills)
            self.tips_label.config(text=self.resume_improvement_tips(skills, certs))
        elif t == "pdf":
            if not pdf_ok:
                self.status_var.set("pdfplumber is not installed (pip install pdfplumber)")
                return
            if not self.pdf_path.get():
                self.status_var.set("No PDF file selected")
                return
            try:
                text = ""
                with pdfplumber.open(self.pdf_path.get()) as pdf:
                    for page in pdf.pages:
                        text += (page.extract_text() or "") + "\n"
                name = self.extract_name(text)
                phone = self.mask_phone(self.find_phone(text))
                email = self.find_email(text)
                skills = self.extract_skills(text)
                pdata = (f"Name: {name}\nPhone: {phone}\nEmail: {email}\nSkills: {', '.join(skills)}")
                certs = ""  # Not parsed
                self.display_resume(pdata)
                self.show_company_matches(skills)
                self.tips_label.config(text=self.resume_improvement_tips(skills, certs))
            except Exception:
                self.status_var.set("PDF extraction error")

    def display_resume(self, text):
        self.parsed_text.config(state="normal")
        self.parsed_text.delete('1.0', tk.END)
        self.parsed_text.insert(tk.END, text)
        self.parsed_text.config(state="disabled")
        self.update_text_style()

    def show_company_matches(self, user_skills):
        for widget in self.company_result_frame.winfo_children():
            widget.destroy()
        df = self.company_df
        matched = []
        for _, row in df.iterrows():
            required = [s.strip().lower() for s in row["Skills"].split(",")]
            matches = set()
            for rs in required:
                for us in user_skills:
                    if rs == us or (difflib.SequenceMatcher(None, rs, us).ratio() > 0.7):
                        matches.add(rs)
            score = int(100 * len(matches) / max(1, len(required)))
            if matches:
                salary = row["Salary Range"] if score > 60 else "Ask HR"
                text = (f"{row['Company Name']}\n"
                        f"Role: {row['Designation']} | Salary: {salary} | Match: {score}%\n"
                        f"Required: {row['Skills']}")
                lab = ttk.Label(self.company_result_frame, text=text,
                                wraplength=720, anchor="w", justify="left",
                                background=self.colors['result_bg'])
                lab.pack(anchor="w", pady=4, ipadx=4, ipady=3, fill="x")
                matched.append(row['Company Name'])
        if not matched:
            ttk.Label(self.company_result_frame, text="No relevant company found.", foreground="#ed2b2b").pack(anchor="w", pady=5)

    # --- NLP, Extraction, Tips ---
    def mask_phone(self, phone):
        s = str(phone)
        if len(s) >= 3:
            return "*******" + s[-3:]
        return phone

    def is_valid_email(self, email):
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    def resume_improvement_tips(self, skills, certifications):
        tips = []
        if not skills or len(skills) < 3:
            tips.append("Tip: List more relevant skills to improve your matching opportunities.")
        if not certifications or certifications.strip() == "":
            tips.append("Tip: Highlighting certifications will make your profile stand out.")
        if not tips:
            return "Looks good! 👍"
        return " ".join(tips)

    def find_phone(self, text):
        match = re.search(r"\b\d{10}\b", text)
        return match.group(0) if match else ""

    def find_email(self, text):
        match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
        return match.group(0) if match else ""

    def extract_name(self, text):
        lines = text.splitlines()
        for line in lines:
            if len(line.split()) >= 2 and len(line) < 48:
                return line.strip()
        return "(?)"

    def extract_skills(self, text):
        m = re.search(r'skills?\s*:\s*(.*)', text, re.I)
        if m:
            raw = m.group(1)
            return [x.strip().lower() for x in raw.split(",")[:8]]
        common_skills = {"python", "java", "excel", "leadership", "marketing", "agile", "project", "management", "strategy"}
        words = re.findall(r'\b([A-Za-z]{4,})\b', text)
        return [w.lower() for w in words if w.lower() in common_skills][:7]

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ResumeParserApp().run()
