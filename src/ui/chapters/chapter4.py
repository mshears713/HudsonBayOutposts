"""
Chapter 4: Hunting Fort Operations & Advanced Multi-Fort Workflows

This chapter demonstrates the Hunting Fort API and showcases advanced distributed
system concepts including multi-fort data aggregation and cross-fort analytics.

Educational Focus:
- Advanced themed API integration (Hunting Fort)
- Multi-endpoint data aggregation
- Cross-fort analytics and comparisons
- Protected administrative operations
- Data visualization across multiple forts

Phase 3 Feature:
Complete integration of a third themed fort with authentication and
cross-fort workflow demonstrations.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
import pandas as pd
from src.api_client.client import OutpostAPIClient
from src.ui.components.auth_components import (
    initialize_auth_session_state,
    is_authenticated,
    render_auth_status_sidebar,
    get_authenticated_client,
    require_authentication
)
import logging

logger = logging.getLogger(__name__)


def render_chapter4():
    """
    Main render function for Chapter 4.

    Educational Note:
    This chapter demonstrates working with a third themed API and performing
    advanced multi-fort workflows that aggregate data across all three forts.
    """
    st.title("🏹 Chapter 4: Hunting Fort Operations")

    st.markdown("""
    Welcome to the Hunting Fort! This chapter introduces a third themed outpost
    focused on wildlife management, hunting parties, and pelt harvests.

    ### Learning Objectives
    - Work with a third themed API (Hunting Fort)
    - Aggregate data across multiple forts
    - Perform cross-fort analytics
    - Manage complex distributed workflows
    - Use authentication for administrative operations

    ### Prerequisites
    - Hunting Fort API running on port 8002
    - Database initialized with sample data
    - Authentication credentials for protected operations
    """)

    # Initialize authentication
    initialize_auth_session_state()

    # Fort configuration
    HUNTING_FORT_URL = st.text_input(
        "Hunting Fort API URL",
        value="http://localhost:8002",
        help="URL of the Hunting Fort API"
    )

    # Create tabs for different sections
    tabs = st.tabs([
        "📋 Overview",
        "🦌 Game Animals",
        "👥 Hunting Parties",
        "🎯 Pelt Harvests",
        "📊 Seasonal Reports",
        "🔐 Admin Dashboard",
        "🌐 Multi-Fort Analytics"
    ])

    # Tab 1: Overview
    with tabs[0]:
        render_overview_tab(HUNTING_FORT_URL)

    # Tab 2: Game Animals
    with tabs[1]:
        render_game_animals_tab(HUNTING_FORT_URL)

    # Tab 3: Hunting Parties
    with tabs[2]:
        render_hunting_parties_tab(HUNTING_FORT_URL)

    # Tab 4: Pelt Harvests
    with tabs[3]:
        render_pelt_harvests_tab(HUNTING_FORT_URL)

    # Tab 5: Seasonal Reports
    with tabs[4]:
        render_seasonal_reports_tab(HUNTING_FORT_URL)

    # Tab 6: Admin Dashboard
    with tabs[5]:
        render_admin_dashboard_tab(HUNTING_FORT_URL)

    # Tab 7: Multi-Fort Analytics
    with tabs[6]:
        render_multi_fort_analytics_tab()


def render_overview_tab(api_url: str):
    """Render the overview tab with fort status and introduction."""
    st.header("Hunting Fort Overview")

    st.markdown("""
    ### About the Hunting Fort

    The Hunting Fort specializes in wildlife management and fur trade operations.
    It tracks game populations, organizes hunting parties, records pelt harvests,
    and generates seasonal reports.

    **Key Features:**
    - **Game Animals**: Track wildlife species, populations, and habitat
    - **Hunting Parties**: Organize and manage hunting expeditions
    - **Pelt Harvests**: Record and value pelt collections
    - **Seasonal Reports**: Analyze hunting success over time
    """)

    # Get fort status
    st.subheader("Fort Status")

    try:
        client = OutpostAPIClient(api_url)
        status = client.get_status()

        if status:
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Fort Name:** {status.get('fort_name', 'Unknown')}")
                st.write(f"**Last Updated:** {status.get('timestamp', 'Unknown')}")

            with col2:
                stats = status.get('statistics', {})
                st.metric("Tracked Species", stats.get('tracked_species', 0))
                st.metric("Active Parties", stats.get('active_parties', 0))

            col3, col4 = st.columns(2)
            with col3:
                st.metric("Pelts This Season", stats.get('pelts_this_season', 0))
            with col4:
                st.metric("Season Value", f"${stats.get('value_this_season', 0):.2f}")

            st.success("✓ Hunting Fort API is operational")
        else:
            st.error("Could not retrieve fort status. Is the API running?")

    except Exception as e:
        st.error(f"Error connecting to Hunting Fort: {str(e)}")
        st.info("Make sure to start the API: `uvicorn raspberry_pi.api.hunting_fort:app --host 0.0.0.0 --port 8002 --reload`")


def render_game_animals_tab(api_url: str):
    """Render the game animals tab."""
    st.header("🦌 Game Animals")

    st.markdown("""
    Browse the wildlife species tracked by the Hunting Fort. This database
    includes population status, habitat information, and economic value.
    """)

    try:
        client = OutpostAPIClient(api_url)

        # Filters
        col1, col2 = st.columns(2)

        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                options=["All", "big_game", "small_game", "fur_bearer", "waterfowl"],
                help="Filter animals by category"
            )

        with col2:
            status_filter = st.selectbox(
                "Filter by Population Status",
                options=["All", "abundant", "common", "fair", "scarce", "protected"],
                help="Filter by population status"
            )

        # Fetch animals
        params = {}
        if category_filter != "All":
            params['category'] = category_filter
        if status_filter != "All":
            params['status'] = status_filter

        # Make request with filters
        if params:
            # Build endpoint with query params
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            animals = client._make_request('GET', f'/animals?{query_string}')
        else:
            animals = client._make_request('GET', '/animals')

        if animals:
            st.write(f"**Found {len(animals)} species**")

            # Convert to DataFrame for display
            df = pd.DataFrame(animals)

            # Display as cards
            for animal in animals:
                with st.expander(f"**{animal['species']}** ({animal['category']})"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**Size:** {animal['typical_size']}")
                        st.write(f"**Status:** {animal['population_status']}")

                    with col2:
                        st.write(f"**Pelt Value:** ${animal.get('pelt_value', 0):.2f}")
                        st.write(f"**Meat Yield:** {animal.get('meat_yield', 'N/A')}")

                    with col3:
                        st.write(f"**Best Season:** {animal['best_season']}")
                        st.write(f"**Habitat:** {animal.get('habitat', 'Unknown')}")

                    if animal.get('notes'):
                        st.info(f"📝 {animal['notes']}")

            # Summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Species", len(animals))
            with col2:
                avg_value = sum(a.get('pelt_value', 0) or 0 for a in animals) / len(animals) if animals else 0
                st.metric("Avg Pelt Value", f"${avg_value:.2f}")
            with col3:
                categories = set(a['category'] for a in animals)
                st.metric("Categories", len(categories))

        else:
            st.info("No animals found with the selected filters")

    except Exception as e:
        st.error(f"Error fetching game animals: {str(e)}")
        logger.error(f"Game animals error: {e}")


def render_hunting_parties_tab(api_url: str):
    """Render the hunting parties tab."""
    st.header("👥 Hunting Parties")

    st.markdown("""
    View hunting party expeditions including active, completed, and planned parties.
    """)

    try:
        client = OutpostAPIClient(api_url)

        # Status filter
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "planning", "active", "completed", "cancelled"],
            help="Filter parties by status"
        )

        # Fetch parties
        if status_filter != "All":
            parties = client._make_request('GET', f'/parties?status={status_filter}')
        else:
            parties = client._make_request('GET', '/parties')

        if parties:
            st.write(f"**Found {len(parties)} hunting parties**")

            # Group by status
            status_groups = {}
            for party in parties:
                status = party['status']
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(party)

            # Display by status
            for status, group in status_groups.items():
                st.subheader(f"{status.capitalize()} Parties ({len(group)})")

                for party in group:
                    status_icon = {
                        "planning": "📋",
                        "active": "🔥",
                        "completed": "✅",
                        "cancelled": "❌"
                    }.get(status, "📝")

                    with st.expander(f"{status_icon} {party['leader_name']} - {party.get('target_species', 'Mixed')} ({party['start_date']})"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.write(f"**Leader:** {party['leader_name']}")
                            st.write(f"**Party Size:** {party['party_size']}")

                        with col2:
                            st.write(f"**Start Date:** {party['start_date']}")
                            st.write(f"**End Date:** {party.get('end_date', 'Ongoing')}")

                        with col3:
                            st.write(f"**Target:** {party.get('target_species', 'Mixed')}")
                            st.write(f"**Region:** {party.get('region', 'Unknown')}")

                        if party.get('total_harvest'):
                            st.metric("Total Harvest", party['total_harvest'])

                        if party.get('success_rate'):
                            st.progress(party['success_rate'] / 100)
                            st.write(f"Success Rate: {party['success_rate']}%")

                        if party.get('notes'):
                            st.info(f"📝 {party['notes']}")

        else:
            st.info("No hunting parties found")

    except Exception as e:
        st.error(f"Error fetching hunting parties: {str(e)}")
        logger.error(f"Hunting parties error: {e}")


def render_pelt_harvests_tab(api_url: str):
    """Render the pelt harvests tab."""
    st.header("🎯 Pelt Harvests")

    st.markdown("""
    View pelt harvest records with quality ratings and estimated values.
    """)

    try:
        client = OutpostAPIClient(api_url)

        # Get harvest summary first
        summary = client._make_request('GET', '/harvests/summary')

        if summary:
            st.subheader("Harvest Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Records", summary.get('total_records', 0))
            with col2:
                st.metric("Total Pelts", summary.get('total_pelts', 0))
            with col3:
                st.metric("Total Value", f"${summary.get('total_value', 0):.2f}")

            # By species breakdown
            st.subheader("By Species")
            by_species = summary.get('by_species', [])
            if by_species:
                df_species = pd.DataFrame(by_species)
                st.dataframe(df_species, use_container_width=True)

            # By quality breakdown
            st.subheader("By Quality")
            by_quality = summary.get('by_quality', [])
            if by_quality:
                df_quality = pd.DataFrame(by_quality)
                st.dataframe(df_quality, use_container_width=True)

        st.divider()

        # Recent harvests
        st.subheader("Recent Harvests")

        harvests = client._make_request('GET', '/harvests')

        if harvests:
            # Show first 20
            for harvest in harvests[:20]:
                quality_icon = {
                    "exceptional": "⭐⭐⭐⭐⭐",
                    "prime": "⭐⭐⭐⭐",
                    "good": "⭐⭐⭐",
                    "fair": "⭐⭐",
                    "poor": "⭐"
                }.get(harvest['quality'], "")

                with st.expander(f"{harvest['species']} x{harvest['quantity']} - {harvest['quality']} {quality_icon} (${harvest['estimated_value']:.2f})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Species:** {harvest['species']}")
                        st.write(f"**Quantity:** {harvest['quantity']}")
                        st.write(f"**Quality:** {harvest['quality']} {quality_icon}")

                    with col2:
                        st.write(f"**Date:** {harvest['date_harvested']}")
                        st.write(f"**Value:** ${harvest['estimated_value']:.2f}")
                        st.write(f"**Party ID:** {harvest['party_id']}")

                    if harvest.get('condition'):
                        st.info(f"Condition: {harvest['condition']}")

        else:
            st.info("No harvest records found")

    except Exception as e:
        st.error(f"Error fetching pelt harvests: {str(e)}")
        logger.error(f"Pelt harvests error: {e}")


def render_seasonal_reports_tab(api_url: str):
    """Render the seasonal reports tab."""
    st.header("📊 Seasonal Reports")

    st.markdown("""
    View seasonal hunting summaries and trends over time.
    """)

    try:
        client = OutpostAPIClient(api_url)

        reports = client._make_request('GET', '/reports')

        if reports:
            st.write(f"**Found {len(reports)} seasonal reports**")

            for report in reports:
                with st.expander(f"📅 {report['season']} ({report['year']})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Total Parties", report['total_parties'])
                        st.metric("Total Hunters", report['total_hunters'])

                    with col2:
                        st.metric("Total Pelts", report['total_pelts'])
                        st.metric("Total Value", f"${report['total_value']:.2f}")

                    if report.get('top_species'):
                        st.write(f"**Top Species:** {report['top_species']}")

                    if report.get('weather_conditions'):
                        st.info(f"☁️ Weather: {report['weather_conditions']}")

                    if report.get('notes'):
                        st.write(f"**Notes:** {report['notes']}")

            # Trends visualization
            if len(reports) > 1:
                st.subheader("Trends Over Time")

                df = pd.DataFrame(reports)
                df = df.sort_values('year')

                col1, col2 = st.columns(2)

                with col1:
                    st.line_chart(df.set_index('season')['total_pelts'])
                    st.caption("Total Pelts by Season")

                with col2:
                    st.line_chart(df.set_index('season')['total_value'])
                    st.caption("Total Value by Season")

        else:
            st.info("No seasonal reports found")

    except Exception as e:
        st.error(f"Error fetching seasonal reports: {str(e)}")
        logger.error(f"Seasonal reports error: {e}")


def render_admin_dashboard_tab(api_url: str):
    """Render the admin dashboard tab (requires authentication)."""
    st.header("🔐 Admin Dashboard")

    # Check authentication
    if not require_authentication():
        return

    st.markdown("""
    This administrative dashboard provides comprehensive statistics across
    all hunting fort operations. **Authentication required.**
    """)

    try:
        client = get_authenticated_client(api_url, "hunting_fort")

        if not client or not client.is_authenticated:
            st.warning("Please log in to access admin statistics")
            return

        # Get admin stats
        stats = client._make_request('GET', '/admin/statistics')

        if stats:
            st.success(f"✓ Data retrieved by: {stats.get('generated_by', 'Unknown')}")

            # Animals stats
            st.subheader("🦌 Game Animals Statistics")
            animal_stats = stats.get('animals', {})

            st.metric("Total Species", animal_stats.get('total_species', 0))

            col1, col2 = st.columns(2)

            with col1:
                st.write("**By Category:**")
                for item in animal_stats.get('by_category', []):
                    st.write(f"- {item['category']}: {item['count']}")

            with col2:
                st.write("**By Population Status:**")
                for item in animal_stats.get('by_status', []):
                    st.write(f"- {item['population_status']}: {item['count']}")

            st.divider()

            # Parties stats
            st.subheader("👥 Hunting Parties Statistics")
            party_stats = stats.get('parties', {})

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Parties", party_stats.get('total_parties', 0))
            with col2:
                st.metric("Active Parties", party_stats.get('active_parties', 0))

            st.write("**By Status:**")
            for item in party_stats.get('by_status', []):
                st.write(f"- {item['status']}: {item['count']}")

            st.divider()

            # Harvest stats
            st.subheader("🎯 Harvest Statistics")
            harvest_stats = stats.get('harvests', {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", harvest_stats.get('total_records', 0))
            with col2:
                st.metric("Total Pelts", harvest_stats.get('total_pelts', 0))
            with col3:
                st.metric("Total Value", f"${harvest_stats.get('total_value', 0):.2f}")

        else:
            st.error("Could not retrieve admin statistics")

    except Exception as e:
        st.error(f"Error fetching admin statistics: {str(e)}")
        logger.error(f"Admin stats error: {e}")


def render_multi_fort_analytics_tab():
    """Render multi-fort analytics comparing all three forts."""
    st.header("🌐 Multi-Fort Analytics")

    st.markdown("""
    This advanced feature demonstrates cross-fort analytics by aggregating
    data from all three Hudson Bay Company outposts: Fishing Fort, Trading Fort,
    and Hunting Fort.

    **Educational Note:**
    This showcases distributed system concepts including:
    - Multi-source data aggregation
    - Cross-system analytics
    - Comparative analysis across nodes
    """)

    # Fort URLs
    col1, col2, col3 = st.columns(3)

    with col1:
        fishing_url = st.text_input("Fishing Fort URL", "http://localhost:8000")
    with col2:
        trading_url = st.text_input("Trading Fort URL", "http://localhost:8001")
    with col3:
        hunting_url = st.text_input("Hunting Fort URL", "http://localhost:8002")

    if st.button("🔄 Aggregate Fort Data"):
        with st.spinner("Gathering data from all forts..."):
            try:
                # Create clients
                fishing_client = OutpostAPIClient(fishing_url)
                trading_client = OutpostAPIClient(trading_url)
                hunting_client = OutpostAPIClient(hunting_url)

                # Get status from all forts
                fishing_status = fishing_client.get_status()
                trading_status = trading_client.get_status()
                hunting_status = hunting_client.get_status()

                st.success("✓ Successfully connected to all three forts!")

                # Display comparison
                st.subheader("Fort Comparison")

                comparison_df = pd.DataFrame([
                    {
                        "Fort": "Fishing Fort",
                        "Status": "✅ Online" if fishing_status else "❌ Offline",
                        "Primary Activity": "Fish Catch Records"
                    },
                    {
                        "Fort": "Trading Fort",
                        "Status": "✅ Online" if trading_status else "❌ Offline",
                        "Primary Activity": "Trade Goods Management"
                    },
                    {
                        "Fort": "Hunting Fort",
                        "Status": "✅ Online" if hunting_status else "❌ Offline",
                        "Primary Activity": "Pelt Harvests"
                    }
                ])

                st.dataframe(comparison_df, use_container_width=True)

                # Show combined metrics
                st.subheader("Combined Network Statistics")

                if all([fishing_status, trading_status, hunting_status]):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Forts", 3)

                    with col2:
                        # Example: could aggregate inventory counts, etc.
                        st.metric("Network Health", "100%")

                    with col3:
                        st.metric("Data Sources", "All Connected")

                    st.balloons()

            except Exception as e:
                st.error(f"Error aggregating fort data: {str(e)}")
                logger.error(f"Multi-fort analytics error: {e}")
