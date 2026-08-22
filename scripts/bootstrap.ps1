$ErrorActionPreference = "Stop"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 scripts/bootstrap.py @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python scripts/bootstrap.py @args
} else {
    throw "Python 3.11+ is required. Install Python and enable it on PATH."
}
