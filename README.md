## Getting Started

Deze instructies helpen je om de MobyPark applicatie lokaal te draaien.

### Vereisten

- Docker en Docker Compose geïnstalleerd op je systeem
- Git

### Applicatie Runnen

1. **Clone de repository**

   ```bash
   git clone https://github.com/bryandevuono/MobyPark-group3.git
   cd MobyPark-group3
   ```

2. **Maak een .env bestand aan**

   Navigeer naar de `v2` directory en maak een `.env` bestand aan met de volgende inhoud:

   ```bash
   cd v2
   ```

   Maak een `.env` bestand met de volgende configuratie:

   ```env
   # Database configuration
   DATABASE_URL="sqlite+aiosqlite:///./data/mobypark.db"

   # Bearer token secret key
   SECRET_KEY="groep3"

   # Default admin password
   DEFAULT_ADMIN_PASSWORD="groep3"
   ```

3. **Maak de database directory aan**

   ```bash
   mkdir -p data
   ```

4. **Start de applicatie met Docker Compose**

   ```bash
   docker compose up -d
   ```

   Dit start de volgende services:
   - API (FastAPI applicatie) op poort 8000
   - Elasticsearch op poort 9200
   - Kibana op poort 5601
   - Filebeat (log collector)

5.**Toegang tot de applicatie**

   - API: http://localhost:8000
   - API Documentatie (Swagger): http://localhost:8000/docs
   - Kibana (Logs): http://localhost:5601

### Applicatie Stoppen

Om de applicatie te stoppen:

```bash
docker compose down
```

Om de applicatie te stoppen en alle data te verwijderen (inclusief database en logs):

```bash
docker compose down -v
```

## Development Setup

<ol>

<li>

**Install Git**

Make sure you select "Checkout as-is, commit Unix-style line endings" during the installation process.

<ul>

<li>

[GitHub CLI](https://cli.github.com/)

</li>

<li>

(Optional) [Git Bash (Windows)](https://gitforwindows.org/)

</li>

</ul>

<li>

**Authenticate with GitHub CLI**

```sh
gh auth login
```

</li>

<li>

**Create Git Repository**

<ul>

<li>

**Create your own repository MobyPark on Github**

<p>
Browse to <a>github.com</a> and create <u>private</u> repository.
</p>

</li>

<li>

**Invite the teacher to your repository**

</li>

<li>

**Clone your git repository**

```bash
gh clone [Your_GitHub_Name]/MobyPark_[group]
```

</li>

<li>

**Configure git**

In order to commit and push your changes, you need identitify yourself.

Run the following commands from your MobyPark repo directory with your own github username and email address:

```sh
git config user.name "github_username"
git config user.email "student@hr.nl"
```

Once done, you can confirm that the information is set by running (see the last two lines):

```sh
git config --list
```
</li>

<li>

**Add, commit and push the copied contents**

<p>

Extract MobyPark.zip and add the contents to your (local) MobyPark repo

Run the following commands from your MobyPark repo directory

```sh
git add .
git commit -m "Added contents for MobyPark"
git push
```

</p>

</li>

</ul>

</li>

</ul>

</li>

<li>

**Install [Visual Studio Code](https://code.visualstudio.com)**

</li>

<li>

(Optional) Enable VSCode to be opened from the command line

Open the Command Palette and type 'shell command' in order to select the Shell command: 
Install 'code' command in PATH

Start VSCode with a command from current directory

```sh
code .
```

</li>

<li>

(Optional) Install VSCode Extensions

<ul>

<li>

[Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

</li>

<li>

[Black formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)

</li>

<li>

[Git Easy extension](https://marketplace.visualstudio.com/items?itemName=bibhasdn.git-easy)

</li>

<li>

[Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)

</li>

<li>

[Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)

</li>

<li>

[Mermaid extension](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)

</li>

<li>

[Graphviz (dot) language support](https://marketplace.visualstudio.com/items?itemName=joaompinto.vscode-graphviz)

</li>

</ul>

</li>

</ol>

## Running Tests

The project includes both unit tests and integration tests. Tests should be run inside the Docker container to ensure all dependencies are available.

### Start the Application

First, make sure the Docker container is running:

```bash
cd v2
docker compose up -d
```

### Run Tests in Docker

You have several options for running tests:

**Option 1: Using docker-compose (from v2 directory)**

```bash
# Run all tests
docker compose exec api pytest tests/ -v

# Run only unit tests
docker compose exec api pytest tests/unit/ -v

# Run only integration tests
docker compose exec api pytest tests/integration/ -v
```

**Option 2: Using docker exec (from project root)**

```bash
# Run all tests
docker exec v2-api-1 pytest tests/ -v

# Run only unit tests
docker exec v2-api-1 pytest tests/unit/ -v

# Run only integration tests
docker exec v2-api-1 pytest tests/integration/ -v
```

### Additional Test Options

```bash
# Run tests with more detailed output
docker compose exec api pytest tests/ -v -s

# Run tests and stop at first failure
docker compose exec api pytest tests/ -x

# Run a specific test file
docker compose exec api pytest tests/unit/test_calculations.py -v

# Run tests without verbose output
docker compose exec api pytest tests/
```

### Interactive Shell in Docker

If you need to run multiple commands or explore the container:

```bash
# Enter the container shell
docker compose exec api /bin/zsh

# Now you're inside the container, run tests directly
pytest tests/unit/ -v
pytest tests/integration/ -v

# Exit the container
exit
```

### Test Structure

- `tests/unit/` - Unit tests (no external dependencies)
  - `test_calculations.py` - Price calculation tests
  - `test_hashing.py` - Hashing function tests

- `tests/integration/` - Integration tests (requires running API)
  - `test_auth.py` - Authentication endpoint tests
  - `test_vehicles.py` - Vehicle endpoint tests
  - `test_parking_lots.py` - Parking lot endpoint tests
  - `test_parking_sessions.py` - Parking session endpoint tests
  - `test_reservations.py` - Reservation endpoint tests
  - `test_payments.py` - Payment endpoint tests
  - `test_profile.py` - Profile endpoint tests

### Stop the Application

When you're done testing:

```bash
docker-compose down
```

## Logging and Monitoring

The application uses the ELK (Elasticsearch, Logstash, Kibana) stack for centralized logging and monitoring.

### ELK Stack Components

- **Elasticsearch** - Stores and indexes log data
- **Kibana** - Web interface for viewing and analyzing logs
- **Filebeat** - Collects logs from the API container and sends them to Elasticsearch

### Starting the ELK Stack

The ELK stack starts automatically when you run:

```bash
cd v2
docker compose up -d
```

This will start:
- API container (port 8000)
- Elasticsearch (port 9200)
- Kibana (port 5601)
- Filebeat (log collector)

### Accessing Kibana

Once the stack is running, access Kibana at:

```
http://localhost:5601
```

**First-time setup:**
1. Navigate to **Management** > **Stack Management** > **Index Patterns**
2. Create a new index pattern: `mobypark-api-*`
3. Select `@timestamp` as the time field
4. Go to **Discover** to view your logs

### Log Levels

The application is configured with `INFO` level logging. Available log levels (in order of severity):

- `logging.debug()` - ❌ Not logged (below INFO level)
- `logging.info()` - ✅ Normal operations (logins, API calls, etc.)
- `logging.warning()` - ✅ Unusual but non-breaking events
- `logging.error()` - ✅ Errors requiring attention
- `logging.critical()` - ✅ Critical system failures

### Log Format

Logs are stored in **ECS (Elastic Common Schema)** JSON format for optimal Elasticsearch integration.

### Log Storage

Logs are stored in a Docker named volume:
- Container path: `/code/logs/mobypark_api.log`
- Volume name: `mobypark_logs`
- Log rotation: 10MB max file size, 5 backup files

### Viewing Logs

**Option 1: Via Kibana Dashboard (Recommended)**
```
http://localhost:5601
```

**Option 2: Docker Logs (Console Output)**
```bash
docker compose logs -f api
```

**Option 3: Access Log Files in Container**
```bash
docker exec -it v2-api-1 cat /code/logs/mobypark_api.log
```

**Option 4: Check Filebeat Status**
```bash
docker compose logs -f filebeat
```

### Troubleshooting

**Logs not appearing in Kibana:**
1. Check if Elasticsearch is running: `curl http://localhost:9200`
2. Verify Filebeat is collecting logs: `docker compose logs filebeat`
3. Ensure index pattern exists in Kibana
4. Check API container is writing logs: `docker exec -it v2-api-1 ls -la /code/logs`

**Reset the ELK Stack:**
```bash
docker compose down -v  # Removes volumes
docker compose up -d    # Fresh start
```
