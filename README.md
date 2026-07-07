# 🏥 Hospital Management System

A full-stack **Hospital Management System** developed using **Spring Boot** to simplify hospital operations such as patient management, doctor management, appointment scheduling, and medical record maintenance. The application provides a secure and user-friendly platform for efficient healthcare administration.

---

## 🚀 Features

- 👨‍⚕️ Doctor Management
  - Add, update, delete, and view doctor details
  - Manage doctor specialization and availability

- 🧑‍🤝‍🧑 Patient Management
  - Register new patients
  - Update patient information
  - View patient records

- 📅 Appointment Management
  - Book appointments
  - View appointment history
  - Update and cancel appointments

- 📋 Medical Records
  - Store patient diagnosis and treatment details
  - Access patient history

- 🔐 Authentication
  - Secure login
  - Role-based access

- 📊 Dashboard
  - Overview of doctors, patients, and appointments

---

## 🛠 Tech Stack

### Backend
- Java
- Spring Boot
- Spring MVC
- Spring Data JPA
- Hibernate

### Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript

### Database
- MySQL

### Tools
- Maven
- Git
- GitHub
- Postman

---

## 📂 Project Structure

```
Hospital-Management-System/
│── src/
│   ├── main/
│   │   ├── java/
│   │   ├── resources/
│   │   └── webapp/
│   └── test/
│
├── pom.xml
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/Rushitha505/Hospital-Management-System.git
```

### Navigate to the project

```bash
cd Hospital-Management-System
```

### Configure MySQL

Create a database:

```sql
CREATE DATABASE hospital_management;
```

Update `application.properties`

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/hospital_management
spring.datasource.username=your_username
spring.datasource.password=your_password
```

### Build the project

```bash
mvn clean install
```

### Run the application

```bash
mvn spring-boot:run
```

Open your browser:

```
http://localhost:8080
```

---

## 📸 Modules

- Admin Dashboard
- Doctor Management
- Patient Management
- Appointment Booking
- Medical Records
- Authentication

---

## 📈 Future Enhancements

- Online payment integration
- Email/SMS notifications
- Prescription management
- Pharmacy module
- Laboratory module
- Reports and Analytics
- JWT Authentication
- Docker Deployment

---

## 🎯 Learning Outcomes

- Spring Boot Development
- REST API Development
- Hibernate & JPA
- MySQL Database Design
- MVC Architecture
- CRUD Operations
- Authentication & Authorization
- Git & GitHub Workflow

---

## 👩‍💻 Author

**Arrabothu Rushitha**

- GitHub: https://github.com/Rushitha505
- LinkedIn: https://linkedin.com/in/rushitha-arrabothu

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
