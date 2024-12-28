
FROM python:3.10-slim

WORKDIR /app


COPY . /app


RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 6743

ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0", "--port=6743"]
