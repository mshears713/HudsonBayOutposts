"""
User data models for tracking learner progress through the adventure.

This module defines structures to track user progress, achievements, and
learning state throughout the 10-chapter journey.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set, Optional
from enum import Enum


class ChapterStatus(Enum):
    """Status of a chapter in the learning journey."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    LOCKED = "locked"


@dataclass
class ChapterProgress:
    """
    Tracks progress for a single chapter.

    Attributes:
        chapter_number: Which chapter (1-10)
        status: Current completion status
        started_at: When the user first accessed this chapter
        completed_at: When the user completed all chapter requirements
        tasks_completed: Set of completed task IDs within the chapter
        notes: User's personal notes about the chapter
    """

    chapter_number: int
    status: ChapterStatus = ChapterStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tasks_completed: Set[str] = field(default_factory=set)
    notes: str = ""

    def start_chapter(self) -> None:
        """Mark the chapter as started."""
        if self.status == ChapterStatus.NOT_STARTED:
            self.status = ChapterStatus.IN_PROGRESS
            self.started_at = datetime.now()

    def complete_task(self, task_id: str) -> None:
        """
        Mark a specific task within the chapter as completed.

        Args:
            task_id: Unique identifier for the task
        """
        self.tasks_completed.add(task_id)
        if self.status == ChapterStatus.NOT_STARTED:
            self.start_chapter()

    def complete_chapter(self) -> None:
        """Mark the entire chapter as completed."""
        self.status = ChapterStatus.COMPLETED
        self.completed_at = datetime.now()

    def get_progress_percentage(self, total_tasks: int) -> float:
        """
        Calculate completion percentage.

        Args:
            total_tasks: Total number of tasks in the chapter

        Returns:
            Percentage complete (0-100)
        """
        if total_tasks == 0:
            return 0.0
        return (len(self.tasks_completed) / total_tasks) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'chapter_number': self.chapter_number,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tasks_completed': list(self.tasks_completed),
            'notes': self.notes
        }


@dataclass
class UserProfile:
    """
    Comprehensive user profile tracking progress through the entire adventure.

    Attributes:
        username: Unique username for the learner
        display_name: Friendly display name
        email: Optional contact email
        created_at: When the profile was created
        last_active: Last time the user was active
        chapters: Progress tracking for each chapter
        achievements: Set of earned achievement IDs
        preferences: User preferences for UI and experience
    """

    username: str
    display_name: str
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    chapters: Dict[int, ChapterProgress] = field(default_factory=dict)
    achievements: Set[str] = field(default_factory=set)
    preferences: Dict[str, any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize chapter progress if not provided."""
        if not self.chapters:
            # Initialize all 10 chapters
            for i in range(1, 11):
                self.chapters[i] = ChapterProgress(
                    chapter_number=i,
                    status=ChapterStatus.LOCKED if i > 1 else ChapterStatus.NOT_STARTED
                )

    def update_activity(self) -> None:
        """Update the last active timestamp."""
        self.last_active = datetime.now()

    def get_chapter(self, chapter_number: int) -> Optional[ChapterProgress]:
        """
        Get progress for a specific chapter.

        Args:
            chapter_number: Chapter to retrieve (1-10)

        Returns:
            ChapterProgress object or None if invalid chapter
        """
        return self.chapters.get(chapter_number)

    def unlock_chapter(self, chapter_number: int) -> bool:
        """
        Unlock a specific chapter if prerequisites are met.

        Args:
            chapter_number: Chapter to unlock

        Returns:
            True if successfully unlocked, False otherwise
        """
        if chapter_number < 1 or chapter_number > 10:
            return False

        chapter = self.chapters.get(chapter_number)
        if not chapter:
            return False

        # Check if previous chapter is completed
        if chapter_number > 1:
            prev_chapter = self.chapters.get(chapter_number - 1)
            if not prev_chapter or prev_chapter.status != ChapterStatus.COMPLETED:
                return False

        if chapter.status == ChapterStatus.LOCKED:
            chapter.status = ChapterStatus.NOT_STARTED
            return True

        return False

    def earn_achievement(self, achievement_id: str) -> None:
        """
        Award an achievement to the user.

        Args:
            achievement_id: Unique identifier for the achievement
        """
        self.achievements.add(achievement_id)
        self.update_activity()

    def get_overall_progress(self) -> float:
        """
        Calculate overall progress percentage across all chapters.

        Returns:
            Percentage of chapters completed (0-100)
        """
        completed = sum(
            1 for ch in self.chapters.values()
            if ch.status == ChapterStatus.COMPLETED
        )
        return (completed / 10) * 100

    def get_current_chapter(self) -> Optional[int]:
        """
        Get the current chapter the user should be working on.

        Returns:
            Chapter number or None if all completed
        """
        for i in range(1, 11):
            chapter = self.chapters.get(i)
            if chapter and chapter.status in [ChapterStatus.NOT_STARTED, ChapterStatus.IN_PROGRESS]:
                return i
        return None

    def to_dict(self) -> Dict:
        """Convert user profile to dictionary."""
        return {
            'username': self.username,
            'display_name': self.display_name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat(),
            'chapters': {num: ch.to_dict() for num, ch in self.chapters.items()},
            'achievements': list(self.achievements),
            'preferences': self.preferences,
            'overall_progress': self.get_overall_progress()
        }
