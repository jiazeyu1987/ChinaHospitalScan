# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HBScan (医院层级扫查微服务) is a FastAPI-based microservice for automated hospital hierarchy scanning and data collection using Large Language Models (LLMs). The system collects hierarchical administrative data (provinces → cities → districts → hospitals) across China and stores it in a structured SQLite database.

## Architecture

### Core Components

- **main.py**: FastAPI application entry point with REST API endpoints
- **db.py**: SQLite database layer managing hierarchical data storage
- **schemas.py**: Pydantic models defining API request/response structures and enums
- **tasks.py**: Asynchronous task management system with background job processing
- **llm_client.py**: LLM API client for data extraction (supports Alibaba DashScope and OpenAI-compatible APIs)

### Database Schema

The system uses SQLite with four main tables:
- `tasks`: Background job tracking with status management
- `provinces`: Province-level administrative divisions
- `cities`: City-level divisions linked to provinces
- `districts`: District-level divisions linked to cities
- `hospitals`: Hospital information linked to districts

### Task Management System

The TaskManager handles both in-memory and persistent task storage:
- Tasks have types: HOSPITAL, PROVINCE, NATIONWIDE
- Status flow: PENDING → RUNNING → COMPLETED/FAILED
- Automatic cleanup of completed tasks (configurable retention)
- Background task execution with detailed progress logging

## Development Commands

### Starting the Service
```bash
# Using the provided batch script (Windows)
start_backend.bat

# Manual activation and start
../venv/Scripts/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variables
set DASHSCOPE_API_KEY=your_api_key_here
set LLM_BASE_URL=https://dashscope.aliyuncs.com/api/v1/
set LLM_MODEL=deepseek-r1
```

### Database Management
The SQLite database is auto-created at `data/hospital_scanner_new.db`. No manual migration needed.

## API Endpoints

### Core Scanning Operations
- `POST /scan`: Create single hospital scan task
- `POST /refresh/all`: Full nationwide data refresh (all provinces)
- `POST /refresh/all-provinces`: Cascade refresh all provinces
- `POST /refresh/province/{province_name}`: Refresh province and cities
- `POST /refresh/province-cities-districts/{province_name}`: Full province cascade
- `POST /refresh/city/{city_name}`: Refresh all districts in a city
- `POST /refresh/district/{district_name}`: Refresh hospitals in a district

### Data Query Endpoints
- `GET /provinces`: Paginated province list
- `GET /cities?province={province_name}`: Cities by province (supports name or ID)
- `GET /districts?city={city_name}`: Districts by city (supports name or ID)
- `GET /hospitals?district={district_name}`: Hospitals by district (supports name or ID)
- `GET /hospitals/search?q={query}`: Hospital search

### Task Management
- `GET /task/{task_id}`: Task status and results
- `GET /tasks`: List all tasks
- `POST /tasks/cleanup`: Clean completed tasks older than 1 hour
- `POST /tasks/cleanup/{hours}`: Clean tasks older than specified hours
- `DELETE /tasks/clear`: Delete all task records
- `DELETE /database/clear`: Clear all data (preserve structure)

### System
- `GET /`: Service info
- `GET /health`: Health check

## Key Implementation Details

### LLM Integration
The system uses LLM APIs for intelligent data extraction:
- Province/city/district hierarchy discovery
- Hospital information extraction (name, level, contact info, departments)
- Structured JSON response parsing with error handling
- Rate limiting and retry mechanisms

### Error Handling
- Comprehensive logging with UTF-8 encoding support
- Separate log files: `logs/scanner.log` (main) and `logs/llm_debug.log` (LLM)
- Graceful degradation when LLM APIs are unavailable
- Detailed error messages in task results

### Data Processing Flow
1. National scan retrieves all provinces via LLM
2. For each province: cascade through cities → districts → hospitals
3. Automatic deduplication based on names
4. Progress tracking at each level
5. Detailed logging for monitoring and debugging

### Concurrency Management
- Async/await throughout the codebase
- Background task processing via FastAPI BackgroundTasks
- Rate limiting between API calls to prevent throttling
- Thread-safe task state management

## Configuration

### Environment Variables
- `DASHSCOPE_API_KEY`: LLM API authentication (required)
- `LLM_BASE_URL`: API endpoint URL (defaults to Alibaba DashScope)
- `LLM_MODEL`: Model name (defaults to deepseek-r1)

### Database Configuration
- Path: `data/hospital_scanner_new.db`
- Auto-initialization on startup
- Foreign key constraints enforced
- Indexes on name fields for fast lookups

## Logging Strategy

Two-tier logging system:
- Main application logs: `logs/scanner.log`
- LLM API debugging: `logs/llm_debug.log`

Both use UTF-8 encoding to properly handle Chinese characters and include timestamps, log levels, and detailed progress information.

## Testing Notes

The service includes several test endpoints for development:
- `POST /test/district`: Test district endpoint registration
- `POST /test/city`: Test city endpoint registration

These help verify API routing during development.