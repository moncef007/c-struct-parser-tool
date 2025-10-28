# Changelog

All notable changes to **C Struct Parser Tool** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-10-28

### Added
- Core `StructParser` class to parse C `typedef struct` definitions from header files
- Support for common C data types: `bool`, `char`, `int8_t`–`int64_t`, `uint8_t`–`uint64_t`, `float`, `double`, pointers
- Automatic struct layout calculation with proper **C alignment and padding**
- Nested struct support (recursive parsing)
- Array handling (1D and multi-dimensional)
- Binary dump extraction at specified offset
- Struct scanning mode with optional hex pattern search
- CLI interface with options for offset, scan, JSON output, and more
- Human-readable and JSON output formats
- Comprehensive test suite covering:
  - Simple and nested structs
  - Padding and alignment edge cases
  - Large structs
  - Arrays of primitives and structs

[0.0.1]: https://github.com/moncef007/c-struct-parser-tool/releases/tag/v0.0.1