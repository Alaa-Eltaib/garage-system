# 🚗 Smart Garage Management System

A simple web-based Garage Management System built using Flask.  
The system helps manage car parking operations such as entry, exit, pricing, and availability tracking.

---

## 📌 Features

- Add new cars to the garage
- Track entry time automatically
- Checkout system with automatic price calculation
- Calculate parking duration
- Display available and occupied spots
- Revenue tracking dashboard
- Search for cars by number
- Delete car records
- Clean and responsive UI (Bootstrap)

---

## 🛠️ Tech Stack

- Python (Flask)
- SQLite (Database)
- HTML / CSS 
- Docker
- Jenkins (CI/CD)
- GitHub (Version Control)

---

## 🧠 System Logic

- Each car is stored with entry time
- On checkout, system calculates duration:
  - Price = hours × 10 EGP
  - Minimum charge = 10 EGP
- Total spots = 50 (configurable)

---

## 📁 Project Structure
```
garage-system/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── Jenkinsfile
├── Redme.md
|
├── templates/
│ ├── index.html
│ ├── add_car.html
| ├── report.html
│ ├── edit_car.html
```
---

## 🚀 How to Run Locally

### Install dependencies


pip install -r requirements.txt


### Run the app


python app.py


### Open in browser


http://127.0.0.1:5000


---

## 🐳 Run with Docker

### Build image


docker build -t garage-system .


### Run container


docker run -p 5000:5000 garage-system


---

## ⚙️ CI/CD (Jenkins Pipeline)

- Build Docker image  
- Run container  
- Automate deployment process  

---

## 📊 Dashboard Includes

- Total parking spots  
- Available spots  
- Parked cars  
- Total revenue  
- Live search functionality  

---

## 👩‍💻 Author

Developed as a Graduation Project for DevOps course.