#!/usr/bin/env python3
"""
Audit E entry point — delegates to the frozen final workflow.

The original v1 script (with incorrect substantive divergence use of
_decision_diverges) is preserved at run_post60_analytical_audit_E_v1.py.
"""
from __future__ import annotations

import sys

from run_post60_analytical_audit_E_final import main

if __name__ == "__main__":
    print("Note: using Audit E final workflow (run_post60_analytical_audit_E_final.py)")
    print("Original v1 script preserved at scripts/run_post60_analytical_audit_E_v1.py")
    raise SystemExit(main())
