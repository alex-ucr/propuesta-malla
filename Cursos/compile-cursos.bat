@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem Run from the parent of this folder so Biblio.bib and preamble-body.tex resolve
cd /d "%~dp0\.."
if not exist "Cursos" (
  echo Cursos folder not found next to this script. >&2
  exit /b 1
)
where latexmk >nul 2>&1
if errorlevel 1 (
  echo latexmk not on PATH. Install MiKTeX/TeX Live and ensure the bin directory is in PATH. >&2
  exit /b 1
)

set "FAILED=0"
for /f "delims=" %%F in ('dir /b "Cursos\*.tex" 2^>nul ^| findstr /v /i "cuerpo"') do (
  echo.
  echo ===== Compiling Cursos\%%F =====
  latexmk -pdf -interaction=nonstopmode -f "Cursos\%%F"
  if errorlevel 1 set "FAILED=1"
)
echo.
if !FAILED! equ 0 (
  echo All Cursos non-cuerpo drivers built successfully.
  exit /b 0
) else (
  echo One or more builds failed.
  exit /b 1
)
