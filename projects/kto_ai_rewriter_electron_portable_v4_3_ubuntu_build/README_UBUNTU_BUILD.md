# KTO AI Editor — сборка Windows EXE на Ubuntu

## Цель
Собрать Windows portable `.exe` на Ubuntu без запуска Windows.

## Рекомендуемый способ: Docker
Electron Builder официально рекомендует Docker-образ `electronuserland/builder:wine` для сборки Windows-приложений на Linux, потому что внутри уже есть Wine и нужные системные зависимости.

### Команды
```bash
cd kto_ai_rewriter_electron_portable_v4_3_ubuntu_build
chmod +x *.sh
./CHECK_ENV_UBUNTU.sh
./BUILD_WINDOWS_EXE_UBUNTU_DOCKER.sh
```

Готовый файл появится в папке:

```text
dist/
```

Ожидаемое имя:

```text
KTO_AI_Editor_Portable_4.2.0_x64.exe
```

## Если Docker недоступен
Можно собрать через локальный Wine:

```bash
sudo apt update
sudo apt install -y wine64
cd kto_ai_rewriter_electron_portable_v4_3_ubuntu_build
chmod +x *.sh
./BUILD_WINDOWS_EXE_UBUNTU_LOCAL_WINE.sh
```

## Проверка приложения на Ubuntu без сборки EXE
```bash
./RUN_ON_UBUNTU_FOR_TEST.sh
```

## Частые ошибки

### Docker daemon is not available
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
```
После `usermod` нужно выйти из системы и войти снова.

Можно временно запустить через:

```bash
sudo ./BUILD_WINDOWS_EXE_UBUNTU_DOCKER.sh
```

### wine: command not found
Используйте Docker-скрипт или установите Wine:

```bash
sudo apt install -y wine64
```

### Ошибка скачивания Electron
Проверьте интернет и повторите сборку. Кэш хранится в `.cache/` внутри проекта.

### Windows ругается на неизвестного издателя
Это нормально для неподписанного EXE. Для внедрения нужен code signing сертификат.

## Раздача пользователям
После запуска EXE на ПК администратора создайте гостевой ярлык через меню приложения или через файл `CREATE_GUEST_SHORTCUT.cmd` на Windows. Пользователи заходят по ссылке вида:

```text
http://IP_ПК_АДМИНИСТРАТОРА:8787
```
