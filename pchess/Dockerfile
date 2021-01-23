FROM python:3

MAINTAINER Tyler Weston "tylerjohnweston@gmail.com"

WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

COPY . .

CMD ./wait-for-postgres.sh db && flask db init && flask db upgrade && flask db migrate && flask run -h 0.0.0.0 -p 5000