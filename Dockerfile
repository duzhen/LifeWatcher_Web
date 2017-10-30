FROM ubuntu:latest
MAINTAINER Zhen Du "jenkin.du@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["LifeWatcher_Web.py"]