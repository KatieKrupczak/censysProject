# Censys Host Diff Tool

A full-stack application that ingests host snapshots collected at different points in time and highlights meaningful changes such as added or removed services, modified software versions, or newly discovered vulnerabilities.

Built with **FastAPI (Python)** and **React + Vite (TypeScript)**, the system demonstrates lightweight backend–frontend integration, clear data modeling, and a focus on explainable, human-readable diffs.


## How to Run

1. Clone the repository and open a terminal in the **`host-diff-tool/`** folder (where the `docker-compose.yml` file is located).  
2. Run the application with:

```bash
docker compose up
```

3. After the build completes:
   - Frontend UI: http://localhost:5173
   - Backend Health: http://localhost:8000/api/health
   - API Docs (Swagger UI): http://localhost:8000/docs
4. Stop all containers with:
```bash
docker compose down
```
All snapshot data and the SQLite database are stored in a persistent Docker volume name snapshots.

### Assumptions Made During Development
- Each uploaded snapshot JSON includes an ip, timestamp, and services field.

- If these fields are missing, the filename format host_<ip>_<timestamp>.json is used to infer them.

- Ports 8000 (backend) and 5173 (frontend) are available on the host.

- The project will be run from the host-diff-tool directory using Docker Compose.

### Simple Testing Instructions
#### Manual Testing
1. Run docker compose up and open the web UI at http://localhost:5173


2. Upload two host snapshot JSON files for the same IP address.

3. Select the host and two timestamps in the dropdowns and click Compare.

4. The application displays added, removed, or changed services between the snapshots.

5. Optionally verify backend endpoints at http://localhost:8000/docs

#### Automated Backend Tests: Storage & Diff Logic
The backend includes lightweight pytest unit tests for the storage and diff modules.
To run them inside the backend image:

```bash
docker compose run --rm api pytest -q
```

All tests should pass without errors.

### AI Techniques
AI tools were used throughout the development process to accelerate implementation and debugging:

- ChatGPT was used to generate boilerplate FastAPI and React code, structure Docker configurations, and troubleshoot dependency and environment issues.

- GitHub Copilot (VS Code inline AI assistant) provided real-time code completions and syntax suggestions while coding.

- These AI tools improved development speed and reduced setup errors


# Future Enhancements List:
- **Snapshot Caching:** Cache host and snapshot lists in the frontend to reduce repetitive API calls and improve responsiveness.  
- **Input Validation:** Prevent users from selecting the same snapshot for both comparison fields (A and B).  
- **Improved Diff Visualization:** Use color-coded highlighting and collapsible sections for added, removed, and changed services.  
- **File Validation on Upload:** Check for valid JSON structure and required fields (`ip`, `timestamp`, `services`) before sending files to the backend.  
- **Pagination or Search:** Add filtering and sorting for hosts and timestamps when handling large datasets.  
- **Error and Status Notifications:** Display toast or banner messages for successful uploads, invalid inputs, or failed API requests.  
- **Frontend State Persistence:** Remember the user’s last-selected host and timestamps between sessions.  
- **Security Hardening:** Add rate limiting, authentication, and input sanitization for production deployment.  
- **Automated CI Testing:** Integrate backend `pytest` and frontend build checks into a GitHub Actions workflow.