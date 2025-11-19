"""
Data Synchronization UI Components for Streamlit Dashboard

This module provides reusable Streamlit components for data synchronization flows,
including sync triggers, status displays, conflict resolution, and progress tracking.

Educational Note:
These components demonstrate how to build distributed system UIs that handle
data synchronization, conflict resolution, and multi-node coordination.

Phase 3 Feature:
Complete data sync UI with visual feedback and error handling.
"""

import streamlit as st
from typing import Optional, Dict, Any, List, Tuple
from src.api_client.client import OutpostAPIClient
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


# ============================================================================
# Session State Management for Sync
# ============================================================================

def initialize_sync_session_state():
    """
    Initialize sync-related session state variables.

    Educational Note:
    Managing sync state helps track ongoing operations, history, and errors
    across user interactions without losing context.
    """
    if 'sync_history' not in st.session_state:
        st.session_state.sync_history = []

    if 'sync_in_progress' not in st.session_state:
        st.session_state.sync_in_progress = False

    if 'last_sync_result' not in st.session_state:
        st.session_state.last_sync_result = None

    if 'sync_errors' not in st.session_state:
        st.session_state.sync_errors = []


# ============================================================================
# Sync Status Components
# ============================================================================

def render_sync_status_badge(fort_name: str, last_sync: Optional[datetime] = None):
    """
    Display a compact sync status badge for a fort.

    Args:
        fort_name: Name of the fort
        last_sync: Timestamp of last successful sync

    Educational Note:
    Visual status indicators help users quickly understand the sync state
    without needing to read detailed information.
    """
    if last_sync:
        time_diff = (datetime.now() - last_sync).total_seconds()
        if time_diff < 300:  # Less than 5 minutes
            status = "🟢 Synced"
            color = "green"
        elif time_diff < 3600:  # Less than 1 hour
            status = "🟡 Recent"
            color = "orange"
        else:
            status = "🔴 Stale"
            color = "red"
    else:
        status = "⚪ Never"
        color = "gray"

    st.markdown(
        f"**{fort_name}**: "
        f"<span style='color: {color};'>{status}</span>",
        unsafe_allow_html=True
    )


def render_sync_capabilities(client: OutpostAPIClient, fort_name: str):
    """
    Display sync capabilities and status for a fort.

    Args:
        client: Authenticated API client
        fort_name: Name of the fort

    Educational Note:
    Different nodes may support different sync operations. Always check
    capabilities before attempting sync operations.
    """
    with st.expander(f"🔄 {fort_name} Sync Capabilities", expanded=False):
        try:
            # Get sync status from the fort
            status = client._make_request('GET', '/sync/status')

            st.write("**Supported Operations:**")
            for operation in status.get('supported_operations', []):
                st.write(f"✓ {operation}")

            st.write("**Sync Version:**", status.get('version', 'Unknown'))

            if 'last_sync' in status:
                st.write("**Last Sync:**", status['last_sync'])

        except Exception as e:
            st.error(f"Could not retrieve sync capabilities: {str(e)}")
            logger.error(f"Sync capabilities error for {fort_name}: {e}")


# ============================================================================
# Sync Trigger Components
# ============================================================================

def render_sync_trigger(
    source_client: OutpostAPIClient,
    target_client: OutpostAPIClient,
    source_name: str,
    target_name: str,
    merge_strategy: str = "merge"
) -> Optional[Dict[str, Any]]:
    """
    Render a sync trigger button with strategy selection.

    Args:
        source_client: Client for the source fort
        target_client: Client for the target fort
        source_name: Name of source fort
        target_name: Name of target fort
        merge_strategy: Default merge strategy

    Returns:
        Sync result dictionary if sync was performed, None otherwise

    Educational Note:
    Different merge strategies solve different problems:
    - 'add': Only add new items, safe but may miss updates
    - 'replace': Complete replacement, simple but destructive
    - 'merge': Combine data, most useful but requires conflict handling
    """
    st.subheader(f"Sync: {source_name} → {target_name}")

    # Strategy selection
    strategy = st.selectbox(
        "Merge Strategy",
        options=["merge", "add", "replace"],
        index=["merge", "add", "replace"].index(merge_strategy),
        help="""
        **merge**: Combine quantities for existing items
        **add**: Only add new items, skip existing ones
        **replace**: Replace all data with source data
        """
    )

    # Show strategy explanation
    strategy_explanations = {
        "merge": "📊 Combine data: Update quantities and merge information",
        "add": "➕ Add only: Skip items that already exist at target",
        "replace": "🔄 Replace all: Completely overwrite target data"
    }
    st.info(strategy_explanations[strategy])

    # Sync button
    if st.button(f"🔄 Sync from {source_name} to {target_name}", key=f"sync_{source_name}_{target_name}"):
        return _perform_sync(source_client, target_client, source_name, target_name, strategy)

    return None


def _perform_sync(
    source_client: OutpostAPIClient,
    target_client: OutpostAPIClient,
    source_name: str,
    target_name: str,
    strategy: str
) -> Dict[str, Any]:
    """
    Internal function to perform the actual sync operation.

    Educational Note:
    This demonstrates the typical sync workflow:
    1. Export data from source
    2. Import data to target with chosen strategy
    3. Handle errors and provide feedback
    """
    st.session_state.sync_in_progress = True
    result = {"success": False, "statistics": {}}

    try:
        with st.spinner(f"Exporting data from {source_name}..."):
            # Step 1: Export from source
            export_data = source_client._make_request('POST', '/sync/export-inventory')
            st.success(f"✓ Exported {export_data.get('item_count', 0)} items from {source_name}")

        with st.spinner(f"Importing to {target_name} using '{strategy}' strategy..."):
            # Step 2: Import to target
            import_payload = {
                **export_data,
                "merge_strategy": strategy
            }
            import_result = target_client._make_request(
                'POST',
                '/sync/import-inventory',
                json_data=import_payload
            )

            # Step 3: Display results
            stats = import_result.get('statistics', {})
            st.success("✓ Sync completed successfully!")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Items Added", stats.get('items_added', 0))
            with col2:
                st.metric("Items Updated", stats.get('items_updated', 0))
            with col3:
                st.metric("Items Skipped", stats.get('items_skipped', 0))

            result = {
                "success": True,
                "statistics": stats,
                "source": source_name,
                "target": target_name,
                "strategy": strategy,
                "timestamp": datetime.now().isoformat()
            }

            # Add to sync history
            st.session_state.sync_history.append(result)
            st.session_state.last_sync_result = result

            # Celebration animation
            st.balloons()

    except Exception as e:
        error_msg = f"Sync failed: {str(e)}"
        st.error(error_msg)
        logger.error(f"Sync error ({source_name} -> {target_name}): {e}")

        result = {
            "success": False,
            "error": str(e),
            "source": source_name,
            "target": target_name,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat()
        }

        st.session_state.sync_errors.append(result)

    finally:
        st.session_state.sync_in_progress = False

    return result


# ============================================================================
# Sync Progress and History Components
# ============================================================================

def render_sync_progress():
    """
    Display current sync operation progress.

    Educational Note:
    Real-time progress indicators improve UX for long-running operations.
    In production, you'd use async operations and websockets for live updates.
    """
    if st.session_state.sync_in_progress:
        st.warning("⏳ Sync operation in progress...")
        st.progress(0.5)  # In real implementation, track actual progress
    else:
        st.info("✓ No sync operations currently running")


def render_sync_history(limit: int = 10):
    """
    Display history of sync operations.

    Args:
        limit: Maximum number of history items to show

    Educational Note:
    Maintaining operation history helps with debugging, auditing,
    and understanding distributed system behavior over time.
    """
    st.subheader("📜 Sync History")

    if not st.session_state.sync_history:
        st.info("No sync operations performed yet")
        return

    # Show most recent syncs first
    recent_syncs = list(reversed(st.session_state.sync_history[-limit:]))

    for idx, sync_record in enumerate(recent_syncs):
        timestamp = sync_record.get('timestamp', 'Unknown')
        source = sync_record.get('source', 'Unknown')
        target = sync_record.get('target', 'Unknown')
        strategy = sync_record.get('strategy', 'Unknown')
        success = sync_record.get('success', False)

        status_icon = "✅" if success else "❌"

        with st.expander(f"{status_icon} {source} → {target} ({timestamp})", expanded=(idx == 0)):
            if success:
                stats = sync_record.get('statistics', {})
                st.write(f"**Strategy:** {strategy}")
                st.write(f"**Added:** {stats.get('items_added', 0)}")
                st.write(f"**Updated:** {stats.get('items_updated', 0)}")
                st.write(f"**Skipped:** {stats.get('items_skipped', 0)}")
            else:
                st.error(f"**Error:** {sync_record.get('error', 'Unknown error')}")


def render_sync_statistics_summary():
    """
    Display aggregate statistics across all sync operations.

    Educational Note:
    Aggregate metrics help understand overall system behavior and
    identify patterns or issues in distributed operations.
    """
    if not st.session_state.sync_history:
        return

    st.subheader("📊 Sync Statistics Summary")

    total_syncs = len(st.session_state.sync_history)
    successful_syncs = sum(1 for s in st.session_state.sync_history if s.get('success', False))
    failed_syncs = total_syncs - successful_syncs

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Syncs", total_syncs)
    with col2:
        st.metric("Successful", successful_syncs, delta=None)
    with col3:
        st.metric("Failed", failed_syncs, delta=None if failed_syncs == 0 else -failed_syncs)

    # Calculate totals across all successful syncs
    total_added = sum(
        s.get('statistics', {}).get('items_added', 0)
        for s in st.session_state.sync_history
        if s.get('success', False)
    )
    total_updated = sum(
        s.get('statistics', {}).get('items_updated', 0)
        for s in st.session_state.sync_history
        if s.get('success', False)
    )
    total_skipped = sum(
        s.get('statistics', {}).get('items_skipped', 0)
        for s in st.session_state.sync_history
        if s.get('success', False)
    )

    st.write("**Aggregate Item Statistics:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"Added: {total_added}")
    with col2:
        st.write(f"Updated: {total_updated}")
    with col3:
        st.write(f"Skipped: {total_skipped}")


# ============================================================================
# Conflict Resolution Components
# ============================================================================

def render_conflict_resolution_guide():
    """
    Display educational guide on conflict resolution strategies.

    Educational Note:
    Understanding conflict resolution is crucial in distributed systems.
    Different strategies suit different use cases.
    """
    with st.expander("📚 Understanding Conflict Resolution", expanded=False):
        st.markdown("""
        ### Merge Strategies in Distributed Systems

        When synchronizing data between nodes, conflicts can occur. Here's how
        each strategy handles them:

        #### 🔄 Merge Strategy
        - **Best for:** Inventory systems, counters, aggregations
        - **Behavior:** Combines quantities and updates metadata
        - **Example:** Fort A has 10 pelts, Fort B has 5 pelts → Result: 15 pelts
        - **Pros:** No data loss, preserves contributions from both sides
        - **Cons:** May not be appropriate for all data types

        #### ➕ Add Strategy
        - **Best for:** One-way syncs, initial population
        - **Behavior:** Only adds items that don't exist at target
        - **Example:** Fort A has pelts, Fort B doesn't → Fort B gets pelts
        - **Pros:** Safe, never overwrites existing data
        - **Cons:** Ignores updates to existing items

        #### 🔄 Replace Strategy
        - **Best for:** Full refreshes, master-replica scenarios
        - **Behavior:** Completely replaces target data with source data
        - **Example:** Fort A has 10 items → Fort B gets exactly those 10 items
        - **Pros:** Simple, ensures exact copy
        - **Cons:** Destructive, loses any target-specific data

        ### Production Considerations

        Real-world distributed systems need:
        - Vector clocks or timestamps for conflict detection
        - Last-write-wins or custom merge functions
        - Conflict logs and manual resolution UIs
        - Transaction support and rollback capabilities
        """)


def render_sync_error_log():
    """
    Display recent sync errors with troubleshooting hints.

    Educational Note:
    Error logging and analysis are critical for maintaining distributed systems.
    Good error messages help diagnose network, authentication, and logic issues.
    """
    if not st.session_state.sync_errors:
        return

    st.subheader("⚠️ Recent Sync Errors")

    for error_record in reversed(st.session_state.sync_errors[-5:]):
        timestamp = error_record.get('timestamp', 'Unknown')
        source = error_record.get('source', 'Unknown')
        target = error_record.get('target', 'Unknown')
        error = error_record.get('error', 'Unknown error')

        with st.expander(f"❌ {source} → {target} ({timestamp})", expanded=True):
            st.error(f"**Error:** {error}")

            # Provide troubleshooting hints
            st.write("**Troubleshooting:**")
            if "auth" in error.lower() or "token" in error.lower():
                st.write("- Check that you're logged in to both forts")
                st.write("- Tokens may have expired - try logging in again")
            elif "connection" in error.lower() or "network" in error.lower():
                st.write("- Verify the fort API is running")
                st.write("- Check network connectivity")
            elif "permission" in error.lower():
                st.write("- Ensure you have admin/manager role")
                st.write("- Sync operations require authentication")
            else:
                st.write("- Check the fort API logs for details")
                st.write("- Verify the fort supports sync operations")


# ============================================================================
# Comprehensive Sync Dashboard
# ============================================================================

def render_sync_dashboard(
    forts: Dict[str, OutpostAPIClient],
    fort_names: List[str]
):
    """
    Render a comprehensive sync management dashboard.

    Args:
        forts: Dictionary mapping fort names to authenticated clients
        fort_names: List of fort names

    Educational Note:
    A well-designed sync dashboard provides visibility, control, and
    troubleshooting capabilities for distributed data management.
    """
    initialize_sync_session_state()

    st.title("🔄 Data Synchronization Dashboard")

    st.markdown("""
    Manage data synchronization between Hudson Bay Company outposts.
    This demonstrates distributed system concepts including data consistency,
    conflict resolution, and multi-node coordination.
    """)

    # Sync capabilities overview
    st.header("1. Fort Sync Capabilities")
    cols = st.columns(len(fort_names))
    for idx, fort_name in enumerate(fort_names):
        with cols[idx]:
            if fort_name in forts:
                render_sync_capabilities(forts[fort_name], fort_name)
            else:
                st.warning(f"{fort_name}: Not connected")

    st.divider()

    # Conflict resolution guide
    st.header("2. Understanding Sync Strategies")
    render_conflict_resolution_guide()

    st.divider()

    # Sync triggers
    st.header("3. Perform Synchronization")

    if len(forts) < 2:
        st.warning("⚠️ Need at least 2 connected forts to perform sync")
        st.info("Please connect and authenticate to multiple forts first")
    else:
        # Let user select source and target
        col1, col2 = st.columns(2)

        with col1:
            source_name = st.selectbox(
                "Source Fort",
                options=fort_names,
                help="The fort to export data from"
            )

        with col2:
            target_options = [f for f in fort_names if f != source_name]
            target_name = st.selectbox(
                "Target Fort",
                options=target_options,
                help="The fort to import data to"
            )

        if source_name in forts and target_name in forts:
            render_sync_trigger(
                forts[source_name],
                forts[target_name],
                source_name,
                target_name
            )
        else:
            st.error("Both source and target forts must be connected and authenticated")

    st.divider()

    # Progress and history
    st.header("4. Sync Status & History")

    tab1, tab2, tab3 = st.tabs(["Current Status", "History", "Statistics"])

    with tab1:
        render_sync_progress()

    with tab2:
        render_sync_history()

    with tab3:
        render_sync_statistics_summary()

    st.divider()

    # Error log
    st.header("5. Error Log")
    render_sync_error_log()

    # Clear history button
    if st.button("🗑️ Clear Sync History", help="Remove all sync history and error logs"):
        st.session_state.sync_history = []
        st.session_state.sync_errors = []
        st.session_state.last_sync_result = None
        st.success("✓ History cleared")
        st.rerun()
