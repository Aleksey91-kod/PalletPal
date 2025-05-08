# build-archive.ps1
# Скрипт для автоматической сборки архива PalletPal

# Создаем временную директорию для сборки
$buildDir = ".\PalletPal"
New-Item -ItemType Directory -Force -Path $buildDir

# Копируем файлы
Copy-Item -Path .\index.html,.\driver.html,.\customer.html,.\styles.css -Destination $buildDir
Copy-Item -Path .\static\* -Destination $buildDir\static\ -Recurse -Force
Copy-Item -Path .\bot.py,.\server.py,.\requirements.txt -Destination $buildDir

# Создаем архив
Compress-Archive -Path $buildDir\* -DestinationPath "PalletPal.zip" -Force

# Удаляем временную директорию
Remove-Item -Path $buildDir -Recurse -Force

Write-Host "Архив PalletPal.zip успешно создан!"