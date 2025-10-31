FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

#CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
CMD ["python", "-u", "app.py"]