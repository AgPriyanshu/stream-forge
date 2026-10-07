# StreamForge

A minimal backend project for learning modern API, messaging, streaming, and object-storage technologies by building a small system from scratch.

A small project to learn the core technologies used in SkanAI's backend
architecture by building a minimal system from scratch.

## Goal

Understand how these components fit together in a real backend system:

-   FastAPI
-   Apache APISIX + etcd
-   PostgreSQL + RLS
-   PostgREST
-   RabbitMQ
-   Pushpin
-   Bento
-   fsspec + object storage

**Flink CDC / StarRocks are intentionally out of scope for now.**

## Project

Build a simple **multi-tenant document processing service**.

### Core flow

``` text
Client
  |
  v
APISIX
  |
  +----> FastAPI
  |        |
  |        +----> PostgreSQL
  |        |
  |        +----> RabbitMQ
  |
  +----> PostgREST ---> PostgreSQL

RabbitMQ
  |
  v
Bento
  |
  v
Object Storage

Pushpin
  |
  v
Client (SSE/WebSocket)
```

## Scope

### 1. FastAPI

-   Create document API
-   List/get documents
-   Trigger document processing
-   Tenant-aware requests

### 2. PostgreSQL

-   Tenants
-   Users
-   Documents
-   Processing jobs
-   PostgreSQL Row-Level Security

### 3. PostgREST

-   Expose selected PostgreSQL data through PostgREST
-   Compare PostgREST APIs with FastAPI APIs

### 4. APISIX + etcd

-   Route requests to FastAPI and PostgREST
-   Learn upstreams, routes and configuration
-   Understand how etcd stores APISIX configuration

### 5. RabbitMQ

-   Publish document-processing jobs
-   Implement a basic claim-check pattern
-   Learn exchanges, queues, routing keys and acknowledgements

### 6. Bento

-   Consume messages
-   Perform a small processing pipeline
-   Publish the result/event

### 7. Object Storage + fsspec

-   Store uploaded files
-   Read/write files through fsspec
-   Start with MinIO locally

### 8. Pushpin

-   Send processing status updates to clients
-   Start with SSE
-   Understand where Pushpin fits between clients and backend services

## Non-Goals

Do not add these initially:

-   StarRocks
-   Flink CDC
-   Kubernetes
-   Terraform
-   Cloud deployment
-   Authentication provider
-   Complex frontend
-   Production-grade document processing

## Learning Rules

-   Build everything manually.
-   No AI-generated implementation.
-   Prefer official documentation.
-   Add one technology at a time.
-   Keep the application intentionally small.
-   Write notes about **why** each component exists.
-   Avoid abstractions until they are needed.

## Suggested Order

1.  PostgreSQL + RLS
2.  FastAPI
3.  PostgREST
4.  RabbitMQ
5.  Object storage + fsspec
6.  Bento
7.  APISIX + etcd
8.  Pushpin
9.  Integrate everything

## Success Criteria

The project is complete when a tenant can:

1.  Upload a document.
2.  Store its metadata in PostgreSQL.
3.  Store the file in object storage.
4.  Trigger asynchronous processing through RabbitMQ.
5.  Process the job through Bento.
6.  Receive processing status through SSE.
7.  Access tenant-isolated data through both FastAPI and PostgREST.
8.  Reach the services through APISIX.
