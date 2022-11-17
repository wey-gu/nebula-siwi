# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM ubuntu

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Install production dependencies.
RUN apt-get update && apt-get install -y \
    python3-pip python3-venv
RUN pip3 install --no-cache-dir Cython
RUN pip3 install Flask gunicorn nebula3-python pyahocorasick pyyaml build

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN python3 -m build
RUN pip3 install dist/siwi-*-py3-none-any.whl
# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.

ENV PORT 5000
ENV NG_ENDPOINTS "127.0.0.1:9669"

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 wsgi