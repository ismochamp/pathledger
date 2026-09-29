# PathLedger — Windows Archive Compatibility Audit

**Category:** Legacy Software Modernization  
**Project status:** Independent working project, September 2026. No client engagement or historical production deployment is claimed.

## Short description
A working, read-only C++17 utility that inspects real folders, identifies covered Windows path risks and exports an actionable compatibility report.

## Portfolio description
Archive migrations can fail when file names, path lengths and application encoding assumptions differ between older software and a newer Windows environment.

I built PathLedger to turn this technical uncertainty into a reviewable workflow. A working, read-only C++17 utility that inspects real folders, identifies covered Windows path risks and exports an actionable compatibility report.

- Recursive filesystem audit with symlink boundaries and scan limits
- Windows reserved names, invalid characters, trailing dots/spaces and ASCII case/trim conflicts
- Projected legacy path-length checks and explicit Unicode review findings
- Local dashboard with downloadable JSON, CSV and standalone HTML reports

The implementation combines a compiled C++17 engine with a local Python web interface. Inputs are processed on the user's machine, source files remain unchanged, and the output can be shared as a report.

**Verified evidence:** Compiled with Apple clang++ in C++17 mode with no warnings. Nine engine tests and six live HTTP checks passed. The bundled archive produced 3 blocking findings, 1 path warning and 1 Unicode review item.

**Scope:** Independent new modernization-support tool; no historical client migration is claimed. Windows execution and MSVC compilation are not verified. ASCII case comparison is not full Windows Unicode case folding. Long-path checking assumes C:\Archive\; application-specific Windows validation remains required.

**Skills:** C++17 · debugging · compatibility analysis · filesystem / text processing · Python integration · automated verification

## Screenshot captions
1. The running local workspace accepts a real directory and explains the read-only audit scope.
2. Actual compiled-engine findings from the labeled synthetic archive, with names, rules and next-step guidance.

## Client conversation starter
Are you moving an archive or adapting a file-based Windows application? I can help identify naming and path assumptions before they interrupt the migration.
