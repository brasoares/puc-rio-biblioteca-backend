```markdown
# 📚 Biblioteca Familiar - Backend

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python%203-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/framework-Flask-000000.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/database-SQLite-003b57.svg)](https://www.sqlite.org/)

This repository contains the backend source code for the **Biblioteca Familiar** (Family Library) project.  
It is a robust **RESTful API** built with **Python** and the **Flask** microframework, designed to serve data to the [biblioteca-familiar-frontend](../biblioteca-familiar-frontend/) application.

The API handles all business logic, data persistence, and gamification rules for the family library system.

---

## ✨ Key Features

- **RESTful API:** 30+ well-defined endpoints for managing books, members, loans, wishlists, and reviews.  
- **Database ORM:** SQLAlchemy for clean, safe, and maintainable database interactions.  
- **SQLite Database:** Lightweight, serverless, self-contained database engine.  
- **Gamification Logic:** Points, levels, and rankings for reading activities.  
- **Data Validation:** Server-side validation to ensure data integrity.  
- **API Documentation:** Integrated Swagger UI (via Flasgger) for interactive exploration.  
- **CORS Enabled:** Secure frontend–backend communication.  
- **Modular Structure:** Blueprints for each resource (e.g., livros, membros), following Flask best practices.  

---

## 🛠️ Technologies Used

- **Python 3:** Core programming language.  
- **Flask:** Lightweight WSGI web application framework.  
- **Flask-SQLAlchemy:** SQLAlchemy integration for ORM support.  
- **Flask-CORS:** Cross-Origin Resource Sharing (CORS) handling.  
- **Flasgger:** Swagger UI documentation for Flask APIs.  
- **SQLite:** Database engine.  

---

## 📂 Project Structure

```

biblioteca-familiar-backend/
├── 📄 app.py              # Main application factory and entry point
├── 📄 requirements.txt    # Python dependencies
├── 📁 instance/
│   └── biblioteca.db      # SQLite database file (auto-generated)
├── 📁 models/
│   ├── livro.py           # SQLAlchemy model for books
│   ├── membro.py          # SQLAlchemy model for members
│   └── ... (etc.)         # Other data models
└── 📁 routes/
├── livros.py          # Book endpoints (Blueprint)
├── membros.py         # Member endpoints (Blueprint)
└── ... (etc.)         # Other route blueprints

````

---

## 🚀 Getting Started

To run this backend API locally, you will need **Python 3** and **pip** installed.

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/biblioteca-familiar-backend.git
   cd biblioteca-familiar-backend
````

2. **Create and activate a virtual environment**

   On macOS/Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python app.py
   ```

5. **Verify the API is running**
   Visit: [http://localhost:5000](http://localhost:5000) to see a confirmation message.

---

## 📖 API Documentation

Once the server is running, access interactive documentation at:

[http://localhost:5000/apidocs](http://localhost:5000/apidocs)

Here you can view available endpoints, request formats, and test them directly from your browser.

---

## ✍️ Author

**Henoc** – Initial work & development

---

```
```
