FROM python:3.4

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	sqlite3 

RUN pip install Django

WORKDIR /usr/src/app
COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "127.0.0.1:8002"]