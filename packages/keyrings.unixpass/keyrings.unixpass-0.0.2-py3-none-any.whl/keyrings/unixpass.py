import subprocess
from typing import Optional, Tuple

import keyring

__version__ = "0.0.2"


class Keyring(keyring.backend.KeyringBackend):
    def __init__(self):
        self.username_prefix = ""
        self.password_prefix = ""
        super().__init__()

    @property
    def priority(self) -> int:
        result = subprocess.run(
            ("pass", "version"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:
            raise RuntimeError("pass executable not found")

        return 1

    def _get_credentials(self, key: str) -> Tuple[Optional[str], Optional[str]]:
        result = subprocess.run(("pass", "show", key), capture_output=True, text=True)
        if result.returncode != 0:
            return (None, None)

        # strip trailing '\n'
        # always present when the password is not inserted using multiline
        lines = result.stdout.rstrip("\n").splitlines()

        username = None
        password = None
        for line in lines:
            # default prefixes are empty, so password prefix must be first
            if line.startswith(self.password_prefix):
                prefix_len = len(self.password_prefix)
                password = line[prefix_len:].strip()
            elif line.startswith(self.username_prefix):
                prefix_len = len(self.username_prefix)
                username = line[prefix_len:].strip()

        return (username, password)

    def get_password(self, service: str, username: str) -> Optional[str]:
        _, password = self._get_credentials(f"{service}/{username}")
        return password

    def set_password(self, service: str, username: str, password: str) -> None:
        result = subprocess.run(
            ("pass", "insert", "-m", f"{service}/{username}"),
            input=password,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        if result.returncode != 0:
            raise keyring.errors.PasswordSetError("couldn't insert password")

    def delete_password(self, service: str, username: str) -> Optional[str]:
        result = subprocess.run(
            ("pass", "rm", "-f", f"{service}/{username}"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        if result.returncode != 0:
            raise keyring.errors.PasswordDeleteError("couldn't delete password")

    def get_credential(
        self, service: str, username: Optional[str]
    ) -> Optional[keyring.credentials.Credential]:
        if username is not None:
            _, password = self._get_credentials(f"{service}/{username}")
            if password is None:
                return None
            return keyring.credentials.SimpleCredential(username, password)
        else:
            username, password = self._get_credentials()
            if username is None or password is None:
                return None
            return keyring.credentials.SimpleCredential(username, password)
