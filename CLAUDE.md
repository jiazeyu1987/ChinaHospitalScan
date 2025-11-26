# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HBScan (医院层级扫查微服务) is a full-stack application consisting of a production-grade FastAPI backend microservice and a Next.js frontend interface for automated hospital hierarchy scanning and data collection across China using Large Language Models (LLMs). The system implements a four-tier administrative data structure: provinces → cities → districts → hospitals, with advanced features including web crawling, batch operations, and concurrent task processing.

### Project Structure
- **Backend (this directory)**: FastAPI microservice on port 8000
- **Frontend (../hospital-procurement-interface)**: Next.js application on port 3000

## Architecture

### Core Components

- **main.py** (1,307 lines): FastAPI application with 30+ REST endpoints, CORS middleware, UTF-8 logging
- **db.py** (1,351 lines): SQLite database layer with hierarchical schema, pagination, connection pooling
- **schemas.py** (333 lines): Comprehensive Pydantic models for data validation and API serialization
- **tasks.py** (1,106 lines): Async TaskManager with dual storage (memory + persistent), semaphore control
- **llm_client.py** (915 lines): Multi-provider LLM client (DashScope, OpenAI-compatible) with retry logic
- **crawl.py** (232 lines): Async web crawler for procurement link discovery using crawl4ai

### Database Schema

Six main tables with foreign key relationships:
- `tasks`: Background job tracking with status management (PENDING → RUNNING → COMPLETED/FAILED/CANCELLED)
- `provinces`: Province-level divisions with counts (cities_count, hospitals_count)
- `cities`: City-level divisions linked to provinces with district/hospital counts
- `districts`: District-level divisions linked to cities with hospital counts
- `hospitals`: Hospital information with detailed metadata (level, address, contact info)
- `hospital_info`: Extended hospital data from scans with website and procurement information

### Task Management System

The TaskManager provides enterprise-grade task processing:
- **Task Types**: HOSPITAL, PROVINCE, NATIONWIDE
- **Status Flow**: PENDING → RUNNING → COMPLETED/FAILED/CANCELLED
- **Concurrency Control**: Semaphore-based limiting for district refreshes (`MAX_CONCURRENT_DISTRICT_REFRESHES=3`)
- **Storage**: Dual persistence (in-memory + SQLite) for reliability
- **Cleanup**: Automatic cleanup of completed tasks with configurable retention
- **Background Processing**: FastAPI BackgroundTasks with detailed progress tracking

## Development Commands

### Quick Start

#### Backend (Port 8000)
```bash
# Method 1: Direct start with automatic port management
python main.py  # Automatically checks and frees port 8000

# Method 2: Using the provided batch script (Windows)
start_backend.bat

# Method 3: Manual startup with virtual environment
../venv/Scripts/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Port 3000) - Located at ../hospital-procurement-interface
```bash
# Navigate to frontend directory
cd ../hospital-procurement-interface

# Install dependencies (first time only)
npm install

# Start with automatic port management and browser opening
npm run dev:auto

# Alternative: Standard development mode
npm run dev
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Testing
```bash
# Test hospital website batch updates
python test_batch_update.py

# Manual API testing examples
curl -X POST "http://localhost:8000/hospitals/websites/batch-update" \
  -H "Content-Type: application/json" \
  -d '{"update_all": true, "skip_existing": false}'

curl -X GET "http://localhost:8000/health"
```

### Database Management
The SQLite database auto-initializes at `data/hospital_scanner.db` with full schema creation. Supports switching to PostgreSQL via `DATABASE_URL` configuration.

### Port Management Features
Both backend and frontend include automatic port management:

#### Backend (Port 8000)
- **Automatic Port Checking**: `python main.py` automatically detects and terminates processes using port 8000
- **Cross-Platform Support**: Works on Windows, macOS, and Linux using psutil
- **Safe Process Termination**: Graceful termination followed by force kill if needed
- **Port Release Verification**: Confirms port is fully available before startup

#### Frontend (Port 3000)
- **Enhanced Development Scripts**: Located in `../hospital-procurement-interface/scripts/`
  - `dev:auto`: Recommended script using `cross-port-killer` and `open` packages
  - `dev:full`: Full-featured version using only Node.js built-ins
- **Automatic Browser Opening**: Opens `http://localhost:3000` after server startup
- **Cross-Platform Compatibility**: Windows (`start`), macOS (`open`), Linux (`xdg-open`)

## API Endpoints

### Core Scanning Operations
- `POST /scan`: Create single hospital scan task with hospital name and URL
- `POST /refresh/all`: Full nationwide data refresh (all provinces cascade)
- `POST /refresh/all-provinces`: Refresh all provinces (cascade to cities/districts/hospitals)
- `POST /refresh/province/{province_name}`: Refresh province and its cities
- `POST /refresh/province-cities-districts/{province_name}`: Full province cascade refresh
- `POST /refresh/city/{city_name}`: Refresh all districts in a city
- `POST /refresh/district/{district_name}`: Refresh all hospitals in a district

### Hospital Website Management
- `POST /hospital/website`: Update hospital website information
- `POST /hospitals/websites/batch-update`: Batch update hospital websites (supports limit, skip_existing)
- `GET /hospitals/websites/status`: Get website update status

### Web Crawling & Procurement
- `POST /procurement/crawl`: Crawl procurement information from hospital websites
- `GET /procurement/status`: Get procurement crawling status

### Data Query Endpoints
- `GET /provinces`: Paginated province list with counts
- `GET /cities?province={province_name}`: Cities by province (supports name or ID)
- `GET /districts?city={city_name}`: Districts by city (supports name or ID)
- `GET /hospitals?district={district_name}`: Hospitals by district (supports name or ID)
- `GET /hospitals/search?q={query}`: Hospital search with pagination
- `GET /hospitals/info/{hospital_id}`: Detailed hospital information

### Task Management
- `GET /task/{task_id}`: Task status and detailed results
- `GET /tasks`: List all tasks with pagination and filtering
- `POST /tasks/cleanup`: Clean completed tasks older than 1 hour
- `POST /tasks/cleanup/{hours}`: Clean tasks older than specified hours
- `DELETE /tasks/clear`: Delete all task records
- `DELETE /database/clear`: Clear all data (preserve structure)

### System & Health
- `GET /`: Service information and statistics
- `GET /health`: Health check with database connectivity

### Development Endpoints
- `POST /test/district`: Test district endpoint registration
- `POST /test/city`: Test city endpoint registration

## Advanced Features

### Cascade Refresh System
The system implements sophisticated cascade refresh operations:
- **Province Cascade**: `/refresh/province-cities-districts/{province}` refreshes complete hierarchy
- **Concurrent Processing**: Limited concurrent district refreshes via semaphore control
- **Progress Tracking**: Real-time progress updates at each hierarchy level
- **Error Isolation**: Failures in one region don't stop the entire operation

### Web Crawling Integration
- **Technology**: crawl4ai async web crawler for procurement link discovery
- **Domain Filtering**: Intelligent filtering of hospital website domains
- **Deep Crawling**: Multi-level crawling for procurement information
- **Database Integration**: Automatic storage of discovered procurement links

### Batch Operations
- **Hospital Websites**: Batch update hospital website information with progress tracking
- **Configurable Limits**: Support for batch size limits and skipping existing data
- **Background Processing**: Long-running batch operations with status monitoring

## Key Implementation Details

### LLM Integration
Multi-provider LLM client supporting:
- **Alibaba DashScope**: Primary LLM service with Chinese language optimization
- **OpenAI-Compatible**: Support for OpenAI, DeepSeek, and other compatible APIs
- **Structured Extraction**: JSON-based data extraction with comprehensive error handling
- **Rate Limiting**: Intelligent retry mechanisms and API throttling prevention
- **Response Validation**: Structured validation of LLM responses for data integrity

### Data Processing Flow
1. **National Scan**: LLM retrieves all provinces with metadata
2. **Cascade Processing**: Province → Cities → Districts → Hospitals
3. **Intelligent Deduplication**: Name-based deduplication with fuzzy matching
4. **Website Discovery**: Automated hospital website discovery via LLM
5. **Procurement Crawling**: Deep crawling for procurement information
6. **Progress Tracking**: Real-time updates at each processing stage

### Concurrency Management
- **Async Architecture**: Complete async/await implementation throughout
- **Semaphore Control**: Limited concurrent operations to prevent API overload
- **Background Tasks**: FastAPI BackgroundTasks for long-running operations
- **Resource Management**: Connection pooling and timeout management

## Configuration

### Core Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///data/hospital_scanner.db  # SQLite or PostgreSQL

# LLM Service Configuration (Required)
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
LLM_MODEL=qwen-turbo
LLM_TIMEOUT=30

# Alternative LLM Provider
DASHSCOPE_API_KEY=your_dashscope_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### Performance & Concurrency
```bash
# Concurrency Control
MAX_CONCURRENT_TASKS=10
MAX_CONCURRENT_DISTRICT_REFRESHES=3
TASK_TIMEOUT=300
MAX_TASKS_PER_HOUR=100

# Database Performance
DB_POOL_SIZE=10
DB_POOL_MAX_OVERFLOW=20
HTTP_POOL_CONNECTIONS=10
```

### Monitoring & Logging
```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/scanner.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# Health Monitoring
MONITORING_ENABLED=true
HEALTH_CHECK_INTERVAL=60
```

## Logging Strategy

Two-tier logging system with UTF-8 encoding:
- **Main Application**: `logs/scanner.log` - General application logs and API requests
- **LLM Debugging**: `logs/llm_debug.log` - Detailed LLM API request/response logging
- **Progress Tracking**: Real-time progress updates for long-running tasks
- **Error Reporting**: Comprehensive error logging with context and stack traces

## Development & Testing

### Test Scripts
- **test_batch_update.py**: Comprehensive testing for hospital website batch updates
- **Test Endpoints**: Built-in development endpoints for API route verification

### Frontend Development Scripts
Located at `../hospital-procurement-interface/scripts/`:
- **dev-simple.js**: Recommended development script with automatic port management and browser opening
- **dev-with-port-check.js**: Full-featured version with detailed logging and process management
- **README.md**: Detailed usage instructions and troubleshooting guide

### Manual Testing Examples
```bash
# Test website discovery for specific hospital
curl -X POST "http://localhost:8000/hospital/website" \
  -H "Content-Type: application/json" \
  -d '{"hospital_name": "北京协和医院"}'

# Trigger cascade refresh for specific province
curl -X POST "http://localhost:8000/refresh/province-cities-districts/北京市"
```

### Dependencies Management

#### Backend Requirements
Key dependencies in `requirements.txt`:
- **psutil==5.9.6**: Added for automatic port management and process termination
- FastAPI ecosystem: fastapi, uvicorn[standard], pydantic
- HTTP clients: requests, httpx
- Async support: aiofiles, nest-asyncio
- LLM integration: All existing dependencies maintained

#### Frontend Dependencies
Key additions in `package.json`:
- **cross-port-killer**: Cross-platform port management for Node.js
- **open**: Cross-platform browser opening utility

## Development Workflow

### Full Stack Development
1. **Start Backend**: `python main.py` (auto-manages port 8000)
2. **Start Frontend**: `cd ../hospital-procurement-interface && npm run dev:auto` (auto-manages port 3000 and opens browser)
3. **Access Application**: Frontend at `http://localhost:3000`, Backend API at `http://localhost:8000`

### Port Conflict Resolution
Both applications handle port conflicts automatically:
- Backend uses psutil to detect and terminate processes on port 8000
- Frontend uses cross-port-killer to manage port 3000
- Both provide detailed logging of the port management process