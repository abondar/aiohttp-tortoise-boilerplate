FROM python:3.6

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN mkdir /home/app/
WORKDIR /home/app/
COPY . .

CMD [ "python", "run.py"]
