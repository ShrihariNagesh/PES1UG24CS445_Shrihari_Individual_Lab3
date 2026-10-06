# Vaccination Cohort & Dose Scheduling System: Individual Lab 3

**Course:** Software Engineering Lab, individual project deliverables  
**Problem Statement #17:** Vaccination Cohort & Dose Scheduling System  
**Domain:** Healthcare & Telemedicine

## Student details

| | |
|---|---|
| Name | Shrihari Nagesh |
| SRN | PES1UG24CS445 |
| Department | Computer Science & Engineering, PES University |
| This repository | [PES1UG24CS445_Shrihari_Individual_Lab3](https://github.com/ShrihariNagesh/PES1UG24CS445_Shrihari_Individual_Lab3) |
| Lab 1 repository | [LAB-1_Activity_ShrihariNagesh_PES1UG24CS445](https://github.com/ShrihariNagesh/LAB-1_Activity_ShrihariNagesh_PES1UG24CS445) |
| Jira projects | `Kanban_BPS#17` (KBPS), `Scrum_BPS#17` (SBPS), `Bug_BPS#17` (BBPS) |

## About the project

A public health administration platform that organises vaccination rollouts by cohort, enforces the
minimum number of days between doses, schedules slots at vaccination centres, and issues QR
vaccination certificates that can be verified.

- **Cohort registration:** a citizen registers once and is placed in a phase by occupation, age and comorbidity.
- **Dose interval lock:** Dose 2 cannot be booked until 28 days after Dose 1.
- **Slot booking:** search centres by pincode and date, and book within the centre's daily capacity.
- **Dose recording:** an officer checks the citizen in and records brand, batch number and date.
- **QR certificate:** issued only after the final dose, digitally signed, and checked on scan.

**Actors:** Citizen Registrant, Vaccination Officer.

## Repository structure

```text
PES1UG24CS445_Shrihari_Individual_Lab3/
├── README.md
│
├── 1-RE/                                   a) Requirements Engineering
│   ├── FR_and_NFR.md                          7 functional and 5 non-functional requirements
│   ├── RTM_Table.md                           Requirements traceability matrix
│   ├── Use_Case_Diagram.pdf / .png            Use-case diagram from Lab 1
│   └── Requirements_Engineering_and_RTM.pdf   Both documents as one PDF
│
├── 2-Architectural_Diagram/                b) Architecture (Lab 3 handout)
│   ├── Architecture_Diagram.png / .pdf        UML component diagram
│   ├── Architecture_Diagram.drawio            Editable draw.io version
│   ├── Architecture_Justification_Document.docx / .pdf   One-page justification
│   ├── Architecture_Specification.md / .pdf   Full specification
│   └── generate_component_diagram.py          Script that draws the diagram
│
├── 3-Project_Creational_Screenshots/       c) GitHub and Jira evidence
│   ├── github/                                4 GitHub screenshots
│   └── jira/                                  19 Jira screenshots and the 3 Lab 2 reports
│
├── 4-SRS_and_Work_Breakdown_Steps/         d) SRS and WBS
│   ├── SRS_Document.md                        IEEE 830 structure
│   ├── Work_Breakdown_Structure.md            6 phases, 25 work packages, schedule, risks
│   ├── WBS_Gantt_Chart.png
│   └── SRS_and_Work_Breakdown_Steps.pdf       Both documents as one PDF
│
├── 5-Github_Copilot_Generated_Code/        e) AI-generated code
│   ├── vaccination_core_engine.py             Business rules for FR-001 to FR-007
│   ├── test_vaccination_core_engine.py        15 unit tests
│   └── README.md                              How it was produced, prompts, test output
│
└── 6-Software_Testing_Tools/               f) Testing tools practice
    ├── game_application.py                    Vial Code Breaker game
    ├── test_game_application.py               4 unit tests
    ├── game_patch.diff                        The one-line bug fix
    └── vibe_coding_bugfix_guide.md            Failing run, prompt, diagnosis, patch, retest
```

## Deliverable map

| Folder | Deliverable | What is inside |
|---|---|---|
| [`1-RE`](./1-RE) | a) Requirements Engineering | 7 FRs, 5 NFRs with acceptance criteria, and an RTM linking each one to a use case, Jira story, component, work package, test and Jira bug |
| [`2-Architectural_Diagram`](./2-Architectural_Diagram) | b) Architectural diagram | Microservices architecture: component diagram with 8 components and 10 ball-and-socket interfaces, one-page justification, full specification |
| [`3-Project_Creational_Screenshots`](./3-Project_Creational_Screenshots) | c) GitHub and Jira screenshots | Kanban board, Scrum backlog, sprint board, burndown chart, 7 bug reports, and the three Lab 2 PDF reports |
| [`4-SRS_and_Work_Breakdown_Steps`](./4-SRS_and_Work_Breakdown_Steps) | d) SRS and work breakdown | SRS in IEEE 830 structure, WBS with 39 story points from Jira, weekly schedule, risk table |
| [`5-Github_Copilot_Generated_Code`](./5-Github_Copilot_Generated_Code) | e) AI-generated code | Core engine in Python with 15 passing unit tests. Generated with Claude, with prompts to reproduce it in GitHub Copilot |
| [`6-Software_Testing_Tools`](./6-Software_Testing_Tools) | f) Testing tools practice | A game, 4 unit tests, 1 real failing test, the AI-assisted fix, and the retest |

## 1. Requirements Engineering

- **Baseline:** FR-001 to FR-005, NFR-001 and NFR-002, the same set tracked in Jira during Lab 2.
- **Added in Lab 3:** FR-006 (certificate verification), FR-007 (notifications), NFR-003 (scalability), NFR-004 (availability), NFR-005 (auditability).
- **RTM:** all 12 requirements are linked to a use case and a component. 8 of 12 have an automated test. The other 4 are quality requirements that need a deployed system.
- PDF: [`Requirements_Engineering_and_RTM.pdf`](./1-RE/Requirements_Engineering_and_RTM.pdf)

## 2. Architectural diagram (Lab 3 handout)

> **We chose Microservices Architecture for the Vaccination Cohort & Dose Scheduling System.**

![UML component diagram](./2-Architectural_Diagram/Architecture_Diagram.png)

| Point | Summary |
|---|---|
| Reason 1 | Load is uneven. Only the Slot Booking Service needs extra instances during a cohort rollout |
| Reason 2 | Fault isolation. If booking is overloaded, officers can still record doses and verify certificates |
| Security advantage | The certificate signing key lives only inside the Certificate Service |
| Performance benefit | Verification is a small separate service, so it stays within 150 ms during booking peaks |

Details: [`Architecture_Specification.md`](./2-Architectural_Diagram/Architecture_Specification.md) and
[`Architecture_Justification_Document.pdf`](./2-Architectural_Diagram/Architecture_Justification_Document.pdf)

## 3. Project creation evidence

| Tool | Project | Evidence |
|---|---|---|
| Jira Kanban | `Kanban_BPS#17` | 7 requirement items, 3 epics, 7 user stories with tasks and sub-tasks |
| Jira Scrum | `Scrum_BPS#17` | 39 story points, Sprint 1 (21 points) and Sprint 2 (18 points), burndown chart |
| Jira bug tracker | `Bug_BPS#17` | 7 defects, each traced to the requirement it breaks |
| GitHub | this repository and Lab 1 | Repository home, commit history, Lab 1 repository |

Index of every screenshot: [`3-Project_Creational_Screenshots/README.md`](./3-Project_Creational_Screenshots/README.md)

## 4. SRS and work breakdown

- **SRS:** introduction, overall description, and specific requirements with input, processing and output for each function.
- **WBS:** 6 phases and 25 work packages. Phase 4 uses the Jira stories and their 39 story points.
- PDF: [`SRS_and_Work_Breakdown_Steps.pdf`](./4-SRS_and_Work_Breakdown_Steps/SRS_and_Work_Breakdown_Steps.pdf)

## 5. AI-generated code

[`vaccination_core_engine.py`](./5-Github_Copilot_Generated_Code/vaccination_core_engine.py)
implements the business rules. The code was generated with Claude, not GitHub Copilot. The folder
README lists prompts that reproduce it in Copilot.

```bash
cd 5-Github_Copilot_Generated_Code
python -m unittest test_vaccination_core_engine -v
```

Result: 15 of 15 tests pass. Six of the seven Jira bugs (BBPS-1 to BBPS-6) have a regression test.

## 6. Software testing tools practice

**Vial Code Breaker** is a small terminal code-breaking game with exactly 4 unit tests.

```bash
cd 6-Software_Testing_Tools
python -m unittest test_game_application -v
```

| Test | Before patch | After patch |
|---|:---:|:---:|
| `test_1_guess_validation` | PASS | PASS |
| `test_2_feedback_without_repeated_colours` | PASS | PASS |
| `test_3_score_and_attempt_limit` | PASS | PASS |
| `test_4_feedback_with_repeated_colours` | **FAIL** | PASS |

The bug: partial matches were over-counted when a colour repeated. The fix is one line
([`game_patch.diff`](./6-Software_Testing_Tools/game_patch.diff)). The failing version and the fix
are separate commits in the history.

## Submission checklist

- [x] 1-RE: functional requirements, non-functional requirements, RTM, PDF
- [x] 2-Architectural_Diagram: component diagram (PNG, PDF, draw.io), one-page justification (Word, PDF), specification
- [x] 3-Project_Creational_Screenshots: GitHub screenshots, Jira screenshots, Lab 2 reports
- [x] 4-SRS_and_Work_Breakdown_Steps: SRS, WBS, schedule, PDF
- [x] 5-Github_Copilot_Generated_Code: core engine and passing tests
- [x] 6-Software_Testing_Tools: game, 4 tests, bug fix, patch, retest
