# linkace-sentry

## Overview
`linkace-sentry` is a sidecar microservice designed to monitor bookmarks in a running LinkAce instance. It utilizes the LinkAce REST API to check the status of bookmarks and tag any dead links without requiring a rebuild of the LinkAce application.

## Project Structure
The project is organized as follows:

```
linkace-sentry
├── src
│   ├── main.py                # Entry point of the application
│   ├── api                    # API module
│   │   ├── __init__.py
│   │   └── routes.py          # Defines API routes
│   ├── services               # Service layer for business logic
│   │   ├── __init__.py
│   │   ├── linkace_client.py   # LinkAce API wrapper
│   │   └── bookmark_checker.py  # URL checking logic
│   ├── models                 # Data models
│   │   ├── __init__.py
│   │   └── bookmark.py        # Bookmark and Tag models
│   ├── config                 # Configuration settings
│   │   ├── __init__.py
│   │   └── settings.py        # Application settings
│   └── utils                  # Utility functions
│       ├── __init__.py
│       └── validators.py      # Input validation functions
├── tests                      # Unit tests
│   ├── __init__.py
│   ├── test_api.py           # Tests for API routes
│   ├── test_services.py       # Tests for service functions
│   └── test_utils.py         # Tests for utility functions
├── requirements.txt           # Project dependencies
├── Dockerfile                 # Docker image configuration
├── docker-compose.yml         # Docker Compose configuration
└── README.md                  # Project documentation
```

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd linkace-sentry
pip install -r requirements.txt
```

## Usage
To run the service, you can use the following command:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Configuration
Configuration settings can be adjusted in `src/config/settings.py`. Ensure that the LinkAce API URL and any necessary authentication tokens are correctly set.

## API Endpoints
The service exposes the following API endpoints:

- **GET /healthz**: Check the health status of the service.
- **GET /metrics**: Retrieve metrics for monitoring.
- **POST /run-once**: Trigger a one-time check of all bookmarks.

## Testing
To run the tests, use the following command:

```bash
pytest
```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.