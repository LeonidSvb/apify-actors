FROM apify/actor-python:3.12

COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY --chown=myuser:myuser . ./

CMD python3 -m src
