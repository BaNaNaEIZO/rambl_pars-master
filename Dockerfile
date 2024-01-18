FROM python:alpine

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python", "main.py"]

#ENTRYPOINT ["./main.py"]