#using the latest alpine python 3.7.3 image (dev env is 3.7)
FROM python:3.7.3-alpine3.9
LABEL org.notatuna.creator="Brian Provenzano"
USER root
RUN apk add --no-cache alpine-conf tzdata bash git && \
    pip3 install boto3
RUN setup-timezone -z America/Denver && ntpd -d -q -n -p north-america.pool.ntp.org
COPY src/copy-s3bucket.py /bin/copy-s3bucket.py
RUN chmod +x /bin/copy-s3bucket.py
ENTRYPOINT [ "/bin/copy-s3bucket.py" ]
CMD [ "-h" ]