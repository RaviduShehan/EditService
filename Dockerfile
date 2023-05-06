FROM python:buster
WORKDIR /EditApp
COPY requirements.txt .
COPY src/serviceAccountKey.json .
RUN pip install -r requirements.txt

COPY src src
# Set environment variables for Firestore connection
ENV GOOGLE_APPLICATION_CREDENTIALS="./serviceAccountKey.json"
RUN pip install google-cloud-firestore
RUN pip install firebase-admin

EXPOSE 5003
ENTRYPOINT ["python", "./src/edit.py"]