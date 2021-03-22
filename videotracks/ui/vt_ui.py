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
To do: module description here.
"""

import bpy

from bpy.types import Panel, Menu, Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

from videotracks.utils import utils
from videotracks.properties import vt_props
from videotracks.operators import tracks

import videotracks.config as config


######
# Video Tracks main panel #
######


class UAS_PT_VideoTracks(Panel):
    bl_label = "UAS Video Tracks   V. " + utils.addonVersion("UAS Video Tracks")[0]
    bl_idname = "UAS_PT_Video_Tracks"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Video Tracks"

    def draw_header(self, context):
        props = context.scene.UAS_video_tracks_props
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # if context.window_manager.UAS_video_shot_manager_displayAbout:
        #     row.alert = True
        # else:
        #     row.alert = False

        icon = config.vt_icons_col["General_Ubisoft_32"]
        row.operator("uas_video_tracks.about", text="", icon_value=icon.icon_id)

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        # row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        # row.separator(factor=2)
        icon = config.vt_icons_col["General_Explorer_32"]
        row.operator("uas_video_tracks.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            bpy.data.filepath
        )

        row.separator(factor=1)
        row.menu("UAS_MT_Video_Tracks_prefs_mainmenu", icon="PREFERENCES", text="")

        # row.separator(factor=3)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props

        # if not "UAS_shot_manager_props" in context.scene:
        if not vt_props.isInitialized:
            layout.separator()
            row = layout.row()
            row.alert = True
            row.operator("uas_video_tracks.initialize")
            layout.separator()

        # if 32 > vt_props.numTracks:
        #     vt_props.numTracks = 32

        # scene warnings
        ################

        if config.uasDebug:
            row = layout.row()
            subRow = row.row()
            subRow.alert = True
            subRow.label(text=" " + ("  Debug  " if config.uasDebug else ""))

        row = layout.row()
        vseFirstFrame = scene.frame_start
        if vseFirstFrame != 0:
            # wkip RRS Specific
            if not (
                scene.name.startswith("Act01_Seq")
                or scene.name.startswith("Act02_Seq")
                or scene.name.startswith("Act03_Seq")
            ):
                subRow = row.row()
                subRow.alert = True
                subRow.label(text=f" ***    First Frame is not 0 !!!: {vseFirstFrame}    *** ")

        #########################################
        # Tools
        #########################################

        if 1 < len(bpy.data.scenes):
            row = layout.row(align=True)
            row.separator(factor=1)
            row.prop(vt_props, "jumpToScene", text="")
            if vt_props.jumpToScene is None:
                #                vt_props.jumpToScene = bpy.data.scenes[0] if bpy.data.scenes[0] is not context.scene else bpy.data.scenes[1]
                subRow = row.row()
                subRow.enabled = False
                subRow.alert = True
                subRow.operator("uas_video_tracks.go_to_scene", text="Jump to Scene")
            else:
                row.operator("uas_video_tracks.go_to_scene", text="Jump to Scene").sceneName = vt_props.jumpToScene.name
            row.separator(factor=1)
            # icon="SCENE_DATA"

        #########################################
        # Tracks
        #########################################

        layout.separator(factor=2)
        row = layout.row()
        row.label(text="Tracks:")

        if config.uasDebug:
            row.prop(vt_props, "numTracks")
        row.operator("uas_video_tracks.update_tracks_list", text="", icon="FILE_REFRESH")
        subRow = row.row(align=True)
        if config.uasDebug:
            subRow.operator("uas_video_tracks.clear_all")
        subRow.menu("UAS_MT_Video_Tracks_clear_menu", icon="TRIA_RIGHT", text="")

        box = layout.box()
        row = box.row()
        templateList = row.template_list(
            "UAS_UL_VideoTracks_Items", "", vt_props, "tracks", vt_props, "selected_track_index_inverted", rows=6,
        )

        col = row.column(align=True)
        if config.uasDebug:
            col.operator("uas_video_tracks.add_track", icon="ADD", text="")
            col.operator("uas_video_tracks.duplicate_track", icon="DUPLICATE", text="")
            col.operator("uas_video_tracks.remove_track", icon="REMOVE", text="")
            col.separator()
        col.operator("uas_video_tracks.move_treack_up_down", icon="TRIA_UP", text="").action = "UP"
        col.operator("uas_video_tracks.move_treack_up_down", icon="TRIA_DOWN", text="").action = "DOWN"
        col.separator()
        col.menu("UAS_MT_Video_Tracks_toolsmenu", icon="TOOL_SETTINGS", text="")

    # layout.separator ( factor = 1 )


#############
# tracks
#############


class UAS_UL_VideoTracks_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        global vt_icons_col
        vt_props = context.scene.UAS_video_tracks_props
        prefs = context.preferences.addons["videotracks"].preferences

        if not (
            "CUSTOM" == item.trackType
            or "STANDARD" == item.trackType
            or "AUDIO" == item.trackType
            or "VIDEO" == item.trackType
        ):
            layout.alert = item.shotManagerScene is None

        row = layout.row(align=True)

        if vt_props.display_color_in_tracklist:
            row.scale_x = 0.3
            row.prop(item, "color", text="")
            row.separator(factor=0.2)

        row = layout.row(align=True)
        subRow = row.row(align=False)
        subRow.scale_x = 0.3
        subRow.prop(item, "enabled", text=f" ")
        # subrow.separator(factor=0.2)
        row.label(text=f" {item.vseTrackIndex}: {item.name}")

        # c.operator("uas_video_tracks.set_current_shot", icon_value=icon.icon_id, text="").index = index
        # layout.separator(factor=0.1)

        row = layout.row(align=True)

        ###############
        # volume and opacity
        if vt_props.display_opacity_or_volume_in_tracklist:
            row.scale_x = 0.5
            if "AUDIO" == item.trackType:
                row.prop(item, "volume", text="")
            else:
                row.prop(item, "opacity", text="")
            row.separator(factor=0.2)

        ###############
        # track type
        if vt_props.display_track_type_in_tracklist:
            subRow = row.row(align=True)
            subRow.scale_x = 1.3
            subRow.prop(item, "trackType", text="")
            subSubRow = subRow.row(align=True)
            subSubRow.scale_x = 1.2

            if (
                "CUSTOM" == item.trackType
                or "STANDARD" == item.trackType
                or "AUDIO" == item.trackType
                or "VIDEO" == item.trackType
            ):
                subSubRow.enabled = False
                subSubRow.prop(prefs, "emptyBool", text="", icon="BLANK1")
                subSubRow.prop(prefs, "emptyBool", text="", icon="BLANK1")
                pass
            else:

                #     if item.shotManagerScene is None:
                #         grid_flow.alert = True
                #     grid_flow.prop(item, "shotManagerScene", text="")
                #     if item.shotManagerScene is None:
                #         grid_flow.alert = False

                #     if item.shotManagerScene is None or item.sceneTakeName == "":
                #         grid_flow.alert = True
                #     grid_flow.prop(item, "sceneTakeName", text="")
                #     if item.shotManagerScene is None:
                #         grid_flow.alert = False

                #   grid_flow.scale_x = 1.0
                subSubRow.operator(
                    "uas_video_tracks.update_vse_track", text="", icon="FILE_REFRESH"
                ).trackName = item.name

                subSubRow.operator(
                    "uas_video_tracks.go_to_specified_scene", text="", icon="SCENE_DATA"
                ).trackName = item.name
            # grid_flow.scale_x = 1.8


# ##################
# # track properties
# ##################


class UAS_PT_VideoTracks_TrackProperties(Panel):
    bl_label = " "  # "Current Track Properties" # keep the space !!
    bl_idname = "UAS_PT_Video_Tracks_TrackProperties"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    bl_parent_id = "UAS_PT_Video_Tracks"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        vt_props = context.scene.UAS_video_tracks_props
        track = vt_props.getTrackByIndex(vt_props.selected_track_index)
        return track is not None

    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        row.label(text="Selected Track Properties")

    def draw_header_preset(self, context):
        vt_props = context.scene.UAS_video_tracks_props
        layout = self.layout
        # layout.emboss = "NONE"

        row = layout.row(align=True)
        op = row.operator("uas_video_tracks.select_track_from_clip_selection", text="Sel. Track")
        op = row.operator("uas_video_tracks.track_select_and_zoom_view", text="Zoom on Clips")
        op.actionMode = "TRACKCLIPS"
        op.trackIndex = vt_props.getSelectedTrackIndex()

    def draw(self, context):
        scene = context.scene
        vt_props = scene.UAS_video_tracks_props

        track = vt_props.getTrackByIndex(vt_props.selected_track_index)

        layout = self.layout

        if track is not None:
            box = layout.box()

            # channel
            row = box.row()
            row.separator(factor=1.0)
            row.label(text=f"Channel: {track.vseTrackIndex}")

            # name and color
            row = box.row()
            row.separator(factor=1.0)
            row.prop(track, "name", text="Name")
            row.prop(track, "color", text="")
            row.prop(vt_props, "display_color_in_tracklist", text="")

            row = box.row()
            row.separator(factor=1.0)
            if "AUDIO" == track.trackType:
                row.prop(track, "volume", text="Volume")
            else:
                row.prop(track, "opacity", text="Opacity")
            row.prop(vt_props, "display_opacity_or_volume_in_tracklist", text="")

            row = box.row()
            row.separator(factor=1.0)
            row.prop(track, "trackType")
            row.prop(vt_props, "display_track_type_in_tracklist", text="")

            row = box.row()
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)

            if "CUSTOM" == track.trackType:
                layout.separator()
                row = layout.row()
                row.operator("uas_video_tracks.clear_vse_track")
                pass

            elif "STANDARD" == track.trackType or "AUDIO" == track.trackType or "VIDEO" == track.trackType:
                layout.separator()
                row = layout.row()
                row.operator("uas_video_tracks.clear_vse_track")
                pass

            else:
                if track.shotManagerScene is None:
                    grid_flow.alert = True
                grid_flow.prop(track, "shotManagerScene")
                if track.shotManagerScene is None:
                    grid_flow.alert = False

                if track.shotManagerScene is None:
                    grid_flow.alert = True
                grid_flow.prop(track, "sceneTakeName")
                if track.shotManagerScene is None:
                    grid_flow.alert = False

                layout.separator()
                row = layout.row()
                row.operator("uas_video_tracks.clear_vse_track")
                row.operator("uas_video_tracks.update_vse_track", icon="FILE_REFRESH").trackName = track.name
                row.operator("uas_video_tracks.go_to_specified_scene", icon="SCENE_DATA").trackName = track.name
                layout.separator()


#################
# tools for tracks
#################


class UAS_MT_VideoTracks_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Video_Tracks_toolsmenu"
    bl_label = "Tracks Tools"
    bl_description = "Tracks Tools"

    def draw(self, context):

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        # row.label(text="Tools for Tracks:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_tracks.remove_multiple_tracks", text="   Remove Disabled Tracks").action = "DISABLED"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_tracks.remove_multiple_tracks", text="   Remove All Tracks").action = "ALL"

        # import edits
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Import Edits:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uasotio.openfilebrowser", text="   Import Edit From EDL").importMode = "IMPORT_EDIT"

        # export edits
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Export Edits:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "uas_video_tracks.export_content_between_markers", text="   Batch Export Content Between Markers..."
        )

        layout.separator()
        # wkip debug - to remove:
        if config.uasDebug:
            row = layout.row(align=True)
            row.operator("uas_video_tracks.importeditfromotio", text="   Import Edit From EDL - Debug...")

        if config.uasDebug:
            row = layout.row(align=True)
            row.operator(
                "uas_video_tracks.importeditfromotio", text="   Import Edit From EDL - Debug + file"
            ).otioFile = (
                # r"Z:\_UAS_Dev\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
                r"Z:\EvalSofts\Blender\DevPython_Data\UAS_VideoTracks_Data\ImportEDLPremiere\ImportEDLPremiere.xml"
                # r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere_to40.xml"  # _to40
            )

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uasotio.openfilebrowser", text="   Parse Edit From EDL").importMode = "PARSE_EDIT"

        # wkip debug - to remove:
        if config.uasDebug:
            row = layout.row(align=True)
            row.operator("uas_video_tracks.parseeditfromotio", text="   Import Edit From EDL - Debug").otioFile = ""


#########
# MISC
#########


class UAS_PT_VideoTracks_Initialize(Operator):
    bl_idname = "uas_video_tracks.initialize"
    bl_label = "Initialize Video Tracks"
    bl_description = "Initialize Video Tracks"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.UAS_video_tracks_props.initialize_video_shot_manager()

        return {"FINISHED"}


_classes = (
    UAS_PT_VideoTracks,
    UAS_PT_VideoTracks_TrackProperties,
    UAS_UL_VideoTracks_Items,
    UAS_MT_VideoTracks_ToolsMenu,
    UAS_PT_VideoTracks_Initialize,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
