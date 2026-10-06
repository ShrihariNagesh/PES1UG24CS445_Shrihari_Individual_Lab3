# Software Requirements Specification (SRS)

**Product:** Vaccination Cohort & Dose Scheduling System (Problem Statement #17)  
**Prepared by:** Shrihari Nagesh, PES1UG24CS445, Dept. of CSE, PES University  
**Structure:** IEEE Std 830-1998

## 1. Introduction

### 1.1 Purpose
This document states what the Vaccination Cohort & Dose Scheduling System must do and how well it
must do it. It is written for the people who design, build, test and grade the system.

### 1.2 Scope
The product is a public health administration platform. It will:

- register citizens and place each one in a vaccination cohort (phase)
- stop a citizen from booking the next dose before the minimum interval has passed
- let citizens find a centre by pincode and date and book a slot within the centre's capacity
- let Vaccination Officers check citizens in and record each dose
- issue a digitally signed QR vaccination certificate after the final dose, and verify it on scan

Out of scope: vaccine stock and cold-chain management, payments, and adverse-event reporting.

### 1.3 Definitions and abbreviations

| Term | Meaning |
|---|---|
| Cohort / phase | A group of citizens who become eligible together (for example healthcare workers first) |
| Dose interval | Minimum number of days between two doses (28 days by default) |
| Slot | A bookable place at one centre on one date, limited by daily capacity |
| QR certificate | Vaccination proof whose QR code carries citizen ID, dose dates and a digital signature |
| FR / NFR | Functional / non-functional requirement |
| RTM | Requirements traceability matrix |
| PII | Personally identifiable information |
| RBAC | Role-based access control |

### 1.4 References

1. Problem Statement #17, SE Lab 1 handout, PES University
2. IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications
3. [`1-RE/FR_and_NFR.md`](../1-RE/FR_and_NFR.md) and [`1-RE/RTM_Table.md`](../1-RE/RTM_Table.md)
4. [`2-Architectural_Diagram/Architecture_Specification.md`](../2-Architectural_Diagram/Architecture_Specification.md)

### 1.5 Overview
Section 2 describes the product and its users. Section 3 lists the specific requirements.

## 2. Overall description

### 2.1 Product perspective
A new, self-contained system built as microservices behind one API gateway. Citizens use a web or
mobile portal. Officers use a console at the vaccination centre. Each service keeps its own database.

### 2.2 Product functions
Registration and cohort assignment, dose-interval enforcement, slot search and booking, dose
recording, certificate generation, certificate verification, and booking notifications.

### 2.3 User classes

| User | What they do | Skill assumed |
|---|---|---|
| Citizen Registrant | Registers, books slots, downloads the certificate | Basic smartphone use, may be a first-time user |
| Vaccination Officer | Checks citizens in, records doses, scans certificates | Trained on the console, works under time pressure |

### 2.4 Operating environment
- Citizen Portal: current mobile and desktop browsers
- Officer Console: browser on a centre laptop or tablet with a camera for QR scanning
- Backend: containerised services on a cloud platform, one relational database per service

### 2.5 Design and implementation constraints
- Dose rules (interval days, required doses, cohort criteria) must be configuration, not hard-coded
- All traffic uses TLS 1.2 or later, and stored personal data uses AES-256 (NFR-002)
- The certificate signing key is held only by the Certificate Service
- Certificate verification must work offline, so the QR payload carries everything needed to check it

### 2.6 Assumptions and dependencies
- Each citizen has one valid government ID and a reachable phone number or email
- Centres publish their daily capacity before booking opens
- An SMS or email provider is available for notifications

## 3. Specific requirements

### 3.1 External interface requirements

| Interface | Requirement |
|---|---|
| User | Citizen Portal: booking in a few clear steps, readable on a phone. Officer Console: one-screen check-in form with required fields marked |
| Hardware | Camera on the officer device for QR scanning |
| Software | SMS or email gateway for notifications, relational databases, PDF generation for certificates |
| Communication | REST over HTTPS between clients and the gateway, REST or asynchronous messages between services |

### 3.2 Functional requirements

**3.2.1 Registration and cohort assignment (FR-002)**

- **Input:** name, age, government ID, comorbidity flag, occupation category.
- **Processing:** validate the fields, reject duplicate IDs and under-age citizens, assign the earliest
  cohort the citizen qualifies for (occupation, then age or comorbidity).
- **Output:** citizen profile with its cohort.

**3.2.2 Dose interval enforcement (FR-001)**

- **Input:** citizen ID and the date of the slot being requested.
- **Processing:** compare the slot date with the date of the previous dose. Block when the gap is under
  the minimum interval (28 days).
- **Output:** booking allowed, or a message saying how many days remain.

**3.2.3 Centre search and slot booking (FR-003)**

- **Input:** pincode, date, chosen slot.
- **Processing:** list slots with seats left. On booking, check capacity and take the seat in a single
  atomic step so the last seat cannot be given twice.
- **Output:** booking confirmation, and the remaining count goes down by one.

**3.2.4 Check-in and dose recording (FR-004)**

- **Input:** booking, vaccine brand, batch/lot number, date, officer ID.
- **Processing:** reject a blank batch number. Save the dose record. Move the citizen status from
  "Slot Booked" to "Dose Administered".
- **Output:** updated vaccination record.

**3.2.5 Certificate generation (FR-005)**

- **Input:** citizen with the required number of doses recorded.
- **Processing:** build the certificate data (citizen ID, dose dates), sign it, encode it as a QR code.
  Never issue before the final dose.
- **Output:** signed QR certificate, downloadable as a PDF.

**3.2.6 Certificate verification (FR-006)**

- **Input:** scanned QR payload.
- **Processing:** check the signature against the payload.
- **Output:** "Valid" with the citizen's name and dose dates, or "Invalid".

**3.2.7 Notifications (FR-007)**

- **Input:** a successful booking.
- **Processing:** queue one confirmation at once and one reminder 24 hours before the slot.
- **Output:** SMS or email to the citizen.

### 3.3 Non-functional requirements

| ID | Quality | Requirement | Measure |
|---|---|---|---|
| NFR-001 | Performance & Security | Verify a signed QR certificate offline or online | Under 150 ms under simulated peak load |
| NFR-002 | Security & Privacy | Encrypt personal and health data at rest and in transit, officers only | TLS 1.2+, AES-256, RBAC confirmed by security review |
| NFR-003 | Scalability | Handle a rollout rush of bookings | 5,000 concurrent requests, 95% answered within 3 s, zero double-bookings |
| NFR-004 | Availability | Recording and verification keep working if booking is down | Both actions succeed with the booking service stopped |
| NFR-005 | Auditability | Know who recorded each dose and when | Officer ID and date on every record, changes logged |

### 3.4 Logical database requirements

| Store | Owned by | Holds |
|---|---|---|
| Citizen DB | Citizen Registry Service | Profiles, cohort, government ID (encrypted) |
| Booking DB | Slot Booking Service | Centres, slots, capacity, bookings |
| Records DB | Vaccination Record Service | Dose records, interval rules, audit entries |
| Certificate Store | Certificate Service | Issued certificates and signing key reference |

No service reads another service's database. It asks through that service's interface.
