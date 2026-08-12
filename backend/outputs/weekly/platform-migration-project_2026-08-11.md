# Weekly Project Health Report: Platform Migration Project

Run date: 2026-08-11
Source file: `Project_Alpha_Week3.xlsx`

## Executive Summary

- Agent RAG: **Red**
- Risk score: **68.4/100**
- Confidence: **High**
- Data quality score: **100%**
- Existing source schedule health: **Red**
- Agent mode: **llm:groq**

## Why This Status

- The project's RAG status is Red, primarily due to 5 red schedule-health rows and 1 late task, as seen in source rows 2, 5, 6, 7, and 8. The project is also facing significant risks, including vendor contract termination and predecessor tasks being on hold. The average completion is 47.86% versus the expected progress of 37.5%, but this progress is overshadowed by critical path risks and blockers.
- 5 red schedule-health rows contribute to the Red RAG status
- 1 late task indicates potential delays
- Blockers, such as the terminated vendor contract, hinder progress
- Predecessor tasks being on hold delay subsequent tasks
- Milestone misses require escalation and impact project timeline

## Stakeholder Sentiment

Stakeholders have expressed significant concerns, with comments indicating that the project is blocked due to a terminated vendor contract (source row 5), cannot start because predecessors are on hold (source row 6), and is at risk of a 30+ day slip (source row 7). Additionally, a milestone was missed, requiring board-level escalation (source row 8).

## Risk Themes

- Vendor Contract Risks
- Predecessor Task Delays
- Critical Path Risks
- Blockers and Hold-ups
- Milestone Misses

## Score Breakdown

| Signal | Weight | Score | Weighted | Evidence |
|---|---:|---:|---:|---|
| schedule | 30 | 1.00 | 30.0 | 5 red and 0 amber/yellow schedule-health rows |
| progress | 20 | 0.10 | 2.0 | Completion is 10.4 points ahead of expected timeline. |
| milestone | 20 | Excluded | 0.0 | No milestone/phase rows detected. |
| blockers | 15 | 1.00 | 15.0 | 5 task rows show blocker, critical-path, on-hold, negative-float, or keyword risk. |
| sentiment | 10 | 0.43 | 4.3 | Comment row 5: BLOCKED — vendor contract terminated unexpectedly. Cannot proceed without a replacement partner. |
| budget | 5 | Excluded | 0.0 | Budget/burn columns are absent in the provided workbook. |

## Delivery Indicators

- Tasks: 7 total, 5 active
- Milestones/phases detected: 0
- Average completion: 47.86%
- Expected progress by dates: 37.5%
- Progress gap: -10.36 percentage points
- Schedule health distribution: {'Red': 5, 'Green': 2}
- Status distribution: {'In Progress': 1, 'Completed': 2, 'On Hold': 1, 'Not Started': 2, 'Missed': 1}

## Top Risks

- Row 2: Platform Migration Project (Red)
- Row 5: 1.3 Dev Environment Setup (Red)
- Row 6: 1.4 Core Module Development (Red)
- Row 7: 1.5 Integration Testing (Red)
- Row 8: MILESTONE: Phase 1 Sign-off (Red)

## Recommended Actions

- Run a schedule recovery review focused on red/yellow rows and near-term milestones
- Create an escalation list for critical-path, pending, and dependency-driven blockers
- Address vendor contract termination and find a replacement partner
- Resolve predecessor task hold-ups to allow subsequent tasks to proceed
- Develop a mitigation plan for milestone misses and their impact on the project timeline
- Conduct regular progress reviews to identify and address emerging risks

## Data Caveats

- No milestone/phase rows detected.
- Budget/burn columns are absent in the provided workbook.
- No stakeholder comments available.
- No milestone/phase rows detected in the provided data
- Budget/burn columns are absent in the provided workbook, limiting financial analysis
- Initial data quality issues noted, but the data quality score is 100, indicating high-quality data for the available fields

## Preserved Workbook Attributes

`% Complete`, `Baseline Finish`, `Baseline Start`, `Comments`, `Critical`, `End Date`, `Owner`, `Phase / Milestone`, `Schedule Health`, `Start Date`, `Status`, `Task Name`, `Total Float`
