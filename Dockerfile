FROM python:3.11-slim

RUN pip install -r requirements.txt


WORKDIR /app
COPY app.py .
COPY index.html .

ENV FLASK_APP=app.py

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]