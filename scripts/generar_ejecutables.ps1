param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$raizProyecto = Split-Path -Parent $PSScriptRoot

if ($env:OS -ne "Windows_NT") {
    throw "Los ejecutables de Windows deben compilarse en Windows."
}

# Resuelve el interprete antes de cambiar de carpeta.
$interpreteProyecto = (Get-Command $Python -ErrorAction Stop).Source
$carpetaEjecutables = Join-Path $raizProyecto "ejecutables"
$carpetaCompilacion = Join-Path $raizProyecto "build"
New-Item -ItemType Directory -Path $carpetaEjecutables -Force | Out-Null
New-Item -ItemType Directory -Path $carpetaCompilacion -Force | Out-Null

Push-Location $raizProyecto
try {
    & $interpreteProyecto -m PyInstaller --version
    if ($LASTEXITCODE -ne 0) {
        throw "Instala PyInstaller con el mismo Python antes de compilar."
    }

    $aplicaciones = @(
        @{ Nombre = "Juego21"; Entrada = "juego-21/interfaz.py" },
        @{ Nombre = "Misioneros-Canibales"; Entrada = "misioneros-canibales/main.py" }
    )

    foreach ($aplicacion in $aplicaciones) {
        Write-Host "Compilando $($aplicacion.Nombre)..."
        & $interpreteProyecto -m PyInstaller --noconfirm --clean --onefile --windowed `
            --name $aplicacion.Nombre --distpath $carpetaEjecutables `
            --workpath $carpetaCompilacion --specpath $carpetaCompilacion `
            $aplicacion.Entrada
        if ($LASTEXITCODE -ne 0) {
            throw "No se pudo compilar $($aplicacion.Nombre)."
        }
    }

    Write-Host "Ejecutables disponibles en $carpetaEjecutables"
}
finally {
    Pop-Location
}
