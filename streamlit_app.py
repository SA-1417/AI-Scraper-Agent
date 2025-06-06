# streamlit_app.py

import streamlit as st
import pandas as pd
import json
import sys
import asyncio
from datetime import datetime
# ---local imports---
from scraper import scrape_urls
from api_management import get_supabase_client

# Only use WindowsProactorEventLoopPolicy on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialize Streamlit app
st.set_page_config(page_title="Internal Web Scraper", page_icon="🦑")

# Initialize session state for tracking totals
if 'total_input_tokens' not in st.session_state:
    st.session_state.total_input_tokens = 0
if 'total_output_tokens' not in st.session_state:
    st.session_state.total_output_tokens = 0
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0

# Initialize Supabase client
supabase = get_supabase_client()
if supabase is None:
    st.error("🚨 **Supabase is not configured!** Please check your environment variables for Supabase configuration.")
    st.stop()

# Define the fields to extract (from changes.md)
FIELDS_TO_EXTRACT = [
    "company location",
    "company overview",
    "investment criteria",
    "investment strategy",
    "portfolio companies",
    "team/leadership"
]

# Main title
st.title("Internal Web Scraper 🦑")

# Get total number of rows in subpages table
try:
    response = supabase.table("subpages").select("id", "full_url").execute()
    subpages_data = response.data
    total_rows = len(subpages_data)
    
    if total_rows == 0:
        st.error("No URLs found in the subpages table.")
        st.stop()
        
    st.info(f"Found {total_rows} URLs in the subpages table.")
    
    # Input for start and end row numbers
    col1, col2 = st.columns(2)
    with col1:
        start_row = st.number_input("Start Row Number", min_value=1, max_value=total_rows, value=1)
    with col2:
        end_row = st.number_input("End Row Number", min_value=start_row, max_value=total_rows, value=min(start_row + 9, total_rows))

    # Display selected range info
    st.write(f"Selected range: Rows {start_row} to {end_row} ({end_row - start_row + 1} URLs)")
    
    # Create a placeholder for the metrics
    metrics_placeholder = st.empty()
    
    # Main action button
    if st.button("Start Scraping", type="primary"):
        # Reset totals
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.total_cost = 0
        
        # Get URLs for selected range
        selected_urls = subpages_data[start_row-1:end_row]
        
        with st.spinner(f"Scraping {len(selected_urls)} URLs..."):
            for url_data in selected_urls:
                subpage_id = url_data['id']
                url = url_data['full_url']
                
                st.write(f"Processing URL: {url}")
                
                try:
                    # Scrape the URL
                    scraped_data, token_counts, cost = scrape_urls([url], FIELDS_TO_EXTRACT, "gpt-4o-mini")
                    
                    # Update totals
                    st.session_state.total_input_tokens += token_counts["input_tokens"]
                    st.session_state.total_output_tokens += token_counts["output_tokens"]
                    st.session_state.total_cost += cost
                    
                    # Update total metrics display
                    col1, col2, col3 = metrics_placeholder.columns(3)
                    col1.metric("Total Input Tokens", st.session_state.total_input_tokens)
                    col2.metric("Total Output Tokens", st.session_state.total_output_tokens)
                    col3.metric("Total Cost", f"${st.session_state.total_cost:.4f}")
                    
                    # Prepare data for insertion
                    insert_data = {
                        'subpage_id': subpage_id,
                        'data_json': json.dumps(scraped_data),
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Insert into scraped_data2 table
                    supabase.table("scraped_data2").insert(insert_data).execute()
                    
                    st.success(f"Successfully scraped and stored data for URL {url}")
                    
                except Exception as e:
                    st.error(f"Error processing URL {url}: {str(e)}")
                    continue
        
        st.success("Scraping completed!")

except Exception as e:
    st.error(f"Error accessing Supabase: {str(e)}")

