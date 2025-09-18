FROM quay.io/minio/mc:latest
COPY minio-bootstrap.sh /usr/local/bin/minio-bootstrap.sh
RUN chmod +x /usr/local/bin/minio-bootstrap.sh
ENTRYPOINT ["/bin/sh","-lc"]
CMD ["/usr/local/bin/minio-bootstrap.sh"]
