"""Compatibility shim.

Routine generation is template-based and auditable. This module intentionally does
not expose or fabricate model reasoning traces.
"""

from app.simulation.routine import build_daily_routine

__all__ = ["build_daily_routine"]
