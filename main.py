"""
Raspberry Pi Frontier - Main Streamlit Application

This is the central dashboard for the Raspberry Pi Frontier learning adventure.
It provides a multi-page navigation interface for managing distributed Raspberry Pi
outposts, visualizing data, and tracking user progress.

Educational Note:
Streamlit is a Python framework for building interactive web applications.
It uses a declarative syntax where you write Python code and Streamlit
automatically creates the UI. The app reruns from top to bottom on each
user interaction.
"""

import streamlit as st
from pathlib import Path
import sys

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.models import UserProfile, ChapterStatus
from src.models.outpost import Outpost, OutpostType, OutpostStatus

# Page configuration
st.set_page_config(
    page_title="Raspberry Pi Frontier",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """
    Initialize Streamlit session state variables.

    Educational Note:
    Session state allows you to persist data across reruns of the app.
    It's similar to cookies or local storage in web development.
    Each user session has its own isolated state.
    """
    # Initialize user profile if not exists
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = UserProfile(
            username="explorer",
            display_name="Frontier Explorer",
            email=None
        )

    # Initialize outposts list if not exists
    if 'outposts' not in st.session_state:
        st.session_state.outposts = []

    # Initialize current page if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"

    # Initialize demo mode flag
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False


def render_sidebar():
    """
    Render the sidebar with navigation and user information.

    Educational Note:
    Sidebars in Streamlit provide persistent navigation and context
    while the main area changes based on user selection.
    """
    with st.sidebar:
        # Title and branding
        st.title("🏔️ Raspberry Pi Frontier")
        st.markdown("*Hudson Bay Outposts Network*")
        st.divider()

        # User profile section
        user = st.session_state.user_profile
        st.subheader(f"👤 {user.display_name}")

        # Progress overview
        progress = user.get_overall_progress()
        st.progress(progress / 100, text=f"Overall Progress: {progress:.1f}%")

        current_chapter = user.get_current_chapter()
        if current_chapter:
            st.caption(f"📖 Current: Chapter {current_chapter}")

        st.divider()

        # Navigation menu
        st.subheader("📍 Navigation")

        pages = [
            ("Home", "🏠"),
            ("Outposts", "🏰"),
            ("Chapter 1", "1️⃣"),
            ("Chapter 2", "2️⃣"),
            ("Chapter 3", "3️⃣"),
            ("Settings", "⚙️"),
            ("Help", "❓")
        ]

        for page_name, icon in pages:
            if st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_name else "secondary"
            ):
                st.session_state.current_page = page_name
                st.rerun()

        st.divider()

        # Quick stats
        st.caption("📊 Quick Stats")
        st.caption(f"Outposts: {len(st.session_state.outposts)}")
        online_count = sum(
            1 for o in st.session_state.outposts
            if o.status == OutpostStatus.ONLINE
        )
        st.caption(f"Online: {online_count}")
        st.caption(f"Achievements: {len(user.achievements)}")


def render_home_page():
    """Render the home page with welcome information."""
    st.title("🏔️ Welcome to Raspberry Pi Frontier!")

    st.markdown("""
    ### An Interactive Learning Adventure

    Welcome to the **Raspberry Pi Frontier**, an immersive journey through distributed
    systems, API design, and remote server management. You'll build and manage a network
    of Raspberry Pi "outposts" representing Hudson Bay Company frontier forts.

    #### 🎯 What You'll Learn

    - **SSH Mastery**: Securely manage remote Raspberry Pi nodes
    - **RESTful APIs**: Design and consume JSON APIs with FastAPI
    - **Multi-Endpoint Workflows**: Orchestrate distributed operations
    - **Authentication**: Implement token-based security
    - **Distributed Systems**: Data synchronization and visualization

    #### 🗺️ Your Journey

    This adventure spans **10 chapters**, each building on the previous:

    1. **Foundations** - SSH setup and basic connectivity
    2. **File Operations** - Remote file management
    3. **API Development** - Building your first endpoints
    4. **Authentication** - Securing your APIs
    5. **Multi-Node Workflows** - Coordinating between outposts
    6. And more exciting chapters to come!
    """)

    # Current progress
    st.divider()
    st.subheader("📈 Your Progress")

    user = st.session_state.user_profile
    cols = st.columns(3)

    with cols[0]:
        st.metric("Overall Progress", f"{user.get_overall_progress():.0f}%")

    with cols[1]:
        completed = sum(
            1 for ch in user.chapters.values()
            if ch.status == ChapterStatus.COMPLETED
        )
        st.metric("Chapters Completed", f"{completed}/10")

    with cols[2]:
        st.metric("Achievements", len(user.achievements))

    # Getting started section
    st.divider()
    st.subheader("🚀 Getting Started")

    st.markdown("""
    #### Next Steps:

    1. **Configure Your Outposts** - Go to the Outposts page to add your Raspberry Pis
    2. **Start Chapter 1** - Begin your learning journey
    3. **Explore the Dashboard** - Familiarize yourself with the tools

    #### Need Help?

    - Click the **Help** button in the sidebar for guides and tutorials
    - Check the **Settings** page to customize your experience
    - All UI elements have tooltips with additional information
    """)

    # Demo mode toggle
    st.divider()
    demo_mode = st.checkbox(
        "🧪 Demo Mode (simulate outposts without real Raspberry Pis)",
        value=st.session_state.demo_mode,
        help="Enable this if you don't have physical Raspberry Pis to test with"
    )
    st.session_state.demo_mode = demo_mode


def render_outposts_page():
    """Render the outposts management page."""
    st.title("🏰 Outpost Management")

    st.markdown("""
    Manage your network of Raspberry Pi outposts. Each outpost represents a frontier
    fort with its own API services and data.
    """)

    # Add new outpost form
    with st.expander("➕ Add New Outpost", expanded=len(st.session_state.outposts) == 0):
        with st.form("add_outpost"):
            st.subheader("Outpost Configuration")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Outpost Name", placeholder="Fort William")
                outpost_type = st.selectbox(
                    "Type",
                    options=[t.value for t in OutpostType],
                    format_func=lambda x: x.title()
                )
                ip_address = st.text_input("IP Address", placeholder="192.168.1.100")

            with col2:
                port = st.number_input("API Port", value=8000, min_value=1, max_value=65535)
                ssh_port = st.number_input("SSH Port", value=22, min_value=1, max_value=65535)

            submitted = st.form_submit_button("Add Outpost", type="primary")

            if submitted:
                if name and ip_address:
                    new_outpost = Outpost(
                        name=name,
                        outpost_type=OutpostType(outpost_type),
                        ip_address=ip_address,
                        port=port,
                        ssh_port=ssh_port
                    )
                    st.session_state.outposts.append(new_outpost)
                    st.success(f"✅ Added outpost: {name}")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")

    # Display existing outposts
    st.divider()
    st.subheader("📡 Connected Outposts")

    if not st.session_state.outposts:
        st.info("No outposts configured yet. Add your first outpost above!")
    else:
        for idx, outpost in enumerate(st.session_state.outposts):
            with st.container():
                cols = st.columns([3, 1, 1, 1])

                with cols[0]:
                    status_emoji = "🟢" if outpost.is_online else "🔴"
                    st.markdown(f"### {status_emoji} {outpost.name}")
                    st.caption(f"Type: {outpost.outpost_type.value.title()} | {outpost.api_base_url}")

                with cols[1]:
                    st.metric("Status", outpost.status.value.title())

                with cols[2]:
                    if st.button("🔄 Test", key=f"test_{idx}"):
                        st.info("Testing connection... (not implemented in Phase 1)")

                with cols[3]:
                    if st.button("🗑️ Remove", key=f"remove_{idx}"):
                        st.session_state.outposts.pop(idx)
                        st.rerun()

                st.divider()


def render_chapter_placeholder(chapter_num: int):
    """Render a placeholder for chapter pages."""
    st.title(f"Chapter {chapter_num}")
    st.info(f"Chapter {chapter_num} content will be implemented in Phase 2!")


def render_settings_page():
    """Render the settings page."""
    st.title("⚙️ Settings")

    st.subheader("User Profile")

    user = st.session_state.user_profile

    with st.form("user_settings"):
        display_name = st.text_input("Display Name", value=user.display_name)
        email = st.text_input("Email (optional)", value=user.email or "")

        if st.form_submit_button("Save Settings"):
            user.display_name = display_name
            user.email = email if email else None
            st.success("✅ Settings saved!")

    st.divider()
    st.subheader("Preferences")

    demo_mode = st.checkbox(
        "Demo Mode",
        value=st.session_state.demo_mode,
        help="Simulate outposts without real Raspberry Pis"
    )
    st.session_state.demo_mode = demo_mode


def render_help_page():
    """Render the help page."""
    st.title("❓ Help & Documentation")

    st.markdown("""
    ### Getting Help

    #### 📚 Documentation

    - **Setup Guide**: Instructions for configuring Raspberry Pis
    - **API Reference**: Documentation for all API endpoints
    - **Troubleshooting**: Common issues and solutions

    #### 🎓 Learning Resources

    - **Streamlit**: https://docs.streamlit.io/
    - **FastAPI**: https://fastapi.tiangolo.com/
    - **Paramiko SSH**: https://docs.paramiko.org/

    #### 💡 Tips

    - Hover over UI elements for helpful tooltips
    - Use Demo Mode to explore without hardware
    - Progress through chapters sequentially for best results

    #### 🐛 Troubleshooting

    **Cannot connect to Raspberry Pi:**
    - Verify SSH is enabled on the Pi
    - Check that you're on the same network
    - Confirm the IP address is correct

    **API errors:**
    - Ensure FastAPI server is running on the Pi
    - Check firewall settings
    - Verify port numbers match configuration
    """)


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Render current page
    page = st.session_state.current_page

    if page == "Home":
        render_home_page()
    elif page == "Outposts":
        render_outposts_page()
    elif page == "Chapter 1":
        render_chapter_placeholder(1)
    elif page == "Chapter 2":
        render_chapter_placeholder(2)
    elif page == "Chapter 3":
        render_chapter_placeholder(3)
    elif page == "Settings":
        render_settings_page()
    elif page == "Help":
        render_help_page()


if __name__ == "__main__":
    main()
