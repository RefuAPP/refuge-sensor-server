# Refuge Sensors API

## Overview

This API serves as the backend for the Refuge Sensors project. It's responsible for receiving sensor data, authenticating incoming data, do the logic of counting the number of people in a refugee 
and storing it in a database.

## Features

- Sensor data registration and authentication.
- HTTP status code-based error handling.
- Connectivity with PostgreSQL database.

## Quick Start

1. Clone the repository.
2. Install the dependencies using `pip install -r requirements.txt`.
3. Run the API using `uvicorn api:app --host 0.0.0.0 --port 8000`.

## API Endpoints

- **POST /sensor/**: Registers new sensor data.

## Authentication

The API uses basic authentication for sensor data. Make sure to include the `id_refugio` and `password` in each request to the `/sensor/` endpoint.

## Error Handling

The API returns appropriate HTTP status codes for each type of error:

- 404: Refuge not found
- 422: Invalid data format

## Dependencies

- FastAPI
- Uvicorn
- psycopg2
- Pydantic
