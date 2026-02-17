# Curve Protocol Dashboard

Дашборд для мониторинга опережающих индикаторов Curve Finance на Ethereum.

## Возможности
- **3Pool Imbalance (Fiddy Indicator)**: Отслеживание баланса USDT/USDC/DAI. Сигналы Risk-Off при доминировании USDT.
- **Gauge Weight Monitor**: Отслеживание весов голосов в GaugeController.
- **Fee Velocity (Alpha)**: Мониторинг накопления комиссий (в процессе накопления данных).
- **SQLite Storage**: Все данные сохраняются локально в `curve_data.db`.
- **Streamlit UI**: Красивый интерфейс с интерактивными графиками.

## Установка и запуск

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Настройте `.env` (опционально):
   Добавьте свой ключ Alchemy/Infura в `ETH_RPC_URL` для более стабильной работы.
3. Запустите дашборд:
   ```powershell
   ./run.ps1
   ```
   Или вручную:
   ```bash
   python collector.py  # Сбор данных в фоновом режиме
   streamlit run app.py # Запуск интерфейса
   ```

## Архитектура
- `collector.py`: Скрипт сбора данных (каждые 5 минут).
- `db.py`: Инициализация базы данных.
- `analytics.py`: Логика обработки данных и расчет RoC.
- `app.py`: Фронтенд на Streamlit.
