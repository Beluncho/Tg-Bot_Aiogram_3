FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Проверяем, что файлы на месте
RUN ls -la && test -f bot.py && echo "✅ bot.py found!" || echo "❌ bot.py NOT found!"

# Запускаем бота
CMD ["python", "bot.py"]