# ADR-001: Modular Monolith with Decoupled SPA

## Status
Accepted

## Context
Building a full-stack examination system in 10 hours for a hackathon. Need to maximize development speed while maintaining clear separation of concerns and security boundaries.

## Decision
Modular monolith backend (FastAPI) + decoupled SPA frontend (React).

## Rationale
- Single deployable backend unit avoids microservice coordination overhead
- FastAPI async support handles concurrent exam attempts efficiently
- React SPA provides rich interactive exam workspace without page reloads
- Clear module boundaries within the monolith enable parallel development
- PostgreSQL provides ACID transactions for grade and dispute integrity

## Consequences
- Backend modules can be extracted to microservices later if needed
- All business logic lives in one deployable unit — simpler ops for a 10-hour hackathon
- Frontend and backend teams work independently against agreed API contracts
