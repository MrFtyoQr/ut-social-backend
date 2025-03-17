from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import users, posts, comments, reactions
from app.core.config import settings

app = FastAPI(
    title="UT Social API",
    description="Social media platform for UT with file sharing capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(reactions.router, prefix="/api/reactions", tags=["reactions"])

@app.get("/")
async def root():
    return {"message": "Welcome to UT Social API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)