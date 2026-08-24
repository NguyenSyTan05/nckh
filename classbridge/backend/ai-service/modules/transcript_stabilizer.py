"""
ClassBridge Realtime Transcript Stabilizer Module
"""

from __future__ import annotations

import sys
from pathlib import Path

# Re-export from root transcript_stabilizer
sys.path.insert(0, str(Path(__file__).parent.parent))
from transcript_stabilizer import StabilizedResult, TranscriptStabilizer

__all__ = ["StabilizedResult", "TranscriptStabilizer"]
