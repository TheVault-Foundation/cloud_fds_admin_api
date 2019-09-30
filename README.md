# Cloud FDS Admin Api

Cloud FDS Admin API for Dashboard

## Development

### Prequisites

- Python 3.6+
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [pipenv](https://pipenv.readthedocs.io/en/latest/)

### Setup

- Install dependencies and activate virtualenv:

  ```bash
  pipenv install
  pipenv shell # activate python virtualenv
  ```

- Install development tools

  - Run command:

    ```bash
    pipenv install --dev
    ```

- Configure your env file

  ```bash
  cp env.example .env
  # then edit your .env file
  ```

- Build & launch development server

  ```bash
  docker-compose build
  docker-compose up # localhost:5000
  ```
