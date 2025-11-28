# ⏳ Kairos - Intelligent Distributed Scheduling Platform

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Stack](https://img.shields.io/badge/Stack-React%20|%20FastAPI%20|%20PostgreSQL%20|%20Redis%20|%20Celery-6366f1)

Kairos is a high-performance workforce management engine designed to automate complex staff rostering. Unlike traditional greedy scheduling scripts, it uses constraint programming (CP-SAT) to mathematically optimize staff coverage while respecting availability, fairness rules, and business demand.

**Live Demo:** [https://kairos-david-kim.vercel.app/](https://kairos-david-kim.vercel.app/)

## ✨ Key Features

* **🧩 Constraint Satisfaction Engine:** Modeled using **Google OR-Tools** to solve NP-hard scheduling problems, optimizing for maximum coverage and equitable shift distribution.
* **⚡ Distributed Architecture:** Offloads heavy solver computations to **Celery** workers backed by **Redis**, ensuring the API remains non-blocking and responsive.
* **🔄 Real-Time Collaboration:** Implements a **WebSocket** layer that synchronizes the interface across multiple clients instantly (Optimistic UI updates).
* **📂 Dynamic Data Ingestion:** Features a drag-and-drop Excel parser that intelligently maps "messy" real-world availability data (e.g., "Open", "Close", "On") into structured database records.
* **📅 Homebase Integration:** Generates CSV exports formatted specifically for one-click import into Homebase/Payroll systems.

## 🛠️ Tech Stack

**Frontend:**
* React (Vite)
* Tailwind CSS (v4)
* Lucide React (Icons)
* WebSockets (Real-time State)

**Backend:**
* Python (FastAPI)
* PostgreSQL (Supabase)
* Redis (Upstash) & Celery (Async Tasks)
* Google OR-Tools (CP-SAT Solver)
* Pandas (Data Processing)

**Deployment:**
* Frontend: Vercel
* Backend: Render

## 🚀 Getting Started

### Prerequisites
* Node.js (v18+)
* Python (3.10+)
* PostgreSQL Database (Supabase recommended)
* Redis Instance (Upstash recommended)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/davidgskkim/kairos.git](https://github.com/davidgskkim/kairos.git)
    cd kairos
    ```

2.  **Install Backend Dependencies:**
    ```bash
    cd backend
    python -m venv venv
    # Windows: venv\Scripts\activate | Mac: source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Install Frontend Dependencies:**
    ```bash
    cd ../frontend
    npm install
    ```

4.  **Environment Setup:**
    Create a `.env` file in the `/backend` directory:
    ```env
    DATABASE_URL=postgresql://user:pass@endpoint:5432/postgres
    REDIS_URL=rediss://default:pass@endpoint:6379
    ```

5.  **Run Locally:**
    * **Backend API:** `cd backend && py -m uvicorn main:app --reload`
    * **Background Worker:** `cd backend && py -m celery -A worker.celery_app worker --loglevel=info -P eventlet`
    * **Frontend:** `cd frontend && npm run dev`

## 📸 Screenshots

| Dashboard 
|:---:
| ![Dashboard](./assets/kairos.png) 

## 👤 Author

**David Kim**
* [LinkedIn](https://www.linkedin.com/in/david-gs-kim)
* [GitHub](https://github.com/davidgskkim)