# 🏥 Hospital Management System (Streamlit)

A **web-based Hospital Management System** built using **Python and Streamlit**.
This project helps manage **medicine inventory, patients, prescriptions, and reports**, and can generate **professional PDF prescriptions**.

---

## 🌐 Live Demo

```
https://hospital-management-system-bpbmle6pf7fjgg7i5valhe.streamlit.app/
```

---

## 🚀 Features

### 🧾 Patient Management

* Register new patients
* Store age and gender details
* View complete patient prescription history

### 💊 Medicine Inventory

* Add, update, and delete medicines
* Track medicine quantities and prices
* Low-stock alerts

### 📋 Prescription System

* Create prescriptions for patients
* Automatic stock deduction
* Prevents prescriptions if stock is insufficient

### 📄 PDF Reports

* Professional prescription PDF generation
* Inventory report PDF
* Patient history PDF

---

## 🛠️ Technologies Used

* **Python 3**
* **Streamlit** – Web framework
* **ReportLab** – PDF generation
* **JSON** – Data storage

---

## 📂 Project Structure

```
Hospital_Management_System/
│
├── hospital_management_system.py   # Main Streamlit application
├── medicines.json                  # Medicine inventory data
├── patients.json                   # Patient records
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
└── .gitignore
```

---

## ▶️ How to Run Locally

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the app

```bash
streamlit run hospital_management_system.py
```

The app will open automatically in your browser.

---

## ☁️ Deployment

This project can be deployed for free using **Streamlit Community Cloud**.

Steps:

1. Upload project to GitHub
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect GitHub repository
4. Select `hospital_management_system.py` as main file

---

## 🎓 Academic Purpose

This project is developed for **learning and academic demonstration purposes** as part of a **Computer Engineering curriculum**.

It demonstrates:

* Object-Oriented Programming (OOP)
* File handling with JSON
* Web app development using Streamlit
* Real-world problem solving

---

## 👨‍💻 Author

**Yash Maru**
Computer Engineering Student

---

## 📜 License

This project is open-source and free to use for educational purposes.
