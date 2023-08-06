import subprocess
from typing import Optional

import keyring.backend
import keyring.errors

__version__ = "0.0.1"

class Keyring(keyring.backend.KeyringBackend):
    @property
    def priority(self) -> int:
        result = subprocess.run(
            ("pass", "version"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:
            raise RuntimeError("pass executable not found")

        return 1

    def get_password(self, service: str, username: str) -> Optional[str]:
        result = subprocess.run(
            ("pass", "show", f"{service}/{username}"), capture_output=True, text=True
        )
        if result.returncode != 0:
            return None

        # strip trailing '\n'
        return result.stdout.rstrip('\n')

    def set_password(self, service: str, username: str, password: str) -> None:
        result = subprocess.run(
            ("pass", "insert", f"{service}/{username}"),
            # pass asks for retyping
            input=f"{password}\n{password}\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        if result.returncode != 0:
            raise keyring.errors.PasswordSetError("couldn't insert password")

    def delete_password(self, service: str, username: str) -> Optional[str]:
        result = subprocess.run(
            ("pass", "rm", "-f", f"{service}/{username}"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )

        if result.returncode != 0:
            raise keyring.errors.PasswordDeleteError("couldn't delete password")
