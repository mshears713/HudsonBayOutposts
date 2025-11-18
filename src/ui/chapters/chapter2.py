"""
Chapter 2: SSH Command Execution and Remote Operations

This module provides the Streamlit interface for Chapter 2, focusing on
SSH remote command execution and system management.

Educational Focus:
- SSH command execution
- Remote system administration
- Understanding Linux commands
- Secure remote access patterns
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models.outpost import Outpost
from src.ui.components.ssh_terminal import render_ssh_terminal


def render_chapter2_page():
    """
    Main render function for Chapter 2.

    Educational Note:
    This chapter teaches SSH command execution and remote system management,
    building on the API knowledge from Chapter 1.
    """
    st.title("🖥️ Chapter 2: Remote Command Execution")

    st.markdown("""
    ### Master SSH and Remote Operations

    In this chapter, you'll learn to execute commands on remote Raspberry Pi outposts
    using SSH (Secure Shell). This is a fundamental skill for managing distributed systems.

    #### Learning Objectives:
    - 🔐 Understand SSH authentication
    - 💻 Execute remote shell commands
    - 📊 Monitor system resources remotely
    - 🔍 Explore file systems via command line
    - 📝 Read and analyze log files

    ---
    """)

    # Select outpost
    outpost = select_outpost()

    if not outpost:
        render_setup_guide()
        return

    # Main content tabs
    tab1, tab2, tab3 = st.tabs([
        "🖥️ Terminal",
        "📊 System Monitor",
        "📚 Learning Guide"
    ])

    with tab1:
        render_terminal_tab(outpost)

    with tab2:
        render_system_monitor_tab(outpost)

    with tab3:
        render_learning_guide_tab()


def select_outpost() -> Optional[Outpost]:
    """
    Let user select an outpost from configured ones.

    Returns:
        Selected outpost or None
    """
    if 'outposts' not in st.session_state or not st.session_state.outposts:
        return None

    outposts = st.session_state.outposts

    # Outpost selection
    with st.expander("🏰 Select Outpost", expanded=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            outpost_names = [f"{o.name} ({o.outpost_type.value})" for o in outposts]
            selected_name = st.selectbox(
                "Choose an outpost",
                outpost_names,
                key="chapter2_outpost"
            )

            selected_idx = outpost_names.index(selected_name)
            selected_outpost = outposts[selected_idx]

        with col2:
            st.metric("Type", selected_outpost.outpost_type.value.title())

        st.caption(f"📡 IP Address: `{selected_outpost.ip_address}:{selected_outpost.ssh_port}`")

    return selected_outpost


def render_setup_guide():
    """Display setup instructions if no outposts configured."""
    st.warning("⚠️ No outposts configured!")

    st.markdown("""
    ### Setup Required

    To complete this chapter, you need to:

    1. **Add an outpost** in the Outposts page
    2. **Enable SSH** on your Raspberry Pi
    3. **Configure credentials** for SSH access

    #### SSH Setup on Raspberry Pi:

    ```bash
    # Enable SSH
    sudo raspi-config
    # Select: Interface Options → SSH → Enable

    # Or enable via command
    sudo systemctl enable ssh
    sudo systemctl start ssh
    ```

    #### Testing SSH Connection:

    ```bash
    # From your laptop
    ssh pi@<raspberry-pi-ip>
    # Default password is usually 'raspberry'
    ```

    💡 **Tip**: Use Demo Mode to explore without hardware!
    """)


def render_terminal_tab(outpost: Outpost):
    """
    Render the SSH terminal tab.

    Args:
        outpost: The selected outpost
    """
    st.markdown("""
    Use this terminal to execute commands on the remote outpost. Try the
    quick command buttons or enter your own commands.

    **Safety First:**
    - Start with simple commands like `pwd`, `whoami`, `ls`
    - Avoid destructive commands like `rm -rf`
    - Each command runs independently (no persistent session)
    """)

    st.divider()

    # Render SSH terminal component
    render_ssh_terminal(outpost, default_username="pi")

    # Command suggestions
    st.divider()

    with st.expander("💡 Helpful Commands to Try"):
        st.markdown("""
        ### System Information
        - `uname -a` - Show system information
        - `hostname` - Display hostname
        - `uptime` - Show how long system has been running
        - `whoami` - Display current user

        ### File System
        - `pwd` - Print working directory
        - `ls -la` - List files with details
        - `ls -lh /home/pi` - List files in home directory
        - `du -sh /home/pi/*` - Show directory sizes

        ### System Resources
        - `free -h` - Show memory usage
        - `df -h` - Show disk space
        - `top -bn1 | head -20` - Show top processes
        - `ps aux` - List all processes

        ### Network
        - `ifconfig` or `ip addr` - Show network interfaces
        - `hostname -I` - Show IP addresses
        - `ping -c 4 8.8.8.8` - Test internet connectivity

        ### Logs and Files
        - `cat /var/log/syslog | tail -50` - View recent system logs
        - `cat /etc/os-release` - Show OS information
        - `ls -la /home/pi/` - List files in home directory
        """)


def render_system_monitor_tab(outpost: Outpost):
    """
    Render system monitoring dashboard.

    Args:
        outpost: The selected outpost
    """
    st.markdown("""
    Monitor the system resources and status of your outpost.
    Click "Refresh" to update the information.
    """)

    col1, col2 = st.columns([4, 1])

    with col2:
        refresh = st.button("🔄 Refresh All", use_container_width=True)

    st.divider()

    # System Info
    st.subheader("💻 System Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown("**Hostname & OS:**")
        st.code(f"""
        Run: hostname && cat /etc/os-release | grep PRETTY_NAME
        """)
        st.caption("Use the Terminal tab to execute this command")

    with info_col2:
        st.markdown("**Uptime:**")
        st.code("Run: uptime")
        st.caption("Shows how long the system has been running")

    st.divider()

    # Resource Usage
    st.subheader("📊 Resource Usage")

    resource_col1, resource_col2 = st.columns(2)

    with resource_col1:
        st.markdown("**Memory Usage:**")
        st.code("Run: free -h")

    with resource_col2:
        st.markdown("**Disk Usage:**")
        st.code("Run: df -h")

    st.divider()

    # Processes
    st.subheader("🔄 Running Processes")

    st.markdown("**Top Processes:**")
    st.code("Run: ps aux --sort=-%mem | head -10")
    st.caption("Shows top 10 processes by memory usage")

    # Educational note
    st.info("""
    💡 **Learning Tip**: These commands give you a snapshot of the system's
    health. In production systems, you'd typically use monitoring tools that
    run these automatically and track trends over time.
    """)


def render_learning_guide_tab():
    """Render educational content for Chapter 2."""
    st.subheader("📚 Learning Guide: SSH and Remote Command Execution")

    st.markdown("""
    ### What is SSH?

    **SSH (Secure Shell)** is a network protocol for secure remote access to computers.
    It provides:

    - 🔐 **Encryption**: All communication is encrypted
    - 🔑 **Authentication**: Verifies identity using passwords or keys
    - 🛡️ **Integrity**: Ensures data isn't tampered with in transit

    ### How SSH Works

    ```
    1. Client connects to server on port 22 (default)
    2. Server sends its public key
    3. Client verifies server identity
    4. Client sends authentication (password or key)
    5. Encrypted tunnel established
    6. Commands sent through tunnel
    7. Results returned to client
    ```

    ### Authentication Methods

    #### Password Authentication
    - Simplest method
    - User enters password for each connection
    - Less secure than keys
    - Vulnerable to brute force attacks

    #### Key-Based Authentication
    - More secure
    - Uses public/private key pairs
    - No password needed after setup
    - Recommended for production

    **Setting up SSH keys:**

    ```bash
    # On your laptop
    ssh-keygen -t rsa -b 4096

    # Copy key to Pi
    ssh-copy-id pi@<pi-ip>

    # Now you can connect without password
    ssh pi@<pi-ip>
    ```

    ### Understanding Command Output

    When you run a command via SSH:

    1. **Standard Output (stdout)**: Normal program output
    2. **Standard Error (stderr)**: Error messages and warnings
    3. **Exit Code**: 0 = success, non-zero = error

    ### Common Linux Commands

    #### Navigation
    - `pwd` - Print working directory
    - `cd <dir>` - Change directory
    - `ls` - List directory contents
    - `ls -la` - List with details and hidden files

    #### File Operations
    - `cat <file>` - Display file contents
    - `less <file>` - View file with pagination
    - `tail -f <file>` - Follow file updates (logs)
    - `grep <pattern> <file>` - Search file for pattern

    #### System Information
    - `uname -a` - System information
    - `df -h` - Disk space (human-readable)
    - `free -h` - Memory usage
    - `ps aux` - Process list
    - `top` - Real-time process monitor

    #### Process Management
    - `ps aux` - List all processes
    - `kill <pid>` - Terminate process
    - `killall <name>` - Kill by name
    - `systemctl status <service>` - Check service status

    ### Best Practices

    ✅ **Do:**
    - Use SSH keys instead of passwords
    - Keep software updated
    - Use strong, unique passwords
    - Review command before executing
    - Back up important data

    ❌ **Don't:**
    - Share SSH keys
    - Use default passwords
    - Run unknown commands as root
    - Disable firewall completely
    - Ignore security updates

    ### Security Considerations

    - **Principle of Least Privilege**: Only give users the minimum permissions needed
    - **Firewall**: Only expose necessary ports (SSH on 22)
    - **Fail2Ban**: Automatically block repeated failed login attempts
    - **Regular Updates**: Keep system and packages updated
    - **Monitoring**: Track login attempts and system activity

    ### Troubleshooting SSH Issues

    **Connection Refused:**
    - Check SSH service is running: `sudo systemctl status ssh`
    - Verify firewall allows port 22
    - Confirm correct IP address

    **Permission Denied:**
    - Check username and password
    - Verify SSH is enabled on Pi
    - Check key permissions (should be 600)

    **Timeout:**
    - Verify network connectivity
    - Check Pi is powered on
    - Confirm same network/subnet

    ### Next Steps

    In Chapter 3, you'll learn to:
    - Build custom APIs with authentication
    - Handle file uploads and downloads
    - Manage structured data across outposts
    - Orchestrate multi-node operations

    ---

    💡 **Practice Tip**: Try executing various commands in the Terminal tab.
    Understanding command-line operations is essential for DevOps and system
    administration!
    """)


# Make module callable directly
if __name__ == "__main__":
    st.set_page_config(page_title="Chapter 2", layout="wide")
    render_chapter2_page()
