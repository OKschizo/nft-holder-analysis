@echo off
echo Starting NFT Holder Analysis Dashboard...
echo.
streamlit run dashboard.py
if errorlevel 1 (
    echo.
    echo Error occurred! Press any key to close...
    pause >nul
)

