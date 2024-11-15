ARG IMG="ubuntu"
ARG TAG="22.04"

FROM ${IMG}:${TAG}

COPY install-prereqs.sh /root
COPY shared_vars.sh /root

WORKDIR /root

RUN cd /root && ./install-prereqs.sh

ENTRYPOINT [ "/usr/bin/tail", "-f", "/dev/null" ]
