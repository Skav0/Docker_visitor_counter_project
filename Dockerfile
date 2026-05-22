FROM python:3.13.13-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY . .
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["flask", "run"]


#we can optimize the image by doing multi stage build.