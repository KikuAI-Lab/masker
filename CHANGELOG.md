# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-29

### Added
- **Rate Limiting**: Added token bucket rate limiter (60 req/min per IP, 1000 req/min global).
- **Entity Filtering**: Added ability to filter specific PII types (e.g., only EMAIL).
- **RapidAPI Endpoint**: Unified `/v1/redact` endpoint optimized for RapidAPI integration.
- **Health Check**: Enhanced `/health` endpoint with uptime and component status.
- **Documentation**: Added comprehensive RapidAPI readiness guide.

### Changed
- **API Structure**: Refactored to support both text and JSON input modes in all endpoints.
- **Performance**: Optimized PII detection with regex priority over NER.
- **Logging**: Enhanced structured logging with request IDs and processing time.

### Fixed
- **Entity Filtering**: Fixed bug where entity filter was ignored in detection logic.
- **JSON Processing**: Fixed recursive JSON processing to correctly handle nested structures.

## [0.1.0] - 2025-11-01

### Added
- Initial release of Masker API.
- Basic PII detection (EMAIL, PHONE, CARD, PERSON).
- Text and JSON masking support.
- Docker support.
