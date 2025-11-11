# 🎯 Fiverr Market Analyzer

**A Python-powered data analytics tool that scrapes, analyzes, and visualizes Fiverr market trends — helping freelancers identify profitable niches and pricing insights.**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![BeautifulSoup](https://img.shields.io/badge/Scraping-BeautifulSoup-orange)
![Matplotlib](https://img.shields.io/badge/Visualization-Matplotlib-yellow)
![Seaborn](https://img.shields.io/badge/Analytics-Seaborn-blueviolet)
![Automation](https://img.shields.io/badge/Automation-PyInstaller-lightgrey)

---

## 🚀 **Overview**

The **Fiverr Market Analyzer** is an end-to-end desktop application that:
- Scrapes Fiverr gigs for a chosen keyword (e.g., “Python developer”, “Data analysis”)
- Cleans and processes market data
- Generates a **comprehensive PDF report** including:
  - Top keywords and market trends  
  - Pricing distribution and competition  
  - Seller productivity analysis  
  - Niche profitability breakdowns

This project combines **Python scripting, data analysis, visualization, and GUI automation**, packaged for end users via **PyInstaller**.

---

## 🧩 **Key Features**

✅ **GUI Application (Tkinter)** – Intuitive interface to input keywords, output paths, and progress tracking.  
✅ **Live Web Scraping** – Extracts data directly from Fiverr search results using `requests` + `BeautifulSoup`.  
✅ **Automated Data Cleaning** – Parses and normalizes price data with regex and pandas.  
✅ **Market Insights & Visualization** – Generates charts for trends, competition, and pricing with `matplotlib` and `seaborn`.  
✅ **PDF Report Generation** – Automatically exports all analysis visuals and insights into a clean, shareable PDF file.  
✅ **Multi-threaded Execution** – Keeps the UI responsive during data scraping and analysis.  
✅ **Error Handling & Progress Feedback** – Provides real-time feedback during scraping and analysis.  

---

## 🧠 **Tech Stack**

| Category | Tools & Libraries |
|-----------|------------------|
| GUI | `Tkinter`, `ttk` |
| Web Scraping | `requests`, `BeautifulSoup4` |
| Data Processing | `pandas`, `numpy`, `re` |
| Visualization | `matplotlib`, `seaborn` |
| Reporting | `PdfPages` (matplotlib backend) |
| Automation | `threading`, `PyInstaller` (for packaging) |

---

## 🖥️ **Screenshots**

| GUI Interface | Sample Report |
|----------------|----------------|
| ![App Screenshot](assets/app_gui.gif) | ![Report Sample](assets/PDF_sample.pdf) | ![Report Sample](assets/CSV_sample.csv)

---

## ⚙️ **How It Works**

### 1️⃣ Scraping Phase
- Uses the Fiverr search URL to fetch gig listings for the entered keyword.
- Extracts gig titles, sellers, and prices using `BeautifulSoup`.
- Cleans and stores the raw data into a CSV file.

### 2️⃣ Analysis Phase
- Loads the CSV and processes gig pricing.
- Extracts and counts common niche keywords.
- Calculates pricing statistics (median, Q1, Q3) and competition metrics.

### 3️⃣ Report Generation
- Creates **five detailed visualizations**:
  1. Top 20 Keywords by Gig Volume  
  2. Market Price Distribution  
  3. Price by Niche (Box Plot)  
  4. Competition (Unique Sellers per Keyword)  
  5. Top 10 Sellers by Gig Volume  
- Exports them into a multi-page **PDF report**.

---

## 🧰 **Setup Instructions**

### 🔹 Clone the repository
```bash
git clone https://github.com/yourusername/fiverr-market-analyzer.git
cd fiverr-market-analyzer

