# Architecture

Browser → same-origin local Python HTTP server → bounded subprocess call → C++17 engine → structured JSON → dashboard and export.

The engine owns the actual analysis. The server validates the input, serializes jobs with a lock, gives each process a 30-second timeout, and writes the latest report into `runtime`. The browser renders escaped values; report exports preserve the latest successful analysis. There is no database, cloud connection or remote service.

The filesystem walker uses std::filesystem with error-code overloads, explicit depth/entry limits and symlink_status to avoid following linked directories. Windows compatibility checks are advisory rule checks, not an emulation of every Windows filesystem or application.

The source is newly authored for this independent project. No upstream code or third-party source license is involved. Microsoft documentation was consulted for Windows path semantics; it is referenced in SOURCES.md where applicable.
