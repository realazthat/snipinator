FROM python:3.12-slim


WORKDIR /snipinator

# apt-get -y --no-install-recommends install git=1:2.39.2-1.1 &&
# apt-get -y upgrade &&

COPY . /snipinator
RUN apt-get -y update && apt-get -y --no-install-recommends install bash=5.1-6ubuntu1.1 && \
  apt-get -y clean && \
  apt-get -y autoremove && \
  rm -rf /var/lib/apt/lists/* && \
  pip install --no-cache-dir --upgrade pip setuptools wheel && \
  mkdir -p /home/nobody/.local && \
  chown -R nobody:nogroup /snipinator /home/nobody/.local && \
  chmod -R a+wrX /snipinator


USER nobody
WORKDIR /snipinator
ENV PATH=/home/nobody/.local/bin:$PATH
ENV PYTHONPATH=/home/nobody/.local/lib/python3.12/site-packages
RUN pip install --no-cache-dir --prefix=/home/nobody/.local .

# This is where the user will mount their data to.
WORKDIR /data

ENTRYPOINT ["python", "-m", "snipinator.cli"]
CMD ["--help"]
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -m snipinator.cli --version || exit 1
