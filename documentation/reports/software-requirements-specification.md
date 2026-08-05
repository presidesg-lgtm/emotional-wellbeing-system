# Software Requirements Specification

## Project Title

A Text-Based Emotional Wellbeing Analysis System Using Machine Learning

## 1. Introduction

### 1.1 Purpose

The purpose of this Software Requirements Specification is to define the
functional, non-functional, data, interface, and machine-learning requirements
of the Text-Based Emotional Wellbeing Analysis System.

The system will allow users to submit text describing their thoughts or
emotional experiences. A trained machine-learning model will analyse the text
and identify the most likely expressed emotional category. The application
will store analysis results, display emotional trends, and provide carefully
controlled supportive feedback.

The system is intended to support emotional self-awareness and early
reflection. It is not a clinical diagnostic system and is not intended to
replace professional mental-health services.

### 1.2 Project Scope

The project will develop a web-based emotional wellbeing analysis platform
consisting of three principal components:

1. User Portal
2. Admin Portal
3. AI Analysis Engine

The User Portal will support account management, submission of emotional text,
viewing of prediction results, mood-history tracking, dashboard visualisation,
counsellor discovery, appointment booking, payment-proof submission, and
participation in a moderated community forum.

The Admin Portal will support the management of users, counsellors,
appointments, payment submissions, community content, system reports, and
machine-learning model information.

The AI Analysis Engine will preprocess user-submitted text, classify the
expressed emotion using a trained machine-learning model, return a prediction
with an associated confidence value, and provide the result to the web
application for storage and presentation.

### 1.3 Intended Audience

### 1.4 Definitions and Abbreviations

## 2. Overall Description

### 2.1 Product Perspective

### 2.2 Product Functions

### 2.3 User Classes

#### Registered User

A registered user can maintain an account, submit text for emotional analysis,
view analysis results, review mood history, access dashboard visualisations,
browse counsellor information, request appointments, submit payment proof, and
participate in the community forum.

#### Counsellor

A counsellor can maintain a professional profile, define available appointment
slots, review appointment requests assigned to them, and update appointment
statuses.

The counsellor role does not receive unrestricted access to private user mood
entries unless such access is explicitly implemented with user consent.

#### Administrator

An administrator can manage user and counsellor accounts, review system
activity, verify payment submissions, manage appointments, moderate community
content, view reports, and maintain information about the deployed
machine-learning model.

### 2.4 Operating Environment

### 2.5 Constraints

### 2.6 Assumptions and Dependencies

## 3. Functional Requirements

### 3.1 User Account Management

#### FR-AUTH-001 — User Registration

The system shall allow a new user to create an account by providing the
required registration information.

#### FR-AUTH-002 — Unique Email Address

The system shall prevent more than one active account from being registered
with the same email address.

#### FR-AUTH-003 — Password Protection

The system shall store passwords using a secure one-way password-hashing
method and shall not store plain-text passwords.

#### FR-AUTH-004 — User Login

The system shall allow a registered user to log in using valid credentials.

#### FR-AUTH-005 — Invalid Login Handling

The system shall reject invalid login credentials without revealing whether
the email address or password was incorrect.

#### FR-AUTH-006 — User Logout

The system shall allow an authenticated user to end their session securely.

#### FR-AUTH-007 — Role-Based Access

The system shall restrict user, counsellor, and administrator functions
according to the authenticated account role.

### 3.2 Emotional Text Analysis

#### FR-ML-001 — Text Submission

The system shall allow an authenticated user to submit textual input for
emotional analysis.

#### FR-ML-002 — Empty Input Validation

The system shall reject empty or whitespace-only text submissions.

#### FR-ML-003 — Input-Length Validation

The system shall enforce a documented minimum and maximum input length.

#### FR-ML-004 — Text Preprocessing

The system shall apply the same preprocessing pipeline used during model
training before performing a prediction.

#### FR-ML-005 — Emotion Classification

The system shall use the deployed machine-learning model to classify the
submitted text into one of the supported emotion categories.

#### FR-ML-006 — Prediction Confidence

The system shall display a confidence value where the selected model supports
probability-based output.

#### FR-ML-007 — Analysis Storage

The system shall store the submitted text, predicted emotion, confidence value,
model version, and analysis timestamp.

#### FR-ML-008 — Supportive Feedback

The system shall display a predefined supportive message associated with the
predicted emotional category.

#### FR-ML-009 — Non-Diagnostic Disclaimer

The system shall clearly inform users that prediction results are not clinical
diagnoses.

#### FR-ML-010 — High-Risk Content Response

The system shall display a predefined safety response when configured
high-risk expressions are identified.

The response shall not claim that the machine-learning model has made a
clinical determination.

### 3.3 Mood History and Dashboard

#### FR-MOOD-001 — Mood History

The system shall allow a user to view their previous emotional-analysis
entries in reverse chronological order.

#### FR-MOOD-002 — Entry Ownership

The system shall prevent a user from viewing another user's private mood
entries.

#### FR-MOOD-003 — Dashboard Summary

The system shall display a summary of the user's emotional classifications
over a selected time period.

#### FR-MOOD-004 — Mood Visualisation

The system shall display emotional trends using at least one appropriate chart.

#### FR-MOOD-005 — Entry Deletion

The system shall allow a user to delete one of their own mood entries, subject
to confirmation.

#### FR-MOOD-006 — No Medical Interpretation

The dashboard shall not present emotion frequencies as medical diagnoses or
clinical scores.

### 3.4 Counsellor Management

### 3.5 Appointment Management

### 3.6 Payment Proof Management

### 3.7 Community Forum

### 3.8 Administration and Reporting

## 4. Non-Functional Requirements

### 4.1 Security

#### NFR-SEC-001

Passwords shall be stored using secure password hashing.

#### NFR-SEC-002

Database queries shall use parameterised statements or framework-provided safe
query mechanisms.

#### NFR-SEC-003

Protected routes shall require authentication.

#### NFR-SEC-004

Administrative routes shall require the administrator role.

#### NFR-SEC-005

Secret values such as database passwords and application secret keys shall not
be committed to Git.

### 4.2 Performance

#### NFR-PERF-001

Under normal local demonstration conditions, an emotional-analysis request
should return a result within five seconds.

#### NFR-PERF-002

Normal web pages should load without unnecessary blocking operations.

### 4.3 Reliability

#### NFR-REL-001

The application shall validate user input and handle expected errors without
terminating the server.

#### NFR-REL-002

Database operations that involve multiple dependent changes shall use
transactions where appropriate.

### 4.4 Usability

#### NFR-USA-001

The interface shall use clear navigation and understandable labels.

#### NFR-USA-002

Validation errors shall explain what the user needs to correct.

#### NFR-USA-003

The interface shall be usable on common desktop and mobile screen sizes.

### 4.5 Maintainability

#### NFR-MAIN-001

Routes, business logic, database operations, and machine-learning functions
shall be separated into appropriate modules.

#### NFR-MAIN-002

Important classes and functions shall contain meaningful names and concise
documentation.

### 4.6 Privacy and Ethical Requirements

#### NFR-ETH-001

The system shall inform users how submitted emotional text is stored and used.

#### NFR-ETH-002

The system shall not use private user entries for model retraining without
explicit consent and an approved process.

#### NFR-ETH-003

The system shall clearly state that it does not replace professional care.

#### NFR-ETH-004

Access to sensitive user information shall be restricted according to role and
legitimate purpose.

## 5. Machine-Learning Requirements

## 6. Data Requirements

## 7. External Interface Requirements

## 8. Acceptance Criteria

The core system will be considered functionally complete when:

1. A user can register and log in securely.
2. An authenticated user can submit valid text for analysis.
3. The deployed model returns one supported emotion label.
4. The application displays the prediction and an appropriate disclaimer.
5. The analysis result is stored in the database.
6. The user can view their own mood history.
7. The user can view a chart summarising previous predictions.
8. An administrator can access protected administrative functions.
9. Unauthorised users cannot access protected pages.
10. The trained model has documented accuracy, precision, recall, F1-score,
    confusion matrix, and error analysis.
11. Core requirements have corresponding test cases.
12. The system clearly communicates that it is not a diagnostic tool.

## 9. Out-of-Scope Features