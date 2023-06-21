# Memberships

Manage memberships of an organization.

Key features:

- Multiple types of membership can be defined with different possible membership statuses.
- Users can apply for a membership through the platform. Each membership type can have its own application form. Other extensions can add additional fields to the application form.
- Memberships can require shares or regular fees. Automatic invoices are generated if the [payments](payments.md) extension is installed.


## Installation

Add the following entry to [`collectivo.yml`](reference.md#settings):

```yaml
- extensions:
  - collectivo.memberships:
      - registration_serializers:
          - create: collectivo.memberships.serializers.MembershipRegisterSerializer
```

The setting `registration_serializers` defines the serializers used to create a membership application. Entries can be `create` or `update` and must define a path to a serializer class. The default serializer is `collectivo.memberships.serializers.MembershipRegisterSerializer`.
