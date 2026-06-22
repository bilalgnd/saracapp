# SaracApp Project Rules

**Rule 1: Build Outputs**
- Compiled EXEs and APKs MUST ALWAYS be placed in `C:\Users\bilal\SARACAPP\0-versions`.
- The output files MUST be named `saracappX.X.X.exe` and `saracappX.X.X.apk` (replacing X.X.X with the current version).

**Rule 2: Versioning**
- Every update must increment the version number.
- The version string (e.g., `v4.3.3`) MUST be updated automatically across App1 (Python PC App), App2 (Android Kotlin App), and Web (HTML frontend). This includes UI headers, `build.gradle.kts`, and any config files.

**Rule 3: Clean Directory Structure**
- The `SARACAPP` root directory must ONLY contain the absolutely necessary files for running/building the app.
- All backup files, fix scripts, and utility tools must be stored in a subfolder named `tools/`.
- Temporary build directories like `build/`, `dist/`, and `__pycache__/` must be cleaned up after compilations or configured to output elsewhere so they do not clutter the root folder.

**Rule 4: Unified Monorepo & Naming Conventions**
- The Android project (App2) must reside INSIDE the `SARACAPP` root directory (e.g., `SARACAPP/android_app/`).
- Python files should be named professionally (e.g., `server.py` -> `saracapp_server.py`).
- **Code Language Policy**: All variable names, function names, and structural code must be in ENGLISH (`kalemler` -> `items`, `siparisler` -> `orders`).
- ONLY user-facing UI text elements (labels, buttons, printed receipts) should remain in Turkish.

**Rule 5: UI Modernization & Performance**
- The Tkinter/CustomTkinter UI must be optimized to prevent sluggishness.
- It must scale properly across different screen resolutions and monitor sizes.
- Avoid bulky, monolithic logic in the UI loop that blocks rendering.

**Rule 6: Daily Backup Protocol**
- Provide a mechanism to backup the entire `SARACAPP` folder with the current date.
- This backup should ONLY be triggered when the user explicitly says "gün sonu yedeği al" (take end-of-day backup).

**Rule 7: Step-by-Step Execution**
- Major architectural changes must be done incrementally, one step at a time, checking for stability at each step before moving on. Do not attempt monolithic, all-at-once refactors.
