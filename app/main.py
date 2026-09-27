from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import services, auth, tickets, sessions, requests, users, messages

app = FastAPI(title="Cyber Café & E-Services API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(services.router)
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(sessions.router)
app.include_router(requests.router)
app.include_router(users.router)
app.include_router(messages.router)


@app.get("/")
def root():
    return {"status": "ok"}


