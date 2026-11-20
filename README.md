# Ansible Roles

Reusable Ansible roles for self-hosted Linux estates.

Built from the working setup behind [tjayhosting.co.uk](https://tjayhosting.co.uk) -
a fully self-hosted stack (Nextcloud, Matrix, Pi-hole/Unbound, Jellyfin, Immich,
Home Assistant, Nginx Proxy Manager, and a lot of things that do not have a
homepage). The roles here are the generic parts; the estate-specific values live
in a private repo.

## Philosophy

**The playbook IS the documentation.** There is no separate runbook. If you read
the YAML you have read the runbook, and the runbook is what actually executes.
That's the difference between a setup that survives and one that survives only
as long as somebody remembers why it was built that way.

**Roles are generic. Estates are configuration.** A role must never hard-code an
IP address, a hostname, a domain or a credential. It takes them as variables.
That is what makes a role reusable, and it is what lets an estate be described
entirely as values.

**Legible to humans and to AI.** Plain YAML, clear naming, comments that explain
*why* rather than *what*. These files are meant to be read by whoever finds them
next - including an assistant trying to understand a system it did not build.

**Idempotent and non-destructive by default.** Roles converge on a desired state.
Removal roles (like `cockpit`) assert *absence* rather than installing something
you no longer want.

## Layout

```
roles/
  <role_name>/
    README.md        # what it does, variables, requirements, verification
    defaults/main.yml
    tasks/main.yml
    handlers/main.yml
    meta/main.yml
    templates/       # if the role needs them
```

## Usage

Add the roles path to your `ansible.cfg`:

```ini
[defaults]
roles_path = ../ansible-roles/roles:roles
```

Then use a role from a playbook:

```yaml
- hosts: linux_hosts
  become: true
  roles:
    - cockpit
```

Roles are safe to re-run. A second run should report `ok` for every task.

## Roles

| Role | Purpose |
|---|---|
| [`cockpit`](roles/cockpit/) | Remove the Cockpit web console. Asserts absence: packages purged, socket stopped/disabled/masked, config removed. |

## Safety

- No role in this repository contains credentials, hostnames, IP addresses or
  domain names. If a role needs one, it is a variable and it belongs in the
  estate's own `group_vars`.
- Secrets belong in `ansible-vault`, never in a committed file.
- Always `--check --diff` before a real run against a live estate.

## Licence

MIT.

## Acknowledgements

Standing on the shoulders of [matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy)
by A.S. - the project that showed what automated, legible infrastructure
documentation should look like.

🦞
