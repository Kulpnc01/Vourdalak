@echo off
:: This is a tiny "baton" that immediately hands control to native ARM64 PowerShell
powershell.exe -ExecutionPolicy Bypass -File "%~dp0vourdalak.ps1" %*
