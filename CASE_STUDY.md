# PathLedger
## Windows Archive Compatibility Audit

### Context and business problem
Archive migrations can fail when file names, path lengths and application encoding assumptions differ between older software and a newer Windows environment. The practical need is a tool that can inspect actual inputs, preserve the source, and produce evidence that another person can review.

### Delivered solution
A working, read-only C++17 utility that inspects real folders, identifies covered Windows path risks and exports an actionable compatibility report.

- Recursive filesystem audit with symlink boundaries and scan limits
- Windows reserved names, invalid characters, trailing dots/spaces and ASCII case/trim conflicts
- Projected legacy path-length checks and explicit Unicode review findings
- Local dashboard with downloadable JSON, CSV and standalone HTML reports

### A complete working flow
Real local directory → C++17 read-only enumeration → compatibility rules → review dashboard → JSON / CSV / HTML report.

The interface calls a real compiled executable for each analysis. Results are not hardcoded. Users can replace the bundled fixture with their own directory or log path. Exports are generated from the latest successful analysis.

### Engineering decisions
- C++17 standard-library implementation without external runtime libraries.
- Read-only access to original inputs; generated reports stay in the project's runtime directory.
- Explicit data limits, descriptive input errors, and visible partial-result conditions.
- Python binds only to the loopback interface; Host and Origin checks protect browser requests.
- UI text is escaped; exported HTML is escaped; CSV fields that resemble spreadsheet formulas are prefixed safely.

### What was verified
Compiled with Apple clang++ in C++17 mode with no warnings. Nine engine tests and six live HTTP checks passed. The bundled archive produced 3 blocking findings, 1 path warning and 1 Unicode review item. See TEST_RESULTS.md and executable tests for exact coverage.

### Accurate positioning
Independent new modernization-support tool; no historical client migration is claimed. Windows execution and MSVC compilation are not verified. ASCII case comparison is not full Windows Unicode case folding. Long-path checking assumes C:\Archive\; application-specific Windows validation remains required.

This project demonstrates modernization-support engineering. It is not represented as a completed port of a pre-existing customer application. All bundled example data is explicitly synthetic; the software itself processes real user inputs.

### Deliverables
- C++ source and CMake configuration
- Local Python dashboard with a start script
- Input fixtures and executable tests
- CSV, JSON and HTML export routes
- Case study, verification record and screenshot captions
- Actual browser screenshots added during final packaging
