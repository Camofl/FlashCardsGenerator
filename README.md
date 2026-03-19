# FlashCardsGenerator

FlashCardsGenerator is a Django web app for creating flashcards manually or in bulk, with built-in dictionary lookup to generate definitions in multiple languages.

## Features

- Create and edit flashcards
- Bulk review and generate card backs
- Dictionary-powered definitions
- Language support for English, Spanish, French, and German
- Simple web interface with authentication
- Create, edit and export decks for learning-apps like anki

## Stack

- Python
- Django
- Bootstrap
- JavaScript

## Getting started

### 1. Clone the repository

### 2. Create and activate a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Usage

After logging in, you can:

- Create flashcards one by one
- Generate definitions for a selected API and language
- Bulk paste words and review generated backs before saving

## Supported languages

- English (`en`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)

## Troubleshooting

### Dependencies do not install

Make sure your virtual environment is activated before running:

```bash
pip install -r requirements.txt
```

### Port already in use

Start Django on another port:

```bash
python manage.py runserver 8001
```

### Database reset for local development

If you are using SQLite and want a fresh start, delete `db.sqlite3` and run:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Notes

- This project is intended for local development in it's current stage
