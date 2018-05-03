FROM upy:latest
MAINTAINER someone@jrz-target.at

COPY entrypoint-server.sh /

COPY pack.tar.bz2 /
RUN mkdir /outside-module && \
    tar -C /outside-module -xvf /pack.tar.bz2

ENTRYPOINT ["/entrypoint-server.sh"]
