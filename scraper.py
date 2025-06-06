# scraper.py

import json
from typing import List, Dict
from pydantic import BaseModel, create_model
from assets import (OPENAI_MODEL_FULLNAME,GEMINI_MODEL_FULLNAME)
from llm_calls import (call_llm_model)
from markdown import read_raw_data
from api_management import get_supabase_client
from utils import  generate_unique_name
from datetime import datetime
from playwright.sync_api import sync_playwright
import time

supabase = get_supabase_client()

SYSTEM_MESSAGE = """You are a web scraping assistant specialized in extracting information from venture capital and investment firm websites. Extract the following information from the provided HTML content:

1. company_location: The physical location(s) of the company/firm
2. company_overview: A summary of the company's mission, history, and approach
3. investment_criteria: The specific criteria they use when evaluating investment opportunities
4. investment_strategy: Their overall investment approach, focus areas, and methodology
5. portfolio_companies: List of companies they have invested in
6. team_leadership: An array of team members, where each member MUST have these exact fields:
   {
     "name": "Full name of the person",
     "role": "Their position/title",
     "bio": "Their biographical information"
   }

For team_leadership, ensure each team member entry is structured exactly as shown above.
If any field's information is not found, return an empty string for that field.
For team_leadership, if no team members are found, return an empty array.

Example of expected team_leadership format:
"team_leadership": [
    {
        "name": "John Smith",
        "role": "Managing Partner",
        "bio": "John has 20 years of experience..."
    },
    {
        "name": "Jane Doe",
        "role": "Investment Director",
        "bio": "Jane leads our healthcare investments..."
    }
]

Ensure the response is properly formatted JSON matching the provided schema."""

def get_page_content(url: str) -> str:
    """Get the HTML content of a page using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait a bit for any dynamic content to load
            time.sleep(2)
            content = page.content()
            browser.close()
            return content
        except Exception as e:
            browser.close()
            raise Exception(f"Failed to fetch page content: {str(e)}")

def create_dynamic_listing_model(field_names: List[str]):
    """Create a Pydantic model for the fields we want to extract."""
    field_definitions = {}
    for field in field_names:
        if field == "team/leadership":
            # Create a nested model for team members
            TeamMember = create_model('TeamMember', 
                name=(str, ""),
                role=(str, ""),
                bio=(str, "")
            )
            field_definitions["team_leadership"] = (List[TeamMember], [])
        else:
            field_definitions[field.replace(" ", "_").replace("/", "_")] = (str, "")
    return create_model('DynamicListingModel', **field_definitions)

def create_listings_container_model(listing_model: BaseModel):
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

def generate_system_message(listing_model: BaseModel) -> str:
    # same logic as your code
    schema_info = listing_model.model_json_schema()
    field_descriptions = []
    for field_name, field_info in schema_info["properties"].items():
        field_type = field_info["type"]
        field_descriptions.append(f'"{field_name}": "{field_type}"')

    schema_structure = ",\n".join(field_descriptions)

    final_prompt= SYSTEM_MESSAGE+"\n"+f"""strictly follows this schema:
    {{
       "listings": [
         {{
           {schema_structure}
         }}
       ]
    }}
    """

    return final_prompt


def save_formatted_data(unique_name: str, formatted_data):
    if isinstance(formatted_data, str):
        try:
            data_json = json.loads(formatted_data)
        except json.JSONDecodeError:
            data_json = {"raw_text": formatted_data}
    elif hasattr(formatted_data, "dict"):
        data_json = formatted_data.dict()
    else:
        data_json = formatted_data

    supabase.table("scraped_data").update({
        "formatted_data": data_json
    }).eq("unique_name", unique_name).execute()
    MAGENTA = "\033[35m"
    RESET = "\033[0m"  # Reset color to default
    print(f"{MAGENTA}INFO:Scraped data saved for {unique_name}{RESET}")

def save_raw_data(unique_name: str, url: str, raw_data: str) -> None:
    """
    Save or update the row in supabase with unique_name, url, and raw_data.
    Also save metadata for analytics.
    """
    supabase.table("scraped_data").upsert({
        "unique_name": unique_name,
        "url": url,
        "raw_data": raw_data,
        "created_at": datetime.now().isoformat(),
        "content_length": len(raw_data),
        "success": len(raw_data) > 0
    }, on_conflict="unique_name").execute()

def scrape_urls(urls: List[str], fields: List[str], model: str = "gpt-4o-mini") -> tuple:
    """
    Scrape the specified URLs and extract the requested fields.
    Returns a tuple of (results, token_counts, cost)
    """
    DynamicListingModel = create_dynamic_listing_model(fields)
    
    results = {}
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0
    
    for url in urls:
        try:
            # Get the page content
            content = get_page_content(url)
            
            # Create the schema for the LLM
            parsed_data, token_counts, cost = call_llm_model(
                content, 
                DynamicListingModel, 
                model, 
                SYSTEM_MESSAGE
            )
            
            # Update totals
            total_input_tokens += token_counts["input_tokens"]
            total_output_tokens += token_counts["output_tokens"]
            total_cost += cost
            
            # Convert Pydantic model to dict if necessary
            if hasattr(parsed_data, 'dict'):
                parsed_data = parsed_data.dict()
            
            results[url] = parsed_data
            
        except Exception as e:
            results[url] = {"error": str(e)}
    
    token_counts = {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens
    }
    
    return results, token_counts, total_cost
