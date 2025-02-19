# Architecture

Our system is a digital twin of Los Angeles to simulate COVID‑19 spread using realistic human agents. The key components are:

- **Frontend:** Built with Next.js, using Leaflet for interactive maps and Chart.js for simulation charts.
- **Backend:** FastAPI server that runs a simulation engine. Agents are given realistic profiles (age, occupation, income) and daily routines generated using chain‑of‑thought reasoning.
- **ML Module:** A custom Gym environment and RL training using Stable Baselines3 to explore intervention strategies.
- **Infrastructure:** Docker Compose and Kubernetes for container orchestration and deployment.

Each module communicates via REST APIs or through shared data stores.
