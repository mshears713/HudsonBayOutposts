"""
Chapter 3: Trading Fort with Authentication

This chapter introduces the Trading Fort API and demonstrates authenticated
API interactions, including protected endpoints and role-based access.

Educational Note:
This chapter builds on previous chapters by adding:
- Token-based authentication
- Protected API endpoints
- User roles and permissions
- Secure data access patterns
"""

import streamlit as st
import pandas as pd
from typing import Optional
from src.api_client.client import OutpostAPIClient
from src.ui.components.auth_components import (
    initialize_auth_session_state,
    render_login_form,
    render_user_status_badge,
    render_user_profile_card,
    render_logout_button,
    require_authentication,
    get_authenticated_client,
    is_authenticated
)
import logging

logger = logging.getLogger(__name__)

# Trading Fort API configuration
TRADING_FORT_API = "http://localhost:8001"  # Update with actual Pi address


def render_chapter3():
    """
    Main render function for Chapter 3.

    Educational Note:
    This demonstrates a complete authenticated workflow:
    1. Check authentication status
    2. Show login if needed
    3. Display authenticated content
    4. Handle protected operations
    """
    # Initialize auth session state
    initialize_auth_session_state()

    st.title("🏪 Chapter 3: Trading Fort Operations")
    st.markdown("---")

    # Show authentication status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        **Learning Objectives:**
        - Authenticate with token-based APIs
        - Access protected endpoints
        - Understand role-based access control
        - Manage user sessions
        """)

    with col2:
        render_user_status_badge()

    st.markdown("---")

    # Create tabs for different sections
    tabs = st.tabs([
        "📚 Overview",
        "🔐 Authentication",
        "📦 Trade Goods",
        "👥 Traders",
        "💼 Trade Records",
        "📊 Admin Dashboard"
    ])

    with tabs[0]:
        render_overview()

    with tabs[1]:
        render_authentication_section()

    with tabs[2]:
        render_goods_section()

    with tabs[3]:
        render_traders_section()

    with tabs[4]:
        render_trades_section()

    with tabs[5]:
        render_admin_section()


def render_overview():
    """Render chapter overview and introduction."""
    st.header("📚 Trading Fort Overview")

    st.markdown("""
    ### Welcome to the Trading Fort!

    The Trading Fort is the economic heart of the frontier, where trappers,
    traders, and merchants exchange goods, furs, and supplies.

    **What You'll Learn:**

    1. **Authentication Flow**
       - How to log in with username and password
       - Token-based authentication
       - Managing user sessions

    2. **Protected Endpoints**
       - Accessing endpoints that require authentication
       - Understanding bearer tokens
       - Handling authentication errors

    3. **Role-Based Access**
       - Different user roles (admin, manager, user)
       - Permission-based features
       - Fort-specific access control

    4. **Secure Data Operations**
       - Creating and modifying data securely
       - Audit trails (who made changes)
       - Access logging

    ### Getting Started

    1. Go to the **Authentication** tab
    2. Log in with a demo account
    3. Explore the different features based on your role
    4. Try accessing admin features with different roles

    ### API Information

    - **Endpoint:** `{TRADING_FORT_API}`
    - **Authentication:** Bearer Token (JWT)
    - **Documentation:** `{TRADING_FORT_API}/docs`
    """)

    # Show API health status
    st.markdown("### 🏥 API Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Check Health", use_container_width=True):
            try:
                client = OutpostAPIClient(TRADING_FORT_API)
                health = client.health_check()
                if health:
                    st.success(f"✅ {health['service']} is healthy")
                    st.json(health)
                else:
                    st.error("❌ Health check failed")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with col2:
        if st.button("Get Status", use_container_width=True):
            try:
                client = OutpostAPIClient(TRADING_FORT_API)
                status = client.get_status()
                if status:
                    st.success("✅ Status retrieved")
                    st.json(status)
                else:
                    st.error("❌ Failed to get status")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_authentication_section():
    """Render authentication and login section."""
    st.header("🔐 Authentication")

    if is_authenticated():
        st.success("✅ You are logged in!")

        col1, col2 = st.columns(2)

        with col1:
            render_user_profile_card()

        with col2:
            st.markdown("### 🎮 Actions")

            if st.button("🔄 Refresh User Info", use_container_width=True):
                client = get_authenticated_client('trading', TRADING_FORT_API)
                if client:
                    user_info = client.get_current_user()
                    if user_info:
                        st.json(user_info)
                    else:
                        st.error("Failed to get user info")

            if st.button("📋 List Available Users", use_container_width=True):
                client = OutpostAPIClient(TRADING_FORT_API)
                users = client.list_available_users()
                if users:
                    st.json(users)

            st.markdown("---")
            render_logout_button()

    else:
        st.info("👋 Please log in to access Trading Fort features")

        render_login_form(
            TRADING_FORT_API,
            on_success=lambda user: st.success(f"Welcome, {user['username']}!")
        )


def render_goods_section():
    """Render trade goods management section."""
    st.header("📦 Trade Goods")

    if not require_authentication(TRADING_FORT_API, "Please log in to view trade goods"):
        return

    client = get_authenticated_client('trading', TRADING_FORT_API)
    if not client:
        st.error("Failed to get authenticated client")
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All", "furs", "tools", "trade_goods", "provisions"],
            help="Filter goods by category"
        )

    with col2:
        quality_filter = st.selectbox(
            "Quality",
            ["All", "poor", "fair", "good", "excellent"],
            help="Filter goods by quality"
        )

    with col3:
        if st.button("🔄 Refresh Goods", use_container_width=True):
            st.rerun()

    # Fetch goods
    with st.spinner("Loading trade goods..."):
        try:
            category = None if category_filter == "All" else category_filter
            quality = None if quality_filter == "All" else quality_filter

            # Note: Need to add filter support to client method
            goods = client.get_goods()

            if goods:
                # Convert to DataFrame
                df = pd.DataFrame(goods)

                # Apply filters
                if category:
                    df = df[df['category'] == category]
                if quality:
                    df = df[df['quality'] == quality]

                st.success(f"Found {len(df)} goods")

                # Display as table
                st.dataframe(
                    df[['name', 'category', 'quantity', 'unit', 'current_price', 'quality', 'origin']],
                    use_container_width=True
                )

                # Detailed view
                with st.expander("📊 Detailed View"):
                    selected_good = st.selectbox(
                        "Select a good for details",
                        df['name'].tolist()
                    )

                    good_details = df[df['name'] == selected_good].iloc[0].to_dict()
                    st.json(good_details)

            else:
                st.warning("No goods found")

        except Exception as e:
            logger.error(f"Error fetching goods: {e}")
            st.error(f"❌ Error: {str(e)}")


def render_traders_section():
    """Render traders registry section."""
    st.header("👥 Traders Registry")

    if not require_authentication(TRADING_FORT_API, "Please log in to view traders"):
        return

    client = get_authenticated_client('trading', TRADING_FORT_API)
    if not client:
        st.error("Failed to get authenticated client")
        return

    # Fetch traders
    with st.spinner("Loading traders..."):
        try:
            traders = client.get_traders()

            if traders:
                df = pd.DataFrame(traders)

                st.success(f"Found {len(df)} registered traders")

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Traders", len(df))

                with col2:
                    st.metric("Trappers", len(df[df['trader_type'] == 'trapper']))

                with col3:
                    st.metric("Merchants", len(df[df['trader_type'] == 'merchant']))

                with col4:
                    avg_reputation = df['reputation'].value_counts()
                    st.metric("Most Common Rep", avg_reputation.index[0] if len(avg_reputation) > 0 else "N/A")

                # Display table
                st.dataframe(
                    df[['name', 'trader_type', 'reputation', 'total_trades', 'total_value']],
                    use_container_width=True
                )

            else:
                st.warning("No traders found")

        except Exception as e:
            logger.error(f"Error fetching traders: {e}")
            st.error(f"❌ Error: {str(e)}")


def render_trades_section():
    """Render trade records section."""
    st.header("💼 Trade Records")

    if not require_authentication(TRADING_FORT_API, "Please log in to view trade records"):
        return

    client = get_authenticated_client('trading', TRADING_FORT_API)
    if not client:
        st.error("Failed to get authenticated client")
        return

    # Trade summary
    st.subheader("📊 Trade Summary")

    with st.spinner("Loading trade summary..."):
        try:
            summary = client.get_trade_summary()

            if summary and 'summary_by_type' in summary:
                col1, col2, col3 = st.columns(3)

                for i, (trade_type, stats) in enumerate(summary['summary_by_type'].items()):
                    with [col1, col2, col3][i % 3]:
                        st.metric(
                            f"{trade_type.capitalize()} Trades",
                            stats['count'],
                            delta=f"${stats['total_value']:.2f}"
                        )

        except Exception as e:
            logger.error(f"Error fetching trade summary: {e}")
            st.error(f"❌ Error: {str(e)}")

    st.markdown("---")

    # Recent trades
    st.subheader("📜 Recent Trades")

    with st.spinner("Loading trade records..."):
        try:
            trades = client.get_trades()

            if trades:
                df = pd.DataFrame(trades)
                st.success(f"Found {len(df)} trade records")

                st.dataframe(
                    df[['trade_type', 'quantity', 'price_per_unit', 'total_value', 'trade_date', 'payment_method']].head(20),
                    use_container_width=True
                )

            else:
                st.warning("No trade records found")

        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            st.error(f"❌ Error: {str(e)}")


def render_admin_section():
    """
    Render admin dashboard (protected section).

    Educational Note:
    This demonstrates role-based access. Only users with appropriate
    permissions can view this section.
    """
    st.header("📊 Admin Dashboard")

    if not require_authentication(TRADING_FORT_API):
        return

    st.info("🔐 This section demonstrates protected endpoint access")

    st.markdown("""
    **Educational Note:**

    The admin stats endpoint requires authentication. The API:
    1. Checks for a valid token in the Authorization header
    2. Verifies the token hasn't expired
    3. Extracts user information from the token
    4. Returns comprehensive statistics

    Try accessing this with different user roles to see permissions in action.
    """)

    if st.button("🔓 Get Admin Statistics", use_container_width=True):
        client = get_authenticated_client('trading', TRADING_FORT_API)

        if client:
            with st.spinner("Fetching admin statistics..."):
                try:
                    stats = client.get_admin_stats()

                    if stats:
                        st.success(f"✅ Statistics retrieved by: {stats['requested_by']}")

                        # Display statistics
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### 📦 Inventory Stats")
                            inv = stats['inventory']
                            st.metric("Total Items", inv['total_items'])
                            st.metric("Total Quantity", inv['total_quantity'])
                            st.metric("Total Value", f"${inv['total_value']:.2f}")

                        with col2:
                            st.markdown("#### 💼 Trade Stats")
                            trades = stats['catches']
                            st.metric("Total Records", trades['total_records'])
                            st.metric("Total Items Traded", trades['total_fish'])

                        # System stats
                        st.markdown("#### 💾 System Information")
                        sys = stats['system']
                        st.metric("Disk Usage", f"{sys['disk_percent_used']:.1f}%")
                        st.progress(sys['disk_percent_used'] / 100)

                        # Full JSON
                        with st.expander("📋 Full Statistics JSON"):
                            st.json(stats)

                    else:
                        st.error("Failed to retrieve statistics")

                except Exception as e:
                    logger.error(f"Error getting admin stats: {e}")
                    if "401" in str(e) or "Unauthorized" in str(e):
                        st.error("❌ Unauthorized: Your token may have expired or be invalid")
                        st.info("💡 Try logging out and logging in again")
                    else:
                        st.error(f"❌ Error: {str(e)}")


# ============================================================================
# Helper Functions
# ============================================================================

def get_goods():
    """Helper to fetch goods with error handling."""
    try:
        client = get_authenticated_client('trading', TRADING_FORT_API)
        if client:
            return client.get_goods()
    except Exception as e:
        logger.error(f"Error fetching goods: {e}")
    return None


def get_traders():
    """Helper to fetch traders with error handling."""
    try:
        client = get_authenticated_client('trading', TRADING_FORT_API)
        if client:
            return client.get_traders()
    except Exception as e:
        logger.error(f"Error fetching traders: {e}")
    return None
