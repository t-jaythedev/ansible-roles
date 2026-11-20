# nextcloud

Bare metal Nextcloud server: Apache 2.4, PHP-FPM, MariaDB and Redis.

This role configures the *server stack* around an existing Nextcloud
installation. It does not download or install the Nextcloud application
itself - the application, its version and its upgrade path are the
operator's business. Tasks that drive `occ` are skipped when
`nextcloud_occ_installed` is false.

## What it does

- **MariaDB** - installs the server, writes Nextcloud's recommended tuning to
  `/etc/mysql/mariadb.conf.d/nextcloud.cnf`, creates the database and the
  application user.
- **Redis** - installs and runs Redis bound to the loopback interface, used
  for Nextcloud's file locking cache.
- **PHP-FPM** - installs PHP with the module set Nextcloud expects (APCu for
  the local cache, the Redis extension, `bcmath`, `gmp`, `imagick`), then
  applies the memory, upload size and opcache tuning, and raises the FPM
  pool limits above the packaged defaults.
- **Apache** - installs Apache, enables the module set Nextcloud needs,
  switches from `mpm_prefork` to `mpm_event`, writes the virtual host and
  validates the config before restarting.
- **Directories** - creates the web root, data directory and config directory
  with `www-data` ownership.
- **occ** - sets the CLI URL, overwrite protocol and data directory, and
  installs the five-minute background cron job.

## What it does not do

- It does not install the Nextcloud application or its apps.
- It does not terminate TLS. This role expects a reverse proxy in front of
  it; the virtual host listens on port 80 only.
- It does not manage the external Talk signalling server or the TURN server.
  Those are separate services with their own credentials.

## Requirements

The role uses `ansible.builtin.mysql_db` and `ansible.builtin.mysql_user`, so
the `community.mysql` collection must be installed on the control machine.

## Role variables

See `defaults/main.yml`. The variables you are most likely to override:

| Variable | Default | Purpose |
|---|---|---|
| `nextcloud_php_version` | `8.4` | PHP major.minor version |
| `nextcloud_server_name` | `nextcloud.example.com` | ServerName and CLI URL |
| `nextcloud_data_dir` | `/var/www/nextcloud/data` | Data directory |
| `nextcloud_db_name` | `nextcloud` | Database name |
| `nextcloud_db_user` | `nextcloud` | Database user |
| `nextcloud_occ_installed` | `true` | Set false to skip occ-driven tasks |

### Secrets

`nextcloud_db_password` is **required** but deliberately has no default. The
role asserts that it is defined and fails with a clear message if it is not.
Supply it through Ansible Vault or an encrypted `group_vars` file in the
consuming project. It must never be committed here.

## Tags

- `nextcloud` - everything
- `nextcloud_db` - MariaDB
- `nextcloud_cache` - Redis
- `nextcloud_php` - PHP-FPM
- `nextcloud_web` - Apache

## Example playbook

```yaml
- name: Configure the Nextcloud server
  hosts: nextcloud
  become: true
  roles:
    - role: nextcloud
      vars:
        nextcloud_server_name: nextcloud.example.com
```

## Idempotency

The role is written to be idempotent. `occ config:system:set` reports a
change only when the stored value actually differs, and the Apache and PHP
steps use declarative modules or handlers. Running the role twice should
report no changes on a correctly configured host.

## License

MIT
