# debug_android.ps1
# Script para facilitar la depuración de Kivy/Python en Android
# Uso: .\debug_android.ps1

$PACKAGE_NAME = "com.baxner.tiktokbattle"

Write-Host "📱 Buscando dispositivos Android..." -ForegroundColor Cyan
$adbOutput = adb devices
$adbOutput | Write-Host

# Filtrar líneas vacías y la cabecera
# Buscamos líneas que terminen en "device" (indicando conectado y autorizado)
$connectedDevices = $adbOutput | Where-Object { $_ -match "\tdevice$" -or $_ -match "\sdevice$" }

if (-not $connectedDevices) {
    Write-Host "⚠️ NO SE DETECTÓ NINGÚN DISPOSITIVO." -ForegroundColor Red
    Write-Host "   1. Conecta tu celular por USB." -ForegroundColor Yellow
    Write-Host "   2. Acepta la notificación 'Depuración USB' en tu pantalla." -ForegroundColor Yellow
    Write-Host "   3. Asegúrate que tienes los drivers instalados." -ForegroundColor Yellow
    
    # Check for unauthorized (connected but not allowed)
    if ($adbOutput -match "unauthorized") {
        Write-Host "⚠️ DISPOSITIVO NO AUTORIZADO: Mira la pantalla de tu celular y acepta la conexión." -ForegroundColor Red
    }
    
    exit
}

Write-Host "✅ Dispositivo encontrado." -ForegroundColor Green
Write-Host "🧹 Limpiando logs antiguos..." -ForegroundColor Yellow
adb logcat -c

Write-Host "🚀 Intentando iniciar App ($PACKAGE_NAME)..." -ForegroundColor Green

# Intentar lanzar la app
$monkeyOutput = adb shell monkey -p $PACKAGE_NAME -c android.intent.category.LAUNCHER 1
if ($monkeyOutput -match "No activities found") {
    Write-Host "❌ ERROR: La aplicación no parece estar instalada." -ForegroundColor red
    Write-Host "   1. Asegúrate de haber instalado el APK generado." -ForegroundColor Yellow
    Write-Host "   2. Si no lo has instalado, usa: adb install -r nombre_del_archivo.apk" -ForegroundColor Yellow
    exit
}

Write-Host "📜 Filtrando logs (Python + Kivy)..." -ForegroundColor Green
Write-Host "   (Presiona Ctrl+C para salir)" -ForegroundColor Gray

# Usar array de argumentos para evitar problemas de parsing en PowerShell
$logcatArgs = @(
    "logcat",
    "-v", "color",
    "python:D",
    "Pylib:D",
    "$($PACKAGE_NAME):D",
    "AndroidRuntime:E",
    "*:E"  # Mostrar TODOS los errores del sistema (para ver crashes nativos)
)

# Ejecutar adb directamente
& adb $logcatArgs
