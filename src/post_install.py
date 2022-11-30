from subprocess import call
from setuptools.command.install import install as _install


class Install(_install):
    def __post_install(self, dir):
        call(['./auto_complete_install.sh'])

    def run(self):
        _install.run(self)
        self.execute(
            self.__post_install, (self.install_lib,), msg="installing auto completion"
        )
