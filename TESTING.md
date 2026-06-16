# NeuralRadar v0.1-alpha Manual Testing Checklist

Use this checklist to perform manual quality assurance before finalizing a release build.

## Core Setup
- [ ] **Virtual environment setup**: Verify `venv` creation and activation works correctly across Windows and Linux.
- [ ] **Requirements install**: Ensure `pip install -r requirements.txt` succeeds and pulls necessary packages (`PySide6`, `loguru`, `SQLAlchemy`, `requests`).
- [ ] **App startup**: Run `python app/main.py`. The GUI should launch without console errors, and the window title should display the current version.

## IPHawk (Network Discovery)
- [ ] **IPHawk scanning**: Input a valid local subnet and click `Start Scan`. Verify hosts populate.
- [ ] **IPHawk Stop Scan**: Click `Stop Scan` mid-scan. The scanning should halt gracefully.
- [ ] **Save IPHawk results to DeviceVault**: Select hosts and click `Save Results to DeviceVault`. Verify confirmation prompt appears.

## DeviceVault (Asset Inventory)
- [ ] **DeviceVault view**: Open DeviceVault and verify saved devices from IPHawk appear.
- [ ] **DeviceVault editing**: Edit a device's details manually (e.g. name or override) and save.
- [ ] **DeviceVault persistence after restart**: Close and reopen NeuralRadar. Verify devices and their manual edits are retained.

## PortScope (TCP Port Discovery)
- [ ] **PortScope scanning**: Scan a target device from the DeviceVault list.
- [ ] **PortScope Stop Scan**: Stop the scan mid-way.
- [ ] **Save PortScope results to DeviceVault**: Save discovered open ports. Verify they attach to the correct device in DeviceVault.

## WebPulse (Web Service Checks)
- [ ] **WebPulse checks**: Input a valid URL and start check.
- [ ] **WebPulse Stop Check**: Stop a check before it completes.
- [ ] **WebPulse failed-result toggle**: Use the checkbox to toggle visibility of failed web checks.
- [ ] **WebPulse TLS Warning**: Test an endpoint with a valid but slightly misconfigured/expiring certificate to trigger warning.
- [ ] **WebPulse TLS/SNI Error**: Test an endpoint with invalid certs to trigger an error.
- [ ] **WebPulse Protocol Mismatch**: Test HTTP over HTTPS port or vice versa.
- [ ] **Save WebPulse results to DeviceVault**: Save results and verify they persist in the DeviceVault properly.

## General
- [ ] **Regression checks for all modules**: Navigate through all tabs (Dashboard, Settings, etc.) while scans are running to verify UI stability.
