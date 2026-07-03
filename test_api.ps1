$log = "D:\backend\server.log"
$proc = Start-Process -NoNewWindow -FilePath python -ArgumentList "run.py" -PassThru -RedirectStandardOutput $log -RedirectStandardError $log
Start-Sleep -Seconds 6
Write-Host "Server PID: $($proc.Id)"
try {
    $r = Invoke-RestMethod -Uri "http://localhost:8003/asesores/login" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"codigo_empleado":"ADMIN","password":"123456"}'
    Write-Host "Login OK: access_token=$($r.access_token)"
    # Test a GET endpoint
    $token = $r.access_token
    $headers = @{"Authorization" = "Bearer $token"}
    $dash = Invoke-RestMethod -Uri "http://localhost:8003/cartera/dashboard" -Method Get -Headers $headers
    Write-Host "Dashboard OK: $($dash | ConvertTo-Json -Compress)"
} catch {
    Write-Host "API Error: $_"
    Get-Content $log -Tail 20
}
# Leave server running
Write-Host "Server is running on port 8003"
