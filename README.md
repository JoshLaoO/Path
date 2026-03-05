Path

Path is an AI-powered Bible reading plan builder designed to help believers grow through personalized Scripture plans, guided reflection questions, and intentional journaling.

Instead of static, one-size-fits-all reading plans, Path allows users to generate structured, theme-based plans tailored to their spiritual goals and time availability. AI is used to assist in creating thoughtful reflection questions and prayer prompts while keeping Scripture central.

✨ Vision

Spiritual growth is not accidental — it happens through intentional time in God’s Word.

Path exists to help users:

Build consistent Bible reading habits

Reflect deeply on Scripture

Apply biblical truth personally

Grow in discipleship through structured guidance

The goal is not to replace Scripture with AI, but to use AI responsibly as a tool to support reflection, prayer, and application.

🚀 Features (Version 1)

🔐 User accounts

📖 Custom Bible reading plan generation (by theme + duration)

🧠 AI-generated reflection questions

🙏 AI-generated prayer prompts

✅ Daily progress tracking

✍️ Journaling for each reading day

🏗 Tech Stack

Backend

FastAPI (Python)

SQLAlchemy

SQLite (initially)

Frontend

React + Vite (in `frontend/`)

**Run the frontend (dev):** From project root, `cd frontend && npm install && npm run dev`. Open http://localhost:5173. The dev server proxies API requests to the backend (default http://localhost:8000).

**Run with Docker:** From project root, `docker compose up --build`. Backend at http://localhost:8000, frontend at http://localhost:3000. The frontend container serves the built app with nginx and proxies `/api` to the backend.

AI Integration

OpenAI API for reflection and prayer generation

🧠 How It Works

A user selects a theme (e.g., Anxiety, Identity, Evangelism).

The system generates a structured reading plan.

For each day, AI generates:

Reflection questions

A prayer prompt

The user can mark progress and journal insights.

🎯 Design Philosophy

Scripture is primary.

AI is assistive, not authoritative.

Structure promotes consistency.

Simplicity over feature bloat.

Built for long-term spiritual growth.

🔮 Future Roadmap

Small group mode

Shared plans

Leader dashboards

Plan marketplace

Advanced journaling insights

Multiple Bible translation support

⚠️ Disclaimer

Path uses AI to generate reflection questions and prompts. All content should be evaluated in light of Scripture. Users are encouraged to read passages in full context and engage thoughtfully with the Word.

📌 Project Status

Currently in active development (Version 1).