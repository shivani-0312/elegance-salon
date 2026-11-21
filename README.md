
# Elegance Salon - Salon Appointment System

## About the Project

Elegance Salon is a web-based Salon Appointment Management System developed using Python and Django. The application helps customers explore salon services and book appointments online.

It also provides management features to handle customer details, salon services, and appointment information.

## Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite3
- **Tools:** VS Code, Git, GitHub

## Features

- Customer Registration and Login
- User Authentication
- Customer Profile Management
- View Salon Services
- Online Appointment Booking
- Appointment Management
- Reschedule and Cancel Appointments
- Manage Salon Services and Packages

## Project Structure

```text
beauty_salon/
│
├── beauty_salon/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── salon/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the Project Folder

```bash
cd beauty_salon
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file and add your Django secret key:

```env
DJANGO_SECRET_KEY=your_secret_key
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

http://127.0.0.1:8000/

## Project Status

Developed as a Python Django project. Further improvements and testing are ongoing.

## Author

Shivani Kyasa
