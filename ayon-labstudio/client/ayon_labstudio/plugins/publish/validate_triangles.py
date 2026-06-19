# -*- coding: utf-8 -*-
import ayon_maya.api.action
from ayon_core.pipeline.publish import (
    OptionalPyblishPluginMixin,
    PublishValidationError,
    ValidateMeshOrder,
)
from ayon_maya.api import plugin
from maya import cmds


class ValidateMeshTriangulated(plugin.MayaInstancePlugin,
                                     OptionalPyblishPluginMixin):
    """Validate if the geometry does not contain any triangles"""

    order = ValidateMeshOrder
    families = ["model"]
    optional = True
    label = "Mesh contain triangles"
    actions = [ayon_maya.api.action.SelectInvalidAction]

    @classmethod
    def get_invalid(cls, instance):
        invalid = []
        meshes = cmds.ls(instance, type="mesh", long=True)
        for mesh in meshes:
            faces = cmds.polyEvaluate(mesh, face=True)
            tris = cmds.polyEvaluate(mesh, triangle=True)
            if faces != int(tris/2):
                invalid.append(mesh)

        return invalid

    def process(self, instance):
        if not self.is_active(instance.data):
            return
        invalid = self.get_invalid(instance)
        if invalid:
            raise PublishValidationError("Meshes with triangles")