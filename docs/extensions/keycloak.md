# Keycloak

Enable authentication with [keycloak](https://www.keycloak.org/) and [python-keycloak](https://github.com/marcospereirampj/python-keycloak). Keycloak access tokens can be used to authenticate requests and user data is synchronized between collectivo and keycloak.

## Installation

Add the following entry to [`collectivo.yml`](reference.md#settings):

```yaml
- extensions:
  - collectivo.auth.keycloak:
      - server_url:     # Path towards the keycloak server
      - realm_name:     # Realm name the collectivo client
      - client_id:      # Name of the collectivo client
      - client_secret:  # Secret key of the collectivo client
```

When keycloak is not correctly configured, a warning will appear in the logs.
