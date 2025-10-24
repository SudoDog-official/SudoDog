"""
SudoDog - Security for AI Agents
Sandboxing and monitoring for AI agents in one command
"""

__version__ = '0.1.0'
__author__ = 'SudoDog'
__license__ = 'MIT'

from .monitor import AgentMonitor, AgentSession

__all__ = ['AgentMonitor', 'AgentSession']
