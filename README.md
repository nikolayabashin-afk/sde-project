# sde-project

## Prerequisites

```bat
# Docker Desktop must be running
# Ports 8000–8003 must be free

Step 1 — Start the System
docker compose up -d --build

Step 2 — Verify Services Are Running
docker compose ps

Step 3 — Open Swagger In order to see all the commands
http://localhost:8000/docs   (Orchestrator)
http://localhost:8001/docs   (Data Service)
http://localhost:8002/docs   (Adapter Service)
http://localhost:8003/docs   (Business Logic Service)

Step 4 — Run Demo 1 (Internal SOA Workflow)
This demo uses the internal mock marketplace.

demo_e2e.bat

What Demo 1 does:
    Creates a user
    Creates a tracked item
    Creates a rule
    Runs the orchestration cycle
    Fetches alerts

    
Step 5 — RESET SYSTEM (MANDATORY)

Demo scripts assume IDs start from 1.
Reset the system before running Demo 2.

docker compose down -v
docker compose up -d --build

Step 6 — Run Demo 2 (External DummyJSON Integration)

This demo uses a real external API (DummyJSON) to fetch the price.

demo_dummyjson16_e2e.bat


What Demo 2 does:
    Fetches product price from DummyJSON (Apple, id=16)
    Creates a user
    Creates a tracked item linked to DummyJSON
    Creates a rule using the external price
    Runs the orchestration cycle
    Fetches alerts

Step 7 — Stop the System

docker compose down

Step 8 — Full Cleanup 
Stops services and removes all stored data.

docker compose down -v