#!/usr/bin/env python3
"""Print the host ports published by a compose project.

Reads the compose file with `docker compose config --format json` and prints
every published host port, space separated, on one line.

Used by the base role's readiness check. A container can be RUNNING and still
not answering - a service that binds its port late, or one whose healthcheck
has not passed yet. Probing the published ports proves the service is
actually serving, which is the question that matters.

Projects that publish no ports (host networking) print nothing, and the
caller falls through to the container-level check.
"""
import json
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: list_published_ports.py <compose-file>\n")
        return 2

    compose_file = sys.argv[1]
    proc = subprocess.run(
        ["docker", "compose", "-f", compose_file, "config", "--format", "json"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        # A project whose compose file cannot be parsed publishes nothing.
        # The caller treats an empty result as "no ports to probe".
        return 0

    try:
        config = json.loads(proc.stdout)
    except ValueError:
        return 0

    ports = set()
    for service in (config.get("services") or {}).values():
        for port in service.get("ports") or []:
            published = port.get("published")
            if published is None:
                continue
            text = str(published)
            if text.isdigit():
                ports.add(text)

    print(" ".join(sorted(ports, key=int)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
