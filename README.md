# Text-Based Emotional Wellbeing Analysis System

## Project Overview

This final-year project presents a web-based emotional wellbeing analysis system that uses machine learning and natural language processing to analyse short text entered by users and identify the expressed emotion.

The system is designed to support emotional self-awareness and provide access to useful wellbeing-related features such as mood tracking, counsellor recommendations, appointment management, anonymous community discussion, payment-proof handling, administrative monitoring, and controlled AI model management.

The system is intended for emotional reflection and support only. It is not a clinical diagnostic tool and does not replace professional mental healthcare.

---

## Main Features

### User Features
- User registration and login
- Text-based emotion analysis
- Emotion confidence score
- Mood history
- Weekly mood summaries and trends
- Risk-aware supportive messaging
- Counsellor recommendations
- Counsellor browsing
- Appointment booking
- Payment proof submission
- Anonymous community forum
- Forum replies and reporting
- User profile management

### Counsellor Features
- Counsellor login
- Appointment dashboard
- Availability management
- Appointment request review
- Appointment confirmation and rejection

### Administrator Features
- Administrator dashboard
- User and counsellor management
- Payment proof review
- Community forum moderation
- User-counsellor assignment management
- Analytics and reports
- Controlled AI model update management

---

## Machine Learning

The system uses a DistilBERT-based transformer model for emotion classification.

The model classifies text into six emotion categories:

- Sadness
- Joy
- Love
- Anger
- Fear
- Surprise

A TF-IDF and Logistic Regression model was initially developed as a baseline before evaluating the transformer-based approach.

The selected DistilBERT model achieved strong validation and test performance and was integrated into the Flask application for local inference.

---

## Technology Stack

### Backend
- Python
- Flask
- MySQL

### Machine Learning
- PyTorch
- Hugging Face Transformers
- DistilBERT
- Scikit-learn
- Pandas
- NumPy

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap

### Development Tools
- Git
- GitHub
- Visual Studio Code
- Ubuntu through Windows Subsystem for Linux (WSL)

---

## Development Environment

Development initially began in a Windows environment.

During implementation, compatibility and security-related issues affected parts of the Python and machine-learning toolchain. To maintain a stable Linux-compatible development environment without weakening Windows security controls, development was moved to Ubuntu using Windows Subsystem for Linux (WSL).

The project continued to run on the same development laptop, while WSL provided the required Linux environment for Python, machine-learning libraries, testing, and Flask development.

---

## System Architecture

The application follows a modular Flask-based architecture.

Major components include:

- Web interface
- Authentication and role-based access control
- Emotion analysis service
- Risk-support service
- Counsellor recommendation service
- Appointment management
- Payment validation
- Community forum
- Administrative management
- Analytics and reporting
- Model update management
- MySQL database

---

## Database

The system uses MySQL.

Main database tables include:

- `users`
- `mood_entries`
- `counsellor_profiles`
- `appointments`
- `payment_proofs`
- `forum_posts`
- `forum_reports`
- `forum_replies`
- `counsellor_availability_slots`
- `user_counsellor_assignments`
- `model_update_runs`

Database migration files are included in the repository.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/presidesg-lgtm/emotional-wellbeing-system.git