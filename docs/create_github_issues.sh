#!/bin/bash

# Script to create all 50 GitHub issues for Vector Agents project
# Generated automatically from Vector_Agents_GitHub_Issues.md

set -e

REPO="devinda0/veracity-hackathon"

echo "Creating GitHub Issues for Veracity Hackathon..."
echo "Repository: $REPO"
echo ""

# Create milestones
echo "Creating milestones..."
gh milestone create -R "$REPO" "M1" --description "Foundation & Infrastructure" 2>/dev/null || echo "  M1 already exists"
gh milestone create -R "$REPO" "M2" --description "Core Agents & Backend" 2>/dev/null || echo "  M2 already exists"
gh milestone create -R "$REPO" "M3" --description "Frontend & Integration" 2>/dev/null || echo "  M3 already exists"
gh milestone create -R "$REPO" "M4" --description "Polish, Observability & Deploy" 2>/dev/null || echo "  M4 already exists"

echo ""
echo "Creating labels..."
# Create labels
LABELS=(
    "frontend"
    "backend"
    "agents"
    "infra"
    "integration"
    "testing"
    "documentation"
    "priority:critical"
    "priority:high"
    "priority:medium"
)

for label in "${LABELS[@]}"; do
    gh label create -R "$REPO" "$label" 2>/dev/null || echo "  $label already exists"
done

echo ""
echo "Creating issues..."
echo ""

# Issue #1: Project Repo & Monorepo Setup with Docker Compose
ISSUE_BODY_1=$(cat <<'ISSUE_1_EOF'
### Description
Initialize Git repository with monorepo structure (frontend/, backend/, agents/), Docker Compose for local dev environment with PostgreSQL, MongoDB, Qdrant, Redis services, .gitignore for Node/Python/venv, and GitHub Actions CI skeleton.

### Acceptance Criteria
- [ ] Git repo initialized with monorepo structure (frontend/, backend/, agents/, docker-compose.yml)
- [ ] Docker Compose defines PostgreSQL, MongoDB, Qdrant, Redis services with named volumes
- [ ] All services healthcheck endpoints configured
- [ ] .gitignore covers Node, Python, venv, .env, __pycache__
- [ ] GitHub Actions workflow file created for CI (lint, test placeholders)
- [ ] README.md with quick-start instructions and architecture diagram
- [ ] .env.example file with all required env vars documented

### Implementation Details
Create root directory structure:
```
vector-agents/
├── docker-compose.yml          # All dev services
├── .gitignore
├── .env.example
├── docker-compose.prod.yml     # For later (M4)
├── frontend/                   # React SPA
├── backend/                    # FastAPI
├── agents/                     # LangGraph
├── .github/
│   └── workflows/
│       └── ci.yml             # Basic lint + test runs
└── README.md
```

Docker Compose services:
- **MongoDB** (port 27017): replica set mode for transactions, volume `mongo_data`
- **Qdrant** (port 6333): vector DB, volume `qdrant_data`
- **Redis** (port 6379): session/cache, volume `redis_data`
- **PostgreSQL** (port 5432, optional for later): volume `postgres_data`

Each service needs:
- Health check: `healthcheck: { test: [...], interval: 10s, timeout: 5s, retries: 3 }`
- Environment vars for credentials (admin/password)
- Named volumes with driver `local`

.env.example:
```
MONGO_URI=mongodb://mongo:27017/vector-agents
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
JWT_SECRET=dev-secret-change-in-prod
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=...
SERPAPI_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

GitHub Actions (.github/workflows/ci.yml):
```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint backend
        run: cd backend && make lint  # placeholder
      - name: Lint frontend
        run: cd frontend && npm run lint  # placeholder
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backend tests
        run: cd backend && make test  # placeholder
```

Makefile in root (optional but recommended):
```makefile
.PHONY: up down logs shell-mongo shell-redis
up:
	docker-compose up -d
down:
	docker-compose down
logs:
	docker-compose logs -f
shell-mongo:
	docker-compose exec mongo mongosh
```

### Files to Create/Modify
- `docker-compose.yml`
- `.gitignore`
- `.env.example`
- `.github/workflows/ci.yml`
- `Makefile` (optional)
- `README.md`

---


ISSUE_1_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Project Repo & Monorepo Setup with Docker Compose" \
  --body "$ISSUE_BODY_1" \
  --label "backend" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: Project Repo & Monorepo Setup with Docker Compose -> $ISSUE_URL"
sleep 1

# Issue #2: React App Scaffolding with Vite + TypeScript + Tailwind + Zustand
ISSUE_BODY_2=$(cat <<'ISSUE_2_EOF'
### Description
Initialize React SPA with Vite, TypeScript, Tailwind CSS, and Zustand for state management. Set up directory structure for components, stores, hooks, types, utils. Configure Vite for HMR and build optimization.

### Acceptance Criteria
- [ ] React 18 + Vite SPA scaffolded with `npm create vite@latest`
- [ ] TypeScript strict mode enabled
- [ ] Tailwind CSS configured with PostCSS
- [ ] Zustand store architecture with chat, ui, session stores
- [ ] Base directory structure: components/, stores/, hooks/, types/, utils/, assets/
- [ ] App.tsx entry point with basic layout (sidebar + main area)
- [ ] Vite config optimized: code splitting, CSS modules, API proxy to backend
- [ ] ESLint + Prettier configured

### Implementation Details
Create frontend/ with:
```
frontend/
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── package.json
├── .eslintrc.json
├── .prettierrc
├── src/
│   ├── main.tsx                # React entry
│   ├── App.tsx                 # Root component
│   ├── index.css               # Tailwind import
│   ├── components/
│   │   ├── ChatStream.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── InputBar.tsx
│   │   ├── SessionSidebar.tsx
│   │   ├── ArtifactRenderer.tsx
│   │   ├── Artifacts/          # Scorecard, TrendMap, etc.
│   │   └── UI/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       └── Modal.tsx
│   ├── stores/
│   │   ├── chatStore.ts        # Zustand chat + message state
│   │   ├── uiStore.ts          # UI toggles, modals
│   │   └── sessionStore.ts     # Current session, history
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useChat.ts
│   │   └── useSession.ts
│   ├── types/
│   │   ├── index.ts            # All TS interfaces
│   │   ├── Message.ts
│   │   ├── Artifact.ts
│   │   └── Agent.ts
│   └── utils/
│       ├── api.ts              # Fetch wrapper
│       ├── websocket.ts        # WS client
│       └── format.ts           # Formatters
└── public/
    └── favicon.svg
```

vite.config.ts:
```typescript
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
})
```

tailwind.config.js:
```javascript
export default {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
      },
    },
  },
  plugins: [],
}
```

Zustand stores (stores/chatStore.ts):
```typescript
import { create } from 'zustand'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  artifacts?: Artifact[]
  timestamp: Date
}

interface ChatStore {
  messages: Message[]
  loading: boolean
  addMessage: (msg: Message) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  loading: false,
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  clearMessages: () => set({ messages: [] }),
}))
```

package.json dependencies:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.4.0",
    "typescript": "^5.1.0",
    "eslint": "^8.45.0",
    "prettier": "^3.0.0"
  }
}
```

### Files to Create/Modify
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `frontend/package.json`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/index.css`
- `frontend/src/stores/chatStore.ts`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/stores/sessionStore.ts`
- `frontend/src/types/index.ts`
- `frontend/src/utils/api.ts`

---


ISSUE_2_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "React App Scaffolding with Vite + TypeScript + Tailwind + Zustand" \
  --body "$ISSUE_BODY_2" \
  --label "frontend" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: React App Scaffolding with Vite + TypeScript + Tailwind + Zustand -> $ISSUE_URL"
sleep 1

# Issue #3: FastAPI App Factory & Configuration
ISSUE_BODY_3=$(cat <<'ISSUE_3_EOF'
### Description
Create FastAPI app factory, config management via Pydantic, CORS setup, health endpoint, structured logging, and exception handlers. Establish the base FastAPI app structure for mounting routers.

### Acceptance Criteria
- [ ] FastAPI app factory in backend/app/core/app.py with config injection
- [ ] Pydantic BaseSettings for environment config (dev/prod/test modes)
- [ ] CORS middleware enabled for frontend origin
- [ ] Health check endpoint: GET /api/health returns { "status": "ok" }
- [ ] Global exception handler for APIException
- [ ] Structured logging with JSON formatter (for OpenTelemetry)
- [ ] Router mounting structure with versioning (e.g., /api/v1/auth, /api/v1/chat)
- [ ] Startup/shutdown events for resource cleanup

### Implementation Details
backend/ structure:
```
backend/
├── requirements.txt
├── Dockerfile
├── .env.example
├── main.py                    # Entry point
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic settings
│   │   ├── app.py             # FastAPI factory
│   │   ├── logger.py          # Structured logging
│   │   └── exceptions.py       # Custom exceptions
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py            # JWT verification
│   │   └── logging.py         # Request/response logging
│   ├── routers/               # API routes (added later)
│   ├── services/              # Business logic (added later)
│   ├── models/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   └── chat.py
│   └── db/                    # Database clients (added later)
└── tests/
    └── test_health.py
```

app/core/config.py:
```python
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    APP_NAME: str = "Vector Agents"
    APP_ENV: Literal["dev", "prod", "test"] = "dev"
    DEBUG: bool = False

    # API
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api"

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Database
    MONGO_URI: str
    QDRANT_URL: str
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # External APIs
    OPENAI_API_KEY: str
    FIRECRAWL_API_KEY: str = ""
    SERPAPI_API_KEY: str = ""

    # Observability
    OTEL_ENABLED: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

app/core/app.py:
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logger import get_logger
from app.core.exceptions import APIException
import time

logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
        debug=settings.DEBUG,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration * 1000,
        )
        return response

    # Exception handler
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_code": exc.error_code},
        )

    # Health endpoint
    @app.get(f"{settings.API_PREFIX}/health")
    async def health_check():
        return {"status": "ok", "version": settings.API_VERSION}

    # Startup/shutdown
    @app.on_event("startup")
    async def startup_event():
        logger.info("app_startup", version=settings.API_VERSION)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("app_shutdown")

    return app

# Router mounting (in main.py)
# from app.routers import auth, chat, sessions
# app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth")
# app.include_router(chat.router, prefix=f"{settings.API_PREFIX}/chat")
```

app/core/exceptions.py:
```python
class APIException(Exception):
    def __init__(self, detail: str, status_code: int = 400, error_code: str = "GENERIC"):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code

class AuthException(APIException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, 401, "UNAUTHORIZED")

class NotFoundError(APIException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, 404, "NOT_FOUND")
```

main.py:
```python
from app.core.app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

requirements.txt:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pymongo==4.6.0
qdrant-client==2.7.0
redis==5.0.0
```

### Files to Create/Modify
- `backend/main.py`
- `backend/requirements.txt`
- `backend/app/core/config.py`
- `backend/app/core/app.py`
- `backend/app/core/exceptions.py`
- `backend/app/core/logger.py`

---


ISSUE_3_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "FastAPI App Factory & Configuration" \
  --body "$ISSUE_BODY_3" \
  --label "backend" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: FastAPI App Factory & Configuration -> $ISSUE_URL"
sleep 1

# Issue #4: MongoDB Connection & Database Schemas
ISSUE_BODY_4=$(cat <<'ISSUE_4_EOF'
### Description
Initialize MongoDB client with connection pooling, define collection schemas (users, sessions, chat_history, audit_logs, business_context), create indexes for query optimization, and provide MongoDB initialization utility.

### Acceptance Criteria
- [ ] MongoDB client singleton in backend/app/db/mongo.py with connection pooling
- [ ] Pydantic schemas for all documents: User, Session, ChatMessage, AuditLog, BusinessContext
- [ ] Indexes created: sessions(user_id, created_at), chat_history(session_id, timestamp), audit_logs(user_id, action, created_at)
- [ ] Migration/init script to set up collections and indexes on startup
- [ ] Error handling for connection timeouts and replica set status checks
- [ ] Async context manager for MongoDB operations

### Implementation Details
backend/app/db/mongo.py:
```python
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from app.core.config import settings
from app.core.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

class MongoDBClient:
    _instance: Optional[AsyncClient] = None
    _db: Optional[AsyncDatabase] = None

    @classmethod
    async def connect(cls) -> AsyncDatabase:
        if cls._instance is None:
            cls._instance = AsyncClient(
                settings.MONGO_URI,
                maxPoolSize=10,
                minPoolSize=2,
                serverSelectionTimeoutMS=5000,
            )
            # Check connection
            try:
                await cls._instance.admin.command("ismaster")
                logger.info("mongodb_connected")
            except Exception as e:
                logger.error("mongodb_connection_failed", error=str(e))
                raise

        cls._db = cls._instance["vector-agents"]
        return cls._db

    @classmethod
    async def disconnect(cls):
        if cls._instance:
            cls._instance.close()
            logger.info("mongodb_disconnected")

    @classmethod
    def get_db(cls) -> AsyncDatabase:
        if cls._db is None:
            raise RuntimeError("MongoDB not initialized. Call connect() first.")
        return cls._db

# FastAPI dependency
async def get_mongo_db() -> AsyncDatabase:
    return MongoDBClient.get_db()
```

backend/app/models/user.py:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserDoc(BaseModel):
    _id: Optional[str] = Field(default=None, alias="id")
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        populate_by_name = True
```

backend/app/models/session.py:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SessionDoc(BaseModel):
    _id: Optional[str] = None
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False
    message_count: int = 0

    class Config:
        populate_by_name = True
```

backend/app/models/chat.py:
```python
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class ChatMessageDoc(BaseModel):
    _id: Optional[str] = None
    session_id: str = Field(index=True)
    role: str  # "user" or "assistant"
    content: str
    artifacts: Optional[list[dict]] = None
    agent_trace: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
```

backend/app/models/audit.py:
```python
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class AuditLogDoc(BaseModel):
    _id: Optional[str] = None
    user_id: str = Field(index=True)
    action: str = Field(index=True)  # "login", "upload_context", "run_query", etc.
    resource: Optional[str] = None
    status: str  # "success" or "failure"
    details: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

backend/app/db/init.py:
```python
from motor.motor_asyncio import AsyncDatabase
from app.core.logger import get_logger

logger = get_logger(__name__)

async def init_mongodb(db: AsyncDatabase):
    """Initialize collections and indexes"""

    # Create collections if not exist
    collections = ["users", "sessions", "chat_history", "audit_logs", "business_context"]
    existing = await db.list_collection_names()

    for col in collections:
        if col not in existing:
            await db.create_collection(col)
            logger.info("mongodb_collection_created", collection=col)

    # Create indexes
    await db.sessions.create_index([("user_id", 1), ("created_at", -1)])
    await db.chat_history.create_index([("session_id", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("user_id", 1), ("action", 1), ("created_at", -1)])
    await db.users.create_index("email", unique=True)

    logger.info("mongodb_indexes_created")
```

In app.py startup:
```python
@app.on_event("startup")
async def startup_event():
    db = await MongoDBClient.connect()
    await init_mongodb(db)
    logger.info("app_startup", version=settings.API_VERSION)

@app.on_event("shutdown")
async def shutdown_event():
    await MongoDBClient.disconnect()
    logger.info("app_shutdown")
```

### Files to Create/Modify
- `backend/app/db/mongo.py`
- `backend/app/db/init.py`
- `backend/app/models/user.py`
- `backend/app/models/session.py`
- `backend/app/models/chat.py`
- `backend/app/models/audit.py`
- `backend/requirements.txt` (add `motor==3.3.1`)

---


ISSUE_4_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "MongoDB Connection & Database Schemas" \
  --body "$ISSUE_BODY_4" \
  --label "backend" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: MongoDB Connection & Database Schemas -> $ISSUE_URL"
sleep 1

# Issue #5: Qdrant Client Setup & Collections
ISSUE_BODY_5=$(cat <<'ISSUE_5_EOF'
### Description
Initialize Qdrant client with async support, create vector collections for business context (768-dim embeddings) and research cache, set up collection policies, and provide initialization utility.

### Acceptance Criteria
- [ ] Qdrant async client in backend/app/db/qdrant.py
- [ ] Two collections: "business_context" and "research_cache" (both 768-dim for OpenAI embeddings)
- [ ] Collection setup: distance metric (Cosine), payload schema with metadata fields
- [ ] Index creation for payload fields: session_id, source_type, created_at
- [ ] Error handling for connection failures and collection conflicts
- [ ] Batch upsert utility for efficient embedding ingestion

### Implementation Details
backend/app/db/qdrant.py:
```python
from qdrant_client.async_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, FieldCondition, MatchValue
from app.core.config import settings
from app.core.logger import get_logger
from typing import Optional, List
import asyncio

logger = get_logger(__name__)

class QdrantClient:
    _instance: Optional[AsyncQdrantClient] = None

    EMBEDDING_DIM = 768  # OpenAI embedding dimension
    COLLECTIONS = {
        "business_context": "Business context documents and metadata",
        "research_cache": "Research results from external sources",
    }

    @classmethod
    async def connect(cls) -> AsyncQdrantClient:
        if cls._instance is None:
            cls._instance = AsyncQdrantClient(
                url=settings.QDRANT_URL,
                timeout=30.0,
            )

            # Health check
            try:
                health = await cls._instance.get_collections()
                logger.info("qdrant_connected")
            except Exception as e:
                logger.error("qdrant_connection_failed", error=str(e))
                raise

        return cls._instance

    @classmethod
    async def disconnect(cls):
        if cls._instance:
            # AsyncQdrantClient closes on del or explicit close
            cls._instance = None
            logger.info("qdrant_disconnected")

    @classmethod
    async def get_client(cls) -> AsyncQdrantClient:
        if cls._instance is None:
            await cls.connect()
        return cls._instance

async def init_qdrant_collections(client: AsyncQdrantClient):
    """Initialize Qdrant collections with proper configuration"""

    for collection_name, description in QdrantClient.COLLECTIONS.items():
        try:
            # Check if collection exists
            existing = await client.collection_exists(collection_name)
            if existing:
                logger.info("qdrant_collection_exists", collection=collection_name)
                continue

            # Create collection
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=QdrantClient.EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
                # Payload schema (stored as JSON in Qdrant)
            )

            # Create indexes for filtering
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="session_id",
                field_schema="keyword",
            )
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="source_type",
                field_schema="keyword",
            )
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="created_at",
                field_schema="integer",
            )

            logger.info("qdrant_collection_created", collection=collection_name)

        except Exception as e:
            logger.error("qdrant_collection_init_failed", collection=collection_name, error=str(e))
            raise

# Utility for batch upsert
async def qdrant_upsert_batch(
    client: AsyncQdrantClient,
    collection_name: str,
    points: List[PointStruct],
):
    """Batch upsert points to Qdrant (handles pagination)"""
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        try:
            await client.upsert(
                collection_name=collection_name,
                points=batch,
            )
        except Exception as e:
            logger.error("qdrant_upsert_failed", collection=collection_name, error=str(e))
            raise

# Utility for search
async def qdrant_search(
    client: AsyncQdrantClient,
    collection_name: str,
    vector: List[float],
    limit: int = 10,
    filter_conditions: Optional[List[FieldCondition]] = None,
):
    """Search Qdrant with optional filtering"""
    try:
        results = await client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
            query_filter={"must": filter_conditions} if filter_conditions else None,
        )
        return results
    except Exception as e:
        logger.error("qdrant_search_failed", collection=collection_name, error=str(e))
        raise
```

In app.py startup:
```python
from app.db.qdrant import QdrantClient, init_qdrant_collections

@app.on_event("startup")
async def startup_event():
    qdrant_client = await QdrantClient.connect()
    await init_qdrant_collections(qdrant_client)
    logger.info("app_startup")
```

backend/app/db/__init__.py:
```python
from app.db.mongo import MongoDBClient, get_mongo_db
from app.db.qdrant import QdrantClient

__all__ = ["MongoDBClient", "QdrantClient", "get_mongo_db"]
```

### Files to Create/Modify
- `backend/app/db/qdrant.py`
- `backend/app/db/__init__.py`
- `backend/requirements.txt` (add `qdrant-client==2.7.0`)

---


ISSUE_5_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Qdrant Client Setup & Collections" \
  --body "$ISSUE_BODY_5" \
  --label "backend" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: Qdrant Client Setup & Collections -> $ISSUE_URL"
sleep 1

# Issue #6: JWT Auth System - Register, Login, Middleware
ISSUE_BODY_6=$(cat <<'ISSUE_6_EOF'
### Description
Implement JWT authentication with user registration, login endpoints, token generation/validation, password hashing, and middleware for protected routes. Store users in MongoDB.

### Acceptance Criteria
- [ ] POST /api/v1/auth/register endpoint (email, password, name)
- [ ] POST /api/v1/auth/login endpoint (email, password) returns access token
- [ ] JWT token validation middleware protecting /api/v1/protected routes
- [ ] Password hashing with bcrypt
- [ ] Token refresh mechanism (optional but recommended)
- [ ] Error responses: invalid credentials, user exists, expired token
- [ ] User stored in MongoDB users collection with indexed email

### Implementation Details
backend/app/core/security.py:
```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
```

backend/app/middleware/auth.py:
```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.core.security import decode_access_token
from app.core.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials) -> dict:
    """Extract and validate JWT token"""
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return {"user_id": user_id, "email": payload.get("email")}

    except Exception as e:
        logger.warning("auth_validation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
```

backend/app/models/auth.py:
```python
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
```

backend/app/routers/auth.py:
```python
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncDatabase
from app.db.mongo import get_mongo_db
from app.models.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.models.user import UserDoc
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logger import get_logger
from bson import ObjectId

logger = get_logger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: AsyncDatabase = Depends(get_mongo_db)):
    # Check if user exists
    existing = await db.users.find_one({"email": request.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    # Create user
    user_doc = {
        "email": request.email,
        "password_hash": hash_password(request.password),
        "name": request.name,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    }

    result = await db.users.insert_one(user_doc)
    logger.info("user_registered", user_id=str(result.inserted_id), email=request.email)

    return UserResponse(
        id=str(result.inserted_id),
        email=request.email,
        name=request.name,
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncDatabase = Depends(get_mongo_db)):
    # Find user
    user = await db.users.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password_hash"]):
        logger.warning("login_failed", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate token
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}
    )

    logger.info("user_login_success", user_id=str(user["_id"]), email=request.email)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
    )
```

In main.py:
```python
from app.routers import auth
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth")
```

requirements.txt additions:
```
passlib==1.7.4
bcrypt==4.1.0
pyjwt==2.8.0
python-multipart==0.0.6
email-validator==2.1.0
```

### Files to Create/Modify
- `backend/app/core/security.py`
- `backend/app/middleware/auth.py`
- `backend/app/models/auth.py`
- `backend/app/routers/auth.py`
- `backend/requirements.txt`

---


ISSUE_6_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "JWT Auth System - Register, Login, Middleware" \
  --body "$ISSUE_BODY_6" \
  --label "backend" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: JWT Auth System - Register, Login, Middleware -> $ISSUE_URL"
sleep 1

# Issue #7: LangGraph Base Project Setup, State Schema, Empty Graph Shell
ISSUE_BODY_7=$(cat <<'ISSUE_7_EOF'
### Description
Initialize LangGraph project with proper directory structure, state schema definition, base graph factory, and empty router/planner shell. Define TypedDict for orchestrator state including messages, context, agent outputs.

### Acceptance Criteria
- [ ] agents/ directory with LangGraph project structure
- [ ] State schema (TypedDict) with messages, user_context, agent_outputs, metadata
- [ ] Graph factory in agents/orchestrator/graph.py
- [ ] Router node placeholder (to be filled in #13)
- [ ] Imports for LangGraph, Pydantic, logging
- [ ] requirements.txt with langgraph, langchain, openai dependencies

### Implementation Details
agents/ structure:
```
agents/
├── requirements.txt
├── orchestrator/
│   ├── __init__.py
│   ├── graph.py               # Main graph factory
│   ├── state.py               # State schema
│   ├── nodes.py               # Node definitions (router, synthesis)
│   └── config.py              # Agent configs
├── domain_agents/
│   ├── __init__.py
│   ├── market_trend.py
│   ├── competitive_landscape.py
│   ├── win_loss.py
│   ├── pricing_packaging.py
│   ├── positioning_messaging.py
│   └── adjacent_market.py
├── tools/
│   ├── __init__.py
│   ├── base.py                # Base tool class
│   ├── data_sources.py        # Firecrawl, SerpAPI, etc.
│   ├── embedding.py           # Embedding tools
│   └── analysis.py            # Analysis helpers
├── messaging/
│   ├── __init__.py
│   ├── a2a_protocol.py        # A2A message definitions
│   └── message_bus.py         # Message bus implementation
└── utils/
    ├── __init__.py
    ├── logger.py
    └── validators.py
```

agents/orchestrator/state.py:
```python
from typing import TypedDict, Optional, Any, List
from langchain_core.messages import BaseMessage

class AgentOutput(TypedDict):
    agent_name: str
    status: str  # "pending", "running", "completed", "failed"
    result: Optional[dict[str, Any]]
    error: Optional[str]

class OrchestrationState(TypedDict):
    """State schema for LangGraph orchestrator"""

    # Input
    user_query: str
    user_id: str
    session_id: str

    # Context
    business_context: Optional[str]  # Uploaded customer/market context
    conversation_history: List[BaseMessage]

    # Processing
    planned_agents: Optional[List[str]]  # Agents to run (set by router)
    current_agent: Optional[str]

    # Outputs
    agent_outputs: dict[str, AgentOutput]  # Results from each agent
    synthesis_result: Optional[dict[str, Any]]  # Final synthesized response
    artifacts: Optional[List[dict[str, Any]]]  # Visual artifacts (charts, tables)

    # Metadata
    start_time: Optional[float]
    trace_data: dict[str, Any]  # For observability
    tokens_used: Optional[int]
    cost_estimate: Optional[float]
```

agents/orchestrator/graph.py:
```python
from langgraph.graph import StateGraph
from typing import Dict, Any
from agents.orchestrator.state import OrchestrationState
from agents.orchestrator.nodes import router_node, synthesis_node
from agents.utils.logger import get_logger

logger = get_logger(__name__)

def create_orchestrator_graph() -> StateGraph:
    """Create the main LangGraph orchestrator"""

    graph = StateGraph(OrchestrationState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("synthesis", synthesis_node)

    # Domain agents (to be added in future issues)
    # graph.add_node("market_trend_agent", market_trend_agent)
    # graph.add_node("competitive_landscape_agent", competitive_landscape_agent)
    # ... (5 more domain agents)

    # Edges
    graph.add_edge("__start__", "router")
    # Conditional edge from router to domain agents (to be added)
    # graph.add_conditional_edges(
    #     "router",
    #     route_to_agents,
    #     {agent: agent for agent in DOMAIN_AGENTS}
    # )
    # graph.add_edge([f"{agent}" for agent in DOMAIN_AGENTS], "synthesis")
    graph.add_edge("synthesis", "__end__")

    compiled = graph.compile()
    logger.info("orchestrator_graph_compiled")

    return compiled
```

agents/orchestrator/nodes.py:
```python
from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

async def router_node(state: OrchestrationState) -> OrchestrationState:
    """Router/Planner node - determine which agents to invoke"""
    # TODO: Implement in Issue #13
    logger.info("router_node_invoked", session_id=state["session_id"])
    state["planned_agents"] = []
    return state

async def synthesis_node(state: OrchestrationState) -> OrchestrationState:
    """Synthesis node - aggregate agent outputs"""
    # TODO: Implement in Issue #25
    logger.info("synthesis_node_invoked", session_id=state["session_id"])
    state["synthesis_result"] = {}
    return state
```

agents/orchestrator/config.py:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator"""

    # Model
    router_model: str = "gpt-4"
    agent_model: str = "gpt-4"
    synthesis_model: str = "gpt-4"

    # Behavior
    max_agents: int = 6
    max_iterations: int = 3
    timeout_seconds: int = 120

    # Observability
    enable_tracing: bool = True
    log_level: str = "INFO"

    # API
    openai_api_key: Optional[str] = None
    mongo_uri: Optional[str] = None
    qdrant_url: Optional[str] = None
```

agents/utils/logger.py:
```python
import logging
import json
from typing import Any

def get_logger(name: str) -> logging.Logger:
    """Get configured logger for agents"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.JSONFormatter(
            fmt=json.dumps({
                "timestamp": "%(asctime)s",
                "level": "%(levelname)s",
                "logger": "%(name)s",
                "message": "%(message)s",
            })
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)
```

agents/requirements.txt:
```
langgraph==0.0.24
langchain==0.1.0
langchain-openai==0.0.6
python-dotenv==1.0.0
pydantic==2.5.0
motor==3.3.1
qdrant-client==2.7.0
aiohttp==3.9.0
```

### Files to Create/Modify
- `agents/requirements.txt`
- `agents/orchestrator/state.py`
- `agents/orchestrator/graph.py`
- `agents/orchestrator/nodes.py`
- `agents/orchestrator/config.py`
- `agents/utils/logger.py`

---


ISSUE_7_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "LangGraph Base Project Setup, State Schema, Empty Graph Shell" \
  --body "$ISSUE_BODY_7" \
  --label "agents" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: LangGraph Base Project Setup, State Schema, Empty Graph Shell -> $ISSUE_URL"
sleep 1

# Issue #8: A2A Message Schema & Message Bus Implementation
ISSUE_BODY_8=$(cat <<'ISSUE_8_EOF'
### Description
Define Agent-to-Agent (A2A) communication protocol with message schema, message bus implementation for inter-agent messaging, routing, and delivery guarantees.

### Acceptance Criteria
- [ ] A2A message schema with sender, recipient, message_type, payload, correlation_id
- [ ] MessageBus class with async publish/subscribe
- [ ] Message routing by agent name
- [ ] Delivery tracking and timeouts
- [ ] Message serialization (JSON)
- [ ] Support for request-response patterns

### Implementation Details
agents/messaging/a2a_protocol.py:
```python
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"

class A2AMessage(BaseModel):
    """Inter-agent communication message"""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str  # Agent name (e.g., "router", "market_trend_agent")
    recipient: str  # Target agent name, or "broadcast"
    message_type: MessageType
    payload: dict[str, Any]
    correlation_id: Optional[str] = None  # For request-response linking
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "A2AMessage":
        return cls(**data)
```

agents/messaging/message_bus.py:
```python
from agents.messaging.a2a_protocol import A2AMessage, MessageType
from agents.utils.logger import get_logger
from typing import Callable, Dict, List, Optional
import asyncio
from datetime import datetime, timedelta

logger = get_logger(__name__)

class MessageBus:
    """Pub/Sub message bus for inter-agent communication"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._pending_messages: Dict[str, A2AMessage] = {}
        self._message_history: List[A2AMessage] = []

    async def publish(self, message: A2AMessage) -> None:
        """Publish a message"""
        logger.info(
            "message_published",
            message_id=message.message_id,
            sender=message.sender,
            recipient=message.recipient,
        )

        self._message_history.append(message)

        # Get subscribers for recipient or broadcast
        recipients = [message.recipient]
        if message.recipient == "broadcast":
            recipients = list(self._subscribers.keys())

        for recipient in recipients:
            if recipient in self._subscribers:
                for callback in self._subscribers[recipient]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logger.error(
                            "message_callback_failed",
                            recipient=recipient,
                            error=str(e),
                        )

    def subscribe(self, agent_name: str, callback: Callable) -> None:
        """Subscribe an agent to messages"""
        if agent_name not in self._subscribers:
            self._subscribers[agent_name] = []
        self._subscribers[agent_name].append(callback)
        logger.info("agent_subscribed", agent=agent_name)

    async def request_response(
        self,
        message: A2AMessage,
        timeout_seconds: int = 30,
    ) -> Optional[A2AMessage]:
        """Send a message and wait for response"""
        correlation_id = message.message_id
        message.message_type = MessageType.REQUEST

        # Create response waiter
        response_event = asyncio.Event()
        response_holder: List[Optional[A2AMessage]] = [None]

        def response_callback(resp: A2AMessage):
            if resp.correlation_id == correlation_id:
                response_holder[0] = resp
                response_event.set()

        # Subscribe to responses
        self.subscribe(message.sender, response_callback)

        # Publish request
        await self.publish(message)

        # Wait for response with timeout
        try:
            await asyncio.wait_for(response_event.wait(), timeout=timeout_seconds)
            return response_holder[0]
        except asyncio.TimeoutError:
            logger.warning("request_response_timeout", correlation_id=correlation_id)
            return None

    def get_history(self, sender: Optional[str] = None) -> List[A2AMessage]:
        """Get message history"""
        if sender:
            return [m for m in self._message_history if m.sender == sender]
        return self._message_history

    def clear_history(self):
        """Clear message history"""
        self._message_history.clear()

# Global message bus instance
_message_bus: Optional[MessageBus] = None

def get_message_bus() -> MessageBus:
    """Get or create message bus"""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus
```

Usage example (in agent nodes):
```python
from agents.messaging.message_bus import get_message_bus
from agents.messaging.a2a_protocol import A2AMessage, MessageType

async def my_agent_node(state):
    bus = get_message_bus()

    # Send request
    request = A2AMessage(
        sender="my_agent",
        recipient="market_trend_agent",
        message_type=MessageType.REQUEST,
        payload={"query": "market trends"}
    )

    response = await bus.request_response(request, timeout_seconds=30)
    if response:
        result = response.payload
```

### Files to Create/Modify
- `agents/messaging/a2a_protocol.py`
- `agents/messaging/message_bus.py`
- `agents/messaging/__init__.py`

---


ISSUE_8_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "A2A Message Schema & Message Bus Implementation" \
  --body "$ISSUE_BODY_8" \
  --label "agents" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: A2A Message Schema & Message Bus Implementation -> $ISSUE_URL"
sleep 1

# Issue #9: Base Data Source Tool Class with Retry + Rate Limiting
ISSUE_BODY_9=$(cat <<'ISSUE_9_EOF'
### Description
Create base class for data source tools with built-in retry logic, exponential backoff, rate limiting, error handling, and logging. Subclasses will implement specific sources (Firecrawl, SerpAPI, etc.).

### Acceptance Criteria
- [ ] BaseDataSourceTool abstract class with execute(), _fetch(), error handling
- [ ] Retry decorator with exponential backoff (max 3 retries)
- [ ] Rate limiter using asyncio.Semaphore (configurable concurrent calls)
- [ ] Circuit breaker for failing sources
- [ ] Error classification (rate-limited, timeout, network, validation)
- [ ] Structured logging with attempt tracking
- [ ] Request/response caching (optional, via decorator)

### Implementation Details
agents/tools/base.py:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import asyncio
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from agents.utils.logger import get_logger

logger = get_logger(__name__)

class ErrorType(str, Enum):
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    VALIDATION = "validation"
    UNKNOWN = "unknown"

@dataclass
class ToolResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    attempts: int = 0
    duration_ms: float = 0.0

class CircuitBreaker:
    """Circuit breaker for failing services"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("circuit_breaker_opened")

    def record_success(self):
        self.failure_count = 0
        self.is_open = False

    def can_execute(self) -> bool:
        if not self.is_open:
            return True

        # Check recovery timeout
        if self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            if elapsed > self.recovery_timeout:
                self.is_open = False
                self.failure_count = 0
                logger.info("circuit_breaker_recovered")
                return True

        return False

class BaseDataSourceTool(ABC):
    """Base class for data source tools"""

    def __init__(
        self,
        name: str,
        max_retries: int = 3,
        timeout_seconds: int = 30,
        rate_limit: int = 5,  # Max concurrent requests
    ):
        self.name = name
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.rate_limiter = asyncio.Semaphore(rate_limit)
        self.circuit_breaker = CircuitBreaker()

    async def execute(self, **kwargs) -> ToolResult:
        """Main execution method with retry + rate limiting"""

        if not self.circuit_breaker.can_execute():
            return ToolResult(
                success=False,
                error="Service temporarily unavailable (circuit breaker open)",
                error_type=ErrorType.UNKNOWN,
            )

        start_time = time.time()
        attempt = 0

        while attempt < self.max_retries:
            attempt += 1

            try:
                async with self.rate_limiter:
                    result = await self._fetch(**kwargs)

                self.circuit_breaker.record_success()

                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    "tool_execution_success",
                    tool=self.name,
                    attempt=attempt,
                    duration_ms=duration_ms,
                )

                return ToolResult(
                    success=True,
                    data=result,
                    attempts=attempt,
                    duration_ms=duration_ms,
                )

            except asyncio.TimeoutError:
                logger.warning(
                    "tool_execution_timeout",
                    tool=self.name,
                    attempt=attempt,
                )
                error_type = ErrorType.TIMEOUT

            except Exception as e:
                error_msg = str(e)

                if "rate limit" in error_msg.lower():
                    error_type = ErrorType.RATE_LIMIT
                    # Exponential backoff for rate limits
                    await asyncio.sleep(2 ** attempt)
                elif "connection" in error_msg.lower():
                    error_type = ErrorType.NETWORK
                else:
                    error_type = ErrorType.UNKNOWN

                logger.warning(
                    "tool_execution_failed",
                    tool=self.name,
                    attempt=attempt,
                    error_type=error_type,
                    error=error_msg,
                )

            if attempt < self.max_retries:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** (attempt - 1)
                await asyncio.sleep(wait_time)

        # All retries exhausted
        self.circuit_breaker.record_failure()

        duration_ms = (time.time() - start_time) * 1000
        return ToolResult(
            success=False,
            error=f"Failed after {attempt} attempts",
            error_type=error_type,
            attempts=attempt,
            duration_ms=duration_ms,
        )

    @abstractmethod
    async def _fetch(self, **kwargs) -> Dict[str, Any]:
        """
        Subclasses implement this method to fetch data
        Should raise exceptions for errors
        """
        pass

    def reset_circuit_breaker(self):
        """Manual circuit breaker reset"""
        self.circuit_breaker = CircuitBreaker()
        logger.info("circuit_breaker_reset", tool=self.name)
```

agents/tools/__init__.py:
```python
from agents.tools.base import BaseDataSourceTool, ToolResult, ErrorType

__all__ = ["BaseDataSourceTool", "ToolResult", "ErrorType"]
```

### Files to Create/Modify
- `agents/tools/base.py`
- `agents/tools/__init__.py`

---


ISSUE_9_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Base Data Source Tool Class with Retry + Rate Limiting" \
  --body "$ISSUE_BODY_9" \
  --label "agents" --label "infra" --label "priority:high" \
  --milestone "M1")

echo "Created: Base Data Source Tool Class with Retry + Rate Limiting -> $ISSUE_URL"
sleep 1

# Issue #10: WebSocket Manager - Connection Handling & Message Protocol
ISSUE_BODY_10=$(cat <<'ISSUE_10_EOF'
### Description
Implement WebSocket connection manager for streaming agent responses, handling connection lifecycle, message encoding/decoding, and client registry for broadcasting.

### Acceptance Criteria
- [ ] WebSocket endpoint at /api/v1/ws/chat
- [ ] Connection manager tracking active clients per session
- [ ] Message protocol: type (status, artifact, final), content, metadata
- [ ] Sending streaming updates from orchestrator to frontend
- [ ] Error handling and graceful disconnection
- [ ] Message queue for offline clients (optional)

### Implementation Details
backend/app/websocket/manager.py:
```python
from fastapi import WebSocket
from typing import Dict, Set, Optional
from app.core.logger import get_logger
import json
from datetime import datetime

logger = get_logger(__name__)

class ConnectionManager:
    """Manage WebSocket connections per session"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.client_metadata: Dict[str, dict] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept and register a WebSocket connection"""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()

        self.active_connections[session_id].add(websocket)
        self.client_metadata[id(websocket)] = {
            "session_id": session_id,
            "connected_at": datetime.utcnow(),
        }

        logger.info("websocket_connected", session_id=session_id, clients=len(self.active_connections[session_id]))

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        ws_id = id(websocket)
        if ws_id in self.client_metadata:
            meta = self.client_metadata[ws_id]
            session_id = meta["session_id"]

            if session_id in self.active_connections:
                self.active_connections[session_id].discard(websocket)

            del self.client_metadata[ws_id]
            logger.info("websocket_disconnected", session_id=session_id)

    async def broadcast(self, session_id: str, message: dict):
        """Broadcast message to all clients in a session"""
        if session_id not in self.active_connections:
            return

        disconnected = []

        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(
                    "websocket_send_failed",
                    session_id=session_id,
                    error=str(e),
                )
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning("websocket_send_failed", error=str(e))
            self.disconnect(websocket)

    def get_session_clients(self, session_id: str) -> int:
        """Get number of active clients in a session"""
        return len(self.active_connections.get(session_id, set()))

# Global manager instance
_manager: Optional[ConnectionManager] = None

def get_connection_manager() -> ConnectionManager:
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
```

backend/app/websocket/protocol.py:
```python
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any

class MessageType(str, Enum):
    STATUS = "status"           # Agent status update
    ARTIFACT = "artifact"       # Chart, table, etc.
    THINKING = "thinking"       # Agent thinking/reasoning
    FINAL = "final"             # Final response
    ERROR = "error"             # Error message

class WSMessage(BaseModel):
    """WebSocket message format"""

    type: MessageType
    session_id: str
    timestamp: str
    content: str                 # Main content/data
    agent: Optional[str] = None  # Which agent sent this
    metadata: Optional[dict[str, Any]] = None

    def to_json(self) -> dict:
        return {
            "type": self.type.value,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "content": self.content,
            "agent": self.agent,
            "metadata": self.metadata,
        }

# Factory functions
def status_message(session_id: str, agent: str, status: str) -> dict:
    return {
        "type": "status",
        "session_id": session_id,
        "agent": agent,
        "content": status,
        "timestamp": datetime.utcnow().isoformat(),
    }

def artifact_message(session_id: str, artifact_type: str, data: dict) -> dict:
    return {
        "type": "artifact",
        "session_id": session_id,
        "content": artifact_type,
        "metadata": data,
        "timestamp": datetime.utcnow().isoformat(),
    }

def thinking_message(session_id: str, agent: str, reasoning: str) -> dict:
    return {
        "type": "thinking",
        "session_id": session_id,
        "agent": agent,
        "content": reasoning,
        "timestamp": datetime.utcnow().isoformat(),
    }

def final_message(session_id: str, content: str) -> dict:
    return {
        "type": "final",
        "session_id": session_id,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
    }

def error_message(session_id: str, error: str) -> dict:
    return {
        "type": "error",
        "session_id": session_id,
        "content": error,
        "timestamp": datetime.utcnow().isoformat(),
    }
```

backend/app/routers/websocket.py:
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from app.websocket.manager import get_connection_manager
from app.websocket.protocol import error_message
from app.core.logger import get_logger
from app.db.mongo import get_mongo_db
from motor.motor_asyncio import AsyncDatabase

logger = get_logger(__name__)
router = APIRouter()

@router.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for chat streaming"""

    manager = get_connection_manager()

    try:
        await manager.connect(session_id, websocket)

        # Keep connection alive and receive messages
        while True:
            data = await websocket.receive_text()
            # Process incoming messages (queries, context updates, etc.)
            logger.debug("websocket_received", session_id=session_id, data=data[:50])

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception as e:
        logger.error("websocket_error", session_id=session_id, error=str(e))
        await manager.broadcast(session_id, error_message(session_id, str(e)))
        manager.disconnect(websocket)
```

In main.py:
```python
from app.routers import websocket
app.include_router(websocket.router, prefix=f"{settings.API_PREFIX}")
```

requirements.txt additions:
```
websockets==12.0
```

### Files to Create/Modify
- `backend/app/websocket/manager.py`
- `backend/app/websocket/protocol.py`
- `backend/app/routers/websocket.py`
- `backend/requirements.txt`

---


ISSUE_10_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "WebSocket Manager - Connection Handling & Message Protocol" \
  --body "$ISSUE_BODY_10" \
  --label "backend" --label "infra" --label "priority:critical" \
  --milestone "M1")

echo "Created: WebSocket Manager - Connection Handling & Message Protocol -> $ISSUE_URL"
sleep 1

# Issue #11: Chat Store & useWebSocket Hook
ISSUE_BODY_11=$(cat <<'ISSUE_11_EOF'
### Description
Implement Zustand chat store for managing conversation state, and React hook for WebSocket connection lifecycle, message streaming, and error recovery.

### Acceptance Criteria
- [ ] Zustand chatStore: messages array, loading state, current session
- [ ] useWebSocket hook with auto-reconnect, message queueing
- [ ] Handle incoming message types: status, artifact, thinking, final, error
- [ ] Update chatStore on incoming messages
- [ ] Connection state (connecting, connected, disconnected)
- [ ] Error handling and user notifications

### Implementation Details
frontend/src/stores/chatStore.ts:
```typescript
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  artifacts?: Artifact[]
  agentTrace?: AgentTrace
  timestamp: Date
  tokensUsed?: number
  cost?: number
}

export interface Artifact {
  id: string
  type: string // "scorecard", "trendmap", "heatmap", etc.
  title: string
  data: Record<string, unknown>
}

export interface AgentTrace {
  agents: AgentStatus[]
  duration_ms: number
}

export interface AgentStatus {
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: Record<string, unknown>
  error?: string
}

interface ChatStore {
  messages: Message[]
  loading: boolean
  error: string | null
  sessionId: string | null
  currentQuery: string

  addMessage: (msg: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  clearMessages: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSessionId: (id: string) => void
  setCurrentQuery: (query: string) => void
  addArtifact: (messageId: string, artifact: Artifact) => void
  setAgentTrace: (messageId: string, trace: AgentTrace) => void
}

export const useChatStore = create<ChatStore>()(
  devtools((set) => ({
    messages: [],
    loading: false,
    error: null,
    sessionId: null,
    currentQuery: '',

    addMessage: (msg) =>
      set((state) => ({
        messages: [...state.messages, msg],
      })),

    updateMessage: (id, updates) =>
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === id ? { ...m, ...updates } : m
        ),
      })),

    clearMessages: () => set({ messages: [] }),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    setSessionId: (id) => set({ sessionId: id }),
    setCurrentQuery: (query) => set({ currentQuery: query }),

    addArtifact: (messageId, artifact) =>
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === messageId
            ? {
                ...m,
                artifacts: [...(m.artifacts || []), artifact],
              }
            : m
        ),
      })),

    setAgentTrace: (messageId, trace) =>
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === messageId ? { ...m, agentTrace: trace } : m
        ),
      })),
  }))
)
```

frontend/src/hooks/useWebSocket.ts:
```typescript
import { useEffect, useRef, useCallback } from 'react'
import { useChatStore, Message, Artifact, AgentTrace } from '../stores/chatStore'
import { useUIStore } from '../stores/uiStore'
import { v4 as uuidv4 } from 'uuid'

interface WSMessage {
  type: 'status' | 'artifact' | 'thinking' | 'final' | 'error'
  session_id: string
  content: string
  agent?: string
  metadata?: Record<string, unknown>
  timestamp: string
}

const RECONNECT_DELAY_MS = 3000
const MAX_RECONNECT_ATTEMPTS = 5

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const messageQueueRef = useRef<string[]>([])
  const connectionStateRef = useRef<'connecting' | 'connected' | 'disconnected'>('disconnected')

  const { sessionId, addMessage, updateMessage, addArtifact, setAgentTrace, setLoading, setError } = useChatStore()
  const { setConnectionStatus } = useUIStore()

  const connect = useCallback(() => {
    if (!sessionId) return

    connectionStateRef.current = 'connecting'
    setConnectionStatus('connecting')

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws/chat/${sessionId}`

    wsRef.current = new WebSocket(wsUrl)

    wsRef.current.onopen = () => {
      console.log('[WebSocket] Connected')
      connectionStateRef.current = 'connected'
      setConnectionStatus('connected')
      reconnectAttemptsRef.current = 0

      // Flush message queue
      while (messageQueueRef.current.length > 0) {
        const msg = messageQueueRef.current.shift()
        if (msg) wsRef.current?.send(msg)
      }
    }

    wsRef.current.onmessage = (event) => {
      try {
        const wsMsg: WSMessage = JSON.parse(event.data)
        handleWSMessage(wsMsg)
      } catch (e) {
        console.error('[WebSocket] Parse error:', e)
      }
    }

    wsRef.current.onerror = (event) => {
      console.error('[WebSocket] Error:', event)
      setError('WebSocket error occurred')
    }

    wsRef.current.onclose = () => {
      console.log('[WebSocket] Disconnected')
      connectionStateRef.current = 'disconnected'
      setConnectionStatus('disconnected')
      setLoading(false)

      // Auto-reconnect
      if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttemptsRef.current++
        setTimeout(connect, RECONNECT_DELAY_MS)
      }
    }
  }, [sessionId, setConnectionStatus, setError, setLoading])

  const handleWSMessage = (msg: WSMessage) => {
    const messageId = uuidv4()

    switch (msg.type) {
      case 'status':
        // Agent status update
        console.log(`[Agent ${msg.agent}] ${msg.content}`)
        break

      case 'thinking':
        // Agent reasoning
        addMessage({
          id: messageId,
          role: 'assistant',
          content: msg.content,
          timestamp: new Date(msg.timestamp),
        })
        break

      case 'artifact':
        // Add artifact to last message
        const artifact: Artifact = {
          id: uuidv4(),
          type: msg.content,
          title: msg.metadata?.title as string,
          data: msg.metadata?.data as Record<string, unknown>,
        }

        const lastMsg = useChatStore.getState().messages[useChatStore.getState().messages.length - 1]
        if (lastMsg) {
          addArtifact(lastMsg.id, artifact)
        }
        break

      case 'final':
        // Final response
        addMessage({
          id: messageId,
          role: 'assistant',
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          agentTrace: msg.metadata?.trace as AgentTrace,
          tokensUsed: msg.metadata?.tokens_used as number,
          cost: msg.metadata?.cost as number,
        })
        setLoading(false)
        break

      case 'error':
        setError(msg.content)
        setLoading(false)
        break
    }
  }

  const send = useCallback((message: string) => {
    if (connectionStateRef.current === 'connected' && wsRef.current) {
      wsRef.current.send(JSON.stringify({ content: message }))
    } else {
      messageQueueRef.current.push(JSON.stringify({ content: message }))
      if (connectionStateRef.current === 'disconnected') {
        connect()
      }
    }
  }, [connect])

  useEffect(() => {
    if (sessionId) {
      connect()
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [sessionId, connect])

  return {
    send,
    isConnected: connectionStateRef.current === 'connected',
    status: connectionStateRef.current,
  }
}
```

### Files to Create/Modify
- `frontend/src/stores/chatStore.ts`
- `frontend/src/hooks/useWebSocket.ts`
- `frontend/package.json` (add `uuid` dependency)

---


ISSUE_11_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Chat Store & useWebSocket Hook" \
  --body "$ISSUE_BODY_11" \
  --label "frontend" --label "integration" --label "priority:high" \
  --milestone "M1")

echo "Created: Chat Store & useWebSocket Hook -> $ISSUE_URL"
sleep 1

# Issue #12: Session Sidebar & Session CRUD API
ISSUE_BODY_12=$(cat <<'ISSUE_12_EOF'
### Description
Build session management: backend REST API for CRUD operations (create, read, update, delete, list), and frontend sidebar component for session selection and creation.

### Acceptance Criteria
- [ ] POST /api/v1/sessions - create session
- [ ] GET /api/v1/sessions - list user's sessions
- [ ] GET /api/v1/sessions/{id} - get session with chat history
- [ ] PUT /api/v1/sessions/{id} - update session title/description
- [ ] DELETE /api/v1/sessions/{id} - delete session
- [ ] SessionSidebar component with session list and new session button
- [ ] Session selection updates frontend state and WebSocket endpoint

### Implementation Details
**Backend (Person B):**

backend/app/models/session.py (update):
```python
class SessionResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        populate_by_name = True

class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int
```

backend/app/services/session.py:
```python
from motor.motor_asyncio import AsyncDatabase
from app.models.session import SessionDoc, SessionResponse
from bson import ObjectId
from datetime import datetime
from app.core.logger import get_logger

logger = get_logger(__name__)

class SessionService:
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.collection = db.sessions

    async def create(self, user_id: str, title: str, description: str = None) -> SessionDoc:
        session = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_archived": False,
            "message_count": 0,
        }
        result = await self.collection.insert_one(session)
        session["_id"] = result.inserted_id
        logger.info("session_created", session_id=str(result.inserted_id), user_id=user_id)
        return session

    async def get(self, session_id: str, user_id: str) -> Optional[SessionDoc]:
        session = await self.collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": user_id,
        })
        return session

    async def list_user_sessions(self, user_id: str, skip: int = 0, limit: int = 50):
        sessions = await self.collection.find({
            "user_id": user_id,
            "is_archived": False,
        }).sort("updated_at", -1).skip(skip).limit(limit).to_list(None)

        total = await self.collection.count_documents({
            "user_id": user_id,
            "is_archived": False,
        })

        return sessions, total

    async def update(self, session_id: str, user_id: str, title: str = None, description: str = None):
        update_data = {"updated_at": datetime.utcnow()}
        if title:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description

        result = await self.collection.update_one(
            {"_id": ObjectId(session_id), "user_id": user_id},
            {"$set": update_data},
        )

        return result.modified_count > 0

    async def delete(self, session_id: str, user_id: str):
        # Soft delete
        result = await self.collection.update_one(
            {"_id": ObjectId(session_id), "user_id": user_id},
            {"$set": {"is_archived": True, "updated_at": datetime.utcnow()}},
        )

        return result.modified_count > 0
```

backend/app/routers/sessions.py:
```python
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncDatabase
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.session import SessionResponse, SessionListResponse
from app.services.session import SessionService
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()

class CreateSessionRequest(BaseModel):
    title: str
    description: Optional[str] = None

class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    service = SessionService(db)
    session = await service.create(current_user["user_id"], request.title, request.description)
    return SessionResponse(**session, id=str(session["_id"]))

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    service = SessionService(db)
    sessions, total = await service.list_user_sessions(current_user["user_id"], skip, limit)

    return SessionListResponse(
        sessions=[SessionResponse(**s, id=str(s["_id"])) for s in sessions],
        total=total,
    )

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    service = SessionService(db)
    session = await service.get(session_id, current_user["user_id"])

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionResponse(**session, id=str(session["_id"]))

@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    service = SessionService(db)
    updated = await service.update(session_id, current_user["user_id"], request.title, request.description)

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session = await service.get(session_id, current_user["user_id"])
    return SessionResponse(**session, id=str(session["_id"]))

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    service = SessionService(db)
    deleted = await service.delete(session_id, current_user["user_id"])

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
```

**Frontend (Person A):**

frontend/src/stores/sessionStore.ts:
```typescript
import { create } from 'zustand'

export interface Session {
  id: string
  title: string
  description?: string
  created_at: Date
  updated_at: Date
  message_count: number
}

interface SessionStore {
  sessions: Session[]
  currentSessionId: string | null
  loading: boolean

  setSessions: (sessions: Session[]) => void
  setCurrentSessionId: (id: string) => void
  addSession: (session: Session) => void
  removeSession: (id: string) => void
  updateSession: (id: string, updates: Partial<Session>) => void
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessions: [],
  currentSessionId: null,
  loading: false,

  setSessions: (sessions) => set({ sessions }),
  setCurrentSessionId: (id) => set({ currentSessionId: id }),
  addSession: (session) =>
    set((state) => ({ sessions: [session, ...state.sessions] })),
  removeSession: (id) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== id),
    })),
  updateSession: (id, updates) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === id ? { ...s, ...updates } : s
      ),
    })),
}))
```

frontend/src/components/SessionSidebar.tsx:
```typescript
import React, { useEffect } from 'react'
import { useSessionStore } from '../stores/sessionStore'
import { useChatStore } from '../stores/chatStore'
import { formatDistanceToNow } from 'date-fns'

export function SessionSidebar() {
  const { sessions, currentSessionId, setSessions, setCurrentSessionId } = useSessionStore()
  const { setSessionId, clearMessages } = useChatStore()

  useEffect(() => {
    // Fetch sessions on mount
    fetchSessions()
  }, [])

  async function fetchSessions() {
    try {
      const response = await fetch('/api/v1/sessions', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      })
      const data = await response.json()
      setSessions(data.sessions.map((s: any) => ({
        ...s,
        created_at: new Date(s.created_at),
        updated_at: new Date(s.updated_at),
      })))
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
    }
  }

  async function createNewSession() {
    try {
      const response = await fetch('/api/v1/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          title: `Chat ${new Date().toLocaleDateString()}`,
          description: '',
        }),
      })
      const session = await response.json()

      useSessionStore.setState((state) => ({
        sessions: [session, ...state.sessions],
        currentSessionId: session.id,
      }))

      setSessionId(session.id)
      clearMessages()
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  function selectSession(sessionId: string) {
    setCurrentSessionId(sessionId)
    setSessionId(sessionId)
    clearMessages()
  }

  async function deleteSession(sessionId: string) {
    try {
      await fetch(`/api/v1/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      })

      useSessionStore.setState((state) => ({
        sessions: state.sessions.filter((s) => s.id !== sessionId),
      }))

      if (currentSessionId === sessionId) {
        const nextSession = sessions[0]
        if (nextSession) {
          selectSession(nextSession.id)
        } else {
          createNewSession()
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      <button
        onClick={createNewSession}
        className="m-4 p-2 bg-blue-600 rounded hover:bg-blue-700 transition"
      >
        + New Chat
      </button>

      <div className="flex-1 overflow-y-auto">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`p-3 cursor-pointer border-l-2 transition ${
              currentSessionId === session.id
                ? 'border-blue-500 bg-gray-800'
                : 'border-gray-700 hover:bg-gray-800'
            }`}
            onClick={() => selectSession(session.id)}
          >
            <div className="font-medium truncate">{session.title}</div>
            <div className="text-xs text-gray-400">
              {formatDistanceToNow(new Date(session.updated_at), { addSuffix: true })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Files to Create/Modify
- `backend/app/services/session.py`
- `backend/app/routers/sessions.py`
- `frontend/src/stores/sessionStore.ts`
- `frontend/src/components/SessionSidebar.tsx`

---

## MILESTONE M2: Core Agents & Backend

---


ISSUE_12_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Session Sidebar & Session CRUD API" \
  --body "$ISSUE_BODY_12" \
  --label "frontend" --label "backend" --label "integration" --label "priority:high" \
  --milestone "M1")

echo "Created: Session Sidebar & Session CRUD API -> $ISSUE_URL"
sleep 1

# Issue #13: Router/Planner Agent Implementation
ISSUE_BODY_13=$(cat <<'ISSUE_13_EOF'
### Description
Implement router/planner agent that analyzes user queries, determines which domain agents to invoke, creates execution plan, and delegates to sub-agents. Uses LLM reasoning with structured output.

### Acceptance Criteria
- [ ] Router node integrated into LangGraph orchestrator
- [ ] Parses user_query and business_context to determine relevant domains
- [ ] Outputs planned_agents list (subset of 6 domain agents)
- [ ] Creates reasoning trace for observability
- [ ] Handles ambiguous queries with clarification requests
- [ ] Uses OpenAI function calling for structured output
- [ ] Timeout: max 10 seconds

### Implementation Details
agents/orchestrator/router_agent.py:
```python
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger
import json

logger = get_logger(__name__)

DOMAIN_AGENTS = [
    "market_trend_agent",
    "competitive_landscape_agent",
    "win_loss_agent",
    "pricing_packaging_agent",
    "positioning_messaging_agent",
    "adjacent_market_agent",
]

class RouterPlan(BaseModel):
    """Structured output from router"""
    selected_agents: List[str] = Field(
        description="List of domain agents to invoke"
    )
    reasoning: str = Field(
        description="Why these agents were selected"
    )
    priority_order: List[str] = Field(
        description="Order to execute agents"
    )
    needs_clarification: bool = Field(
        description="Does user need clarification"
    )
    clarification_prompt: str = Field(
        default="",
        description="Question to ask user if clarification needed"
    )

async def router_node(state: OrchestrationState) -> dict:
    """Route query to appropriate domain agents"""

    llm = ChatOpenAI(model="gpt-4", temperature=0)

    system_prompt = f"""You are a query router for a market intelligence system.
Analyze the user query and business context to determine which domain agents to invoke.

Available agents:
- market_trend_agent: Market trends, growth signals, emerging opportunities
- competitive_landscape_agent: Competitor analysis, market share, positioning
- win_loss_agent: Win/loss reasons, customer preferences, decision criteria
- pricing_packaging_agent: Pricing strategy, packaging, monetization models
- positioning_messaging_agent: Messaging, value proposition, positioning
- adjacent_market_agent: Adjacent/neighboring markets, expansion opportunities

User query: {state['user_query']}
Business context: {state.get('business_context', 'None provided')}

Select the most relevant agents (1-6). If query is ambiguous, set needs_clarification=true."""

    try:
        response = llm.invoke([{
            "role": "user",
            "content": system_prompt
        }])

        # Parse structured output
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            plan_data = json.loads(json_match.group())
            plan = RouterPlan(**plan_data)
        else:
            # Fallback: select all agents
            plan = RouterPlan(
                selected_agents=DOMAIN_AGENTS,
                reasoning="Query complexity suggests all domains needed",
                priority_order=DOMAIN_AGENTS,
                needs_clarification=False,
            )

        state["planned_agents"] = plan.selected_agents
        state["trace_data"]["router_plan"] = {
            "selected_agents": plan.selected_agents,
            "reasoning": plan.reasoning,
            "needs_clarification": plan.needs_clarification,
        }

        logger.info(
            "router_plan_created",
            session_id=state["session_id"],
            agents=plan.selected_agents,
        )

        return state

    except Exception as e:
        logger.error("router_node_failed", error=str(e))
        state["planned_agents"] = DOMAIN_AGENTS
        return state
```

In graph.py:
```python
from agents.orchestrator.router_agent import router_node as new_router_node

# Replace placeholder in add_node
graph.add_node("router", new_router_node)
```

### Files to Create/Modify
- `agents/orchestrator/router_agent.py`
- `agents/orchestrator/graph.py`

---


ISSUE_13_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Router/Planner Agent Implementation" \
  --body "$ISSUE_BODY_13" \
  --label "agents" --label "priority:critical" \
  --milestone "M2")

echo "Created: Router/Planner Agent Implementation -> $ISSUE_URL"
sleep 1

# Issue #14: Firecrawl Tool Implementation
ISSUE_BODY_14=$(cat <<'ISSUE_14_EOF'
### Description
Implement Firecrawl wrapper for web scraping and search. Handles URL fetching, markdown extraction, and error recovery with exponential backoff.

### Acceptance Criteria
- [ ] Firecrawl API client with async support
- [ ] scrape_url(url) returns markdown content
- [ ] search(query) returns top 10 results with snippets
- [ ] Rate limiting: max 5 concurrent requests
- [ ] Retry logic with exponential backoff
- [ ] Timeout: 30 seconds per request
- [ ] Cache results in Qdrant

### Implementation Details
agents/tools/firecrawl_tool.py:
```python
import aiohttp
from agents.tools.base import BaseDataSourceTool, ToolResult, ErrorType
from app.core.config import settings
from agents.utils.logger import get_logger
from typing import Any, Dict
import json

logger = get_logger(__name__)

class FirecrawlTool(BaseDataSourceTool):
    def __init__(self):
        super().__init__(
            name="firecrawl",
            max_retries=3,
            timeout_seconds=30,
            rate_limit=5,
        )
        self.api_key = settings.FIRECRAWL_API_KEY
        self.base_url = "https://api.firecrawl.dev/v1"

    async def _fetch(self, **kwargs) -> Dict[str, Any]:
        """Firecrawl API call"""

        action = kwargs.get("action", "scrape")
        url = kwargs.get("url")
        query = kwargs.get("query")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if action == "scrape":
            return await self._scrape_url(url, headers)
        elif action == "search":
            return await self._search(query, headers)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _scrape_url(self, url: str, headers: dict) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            payload = {
                "url": url,
                "formats": ["markdown"],
            }

            async with session.post(
                f"{self.base_url}/scrape",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "url": url,
                        "content": data.get("markdown", ""),
                        "source": "firecrawl",
                    }
                elif resp.status == 429:
                    raise Exception("Rate limited by Firecrawl")
                else:
                    raise Exception(f"Firecrawl error: {resp.status}")

    async def _search(self, query: str, headers: dict) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query,
                "limit": 10,
            }

            async with session.post(
                f"{self.base_url}/search",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "query": query,
                        "results": data.get("results", []),
                        "source": "firecrawl",
                    }
                else:
                    raise Exception(f"Firecrawl search error: {resp.status}")

# Global instance
_firecrawl: FirecrawlTool = FirecrawlTool()

async def scrape_url(url: str) -> ToolResult:
    return await _firecrawl.execute(action="scrape", url=url)

async def search_web(query: str) -> ToolResult:
    return await _firecrawl.execute(action="search", query=query)
```

### Files to Create/Modify
- `agents/tools/firecrawl_tool.py`

---


ISSUE_14_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Firecrawl Tool Implementation" \
  --body "$ISSUE_BODY_14" \
  --label "agents" --label "priority:critical" \
  --milestone "M2")

echo "Created: Firecrawl Tool Implementation -> $ISSUE_URL"
sleep 1

# Issue #15: SerpAPI Tool Implementation
ISSUE_BODY_15=$(cat <<'ISSUE_15_EOF'
### Description
Implement SerpAPI wrapper for Google Trends, News, Ads Transparency. Supports multiple search types with structured parsing.

### Acceptance Criteria
- [ ] SerpAPI client with async support
- [ ] google_search(query) returns organic results
- [ ] google_trends(query) returns trend data
- [ ] google_news(query) returns recent news
- [ ] Rate limiting: 100 calls/month (SerpAPI limit)
- [ ] Retry on quota exceeded
- [ ] Parse and normalize results

### Implementation Details
agents/tools/serpapi_tool.py:
```python
import aiohttp
from agents.tools.base import BaseDataSourceTool, ToolResult
from app.core.config import settings
from agents.utils.logger import get_logger
from typing import Any, Dict
import json

logger = get_logger(__name__)

class SerpAPITool(BaseDataSourceTool):
    def __init__(self):
        super().__init__(
            name="serpapi",
            max_retries=2,
            timeout_seconds=30,
            rate_limit=3,  # Conservative rate limit
        )
        self.api_key = settings.SERPAPI_API_KEY
        self.base_url = "https://serpapi.com/search"

    async def _fetch(self, **kwargs) -> Dict[str, Any]:
        """SerpAPI call"""

        search_type = kwargs.get("type", "google")
        query = kwargs.get("query")

        params = {
            "api_key": self.api_key,
            "q": query,
        }

        if search_type == "google":
            params["engine"] = "google"
            params["num"] = 10
        elif search_type == "trends":
            params["engine"] = "google_trends"
            params["data_type"] = "TIMESERIES"
        elif search_type == "news":
            params["engine"] = "google_news"
            params["num"] = 10
        else:
            raise ValueError(f"Unknown search type: {search_type}")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.base_url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._parse_response(search_type, data)
                elif resp.status == 429:
                    raise Exception("SerpAPI quota exceeded")
                else:
                    raise Exception(f"SerpAPI error: {resp.status}")

    def _parse_response(self, search_type: str, data: dict) -> Dict[str, Any]:
        if search_type == "google":
            return {
                "query": data.get("search_parameters", {}).get("q"),
                "results": [
                    {
                        "title": r.get("title"),
                        "link": r.get("link"),
                        "snippet": r.get("snippet"),
                    }
                    for r in data.get("organic_results", [])[:10]
                ],
                "source": "serpapi",
            }
        elif search_type == "trends":
            return {
                "query": data.get("search_parameters", {}).get("q"),
                "interest_over_time": data.get("interest_over_time", []),
                "related_queries": data.get("related_queries", []),
                "source": "serpapi_trends",
            }
        elif search_type == "news":
            return {
                "query": data.get("search_parameters", {}).get("q"),
                "news": [
                    {
                        "title": n.get("title"),
                        "source": n.get("source"),
                        "date": n.get("date"),
                        "link": n.get("link"),
                    }
                    for n in data.get("news_results", [])[:10]
                ],
                "source": "serpapi_news",
            }

# Global instance
_serpapi = SerpAPITool()

async def google_search(query: str) -> ToolResult:
    return await _serpapi.execute(type="google", query=query)

async def google_trends(query: str) -> ToolResult:
    return await _serpapi.execute(type="trends", query=query)

async def google_news(query: str) -> ToolResult:
    return await _serpapi.execute(type="news", query=query)
```

### Files to Create/Modify
- `agents/tools/serpapi_tool.py`

---


ISSUE_15_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "SerpAPI Tool Implementation" \
  --body "$ISSUE_BODY_15" \
  --label "agents" --label "priority:critical" \
  --milestone "M2")

echo "Created: SerpAPI Tool Implementation -> $ISSUE_URL"
sleep 1

# Issue #16: Reddit + HN Algolia Tool Implementation
ISSUE_BODY_16=$(cat <<'ISSUE_16_EOF'
### Description
Implement Reddit API and HN Algolia search wrappers for community insights, discussion sentiment, and news aggregation.

### Acceptance Criteria
- [ ] Reddit PRAW client for subreddit searches
- [ ] HN Algolia search integration
- [ ] Parse posts, comments, sentiment
- [ ] Filter by date, score, engagement
- [ ] Rate limiting per API
- [ ] Timeout: 20 seconds per request

### Implementation Details
agents/tools/community_tool.py:
```python
import aiohttp
import praw
from agents.tools.base import BaseDataSourceTool, ToolResult
from app.core.config import settings
from agents.utils.logger import get_logger
from typing import Any, Dict, List
from datetime import datetime, timedelta
import json

logger = get_logger(__name__)

class CommunityTool(BaseDataSourceTool):
    def __init__(self):
        super().__init__(
            name="community",
            max_retries=2,
            timeout_seconds=20,
            rate_limit=5,
        )
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent="vector-agents/1.0",
        )

    async def _fetch(self, **kwargs) -> Dict[str, Any]:
        source = kwargs.get("source", "reddit")
        query = kwargs.get("query")
        limit = kwargs.get("limit", 25)

        if source == "reddit":
            return await self._search_reddit(query, limit)
        elif source == "hackernews":
            return await self._search_hackernews(query, limit)
        else:
            raise ValueError(f"Unknown source: {source}")

    async def _search_reddit(self, query: str, limit: int) -> Dict[str, Any]:
        try:
            subreddits = ["startup", "business", "entrepreneur", "technology"]
            posts = []

            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                for post in subreddit.search(query, time_filter="month", limit=5):
                    posts.append({
                        "title": post.title,
                        "subreddit": subreddit_name,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "url": post.url,
                        "created": datetime.fromtimestamp(post.created_utc).isoformat(),
                    })

            return {
                "query": query,
                "posts": posts[:limit],
                "source": "reddit",
            }
        except Exception as e:
            logger.error("reddit_search_failed", error=str(e))
            raise

    async def _search_hackernews(self, query: str, limit: int) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            params = {
                "query": query,
                "numericFilters": f"created_at_i>{int((datetime.now() - timedelta(days=30)).timestamp())}",
                "hitsPerPage": limit,
            }

            async with session.get(
                "https://hn.algolia.com/api/v1/search",
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "query": query,
                        "stories": [
                            {
                                "title": h.get("title"),
                                "url": h.get("url"),
                                "points": h.get("points"),
                                "num_comments": h.get("num_comments"),
                                "created_at": h.get("created_at"),
                            }
                            for h in data.get("hits", [])
                        ],
                        "source": "hackernews",
                    }
                else:
                    raise Exception(f"HN Algolia error: {resp.status}")

# Global instance
_community = CommunityTool()

async def search_reddit(query: str, limit: int = 25) -> ToolResult:
    return await _community.execute(source="reddit", query=query, limit=limit)

async def search_hackernews(query: str, limit: int = 25) -> ToolResult:
    return await _community.execute(source="hackernews", query=query, limit=limit)
```

### Files to Create/Modify
- `agents/tools/community_tool.py`

---


ISSUE_16_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Reddit + HN Algolia Tool Implementation" \
  --body "$ISSUE_BODY_16" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: Reddit + HN Algolia Tool Implementation -> $ISSUE_URL"
sleep 1

# Issue #17: Meta Ad Library + LinkedIn Tool
ISSUE_BODY_17=$(cat <<'ISSUE_17_EOF'
### Description
Implement Meta Ad Library API and LinkedIn scraper for competitive advertising intelligence and messaging insights.

### Acceptance Criteria
- [ ] Meta Ad Library client (ads.facebook.com API)
- [ ] LinkedIn company page scraper (via Playwright)
- [ ] Extract ad copy, targeting, creatives
- [ ] Parse company info, job postings, employees
- [ ] Rate limiting and caching
- [ ] Error handling for blocked requests

### Implementation Details
agents/tools/advertising_tool.py:
```python
import aiohttp
import asyncio
from agents.tools.base import BaseDataSourceTool, ToolResult
from app.core.logger import get_logger
from typing import Any, Dict
import json

logger = get_logger(__name__)

class AdvertisingTool(BaseDataSourceTool):
    def __init__(self):
        super().__init__(
            name="advertising",
            max_retries=2,
            timeout_seconds=30,
            rate_limit=3,
        )

    async def _fetch(self, **kwargs) -> Dict[str, Any]:
        source = kwargs.get("source", "meta")
        query = kwargs.get("query")

        if source == "meta":
            return await self._search_meta_ads(query)
        elif source == "linkedin":
            return await self._search_linkedin(query)
        else:
            raise ValueError(f"Unknown advertising source: {source}")

    async def _search_meta_ads(self, company_name: str) -> Dict[str, Any]:
        """Meta Ad Library API search"""
        async with aiohttp.ClientSession() as session:
            # Meta Ad Library API endpoint
            params = {
                "search_term": company_name,
                "ad_type": "POLITICAL_AND_ISSUE_ADS",
                "country": "US",
            }

            try:
                async with session.get(
                    "https://ads.facebook.com/ads/library/api",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "company": company_name,
                            "ads": self._parse_meta_ads(data),
                            "source": "meta_ad_library",
                        }
                    else:
                        raise Exception(f"Meta API error: {resp.status}")
            except Exception as e:
                logger.warning("meta_ads_fetch_failed", error=str(e))
                raise

    def _parse_meta_ads(self, data: dict) -> list:
        ads = []
        for ad in data.get("ads", [])[:20]:
            ads.append({
                "title": ad.get("ad_creative_bodies", [{}])[0].get("body", ""),
                "url": ad.get("ad_snapshot_url"),
                "created_date": ad.get("ad_creation_date"),
                "impressions": ad.get("impressions"),
                "spend": ad.get("spend"),
            })
        return ads

    async def _search_linkedin(self, company_name: str) -> Dict[str, Any]:
        """LinkedIn company page scraper (placeholder)"""
        # Note: Full LinkedIn scraping requires Playwright
        # This is a stub for the tool interface
        return {
            "company": company_name,
            "employees": [],
            "job_postings": [],
            "source": "linkedin",
            "note": "Use Issue #18 Playwright tool for full scraping",
        }

# Global instance
_advertising = AdvertisingTool()

async def search_meta_ads(company_name: str) -> ToolResult:
    return await _advertising.execute(source="meta", query=company_name)

async def search_linkedin(company_name: str) -> ToolResult:
    return await _advertising.execute(source="linkedin", query=company_name)
```

### Files to Create/Modify
- `agents/tools/advertising_tool.py`

---


ISSUE_17_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Meta Ad Library + LinkedIn Tool" \
  --body "$ISSUE_BODY_17" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: Meta Ad Library + LinkedIn Tool -> $ISSUE_URL"
sleep 1

# Issue #18: USPTO Patents + Playwright Fallback Tool
ISSUE_BODY_18=$(cat <<'ISSUE_18_EOF'
### Description
Implement USPTO patent search and Playwright-based scraper for sites without APIs. Handles dynamic content, JavaScript rendering, fallback when Firecrawl unavailable.

### Acceptance Criteria
- [ ] USPTO.gov patent search and parsing
- [ ] Playwright browser automation for JavaScript sites
- [ ] Extract patents, trademarks, filings
- [ ] Timeout: 45 seconds per request
- [ ] Fallback when Firecrawl rate-limited
- [ ] Cache Playwright sessions

### Implementation Details
agents/tools/patent_tool.py:
```python
import aiohttp
from agents.tools.base import BaseDataSourceTool, ToolResult
from app.core.logger import get_logger
from typing import Any, Dict
import json

logger = get_logger(__name__)

class PatentTool(BaseDataSourceTool):
    def __init__(self):
        super().__init__(
            name="patent",
            max_retries=2,
            timeout_seconds=45,
            rate_limit=2,
        )

    async def _fetch(self, **kwargs) -> Dict[str, Any]:
        search_type = kwargs.get("type", "patent")
        query = kwargs.get("query")

        if search_type == "patent":
            return await self._search_patents(query)
        elif search_type == "trademark":
            return await self._search_trademarks(query)
        else:
            raise ValueError(f"Unknown patent search type: {search_type}")

    async def _search_patents(self, query: str) -> Dict[str, Any]:
        """Search USPTO patents"""
        async with aiohttp.ClientSession() as session:
            params = {
                "q": query,
                "f": "S",  # Simple search
                "p": 1,
            }

            async with session.get(
                "https://www.uspto.gov/cgi-bin/patft/srchnum.html",
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    return {
                        "query": query,
                        "patents": self._parse_patent_results(html),
                        "source": "uspto_patents",
                    }
                else:
                    raise Exception(f"USPTO error: {resp.status}")

    def _parse_patent_results(self, html: str) -> list:
        """Parse patent results from HTML"""
        import re
        patents = []

        # Simple regex parsing (in prod, use BeautifulSoup)
        patent_blocks = re.findall(r'<a href="([^"]*)"[^>]*>(\d{7,})</a>', html)

        for link, patent_id in patent_blocks[:10]:
            patents.append({
                "id": patent_id,
                "link": f"https://www.uspto.gov{link}",
                "source": "uspto",
            })

        return patents

    async def _search_trademarks(self, query: str) -> Dict[str, Any]:
        """Search USPTO trademarks"""
        async with aiohttp.ClientSession() as session:
            # TESS (Trademark Electronic Search System)
            async with session.get(
                f"https://www.uspto.gov/trademarks-application-process/search-trademark-database",
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    return {
                        "query": query,
                        "trademarks": [],
                        "source": "uspto_trademarks",
                        "note": "Trademark search requires interactive form submission",
                    }
                else:
                    raise Exception(f"TESS error: {resp.status}")

# Global instance
_patent = PatentTool()

async def search_patents(query: str) -> ToolResult:
    return await _patent.execute(type="patent", query=query)

async def search_trademarks(query: str) -> ToolResult:
    return await _patent.execute(type="trademark", query=query)
```

### Files to Create/Modify
- `agents/tools/patent_tool.py`

---


ISSUE_18_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "USPTO Patents + Playwright Fallback Tool" \
  --body "$ISSUE_BODY_18" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: USPTO Patents + Playwright Fallback Tool -> $ISSUE_URL"
sleep 1

# Issue #19: Market Trend Domain Agent
ISSUE_BODY_19=$(cat <<'ISSUE_19_EOF'
### Description
Implement domain agent for market trends: growth signals, emerging markets, revenue indicators, TAM expansion. Uses tools: Firecrawl, SerpAPI Trends, company filings.

### Acceptance Criteria
- [ ] Agent node in LangGraph
- [ ] Calls Firecrawl + SerpAPI for web + trends data
- [ ] Analyzes growth indicators from sources
- [ ] Returns structured trend findings
- [ ] Timeout: 60 seconds
- [ ] Confidence scoring for findings

### Implementation Details
agents/domain_agents/market_trend.py:
```python
from langchain_openai import ChatOpenAI
from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import search_web, scrape_url
from agents.tools.serpapi_tool import google_trends, google_news
from agents.utils.logger import get_logger
import json

logger = get_logger(__name__)

async def market_trend_agent(state: OrchestrationState) -> dict:
    """Analyze market trends and growth signals"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    # Gather data
    trend_results = await google_trends(state["user_query"])
    news_results = await google_news(state["user_query"])
    web_results = await search_web(f"{state['user_query']} market growth trends")

    sources = [
        trend_results.data if trend_results.success else {},
        news_results.data if news_results.success else {},
        web_results.data if web_results.success else {},
    ]

    analysis_prompt = f"""
    Analyze market trends based on these sources:

    Trends: {json.dumps(sources[0], default=str)}
    News: {json.dumps(sources[1], default=str)}
    Web: {json.dumps(sources[2], default=str)}

    Business context: {state.get('business_context', 'None')}

    Provide:
    1. Key growth indicators
    2. Market size and TAM
    3. Emerging opportunities
    4. Risk factors
    5. Confidence level (0-100)
    """

    try:
        response = await llm.ainvoke([{"role": "user", "content": analysis_prompt}])

        agent_output = {
            "agent_name": "market_trend_agent",
            "status": "completed",
            "result": {
                "analysis": response.content,
                "sources": [
                    s.get("source", "unknown") for s in sources if s
                ],
            },
            "error": None,
        }

        state["agent_outputs"]["market_trend_agent"] = agent_output
        logger.info("market_trend_agent_completed", session_id=state["session_id"])

    except Exception as e:
        logger.error("market_trend_agent_failed", error=str(e))
        state["agent_outputs"]["market_trend_agent"] = {
            "agent_name": "market_trend_agent",
            "status": "failed",
            "result": None,
            "error": str(e),
        }

    return state
```

In graph.py:
```python
from agents.domain_agents.market_trend import market_trend_agent

graph.add_node("market_trend_agent", market_trend_agent)
```

### Files to Create/Modify
- `agents/domain_agents/market_trend.py`

---


ISSUE_19_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Market Trend Domain Agent" \
  --body "$ISSUE_BODY_19" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: Market Trend Domain Agent -> $ISSUE_URL"
sleep 1

# Issue #20: Competitive Landscape Domain Agent
ISSUE_BODY_20=$(cat <<'ISSUE_20_EOF'
### Description
Implement domain agent for competitive analysis: competitor identification, market positioning, feature comparison, win/loss analysis. Uses tools: web search, patents, ads, company data.

### Acceptance Criteria
- [ ] Agent node in LangGraph
- [ ] Competitor discovery and tracking
- [ ] Feature/capability comparison matrix
- [ ] Pricing and positioning analysis
- [ ] Market share estimation
- [ ] Structured output with confidence scores

### Implementation Details
agents/domain_agents/competitive_landscape.py:
```python
from langchain_openai import ChatOpenAI
from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import search_web, scrape_url
from agents.tools.patent_tool import search_patents
from agents.tools.advertising_tool import search_meta_ads
from agents.utils.logger import get_logger
import json

logger = get_logger(__name__)

async def competitive_landscape_agent(state: OrchestrationState) -> dict:
    """Analyze competitive landscape and positioning"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    # Gather competitor data
    competitor_search = await search_web(f"{state['user_query']} competitors alternatives")
    patent_search = await search_patents(state["user_query"])

    sources = [
        competitor_search.data if competitor_search.success else {},
        patent_search.data if patent_search.success else {},
    ]

    analysis_prompt = f"""
    Based on competitor research, provide:

    Search results: {json.dumps(sources[0], default=str)}
    Patent filings: {json.dumps(sources[1], default=str)}
    Business context: {state.get('business_context', 'None')}

    Analyze:
    1. Top 5 competitors
    2. Market positioning map
    3. Feature differentiation
    4. Pricing strategies
    5. Strategic threats
    6. Opportunities vs competitors
    """

    try:
        response = await llm.ainvoke([{"role": "user", "content": analysis_prompt}])

        agent_output = {
            "agent_name": "competitive_landscape_agent",
            "status": "completed",
            "result": {
                "analysis": response.content,
                "competitor_count": len(sources[0].get("results", [])),
            },
            "error": None,
        }

        state["agent_outputs"]["competitive_landscape_agent"] = agent_output
        logger.info("competitive_landscape_agent_completed", session_id=state["session_id"])

    except Exception as e:
        logger.error("competitive_landscape_agent_failed", error=str(e))
        state["agent_outputs"]["competitive_landscape_agent"] = {
            "agent_name": "competitive_landscape_agent",
            "status": "failed",
            "result": None,
            "error": str(e),
        }

    return state
```

In graph.py:
```python
from agents.domain_agents.competitive_landscape import competitive_landscape_agent

graph.add_node("competitive_landscape_agent", competitive_landscape_agent)
```

### Files to Create/Modify
- `agents/domain_agents/competitive_landscape.py`

---


ISSUE_20_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Competitive Landscape Domain Agent" \
  --body "$ISSUE_BODY_20" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: Competitive Landscape Domain Agent -> $ISSUE_URL"
sleep 1

# Issue #21: Win/Loss Intelligence Domain Agent
ISSUE_BODY_21=$(cat <<'ISSUE_21_EOF'
### Description
Implement domain agent for win/loss analysis: customer preferences, decision criteria, objection handling. Uses tools: community insights (Reddit, HN), news, case studies.

### Acceptance Criteria
- [ ] Agent node in LangGraph
- [ ] Community sentiment analysis
- [ ] Win/loss reason extraction
- [ ] Customer preference mapping
- [ ] Objection and friction point identification
- [ ] Competitive win rate estimation

### Implementation Details
agents/domain_agents/win_loss.py:
```python
from langchain_openai import ChatOpenAI
from agents.orchestrator.state import OrchestrationState
from agents.tools.community_tool import search_reddit, search_hackernews
from agents.tools.firecrawl_tool import search_web
from agents.utils.logger import get_logger
import json

logger = get_logger(__name__)

async def win_loss_agent(state: OrchestrationState) -> dict:
    """Analyze win/loss reasons and customer preferences"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    # Gather community insights
    reddit_insights = await search_reddit(state["user_query"])
    hn_insights = await search_hackernews(f"{state['user_query']} discussion")
    case_studies = await search_web(f"{state['user_query']} case study ROI implementation")

    sources = [
        reddit_insights.data if reddit_insights.success else {},
        hn_insights.data if hn_insights.success else {},
        case_studies.data if case_studies.success else {},
    ]

    analysis_prompt = f"""
    Based on community discussion and case studies, provide:

    Reddit discussions: {json.dumps(sources[0], default=str)}
    HN discussions: {json.dumps(sources[1], default=str)}
    Case studies: {json.dumps(sources[2], default=str)}

    Identify:
    1. Common objections and friction points
    2. Win reasons (why customers choose)
    3. Loss reasons (why they don't choose)
    4. Customer maturity/readiness factors
    5. Decision criteria and evaluation priorities
    6. Implementation challenges
    """

    try:
        response = await llm.ainvoke([{"role": "user", "content": analysis_prompt}])

        agent_output = {
            "agent_name": "win_loss_agent",
            "status": "completed",
            "result": {
                "analysis": response.content,
                "sentiment_sources": [s.get("source") for s in sources if s],
            },
            "error": None,
        }

        state["agent_outputs"]["win_loss_agent"] = agent_output
        logger.info("win_loss_agent_completed", session_id=state["session_id"])

    except Exception as e:
        logger.error("win_loss_agent_failed", error=str(e))
        state["agent_outputs"]["win_loss_agent"] = {
            "agent_name": "win_loss_agent",
            "status": "failed",
            "result": None,
            "error": str(e),
        }

    return state
```

### Files to Create/Modify
- `agents/domain_agents/win_loss.py`

---


ISSUE_21_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Win/Loss Intelligence Domain Agent" \
  --body "$ISSUE_BODY_21" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: Win/Loss Intelligence Domain Agent -> $ISSUE_URL"
sleep 1

# Issue #22: Pricing & Packaging Domain Agent
ISSUE_BODY_22=$(cat <<'ISSUE_22_EOF'
### Description
Implement domain agent for pricing strategy: competitor pricing analysis, packaging options, value-based pricing, monetization models.

### Acceptance Criteria
- [ ] Agent node in LangGraph
- [ ] Competitor pricing extraction
- [ ] Pricing model analysis (SaaS, perpetual, freemium, etc.)
- [ ] Value-based pricing estimation
- [ ] Packaging options mapping
- [ ] Revenue optimization recommendations

### Implementation Details
agents/domain_agents/pricing_packaging.py:
```python
from langchain_openai import ChatOpenAI
from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import search_web, scrape_url
from agents.utils.logger import get_logger
import json

logger = get_logger(__name__)

async def pricing_packaging_agent(state: OrchestrationState) -> dict:
    """Analyze pricing strategy and packaging options"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    # Gather pricing information
    competitor_pricing = await search_web(f"{state['user_query']} pricing comparison")
    pricing_models = await search_web(f"{state['user_query']} pricing models alternatives cost")

    sources = [
        competitor_pricing.data if competitor_pricing.success else {},
        pricing_models.data if pricing_models.success else {},
    ]

    analysis_prompt = f"""
    Based on competitor and market research:

    Competitor pricing: {json.dumps(sources[0], default=str)}
    Pricing models: {json.dumps(sources[1], default=str)}

    Business context: {state.get('business_context', 'None')}

    Provide:
    1. Competitive pricing matrix
    2. Pricing model best practices
    3. Recommended packaging tiers
    4. Value-based pricing recommendations
    5. Monetization optimization opportunities
    6. Price elasticity insights
    """

    try:
        response = await llm.ainvoke([{"role": "user", "content": analysis_prompt}])

        agent_output = {
            "agent_name": "pricing_packaging_agent",
            "status": "completed",
            "result": {
                "analysis": response.content,
                "data_sources": len([s for s in sources if s]),
            },
            "error": None,
        }

        state["agent_outputs"]["pricing_packaging_agent"] = agent_output
        logger.info("pricing_packaging_agent_completed", session_id=state["session_id"])

    except Exception as e:
        logger.error("pricing_packaging_agent_failed", error=str(e))
        state["agent_outputs"]["pricing_packaging_agent"] = {
            "agent_name": "pricing_packaging_agent",
            "status": "failed",
            "result": None,
            "error": str(e),
        }

    return state
```

### Files to Create/Modify
- `agents/domain_agents/pricing_packaging.py`

---


ISSUE_22_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Pricing & Packaging Domain Agent" \
  --body "$ISSUE_BODY_22" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: Pricing & Packaging Domain Agent -> $ISSUE_URL"
sleep 1

# Issue #23: Positioning & Messaging Domain Agent
ISSUE_BODY_23=$(cat <<'ISSUE_23_EOF'
### Description
Implement domain agent for messaging and positioning: value proposition, messaging pillars, target audience segmentation, brand positioning.

### Acceptance Criteria
- [ ] Agent node in LangGraph
- [ ] Competitor messaging analysis
- [ ] Value proposition mapping
- [ ] Target audience segmentation
- [ ] Messaging pillar identification
- [ ] Brand differentiation analysis

### Implementation Details
agents/domain_agents/positioning_messaging.py:
```python
from langchain_openai import ChatOpenAI
from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import search_web
from agents.tools.advertising_tool import search_meta_ads
from agents.utils.logger import get_logger
import json

logger = get_logger(__name__)

async def positioning_messaging_agent(state: OrchestrationState) -> dict:
    """Analyze positioning and messaging strategy"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    # Gather messaging data
    competitor_messaging = await search_web(f"{state['user_query']} value proposition messaging tagline")
    ad_analysis = await search_meta_ads(state["user_query"].split()[0])  # Use first word as company name

    sources = [
        competitor_messaging.data if competitor_messaging.success else {},
        ad_analysis.data if ad_analysis.success else {},
    ]

    analysis_prompt = f"""
    Based on competitor messaging and advertising analysis:

    Web messaging: {json.dumps(sources[0], default=str)}
    Ad creative: {json.dumps(sources[1], default=str)}

    Business context: {state.get('business_context', 'None')}

    Provide:
    1. Competitor positioning map
    2. Key messaging themes
    3. Value proposition recommendations
    4. Target audience personas
    5. Messaging pillar recommendations
    6. Differentiation opportunities
    """

    try:
        response = await llm.ainvoke([{"role": "user", "content": analysis_prompt}])

        agent_output = {
            "agent_name": "positioning_messaging_agent",
            "status": "completed",
            "result": {
                "analysis": response.content,
                "messaging_sources": [s.get("source") for s in sources if s],
            },
            "error": None,
        }

        state["agent_outputs"]["positioning_messaging_agent"] = agent_output
        logger.info("positioning_messaging_agent_completed", session_id=state["session_id"])

    except Exception as e:
        logger.error("positioning_messaging_agent_failed", error=str(e))
        state["agent_outputs"]["positioning_messaging_agent"] = {
            "agent_name": "positioning_messaging_agent",
            "status": "failed",
            "result": None,
            "error": str(e),
        }

    return state
```

### Files to Create/Modify
- `agents/domain_agents/positioning_messaging.py`

---


ISSUE_23_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Positioning & Messaging Domain Agent" \
  --body "$ISSUE_BODY_23" \
  --label "agents" --label "priority:high" \
  --milestone "M2")

echo "Created: Positioning & Messaging Domain Agent -> $ISSUE_URL"
sleep 1

# Issue #24: Adjacent Market Domain Agent
ISSUE_BODY_24=$(cat <<'ISSUE_24_EOF'
### Description
Implement domain agent for adjacent market opportunities: geographic expansion, vertical expansion, adjacent use cases, partnership opportunities.

### Acceptance Criteria
- [ ] Agent node in LangGraph
- [ ] Adjacent market identification
- [ ] Expansion opportunity scoring
- [ ] Partnership and alliance opportunities
- [ ] Market size estimation for adjacent segments
- [ ] Go-to-market recommendations

### Implementation Details
agents/domain_agents/adjacent_market.py:
```python
from langchain_openai import ChatOpenAI
from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import search_web
from agents.tools.patent_tool import search_patents
from agents.utils.logger import get_logger
import json

logger = get_logger(__name__)

async def adjacent_market_agent(state: OrchestrationState) -> dict:
    """Identify adjacent market opportunities"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    # Research adjacent opportunities
    adjacent_search = await search_web(f"{state['user_query']} adjacent markets expansion vertical use cases")
    patent_landscape = await search_patents(f"{state['user_query']} related technology")

    sources = [
        adjacent_search.data if adjacent_search.success else {},
        patent_landscape.data if patent_landscape.success else {},
    ]

    analysis_prompt = f"""
    Identify adjacent market opportunities:

    Market research: {json.dumps(sources[0], default=str)}
    Patent landscape: {json.dumps(sources[1], default=str)}

    Business context: {state.get('business_context', 'None')}

    Provide:
    1. Adjacent vertical opportunities
    2. Geographic expansion candidates
    3. Use case extensions
    4. Partnership opportunities
    5. Addressable market size for each opportunity
    6. Go-to-market recommendations
    """

    try:
        response = await llm.ainvoke([{"role": "user", "content": analysis_prompt}])

        agent_output = {
            "agent_name": "adjacent_market_agent",
            "status": "completed",
            "result": {
                "analysis": response.content,
                "research_sources": [s.get("source") for s in sources if s],
            },
            "error": None,
        }

        state["agent_outputs"]["adjacent_market_agent"] = agent_output
        logger.info("adjacent_market_agent_completed", session_id=state["session_id"])

    except Exception as e:
        logger.error("adjacent_market_agent_failed", error=str(e))
        state["agent_outputs"]["adjacent_market_agent"] = {
            "agent_name": "adjacent_market_agent",
            "status": "failed",
            "result": None,
            "error": str(e),
        }

    return state
```

### Files to Create/Modify
- `agents/domain_agents/adjacent_market.py`

---


ISSUE_24_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Adjacent Market Domain Agent" \
  --body "$ISSUE_BODY_24" \
  --label "agents" --label "priority:medium" \
  --milestone "M2")

echo "Created: Adjacent Market Domain Agent -> $ISSUE_URL"
sleep 1

# Issue #25: Synthesis Agent Implementation
ISSUE_BODY_25=$(cat <<'ISSUE_25_EOF'
### Description
Implement synthesis agent: aggregates all domain agent outputs, cross-references findings, generates artifacts (scorecards, charts), confidence scoring, source attribution.

### Acceptance Criteria
- [ ] Synthesis node in LangGraph
- [ ] Aggregates all agent_outputs into coherent narrative
- [ ] Generates 3-5 artifacts (scorecard, trends, heatmap, etc.)
- [ ] Confidence scoring per recommendation
- [ ] Source trail with citations
- [ ] Final response formatting for frontend

### Implementation Details
agents/orchestrator/synthesis_agent.py:
```python
from langchain_openai import ChatOpenAI
from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger
import json
from typing import List, Dict, Any
import uuid

logger = get_logger(__name__)

async def synthesis_agent(state: OrchestrationState) -> dict:
    """Synthesize domain agent outputs into unified response"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.2)

    # Prepare agent summaries
    agent_summaries = {}
    for agent_name, output in state["agent_outputs"].items():
        if output["status"] == "completed":
            agent_summaries[agent_name] = output.get("result", {})

    synthesis_prompt = f"""
    You are a synthesis expert. Aggregate these analysis results:

    {json.dumps(agent_summaries, default=str, indent=2)}

    Business context: {state.get('business_context', 'None')}

    Provide:
    1. Executive Summary (2-3 sentences)
    2. Top 3 Key Insights with confidence (0-100)
    3. Recommended Actions (3-5 items)
    4. Risk/Opportunity Matrix
    5. Next Steps

    Format output as structured JSON.
    """

    try:
        response = await llm.ainvoke([{"role": "user", "content": synthesis_prompt}])

        # Parse response
        synthesis_result = {
            "summary": "Executive summary from LLM",
            "insights": [],
            "recommendations": [],
            "confidence_scores": {},
        }

        # Generate artifacts
        artifacts = _generate_artifacts(agent_summaries, synthesis_result)

        state["synthesis_result"] = synthesis_result
        state["artifacts"] = artifacts

        logger.info(
            "synthesis_completed",
            session_id=state["session_id"],
            artifact_count=len(artifacts),
        )

    except Exception as e:
        logger.error("synthesis_agent_failed", error=str(e))
        state["synthesis_result"] = {"error": str(e)}

    return state

def _generate_artifacts(
    agent_summaries: Dict[str, Any],
    synthesis_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate visual artifacts from synthesis"""

    artifacts = []

    # 1. Scorecard artifact
    artifacts.append({
        "id": str(uuid.uuid4()),
        "type": "scorecard",
        "title": "Growth Intelligence Score",
        "data": {
            "overall_score": 72,
            "categories": {
                "market_trends": {"score": 75, "status": "strong"},
                "competition": {"score": 70, "status": "moderate"},
                "win_loss": {"score": 68, "status": "moderate"},
                "pricing": {"score": 75, "status": "strong"},
                "positioning": {"score": 70, "status": "moderate"},
                "expansion": {"score": 65, "status": "opportunity"},
            },
        },
    })

    # 2. Trends timeline
    artifacts.append({
        "id": str(uuid.uuid4()),
        "type": "timeline",
        "title": "Market Trends Timeline",
        "data": {
            "events": [
                {"date": "2024-Q1", "event": "Market growth accelerating", "confidence": 85},
                {"date": "2024-Q2", "event": "New competitors entering", "confidence": 75},
            ],
        },
    })

    # 3. Competitive heatmap
    artifacts.append({
        "id": str(uuid.uuid4()),
        "type": "heatmap",
        "title": "Competitive Positioning",
        "data": {
            "dimensions": ["Price", "Features", "Service", "Brand"],
            "competitors": {
                "Competitor A": [8, 7, 9, 6],
                "Competitor B": [6, 8, 7, 7],
                "Your Company": [7, 9, 8, 8],
            },
        },
    })

    return artifacts
```

In graph.py:
```python
from agents.orchestrator.synthesis_agent import synthesis_agent

graph.add_node("synthesis", synthesis_agent)

# Update edges to route all agents to synthesis
graph.add_edge([f"{agent}" for agent in ["market_trend_agent", "competitive_landscape_agent", ...]], "synthesis")
```

### Files to Create/Modify
- `agents/orchestrator/synthesis_agent.py`
- `agents/orchestrator/graph.py`

---


ISSUE_25_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Synthesis Agent Implementation" \
  --body "$ISSUE_BODY_25" \
  --label "agents" --label "priority:critical" \
  --milestone "M2")

echo "Created: Synthesis Agent Implementation -> $ISSUE_URL"
sleep 1

# Issue #26: Document Parser Service - PDF/DOCX/TXT
ISSUE_BODY_26=$(cat <<'ISSUE_26_EOF'
### Description
Implement document parsing service for PDF, DOCX, and TXT files. Extracts text, metadata, structure preservation. Integrates with embedding service.

### Acceptance Criteria
- [ ] PDF parsing with pypdf or pdfplumber
- [ ] DOCX parsing with python-docx
- [ ] TXT file handling
- [ ] Metadata extraction (title, author, date)
- [ ] Chunking strategy (500 tokens per chunk with overlap)
- [ ] Error handling for corrupted files

### Implementation Details
backend/app/services/document_parser.py:
```python
import PyPDF2
from docx import Document as DocxDocument
from typing import Dict, List, Any, Tuple
import re
from app.core.logger import get_logger

logger = get_logger(__name__)

class DocumentParser:
    """Parse documents: PDF, DOCX, TXT"""

    MAX_CHUNK_SIZE = 500  # tokens
    CHUNK_OVERLAP = 100

    @staticmethod
    def parse_file(file_path: str, file_type: str) -> Dict[str, Any]:
        """Parse document by type"""

        if file_type.lower() == "pdf":
            return DocumentParser._parse_pdf(file_path)
        elif file_type.lower() in ["docx", "doc"]:
            return DocumentParser._parse_docx(file_path)
        elif file_type.lower() == "txt":
            return DocumentParser._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """Parse PDF file"""

        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                metadata = reader.metadata

                for page in reader.pages:
                    text += page.extract_text() + "\n"

                chunks = DocumentParser._chunk_text(text)

                return {
                    "content": text,
                    "chunks": chunks,
                    "metadata": {
                        "title": metadata.get("/Title", "") if metadata else "",
                        "author": metadata.get("/Author", "") if metadata else "",
                        "pages": len(reader.pages),
                    },
                    "source": "pdf",
                }

        except Exception as e:
            logger.error("pdf_parse_failed", error=str(e))
            raise

    @staticmethod
    def _parse_docx(file_path: str) -> Dict[str, Any]:
        """Parse DOCX file"""

        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            chunks = DocumentParser._chunk_text(text)

            return {
                "content": text,
                "chunks": chunks,
                "metadata": {
                    "title": doc.core_properties.title or "",
                    "author": doc.core_properties.author or "",
                    "paragraphs": len(doc.paragraphs),
                },
                "source": "docx",
            }

        except Exception as e:
            logger.error("docx_parse_failed", error=str(e))
            raise

    @staticmethod
    def _parse_txt(file_path: str) -> Dict[str, Any]:
        """Parse TXT file"""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = DocumentParser._chunk_text(text)

            return {
                "content": text,
                "chunks": chunks,
                "metadata": {
                    "title": file_path.split("/")[-1],
                    "author": "",
                    "size_bytes": len(text),
                },
                "source": "txt",
            }

        except Exception as e:
            logger.error("txt_parse_failed", error=str(e))
            raise

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into chunks with overlap"""

        # Rough token estimate: 1 token ≈ 4 characters
        char_limit = chunk_size * 4

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < char_limit:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Overlap: keep last 100 chars
                current_chunk = current_chunk[-overlap:] + " " + sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        logger.info("text_chunked", chunk_count=len(chunks), total_chars=len(text))
        return chunks
```

backend/app/routers/documents.py:
```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from motor.motor_asyncio import AsyncDatabase
from app.db.mongo import get_mongo_db
from app.services.document_parser import DocumentParser
from app.middleware.auth import get_current_user
from pathlib import Path
import tempfile

router = APIRouter()

@router.post("/upload-document")
async def upload_document(
    file: UploadFile,
    session_id: str,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Upload and parse document"""

    try:
        # Validate file type
        allowed_types = ["pdf", "docx", "txt"]
        file_ext = file.filename.split(".")[-1].lower()

        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type must be one of: {allowed_types}",
            )

        # Save temp file and parse
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()

            parsed = DocumentParser.parse_file(tmp.name, file_ext)

        # Store in MongoDB
        doc_record = {
            "user_id": current_user["user_id"],
            "session_id": session_id,
            "filename": file.filename,
            "file_type": file_ext,
            "content": parsed["content"],
            "chunks": parsed["chunks"],
            "metadata": parsed["metadata"],
            "created_at": datetime.utcnow(),
        }

        result = await db.business_context.insert_one(doc_record)

        return {
            "document_id": str(result.inserted_id),
            "filename": file.filename,
            "chunks": len(parsed["chunks"]),
        }

    except Exception as e:
        logger.error("document_upload_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

### Files to Create/Modify
- `backend/app/services/document_parser.py`
- `backend/app/routers/documents.py`

---


ISSUE_26_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Document Parser Service - PDF/DOCX/TXT" \
  --body "$ISSUE_BODY_26" \
  --label "backend" --label "priority:high" \
  --milestone "M2")

echo "Created: Document Parser Service - PDF/DOCX/TXT -> $ISSUE_URL"
sleep 1

# Issue #27: URL Ingestion Service - Firecrawl + Playwright Fallback
ISSUE_BODY_27=$(cat <<'ISSUE_27_EOF'
### Description
Implement URL ingestion service: scrapes URLs using Firecrawl (primary) with Playwright fallback. Handles JavaScript-heavy sites, errors, and caching.

### Acceptance Criteria
- [ ] URL validation and deduplication
- [ ] Firecrawl scraping with error handling
- [ ] Playwright fallback for dynamic sites
- [ ] Cache results in MongoDB
- [ ] Chunking strategy matching document parser
- [ ] Timeout: 45 seconds per URL

### Implementation Details
backend/app/services/url_ingestion.py:
```python
from app.core.logger import get_logger
from typing import Dict, Any, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncDatabase
import aiohttp
import hashlib

logger = get_logger(__name__)

class URLIngestionService:
    """Ingest and parse URLs"""

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.cache_ttl = timedelta(days=7)

    async def ingest_url(self, url: str, session_id: str, user_id: str) -> Dict[str, Any]:
        """Ingest URL with caching"""

        url_hash = hashlib.md5(url.encode()).hexdigest()

        # Check cache
        cached = await self.db.url_cache.find_one({"url_hash": url_hash})
        if cached and (datetime.utcnow() - cached["created_at"]) < self.cache_ttl:
            logger.info("url_cache_hit", url=url)
            return {
                "url": url,
                "content": cached["content"],
                "chunks": cached["chunks"],
                "source": "cache",
            }

        # Fetch from Firecrawl or Playwright
        try:
            content = await self._fetch_with_firecrawl(url)
        except Exception as e:
            logger.warning("firecrawl_failed, trying playwright", error=str(e))
            content = await self._fetch_with_playwright(url)

        # Parse and chunk
        from app.services.document_parser import DocumentParser
        chunks = DocumentParser._chunk_text(content)

        # Cache result
        cache_doc = {
            "url": url,
            "url_hash": url_hash,
            "content": content,
            "chunks": chunks,
            "created_at": datetime.utcnow(),
        }
        await self.db.url_cache.insert_one(cache_doc)

        logger.info("url_ingested", url=url, chunks=len(chunks))

        return {
            "url": url,
            "content": content,
            "chunks": chunks,
            "source": "web",
        }

    async def _fetch_with_firecrawl(self, url: str) -> str:
        """Fetch URL using Firecrawl API"""
        # Reuse Firecrawl tool from agents
        from agents.tools.firecrawl_tool import scrape_url
        result = await scrape_url(url)
        if result.success:
            return result.data["content"]
        raise Exception(f"Firecrawl failed: {result.error}")

    async def _fetch_with_playwright(self, url: str) -> str:
        """Fallback: Fetch URL using Playwright"""
        # Requires playwright setup
        # For now, use simple aiohttp fallback
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=45)) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    raise Exception(f"HTTP {resp.status}")
        except Exception as e:
            logger.error("playwright_fallback_failed", error=str(e))
            raise
```

backend/app/routers/ingestion.py:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from motor.motor_asyncio import AsyncDatabase
from app.db.mongo import get_mongo_db
from app.services.url_ingestion import URLIngestionService
from app.middleware.auth import get_current_user

router = APIRouter()

class URLIngestionRequest(BaseModel):
    url: HttpUrl
    session_id: str

@router.post("/ingest-url")
async def ingest_url(
    request: URLIngestionRequest,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Ingest URL and add to session context"""

    service = URLIngestionService(db)

    try:
        result = await service.ingest_url(
            str(request.url),
            request.session_id,
            current_user["user_id"],
        )

        # Store ingestion record
        ingestion_doc = {
            "user_id": current_user["user_id"],
            "session_id": request.session_id,
            "url": str(request.url),
            "chunks": len(result["chunks"]),
            "created_at": datetime.utcnow(),
        }
        await db.url_ingestions.insert_one(ingestion_doc)

        return {
            "url": result["url"],
            "chunks": len(result["chunks"]),
            "source": result["source"],
        }

    except Exception as e:
        logger.error("url_ingestion_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

### Files to Create/Modify
- `backend/app/services/url_ingestion.py`
- `backend/app/routers/ingestion.py`

---


ISSUE_27_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "URL Ingestion Service - Firecrawl + Playwright Fallback" \
  --body "$ISSUE_BODY_27" \
  --label "backend" --label "priority:high" \
  --milestone "M2")

echo "Created: URL Ingestion Service - Firecrawl + Playwright Fallback -> $ISSUE_URL"
sleep 1

# Issue #28: Embedding Service + Qdrant Indexing/Retrieval
ISSUE_BODY_28=$(cat <<'ISSUE_28_EOF'
### Description
Implement embedding service using OpenAI embeddings API. Indexes documents/URLs into Qdrant collections. Provides semantic search and retrieval for agent context.

### Acceptance Criteria
- [ ] OpenAI embedding client (text-embedding-3-small, 1536-dim)
- [ ] Batch embedding of document chunks
- [ ] Qdrant upsert with metadata (session_id, source, created_at)
- [ ] Semantic search: query -> top 5 results by similarity
- [ ] Filtering by session, source, date
- [ ] Caching embeddings in MongoDB

### Implementation Details
backend/app/services/embedding.py:
```python
from openai import AsyncOpenAI
from qdrant_client.models import PointStruct, Distance, VectorParams
from app.db.qdrant import QdrantClient
from app.core.config import settings
from app.core.logger import get_logger
from typing import List, Dict, Any
import hashlib
import json
from datetime import datetime

logger = get_logger(__name__)

class EmbeddingService:
    """Embed and index documents in Qdrant"""

    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def embed_chunks(
        self,
        chunks: List[str],
        session_id: str,
        source: str,
        metadata: Dict[str, Any] = None,
    ) -> List[PointStruct]:
        """Embed text chunks and prepare for Qdrant ingestion"""

        # Call OpenAI embedding API
        response = await self.openai_client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=chunks,
        )

        points = []
        for i, embedding_obj in enumerate(response.data):
            point_id = int(hashlib.md5(
                f"{session_id}:{source}:{i}".encode()
            ).hexdigest(), 16) % (2**31)

            point = PointStruct(
                id=point_id,
                vector=embedding_obj.embedding,
                payload={
                    "session_id": session_id,
                    "source": source,
                    "chunk_index": i,
                    "text": chunks[i][:500],  # Preview
                    "created_at": int(datetime.utcnow().timestamp()),
                    **(metadata or {}),
                },
            )
            points.append(point)

        logger.info(
            "chunks_embedded",
            chunk_count=len(chunks),
            session_id=session_id,
        )

        return points

    async def index_chunks(
        self,
        chunks: List[str],
        session_id: str,
        source: str,
        collection: str = "business_context",
    ):
        """Embed and index chunks into Qdrant"""

        # Embed
        points = await self.embed_chunks(chunks, session_id, source)

        # Upsert to Qdrant
        client = await QdrantClient.get_client()
        await client.upsert(
            collection_name=collection,
            points=points,
        )

        logger.info(
            "chunks_indexed",
            chunk_count=len(points),
            collection=collection,
        )

    async def search(
        self,
        query: str,
        session_id: str,
        limit: int = 5,
        collection: str = "business_context",
    ) -> List[Dict[str, Any]]:
        """Semantic search in Qdrant"""

        # Embed query
        response = await self.openai_client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=[query],
        )
        query_vector = response.data[0].embedding

        # Search Qdrant
        client = await QdrantClient.get_client()
        results = await client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit,
            query_filter={
                "must": [
                    {
                        "key": "session_id",
                        "match": {"value": session_id},
                    }
                ]
            },
        )

        # Format results
        search_results = []
        for result in results:
            search_results.append({
                "text": result.payload.get("text"),
                "source": result.payload.get("source"),
                "score": result.score,
                "metadata": {
                    k: v for k, v in result.payload.items()
                    if k not in ["text", "source"]
                },
            })

        logger.info("semantic_search", query=query, results=len(search_results))

        return search_results
```

backend/app/routers/embedding.py:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncDatabase
from app.db.mongo import get_mongo_db
from app.services.embedding import EmbeddingService
from app.middleware.auth import get_current_user
from typing import List

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    session_id: str
    limit: int = 5

@router.post("/semantic-search")
async def semantic_search(
    request: SearchRequest,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Search business context semantically"""

    service = EmbeddingService()

    try:
        results = await service.search(
            query=request.query,
            session_id=request.session_id,
            limit=request.limit,
        )

        return {
            "query": request.query,
            "results": results,
            "total": len(results),
        }

    except Exception as e:
        logger.error("semantic_search_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

### Files to Create/Modify
- `backend/app/services/embedding.py`
- `backend/app/routers/embedding.py`

---

## MILESTONE M3: Frontend & Integration

---


ISSUE_28_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Embedding Service + Qdrant Indexing/Retrieval" \
  --body "$ISSUE_BODY_28" \
  --label "backend" --label "priority:critical" \
  --milestone "M2")

echo "Created: Embedding Service + Qdrant Indexing/Retrieval -> $ISSUE_URL"
sleep 1

# Issue #29: Chat REST + WebSocket API Routes
ISSUE_BODY_29=$(cat <<'ISSUE_29_EOF'
### Description
Create chat API routes: POST /api/v1/chat/messages for REST queries and /api/v1/ws/chat/{session_id} for streaming responses via WebSocket.

### Acceptance Criteria
- [ ] POST /api/v1/chat/messages (user_id, session_id, query)
- [ ] Returns message_id for tracking
- [ ] Triggers orchestrator invocation (async)
- [ ] Streams agent status, artifacts, final response via WebSocket
- [ ] GET /api/v1/chat/messages/{session_id} returns conversation history
- [ ] Error handling with proper HTTP status codes

### Implementation Details
backend/app/routers/chat.py:
```python
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from motor.motor_asyncio import AsyncDatabase
from pydantic import BaseModel
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.websocket.manager import get_connection_manager
from app.services.orchestrator import OrchestratorService
from app.core.logger import get_logger
from datetime import datetime
from bson import ObjectId
import uuid

logger = get_logger(__name__)
router = APIRouter()

class ChatMessageRequest(BaseModel):
    session_id: str
    query: str
    business_context: Optional[str] = None

class ChatMessageResponse(BaseModel):
    message_id: str
    session_id: str
    role: str = "assistant"
    status: str = "queued"  # queued, processing, complete

@router.post("/messages", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Send chat message and trigger orchestrator"""

    message_id = str(uuid.uuid4())

    # Store user message
    user_msg_doc = {
        "_id": ObjectId(),
        "session_id": request.session_id,
        "user_id": current_user["user_id"],
        "role": "user",
        "content": request.query,
        "timestamp": datetime.utcnow(),
        "message_id": message_id,
    }

    try:
        await db.chat_history.insert_one(user_msg_doc)
    except Exception as e:
        logger.error("user_message_store_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to store message")

    # Trigger orchestrator in background
    background_tasks.add_task(
        _run_orchestrator,
        db,
        message_id,
        request.session_id,
        current_user["user_id"],
        request.query,
        request.business_context,
    )

    return ChatMessageResponse(
        message_id=message_id,
        session_id=request.session_id,
        status="queued",
    )

async def _run_orchestrator(
    db: AsyncDatabase,
    message_id: str,
    session_id: str,
    user_id: str,
    query: str,
    business_context: Optional[str],
):
    """Run orchestrator in background"""

    try:
        service = OrchestratorService(db)
        result = await service.run(
            session_id=session_id,
            user_id=user_id,
            query=query,
            business_context=business_context,
        )

        # Send final response via WebSocket
        manager = get_connection_manager()
        await manager.broadcast(
            session_id,
            {
                "type": "final",
                "session_id": session_id,
                "content": result["synthesis"],
                "artifacts": result.get("artifacts"),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info("orchestrator_completed", message_id=message_id, session_id=session_id)

    except Exception as e:
        logger.error("orchestrator_failed", message_id=message_id, error=str(e))
        manager = get_connection_manager()
        await manager.broadcast(
            session_id,
            {
                "type": "error",
                "session_id": session_id,
                "content": f"Query processing failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

@router.get("/messages/{session_id}")
async def get_messages(
    session_id: str,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Get conversation history"""

    messages = await db.chat_history.find({
        "session_id": session_id,
        "user_id": current_user["user_id"],
    }).sort("timestamp", 1).to_list(None)

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": str(m["_id"]),
                "role": m["role"],
                "content": m["content"],
                "timestamp": m["timestamp"].isoformat(),
                "artifacts": m.get("artifacts"),
            }
            for m in messages
        ],
        "total": len(messages),
    }
```

In main.py:
```python
from app.routers import chat
app.include_router(chat.router, prefix=f"{settings.API_PREFIX}/chat")
```

### Files to Create/Modify
- `backend/app/routers/chat.py`

---


ISSUE_29_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Chat REST + WebSocket API Routes" \
  --body "$ISSUE_BODY_29" \
  --label "backend" --label "integration" --label "priority:critical" \
  --milestone "M3")

echo "Created: Chat REST + WebSocket API Routes -> $ISSUE_URL"
sleep 1

# Issue #30: Business Context Upload API
ISSUE_BODY_30=$(cat <<'ISSUE_30_EOF'
### Description
Create API endpoint for uploading business context: documents (PDF/DOCX), URLs, text snippets. Ingests, embeds, stores in Qdrant.

### Acceptance Criteria
- [ ] POST /api/v1/sessions/{session_id}/context for file upload
- [ ] POST /api/v1/sessions/{session_id}/context/url for URL ingestion
- [ ] POST /api/v1/sessions/{session_id}/context/text for text snippets
- [ ] Validates file type and size limits
- [ ] Triggers document parser and embedding
- [ ] Returns context metadata and embedding stats

### Implementation Details
backend/app/routers/context.py:
```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Form
from pydantic import BaseModel, HttpUrl
from motor.motor_asyncio import AsyncDatabase
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.services.document_parser import DocumentParser
from app.services.url_ingestion import URLIngestionService
from app.services.embedding import EmbeddingService
from app.core.logger import get_logger
from datetime import datetime
import tempfile
import uuid

logger = get_logger(__name__)
router = APIRouter()

class TextContextRequest(BaseModel):
    text: str
    title: Optional[str] = None

class URLContextRequest(BaseModel):
    url: HttpUrl

@router.post("/sessions/{session_id}/context")
async def upload_context(
    session_id: str,
    file: UploadFile,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Upload business context document"""

    file_ext = file.filename.split(".")[-1].lower()

    if file_ext not in ["pdf", "docx", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}",
        )

    try:
        # Parse document
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()

            parsed = DocumentParser.parse_file(tmp.name, file_ext)

        # Embed and index
        embedding_service = EmbeddingService()
        await embedding_service.index_chunks(
            chunks=parsed["chunks"],
            session_id=session_id,
            source=f"document:{file.filename}",
            collection="business_context",
        )

        # Store metadata
        context_doc = {
            "session_id": session_id,
            "user_id": current_user["user_id"],
            "context_id": str(uuid.uuid4()),
            "type": "document",
            "source": file.filename,
            "file_type": file_ext,
            "chunk_count": len(parsed["chunks"]),
            "metadata": parsed["metadata"],
            "created_at": datetime.utcnow(),
        }

        await db.business_context.insert_one(context_doc)

        logger.info(
            "context_uploaded",
            session_id=session_id,
            filename=file.filename,
            chunks=len(parsed["chunks"]),
        )

        return {
            "context_id": context_doc["context_id"],
            "source": file.filename,
            "chunks": len(parsed["chunks"]),
            "indexed": True,
        }

    except Exception as e:
        logger.error("context_upload_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/context/url")
async def ingest_url(
    session_id: str,
    request: URLContextRequest,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Ingest URL as business context"""

    try:
        url_service = URLIngestionService(db)
        result = await url_service.ingest_url(
            url=str(request.url),
            session_id=session_id,
            user_id=current_user["user_id"],
        )

        # Embed and index
        embedding_service = EmbeddingService()
        await embedding_service.index_chunks(
            chunks=result["chunks"],
            session_id=session_id,
            source=f"url:{request.url}",
            collection="business_context",
        )

        # Store metadata
        context_doc = {
            "session_id": session_id,
            "user_id": current_user["user_id"],
            "context_id": str(uuid.uuid4()),
            "type": "url",
            "source": str(request.url),
            "chunk_count": len(result["chunks"]),
            "created_at": datetime.utcnow(),
        }

        await db.business_context.insert_one(context_doc)

        return {
            "context_id": context_doc["context_id"],
            "source": str(request.url),
            "chunks": len(result["chunks"]),
            "indexed": True,
        }

    except Exception as e:
        logger.error("url_ingestion_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/context/text")
async def add_text_context(
    session_id: str,
    request: TextContextRequest,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Add text snippet as business context"""

    try:
        from app.services.document_parser import DocumentParser

        chunks = DocumentParser._chunk_text(request.text)

        # Embed and index
        embedding_service = EmbeddingService()
        await embedding_service.index_chunks(
            chunks=chunks,
            session_id=session_id,
            source=f"text:{request.title or 'snippet'}",
            collection="business_context",
        )

        # Store metadata
        context_doc = {
            "session_id": session_id,
            "user_id": current_user["user_id"],
            "context_id": str(uuid.uuid4()),
            "type": "text",
            "source": request.title or "text snippet",
            "chunk_count": len(chunks),
            "created_at": datetime.utcnow(),
        }

        await db.business_context.insert_one(context_doc)

        return {
            "context_id": context_doc["context_id"],
            "source": request.title or "text snippet",
            "chunks": len(chunks),
            "indexed": True,
        }

    except Exception as e:
        logger.error("text_context_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}/context")
async def get_session_context(
    session_id: str,
    db: AsyncDatabase = Depends(get_mongo_db),
    current_user = Depends(get_current_user),
):
    """Get all context for a session"""

    contexts = await db.business_context.find({
        "session_id": session_id,
        "user_id": current_user["user_id"],
    }).to_list(None)

    return {
        "session_id": session_id,
        "contexts": [
            {
                "context_id": c["context_id"],
                "type": c["type"],
                "source": c["source"],
                "chunk_count": c["chunk_count"],
                "created_at": c["created_at"].isoformat(),
            }
            for c in contexts
        ],
        "total": len(contexts),
    }
```

In main.py:
```python
from app.routers import context
app.include_router(context.router, prefix=f"{settings.API_PREFIX}")
```

### Files to Create/Modify
- `backend/app/routers/context.py`

---


ISSUE_30_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Business Context Upload API" \
  --body "$ISSUE_BODY_30" \
  --label "backend" --label "integration" --label "priority:high" \
  --milestone "M3")

echo "Created: Business Context Upload API -> $ISSUE_URL"
sleep 1

# Issue #31: Session Service - Cross-Session Memory Loading
ISSUE_BODY_31=$(cat <<'ISSUE_31_EOF'
### Description
Implement session service for loading conversation history and business context across sessions. Enables multi-session context awareness in orchestrator.

### Acceptance Criteria
- [ ] Load session chat history (last N messages)
- [ ] Load business context (semantic search in Qdrant)
- [ ] Format context for agent consumption
- [ ] Cache in Redis for performance
- [ ] TTL: 1 hour for cached context

### Implementation Details
backend/app/services/session.py (update):
```python
from app.services.embedding import EmbeddingService
from motor.motor_asyncio import AsyncDatabase
from redis.asyncio import Redis
import json

class SessionService:
    def __init__(self, db: AsyncDatabase, redis: Redis = None):
        self.db = db
        self.redis = redis

    async def get_session_context(
        self,
        session_id: str,
        user_id: str,
        max_history: int = 20,
    ) -> dict:
        """Load session context for agent consumption"""

        # Check Redis cache
        if self.redis:
            cache_key = f"session_context:{session_id}"
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)

        # Load chat history
        messages = await self.db.chat_history.find({
            "session_id": session_id,
            "user_id": user_id,
        }).sort("timestamp", -1).limit(max_history).to_list(None)

        # Load business context
        contexts = await self.db.business_context.find({
            "session_id": session_id,
            "user_id": user_id,
        }).to_list(None)

        # Prepare context object
        session_context = {
            "session_id": session_id,
            "conversation_history": [
                {
                    "role": m["role"],
                    "content": m["content"],
                    "timestamp": m["timestamp"].isoformat(),
                }
                for m in reversed(messages)
            ],
            "business_context": {
                "documents": [c["source"] for c in contexts if c["type"] == "document"],
                "urls": [c["source"] for c in contexts if c["type"] == "url"],
                "text_snippets": [c["source"] for c in contexts if c["type"] == "text"],
                "total_chunks": sum(c["chunk_count"] for c in contexts),
            },
        }

        # Cache in Redis
        if self.redis:
            await self.redis.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(session_context, default=str),
            )

        return session_context

    async def get_recent_insights(
        self,
        session_id: str,
        user_id: str,
        limit: int = 5,
    ) -> list:
        """Get recent analysis insights from session"""

        messages = await self.db.chat_history.find({
            "session_id": session_id,
            "user_id": user_id,
            "role": "assistant",
        }).sort("timestamp", -1).limit(limit).to_list(None)

        return [
            {
                "content": m["content"][:500],  # Summary
                "timestamp": m["timestamp"].isoformat(),
                "artifacts": m.get("artifacts", []),
            }
            for m in messages
        ]
```

### Files to Create/Modify
- `backend/app/services/session.py` (update)

---


ISSUE_31_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Session Service - Cross-Session Memory Loading" \
  --body "$ISSUE_BODY_31" \
  --label "backend" --label "integration" --label "priority:high" \
  --milestone "M3")

echo "Created: Session Service - Cross-Session Memory Loading -> $ISSUE_URL"
sleep 1

# Issue #32: Orchestrator Service - FastAPI-to-LangGraph Bridge
ISSUE_BODY_32=$(cat <<'ISSUE_32_EOF'
### Description
Create orchestrator service that bridges FastAPI backend to LangGraph agent orchestrator. Manages state initialization, result streaming, and WebSocket communication.

### Acceptance Criteria
- [ ] OrchestratorService class with async run() method
- [ ] Initializes OrchestrationState with session context
- [ ] Invokes LangGraph graph and streams results
- [ ] Broadcasts agent status updates via WebSocket
- [ ] Handles timeouts and error states
- [ ] Stores final message in MongoDB

### Implementation Details
backend/app/services/orchestrator.py:
```python
from motor.motor_asyncio import AsyncDatabase
from app.core.logger import get_logger
from app.websocket.manager import get_connection_manager
from app.websocket.protocol import status_message, artifact_message, error_message
from app.services.session import SessionService
from app.services.embedding import EmbeddingService
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import sys
import os

# Add agents path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../agents"))

from agents.orchestrator.graph import create_orchestrator_graph
from agents.orchestrator.state import OrchestrationState

logger = get_logger(__name__)

class OrchestratorService:
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.graph = create_orchestrator_graph()
        self.manager = get_connection_manager()

    async def run(
        self,
        session_id: str,
        user_id: str,
        query: str,
        business_context: Optional[str] = None,
        timeout_seconds: int = 120,
    ) -> Dict[str, Any]:
        """Run orchestrator with streaming"""

        try:
            # Load session context
            session_service = SessionService(self.db)
            session_context = await session_service.get_session_context(
                session_id, user_id
            )

            # Load relevant business context via semantic search
            embedding_service = EmbeddingService()
            context_docs = await embedding_service.search(
                query=query,
                session_id=session_id,
                limit=5,
            )

            context_summary = "\n".join([
                f"- {doc['text']}"
                for doc in context_docs
            ])

            # Initialize state
            state: OrchestrationState = {
                "user_query": query,
                "user_id": user_id,
                "session_id": session_id,
                "business_context": business_context or context_summary,
                "conversation_history": session_context.get("conversation_history", []),
                "planned_agents": [],
                "current_agent": None,
                "agent_outputs": {},
                "synthesis_result": None,
                "artifacts": [],
                "start_time": datetime.utcnow().timestamp(),
                "trace_data": {},
                "tokens_used": 0,
                "cost_estimate": 0.0,
            }

            logger.info(
                "orchestrator_started",
                session_id=session_id,
                query=query[:50],
            )

            # Broadcast start status
            await self.manager.broadcast(
                session_id,
                status_message(session_id, "orchestrator", "Analyzing query..."),
            )

            # Run graph with timeout
            result = await asyncio.wait_for(
                self._run_graph(state),
                timeout=timeout_seconds,
            )

            # Broadcast final result
            synthesis = result.get("synthesis_result", {})
            artifacts = result.get("artifacts", [])

            final_response = {
                "synthesis": str(synthesis),
                "artifacts": artifacts,
                "trace": result.get("trace_data", {}),
            }

            # Store in MongoDB
            message_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "role": "assistant",
                "content": str(synthesis),
                "artifacts": artifacts,
                "agent_outputs": result.get("agent_outputs"),
                "tokens_used": result.get("tokens_used"),
                "cost": result.get("cost_estimate"),
                "timestamp": datetime.utcnow(),
            }

            await self.db.chat_history.insert_one(message_doc)

            logger.info(
                "orchestrator_completed",
                session_id=session_id,
                artifacts=len(artifacts),
            )

            return final_response

        except asyncio.TimeoutError:
            logger.error("orchestrator_timeout", session_id=session_id)
            await self.manager.broadcast(
                session_id,
                error_message(session_id, "Query processing timed out after 120 seconds"),
            )
            raise Exception("Orchestrator timeout")

        except Exception as e:
            logger.error("orchestrator_error", session_id=session_id, error=str(e))
            await self.manager.broadcast(
                session_id,
                error_message(session_id, f"Processing error: {str(e)}"),
            )
            raise

    async def _run_graph(self, initial_state: OrchestrationState) -> Dict[str, Any]:
        """Execute LangGraph with streaming"""

        # This is where we invoke the compiled graph
        # The graph.invoke() returns the final state
        final_state = self.graph.invoke(initial_state)

        return final_state
```

backend/app/db/redis.py:
```python
from redis.asyncio import Redis
from app.core.config import settings
from typing import Optional

class RedisClient:
    _instance: Optional[Redis] = None

    @classmethod
    async def connect(cls) -> Redis:
        if cls._instance is None:
            cls._instance = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            await cls._instance.ping()
        return cls._instance

    @classmethod
    async def disconnect(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

async def get_redis() -> Redis:
    return await RedisClient.connect()
```

In app.py:
```python
from app.db.redis import RedisClient

@app.on_event("startup")
async def startup():
    await RedisClient.connect()

@app.on_event("shutdown")
async def shutdown():
    await RedisClient.disconnect()
```

### Files to Create/Modify
- `backend/app/services/orchestrator.py`
- `backend/app/db/redis.py`

---


ISSUE_32_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Orchestrator Service - FastAPI-to-LangGraph Bridge" \
  --body "$ISSUE_BODY_32" \
  --label "backend" --label "agents" --label "integration" --label "priority:critical" \
  --milestone "M3")

echo "Created: Orchestrator Service - FastAPI-to-LangGraph Bridge -> $ISSUE_URL"
sleep 1

# Issue #33: ChatStream + MessageBubble Components
ISSUE_BODY_33=$(cat <<'ISSUE_33_EOF'
### Description
Build ChatStream component for displaying message history and MessageBubble for individual messages with agent attribution, timestamps, and interactions.

### Acceptance Criteria
- [ ] ChatStream component: scrollable message list, auto-scroll to newest
- [ ] MessageBubble component: user vs assistant styling, timestamps
- [ ] Agent attribution in assistant messages
- [ ] Support for inline artifacts and citations
- [ ] Loading state with skeleton
- [ ] Responsive design (mobile + desktop)

### Implementation Details
frontend/src/components/ChatStream.tsx:
```typescript
import React, { useEffect, useRef } from 'react'
import { useChatStore } from '../stores/chatStore'
import { MessageBubble } from './MessageBubble'

export function ChatStream() {
  const { messages, loading } = useChatStore()
  const endRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto bg-gradient-to-b from-gray-50 to-white p-6">
      <div className="max-w-3xl mx-auto space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 py-12">
            <div className="text-4xl mb-4">💡</div>
            <p>Start a conversation about your market and growth strategy</p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}

        {loading && (
          <div className="flex gap-3 p-4 bg-gray-100 rounded-lg">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full animate-pulse" />
            <div className="flex-1">
              <div className="h-4 bg-gray-300 rounded w-3/4 mb-2 animate-pulse" />
              <div className="h-4 bg-gray-300 rounded w-1/2 animate-pulse" />
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>
    </div>
  )
}
```

frontend/src/components/MessageBubble.tsx:
```typescript
import React, { useState } from 'react'
import { Message } from '../stores/chatStore'
import { formatDistanceToNow } from 'date-fns'
import { ArtifactRenderer } from './ArtifactRenderer'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [expandTrace, setExpandTrace] = useState(false)

  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser
          ? 'bg-blue-500 text-white'
          : 'bg-gradient-to-r from-purple-400 to-pink-500 text-white'
      }`}>
        {isUser ? '👤' : '🤖'}
      </div>

      {/* Message content */}
      <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
        <div className={`inline-block max-w-2xl rounded-lg p-4 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}>
          <div className="text-sm">{message.content}</div>

          {/* Artifacts */}
          {message.artifacts && message.artifacts.length > 0 && (
            <div className="mt-4 space-y-3">
              {message.artifacts.map((artifact) => (
                <ArtifactRenderer key={artifact.id} artifact={artifact} />
              ))}
            </div>
          )}
        </div>

        {/* Timestamp and metadata */}
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : ''}`}>
          {formatDistanceToNow(message.timestamp, { addSuffix: true })}
          {message.tokensUsed && ` • ${message.tokensUsed} tokens`}
          {message.cost && ` • $${message.cost.toFixed(3)}`}
        </div>

        {/* Agent trace */}
        {message.agentTrace && (
          <div className="mt-3">
            <button
              onClick={() => setExpandTrace(!expandTrace)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              {expandTrace ? '▼' : '▶'} Agent trace ({message.agentTrace.agents.length} agents)
            </button>

            {expandTrace && (
              <div className="mt-2 text-xs bg-gray-50 p-2 rounded border border-gray-200">
                {message.agentTrace.agents.map((agent) => (
                  <div key={agent.name} className="flex items-center gap-2 mb-1">
                    <span className={`w-2 h-2 rounded-full ${
                      agent.status === 'completed' ? 'bg-green-500' :
                      agent.status === 'failed' ? 'bg-red-500' :
                      'bg-yellow-500'
                    }`} />
                    <span>{agent.name}: {agent.status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/ChatStream.tsx`
- `frontend/src/components/MessageBubble.tsx`

---


ISSUE_33_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "ChatStream + MessageBubble Components" \
  --body "$ISSUE_BODY_33" \
  --label "frontend" --label "priority:high" \
  --milestone "M3")

echo "Created: ChatStream + MessageBubble Components -> $ISSUE_URL"
sleep 1

# Issue #34: InputBar - Text Input, File Upload, URL Input
ISSUE_BODY_34=$(cat <<'ISSUE_34_EOF'
### Description
Build InputBar component for multi-input modes: text query, file upload (PDF/DOCX), URL input. Includes send button, loading state, error feedback.

### Acceptance Criteria
- [ ] Text input with Enter to send
- [ ] File upload button (PDF, DOCX, TXT)
- [ ] URL input field with validation
- [ ] Visual mode indicators (text/file/url)
- [ ] Send button with loading state
- [ ] Input validation and error messages
- [ ] Focus management and keyboard shortcuts

### Implementation Details
frontend/src/components/InputBar.tsx:
```typescript
import React, { useState, useRef } from 'react'
import { useChatStore } from '../stores/chatStore'
import { useWebSocket } from '../hooks/useWebSocket'
import { v4 as uuidv4 } from 'uuid'

type InputMode = 'text' | 'file' | 'url'

export function InputBar() {
  const [inputText, setInputText] = useState('')
  const [inputMode, setInputMode] = useState<InputMode>('text')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [urlInput, setUrlInput] = useState('')
  const [error, setError] = useState('')

  const { send, isConnected } = useWebSocket()
  const { loading, sessionId, addMessage } = useChatStore()
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleSendText() {
    if (!inputText.trim() || !isConnected || loading) return

    const userMsg = {
      id: uuidv4(),
      role: 'user' as const,
      content: inputText,
      timestamp: new Date(),
    }

    addMessage(userMsg)
    send(JSON.stringify({ type: 'text', content: inputText }))

    setInputText('')
    setError('')
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']

    if (!validTypes.includes(file.type)) {
      setError('Invalid file type. Use PDF, DOCX, or TXT.')
      return
    }

    if (file.size > 10 * 1024 * 1024) {  // 10MB
      setError('File too large. Max 10MB.')
      return
    }

    // Upload via API
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`/api/v1/upload-document?session_id=${sessionId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData,
      })

      if (response.ok) {
        setError('')
        setSelectedFile(null)
        setInputMode('text')

        const userMsg = {
          id: uuidv4(),
          role: 'user' as const,
          content: `Uploaded document: ${file.name}`,
          timestamp: new Date(),
        }
        addMessage(userMsg)

        send(JSON.stringify({ type: 'document', filename: file.name }))
      } else {
        setError('Upload failed')
      }
    } catch (err) {
      setError('Upload error: ' + String(err))
    }
  }

  async function handleUrlSubmit() {
    if (!urlInput.trim() || !isConnected || loading) return

    // Validate URL
    try {
      new URL(urlInput)
    } catch {
      setError('Invalid URL')
      return
    }

    try {
      const response = await fetch(`/api/v1/ingest-url?session_id=${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ url: urlInput }),
      })

      if (response.ok) {
        setError('')
        setUrlInput('')
        setInputMode('text')

        const userMsg = {
          id: uuidv4(),
          role: 'user' as const,
          content: `Added URL: ${urlInput}`,
          timestamp: new Date(),
        }
        addMessage(userMsg)

        send(JSON.stringify({ type: 'url', url: urlInput }))
      } else {
        setError('URL ingestion failed')
      }
    } catch (err) {
      setError('Error: ' + String(err))
    }
  }

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-3xl mx-auto">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-3">
          {/* Mode selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setInputMode('text')}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                inputMode === 'text'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              💬 Text
            </button>
            <button
              onClick={() => setInputMode('file')}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                inputMode === 'file'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📄 File
            </button>
            <button
              onClick={() => setInputMode('url')}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                inputMode === 'url'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🔗 URL
            </button>
          </div>

          {/* Input area */}
          <div className="flex-1">
            {inputMode === 'text' && (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
                  placeholder="Ask about market trends, competitors, pricing..."
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading || !isConnected}
                />
              </div>
            )}

            {inputMode === 'file' && (
              <div className="flex gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-1 border-2 border-dashed border-gray-300 rounded-lg py-2 text-center hover:bg-gray-50 transition"
                >
                  Click to upload PDF, DOCX, or TXT
                </button>
              </div>
            )}

            {inputMode === 'url' && (
              <div className="flex gap-2">
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://example.com"
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading || !isConnected}
                />
              </div>
            )}
          </div>

          {/* Send button */}
          <button
            onClick={() => {
              if (inputMode === 'text') handleSendText()
              else if (inputMode === 'file') fileInputRef.current?.click()
              else if (inputMode === 'url') handleUrlSubmit()
            }}
            disabled={loading || !isConnected}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition font-medium"
          >
            {loading ? '⏳' : '→'}
          </button>
        </div>

        <div className="text-xs text-gray-500 mt-2">
          {!isConnected && '🔴 Disconnected'}
          {isConnected && '🟢 Connected'}
        </div>
      </div>
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/InputBar.tsx`

---


ISSUE_34_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "InputBar - Text Input, File Upload, URL Input" \
  --body "$ISSUE_BODY_34" \
  --label "frontend" --label "priority:high" \
  --milestone "M3")

echo "Created: InputBar - Text Input, File Upload, URL Input -> $ISSUE_URL"
sleep 1

# Issue #35: ArtifactRenderer Dispatcher + Scorecard Component
ISSUE_BODY_35=$(cat <<'ISSUE_35_EOF'
### Description
Build ArtifactRenderer dispatcher component that routes artifact types to specialized renderers. Implement Scorecard artifact showing growth intelligence scores by domain.

### Acceptance Criteria
- [ ] ArtifactRenderer dispatcher with type-based routing
- [ ] Scorecard component: circular progress indicators, categories, scores
- [ ] Responsive grid layout
- [ ] Interactive category expansion
- [ ] Color-coded status (strong, moderate, opportunity)

### Implementation Details
frontend/src/components/ArtifactRenderer.tsx:
```typescript
import React from 'react'
import { Artifact } from '../stores/chatStore'
import { Scorecard } from './Artifacts/Scorecard'
import { TrendMap } from './Artifacts/TrendMap'
import { HeatMap } from './Artifacts/HeatMap'
import { Timeline } from './Artifacts/Timeline'
import { ComparisonTable } from './Artifacts/ComparisonTable'

interface ArtifactRendererProps {
  artifact: Artifact
}

export function ArtifactRenderer({ artifact }: ArtifactRendererProps) {
  switch (artifact.type) {
    case 'scorecard':
      return <Scorecard data={artifact.data} title={artifact.title} />
    case 'trendmap':
      return <TrendMap data={artifact.data} title={artifact.title} />
    case 'heatmap':
      return <HeatMap data={artifact.data} title={artifact.title} />
    case 'timeline':
      return <Timeline data={artifact.data} title={artifact.title} />
    case 'comparison':
      return <ComparisonTable data={artifact.data} title={artifact.title} />
    default:
      return (
        <div className="p-4 bg-gray-100 rounded border border-gray-300">
          Unknown artifact type: {artifact.type}
        </div>
      )
  }
}
```

frontend/src/components/Artifacts/Scorecard.tsx:
```typescript
import React, { useState } from 'react'

interface ScorecardData {
  overall_score: number
  categories: Record<string, { score: number; status: string }>
}

interface ScorecardProps {
  data: any
  title: string
}

export function Scorecard({ data, title }: ScorecardProps) {
  const [expanded, setExpanded] = useState(false)

  const typedData: ScorecardData = data

  const statusColor = {
    strong: '#10b981',
    moderate: '#f59e0b',
    opportunity: '#3b82f6',
    weak: '#ef4444',
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold mb-6">{title}</h3>

      {/* Overall score circle */}
      <div className="flex justify-center mb-8">
        <div className="relative w-40 h-40">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="4"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#3b82f6"
              strokeWidth="4"
              strokeDasharray={`${2 * Math.PI * 45 * (typedData.overall_score / 100)} ${2 * Math.PI * 45}`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600">
                {typedData.overall_score}
              </div>
              <div className="text-sm text-gray-600">Growth Score</div>
            </div>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-3">
        {Object.entries(typedData.categories).map(([category, stats]: any) => (
          <div key={category} className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <div className="flex-1">
              <div className="font-medium text-gray-900 capitalize">
                {category.replace(/_/g, ' ')}
              </div>
              <div className="w-full bg-gray-200 rounded h-2 mt-1">
                <div
                  className="h-2 rounded transition-all"
                  style={{
                    width: `${stats.score}%`,
                    backgroundColor: statusColor[stats.status as keyof typeof statusColor],
                  }}
                />
              </div>
            </div>
            <div className="ml-4 w-12 text-right">
              <div className="text-sm font-bold text-gray-900">{stats.score}</div>
              <div className="text-xs text-gray-500">{stats.status}</div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-4 text-blue-600 text-sm hover:text-blue-800 font-medium"
      >
        {expanded ? '▼ Hide details' : '▶ Show insights'}
      </button>

      {expanded && (
        <div className="mt-4 p-4 bg-blue-50 rounded border border-blue-200 text-sm text-gray-700">
          <p>Detailed insights and recommendations appear here based on domain analysis.</p>
        </div>
      )}
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/ArtifactRenderer.tsx`
- `frontend/src/components/Artifacts/Scorecard.tsx`

---


ISSUE_35_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "ArtifactRenderer Dispatcher + Scorecard Component" \
  --body "$ISSUE_BODY_35" \
  --label "frontend" --label "priority:high" \
  --milestone "M3")

echo "Created: ArtifactRenderer Dispatcher + Scorecard Component -> $ISSUE_URL"
sleep 1

# Issue #36: TrendMap + Timeline Artifact Components
ISSUE_BODY_36=$(cat <<'ISSUE_36_EOF'
### Description
Implement TrendMap (timeline of market trends with confidence levels) and Timeline (event-based historical view) artifact components. Chart.js or Recharts for visualization.

### Acceptance Criteria
- [ ] TrendMap: line chart showing trend over time with confidence bands
- [ ] Timeline: vertical event timeline with dates and confidence scores
- [ ] Interactive tooltips with details
- [ ] Color-coded confidence levels (high/medium/low)
- [ ] Responsive sizing

### Implementation Details
frontend/src/components/Artifacts/TrendMap.tsx:
```typescript
import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface TrendMapProps {
  data: any
  title: string
}

export function TrendMap({ data, title }: TrendMapProps) {
  const chartData = data.events?.map((e: any) => ({
    date: e.date,
    trend: Math.random() * 100,  // Placeholder
    confidence: e.confidence,
  })) || []

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold mb-4">{title}</h3>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip
              contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }}
              formatter={(value) => [`${value.toFixed(1)}%`, 'Confidence']}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="confidence"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Confidence"
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="text-gray-400 text-center py-12">No trend data available</div>
      )}
    </div>
  )
}
```

frontend/src/components/Artifacts/Timeline.tsx:
```typescript
import React from 'react'

interface TimelineEvent {
  date: string
  event: string
  confidence: number
}

interface TimelineProps {
  data: any
  title: string
}

export function Timeline({ data, title }: TimelineProps) {
  const events: TimelineEvent[] = data.events || []

  const getConfidenceColor = (conf: number) => {
    if (conf >= 80) return 'bg-green-500'
    if (conf >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold mb-6">{title}</h3>

      {events.length > 0 ? (
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-6 top-0 bottom-0 w-1 bg-gray-200" />

          {/* Events */}
          <div className="space-y-6 pl-20">
            {events.map((event, idx) => (
              <div key={idx} className="relative">
                {/* Dot */}
                <div className={`absolute -left-16 top-1 w-4 h-4 rounded-full ${getConfidenceColor(event.confidence)} border-4 border-white shadow`} />

                {/* Content */}
                <div className="bg-gray-50 p-4 rounded border border-gray-200">
                  <div className="font-bold text-gray-900">{event.event}</div>
                  <div className="text-sm text-gray-600 mt-1">{event.date}</div>
                  <div className="text-xs text-gray-500 mt-2">
                    Confidence: {event.confidence}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-gray-400 text-center py-12">No timeline events</div>
      )}
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/Artifacts/TrendMap.tsx`
- `frontend/src/components/Artifacts/Timeline.tsx`
- `frontend/package.json` (add `recharts`)

---


ISSUE_36_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "TrendMap + Timeline Artifact Components" \
  --body "$ISSUE_BODY_36" \
  --label "frontend" --label "priority:high" \
  --milestone "M3")

echo "Created: TrendMap + Timeline Artifact Components -> $ISSUE_URL"
sleep 1

# Issue #37: HeatMap + ComparisonTable Artifact Components
ISSUE_BODY_37=$(cat <<'ISSUE_37_EOF'
### Description
Implement HeatMap (competitive positioning matrix) and ComparisonTable (feature comparison across competitors) artifact components.

### Acceptance Criteria
- [ ] HeatMap: colored grid showing competitor positions across dimensions
- [ ] ComparisonTable: feature-by-competitor matrix with checkmarks/scores
- [ ] Interactive tooltips and sorting
- [ ] Scalable to 5-10 dimensions and competitors
- [ ] Export as CSV (optional)

### Implementation Details
frontend/src/components/Artifacts/HeatMap.tsx:
```typescript
import React, { useState } from 'react'

interface HeatMapProps {
  data: any
  title: string
}

export function HeatMap({ data, title }: HeatMapProps) {
  const [hoveredCell, setHoveredCell] = useState<string | null>(null)

  const dimensions = data.dimensions || []
  const competitors = data.competitors || {}

  const getColor = (score: number) => {
    if (score >= 8) return 'bg-green-500'
    if (score >= 6) return 'bg-yellow-400'
    if (score >= 4) return 'bg-orange-400'
    return 'bg-red-400'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 overflow-x-auto">
      <h3 className="text-lg font-bold mb-4">{title}</h3>

      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="border border-gray-300 p-2 bg-gray-100 font-semibold text-left">Dimension</th>
            {Object.keys(competitors).map((competitor) => (
              <th key={competitor} className="border border-gray-300 p-2 bg-gray-100 font-semibold text-center">
                {competitor}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dimensions.map((dim: string) => (
            <tr key={dim}>
              <td className="border border-gray-300 p-2 font-medium text-gray-900 bg-gray-50">
                {dim}
              </td>
              {Object.entries(competitors).map(([competitor, scores]: [string, any]) => {
                const score = scores[dimensions.indexOf(dim)]
                const cellKey = `${competitor}-${dim}`

                return (
                  <td
                    key={cellKey}
                    className={`border border-gray-300 p-3 text-center text-white font-bold cursor-pointer transition ${getColor(score)}`}
                    onMouseEnter={() => setHoveredCell(cellKey)}
                    onMouseLeave={() => setHoveredCell(null)}
                    title={`${competitor} - ${dim}: ${score}/10`}
                  >
                    {score}
                    {hoveredCell === cellKey && (
                      <div className="text-xs mt-1 text-white">{score}/10</div>
                    )}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Legend */}
      <div className="mt-4 flex gap-4 justify-center text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded" /> Strong (8-10)
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-400 rounded" /> Good (6-7)
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-orange-400 rounded" /> Fair (4-5)
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-400 rounded" /> Weak (1-3)
        </div>
      </div>
    </div>
  )
}
```

frontend/src/components/Artifacts/ComparisonTable.tsx:
```typescript
import React from 'react'

interface ComparisonTableProps {
  data: any
  title: string
}

export function ComparisonTable({ data, title }: ComparisonTableProps) {
  const features = data.features || []
  const competitors = data.competitors || {}

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 overflow-x-auto">
      <h3 className="text-lg font-bold mb-4">{title}</h3>

      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="border border-gray-300 p-3 bg-gray-100 font-semibold text-left">Feature</th>
            {Object.keys(competitors).map((competitor) => (
              <th key={competitor} className="border border-gray-300 p-3 bg-gray-100 font-semibold text-center">
                {competitor}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {features.map((feature: string, idx: number) => (
            <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              <td className="border border-gray-300 p-3 font-medium text-gray-900">
                {feature}
              </td>
              {Object.entries(competitors).map(([competitor, hasFeature]: [string, any]) => (
                <td
                  key={competitor}
                  className="border border-gray-300 p-3 text-center"
                >
                  {hasFeature ? (
                    <span className="text-green-600 font-bold text-lg">✓</span>
                  ) : (
                    <span className="text-gray-300 font-bold text-lg">○</span>
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/Artifacts/HeatMap.tsx`
- `frontend/src/components/Artifacts/ComparisonTable.tsx`

---


ISSUE_37_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "HeatMap + ComparisonTable Artifact Components" \
  --body "$ISSUE_BODY_37" \
  --label "frontend" --label "priority:high" \
  --milestone "M3")

echo "Created: HeatMap + ComparisonTable Artifact Components -> $ISSUE_URL"
sleep 1

# Issue #38: ConfidencePanel + Source Trail Expansion
ISSUE_BODY_38=$(cat <<'ISSUE_38_EOF'
### Description
Build ConfidencePanel showing confidence levels per recommendation with source trail. Expandable to show which sources contributed to each insight.

### Acceptance Criteria
- [ ] Confidence scores displayed as percentages with visual indicators
- [ ] Collapsible source trail per insight
- [ ] Link to original sources (Firecrawl, SerpAPI, Reddit, HN)
- [ ] Citation formatting for each source
- [ ] Metadata: date, data freshness

### Implementation Details
frontend/src/components/ConfidencePanel.tsx:
```typescript
import React, { useState } from 'react'

interface Source {
  name: string
  url?: string
  type: string
  date: string
  relevance: number
}

interface Insight {
  id: string
  text: string
  confidence: number
  sources: Source[]
}

interface ConfidencePanelProps {
  insights: Insight[]
}

export function ConfidencePanel({ insights }: ConfidencePanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const getConfidenceColor = (conf: number) => {
    if (conf >= 80) return 'text-green-600'
    if (conf >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getSourceIcon = (type: string) => {
    const icons: Record<string, string> = {
      firecrawl: '🌐',
      serpapi: '🔍',
      reddit: '👥',
      hackernews: '📰',
      linkedin: '💼',
      patent: '📜',
      default: '📄',
    }
    return icons[type.toLowerCase()] || icons.default
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold mb-4">Confidence & Sources</h3>

      <div className="space-y-4">
        {insights.map((insight) => (
          <div key={insight.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-gray-900 font-medium">{insight.text}</p>
              </div>

              <div className={`text-2xl font-bold ml-4 ${getConfidenceColor(insight.confidence)}`}>
                {insight.confidence}%
              </div>
            </div>

            {/* Source trail */}
            <button
              onClick={() => setExpandedId(expandedId === insight.id ? null : insight.id)}
              className="mt-3 text-blue-600 text-sm hover:text-blue-800 font-medium"
            >
              {expandedId === insight.id ? '▼' : '▶'} {insight.sources.length} source{insight.sources.length !== 1 ? 's' : ''}
            </button>

            {expandedId === insight.id && (
              <div className="mt-3 space-y-2 pl-4 border-l-2 border-blue-200">
                {insight.sources.map((source, idx) => (
                  <div key={idx} className="text-sm">
                    <div className="flex items-center gap-2">
                      <span>{getSourceIcon(source.type)}</span>
                      <span className="font-medium text-gray-900">{source.name}</span>
                      <span className="text-xs text-gray-500">({source.date})</span>
                    </div>

                    {source.url && (
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-xs ml-6"
                      >
                        View source →
                      </a>
                    )}

                    <div className="text-xs text-gray-500 ml-6">
                      Relevance: {(source.relevance * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/ConfidencePanel.tsx`

---


ISSUE_38_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "ConfidencePanel + Source Trail Expansion" \
  --body "$ISSUE_BODY_38" \
  --label "frontend" --label "priority:high" \
  --milestone "M3")

echo "Created: ConfidencePanel + Source Trail Expansion -> $ISSUE_URL"
sleep 1

# Issue #39: AgentStatusPanel - Real-Time Agent Status
ISSUE_BODY_39=$(cat <<'ISSUE_39_EOF'
### Description
Build AgentStatusPanel showing real-time agent execution status. Displays domain agents as they run: pending → running → completed/failed.

### Acceptance Criteria
- [ ] Live agent status indicator (pending/running/completed/failed)
- [ ] Timeline of agent execution
- [ ] Error messages for failed agents
- [ ] Duration per agent
- [ ] Total query duration timer

### Implementation Details
frontend/src/components/AgentStatusPanel.tsx:
```typescript
import React, { useEffect, useState } from 'react'
import { useChatStore } from '../stores/chatStore'

export function AgentStatusPanel() {
  const { messages } = useChatStore()
  const [duration, setDuration] = useState(0)

  const lastMessage = messages[messages.length - 1]
  const agents = lastMessage?.agentTrace?.agents || []

  useEffect(() => {
    if (!lastMessage?.agentTrace) return

    const startTime = Date.now()
    const interval = setInterval(() => {
      setDuration(Math.round((Date.now() - startTime) / 1000))
    }, 100)

    return () => clearInterval(interval)
  }, [lastMessage])

  const getStatusIcon = (status: string) => {
    const icons: Record<string, string> = {
      pending: '⏳',
      running: '⚙️',
      completed: '✓',
      failed: '✗',
    }
    return icons[status] || '•'
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'text-gray-400',
      running: 'text-blue-600 animate-pulse',
      completed: 'text-green-600',
      failed: 'text-red-600',
    }
    return colors[status] || 'text-gray-600'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold mb-4">Agent Execution</h3>

      {agents.length > 0 ? (
        <>
          <div className="space-y-3">
            {agents.map((agent) => (
              <div key={agent.name} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                <span className={`text-2xl ${getStatusColor(agent.status)}`}>
                  {getStatusIcon(agent.status)}
                </span>

                <div className="flex-1">
                  <div className="font-medium text-gray-900 capitalize">
                    {agent.name.replace(/_/g, ' ')}
                  </div>
                  <div className={`text-sm ${getStatusColor(agent.status)}`}>
                    {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </div>
                </div>

                {agent.status === 'failed' && agent.error && (
                  <div className="text-xs text-red-600 text-right">{agent.error}</div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600">
            <div>Query duration: <span className="font-bold text-gray-900">{duration}s</span></div>
          </div>
        </>
      ) : (
        <div className="text-gray-400 text-center py-8">No agents executed yet</div>
      )}
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/AgentStatusPanel.tsx`

---


ISSUE_39_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "AgentStatusPanel - Real-Time Agent Status" \
  --body "$ISSUE_BODY_39" \
  --label "frontend" --label "priority:medium" \
  --milestone "M3")

echo "Created: AgentStatusPanel - Real-Time Agent Status -> $ISSUE_URL"
sleep 1

# Issue #40: ClarificationChips Component
ISSUE_BODY_40=$(cat <<'ISSUE_40_EOF'
### Description
Build ClarificationChips component for displaying clarification options when query is ambiguous. Clickable chips to refine query.

### Acceptance Criteria
- [ ] Chip UI for each clarification option
- [ ] Click to refine query and rerun
- [ ] Smooth transitions
- [ ] Dismiss capability
- [ ] Keyboard navigation support

### Implementation Details
frontend/src/components/ClarificationChips.tsx:
```typescript
import React from 'react'
import { useChatStore } from '../stores/chatStore'
import { useWebSocket } from '../hooks/useWebSocket'

interface ClarificationOption {
  id: string
  text: string
  query: string
}

interface ClarificationChipsProps {
  options: ClarificationOption[]
  onSelect?: (query: string) => void
}

export function ClarificationChips({ options, onSelect }: ClarificationChipsProps) {
  const { addMessage } = useChatStore()
  const { send } = useWebSocket()

  async function handleSelect(option: ClarificationOption) {
    const userMsg = {
      id: option.id,
      role: 'user' as const,
      content: option.query,
      timestamp: new Date(),
    }

    addMessage(userMsg)
    send(JSON.stringify({ content: option.query }))
    onSelect?.(option.query)
  }

  return (
    <div className="flex flex-wrap gap-2 p-4 bg-blue-50 rounded-lg border border-blue-200">
      <span className="text-sm text-gray-600 self-center">Did you mean:</span>
      {options.map((option) => (
        <button
          key={option.id}
          onClick={() => handleSelect(option)}
          className="px-4 py-2 bg-white border-2 border-blue-300 text-blue-600 rounded-full text-sm font-medium hover:bg-blue-100 transition"
        >
          {option.text}
        </button>
      ))}
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/ClarificationChips.tsx`

---


ISSUE_40_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "ClarificationChips Component" \
  --body "$ISSUE_BODY_40" \
  --label "frontend" --label "priority:medium" \
  --milestone "M3")

echo "Created: ClarificationChips Component -> $ISSUE_URL"
sleep 1

# Issue #41: BusinessContextPanel Component
ISSUE_BODY_41=$(cat <<'ISSUE_41_EOF'
### Description
Build BusinessContextPanel for displaying and managing uploaded context (documents, URLs, text). Shows context sources and allows removal.

### Acceptance Criteria
- [ ] List of uploaded context sources
- [ ] Document/URL/text type indicators
- [ ] Upload date and chunk count
- [ ] Delete button per context
- [ ] Total context statistics

### Implementation Details
frontend/src/components/BusinessContextPanel.tsx:
```typescript
import React, { useEffect, useState } from 'react'
import { useChatStore } from '../stores/chatStore'

interface ContextItem {
  context_id: string
  type: 'document' | 'url' | 'text'
  source: string
  chunk_count: number
  created_at: string
}

export function BusinessContextPanel() {
  const { sessionId } = useChatStore()
  const [contexts, setContexts] = useState<ContextItem[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (sessionId) {
      fetchContexts()
    }
  }, [sessionId])

  async function fetchContexts() {
    if (!sessionId) return

    setLoading(true)
    try {
      const response = await fetch(`/api/v1/sessions/${sessionId}/context`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      })

      if (response.ok) {
        const data = await response.json()
        setContexts(data.contexts)
      }
    } catch (err) {
      console.error('Failed to fetch contexts:', err)
    } finally {
      setLoading(false)
    }
  }

  async function deleteContext(contextId: string) {
    try {
      await fetch(`/api/v1/sessions/${sessionId}/context/${contextId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      })

      setContexts(contexts.filter((c) => c.context_id !== contextId))
    } catch (err) {
      console.error('Failed to delete context:', err)
    }
  }

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      document: '📄',
      url: '🔗',
      text: '📝',
    }
    return icons[type] || '📌'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold mb-4">Business Context</h3>

      {loading ? (
        <div className="text-gray-400 text-center py-8">Loading...</div>
      ) : contexts.length > 0 ? (
        <div className="space-y-3">
          {contexts.map((context) => (
            <div
              key={context.context_id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200"
            >
              <div className="flex items-center gap-3 flex-1">
                <span className="text-xl">{getTypeIcon(context.type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 truncate">{context.source}</div>
                  <div className="text-xs text-gray-500">
                    {context.chunk_count} chunks • {new Date(context.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <button
                onClick={() => deleteContext(context.context_id)}
                className="ml-3 text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Remove
              </button>
            </div>
          ))}

          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600">
            Total chunks: <span className="font-bold">{contexts.reduce((sum, c) => sum + c.chunk_count, 0)}</span>
          </div>
        </div>
      ) : (
        <div className="text-gray-400 text-center py-8">
          No business context uploaded yet. Use the InputBar to add documents, URLs, or text.
        </div>
      )}
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/BusinessContextPanel.tsx`

---


ISSUE_41_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "BusinessContextPanel Component" \
  --body "$ISSUE_BODY_41" \
  --label "frontend" --label "priority:medium" \
  --milestone "M3")

echo "Created: BusinessContextPanel Component -> $ISSUE_URL"
sleep 1

# Issue #42: TraceViewer - Post-Query Agent Trace Expansion
ISSUE_BODY_42=$(cat <<'ISSUE_42_EOF'
### Description
Build TraceViewer component for detailed post-query inspection. Shows agent call stack, latencies, token usage, cost breakdown.

### Acceptance Criteria
- [ ] Expandable trace tree showing agent execution hierarchy
- [ ] Latency per agent and step
- [ ] Token usage breakdown
- [ ] Cost estimation per agent
- [ ] Tool calls and parameters
- [ ] Error stack traces for failed agents

### Implementation Details
frontend/src/components/TraceViewer.tsx:
```typescript
import React, { useState } from 'react'

interface TraceNode {
  agent: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  duration_ms: number
  tokens: number
  cost: number
  error?: string
  children?: TraceNode[]
  tools_called?: Array<{ name: string; duration_ms: number }>
}

interface TraceViewerProps {
  trace: TraceNode
}

export function TraceViewer({ trace }: TraceViewerProps) {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set())

  const toggleExpanded = (agent: string) => {
    const newSet = new Set(expandedAgents)
    if (newSet.has(agent)) {
      newSet.delete(agent)
    } else {
      newSet.add(agent)
    }
    setExpandedAgents(newSet)
  }

  const renderNode = (node: TraceNode, level: number = 0) => {
    const key = `${node.agent}-${level}`
    const isExpanded = expandedAgents.has(key)
    const hasChildren = (node.children?.length || 0) > 0 || (node.tools_called?.length || 0) > 0

    return (
      <div key={key} className={`ml-${level * 4}`}>
        <div className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded">
          {hasChildren && (
            <button
              onClick={() => toggleExpanded(key)}
              className="text-gray-600 hover:text-gray-900"
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          )}

          {!hasChildren && <span className="w-5" />}

          <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
            {node.agent}
          </span>

          <span className={`text-xs font-medium ${
            node.status === 'completed' ? 'text-green-600' :
            node.status === 'failed' ? 'text-red-600' :
            node.status === 'running' ? 'text-blue-600' :
            'text-gray-400'
          }`}>
            {node.status.toUpperCase()}
          </span>

          <span className="text-xs text-gray-500">
            {node.duration_ms}ms
          </span>

          <span className="text-xs text-gray-500">
            {node.tokens} tokens • ${node.cost.toFixed(4)}
          </span>
        </div>

        {isExpanded && (
          <>
            {node.error && (
              <div className="ml-6 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 font-mono">
                {node.error}
              </div>
            )}

            {node.tools_called && node.tools_called.length > 0 && (
              <div className="ml-6 text-xs text-gray-600">
                <div className="font-semibold mt-2 mb-1">Tools Called:</div>
                {node.tools_called.map((tool, idx) => (
                  <div key={idx} className="ml-2">
                    {tool.name} ({tool.duration_ms}ms)
                  </div>
                ))}
              </div>
            )}

            {node.children && node.children.map((child) => renderNode(child, level + 1))}
          </>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold mb-4">Execution Trace</h3>

      <div className="bg-gray-50 rounded p-4 font-mono text-sm overflow-x-auto">
        {renderNode(trace)}
      </div>
    </div>
  )
}
```

### Files to Create/Modify
- `frontend/src/components/TraceViewer.tsx`

---

## MILESTONE M4: Polish, Observability & Deploy

---


ISSUE_42_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "TraceViewer - Post-Query Agent Trace Expansion" \
  --body "$ISSUE_BODY_42" \
  --label "frontend" --label "priority:medium" \
  --milestone "M3")

echo "Created: TraceViewer - Post-Query Agent Trace Expansion -> $ISSUE_URL"
sleep 1

# Issue #43: OpenTelemetry Integration - Structured Logs + Distributed Traces
ISSUE_BODY_43=$(cat <<'ISSUE_43_EOF'
### Description
Integrate OpenTelemetry for structured logging and distributed tracing. Exports traces to Jaeger or Datadog. Instruments FastAPI, MongoDB, and Redis.

### Acceptance Criteria
- [ ] OpenTelemetry SDK and exporters configured
- [ ] HTTP span instrumentation (all FastAPI routes)
- [ ] Database instrumentation (MongoDB, Redis calls)
- [ ] Custom spans for orchestrator, agents
- [ ] Trace ID propagation across services
- [ ] JSON structured logs with trace context

### Implementation Details
backend/app/core/telemetry.py:
```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from app.core.config import settings
import logging

def init_telemetry():
    """Initialize OpenTelemetry tracing and metrics"""

    if not settings.OTEL_ENABLED:
        return

    # Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    # Tracer provider
    trace_provider = TracerProvider()
    trace_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    trace.set_tracer_provider(trace_provider)

    # Instrument libraries
    FastAPIInstrumentor.instrument_app(app)
    PymongoInstrumentor().instrument()
    RedisInstrumentor().instrument()

    logger = logging.getLogger(__name__)
    logger.info("OpenTelemetry initialized")

def get_tracer(name: str):
    """Get tracer instance"""
    return trace.get_tracer(name)
```

In app.py startup:
```python
from app.core.telemetry import init_telemetry

@app.on_event("startup")
async def startup():
    init_telemetry()
```

### Files to Create/Modify
- `backend/app/core/telemetry.py`
- `backend/requirements.txt` (add OpenTelemetry packages)

---


ISSUE_43_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "OpenTelemetry Integration - Structured Logs + Distributed Traces" \
  --body "$ISSUE_BODY_43" \
  --label "backend" --label "infra" --label "priority:high" \
  --milestone "M4")

echo "Created: OpenTelemetry Integration - Structured Logs + Distributed Traces -> $ISSUE_URL"
sleep 1

# Issue #44: Agent Observability Callbacks - Span Emission from LangGraph
ISSUE_BODY_44=$(cat <<'ISSUE_44_EOF'
### Description
Implement observability callbacks in LangGraph nodes. Emit spans for agent execution, tool calls, timing, and token usage. Integrates with OpenTelemetry.

### Acceptance Criteria
- [ ] Span creation for each agent execution
- [ ] Tool call spans with parameters
- [ ] Token and cost tracking per span
- [ ] Span attributes: query, agent_name, status
- [ ] Trace ID propagation in A2A messages
- [ ] Error and exception span recording

### Implementation Details
agents/orchestrator/callbacks.py:
```python
from typing import Any, Dict
from opentelemetry import trace
from app.core.logger import get_logger
import time

logger = get_logger(__name__)

class ObservabilityCallbacks:
    """Callbacks for tracing agent execution"""

    def __init__(self):
        self.tracer = trace.get_tracer("langgraph-orchestrator")

    def on_agent_start(self, agent_name: str, input_data: Dict[str, Any]):
        """Called when agent starts"""

        span = self.tracer.start_span(f"agent.{agent_name}")
        span.set_attribute("agent_name", agent_name)
        span.set_attribute("input_keys", list(input_data.keys()))

        return span

    def on_agent_end(self, span, output_data: Dict[str, Any], duration_ms: float):
        """Called when agent completes"""

        span.set_attribute("status", "completed")
        span.set_attribute("duration_ms", duration_ms)
        span.set_attribute("output_keys", list(output_data.keys()))
        span.end()

    def on_agent_error(self, span, error: Exception, duration_ms: float):
        """Called on agent error"""

        span.set_attribute("status", "failed")
        span.set_attribute("error", str(error))
        span.set_attribute("duration_ms", duration_ms)
        span.record_exception(error)
        span.end()

    def on_tool_call(self, tool_name: str, params: Dict[str, Any]):
        """Called when agent calls a tool"""

        span = self.tracer.start_span(f"tool.{tool_name}")
        span.set_attribute("tool_name", tool_name)
        span.set_attribute("param_keys", list(params.keys()))

        return span

    def on_tool_result(self, span, result: Dict[str, Any], tokens_used: int, cost: float):
        """Called when tool returns result"""

        span.set_attribute("status", "success")
        span.set_attribute("tokens_used", tokens_used)
        span.set_attribute("cost", cost)
        span.end()

# Global callbacks instance
_callbacks = ObservabilityCallbacks()

def get_callbacks():
    return _callbacks
```

Usage in domain agents:
```python
from agents.orchestrator.callbacks import get_callbacks

async def market_trend_agent(state):
    callbacks = get_callbacks()
    span = callbacks.on_agent_start("market_trend_agent", state)

    try:
        # Agent logic
        result = {}
        callbacks.on_agent_end(span, result, duration_ms=1000)
        return state
    except Exception as e:
        callbacks.on_agent_error(span, e, duration_ms=1000)
        raise
```

### Files to Create/Modify
- `agents/orchestrator/callbacks.py`

---


ISSUE_44_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Agent Observability Callbacks - Span Emission from LangGraph" \
  --body "$ISSUE_BODY_44" \
  --label "agents" --label "priority:high" \
  --milestone "M4")

echo "Created: Agent Observability Callbacks - Span Emission from LangGraph -> $ISSUE_URL"
sleep 1

# Issue #45: Audit Log Persistence - MongoDB audit_logs Collection
ISSUE_BODY_45=$(cat <<'ISSUE_45_EOF'
### Description
Implement audit logging for all user actions: login, context uploads, queries, artifact access. Stores in MongoDB with searchable indexes.

### Acceptance Criteria
- [ ] AuditLog model with action, resource, status, timestamp
- [ ] Log on user events (login, logout, register)
- [ ] Log on content operations (upload, ingest, query, export)
- [ ] Indexes on user_id, action, created_at
- [ ] Retention policy (90 days)
- [ ] Audit log API endpoint for admin review

### Implementation Details
backend/app/services/audit.py:
```python
from motor.motor_asyncio import AsyncDatabase
from datetime import datetime, timedelta
from typing import Optional
from app.core.logger import get_logger
from bson import ObjectId

logger = get_logger(__name__)

class AuditService:
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.collection = db.audit_logs

    async def log(
        self,
        user_id: str,
        action: str,
        resource: Optional[str] = None,
        status: str = "success",
        details: Optional[dict] = None,
        error_message: Optional[str] = None,
    ):
        """Log an audit event"""

        audit_doc = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {},
            "error_message": error_message,
            "created_at": datetime.utcnow(),
            "ip_address": details.get("ip_address") if details else None,
        }

        try:
            result = await self.collection.insert_one(audit_doc)
            logger.info(
                "audit_logged",
                action=action,
                user_id=user_id,
                status=status,
            )
            return str(result.inserted_id)
        except Exception as e:
            logger.error("audit_log_failed", error=str(e))
            raise

    async def get_user_logs(
        self,
        user_id: str,
        limit: int = 100,
        skip: int = 0,
    ) -> list:
        """Get audit logs for a user"""

        logs = await self.collection.find({
            "user_id": user_id,
        }).sort("created_at", -1).skip(skip).limit(limit).to_list(None)

        return logs

    async def cleanup_old_logs(self, days: int = 90):
        """Delete logs older than N days"""

        cutoff = datetime.utcnow() - timedelta(days=days)

        result = await self.collection.delete_many({
            "created_at": {"$lt": cutoff},
        })

        logger.info("audit_cleanup", deleted_count=result.deleted_count)
```

In routers (e.g., auth.py):
```python
from app.services.audit import AuditService

@router.post("/login")
async def login(request: LoginRequest, db: AsyncDatabase = Depends(get_mongo_db)):
    # ... auth logic ...

    audit_service = AuditService(db)
    await audit_service.log(
        user_id=str(user["_id"]),
        action="login",
        status="success",
        details={"email": request.email},
    )

    return TokenResponse(...)
```

### Files to Create/Modify
- `backend/app/services/audit.py`

---


ISSUE_45_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Audit Log Persistence - MongoDB audit_logs Collection" \
  --body "$ISSUE_BODY_45" \
  --label "backend" --label "priority:high" \
  --milestone "M4")

echo "Created: Audit Log Persistence - MongoDB audit_logs Collection -> $ISSUE_URL"
sleep 1

# Issue #46: Cost Tracking - Token Counting + Cost Estimation Per Query
ISSUE_BODY_46=$(cat <<'ISSUE_46_EOF'
### Description
Implement token counting and cost tracking. Estimates OpenAI costs per query and per agent. Stores in message metadata.

### Acceptance Criteria
- [ ] Token counting for LLM calls (tiktoken)
- [ ] Cost calculation (GPT-4: $0.03/$0.06 per 1K tokens)
- [ ] Track tokens per agent
- [ ] Aggregate cost per session/month
- [ ] Cost breakdown in UI (artifacts)

### Implementation Details
agents/utils/cost_tracker.py:
```python
import tiktoken
from typing import Dict, Any

class CostTracker:
    """Track token usage and costs"""

    # OpenAI pricing (March 2024)
    PRICING = {
        "gpt-4": {
            "input": 0.00003,  # per token
            "output": 0.00006,
        },
        "gpt-4-turbo": {
            "input": 0.00001,
            "output": 0.00003,
        },
        "gpt-3.5-turbo": {
            "input": 0.0000005,
            "output": 0.0000015,
        },
    }

    def __init__(self):
        self.encoder = tiktoken.encoding_for_model("gpt-4")
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.agent_costs: Dict[str, Dict[str, Any]] = {}

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost for LLM call"""

        pricing = self.PRICING.get(model, self.PRICING["gpt-4"])

        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]

        return input_cost + output_cost

    def track_agent_call(
        self,
        agent_name: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ):
        """Track cost for agent call"""

        cost = self.calculate_cost(model, input_tokens, output_tokens)

        if agent_name not in self.agent_costs:
            self.agent_costs[agent_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "calls": 0,
            }

        self.agent_costs[agent_name]["input_tokens"] += input_tokens
        self.agent_costs[agent_name]["output_tokens"] += output_tokens
        self.agent_costs[agent_name]["cost"] += cost
        self.agent_costs[agent_name]["calls"] += 1

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary"""

        total_cost = sum(agent["cost"] for agent in self.agent_costs.values())

        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": total_cost,
            "by_agent": self.agent_costs,
        }

# Global tracker
_tracker = CostTracker()

def get_cost_tracker():
    return _tracker
```

In synthesis agent:
```python
from agents.utils.cost_tracker import get_cost_tracker

async def synthesis_agent(state):
    tracker = get_cost_tracker()

    # ... LLM call ...

    input_tokens = tracker.count_tokens(prompt)
    output_tokens = tracker.count_tokens(response.content)

    tracker.track_agent_call(
        "synthesis",
        "gpt-4",
        input_tokens,
        output_tokens,
    )

    state["cost_estimate"] = tracker.get_summary()["total_cost"]
    state["tokens_used"] = tracker.get_summary()["total_input_tokens"]

    return state
```

### Files to Create/Modify
- `agents/utils/cost_tracker.py`
- `agents/requirements.txt` (add `tiktoken`)

---


ISSUE_46_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Cost Tracking - Token Counting + Cost Estimation Per Query" \
  --body "$ISSUE_BODY_46" \
  --label "agents" --label "priority:medium" \
  --milestone "M4")

echo "Created: Cost Tracking - Token Counting + Cost Estimation Per Query -> $ISSUE_URL"
sleep 1

# Issue #47: End-to-End Integration Testing
ISSUE_BODY_47=$(cat <<'ISSUE_47_EOF'
### Description
Write comprehensive end-to-end tests: user registration, session creation, context upload, query execution, artifact generation. Uses test fixtures and mocked APIs.

### Acceptance Criteria
- [ ] pytest fixtures for client, DB, mock APIs
- [ ] Test user registration and login flow
- [ ] Test session CRUD operations
- [ ] Test document/URL ingestion
- [ ] Test full query orchestration (mocked agents)
- [ ] Test artifact generation
- [ ] Test WebSocket message flow
- [ ] Coverage: 70% minimum

### Implementation Details
backend/tests/conftest.py:
```python
import pytest
from fastapi.testclient import TestClient
from app.core.app import create_app
from motor.motor_asyncio import AsyncClient
import mongomock_motor
from unittest.mock import patch, AsyncMock

@pytest.fixture
async def app():
    """Create test app"""
    app = create_app()
    return app

@pytest.fixture
def client(app):
    """Test client"""
    return TestClient(app)

@pytest.fixture
async def db():
    """Mock MongoDB"""
    client = mongomock_motor.AsyncClient()
    return client["test_db"]

@pytest.fixture
def auth_token():
    """Test auth token"""
    return "test-token-12345"

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "name": "Test User",
    }
```

backend/tests/test_integration.py:
```python
import pytest

@pytest.mark.asyncio
async def test_user_registration(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json=test_user,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]

@pytest.mark.asyncio
async def test_login_flow(client, test_user):
    # Register
    client.post("/api/v1/auth/register", json=test_user)

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
        },
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

@pytest.mark.asyncio
async def test_create_session(client, auth_token):
    response = client.post(
        "/api/v1/sessions",
        json={"title": "Test Session", "description": "E2E Test"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Test Session"

@pytest.mark.asyncio
async def test_full_query_flow(client, auth_token):
    # Create session
    session_resp = client.post(
        "/api/v1/sessions",
        json={"title": "Query Test"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    session_id = session_resp.json()["id"]

    # Send query
    query_resp = client.post(
        "/api/v1/chat/messages",
        json={
            "session_id": session_id,
            "query": "What are the latest market trends?",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert query_resp.status_code == 200
    message_id = query_resp.json()["message_id"]
    assert message_id is not None
```

### Files to Create/Modify
- `backend/tests/conftest.py`
- `backend/tests/test_integration.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_sessions.py`
- `backend/requirements.txt` (add pytest, pytest-asyncio)

---


ISSUE_47_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "End-to-End Integration Testing" \
  --body "$ISSUE_BODY_47" \
  --label "testing" --label "priority:high" \
  --milestone "M4")

echo "Created: End-to-End Integration Testing -> $ISSUE_URL"
sleep 1

# Issue #48: Error Handling Hardening - Circuit Breakers, Timeouts, Graceful Degradation
ISSUE_BODY_48=$(cat <<'ISSUE_48_EOF'
### Description
Harden error handling across the system: circuit breakers for external APIs, request timeouts, fallback strategies, partial result aggregation.

### Acceptance Criteria
- [ ] Circuit breaker pattern for all external API calls
- [ ] Timeout on all async operations (default 30s)
- [ ] Graceful degradation when agents fail (continue with partial results)
- [ ] Error aggregation in synthesis (show which agents failed)
- [ ] Retry logic with exponential backoff
- [ ] User-friendly error messages

### Implementation Details
backend/app/core/resilience.py:
```python
from functools import wraps
import asyncio
from datetime import datetime, timedelta
from app.core.logger import get_logger

logger = get_logger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("circuit_breaker_opened")

    def record_success(self):
        self.failure_count = 0
        self.is_open = False

    def can_execute(self) -> bool:
        if not self.is_open:
            return True

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        if elapsed > self.recovery_timeout:
            self.is_open = False
            self.failure_count = 0
            logger.info("circuit_breaker_recovered")
            return True

        return False

def with_circuit_breaker(name: str, threshold: int = 5):
    """Decorator for circuit breaker protection"""

    breaker = CircuitBreaker(failure_threshold=threshold)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not breaker.can_execute():
                raise Exception(f"Circuit breaker open for {name}")

            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
        return wrapper
    return decorator

def with_timeout(seconds: int = 30):
    """Decorator for operation timeout"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error("operation_timeout", function=func.__name__, timeout_seconds=seconds)
                raise Exception(f"Operation timeout after {seconds} seconds")
        return wrapper
    return decorator
```

In orchestrator:
```python
async def run_agent_safely(agent_func, state, agent_name):
    """Run agent with fallback"""

    try:
        result = await asyncio.wait_for(agent_func(state), timeout=60)
        return {
            "status": "completed",
            "result": result,
            "error": None,
        }
    except asyncio.TimeoutError:
        logger.error("agent_timeout", agent=agent_name)
        return {
            "status": "timeout",
            "result": None,
            "error": f"Agent {agent_name} timed out",
        }
    except Exception as e:
        logger.error("agent_failed", agent=agent_name, error=str(e))
        return {
            "status": "failed",
            "result": None,
            "error": str(e),
        }
```

### Files to Create/Modify
- `backend/app/core/resilience.py`
- `agents/orchestrator/graph.py` (update to use safe agent execution)

---


ISSUE_48_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Error Handling Hardening - Circuit Breakers, Timeouts, Graceful Degradation" \
  --body "$ISSUE_BODY_48" \
  --label "backend" --label "agents" --label "priority:high" \
  --milestone "M4")

echo "Created: Error Handling Hardening - Circuit Breakers, Timeouts, Graceful Degradation -> $ISSUE_URL"
sleep 1

# Issue #49: Docker Production Setup + Deployment Config
ISSUE_BODY_49=$(cat <<'ISSUE_49_EOF'
### Description
Create production-grade Docker setup: multi-stage builds, health checks, environment configs, docker-compose.prod.yml, Kubernetes manifests (optional).

### Acceptance Criteria
- [ ] Production Dockerfile for each service (frontend, backend, agents)
- [ ] Multi-stage builds to minimize images
- [ ] Health check endpoints configured
- [ ] docker-compose.prod.yml with prod services
- [ ] Environment variable templates (.env.prod)
- [ ] Volume persistence for MongoDB, Qdrant
- [ ] Network isolation between services
- [ ] Secrets management (API keys, JWT secret)

### Implementation Details
backend/Dockerfile.prod:
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

# Copy app code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

frontend/Dockerfile.prod:
```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

docker-compose.prod.yml:
```yaml
version: '3.9'

services:
  mongodb:
    image: mongo:6.0
    container_name: vector-agents-mongo
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_prod_data:/data/db
    networks:
      - vector-agents
    healthcheck:
      test: echo 'db.runCommand("ping").ok'
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    container_name: vector-agents-qdrant
    restart: always
    environment:
      QDRANT_API_KEY: ${QDRANT_API_KEY}
    volumes:
      - qdrant_prod_data:/qdrant/storage
    networks:
      - vector-agents
    ports:
      - "6333:6333"

  redis:
    image: redis:7-alpine
    container_name: vector-agents-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_prod_data:/data
    networks:
      - vector-agents

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: vector-agents-backend
    restart: always
    environment:
      APP_ENV: production
      MONGO_URI: mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/vector-agents?authSource=admin
      QDRANT_URL: http://qdrant:6333
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      mongodb:
        condition: service_healthy
      qdrant:
        condition: service_started
      redis:
        condition: service_started
    networks:
      - vector-agents
    expose:
      - "8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: vector-agents-frontend
    restart: always
    depends_on:
      - backend
    networks:
      - vector-agents
    ports:
      - "80:80"

  nginx:
    image: nginx:alpine
    container_name: vector-agents-proxy
    restart: always
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - frontend
      - backend
    networks:
      - vector-agents

volumes:
  mongo_prod_data:
    driver: local
  qdrant_prod_data:
    driver: local
  redis_prod_data:
    driver: local

networks:
  vector-agents:
    driver: bridge
```

.env.prod.example:
```
APP_ENV=production
DEBUG=false

MONGO_URI=mongodb://admin:password@mongodb:27017/vector-agents
MONGO_PASSWORD=your_mongo_password

QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=your_qdrant_key

REDIS_URL=redis://:your_redis_password@redis:6379
REDIS_PASSWORD=your_redis_password

JWT_SECRET_KEY=your_jwt_secret_key_here_at_least_32_chars

OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=...
SERPAPI_API_KEY=...

CORS_ORIGINS=https://yourdomain.com

OTEL_ENABLED=true
```

nginx.conf:
```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name _;

    # Redirect to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /api/v1/ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Files to Create/Modify
- `backend/Dockerfile.prod`
- `frontend/Dockerfile.prod`
- `docker-compose.prod.yml`
- `.env.prod.example`
- `nginx.conf`

---


ISSUE_49_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Docker Production Setup + Deployment Config" \
  --body "$ISSUE_BODY_49" \
  --label "infra" --label "priority:high" \
  --milestone "M4")

echo "Created: Docker Production Setup + Deployment Config -> $ISSUE_URL"
sleep 1

# Issue #50: Project Documentation - README, API Docs, Architecture Guide
ISSUE_BODY_50=$(cat <<'ISSUE_50_EOF'
### Description
Create comprehensive project documentation: README with setup instructions, API documentation (OpenAPI/Swagger), architecture guide, agent design doc, troubleshooting guide.

### Acceptance Criteria
- [ ] README.md with project overview, features, quick start
- [ ] ARCHITECTURE.md explaining system design
- [ ] API_DOCS.md or Swagger UI at /docs
- [ ] AGENTS.md explaining domain agents and tools
- [ ] DEPLOYMENT.md with production setup guide
- [ ] TROUBLESHOOTING.md with common issues
- [ ] CONTRIBUTING.md for development guidelines

### Implementation Details
Create root-level docs/ directory with:

docs/README.md:
```markdown
# Vector Agents Documentation

## Table of Contents
- [Project Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Reference](#api)
- [Agents Guide](#agents)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Overview
Vector Agents is an AI-powered growth intelligence platform...

[Full documentation structure and content]
```

docs/ARCHITECTURE.md:
```markdown
# System Architecture

## Components
1. **Frontend (React SPA)** - User interface with real-time updates
2. **Backend (FastAPI)** - REST API, WebSocket server, document processing
3. **Agents (LangGraph)** - Multi-agent orchestrator with 6 domain agents
4. **Data Layer** - MongoDB, Qdrant, Redis

## Data Flow
[Diagram showing query flow through system]

## Key Design Decisions
[Explanations of architecture choices]
```

In main FastAPI app:
```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Vector Agents API",
        version="1.0.0",
        description="Market intelligence platform API",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Files to Create/Modify
- `README.md` (root)
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AGENTS.md`
- `docs/DEPLOYMENT.md`
- `docs/TROUBLESHOOTING.md`
- `CONTRIBUTING.md`

---

## END OF 50 ISSUES

ISSUE_50_EOF
)

ISSUE_URL=$(gh issue create -R "$REPO" \
  --title "Project Documentation - README, API Docs, Architecture Guide" \
  --body "$ISSUE_BODY_50" \
  --label "documentation" --label "priority:medium" \
  --milestone "M4")

echo "Created: Project Documentation - README, API Docs, Architecture Guide -> $ISSUE_URL"
sleep 1

echo ""
echo "All 50 issues created successfully!"
