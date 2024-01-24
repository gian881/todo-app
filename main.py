from fastapi import FastAPI

from routers import auth, task

app = FastAPI(root_path='/api/v1')

app.include_router(auth.router)
app.include_router(task.router)
