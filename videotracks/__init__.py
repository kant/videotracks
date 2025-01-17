# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Add-on initialization
"""

import logging

import os
from pathlib import Path

import bpy

from bpy.app.handlers import persistent

from bpy.props import IntProperty
from bpy.props import BoolProperty


from .config import config


bl_info = {
    "name": "Video Tracks",
    "author": "Ubisoft - Julien Blervaque (aka Werwack)",
    "description": "Introduce tracks to the Blender VSE - Ubisoft Animation Studio",
    "blender": (2, 93, 0),
    "version": (0, 1, 31),
    "location": "View3D > Video Tracks",
    "wiki_url": "https://github.com/ubisoft/videotracks",
    "warning": "BETA Version",
    "category": "Ubisoft",
}

__version__ = ".".join(str(i) for i in bl_info["version"])
display_version = __version__


###########
# Logging
###########

# https://docs.python.org/fr/3/howto/logging.html
_logger = logging.getLogger(__name__)
_logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO)
_logger.setLevel(logging.INFO)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET


# _logger.info(f"Logger {str(256) + 'mon texte super long et tout'}")

# _logger.info(f"Logger {str(256)}")
# _logger.warning(f"logger {256}")
# _logger.error(f"error {256}")
# _logger.debug(f"debug {256}")


class Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord):
        """
        The role of this custom formatter is:
        - append filepath and lineno to logging format but shorten path to files, to make logs more clear
        - to append "./" at the begining to permit going to the line quickly with VS Code CTRL+click from terminal
        """
        s = super().format(record)
        pathname = Path(record.pathname).relative_to(MODULE_PATH)
        s += f"  [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
        return s


# def get_logs_directory():
#     def _get_logs_directory():
#         import tempfile

#         if "MIXER_USER_LOGS_DIR" in os.environ:
#             username = os.getlogin()
#             base_shared_path = Path(os.environ["MIXER_USER_LOGS_DIR"])
#             if os.path.exists(base_shared_path):
#                 return os.path.join(os.fspath(base_shared_path), username)
#             logger.error(
#                 f"MIXER_USER_LOGS_DIR env var set to {base_shared_path}, but directory does not exists. Falling back to default location."
#             )
#         return os.path.join(os.fspath(tempfile.gettempdir()), "mixer")

#     dir = _get_logs_directory()
#     if not os.path.exists(dir):
#         os.makedirs(dir)
#     return dir


# def get_log_file():
#     from mixer.share_data import share_data

#     return os.path.join(get_logs_directory(), f"mixer_logs_{share_data.run_id}.log")


###########
# Version
###########


@persistent
def checkDataVersion_post_load_handler(self, context):
    loadedFileName = bpy.path.basename(bpy.context.blend_data.filepath)
    print("\n\n-------------------------------------------------------")
    if "" == loadedFileName:
        print("\nNew file loaded")
    else:
        print("\nExisting file loaded: ", bpy.path.basename(bpy.context.blend_data.filepath))
        _logger.info("  - Video Track is checking the version used to create the loaded scene data...")

        latestVersionToPatch = 1003061

        numScenesToUpgrade = 0
        lowerSceneVersion = -1
        for scn in bpy.data.scenes:

            if getattr(bpy.context.scene, "UAS_shot_manager_props", None) is not None:
                #   print("\n   Shot Manager instance found in scene " + scn.name)
                props = scn.UAS_shot_manager_props

                # # Dirty hack to avoid accidental move of the cameras
                # try:
                #     print("ici")
                #     if bpy.context.space_data is not None:
                #         print("ici 02")
                #         if props.useLockCameraView:
                #             print("ici 03")
                #             bpy.context.space_data.lock_camera = False
                # except Exception as e:
                #     print("ici error")
                #     _logger.error("** bpy.context.space_data.lock_camera had an error **")
                #     pass

                #   print("     Data version: ", props.dataVersion)
                #   print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
                # if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:
                # if props.dataVersion <= 0 or props.dataVersion < props.version()[1]:
                if props.dataVersion <= 0 or props.dataVersion < latestVersionToPatch:  # <= ???
                    _logger.info(
                        f"     *** Scene {scn.name}: Shot Manager Data Version is lower than the latest Shot Manager version to patch"
                    )
                    numScenesToUpgrade += 1
                    if -1 == lowerSceneVersion or props.dataVersion < lowerSceneVersion:
                        lowerSceneVersion = props.dataVersion
                else:
                    if props.dataVersion < props.version()[1]:
                        props.dataVersion = props.version()[1]
                    # set right data version
                    # props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
                    # print("       Data upgraded to version V. ", props.dataVersion)

        if numScenesToUpgrade:
            print(
                "Shot Manager Data Version is lower than the current Shot Manager version - Upgrading data with patches..."
            )
            # apply patch and apply new data version
            # wkip patch strategy to re-think. Collect the data versions and apply the respective patches?

            patchVersion = 1002026
            if lowerSceneVersion < patchVersion:
                from .data_patches.data_patch_to_v1_2_25 import data_patch_to_v1_2_25

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_2_25()
                lowerSceneVersion = patchVersion

            patchVersion = 1003016
            if lowerSceneVersion < patchVersion:
                from .data_patches.data_patch_to_v1_3_16 import data_patch_to_v1_3_16

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_3_16()
                lowerSceneVersion = patchVersion

            patchVersion = 1003061
            if lowerSceneVersion < patchVersion:
                from .data_patches.data_patch_to_v1_3_61 import data_patch_to_v1_3_61

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_3_61()
                lowerSceneVersion = patchVersion

            # current version, no patch required but data version is updated
            if lowerSceneVersion < props.version()[1]:
                props.dataVersion = props.version()[1]


def register():

    from .operators import prefs
    from .operators import general
    from .operators import tracks

    from . import otio
    from .properties import vt_props

    # from .ui.vsm_ui import UAS_PT_VideoTracks
    from .ui import vt_ui
    from .ui import vt_panels_ui
    from .ui import vt_time_controls_ui

    from .operators import about
    from .operators import vt_tools

    from .properties import addon_prefs

    from .tools import vse_render
    from .tools import markers_nav_bar
    from .tools import time_controls_bar

    from .utils import utils
    from .utils import utils_operators

    from .opengl import sequencer_draw

    versionTupple = utils.display_addon_registered_version("Video Tracks")

    config.initGlobalVariables()

    if config.uasDebug:
        _logger.setLevel(logging.DEBUG)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    ###################
    # logging
    ###################

    if len(_logger.handlers) == 0:
        _logger.setLevel(logging.WARNING)
        formatter = None

        # if config.uasDebug_ignoreLoggerFormatting:
        if True:
            ch = "~"  # "\u02EB"
            formatter = Formatter(ch + " {message:<140}", style="{")
        else:
            formatter = Formatter("{asctime} {levelname[0]} {name:<30}  - {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

        # handler = logging.FileHandler(get_log_file())
        # handler.setFormatter(formatter)
        # _logger.addHandler(handler)

    ###################
    # update data
    ###################

    bpy.types.WindowManager.UAS_video_tracks_version = IntProperty(
        name="Add-on Version Int", description="Add-on version as integer", default=versionTupple[1]
    )

    def on_toggle_overlay_updated(self, context):
        if self.UAS_video_tracks_overlay:
            bpy.ops.uas_video_tracks.tracks_overlay("INVOKE_DEFAULT")

    bpy.types.WindowManager.UAS_video_tracks_overlay = BoolProperty(
        name="Toggle Overlay", default=False, update=on_toggle_overlay_updated
    )

    # utils_handlers.removeAllHandlerOccurences(
    #     checkDataVersion_post_load_handler, handlerCateg=bpy.app.handlers.load_post
    # )
    # bpy.app.handlers.load_post.append(checkDataVersion_post_load_handler)

    # if config.uasDebug:
    #     utils_handlers.displayHandlers(handlerCategName="load_post")

    # initialization
    ##################

    # data version is written in the initialize function
    # bpy.types.WindowManager.UAS_shot_manager_isInitialized = BoolProperty(
    #     name="Shot Manager is initialized", description="", default=False
    # )

    # utils_handlers.displayHandlers()
    #   utils_handlers.removeAllHandlerOccurences(jump_to_shot, handlerCateg=bpy.app.handlers.frame_change_pre)
    # utils_handlers.removeAllHandlerOccurences(
    #     jump_to_shot__frame_change_post, handlerCateg=bpy.app.handlers.frame_change_post
    # )
    # utils_handlers.displayHandlers()

    # for cls in classes:
    #     bpy.utils.register_class(cls)

    otio.register()

    addon_prefs.register()

    markers_nav_bar.register()
    time_controls_bar.register()

    utils_operators.register()
    #   utils_vse.register()

    # operators
    prefs.register()
    # markers_nav_bar_addon_prefs.register()

    vse_render.register()

    general.register()

    vt_props.register()
    tracks.register()
    vt_tools.register()

    # ui
    vt_ui.register()
    vt_panels_ui.register()
    vt_time_controls_ui.register()

    sequencer_draw.register()

    about.register()

    if config.uasDebug:
        print(f"\n ------ UAS debug: {config.uasDebug} ------- ")
        print(f" ------ _Logger Level: {logging.getLevelName(_logger.level)} ------- \n")


def unregister():

    from .operators import prefs
    from .operators import general
    from .operators import tracks

    from . import otio
    from .properties import vt_props

    # from .ui.vsm_ui import UAS_PT_VideoTracks
    from .ui import vt_ui
    from .ui import vt_panels_ui
    from .ui import vt_time_controls_ui

    from .operators import about
    from .operators import vt_tools

    from .properties import addon_prefs

    from .tools import vse_render
    from .tools import markers_nav_bar
    from .tools import time_controls_bar

    from .utils import utils_operators

    from .opengl import sequencer_draw

    print("\n*** --- Unregistering UAS Video Tracks Add-on --- ***\n")

    # utils_handlers.removeAllHandlerOccurences(
    #     checkDataVersion_post_load_handler, handlerCateg=bpy.app.handlers.load_post
    # )

    # debug tools
    # if config.uasDebug:
    #     sm_debug.unregister()

    try:
        sequencer_draw.unregister()
    except Exception:
        print("Error (handled) in Unregister sequencer_draw")
    vt_time_controls_ui.unregister()
    vt_panels_ui.unregister()
    vt_ui.unregister()
    vt_tools.unregister()
    tracks.unregister()
    vt_props.unregister()
    prefs.unregister()
    general.unregister()

    vse_render.unregister()

    # ui
    about.unregister()

    utils_operators.unregister()
    time_controls_bar.unregister()
    markers_nav_bar.unregister()
    # markers_nav_bar_addon_prefs.unregister()

    addon_prefs.unregister()

    otio.unregister()
    #  utils_vse.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.UAS_video_tracks_version

    config.releaseGlobalVariables()

