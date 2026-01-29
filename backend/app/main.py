from dotenv import load_dotenv
load_dotenv() # Load env vars before importing services

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import skills, planner, interview, simulator, aws_test
from app.services import dynamodb

app = FastAPI(title="EduCorp API", version="0.1.0")

# CORS setup (Allow Frontend)
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skills.router, prefix="/api", tags=["skills"])
app.include_router(planner.router, prefix="/api", tags=["planner"])
app.include_router(interview.router, prefix="/api", tags=["interview"])
app.include_router(simulator.router, prefix="/api", tags=["simulator"])
app.include_router(aws_test.router, prefix="/api", tags=["aws_test"])

@app.on_event("startup")
async def startup_event():
    print("Initializing AWS DynamoDB Tables...")
    dynamodb.init_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to EduCorp API"}
