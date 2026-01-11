# 🖥️ Терминальные команды: PowerShell vs Git Bash (Windows)

### powershell
```markdown
tt 
tree
tree -all
tt -all
```


---
# 🚀 PowerShell команды для просмотра файлов:
### 1. Простой список всех файлов:
```markdown
Get-ChildItem -Recurse
```
### 2. С дополнительной информацией:
```markdown
Get-ChildItem -Recurse -Force
```
### 3. В виде таблицы:
```markdown
Get-ChildItem -Recurse | Format-Table -AutoSize
```
### 4. Только имена файлов:
```markdown
Get-ChildItem -Recurse -Name
```
### 5. С фильтрацией по расширению:
```markdown
Get-ChildItem -Recurse -Include *.py
```
### 6. Только структура без лишнего:
```markdown
Get-ChildItem -Recurse | Where-Object {
    $_.FullName -notmatch '(__pycache__|\.pytest_cache|\.git|\.idea|\.vscode|venv|env|node_modules|\.pyc$)'
} | ForEach-Object {
    if ($_.PSIsContainer) {
        Write-Host "📁 $($_.FullName)" -ForegroundColor Cyan
    } else {
        # Показываем только важные файлы
        $extensions = @('.py', '.sql', '.json', '.yml', '.yaml', '.md', '.txt', '.html', '.js', '.css', '.dockerfile', '.env')
        if ($extensions -contains $_.Extension.ToLower() -or $_.Name -match '^(docker-compose|requirements|readme|\.env)') {
            Write-Host "📄 $($_.Name)" -ForegroundColor White
        }
    }
}
```
### 🎯 Улучшенная версия с отступами для структуры:
```markdown
function Show-ProjectStructure {
    param(
        [string]$Path = ".",
        [int]$Depth = 0,
        [int]$MaxDepth = 3
    )
    
    $excludePatterns = @(
        '__pycache__',
        '\.pytest_cache',
        '\.git',
        '\.idea',
        '\.vscode',
        'venv',
        'env',
        'node_modules',
        '\.pyc$',
        '\.pyo$',
        '\.pyd$',
        '\.DS_Store$'
    )
    
    $importantExtensions = @(
        '.py', '.sql', '.json', '.yml', '.yaml', '.md', '.txt',
        '.html', '.js', '.css', '.dockerfile', '.env', '.ini',
        '.cfg', '.toml', '.xml', '.csv'
    )
    
    $importantFiles = @(
        'docker-compose', 'requirements', 'readme', '\.env',
        'package\.json', 'setup\.py', 'pyproject\.toml',
        'manage\.py', 'main\.py', 'app\.py'
    )
    
    $items = Get-ChildItem -Path $Path -Force | 
        Where-Object { 
            $isExcluded = $false
            foreach ($pattern in $excludePatterns) {
                if ($_.Name -match $pattern -or $_.FullName -match $pattern) {
                    $isExcluded = $true
                    break
                }
            }
            -not $isExcluded
        } | 
        Sort-Object { $_.PSIsContainer -eq $false }, Name
    
    foreach ($item in $items) {
        $indent = "  " * $Depth
        
        if ($item.PSIsContainer) {
            Write-Host "$indent📁 $($item.Name)" -ForegroundColor Cyan
            if ($Depth -lt $MaxDepth) {
                Show-ProjectStructure -Path $item.FullName -Depth ($Depth + 1) -MaxDepth $MaxDepth
            }
        } else {
            $showFile = $false
            
            # Проверяем расширение
            foreach ($ext in $importantExtensions) {
                if ($item.Extension -eq $ext) {
                    $showFile = $true
                    break
                }
            }
            
            # Проверяем имя файла
            if (-not $showFile) {
                foreach ($pattern in $importantFiles) {
                    if ($item.Name -match $pattern) {
                        $showFile = $true
                        break
                    }
                }
            }
            
            if ($showFile) {
                $size = if ($item.Length -gt 1MB) {
                    "{0:N2} MB" -f ($item.Length / 1MB)
                } elseif ($item.Length -gt 1KB) {
                    "{0:N2} KB" -f ($item.Length / 1KB)
                } else {
                    "{0} B" -f $item.Length
                }
                
                Write-Host "$indent📄 $($item.Name) ($size)" -ForegroundColor White
            }
        }
    }
}

# Использование:
Show-ProjectStructure -Path "D:\Development\Python\Projects" -MaxDepth 4
```


### Метод 2: Функция создания дерева
```markdown
function Show-Tree2 {
    param(
        [string]$Path = ".",
        [string]$Indent = "",
        [switch]$ImportantOnly
    )
    
    # Папки для исключения
    $excludeDirs = @('__pycache__', '.pytest_cache', '.git', '.idea', '.vscode', 'venv', 'env', 'node_modules', '.svn')
    
    # Важные расширения файлов
    $importantExtensions = @('.py', '.sql', '.json', '.yml', '.yaml', '.md', '.txt', '.html', '.css', '.js', 
                           '.dockerfile', '.env', '.ini', '.cfg', '.toml', '.xml', '.csv', '.ps1', '.bat',
                           '.exe', '.pdf', '.zip', '.7z', '.rar')
    
    # Важные имена файлов (даже без подходящего расширения)
    $importantFiles = @('docker-compose', 'requirements', 'readme', 'package', 'setup', 'pyproject',
                       'manage', 'main', 'app', 'config', 'settings', '.env', '.gitignore', '.dockerignore')
    
    $items = Get-ChildItem -Path $Path -Force | 
        Where-Object { 
            # Исключаем папки
            if ($_.PSIsContainer) {
                foreach ($pattern in $excludeDirs) {
                    if ($_.Name -like $pattern) {
                        return $false
                    }
                }
                return $true
            }
            
            # Для файлов
            if ($ImportantOnly) {
                # Проверяем расширение
                $hasImportantExt = $false
                foreach ($ext in $importantExtensions) {
                    if ($_.Extension -eq $ext) {
                        $hasImportantExt = $true
                        break
                    }
                }
                
                # Проверяем имя файла
                $hasImportantName = $false
                foreach ($pattern in $importantFiles) {
                    if ($_.Name -like "$pattern*" -or $_.Name -like "*$pattern*") {
                        $hasImportantName = $true
                        break
                    }
                }
                
                return $hasImportantExt -or $hasImportantName
            }
            
            return $true
        } | 
        Sort-Object { $_.PSIsContainer -eq $false }, Name
    
    $count = $items.Count
    $current = 0
    
    foreach ($item in $items) {
        $current++
        $isLast = $current -eq $count
        
        # Префиксы для дерева
        if ($isLast) {
            $prefix = "└── "
            $nextIndent = $Indent + "    "
        } else {
            $prefix = "├── "
            $nextIndent = $Indent + "│   "
        }
        
        if ($item.PSIsContainer) {
            # Папка
            $folderIcon = "📁"
            
            # Специальные иконки для известных папок
            switch ($item.Name.ToLower()) {
                'docker' { $folderIcon = "🐳" }
                'dbeaver' { $folderIcon = "🗄️" }
                'postman' { $folderIcon = "📮" }
                'python' { $folderIcon = "🐍" }
                'sql' { $folderIcon = "🗃️" }
                'scripts' { $folderIcon = "📜" }
                'data' { $folderIcon = "💾" }
                'images' { $folderIcon = "🖼️" }
                'docs' { $folderIcon = "📚" }
                'tests' { $folderIcon = "🧪" }
                'log' { $folderIcon = "📊" }
                'temp' { $folderIcon = "🗑️" }
            }
            
            Write-Host $Indent$prefix -NoNewline
            Write-Host "$folderIcon " -NoNewline
            Write-Host $item.Name -ForegroundColor Cyan
            
            # Рекурсия для папок
            Show-Tree2 -Path $item.FullName -Indent $nextIndent -ImportantOnly:$ImportantOnly
        } else {
            # Файл
            $icon = switch ($item.Extension.ToLower()) {
                '.py' {'🐍'}
                '.sql' {'🗃️'}
                '.json' {'📋'}
                '.yml' {'⚙️'}
                '.yaml' {'⚙️'}
                '.md' {'📝'}
                '.dockerfile' {'🐳'}
                '.txt' {'📃'}
                '.html' {'🌐'}
                '.css' {'🎨'}
                '.js' {'📜'}
                '.ps1' {'🔧'}
                '.bat' {'📟'}
                '.sh' {'🐚'}
                '.exe' {'⚙️'}
                '.dll' {'🔌'}
                '.zip' {'🗜️'}
                '.7z' {'🗜️'}
                '.rar' {'🗜️'}
                '.pdf' {'📕'}
                '.doc' {'📄'}
                '.docx' {'📄'}
                '.xls' {'📊'}
                '.xlsx' {'📊'}
                '.jpg' {'🖼️'}
                '.jpeg' {'🖼️'}
                '.png' {'🖼️'}
                '.gif' {'🖼️'}
                '.mp3' {'🎵'}
                '.mp4' {'🎬'}
                '.avi' {'🎬'}
                '.mkv' {'🎬'}
                '.iso' {'💿'}
                '.db' {'🗄️'}
                '.sqlite' {'🗄️'}
                '.env' {'🔐'}
                '.gitignore' {'👁️'}
                '.dockerignore' {'👁️'}
                '.yml' {'⚙️'}
                '.yaml' {'⚙️'}
                '.toml' {'⚙️'}
                '.ini' {'⚙️'}
                '.cfg' {'⚙️'}
                '.xml' {'📄'}
                '.csv' {'📊'}
                '.log' {'📋'}
                default {'📄'}
            }
            
            Write-Host $Indent$prefix -NoNewline
            Write-Host "$icon " -NoNewline
            
            # Цвет файла в зависимости от типа
            $color = switch ($item.Extension.ToLower()) {
                '.py' {'Green'}
                '.sql' {'Magenta'}
                '.json' {'Yellow'}
                '.md' {'Gray'}
                '.dockerfile' {'DarkCyan'}
                '.ps1' {'DarkYellow'}
                '.bat' {'DarkGray'}
                '.exe' {'Red'}
                '.zip' {'DarkMagenta'}
                '.7z' {'DarkMagenta'}
                '.rar' {'DarkMagenta'}
                default {'White'}
            }
            
            Write-Host $item.Name -ForegroundColor $color
        }
    }
}

# Использование:
$currentPath = Get-Location | Select-Object -ExpandProperty Path

Write-Host ""
Write-Host "🌳 Структура: " -NoNewline
Write-Host $currentPath -ForegroundColor Yellow
Write-Host "─" * ($currentPath.Length + 12)

# Вариант 1: Только важные файлы (рекомендуется)
Show-Tree2 -Path $currentPath -ImportantOnly
```
### !!!!!!!!!!!!!!!!!!!!Красивый вывод с индикаторами:
```markdown
function Show-Tree {
    param(
        [string]$Path = ".",
        [string]$Indent = "",
        [switch]$ShowFiles
    )
    
    $excludeDirs = @('__pycache__', '.pytest_cache', '.git', '.idea', '.vscode', 'venv', 'env', 'node_modules')
    $excludeFiles = @('*.pyc', '*.pyo', '*.pyd', '.DS_Store')
    
    # Получаем элементы, исключая ненужные
    $items = Get-ChildItem -Path $Path -Force | 
        Where-Object { 
            $isExcluded = $false
            if ($_.PSIsContainer) {
                foreach ($pattern in $excludeDirs) {
                    if ($_.Name -like $pattern) {
                        $isExcluded = $true
                        break
                    }
                }
            } else {
                foreach ($pattern in $excludeFiles) {
                    if ($_.Name -like $pattern) {
                        $isExcluded = $true
                        break
                    }
                }
            }
            -not $isExcluded
        } | 
        Sort-Object { $_.PSIsContainer -eq $false }, Name
    
    $count = $items.Count
    $current = 0
    
    foreach ($item in $items) {
        $current++
        $isLast = $current -eq $count
        
        # Определяем префикс
        if ($isLast) {
            $prefix = "└── "
            $nextIndent = $Indent + "    "
        } else {
            $prefix = "├── "
            $nextIndent = $Indent + "│   "
        }
        
        if ($item.PSIsContainer) {
            # Папки
            Write-Host $Indent$prefix -NoNewline
            Write-Host "📁 " -NoNewline -ForegroundColor Cyan
            Write-Host $item.Name -ForegroundColor Cyan
            
            # Рекурсивно показываем содержимое папки
            Show-Tree -Path $item.FullName -Indent $nextIndent -ShowFiles:$ShowFiles
        } elseif ($ShowFiles) {
            # Файлы только если указан -ShowFiles
            $icon = switch ($item.Extension.ToLower()) {
                '.py' {'🐍'}
                '.sql' {'🗃️'}
                '.json' {'📋'}
                '.yml' {'⚙️'}
                '.yaml' {'⚙️'}
                '.md' {'📝'}
                '.dockerfile' {'🐳'}
                '.txt' {'📃'}
                '.html' {'🌐'}
                '.css' {'🎨'}
                '.js' {'📜'}
                '.exe' {'⚙️'}
                '.bat' {'📟'}
                '.ps1' {'🔧'}
                '.xml' {'📄'}
                '.csv' {'📊'}
                '.zip' {'🗜️'}
                '.7z' {'🗜️'}
                '.rar' {'🗜️'}
                '.pdf' {'📕'}
                '.jpg' {'🖼️'}
                '.png' {'🖼️'}
                '.gif' {'🖼️'}
                '.mp4' {'🎬'}
                '.mp3' {'🎵'}
                default {'📄'}
            }
            
            Write-Host $Indent$prefix -NoNewline
            Write-Host "$icon " -NoNewline
            Write-Host $item.Name -ForegroundColor White
        }
    }
}

# Автоматически определяем текущую папку
$currentPath = Get-Location | Select-Object -ExpandProperty Path

Write-Host ""
Write-Host "Структура: " -NoNewline
Write-Host $currentPath -ForegroundColor Yellow
Write-Host ""

# Запускаем показ структуры с файлами
Show-Tree -Path $currentPath -ShowFiles
```
### С информацией о размерах:
```markdown
Get-ChildItem -Recurse | Select-Object FullName, LastWriteTime, @{Name="SizeKB";Expression={[math]::Round($_.Length/1KB,1)}} | Format-Table -AutoSize
```
### Создать постоянный псевдоним:
```markdown
Set-Alias tree Get-ChildItem -Scope Global
```
### 🎯 Рекомендации для вашего случая:
```markdown
# Покажет все файлы и папки
Get-ChildItem -Recurse

# Покажет только Python файлы с путями
Get-ChildItem -Recurse -Include *.py | Select-Object FullName

# Статистика проекта
Get-ChildItem -Recurse | Measure-Object | Select-Object Count
```
### таблицей
```markdown
Get-ChildItem -Recurse | Where-Object {
    $_.FullName -notmatch '(__pycache__|\.pytest_cache|\.git|\.idea|\.vscode|venv|env|node_modules|\.pyc$)'
} | ForEach-Object {
    if ($_.PSIsContainer) {
        Write-Host "📁 $($_.FullName)" -ForegroundColor Cyan
    } else {
        # Показываем только важные файлы
        $extensions = @('.py', '.sql', '.json', '.yml', '.yaml', '.md', '.txt', '.html', '.js', '.css', '.dockerfile', '.env')
        if ($extensions -contains $_.Extension.ToLower() -or $_.Name -match '^(docker-compose|requirements|readme|\.env)') {
            Write-Host "📄 $($_.Name)" -ForegroundColor White
        }
    }
}
```





## 🔹 1. Навигация по файловой системе

Действие

PowerShell

Git Bash (Bash-стиль)

Перейти в папку

`cd C:pathtofolder`

`cd /c/path/to/folder`

Подняться на уровень выше

`cd ..`

`cd ..`

Вернуться в домашнюю папку

`cd ~` или `cd $HOME`

`cd ~`

Показать текущий путь

`pwd` или `Get-Location`

`pwd`

Список файлов и папок

`ls` или `Get-ChildItem`

`ls`

Подробный список

`ls -Force` (скрытые файлы)

`ls -la`

PowerShell:






## 🔹 2. Работа с файлами и папками

Действие

PowerShell

Git Bash

Создать папку

`mkdir folder_name` или `New-Item -ItemType Directory folder_name`

`mkdir folder_name`

Создать пустой файл

`ni file.txt` или `New-Item file.txt`

`touch file.txt`

Копировать файл

`cp source.txt dest.txt` или `Copy-Item source.txt dest.txt`

`cp source.txt dest.txt`

Копировать папку

`cp -Recurse source/ dest/`

`cp -r source/ dest/`

Переместить / переименовать

`mv old.txt new.txt` или `Move-Item old.txt new.txt`

`mv old.txt new.txt`

Удалить файл

`rm file.txt` или `Remove-Item file.txt`

`rm file.txt`

Удалить папку рекурсивно

`rm -Recurse -Force folder/`

`rm -rf folder/`

> 💡 В PowerShell `rm`, `cp`, `mv` — это **алиасы** для `Remove-Item`, `Copy-Item`, `Move-Item`.

✅ PowerShell сразу создать папку и в ней файл:

New-Item -ItemType Directory -Path ".my_folder" -Force; New-Item -ItemType File -Path ".my_foldermy_file.py" -Force my_folder — имя папки my_file.py — имя файла (можно изменить расширение)

---

## 🔹 3. Работа с Python

Действие

Обе среды (одинаково)

Проверить версию Python

`python --version` или `python -V`

Запустить скрипт

`python script.py`

Установить пакет через pip

`pip install package_name`

Обновить pip

`python -m pip install --upgrade pip`

Список установленных пакетов

`pip list`

Создать виртуальное окружение

`python -m venv myenv`

### Активация виртуального окружения:

Среда

Команда

PowerShell

`.myenvScriptsactivate`

Git Bash

`source myenv/bin/activate`

> ❗ После активации вы увидите `(myenv)` в начале строки.

---

## 🔹 4. Работа с Git

> Git работает **одинаково** в обеих средах — команды **не отличаются**.

Действие

Команда

Инициализировать репозиторий

`git init`

Клонировать репозиторий

`git clone https://github.com/user/repo.git`

Проверить статус

`git status`

Добавить файл к коммиту

`git add file.txt`

Добавить все изменения

`git add .`

Сделать коммит

`git commit -m "описание"`

Отправить в удалённый репозиторий

`git push origin main`

Забрать изменения с удалённого сервера

`git pull origin main`

Посмотреть историю коммитов

`git log --oneline`

Посмотреть ветки

`git branch`

Переключиться на ветку

`git checkout feature` или `git switch feature`

Создать новую ветку

`git checkout -b new-branch`

---

## 🔹 5. Общие и служебные команды

Действие

PowerShell

Git Bash

Очистить экран

`cls`

`clear`

Показать переменную PATH

`$env:PATH`

`echo $PATH`

Найти исполняемый файл

`Get-Command python`

`which python`

История команд

`Get-History` или `history`

`history`

Выход из терминала

`exit`

`exit`

---

## 💡 Советы по использованию в PyCharm:

-   PyCharm использует **системный терминал по умолчанию** (обычно PowerShell на Windows).
-   Чтобы использовать **Git Bash** в PyCharm:  
    `File → Settings → Tools → Terminal → Shell path` → укажите, например:  
    `C:Program FilesGitbinbash.exe`
-   После смены терминала **перезапустите PyCharm**.

Добавить «красивый» промпт (по желанию) PowerShell (Windows) откройте профиль ($PROFILE) и вставьте: powershell

function prompt { $branch = git branch --show-current 2>$null "$([char]0x1b)[96mPS $([char]0x1b)[93m$(Get-Location)$([char]0x1b)[92m $branch$([char]0x1b)[0m`n→ " } python -m venv venv Активация venv: Windows PowerShell:

powershell .venvScriptsActivate.ps1