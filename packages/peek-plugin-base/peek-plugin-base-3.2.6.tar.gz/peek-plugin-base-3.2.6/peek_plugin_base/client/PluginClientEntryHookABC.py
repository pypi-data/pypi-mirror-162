import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from jsoncfg.value_mappers import require_string

from peek_platform import PeekPlatformConfig
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.client.PeekClientPlatformHookABC import (
    PeekClientPlatformHookABC,
)

logger = logging.getLogger(__name__)


class PluginClientEntryHookABC(PluginCommonEntryHookABC):
    def __init__(
        self,
        pluginName: str,
        pluginRootDir: str,
        platform: PeekClientPlatformHookABC,
    ):
        PluginCommonEntryHookABC.__init__(
            self, pluginName=pluginName, pluginRootDir=pluginRootDir
        )
        self._platform = platform

    @property
    def platform(self) -> PeekClientPlatformHookABC:
        return self._platform

    @property
    def publishedClientApi(self) -> Optional[object]:
        return None

    @property
    def angularMainModule(self) -> str:
        """Angular Main Module

        :return: The name of the main module that the Angular2 router will lazy load.
        """
        return self._angularMainModule

    @property
    def angularFrontendAppDir(self) -> str:
        """Angular Frontend Dir

        This directory will be linked into the angular app when it is compiled.

        :return: The absolute path of the Angular2 app directory.
        """
        relDir = self._packageCfg.config.plugin.title(require_string)
        dir = os.path.join(self._pluginRoot, relDir)
        if not os.path.isdir(dir):
            raise NotADirectoryError(dir)
        return dir

    @property
    def platformConfig(self):
        return PeekPlatformConfig.config

    def copyFolder(self, srcDir: Path, dstDir: Path):
        shutil.copytree(srcDir, dstDir, dirs_exist_ok=True)
