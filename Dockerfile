FROM python:3.11-slim

WORKDIR /app

COPY . /app

COPY ./scripts/wait-for-it.sh /app/wait-for-it.sh
COPY ./scripts/migrate.sh /app/migrate.sh

RUN chmod +x /app/wait-for-it.sh

RUN chmod +x /app/migrate.sh

RUN apt update && apt install -y pkg-config python3-dev default-libmysqlclient-dev build-essential

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["./wait-for-it.sh", "db:3306", "--", "python", "src/app.py", "--host=0.0.0.0"]