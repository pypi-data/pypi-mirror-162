import os

from dataclasses import dataclass
from pathlib import Path

from . import helper


@dataclass
class VersionNumberString:
    # partly_semver: bool = True
    date: str = helper.get_date_string()
    time: str = helper.get_time_string()
    ydy: int = helper.get_day_of_year()
    pri: int = int(date[2:4])
    sec: int = int(date[5:7])
    mic: int = 0
    build: int = f"{pri}.{ydy:03d}.{time}"
    release: str = f"{date}"

    @property
    def full_version(self) -> str:
        return f"version: {self.version_string}, build_{self.build}, release {self.release}"

    @property
    def version_string(self) -> str:
        return f"{self.pri}.{self.sec}.{self.mic}"

    def __str__(self) -> str:
        return self.version_string


class AutoVersionNumber:
    def __init__(
        self,
        filename: str = None,
        increase: bool = False,
    ):
        # self.loose_semantic = True

        # self.__version = VersionNumberString(self.loose_semantic)
        self.__version = VersionNumberString()
        self.__root_path = Path(os.getcwd())

        self.__file_content = [
            self.__version.__str__(),
            self.__version.build,
            self.__version.release,
        ]

        if filename:
            self.__file_path = self.__root_path.joinpath(filename)
            if not self.__file_path.is_file():
                with open(self.__file_path, "w") as f:
                    f.write("\n".join(self.__file_content))
            else:
                with open(self.__file_path, "r") as f:
                    lines = f.readlines()

                self.__build_version_number_from_file(lines)

        if increase:
            self.update_version_number()

    def __build_version_number_from_file(self, content):
        _ = [line.rstrip() for line in content]

        pri, sec, mic = _[0].split(".")

        self.__version.pri = int(pri)
        self.__version.sec = int(sec)
        self.__version.mic = int(mic)
        self.__version.build = _[1]
        self.__version.release = _[2]

    def update_version_number(self):
        new_version = VersionNumberString()
        actual_version = self.__version

        if (new_version.pri == actual_version.pri) and (
            new_version.sec == actual_version.sec
        ):
            self.__version.mic += 1
        else:
            self.__version.mic = 0
            self.__version.pri = new_version.pri
            self.__version.sec = new_version.sec

        self.__version.build = new_version.build
        self.__version.release = new_version.release

        self.__file_content[0] = self.__version.version_string

        with open(self.__file_path, "w") as f:
            f.write("\n".join(self.__file_content))

    def __str__(self):
        return self.__version.version_string

    def get_version(self):
        return self.__version.version_string

    def get_full_version(self):
        return self.__version.full_version

    def get_build(self):
        return self.__version.build

    def get_release(self):
        return self.__version.release
