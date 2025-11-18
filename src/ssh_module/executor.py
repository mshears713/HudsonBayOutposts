"""
SSH command execution module using Paramiko.

This module provides secure remote command execution capabilities for
managing Raspberry Pi outposts via SSH. It handles connection management,
command execution, file transfers, and error handling.

Educational Note:
SSH (Secure Shell) provides encrypted remote access to servers. Paramiko
is a Python implementation of SSHv2 that allows programmatic SSH operations.
"""

import paramiko
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
import logging
from io import StringIO

# Configure logging for SSH operations
logger = logging.getLogger(__name__)


@dataclass
class SSHResult:
    """
    Container for SSH command execution results.

    Attributes:
        success: Whether the command executed successfully
        stdout: Standard output from the command
        stderr: Standard error output
        exit_code: Command exit code (0 typically means success)
        error_message: Human-readable error message if failed
    """

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    error_message: Optional[str] = None

    def __str__(self) -> str:
        """String representation of the result."""
        if self.success:
            return f"Success (exit code {self.exit_code}): {self.stdout}"
        else:
            return f"Failed (exit code {self.exit_code}): {self.error_message or self.stderr}"


class SSHExecutor:
    """
    Manages SSH connections and command execution for Raspberry Pi outposts.

    This class provides a safe, reusable interface for remote operations
    including command execution and file transfers.

    Educational Note:
    SSH connections require authentication. We support both password-based
    and key-based authentication. Key-based is more secure and recommended
    for production use.
    """

    def __init__(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22,
        timeout: int = 10
    ):
        """
        Initialize SSH executor.

        Args:
            hostname: IP address or hostname of the Raspberry Pi
            username: SSH username (typically 'pi' for Raspberry Pi)
            password: Password for authentication (optional if using keys)
            key_filename: Path to private key file for key-based auth
            port: SSH port (default 22)
            timeout: Connection timeout in seconds
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.timeout = timeout
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self) -> bool:
        """
        Establish SSH connection to the remote host.

        Returns:
            True if connection successful, False otherwise

        Educational Note:
        AutoAddPolicy automatically adds unknown host keys. In production,
        you'd want to verify host keys manually for security. We use it
        here for educational simplicity.
        """
        try:
            self.client = paramiko.SSHClient()
            # Auto-add unknown hosts (not recommended for production)
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Attempt connection
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                key_filename=self.key_filename,
                timeout=self.timeout,
                allow_agent=False,  # Don't use SSH agent
                look_for_keys=True if self.key_filename else False
            )

            logger.info(f"Successfully connected to {self.hostname}")
            return True

        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {self.hostname}")
            return False
        except paramiko.SSHException as e:
            logger.error(f"SSH error connecting to {self.hostname}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.hostname}: {e}")
            return False

    def disconnect(self) -> None:
        """
        Close the SSH connection.

        Educational Note:
        Always close connections when done to free resources and
        maintain security.
        """
        if self.client:
            self.client.close()
            logger.info(f"Disconnected from {self.hostname}")
            self.client = None

    def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None
    ) -> SSHResult:
        """
        Execute a command on the remote host.

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds (optional)

        Returns:
            SSHResult containing output and status

        Educational Note:
        Be careful with command injection! Always validate and sanitize
        commands before execution, especially if they include user input.
        """
        if not self.client:
            return SSHResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error_message="Not connected to SSH host"
            )

        try:
            # Execute the command
            logger.info(f"Executing command on {self.hostname}: {command}")
            stdin, stdout, stderr = self.client.exec_command(
                command,
                timeout=timeout or self.timeout
            )

            # Wait for command to complete and get results
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')

            success = exit_code == 0

            logger.info(
                f"Command completed with exit code {exit_code} on {self.hostname}"
            )

            return SSHResult(
                success=success,
                stdout=stdout_text,
                stderr=stderr_text,
                exit_code=exit_code,
                error_message=None if success else "Command failed"
            )

        except paramiko.SSHException as e:
            logger.error(f"SSH error executing command: {e}")
            return SSHResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error_message=f"SSH error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error executing command: {e}")
            return SSHResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error_message=f"Unexpected error: {str(e)}"
            )

    def upload_file(
        self,
        local_path: str,
        remote_path: str
    ) -> bool:
        """
        Upload a file to the remote host via SFTP.

        Args:
            local_path: Path to local file
            remote_path: Destination path on remote host

        Returns:
            True if upload successful, False otherwise

        Educational Note:
        SFTP (SSH File Transfer Protocol) provides secure file transfer
        over SSH connections.
        """
        if not self.client:
            logger.error("Not connected to SSH host")
            return False

        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            logger.info(f"Uploaded {local_path} to {self.hostname}:{remote_path}")
            return True

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False

    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> bool:
        """
        Download a file from the remote host via SFTP.

        Args:
            remote_path: Path to file on remote host
            local_path: Local destination path

        Returns:
            True if download successful, False otherwise
        """
        if not self.client:
            logger.error("Not connected to SSH host")
            return False

        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            logger.info(f"Downloaded {self.hostname}:{remote_path} to {local_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False

    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()


def execute_remote_command(
    hostname: str,
    username: str,
    command: str,
    password: Optional[str] = None,
    key_filename: Optional[str] = None,
    port: int = 22
) -> SSHResult:
    """
    Convenience function to execute a single command with automatic connection handling.

    Args:
        hostname: IP address or hostname of the Raspberry Pi
        username: SSH username
        command: Command to execute
        password: Password for authentication (optional)
        key_filename: Path to private key file (optional)
        port: SSH port (default 22)

    Returns:
        SSHResult containing command output and status

    Educational Note:
    This is a simplified interface for one-off commands. For multiple
    commands, use SSHExecutor with context manager to reuse connections.

    Example:
        result = execute_remote_command(
            hostname="192.168.1.100",
            username="pi",
            password="raspberry",
            command="ls -la /home/pi"
        )
        print(result.stdout)
    """
    with SSHExecutor(
        hostname=hostname,
        username=username,
        password=password,
        key_filename=key_filename,
        port=port
    ) as executor:
        return executor.execute_command(command)
