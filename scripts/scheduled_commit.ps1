<#
.SYNOPSIS
  Faz um commit agendado, só se o stage for exatamente o esperado.

.DESCRIPTION
  Pensado para rodar pelo Agendador de Tarefas do Windows (limite de 4 commits por
  dia). O job fica numa pasta com:
    message.txt   mensagem do commit (header + corpo)
    expected.txt  saída esperada de `git diff --cached --name-status`, uma linha por arquivo
  O resultado vai para run.log na mesma pasta. Nunca faz push.

  Sai 0 quando o commit foi feito. Sai 1 quando o stage diverge, nada está staged
  ou o commit falha. Nesses casos, nada é commitado.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File scheduled_commit.ps1 `
    -Repo C:\...\consolidator -JobDir $env:LOCALAPPDATA\mywallet-scheduled-commits\consolidator-003
#>
param(
    [Parameter(Mandatory = $true)][string]$Repo,
    [Parameter(Mandatory = $true)][string]$JobDir,
    [string]$Git = "C:\Program Files\Git\mingw64\bin\git.exe"
)

$ErrorActionPreference = "Stop"
$log = Join-Path $JobDir "run.log"

function Write-Log([string]$msg) {
    $line = "{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $log -Value $line -Encoding UTF8
}

function Normalize([string[]]$lines) {
    return @($lines | ForEach-Object { ($_ -replace "\s+", " ").Trim() } | Where-Object { $_ -ne "" } | Sort-Object)
}

try {
    Write-Log "Início. Repo: $Repo"
    $messageFile = Join-Path $JobDir "message.txt"
    $expectedFile = Join-Path $JobDir "expected.txt"
    foreach ($f in @($messageFile, $expectedFile)) {
        if (-not (Test-Path $f)) { Write-Log "ERRO: arquivo ausente: $f"; exit 1 }
    }

    $actual = Normalize (& $Git -C $Repo diff --cached --name-status)
    $expected = Normalize (Get-Content -Path $expectedFile -Encoding UTF8)

    if ($actual.Count -eq 0) { Write-Log "ABORTADO: nada staged."; exit 1 }

    $diff = Compare-Object -ReferenceObject $expected -DifferenceObject $actual
    if ($diff) {
        Write-Log "ABORTADO: o stage não é o esperado. Nada foi commitado."
        foreach ($d in $diff) {
            $side = if ($d.SideIndicator -eq "<=") { "esperado, ausente" } else { "staged, inesperado" }
            Write-Log ("  {0}: {1}" -f $side, $d.InputObject)
        }
        exit 1
    }

    # Regrava a mensagem em UTF-8 sem BOM: com BOM, o header do commit começaria com um caractere invisível.
    $text = Get-Content -Path $messageFile -Raw -Encoding UTF8
    $cleanMessage = Join-Path $JobDir "message.nobom.txt"
    [System.IO.File]::WriteAllText($cleanMessage, ($text -replace "`r`n", "`n"), (New-Object System.Text.UTF8Encoding($false)))

    $out = & $Git -C $Repo commit -F $cleanMessage 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERRO no git commit (código $LASTEXITCODE): $out"
        exit 1
    }
    $hash = & $Git -C $Repo log -1 --pretty="%h %ad %s" --date=format:"%Y-%m-%d %H:%M"
    Write-Log "OK: commit $hash"
    exit 0
}
catch {
    Write-Log "ERRO inesperado: $($_.Exception.Message)"
    exit 1
}
