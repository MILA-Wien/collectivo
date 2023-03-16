FROM quay.io/keycloak/keycloak:19.0.2
WORKDIR /opt/keycloak
COPY ./import/* /opt/keycloak/data/import/
# for demonstration purposes only, please make sure to use proper certificates in production instead
RUN /opt/keycloak/bin/kc.sh import --dir /opt/keycloak/data/import
ENV ROOT_LOGLEVEL=ALL
ENV KEYCLOAK_LOGLEVEL=DEBUG
# change these values to point to a running postgres instance
CMD [ "start-dev" ]