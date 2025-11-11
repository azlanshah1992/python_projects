import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
import re
import os
import spacy
import pdfplumber
import docx2txt
import threading
import sys  # <--- FIX 1: Import the sys module

# --- Global NLP Configuration ---
try:
    # Load the small English model
    NLP = spacy.load("en_core_web_sm")
except OSError:
    print("Error: 'en_core_web_sm' model not found. Please run: python -m spacy download en_core_web_sm")
    sys.exit() # <--- FIX 2: Replaced exit() with sys.exit()

# Mock list of skills for keyword matching (expand this heavily for production)
TECH_SKILLS = [
    "Python", "Java", "JavaScript", "SQL", "React", "Angular", "Vue", "Node.js",
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "AWS", "Azure",
    "GCP", "Docker", "Kubernetes", "Linux", "Git", "Jira", "Selenium", "API",
    "NLP", "Data Analysis", "Machine Learning", "Deep Learning", "HTML", "CSS",
    "C++", "C#", "Spark", "Kafka", "Tableau", "Power BI", "R", "Figma", "Photoshop",
    "Illustrator", "Canva", "Blender", "AutoCAD", "SketchUp", "UI/UX Design",
    "3D Modeling", "Video Editing", "Premiere Pro", "After Effects", "DaVinci Resolve",
    "Cybersecurity", "Ethical Hacking", "Penetration Testing", "Network Security",
    "Firewalls", "VPN", "SIEM", "ISO 27001", "SOC 2", "Risk Assessment",
    "Incident Response", "DevOps", "CI/CD", "Terraform", "Ansible", "Prometheus",
    "Grafana", "Nagios", "Bash", "Shell Scripting", "PowerShell", "Windows Server",
    "VMware", "Hyper-V", "Active Directory", "Exchange Server", "DNS", "DHCP",
    "Routing", "Switching", "Fortinet", "Cisco", "Firewall Management", "VPN Tunneling",
    "Cloud Security", "Server Administration", "Virtualization", "Storage Management",
    "Salesforce", "HubSpot", "Zoho", "CRM Management", "ERP Systems", "SAP",
    "Oracle", "QuickBooks", "Tally", "Excel", "Google Sheets", "Financial Modeling",
    "Accounting", "Taxation", "Auditing", "Bookkeeping", "Payroll Management",
    "Business Analysis", "Requirements Gathering", "Project Management",
    "Agile", "Scrum", "Kanban", "Waterfall", "Stakeholder Management",
    "Change Management", "Risk Management", "Time Management", "Budgeting",
    "Leadership", "Team Management", "Communication", "Presentation",
    "Negotiation", "Conflict Resolution", "Problem Solving", "Decision Making",
    "Critical Thinking", "Creativity", "Emotional Intelligence", "Adaptability",
    "Customer Service", "Technical Support", "Helpdesk", "Troubleshooting",
    "Remote Support", "ITIL", "ServiceNow", "Zendesk", "Ticketing Systems",
    "Marketing", "Digital Marketing", "SEO", "SEM", "Google Ads", "Meta Ads",
    "Email Marketing", "Content Marketing", "Copywriting", "Brand Strategy",
    "Social Media Marketing", "Influencer Marketing", "Affiliate Marketing",
    "Market Research", "Public Relations", "Advertising", "Sales Strategy",
    "Lead Generation", "CRM Automation", "E-commerce", "Shopify", "WooCommerce",
    "WordPress", "Dropshipping", "Customer Retention", "UX Research",
    "Data Visualization", "Dashboarding", "Business Intelligence",
    "ETL Pipelines", "Data Warehousing", "Big Data", "Data Engineering",
    "Statistics", "Mathematics", "Predictive Analytics", "Forecasting",
    "Artificial Intelligence", "Computer Vision", "Reinforcement Learning",
    "Chatbots", "OpenAI API", "LangChain", "LLMs", "Prompt Engineering",
    "Blockchain", "Smart Contracts", "Solidity", "Web3", "DeFi", "NFTs",
    "Cryptocurrency", "MetaMask", "Ethereum", "Bitcoin", "FinTech",
    "Payment Gateways", "Trading", "Forex", "Stock Analysis", "Portfolio Management",
    "Investment Strategy", "Financial Planning", "Economics", "Business Strategy",
    "Operations Management", "Supply Chain", "Procurement", "Logistics",
    "Inventory Management", "Warehouse Management", "Manufacturing",
    "Quality Control", "Lean Six Sigma", "ISO Standards", "Health and Safety",
    "Environmental Management", "Sustainability", "Energy Management",
    "Solar Systems", "Electrical Design", "Mechanical Design", "Civil Engineering",
    "Structural Analysis", "Construction Management", "Blueprint Reading",
    "Architecture", "Urban Planning", "GIS Mapping", "Surveying",
    "Healthcare Management", "Medical Billing", "Health Informatics",
    "Patient Data Management", "Telemedicine", "Nursing", "Pharmacy",
    "Public Health", "Nutrition", "Psychology", "Counseling",
    "Education", "Teaching", "Curriculum Design", "E-learning",
    "Instructional Design", "LMS Management", "Research", "Report Writing",
    "Grant Writing", "Academic Writing", "Creative Writing", "Editing",
    "Proofreading", "Translation", "Transcription", "Subtitling",
    "Voice Over", "Music Production", "Sound Engineering",
    "Photography", "Cinematography", "Lighting Design", "Script Writing",
    "Event Planning", "Hospitality", "Customer Experience",
    "Travel Management", "Real Estate", "Property Management",
    "Negotiation", "Public Speaking", "Team Collaboration",
    "Entrepreneurship", "Startup Management", "Innovation",
    "Product Management", "Go-to-Market Strategy", "Business Development",
    "Partnerships", "Legal Compliance", "Contract Management", "Policy Writing",
    "HR Management", "Recruitment", "Talent Acquisition", "Payroll",
    "Performance Management", "Employee Engagement", "Training & Development",
    "Remote Work Tools", "Slack", "Zoom", "Microsoft Teams", "Notion",
    "Trello", "Asana", "Miro", "Confluence", "Google Workspace",
    "Data Privacy", "GDPR Compliance", "Ethics", "Corporate Governance"
]

# --- Core Extraction Functions ---

def extract_text_from_file(filepath):
    """Handles text extraction from PDF and DOCX files."""
    text = ""
    file_extension = os.path.splitext(filepath)[1].lower()

    if file_extension == ".pdf":
        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            return f"Error reading PDF: {e}"

    elif file_extension == ".docx":
        try:
            text = docx2txt.process(filepath)
        except Exception as e:
            return f"Error reading DOCX: {e}"

    elif file_extension == ".txt":
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            return f"Error reading TXT: {e}"

    else:
        return f"Unsupported file type: {file_extension}"

    return text


def extract_entities(resume_text):
    """
    Performs NLP and Regex analysis to extract key entities (Email, Phone, Skills).
    """
    if resume_text.startswith("Error"):
        return {"Skills": ["Extraction Error"], "Email": "N/A", "Phone": "N/A"}

    # 1. Regex Extraction for Contact Info
    email = re.search(r"[\w\.-]+@[\w\.-]+", resume_text)
    phone = re.search(r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", resume_text)

    # 2. Skill Extraction (Keyword Matching)
    found_skills = set()
    doc = NLP(resume_text.lower())

    for skill in TECH_SKILLS:
        # Check if the skill word or phrase is present in the text
        if skill.lower() in doc.text:
            found_skills.add(skill)

    # Optional: Use spaCy's built-in Named Entity Recognition (NER) for 'ORG' or 'PERSON'
    # for name extraction, though direct keyword matching is simpler for skills.

    return {
        "Skills": sorted(list(found_skills)),
        "Email": email.group(0) if email else "Not Found",
        "Phone": phone.group(0) if phone else "Not Found"
    }


# --- Tkinter GUI Application ---

class ResumeExtractorApp:
    def __init__(self, master):
        self.master = master
        master.title("Resume Skill Extractor (NLP Demo)")
        master.geometry("800x600")
        master.resizable(False, False)

        # Style Configuration
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TLabel', font=('Arial', 10), padding=2)

        self.filepath = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready. Select a resume file to analyze.")

        self.create_widgets()

    def create_widgets(self):

        # --- File Selection Frame ---
        file_frame = ttk.Frame(self.master, padding="10 10 10 10")
        file_frame.pack(fill='x')

        ttk.Label(file_frame, text="File Path:").pack(side='left', padx=5)
        ttk.Entry(file_frame, textvariable=self.filepath, width=60, state='readonly').pack(side='left', fill='x',
                                                                                           expand=True, padx=5)

        self.select_btn = ttk.Button(file_frame, text="Select Resume (PDF/DOCX)", command=self.select_file)
        self.select_btn.pack(side='left', padx=5)

        self.analyze_btn = ttk.Button(file_frame, text="Analyze Resume", command=self.start_analysis_thread,
                                      state=tk.DISABLED)
        self.analyze_btn.pack(side='left', padx=5)

        # --- Main Content Frame (Results and Raw Text) ---
        main_frame = ttk.Frame(self.master, padding="10 0 10 10")
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Result Panel (Top Half)
        result_frame = ttk.LabelFrame(main_frame, text="Extracted Entities", padding="10")
        result_frame.grid(row=0, column=0, sticky='nsew', pady=10)
        result_frame.columnconfigure(1, weight=1)

        # Result Labels
        ttk.Label(result_frame, text="Email:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.email_label = ttk.Label(result_frame, text="N/A", foreground='blue')
        self.email_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        ttk.Label(result_frame, text="Phone:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.phone_label = ttk.Label(result_frame, text="N/A", foreground='blue')
        self.phone_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        ttk.Label(result_frame, text="--- Detected Skills ---", font=('Arial', 10, 'bold')).grid(row=2, column=0,
                                                                                                 columnspan=2,
                                                                                                 sticky='w',
                                                                                                 pady=(10, 5))

        self.skill_list_text = ScrolledText(result_frame, wrap='word', height=5, width=80, state='disabled',
                                            relief=tk.SUNKEN)
        self.skill_list_text.grid(row=3, column=0, columnspan=2, sticky='ew')

        # Raw Text Panel (Bottom Half)
        raw_text_frame = ttk.LabelFrame(main_frame, text="Raw Resume Text", padding="5")
        raw_text_frame.grid(row=1, column=0, sticky='nsew')

        self.raw_text_display = ScrolledText(raw_text_frame, wrap='word', state='disabled', font=('Courier New', 9))
        self.raw_text_display.pack(fill='both', expand=True, padx=5, pady=5)

        # --- Status Bar ---
        status_bar = ttk.Label(self.master, textvariable=self.status_text, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side=tk.BOTTOM, fill='x')

    # --- Event Handlers ---

    def select_file(self):
        f_types = [('Resume files', ['*.pdf', '*.docx', '*.txt'])]
        filename = filedialog.askopenfilename(filetypes=f_types)
        if filename:
            self.filepath.set(filename)
            self.analyze_btn.config(state=tk.NORMAL)
            self.status_text.set(f"File selected: {os.path.basename(filename)}. Ready for analysis.")
            self.clear_results()

    def clear_results(self):
        """Resets the results display fields."""
        self.email_label.config(text="N/A")
        self.phone_label.config(text="N/A")

        self.skill_list_text.config(state='normal')
        self.skill_list_text.delete('1.0', tk.END)
        self.skill_list_text.config(state='disabled')

        self.raw_text_display.config(state='normal')
        self.raw_text_display.delete('1.0', tk.END)
        self.raw_text_display.config(state='disabled')

    def start_analysis_thread(self):
        """Starts the heavy processing in a separate thread."""
        filepath = self.filepath.get()
        if not filepath:
            self.status_text.set("Error: Please select a file first.")
            return

        self.analyze_btn.config(state=tk.DISABLED, text="Analyzing...")
        self.select_btn.config(state=tk.DISABLED)
        self.clear_results()
        self.status_text.set("Starting text extraction (this may take a few seconds)...")

        # Start processing in a background thread
        processing_thread = threading.Thread(target=self.run_analysis, args=(filepath,))
        processing_thread.start()

    def run_analysis(self, filepath):
        """The main execution function run in the background thread."""
        try:
            # 1. Extract Text
            resume_text = extract_text_from_file(filepath)

            # Update GUI with raw text display
            self.master.after(0, lambda: self.display_raw_text(resume_text))
            self.master.after(0, lambda: self.status_text.set("Text extracted. Performing NLP skill recognition..."))

            # 2. Extract Entities
            entities = extract_entities(resume_text)

            # Update GUI with final results
            self.master.after(0, lambda: self.display_results(entities))
            self.master.after(0, lambda: self.status_text.set("✅ Analysis complete!"))

        except Exception as e:
            error_message = f"Critical Error: {e}"
            print(error_message)
            self.master.after(0, lambda: self.status_text.set(error_message))

        finally:
            self.master.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL, text="Analyze Resume"))
            self.master.after(0, lambda: self.select_btn.config(state=tk.NORMAL))

    def display_raw_text(self, text):
        """Updates the raw text area on the GUI (main thread)."""
        self.raw_text_display.config(state='normal')
        self.raw_text_display.insert(tk.END, text)
        self.raw_text_display.config(state='disabled')

    def display_results(self, entities):
        """Updates the result labels and skill list (main thread)."""
        self.email_label.config(text=entities["Email"])
        self.phone_label.config(text=entities["Phone"])

        self.skill_list_text.config(state='normal')
        if entities["Skills"]:
            skill_output = "\n".join([f"- {s}" for s in entities["Skills"]])
            self.skill_list_text.insert(tk.END, skill_output)
        else:
            self.skill_list_text.insert(tk.END, "No common skills detected.")
        self.skill_list_text.config(state='disabled')


# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeExtractorApp(root)
    root.mainloop()