"""
Chapter 1: Fishing Fort - Inventory Management UI

This module provides the Streamlit interface for Chapter 1, focusing on
basic API interaction with the Fishing Fort outpost. Users learn to fetch
and display inventory data from a RESTful API.

Educational Focus:
- Making HTTP GET requests to APIs
- Displaying tabular data
- Handling API responses and errors
- Understanding JSON data structures
"""

import streamlit as st
import requests
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models.outpost import Outpost, OutpostStatus


def render_chapter1_page():
    """
    Main render function for Chapter 1.

    Educational Note:
    This chapter introduces users to basic API concepts through a fishing
    fort inventory management interface.
    """
    st.title("🎣 Chapter 1: Fishing Fort Inventory")

    st.markdown("""
    ### Welcome to Your First Outpost!

    In this chapter, you'll learn to interact with the **Fishing Fort** outpost API.
    This frontier fort tracks fishing inventory, catch records, and equipment.

    #### Learning Objectives:
    - 📡 Connect to a REST API endpoint
    - 📊 Fetch and display JSON data
    - 🔄 Refresh data from remote sources
    - 📋 Understand HTTP GET requests

    ---
    """)

    # Check if we have a fishing fort configured
    fishing_fort = get_fishing_fort_outpost()

    if not fishing_fort:
        render_outpost_setup_guide()
        return

    # Display outpost connection status
    render_outpost_status(fishing_fort)

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Inventory",
        "🎣 Catch Records",
        "📊 Statistics",
        "📚 Learning Notes"
    ])

    with tab1:
        render_inventory_tab(fishing_fort)

    with tab2:
        render_catch_records_tab(fishing_fort)

    with tab3:
        render_statistics_tab(fishing_fort)

    with tab4:
        render_learning_notes_tab()


def get_fishing_fort_outpost() -> Optional[Outpost]:
    """
    Get the fishing fort outpost from session state.

    Returns:
        Outpost object or None if not configured

    Educational Note:
    This demonstrates how to access shared state across the application.
    """
    if 'outposts' not in st.session_state:
        return None

    # Look for a fishing fort in configured outposts
    for outpost in st.session_state.outposts:
        if outpost.outpost_type.value == 'fishing':
            return outpost

    return None


def render_outpost_setup_guide():
    """Display setup instructions if no fishing fort is configured."""
    st.warning("⚠️ No Fishing Fort outpost configured!")

    st.markdown("""
    ### Setup Instructions:

    To complete this chapter, you need to:

    1. **Configure a Fishing Fort outpost** in the Outposts page
    2. **Or enable Demo Mode** to simulate the outpost

    #### Option 1: Real Raspberry Pi Setup

    - Go to the **Outposts** page (sidebar)
    - Add a new outpost with type "Fishing"
    - Enter your Raspberry Pi's IP address and port
    - Make sure the Fishing Fort API is running on the Pi

    #### Option 2: Demo Mode

    - Enable **Demo Mode** in Settings or on the Home page
    - This simulates API responses without a physical Raspberry Pi
    """)

    # Quick demo mode toggle
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("💡 **Tip**: Demo Mode is perfect for learning without hardware!")
    with col2:
        if st.button("Enable Demo Mode", type="primary"):
            st.session_state.demo_mode = True
            st.rerun()


def render_outpost_status(outpost: Outpost):
    """
    Display outpost connection status.

    Args:
        outpost: The fishing fort outpost

    Educational Note:
    Status checks verify API connectivity before attempting operations.
    """
    with st.expander("🏰 Outpost Connection Status", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Outpost Name", outpost.name)

        with col2:
            st.metric("Type", outpost.outpost_type.value.title())

        with col3:
            # Try to check status
            status = check_outpost_health(outpost)
            if status:
                st.metric("Status", "🟢 Online")
            else:
                st.metric("Status", "🔴 Offline")

        st.caption(f"API Base URL: `{outpost.api_base_url}`")

        if st.button("🔄 Test Connection"):
            with st.spinner("Testing connection..."):
                result = check_outpost_health(outpost)
                if result:
                    st.success(f"✅ Connected successfully! {result.get('inventory_items', 0)} items in database.")
                else:
                    st.error("❌ Connection failed. Check that the API server is running.")


def check_outpost_health(outpost: Outpost) -> Optional[Dict[str, Any]]:
    """
    Check if outpost API is accessible.

    Args:
        outpost: The outpost to check

    Returns:
        Health check response data or None if failed

    Educational Note:
    Health checks use simple GET requests to verify API availability.
    This is a common pattern in distributed systems.
    """
    try:
        url = outpost.get_endpoint_url('/health')
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None


def render_inventory_tab(outpost: Outpost):
    """
    Render the inventory management tab.

    Args:
        outpost: The fishing fort outpost

    Educational Note:
    This demonstrates fetching and displaying API data in a user-friendly format.
    """
    st.subheader("📦 Fort Inventory")

    st.markdown("""
    This inventory shows all supplies, food, and tools at the Fishing Fort.
    Data is fetched in real-time from the outpost's API.

    **Educational Insight**: When you click "Refresh", your browser sends an
    HTTP GET request to the `/inventory` endpoint, receives JSON data, and
    displays it in a table.
    """)

    # Filter options
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        category_filter = st.selectbox(
            "Category Filter",
            options=["All", "food", "tools", "supplies"],
            help="Filter inventory by category"
        )

    with col2:
        min_quantity = st.number_input(
            "Minimum Quantity",
            min_value=0,
            value=0,
            help="Show only items with quantity >= this value"
        )

    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        refresh = st.button("🔄 Refresh", use_container_width=True)

    # Fetch inventory data
    inventory_data = fetch_inventory(
        outpost,
        category=None if category_filter == "All" else category_filter,
        min_quantity=min_quantity
    )

    if inventory_data is None:
        st.error("❌ Failed to fetch inventory data. Check your connection.")
        return

    if not inventory_data:
        st.info("📭 No inventory items match your filters.")
        return

    # Display as DataFrame
    df = pd.DataFrame(inventory_data)

    # Format the dataframe for display
    display_df = df[[
        'name', 'category', 'quantity', 'unit', 'value', 'description'
    ]].copy()

    display_df.columns = [
        'Item Name', 'Category', 'Quantity', 'Unit', 'Value ($)', 'Description'
    ]

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Items", len(df))

    with col2:
        total_value = df['value'].sum()
        st.metric("Total Value", f"${total_value:.2f}")

    with col3:
        categories = df['category'].nunique()
        st.metric("Categories", categories)

    with col4:
        low_stock = len(df[df['quantity'] < 50])
        st.metric("Low Stock Items", low_stock)

    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # Show raw JSON option
    with st.expander("🔍 View Raw JSON Data"):
        st.json(inventory_data)
        st.caption("""
        **Educational Note**: This is the raw JSON data received from the API.
        APIs return data in JSON format, which is then parsed and displayed
        in a user-friendly way.
        """)


def fetch_inventory(
    outpost: Outpost,
    category: Optional[str] = None,
    min_quantity: Optional[int] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch inventory data from the outpost API.

    Args:
        outpost: The outpost to query
        category: Optional category filter
        min_quantity: Optional minimum quantity filter

    Returns:
        List of inventory items or None if failed

    Educational Note:
    This function demonstrates how to construct API requests with query
    parameters and handle responses.
    """
    try:
        url = outpost.get_endpoint_url('/inventory')

        # Build query parameters
        params = {}
        if category:
            params['category'] = category
        if min_quantity is not None and min_quantity > 0:
            params['min_quantity'] = min_quantity

        # Make the request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()
        return data

    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The outpost may be unreachable.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection failed. Is the API server running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP Error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


def render_catch_records_tab(outpost: Outpost):
    """Render the catch records view."""
    st.subheader("🎣 Recent Catches")

    st.markdown("""
    View recent fishing catches recorded at the outpost.
    This demonstrates fetching related data from another API endpoint.
    """)

    # Fetch catch records
    catches = fetch_catch_records(outpost)

    if catches is None:
        st.error("Failed to fetch catch records.")
        return

    if not catches:
        st.info("No catch records found.")
        return

    # Display summary metrics
    df = pd.DataFrame(catches)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Catches", len(df))

    with col2:
        total_weight = df['weight_pounds'].sum()
        st.metric("Total Weight", f"{total_weight:.1f} lbs")

    with col3:
        fish_types = df['fish_type'].nunique()
        st.metric("Fish Types", fish_types)

    # Display table
    display_df = df[[
        'catch_date', 'fish_type', 'quantity', 'weight_pounds', 'location', 'quality'
    ]].copy()

    display_df.columns = [
        'Date', 'Fish Type', 'Count', 'Weight (lbs)', 'Location', 'Quality'
    ]

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)


def fetch_catch_records(outpost: Outpost) -> Optional[List[Dict[str, Any]]]:
    """Fetch catch records from the API."""
    try:
        url = outpost.get_endpoint_url('/catches')
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching catch records: {e}")
        return None


def render_statistics_tab(outpost: Outpost):
    """Render statistics and summary view."""
    st.subheader("📊 Outpost Statistics")

    # Fetch status
    status = fetch_outpost_status(outpost)

    if status:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Inventory Items", status.get('total_inventory_items', 0))

        with col2:
            st.metric("Inventory Value", f"${status.get('total_inventory_value', 0):.2f}")

        with col3:
            st.metric("Recent Catches (7 days)", status.get('recent_catches_count', 0))

        st.divider()
        st.caption(f"Last updated: {status.get('last_updated', 'Unknown')}")


def fetch_outpost_status(outpost: Outpost) -> Optional[Dict[str, Any]]:
    """Fetch outpost status from API."""
    try:
        url = outpost.get_endpoint_url('/status')
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching status: {e}")
        return None


def render_learning_notes_tab():
    """Render educational content about the chapter."""
    st.subheader("📚 Learning Notes: REST APIs and HTTP GET")

    st.markdown("""
    ### What You're Learning in Chapter 1

    #### REST APIs
    REST (Representational State Transfer) is an architectural style for building web APIs.
    Key concepts:

    - **Resources**: Data entities accessed via URLs (e.g., `/inventory`)
    - **HTTP Methods**: GET (read), POST (create), PUT (update), DELETE (remove)
    - **JSON Format**: Structured data format for API responses
    - **Stateless**: Each request is independent

    #### HTTP GET Requests
    When you fetch inventory data, here's what happens:

    ```
    1. Browser/Client → HTTP GET → http://pi-ip:8000/inventory
    2. Server processes request
    3. Server queries database
    4. Server formats data as JSON
    5. Server → HTTP Response → Client
    6. Client displays data
    ```

    #### Query Parameters
    Query parameters filter results:

    ```
    /inventory?category=food&min_quantity=10
    ```

    This asks for: "Give me food items with quantity >= 10"

    #### JSON Response Format
    APIs return data in JSON (JavaScript Object Notation):

    ```json
    [
      {
        "item_id": 1,
        "name": "Fishing Line",
        "category": "supplies",
        "quantity": 500,
        "value": 25.0
      }
    ]
    ```

    #### Try It Yourself!
    - Change the category filter and observe the URL change
    - Check the "View Raw JSON" expander to see actual API responses
    - Click "Refresh" and watch the network request happen

    #### Next Steps
    In Chapter 2, you'll learn to:
    - Execute remote commands via SSH
    - Upload and download files
    - Manage logs and system information

    ---

    💡 **Remember**: Every time you interact with the UI, you're making real API calls!
    """)


# Make this module callable directly
if __name__ == "__main__":
    st.set_page_config(page_title="Chapter 1", layout="wide")
    render_chapter1_page()
