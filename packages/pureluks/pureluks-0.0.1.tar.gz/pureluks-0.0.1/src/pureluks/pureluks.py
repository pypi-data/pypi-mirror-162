# Copyright (c) 4ndrs <andres.degozaru@gmail.com>
# SPDX-License-Identifier: MIT
"""Simple cryptsetup wrapper for LUKS encrypted images"""

import pathlib
import subprocess  # nosec


class PureLUKS:
    """PureLUKS object to manage LUKS encrypted image files. Supports the with
    statement. Consider using the .close() method when not using the with
    statement to avoid leaving the LUKS encrypted image open."""

    def __init__(
        self,
        image_file,
        key_file,
        mapper_name,
        mount_path,
    ):
        self.image_file = pathlib.Path(image_file)
        self.key_file = pathlib.Path(key_file)
        self.mapper = pathlib.Path("/dev/mapper") / mapper_name
        self.mount_path = pathlib.Path(mount_path)

        # Test that all paths exist, and that the mapper is not in use
        if not self.image_file.exists():
            raise FileNotFoundError(
                f"The image file provided, {self.image_file}, does not exist."
            )

        if not self.key_file.exists():
            raise FileNotFoundError(
                f"The key file provided, {self.key_file}, does not exist."
            )

        if not self.mount_path.exists():
            raise FileNotFoundError(
                f"The mount path, {self.mount_path}, does not exist."
            )
        if not self.mount_path.is_dir():
            raise NotADirectoryError(f"{self.mount_path} is not a directory.")

        if self.mapper.exists():
            raise FileExistsError(f"{self.mapper} already does exist.")

        # The following will raise an exception if cryptsetup is not found
        crypt_test = subprocess.check_output(  # nosec
            ["cryptsetup", "-V"]
        ).decode()

        if len(crypt_test) < 1 or crypt_test.split()[0] != "cryptsetup":
            raise ValueError(
                f"Cryptsetup returned an invalid output: {crypt_test}"
            )

        self.opened = False
        self.mounted = False

    def open(self):
        """Opens the encrypted image and sets up the mapper. Does nothing if
        the image is already open."""
        if not self.opened:
            subprocess.check_output(  # nosec
                [
                    "cryptsetup",
                    "--key-file",
                    self.key_file,
                    "luksOpen",
                    self.image_file,
                    self.mapper.name,
                ]
            )
            self.opened = True

        return self

    def close(self):
        """Closes the mapper, unmounts if mounted. Does nothing if the mapper
        is already closed."""
        if self.mounted:
            subprocess.check_output(["umount", self.mount_path])  # nosec
            self.mounted = False

        if self.opened:
            subprocess.check_output(  # nosec
                ["cryptsetup", "luksClose", self.mapper.name]
            )
            self.opened = False

        return self

    def mount(self):
        """Mounts the mapper into path. Raises FileNotFoundError if the mapper
        is not set up. Does nothing if already mounted."""
        if not self.mapper.exists():
            raise FileNotFoundError(
                f"The mapper, {self.mapper}, does not exist. Consider opening "
                "the image before mounting."
            )

        if not self.mounted:
            subprocess.check_output(  # nosec
                [
                    "mount",
                    "-o",
                    "defaults,relatime",
                    self.mapper,
                    self.mount_path,
                ]
            )
            self.mounted = True

        return self

    def umount(self):
        """Unmounts the mounted image. Does nothing if already unmounted."""
        if self.mounted:
            subprocess.check_output(["umount", self.mount_path])  # nosec
            self.mounted = False

        return self

    def __enter__(self):
        return self

    def __exit__(self, exec_type, exc_value, traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except AttributeError:
            pass  # if __init__() never ran, self.mounted won't be defined

    def __str__(self):
        return (
            f"PureLUKS('Mapper:     {self.mapper.absolute()}\n"
            f"          Image:      {self.image_file.absolute()}\n"
            f"          Key:        {self.key_file.absolute()}\n"
            f"          Mount path: {self.mount_path.absolute()}\n"
            f"          Opened:     {str(self.opened)}\n"
            f"          Mounted:    {str(self.mounted)}')"
        )
