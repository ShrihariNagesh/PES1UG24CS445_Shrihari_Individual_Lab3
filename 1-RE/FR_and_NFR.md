# Requirements Engineering: Functional and Non-Functional Requirements

**Problem Statement #17:** Vaccination Cohort & Dose Scheduling System (Healthcare & Telemedicine)  
**Student:** Shrihari Nagesh | **SRN:** PES1UG24CS445 | Dept. of CSE, PES University

## 1. System summary

A public health administration platform that organises vaccination rollouts by cohort, enforces the
minimum number of days between doses, schedules slots at vaccination centres, and issues QR
vaccination certificates that can be verified.

**Actors:** Citizen Registrant, Vaccination Officer.

## 2. Where these requirements come from

| Set | IDs | Source |
|---|---|---|
| Baseline | FR-001 to FR-005, NFR-001, NFR-002 | Lab 1 requirement set, as tracked in Jira during Lab 2 (Kanban, Scrum and bug tracker) |
| Added in Lab 3 | FR-006, FR-007, NFR-003 to NFR-005 | Found while designing the architecture. Not yet in the Jira backlog |

FR-001 and NFR-001 are the two sample requirements given in the problem statement.

## 3. Functional requirements

| ID | Priority | Description | Acceptance criteria |
|---|---|---|---|
| **FR-001** | High | The system shall enforce dose interval rules (e.g., minimum 28 days after Dose 1) before unlocking Dose 2 booking for a citizen. | **Pass:** Dose 2 booking is blocked if the interval is under 28 days. **Fail:** An early vaccination slot is confirmed. |
| **FR-002** | High | The system shall allow a Citizen Registrant to create a profile with demographic details (age, comorbidity flags, occupation category) and automatically assign them to an eligible vaccination cohort/phase. | **Pass:** The registrant is auto-tagged with the correct cohort based on age/comorbidity rules. **Fail:** A registrant is placed in an ineligible cohort. |
| **FR-003** | High | The system shall let a Citizen Registrant search nearby vaccination centres by pincode/date and book an available time slot within that centre's daily capacity. | **Pass:** Booking succeeds only while booked count < centre capacity, and the slot count decrements. **Fail:** A centre accepts a booking beyond its capacity. |
| **FR-004** | Medium | The system shall allow a Vaccination Officer to check in a citizen, record the administered dose (vaccine brand, batch/lot number, date), and update the citizen's vaccination status. | **Pass:** Citizen status moves from "Slot Booked" to "Dose Administered" with a batch number stored. **Fail:** Status can be updated without a batch number. |
| **FR-005** | Medium | Upon completion of the required dose count, the system shall auto-generate a digitally signed QR vaccination certificate for the citizen, downloadable as a PDF. | **Pass:** The certificate QR encodes citizen ID, dose dates and a digital signature. **Fail:** A certificate is generated before the final dose is administered. |
| **FR-006** | High | The system shall let a Vaccination Officer scan a certificate QR code and see whether the certificate is genuine, together with the citizen's name and dose dates. | **Pass:** A genuine certificate shows "Valid" with matching details, and a certificate with any changed character shows "Invalid". **Fail:** A tampered certificate is shown as valid. |
| **FR-007** | Medium | The system shall send the citizen a confirmation when a slot is booked and a reminder 24 hours before the appointment (SMS or email). | **Pass:** Exactly one confirmation is queued for every successful booking, and one reminder 24 hours before the slot. **Fail:** A booking produces no confirmation, or produces duplicates. |

## 4. Non-functional requirements

| ID | Type | Priority | Description | Acceptance criteria |
|---|---|---|---|---|
| **NFR-001** | Performance & Security | High | The vaccination certificate verification endpoint shall authenticate digitally signed QR codes offline/online in under 150 ms. | **Pass:** Benchmarking tests confirm the target latency and security standards under simulated peak load. |
| **NFR-002** | Security & Privacy | High | All citizen personal and health data (name, ID, vaccination history) shall be encrypted at rest and in transit (TLS 1.2+/AES-256) and accessible only to authorized Vaccination Officers. | **Pass:** A security review confirms encryption at rest/in transit and role-based access control. **Fail:** PII is retrievable without authentication or found in plaintext. |
| **NFR-003** | Performance & Scalability | High | The system shall support at least 5,000 concurrent slot-booking requests during a cohort rollout window, with 95% of booking responses within 3 seconds. | **Pass:** A load test with 5,000 concurrent virtual users shows 95th-percentile response time of 3 s or less and zero double-bookings. **Fail:** The 95th percentile exceeds 3 s, or any slot is double-booked. |
| **NFR-004** | Availability | Medium | Dose recording and certificate verification shall remain usable when the booking function is overloaded or down. | **Pass:** With the booking service stopped in a test environment, an officer can still record a dose and verify a certificate. **Fail:** Either action fails because booking is unavailable. |
| **NFR-005** | Auditability | Medium | Every dose record shall store the officer ID and the date, and any later change to a record shall be logged. | **Pass:** Each dose record shows who recorded it and when, and an edit adds an audit entry. **Fail:** A record exists with no officer ID, or is changed with no trace. |

## 5. Quality check of the requirement set

| Property | How the set meets it |
|---|---|
| Unambiguous | Every requirement names one actor and one action |
| Testable | Every requirement has a pass condition that can be observed, most with a number (28 days, 150 ms, 5,000 users, 3 s) |
| Traceable | Each ID is linked to a use case, a component, a work package and a test in [`RTM_Table.md`](./RTM_Table.md) |
| Consistent | The seven baseline requirements are the same ones tracked on the Jira boards |
| Feasible | Each requirement maps to one owning service in the architecture |

## 6. Coverage summary

| | Baseline | Added | Total |
|---|:---:|:---:|:---:|
| Functional | 5 | 2 | 7 |
| Non-functional | 2 | 3 | 5 |
| **Total** | **7** | **5** | **12** |
