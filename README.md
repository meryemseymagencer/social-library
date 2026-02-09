# Social Library – Full Stack Web Application
Social Library is a full-stack social platform where users can discover books and movies, write reviews, and interact with other users.

## Features
- User authentication with JWT
- Book and movie listing
- Review and comment system
- User profiles (posts, followers, following)
- RESTful API architecture

## Tech Stack
**Backend**
- Python (FastAPI)
- PostgreSQL
- JWT Authentication

**Frontend**
- React
- Vite

## Project Structure
- `backend/` contains API logic, database models, and business rules
- `frontend/` contains the user interface
- `docs/` contains project documentation and reports

## Running the Project

### Backend
cd backend
uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev
