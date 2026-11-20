#!/usr/bin/env python3
"""Decrypt vault-held values in a compose service definition.

Ansible passes a value that came from the vault as an EncryptedString
OBJECT, not as a string. When that object is serialised into YAML it comes
out as a literal ``!vault`` tag plus the ciphertext - which Docker cannot
parse, and which puts the encrypted secret on disk in a readable form.

This script walks the service definitions, finds anything that carries the
vault tag, decrypts it, and prints the result as JSON on stdout. The base
role then loads that JSON back into a fact and the compose template renders
ordinary plain strings.

Usage:
    decrypt_vault_values.py --services-b64 <base64 of the services JSON>

The input is base64 encoded because the services definitions contain quotes,
newlines and braces that would be a quoting nightmare on a command line.
"""
import argparse
import base64
import json
import os
import sys


def _vault_password():
    """Read the vault password from the file Ansible was given."""
    path = os.environ.get("ANSIBLE_VAULT_PASSWORD_FILE")
    if not path:
        raise RuntimeError(
            "ANSIBLE_VAULT_PASSWORD_FILE is not set, so the vault cannot be "
            "decrypted."
        )
    if not os.path.exists(path):
        raise RuntimeError(
            "The vault password file {} does not exist.".format(path)
        )
    with open(path, "r") as fh:
        password = fh.read().strip()
    if not password:
        raise RuntimeError("The vault password file {} is empty.".format(path))
    return password


def _ciphertext_of(value):
    """Return the raw vault ciphertext for a vault-tagged value.

    An EncryptedString keeps its ciphertext in `_ciphertext` and decrypts it
    lazily through the ambient VaultSecretsContext. Outside an
    Ansible task that context does not exist, so the value is read straight
    out of the slot and decrypted with an explicit VaultLib instead.
    """
    ciphertext = getattr(value, "_ciphertext", None)
    if isinstance(ciphertext, str) and ciphertext.strip():
        return ciphertext
    # Some Ansible versions hand the value over as a plain string that still
    # carries the vault header.
    if isinstance(value, str) and value.strip().startswith("$ANSIBLE_VAULT;"):
        return value
    return None


def _is_vault_tagged(value):
    """True when the value carries the Ansible vault tag."""
    if isinstance(value, str):
        return value.strip().startswith("$ANSIBLE_VAULT;")
    return hasattr(value, "_ciphertext") or hasattr(value, "decrypt")


def _decrypt(value):
    """Decrypt one vault-tagged value, whatever shape it arrived in."""
    from ansible.parsing.vault import VaultLib, VaultSecret

    ciphertext = _ciphertext_of(value)
    if ciphertext is None:
        raise RuntimeError(
            "A value was tagged as vault-held but carries no ciphertext: "
            "{!r}".format(value)
        )
    # VaultLib takes a LIST of (vault_id, secret) tuples. The vault_id is
    # the identifier embedded in the ciphertext header - for a default vault
    # that is an empty string, and the empty id matches the ciphertext.
    secret = VaultSecret(_vault_password().encode())
    lib = VaultLib(secrets=[("", secret)])
    plaintext = lib.decrypt(ciphertext.strip())
    # VaultLib returns BYTES. The value goes into a YAML compose file, so it
    # must be a str - a bytes value would be written as a python bytes
    # literal and the compose file would not parse.
    if isinstance(plaintext, bytes):
        plaintext = plaintext.decode("utf-8")
    return plaintext


def _walk(node):
    """Recursively decrypt every vault-tagged value in the tree."""
    if isinstance(node, dict):
        return {k: _walk(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_walk(v) for v in node]
    if _is_vault_tagged(node):
        return _decrypt(node)
    return node


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--services-b64", required=True)
    args = parser.parse_args()

    raw = base64.b64decode(args.services_b64).decode("utf-8")
    services = json.loads(raw)
    decrypted = _walk(services)
    sys.stdout.write(json.dumps(decrypted))


if __name__ == "__main__":
    main()
