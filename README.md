# Kairos: Intelligent Distributed Scheduling Platform

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20PostgreSQL%20%7C%20Redis-blue)

**Kairos** (Ancient Greek: *The Opportune Moment*) is a high-performance workforce management engine designed to solve complex scheduling constraints. Unlike traditional greedy scheduling scripts, Kairos utilizes **Constraint Programming (CP-SAT)** to mathematically optimize staff coverage while respecting individual availability, fairness rules, and business demand.

This project demonstrates a **Distributed System Architecture**, decoupling the heavy computational logic from the REST API using asynchronous background workers and real-time WebSocket synchronization.

## 🚀 Key Features

* **Constraint Satisfaction Engine:** Modeled using **Google OR-Tools** to solve NP-hard scheduling problems, optimizing for maximum coverage and equitable shift distribution.
* **Distributed Architecture:** Offloads heavy solver computations to **Celery** workers backed by **Redis**, ensuring the API remains non-blocking and responsive.
* **Real-Time Collaboration:** Implements a **WebSocket** layer that synchronizes the interface across multiple clients instantly (Optimistic UI updates).
* **Dynamic Data Ingestion:** Features a drag-and-drop Excel parser that intelligently maps "messy" real-world availability data (e.g., "Open", "Close", "On") into structured database records using dynamic legend detection.
* **Homebase Integration:** Generates CSV exports formatted specifically for one-click import into Homebase/Payroll systems.

## 🛠️ Technical Stack

### Backend (Python)
* **Framework:** FastAPI (Async/Await)
* **Database:** PostgreSQL (via Supabase), SQLAlchemy ORM
* **Task Queue:** Celery + Redis (Upstash)
* **Algorithm:** Google OR-Tools (CP-SAT Solver)
* **Data Processing:** Pandas (Excel parsing)

### Frontend (TypeScript)
* **Framework:** React + Vite
* **Styling:** Tailwind CSS v4
* **Icons:** Lucide React
* **State Management:** Real-time WebSockets + React Hooks

## 🏗️ System Architecture

1.  **Client Action:** User uploads a roster or clicks "Generate Schedule" on the React Frontend.
2.  **API Layer:** FastAPI accepts the request and pushes a task to the **Redis Message Broker**.
3.  **Worker Layer:** A generic **Celery Worker** picks up the task, fetches constraints from **PostgreSQL**, and runs the CP-SAT solver.
4.  **Optimization:** The solver evaluates thousands of permutations to find the optimal schedule while preventing overlaps and ensuring fairness.
5.  **Broadcast:** Upon completion, the worker notifies the API, which blasts a `roster_update` event via **WebSockets** to all connected clients, refreshing their screens instantly.

## ⚡ Getting Started

### Prerequisites
* Node.js (v18+)
* Python (3.10+)
* Redis (Cloud URL recommended for Windows)
* PostgreSQL (Supabase recommended)

### 1. Environment Setup
Create a `.env` file in the `/backend` directory (optional but recommended for production):
```env
DATABASE_URL=postgresql://user:pass@endpoint:5432/postgres
REDIS_URL=rediss://default:pass@endpoint:6379