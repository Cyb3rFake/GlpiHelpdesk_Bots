FROM python:3.10.12

# RUN mkdir -p app
WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "sender.py" ]
