import logging
from collections import deque
from collections import namedtuple
from pathlib import Path
from typing import Deque

from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_platform.util.PtyUtil import SpawnOsCommandException
from peek_plugin_base.util.build_common.BuilderOsCmd import runCommand
from peek_plugin_base.util.build_common.BuilderOsCmd import runNgBuild
from peek_plugin_base.util.build_frontend.FrontendFileSync import (
    FrontendFileSync,
)
from peek_plugin_base.util.build_frontend.WebBuilder import WebBuilder

logger = logging.getLogger(__name__)

PatchItem = namedtuple("PatchItem", ["target", "patch"])


class EdnarWebBuilder(WebBuilder):
    APP_NAME = "ednar peek app"
    PATCH_ITEMS = [
        PatchItem(
            target="src/@peek/peek_core_device/device-enrolment.service.ts",
            patch="patch/device-enrolment.service.ts.diff",
        ),
        PatchItem(
            target="src/@peek/peek_plugin_diagram/_private/branch"
            "/PrivateDiagramBranchContext.ts",
            patch="patch/PrivateDiagramBranchContext.ts.diff",
        ),
        PatchItem(
            target="src/@_peek/peek_plugin_enmac_diagram/pofDiagram"
            ".module.ts",
            patch="patch/pofDiagram.module.ts.diff",
        ),
    ]

    def __init__(self, frontendProjectDir: str, outputPath: str, jsonCfg):
        self._frontendProjectDir = frontendProjectDir
        self._outputPath = outputPath

        self._jsonCfg = jsonCfg
        self.fileSync = FrontendFileSync(lambda f, c: self._syncFileHook(f, c))
        self._patchTasks: Deque[PatchItem] = deque()
        self._patchRejectedFile: Path = Path(self._frontendProjectDir) / Path(
            "./PATCH_REJECTED.rej"
        )
        if self._patchRejectedFile.exists():
            self._patchRejectedFile.unlink()

    def _syncFileHook(self, fileName: str, contents: bytes) -> bytes:
        for patchItem in self.PATCH_ITEMS:
            if fileName.endswith(patchItem.target):
                self._patchTasks.append(patchItem)
        return contents

    def _patchFiles(self):
        # apply patches
        #  patch src/@peek/peek_core_device/device-enrolment.service.ts \
        # patch/device-enrolment.service.ts.diff

        # patch src/@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchContext.ts \
        # patch/PrivateDiagramBranchContext.ts.diff

        # patch src/@_peek/peek_plugin_enmac_diagram/pofDiagram.module.ts \
        #  patch/pofDiagram.module.ts.diff
        while self._patchTasks:
            patchItem = self._patchTasks.popleft()
            # patch diff and ignore previously patched
            #  https://stackoverflow.com/a/52967701
            command = (
                f"patch -p0 --forward -r PATCH_REJECTED.rej"
                f" {patchItem.target}"
                f" {patchItem.patch}"
            )
            try:
                runCommand(self._frontendProjectDir, command.split())
            except SpawnOsCommandException as e:
                if self._patchRejectedFile.exists():
                    logger.error(f"patch rejected {patchItem.patch}")
                else:
                    logger.debug(f"patch previously applied {patchItem.patch}")

    @deferToThreadWrapWithLogger(logger, checkMainThread=False)
    def build(self):
        if not self._jsonCfg.feWebBuildPrepareEnabled:
            logger.info(
                f"{self.APP_NAME} build SKIPPING, Web build prepare is "
                f"disabled in config"
            )
            return

        # check if npm installed
        endarAngularExecutable = Path(self._frontendProjectDir) / Path(
            "./node_modules/.bin/ng"
        )
        if (
            not endarAngularExecutable.is_file()
            or not endarAngularExecutable.exists()
        ):
            raise FileNotFoundError(
                "nodule_modules for ednar peek app is not ready for building."
            )

        excludeRegexp = [r".*__pycache__.*", r".*[.]py$"]

        import peek_office_app

        baseSrcDir = Path(peek_office_app.__file__).parent / Path("./src")

        for moduleName in ["@_peek", "@peek"]:
            srcDir = baseSrcDir / Path(f"./{moduleName}")
            dstDir = Path(self._frontendProjectDir) / Path(
                f"./src/{moduleName}"
            )
            self.fileSync.addSyncMapping(
                srcDir=str(srcDir),
                dstDir=str(dstDir),
                parentMustExist=True,
                deleteExtraDstFiles=False,
                postSyncCallback=self._patchFiles,
                excludeFilesRegex=excludeRegexp,
            )

        self.fileSync.syncFiles()

        if self._jsonCfg.feSyncFilesForDebugEnabled:
            logger.info(
                f"{self.APP_NAME} starting frontend development file sync"
            )
            self.fileSync.startFileSyncWatcher()

        if self._jsonCfg.feWebBuildEnabled:
            # ng build --prod --output-hashing none --base-href ./
            ngArgs = (
                f"ng build --prod --output-hashing none --base-href ./"
                f" --output-path {self._outputPath}".split()
            )
            runNgBuild(
                self._frontendProjectDir,
                ngBuildArgs=ngArgs,
            )
