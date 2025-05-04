FROM public.ecr.aws/opensearchproject/opensearch:2.15.0

# Seems to be required in order to allow the bind mount to work
# https://stackoverflow.com/a/72172651
USER 1000:1000
RUN chown -R 1000:1000 /usr/share/opensearch/data
VOLUME ["/usr/share/opensearch/data"]