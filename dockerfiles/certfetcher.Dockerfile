FROM public.ecr.aws/docker/library/alpine:3.18

VOLUME /etc/letsencrypt

# Install certbot
RUN apk update && \
    apk add --no-cache certbot py3-pip && \
    pip install certbot-dns-route53

COPY fetch-certs.sh .

CMD ["./fetch-certs.sh"]