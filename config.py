# config.py

# Browser Configuration
BROWSER_CONFIG = {
    "headless": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
    "ignore_https_errors": True
}

# API Keys and Credentials
API_KEYS = {
    "supabase_url": "your-supabase-url",
    "supabase_key": "your-supabase-key"
}

# Scraping Configuration
SCRAPING_CONFIG = {
    "timeout": 40000,  # milliseconds
    "max_retries": 3,
    "concurrent_limit": 5,
    "wait_time": 2,  # seconds between requests
}

# Fields to extract from each page
EXTRACT_FIELDS = {
    "team": {
        "selectors": [
            "//div[contains(@class, 'team')]",
            "//section[contains(@class, 'people')]",
            "//div[contains(@class, 'about')]"
        ],
        "required": True
    },
    "investment": {
        "selectors": [
            "//div[contains(@class, 'portfolio')]",
            "//section[contains(@class, 'investments')]",
            "//div[contains(@class, 'companies')]"
        ],
        "required": True
    },
    "contact": {
        "selectors": [
            "//div[contains(@class, 'contact')]",
            "//section[contains(@class, 'contact')]"
        ],
        "required": False
    }
}

# Pagination Configuration
PAGINATION_CONFIG = {
    "max_pages": 10,
    "next_page_selector": "//a[contains(@class, 'next')]",
    "page_param": "page"
}

# Rate Limiting
RATE_LIMIT = {
    "requests_per_minute": 30,
    "burst_size": 5
}

# Error Handling
ERROR_HANDLING = {
    "retry_codes": [429, 500, 502, 503, 504],
    "max_retries": 3,
    "backoff_factor": 2
}

# Content Processing
CONTENT_PROCESSING = {
    "min_content_length": 100,
    "max_content_length": 1000000,
    "remove_scripts": True,
    "remove_styles": True,
    "extract_metadata": True
} 