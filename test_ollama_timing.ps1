$systemPrompt = 'You are a security researcher generating a REALISTIC simulated Windows event log excerpt. Generate 6-10 plausible Windows Security event log lines depicting a junction/reparse point attack against mpengine.dll (CVE-2026-50656). Respond ONLY with valid JSON in this structure: {"scenario_name": "...", "log_lines": ["...", "..."]}'

$body = @{
    model = "qwen2.5-coder:7b-instruct-q4_0"
    messages = @(
        @{ role = "system"; content = $systemPrompt },
        @{ role = "user"; content = "Generate the simulated log excerpt now." }
    )
    stream = $false
    format = "json"
} | ConvertTo-Json -Depth 10

Measure-Command {
    Invoke-RestMethod -Uri "http://localhost:11434/api/chat" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 240
}