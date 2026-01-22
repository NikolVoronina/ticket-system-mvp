# Ticket System (Flask + MariaDB)

This project is a simple **ticket management system** developed as part of an IT school assignment.  
The goal is to organize customer support requests and give a clear overview of ticket status and responsibility.

The system is built with **Flask** and **MariaDB** and is designed to be easy to understand, maintain, and extend.

---

## Features

### Authentication
- User registration and login
- Secure password hashing
- Session-based authentication
- Role-based access control

### User (bruker)
- Create new support tickets
- View own tickets
- Track ticket status

### Support staff (drift)
- View all tickets in the system
- Take ownership of a ticket
- Update ticket status (åpen / under_arbeid / lukket)

---

## Tech Stack

- Python
- Flask
- MariaDB
- HTML (Jinja templates)
- GitHub for version control

---

## Database Structure

### users
- id
- brukernavn
- passord
- rolle (bruker / drift)

### tickets
- id
- bruker_id
- tittel
- beskrivelse
- status
- behandler_id

---

## Setup & Run

### 1. Clone the repository
```bash
git clone <repository-url>
cd code


2. Create virtual environment
py -m venv .venv
.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Environment variables

Create a .env file based on .env.example and configure database credentials.

5. Create database
mysql -u root -p < schema.sql

6. Run the application
set FLASK_APP=app.py
flask run


Open in browser:
http://127.0.0.1:5000



What I Learned

Building a Flask application from scratch

Working with relational databases (MariaDB)

Implementing authentication and authorization

Using sessions and role-based access

Structuring a backend project for further development

Using GitHub for version control and collaboration