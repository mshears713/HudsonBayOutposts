"""
SSH module for remote Raspberry Pi management.

This package provides secure SSH-based remote command execution
and file transfer capabilities using Paramiko.
"""

from src.ssh_module.executor import (
    SSHExecutor,
    SSHResult,
    execute_remote_command
)

__all__ = [
    'SSHExecutor',
    'SSHResult',
    'execute_remote_command',
]
