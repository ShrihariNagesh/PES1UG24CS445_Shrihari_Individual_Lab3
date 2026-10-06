# Requirements Traceability Matrix (RTM)

**Problem Statement #17:** Vaccination Cohort & Dose Scheduling System  
**Student:** Shrihari Nagesh | **SRN:** PES1UG24CS445

## 1. Purpose

The RTM links every requirement forward to the place it is designed, planned, built and tested, and
back to the use case it came from. It answers two questions quickly: "is every requirement covered?"
and "if this requirement changes, what else must change?"

| Column | Where it points |
|---|---|
| Use case | Lab 1 use-case diagram (UC-01 to UC-09) |
| Jira story | Scrum project `Scrum_BPS#17` (SBPS-1 to SBPS-7), same stories as the Kanban project |
| Component | Lab 3 component diagram in [`2-Architectural_Diagram`](../2-Architectural_Diagram) |
| WBS | Work packages in [`Work_Breakdown_Structure.md`](../4-SRS_and_Work_Breakdown_Steps/Work_Breakdown_Structure.md) |
| Test | Unit tests in [`test_vaccination_core_engine.py`](../5-Github_Copilot_Generated_Code/test_vaccination_core_engine.py) |
| Jira bug | Bug tracker project `Bug_BPS#17` (BBPS-1 to BBPS-7) |

## 2. Traceability matrix

| Req. | Requirement (short) | Use case | Jira story | Component | WBS | Test | Jira bug | Status |
|---|---|---|---|---|---|---|---|---|
| FR-001 | Dose interval lock (28 days) | UC-03 | SBPS-1 | Vaccination Record Service (`IDoseEligibility`) | 4.2 | TC-01, TC-02 | BBPS-1 | Built, unit tested |
| FR-002 | Registration and cohort assignment | UC-01 | SBPS-2 | Citizen Registry Service | 4.1 | TC-03, TC-04, TC-05 | BBPS-2 | Built, unit tested |
| FR-003 | Centre search and slot booking | UC-02 | SBPS-3 | Slot Booking Service | 4.3 | TC-06, TC-07, TC-08 | BBPS-3 | Built, unit tested |
| FR-004 | Check-in and dose recording | UC-04, UC-05 | SBPS-4 | Vaccination Record Service, Officer Console | 4.4 | TC-10, TC-11 | BBPS-4 | Built, unit tested |
| FR-005 | Signed QR certificate after final dose | UC-06 | SBPS-5 | Certificate Service | 4.5 | TC-12, TC-13 | BBPS-5 | Built, unit tested (PDF export not built) |
| FR-006 | Certificate verification by QR scan | UC-07 | not in backlog | Certificate Service, Officer Console | 4.6 | TC-14 | none | Built, unit tested |
| FR-007 | Booking confirmation and reminder | UC-08 | not in backlog | Notification Service | 4.8 | TC-09 | none | Confirmation built and tested, reminder not built |
| NFR-001 | Verification under 150 ms | UC-07 | SBPS-6 | Certificate Service | 4.6 | TC-15 (local timing only) | BBPS-6 | Peak-load benchmark planned (WBS 5.3) |
| NFR-002 | Encryption and officer-only access | all | SBPS-7 | API Gateway, one database per service | 4.7 | none yet | BBPS-7 | Designed, security review planned (WBS 5.3) |
| NFR-003 | 5,000 concurrent bookings, p95 within 3 s | UC-02 | not in backlog | Slot Booking Service (scaled out) | 5.3 | none yet | none | Designed, load test planned |
| NFR-004 | Recording and verification survive a booking outage | UC-04, UC-07 | not in backlog | Separate services and databases | 5.3 | none yet | none | Designed, failover test planned |
| NFR-005 | Officer ID and date on every dose record | UC-05 | not in backlog | Vaccination Record Service, Records DB | 4.4 | none yet | none | Officer ID and date stored, change log not built |

UC-09 (Configure Cohort & Interval Rules) supplies the rule values that FR-001 and FR-002 enforce.

## 3. Jira bug traceability

Status is the Jira status at the time of the Lab 2 bug report. "Regression test" is the unit test in
this repository that would fail if the bug came back.

| Jira key | Bug | Requirement | Severity | Jira status | Regression test |
|---|---|---|---|---|---|
| BBPS-1 | Dose 2 booking not blocked at exactly 27-day interval | FR-001 | Critical | Done | TC-01 |
| BBPS-2 | Comorbidity flag ignored during cohort assignment | FR-002 | High | In Progress | TC-04 |
| BBPS-3 | Centre slot allows double-booking at zero remaining capacity | FR-003 | Critical | To Do | TC-07 |
| BBPS-4 | Dose record can be saved with an empty batch number | FR-004 | Medium | To Do | TC-10 |
| BBPS-5 | QR certificate generated before final dose is administered | FR-005 | Critical | In Progress | TC-12 |
| BBPS-6 | Certificate verification exceeds 150 ms target under peak load | NFR-001 | High | To Do | TC-15 (partial: checks key reuse, not peak load) |
| BBPS-7 | Citizen health data visible in plaintext in network logs | NFR-002 | Critical | To Do | none (deployment setting, not engine code) |

## 4. Coverage summary

| Measure | Count |
|---|---|
| Requirements in the matrix | 12 of 12 |
| Requirements linked to a use case | 12 of 12 |
| Requirements linked to a component | 12 of 12 |
| Requirements with at least one automated test | 8 of 12 |
| Requirements with a Jira story | 7 of 12 (the 5 added in Lab 3 are not in the backlog yet) |
| Jira bugs with a regression test | 6 of 7 |
| Automated unit tests in the core engine | 15, all passing |

The four requirements without an automated test (NFR-002 to NFR-005) need a deployed system to
check. They are planned under work package 5.3.
