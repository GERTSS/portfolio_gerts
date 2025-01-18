FROM postgres:latest

RUN groupadd -g 1000 mygroup && \
    useradd -u 1000 -g mygroup -s /bin/bash -m myuser

RUN mkdir -p /var/run/postgresql && chown -R myuser:mygroup /var/run/postgresql && chmod -R 700 /var/run/postgresql

RUN mkdir -p /var/lib/postgresql/data && chown -R myuser:mygroup /var/lib/postgresql/data && chmod -R 700 /var/lib/postgresql/data

USER myuser