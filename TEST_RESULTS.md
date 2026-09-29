# Verification record — PathLedger

Date: 2026-09-28. Environment: macOS 15.7.8, Python 3.14.7, Apple clang++ with `-std=c++17 -O2 -Wall -Wextra -Wpedantic`.

## Build

Compilation completed successfully with no compiler warnings.

## Automated engine checks

**9 tests passed** with `python3 -m unittest discover -s tests -v`.

- Bundled archive: exact expected error/warning/review counts
- Missing path, ordinary file rejection and empty directory
- External symlink target not traversed; source hash unchanged
- Trailing-name collision and reserved COM/LPT names
- Quotes, newline and backslash JSON escaping
- Unicode name retained without being classified as an error
- Deep tree marked as partially inspected at the depth limit

## Live HTTP checks

**6 tests passed** against the running local dashboard on port 8113: health route, invalid Host rejected, invalid Origin rejected, non-object JSON rejected, missing input rejected, real-engine response and all three download formats returned successfully. Initial network attempts were blocked by the execution sandbox; the same read-only local checks passed after local-network permission was applied.

## Measured fixture result

Compiled with Apple clang++ in C++17 mode with no warnings. Nine engine tests and six live HTTP checks passed. The bundled archive produced 3 blocking findings, 1 path warning and 1 Unicode review item.

## Deliberately unverified

Windows runtime, Visual Studio/MSVC compilation, multi-user deployment, real customer outcomes, unattended production operation, performance under concurrent load and every possible third-party log/filename convention. Browser screenshots and final PDF layout are verified during packaging separately.

## Publication preparation — 2026-09-30

Recompiled C++17 from source without compiler warnings. All 12 unit tests passed (9 engine checks plus 3 fixture checks), followed by all 6 live HTTP checks. The archive fixture now materializes from a portable JSON manifest into ignored runtime storage; its measured result remains 3 blocking findings, 1 warning and 1 Unicode review item. Additional checks confirm exact manifest round-trip/idempotence, existing-file preservation and rejection of symlinked fixture destinations. Windows/MSVC execution remains unverified.
