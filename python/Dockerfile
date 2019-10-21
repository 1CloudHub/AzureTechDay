FROM python:3.7

ENV PORT=80
 
EXPOSE $PORT 
 
WORKDIR /app

RUN pip install flask

COPY . /app

WORKDIR /app

CMD ["python", "app.py"]
