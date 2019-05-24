import textwrap
from typing import TYPE_CHECKING, Optional

from .utils import Cmd, _Pathish, pathstr

if TYPE_CHECKING:
    from .application import Application


class JuliaRuntime:
    # executable: str
    # sysimage: Optional[_Pathish]

    def __init__(self, executable: str, sysimage: Optional[_Pathish]):
        self.executable = executable
        self.sysimage = sysimage

    def cmd(self) -> Cmd:
        assert self.sysimage
        cmd = [pathstr(self.executable)]
        cmd.extend(["--sysimage", pathstr(self.sysimage)])
        return cmd

    def summary(self) -> str:
        summary = """
        Executable  : {self.executable}
        System image: {self.sysimage}
        """
        return textwrap.dedent(summary.format(self=self)).strip()

    def resolve(self, app: "Application") -> "JuliaRuntime":
        if not self.sysimage:
            self.sysimage = app.sysimage_for(self.executable)
        return self
