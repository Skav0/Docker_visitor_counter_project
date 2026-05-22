FROM python:3.13.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt


COPY app.py .
COPY index.html .


EXPOSE 5000
CMD ["python", "app.py"]