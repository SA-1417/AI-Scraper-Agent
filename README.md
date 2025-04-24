# 🌐 Universal Web Scraper

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.22.0-red" alt="Streamlit Version">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-green" alt="Supabase">
  <img src="https://img.shields.io/badge/Playwright-Automation-purple" alt="Playwright">
</div>

## 📋 Overview

Universal Web Scraper is a powerful, user-friendly web scraping application that allows you to extract structured data from websites. Built with Streamlit, it provides an intuitive interface for configuring and executing web scraping tasks, with support for pagination, custom field extraction, and data storage in Supabase.

## ✨ Features

- **Intuitive Web Interface**: User-friendly Streamlit dashboard for configuring and executing scraping tasks
- **Custom Field Extraction**: Define specific fields to extract from websites
- **Pagination Support**: Automatically navigate through multi-page websites
- **Data Storage**: Store scraped data in Supabase for easy access and management
- **Markdown Conversion**: Convert HTML content to clean, readable markdown
- **Error Handling**: Robust error handling and retry mechanisms
- **API Integration**: Support for various LLM models for data extraction and processing
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

- **Frontend**: Streamlit, HTML, CSS
- **Backend**: Python 3.8+
- **Web Scraping**: Playwright, html2text
- **Database**: Supabase (PostgreSQL)
- **Data Processing**: Pandas, Pydantic
- **LLM Integration**: LiteLLM, OpenAI, Gemini
- **Deployment**: Docker (optional)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/universal-web-scraper.git
   cd universal-web-scraper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install Playwright browsers**
   ```bash
   playwright install
   ```

### Supabase Setup

1. **[Create a free Supabase account](https://supabase.com/)**
2. **Create a new project** inside Supabase
3. **Create a table** in your project by running the following SQL command in the **SQL Editor**:
   ```sql
   CREATE TABLE IF NOT EXISTS scraped_data (
     id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
     unique_name TEXT NOT NULL,
     url TEXT,
     raw_data JSONB,        
     formatted_data JSONB, 
     pagination_data JSONB,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```
4. **Go to Project Settings → API** and copy:
   - **Supabase URL**
   - **Anon Key**
5. **Update your `.env` file** with these values:
   ```
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```

### Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Access the application** in your web browser at `http://localhost:8501`

## 📝 Usage Guide

1. **Enter URLs**: Input the URLs you want to scrape in the sidebar
2. **Configure Fields**: Define the fields you want to extract from each website
3. **Select Model**: Choose the LLM model for data extraction
4. **Start Scraping**: Click the "Start Scraping" button to begin the process
5. **View Results**: See the extracted data in the main panel

## 🔧 Configuration

You can configure the application by:

- Setting API keys in the `.env` file
- Adjusting scraping parameters in the UI
- Modifying the `config.py` file for advanced settings

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Playwright](https://playwright.dev/) for the browser automation
- [Supabase](https://supabase.com/) for the database backend
- [html2text](https://github.com/Alir3z4/html2text) for HTML to Markdown conversion