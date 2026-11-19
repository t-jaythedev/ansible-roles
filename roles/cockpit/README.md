# cockpit

Remove the Cockpit web console from a host.

Cockpit is a retired service in this estate. This role asserts its **absence**:
packages purged, socket stopped/disabled/masked, config directory removed,
systemd overrides removed, daemon reloaded.

## Requirements

- Ubuntu (tested on noble / questing)
- `become` privilege

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `cockpit_remove` | `true` | Set to `false` to skip removal entirely. |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: linux_hosts
  become: true
  roles:
    - cockpit
```

To leave Cockpit alone on one host:

```yaml
- hosts: linux_hosts
  become: true
  roles:
    - role: cockpit
      vars:
        cockpit_remove: false
```

## Idempotency

Fully idempotent. A second run reports `ok` for every task - nothing is
installed, purged or removed twice.

## Verification

```bash
dpkg-query -W -f='${Status}' cockpit   # expect not installed
systemctl is-active cockpit.socket     # expect inactive
ss -ltn | grep :9090                   # expect no output
```
