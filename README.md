# Software Construction Process & Tools

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
