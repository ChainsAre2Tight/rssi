## 1 - сборка образа
```bash
docker compose --profile frontend --profile api --profile ingestion --profile ntp --profile core --profile localization
```
## 2 - запуск фронт+апи (локализация выключена)
```bash
docker compose --profile frontend --profile api up --force-recreate
```
## 3 - запуск фронт+апи+локализация
```bash
docker compose --profile frontend --profile api --profile localization up --force-recreate
```
## 4 - выключение
```bash
docker compose --profile frontend --profile api --profile ingestion --profile ntp --profile core --profile localization down --remove-orphans
```
## запуск (все воркеры)
```bash
docker compose --profile frontend --profile api --profile ingestion --profile ntp --profile core --profile localization up --force-recreate
```
