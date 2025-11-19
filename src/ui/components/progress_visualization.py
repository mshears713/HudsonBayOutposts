"""
Enhanced Progress Visualization Components for Streamlit

This module provides advanced progress tracking and visualization components
for the Streamlit dashboard, improving user experience during long operations.

Educational Note:
Progress indicators are crucial for UX in applications with time-consuming operations.
Good progress visualization:
- Sets user expectations
- Reduces perceived wait time
- Provides feedback that system is working
- Allows user to estimate completion time

Phase 4 Feature (Step 37):
Production-quality progress bars, spinners, status indicators, and step trackers.
"""

import streamlit as st
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Progress State Management
# ============================================================================

class ProgressState(Enum):
    """
    Progress state enumeration.

    Educational Note:
    Explicit state management prevents inconsistencies and
    makes state transitions clear.
    """
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressInfo:
    """
    Dataclass for progress information.

    Educational Note:
    Dataclasses provide clean, typed data structures for
    tracking complex state.
    """
    total_steps: int
    current_step: int = 0
    state: ProgressState = ProgressState.NOT_STARTED
    current_message: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage (0-100)."""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100

    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Calculate elapsed time."""
        if self.start_time is None:
            return None
        end = self.end_time or datetime.now()
        return end - self.start_time

    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        """Estimate remaining time based on current progress."""
        if self.start_time is None or self.current_step == 0:
            return None

        elapsed = self.elapsed_time
        if elapsed is None:
            return None

        time_per_step = elapsed / self.current_step
        remaining_steps = self.total_steps - self.current_step

        return time_per_step * remaining_steps


# ============================================================================
# Basic Progress Components
# ============================================================================

def render_progress_bar(
    progress: float,
    label: str = "",
    show_percentage: bool = True
):
    """
    Render an enhanced progress bar.

    Educational Note:
    Progress bars give users visual feedback about completion status.
    Always include percentage or other quantitative indicator.

    Args:
        progress: Progress value (0.0 to 1.0)
        label: Label to display above progress bar
        show_percentage: Whether to show percentage
    """
    if label:
        st.write(f"**{label}**")

    if show_percentage:
        st.write(f"{progress*100:.1f}%")

    st.progress(progress)


def render_step_progress(
    current_step: int,
    total_steps: int,
    step_name: str = ""
):
    """
    Render progress for multi-step operations.

    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        step_name: Name of current step
    """
    progress = current_step / total_steps if total_steps > 0 else 0

    col1, col2 = st.columns([3, 1])

    with col1:
        st.progress(progress)
        if step_name:
            st.write(f"**Step {current_step}/{total_steps}:** {step_name}")
        else:
            st.write(f"**Step {current_step} of {total_steps}**")

    with col2:
        st.metric("Progress", f"{progress*100:.0f}%")


def render_indeterminate_progress(message: str = "Processing..."):
    """
    Render indeterminate progress indicator (spinner).

    Educational Note:
    Use spinners when you can't determine exact progress.
    Always include a descriptive message.

    Args:
        message: Message to display
    """
    with st.spinner(message):
        # This creates a context manager, user code goes inside
        pass


# ============================================================================
# Advanced Progress Tracking
# ============================================================================

class ProgressTracker:
    """
    Advanced progress tracker with time estimation.

    Educational Note:
    Tracking progress state in a class provides better organization
    and enables features like time estimation.
    """

    def __init__(self, total_steps: int, key: str = "default"):
        """
        Initialize progress tracker.

        Args:
            total_steps: Total number of steps
            key: Unique key for session state
        """
        self.key = f"progress_tracker_{key}"
        self.total_steps = total_steps

        if self.key not in st.session_state:
            st.session_state[self.key] = ProgressInfo(total_steps=total_steps)

    @property
    def progress(self) -> ProgressInfo:
        """Get current progress info."""
        return st.session_state[self.key]

    def start(self):
        """Start progress tracking."""
        self.progress.state = ProgressState.IN_PROGRESS
        self.progress.start_time = datetime.now()
        self.progress.current_step = 0

    def update(self, step: int, message: str = ""):
        """
        Update progress.

        Args:
            step: Current step number
            message: Current step message
        """
        self.progress.current_step = step
        self.progress.current_message = message

    def complete(self):
        """Mark as completed."""
        self.progress.state = ProgressState.COMPLETED
        self.progress.end_time = datetime.now()
        self.progress.current_step = self.total_steps

    def fail(self, error_message: str):
        """
        Mark as failed.

        Args:
            error_message: Error message
        """
        self.progress.state = ProgressState.FAILED
        self.progress.end_time = datetime.now()
        self.progress.error_message = error_message

    def render(self):
        """Render the progress tracker UI."""
        progress = self.progress

        # State indicator
        state_colors = {
            ProgressState.NOT_STARTED: "=5",
            ProgressState.IN_PROGRESS: "=á",
            ProgressState.COMPLETED: "=â",
            ProgressState.FAILED: "=4",
            ProgressState.CANCELLED: "«"
        }

        state_icon = state_colors.get(progress.state, "ª")

        # Progress bar
        if progress.state == ProgressState.IN_PROGRESS:
            col1, col2, col3 = st.columns([6, 2, 2])

            with col1:
                st.progress(progress.progress_percent / 100)

            with col2:
                st.metric("Step", f"{progress.current_step}/{progress.total_steps}")

            with col3:
                st.metric("Progress", f"{progress.progress_percent:.0f}%")

            # Current message
            if progress.current_message:
                st.info(f"{state_icon} {progress.current_message}")

            # Time estimates
            if progress.elapsed_time and progress.estimated_remaining:
                col1, col2 = st.columns(2)

                with col1:
                    elapsed_str = str(progress.elapsed_time).split('.')[0]
                    st.write(f"ñ Elapsed: {elapsed_str}")

                with col2:
                    remaining_str = str(progress.estimated_remaining).split('.')[0]
                    st.write(f"ó Remaining: ~{remaining_str}")

        elif progress.state == ProgressState.COMPLETED:
            st.success(f"{state_icon} Completed!")
            if progress.elapsed_time:
                elapsed_str = str(progress.elapsed_time).split('.')[0]
                st.write(f"ñ Total time: {elapsed_str}")

        elif progress.state == ProgressState.FAILED:
            st.error(f"{state_icon} Failed: {progress.error_message}")


# ============================================================================
# Step-by-Step Progress Wizard
# ============================================================================

class StepWizard:
    """
    Multi-step wizard with visual progress tracking.

    Educational Note:
    Wizards guide users through complex multi-step processes,
    showing progress and enabling forward/backward navigation.
    """

    def __init__(self, steps: List[Dict[str, Any]], key: str = "wizard"):
        """
        Initialize step wizard.

        Args:
            steps: List of step dictionaries with 'title' and 'description'
            key: Unique session state key

        Example:
            steps = [
                {'title': 'Configure', 'description': 'Set up configuration'},
                {'title': 'Execute', 'description': 'Run the operation'},
                {'title': 'Review', 'description': 'Review results'}
            ]
            wizard = StepWizard(steps)
        """
        self.steps = steps
        self.key = f"wizard_{key}"

        if f"{self.key}_current" not in st.session_state:
            st.session_state[f"{self.key}_current"] = 0

    @property
    def current_step(self) -> int:
        """Get current step index."""
        return st.session_state[f"{self.key}_current"]

    @current_step.setter
    def current_step(self, value: int):
        """Set current step index."""
        st.session_state[f"{self.key}_current"] = value

    def render_progress(self):
        """Render wizard progress indicator."""
        st.write("### Progress")

        # Progress bar
        progress = (self.current_step + 1) / len(self.steps)
        st.progress(progress)

        # Step indicators
        cols = st.columns(len(self.steps))

        for idx, (col, step) in enumerate(zip(cols, self.steps)):
            with col:
                if idx < self.current_step:
                    # Completed step
                    st.success(f" {idx + 1}")
                    st.caption(step['title'])
                elif idx == self.current_step:
                    # Current step
                    st.info(f"¶ {idx + 1}")
                    st.caption(f"**{step['title']}**")
                else:
                    # Future step
                    st.write(f"U {idx + 1}")
                    st.caption(step['title'])

        st.divider()

    def render_navigation(self):
        """Render wizard navigation buttons."""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if self.current_step > 0:
                if st.button(" Previous"):
                    self.current_step -= 1
                    st.rerun()

        with col2:
            current = self.steps[self.current_step]
            st.write(f"**{current['title']}**")
            if 'description' in current:
                st.caption(current['description'])

        with col3:
            if self.current_step < len(self.steps) - 1:
                if st.button("Next ¡"):
                    self.current_step += 1
                    st.rerun()
            else:
                if st.button(" Finish"):
                    return True  # Signal completion

        return False


# ============================================================================
# Loading States
# ============================================================================

def render_loading_state(
    items: List[str],
    load_func: Callable[[str], Any],
    success_message: str = "All items loaded successfully"
):
    """
    Render loading state for multiple items.

    Educational Note:
    This pattern shows progress while loading multiple items,
    providing feedback for each item loaded.

    Args:
        items: List of items to load
        load_func: Function that loads each item
        success_message: Message to show on completion

    Example:
        forts = ['Fishing', 'Trading', 'Hunting']
        render_loading_state(
            forts,
            lambda fort: client.get_status(fort),
            "All forts loaded"
        )
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    for idx, item in enumerate(items):
        # Update progress
        progress = (idx + 1) / len(items)
        progress_bar.progress(progress)
        status_text.write(f"Loading {item}... ({idx + 1}/{len(items)})")

        # Load item
        try:
            result = load_func(item)
            results.append((item, result, None))
        except Exception as e:
            results.append((item, None, str(e)))

    # Clear loading indicators
    progress_bar.empty()
    status_text.empty()

    # Show results
    success_count = sum(1 for _, result, error in results if error is None)

    if success_count == len(items):
        st.success(success_message)
    else:
        st.warning(f"Loaded {success_count}/{len(items)} items")

        # Show errors
        for item, _, error in results:
            if error:
                st.error(f"Failed to load {item}: {error}")

    return results


# ============================================================================
# Real-time Progress Updates
# ============================================================================

class LiveProgressMonitor:
    """
    Monitor for real-time progress updates.

    Educational Note:
    For long-running operations, real-time updates keep users
    informed and engaged.
    """

    def __init__(self, key: str = "live_monitor"):
        self.key = f"live_monitor_{key}"

        if f"{self.key}_messages" not in st.session_state:
            st.session_state[f"{self.key}_messages"] = []

    def log(self, message: str, level: str = "info"):
        """
        Add a log message.

        Args:
            message: Message text
            level: Message level (info, success, warning, error)
        """
        entry = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'message': message,
            'level': level
        }

        st.session_state[f"{self.key}_messages"].append(entry)

        # Keep only last 50 messages
        st.session_state[f"{self.key}_messages"] = \
            st.session_state[f"{self.key}_messages"][-50:]

    def render(self, max_messages: int = 10):
        """
        Render recent log messages.

        Args:
            max_messages: Maximum number of messages to show
        """
        messages = st.session_state[f"{self.key}_messages"]

        if not messages:
            st.info("No activity yet")
            return

        # Show recent messages (most recent first)
        for entry in reversed(messages[-max_messages:]):
            timestamp = entry['timestamp']
            message = entry['message']
            level = entry['level']

            icon = {
                'info': '9',
                'success': '',
                'warning': ' ',
                'error': 'L'
            }.get(level, '9')

            st.write(f"{icon} `{timestamp}` {message}")

    def clear(self):
        """Clear all messages."""
        st.session_state[f"{self.key}_messages"] = []


# ============================================================================
# Convenience Functions
# ============================================================================

def with_progress(
    items: List[Any],
    process_func: Callable[[Any], Any],
    description: str = "Processing items"
) -> List[Any]:
    """
    Process items with automatic progress display.

    Educational Note:
    This wrapper adds progress visualization to any processing loop.

    Args:
        items: Items to process
        process_func: Function to process each item
        description: Description for progress bar

    Returns:
        List of processed results

    Example:
        results = with_progress(
            forts,
            lambda fort: client.get_status(fort),
            "Fetching fort statuses"
        )
    """
    results = []
    progress_bar = st.progress(0)
    status = st.empty()

    for idx, item in enumerate(items):
        # Update progress
        progress = (idx + 1) / len(items)
        progress_bar.progress(progress)
        status.write(f"{description}... ({idx + 1}/{len(items)})")

        # Process item
        result = process_func(item)
        results.append(result)

    # Clean up
    progress_bar.empty()
    status.empty()

    return results
