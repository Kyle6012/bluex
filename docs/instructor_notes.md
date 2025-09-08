# Instructor Notes & Answer Keys

This document provides expected JSON structures, grading rubrics, and answers for the exercises.

## Exercise 1 - SIM_MITM_DETAILED
Expected JSON keys:
- module == 'SIM_MITM_DETAILED'
- timestamp (int)
- steps (list) containing step dicts with keys: step, time, ...
- summary dict with keys risk and confidence

Grading rubric (20 points):
- Report exists (5)
- steps include 'scan_result' (5)
- 'pairing_capture' present (5)
- summary.risk present (5)

## Exercise 2 - SIM_PAIRING_DETAILED
Expected JSON keys:
- module == 'SIM_PAIRING_DETAILED'
- attempts list (length 5)

Grading rubric (15 points):
- Report exists (5)
- attempts length ==5 (5)
- at least one attempt entry has keys method and result (5)

## Exercise 3 - SIM_FUZZ_DETAILED
Expected JSON keys:
- module == 'SIM_FUZZ_DETAILED'
- profiles list with at least one profile
- coverage dict

Grading rubric (15 points):
- Report exists (5)
- profiles present (5)
- coverage present (5)

Total points: 50

Use the CLI test-suite to auto-run modules and produce grading_results.csv. Review CSV to assign student grades.
