$log = "D:\backend\server.log"
# Kill any existing python on port 8003
Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
# Start server
$p = Start-Process -NoNewWindow -FilePath python -ArgumentList "D:\backend\run.py" -PassThru -RedirectStandardOutput $log -RedirectStandardError "D:\backend\server_err.log"
Start-Sleep -Seconds 6
Write-Host "Server PID: $($p.Id)"
try {
    $r = Invoke-RestMethod -Uri "http://localhost:8003/auth/login" -Method Post -ContentType "application/json" -Body '{"codigo_empleado":"ADMIN","password":"123456"}'
    Write-Host "Login OK: token=$($r.token)"
    $headers = @{Authorization = "Bearer $($r.token)"}
    $dash = Invoke-RestMethod -Uri "http://localhost:8003/cartera/dashboard" -Method Get -Headers $headers
    Write-Host "Dashboard OK: $(($dash | ConvertTo-Json -Compress).Substring(0, [Math]::Min(200, ($dash | ConvertTo-Json -Compress).Length)))"
    $health = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method Get
    Write-Host "Health OK: $($health | ConvertTo-Json -Compress)"
} catch {
    Write-Host "API Error: $_"
    if (Test-Path $log) { Write-Host "=== Server Log ==="; Get-Content $log -Tail 20 }
    if (Test-Path "D:\backend\server_err.log") { Write-Host "=== Error Log ==="; Get-Content "D:\backend\server_err.log" -Tail 20 }
}
Write-Host "Server running on port 8003"
