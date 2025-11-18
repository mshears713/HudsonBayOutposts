"""
SSH Terminal Component for Streamlit

This module provides a reusable SSH terminal component that allows users
to execute remote commands on Raspberry Pi outposts.

Educational Focus:
- Understanding SSH remote command execution
- Handling command output and errors
- Secure remote operations
- User input validation
"""

import streamlit as st
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models.outpost import Outpost
from src.ssh_module.executor import SSHExecutor, SSHResult


def render_ssh_terminal(
    outpost: Outpost,
    default_username: str = "pi",
    show_credentials: bool = True,
    allowed_commands: Optional[list] = None
):
    """
    Render an interactive SSH terminal for executing remote commands.

    Args:
        outpost: The outpost to connect to
        default_username: Default SSH username
        show_credentials: Whether to show credential inputs
        allowed_commands: List of allowed commands (None = all allowed)

    Educational Note:
    This component demonstrates safe SSH command execution with
    proper error handling and user feedback.
    """
    st.subheader("🖥️ Remote Command Terminal")

    st.markdown(f"""
    Execute commands on **{outpost.name}** via SSH.

    **Safety Notes:**
    - Commands execute with the permissions of the SSH user
    - Be careful with system-modifying commands
    - Command output is displayed below
    """)

    # Credentials section
    if show_credentials:
        with st.expander("🔑 SSH Credentials", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                username = st.text_input(
                    "Username",
                    value=default_username,
                    key=f"ssh_user_{outpost.name}",
                    help="SSH username (typically 'pi' for Raspberry Pi)"
                )

            with col2:
                password = st.text_input(
                    "Password",
                    type="password",
                    key=f"ssh_pass_{outpost.name}",
                    help="SSH password (leave empty if using key-based auth)"
                )

            st.caption("💡 **Tip**: Key-based authentication is more secure than passwords!")
    else:
        username = default_username
        password = st.session_state.get(f"ssh_pass_{outpost.name}", "")

    # Command input
    st.divider()

    # Quick command buttons
    st.markdown("**Quick Commands:**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📁 List Files", use_container_width=True):
            st.session_state[f"ssh_cmd_{outpost.name}"] = "ls -la ~"

    with col2:
        if st.button("💾 Disk Usage", use_container_width=True):
            st.session_state[f"ssh_cmd_{outpost.name}"] = "df -h"

    with col3:
        if st.button("🔄 Processes", use_container_width=True):
            st.session_state[f"ssh_cmd_{outpost.name}"] = "ps aux | head -20"

    with col4:
        if st.button("📊 System Info", use_container_width=True):
            st.session_state[f"ssh_cmd_{outpost.name}"] = "uname -a && uptime"

    # Custom command input
    command = st.text_input(
        "Command",
        key=f"ssh_cmd_{outpost.name}",
        placeholder="Enter SSH command (e.g., 'ls -la', 'pwd', 'whoami')",
        help="Enter any valid shell command"
    )

    # Validation warnings
    if command:
        if any(dangerous in command.lower() for dangerous in ['rm -rf', 'dd if=', 'mkfs', ':(){:|:&};:']):
            st.error("⚠️ **DANGER**: This command could damage the system. Please use with extreme caution!")

    # Execute button
    col1, col2 = st.columns([3, 1])

    with col1:
        execute_btn = st.button(
            "▶️ Execute Command",
            type="primary",
            use_container_width=True,
            disabled=not command
        )

    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
        if clear_btn:
            if f"ssh_output_{outpost.name}" in st.session_state:
                del st.session_state[f"ssh_output_{outpost.name}"]

    # Execute command
    if execute_btn and command:
        execute_ssh_command(outpost, command, username, password, allowed_commands)

    # Display output
    if f"ssh_output_{outpost.name}" in st.session_state:
        render_command_output(st.session_state[f"ssh_output_{outpost.name}"])


def execute_ssh_command(
    outpost: Outpost,
    command: str,
    username: str,
    password: Optional[str],
    allowed_commands: Optional[list] = None
):
    """
    Execute an SSH command and store results in session state.

    Args:
        outpost: The outpost to connect to
        command: Command to execute
        username: SSH username
        password: SSH password (optional)
        allowed_commands: List of allowed commands for validation

    Educational Note:
    This demonstrates proper SSH execution with error handling
    and user feedback at each step.
    """
    # Validate command against allowed list
    if allowed_commands is not None:
        command_base = command.split()[0] if command else ""
        if command_base not in allowed_commands:
            st.error(f"❌ Command '{command_base}' is not in the allowed list.")
            st.info(f"Allowed commands: {', '.join(allowed_commands)}")
            return

    # Execute command
    with st.spinner(f"🔄 Executing command on {outpost.name}..."):
        try:
            # Create SSH executor
            executor = SSHExecutor(
                hostname=outpost.ip_address,
                username=username,
                password=password if password else None,
                port=outpost.ssh_port,
                timeout=10
            )

            # Connect
            if not executor.connect():
                st.error(f"❌ Failed to connect to {outpost.name}")
                st.session_state[f"ssh_output_{outpost.name}"] = {
                    "success": False,
                    "error": "Connection failed. Check credentials and network connectivity."
                }
                return

            # Execute command
            result = executor.execute_command(command, timeout=30)

            # Disconnect
            executor.disconnect()

            # Store result
            st.session_state[f"ssh_output_{outpost.name}"] = {
                "success": result.success,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "error": result.error_message
            }

            # Show success/failure notification
            if result.success:
                st.success(f"✅ Command executed successfully (exit code: {result.exit_code})")
            else:
                st.error(f"❌ Command failed (exit code: {result.exit_code})")

        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.session_state[f"ssh_output_{outpost.name}"] = {
                "success": False,
                "error": str(e)
            }


def render_command_output(output: Dict[str, Any]):
    """
    Render the command execution output.

    Args:
        output: Dictionary containing command results

    Educational Note:
    This demonstrates how to display command output in a user-friendly way,
    separating standard output from errors.
    """
    st.divider()
    st.markdown("### 📤 Command Output")

    if not output.get("success", False):
        st.error("❌ Command Execution Failed")
        st.code(output.get("error", "Unknown error"), language="text")
        return

    # Display command that was executed
    st.caption(f"**Command:** `{output.get('command', 'N/A')}`")
    st.caption(f"**Exit Code:** {output.get('exit_code', 'N/A')}")

    # Standard output
    stdout = output.get("stdout", "").strip()
    if stdout:
        st.markdown("**Standard Output:**")
        st.code(stdout, language="bash")
    else:
        st.info("(No output)")

    # Standard error (if any)
    stderr = output.get("stderr", "").strip()
    if stderr:
        st.markdown("**Standard Error:**")
        st.code(stderr, language="bash")

    # Educational note
    with st.expander("📚 Understanding Command Output"):
        st.markdown("""
        #### Exit Codes
        - **0**: Command succeeded
        - **Non-zero**: Command failed (specific meaning depends on command)

        #### Standard Output (stdout)
        The normal output of the command. This is what you see when running
        commands successfully in a terminal.

        #### Standard Error (stderr)
        Error messages and warnings. A command can have stderr output even
        if it succeeds (exit code 0).

        #### Common Commands
        - `ls -la`: List files with details
        - `pwd`: Print working directory
        - `whoami`: Show current user
        - `df -h`: Show disk space
        - `ps aux`: Show running processes
        - `cat <file>`: Display file contents
        """)


def render_command_history(outpost: Outpost):
    """
    Render command history for an outpost.

    Args:
        outpost: The outpost to show history for

    Educational Note:
    Keeping command history helps users learn from previous commands
    and track their actions.
    """
    history_key = f"ssh_history_{outpost.name}"

    if history_key not in st.session_state:
        st.session_state[history_key] = []

    if not st.session_state[history_key]:
        st.info("No command history yet. Execute some commands to see them here!")
        return

    st.markdown("### 📜 Command History")

    for i, entry in enumerate(reversed(st.session_state[history_key][-10:])):
        with st.expander(f"Command {len(st.session_state[history_key]) - i}: {entry['command']}", expanded=False):
            st.caption(f"Exit Code: {entry.get('exit_code', 'N/A')}")
            st.caption(f"Status: {'✅ Success' if entry.get('success') else '❌ Failed'}")

            if entry.get('stdout'):
                st.code(entry['stdout'][:500], language="bash")
