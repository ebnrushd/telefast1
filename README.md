# Telegram Marketing Bot - API Backend & Frontend Scaffold

This project has been restructured into a full-stack application. This repository contains:
1.  A **FastAPI Backend** that serves as an API and runs the Telegram bot logic.
2.  A **React Frontend** scaffold that is ready for further development.

Due to environmental limitations, the frontend dependencies could not be installed, but the project structure is in place for you to continue the work.

---

## Backend

The backend is a Python application located in the `backend/` directory that:
1.  Runs the Telegram bot to listen for commands (`/add_chat`, etc.).
2.  Provides a full web API to control the bot's features from a web interface.

### Setup and Running the Backend

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure your bot:**
    *   In the `backend/` directory, copy `.env.example` to a new file named `.env`.
    *   Open the `.env` file and fill in all the required values (`TELEGRAM_TOKEN`, `OWNER_ID`, `SECRET_KEY`, etc.).

4.  **Run the API Server:**
    *   From the `backend/` directory, run the following command:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be running at `http://127.0.0.1:8000` and the interactive documentation can be found at `http://127.0.0.1:8000/docs`.

### API Features

The API is protected by a login system. You can find the default credentials in `.env.example`. The API includes endpoints for stats, chat management, template management, and sending messages.

---

## Frontend

The `frontend/` directory contains a scaffolded React application created with Vite. To begin development:

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the development server:**
    ```bash
    npm run dev
    ```
The frontend application will then be running at `http://localhost:5173` (or a similar address).
