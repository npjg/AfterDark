#!/usr/bin/python

from dataclasses import dataclass
from typing import Dict
import logging

import self_documenting_struct as struct
import nefile
from nefile.resource_table import ResourceType as NEResourceType

from resources import Control, Palette, Rdat, Rlep, EngineString, StringList

@dataclass
class ResourceType:
    # These resources display on the engine interface.
    AD_CONTROL = 1000
    AD_STRING = 2000
    # The module only uses these resources internally.
    AD_WAV = 3000
    AD_PALETTE = 'PAL'
    AD_IMAGECONFIG = 'RDAT'
    AD_IMAGES = 'RLEP'
    AD_STRINGS = 'STRINGLIST'

## A Windows 16-bit After Dark module.
class Win16Module:
    MODULE_RESOURCE_PARSERS = {
        ResourceType.AD_CONTROL: Control.Control,
        ResourceType.AD_STRING: EngineString.EngineString,
        ResourceType.AD_PALETTE: Palette.Palette,
        ResourceType.AD_IMAGECONFIG: Rdat.Rdat,
        ResourceType.AD_IMAGES: Rlep.Rlep,
        ResourceType.AD_STRINGS: StringList.StringList
    }

    def __init__(self, module_filepath, string_encoding = 'latin-1'):
        # OPEN THE EXECUTABLE.
        # This gives easy access to the resources in this executable.
        self.executable = nefile.NE(module_filepath, user_defined_resource_parsers = self.MODULE_RESOURCE_PARSERS)

        # READ THE ENGINE STRINGS.
        # If no AD_STRING resources are present, an empty dictionary is returned
        # so the respective engine strings are None.
        strings = self.executable.resource_table.resources.get(ResourceType.AD_STRING, {})
        # The credit string is usually two lines with authorship and copyright information.
        self.credit_string = strings.get(EngineString.Type.RES_CREDIT)
        # The module name is very short - it only displays in the module list.
        self.module_name = strings.get(EngineString.Type.RES_NAME)
        # The about box text is a few sentences that describe the module in more detail.
        self.about_text = strings.get(EngineString.Type.RES_ABOUT)

        # READ THE CONTROLS.
        # There can be up to 4 controls.
        self.controls = self.executable.resource_table.resources.get(ResourceType.AD_CONTROL)

        # GET THE ICON.
        self.thumb_resource = self.executable.resource_table.find_resource_by_id(
            resource_id = 42, type_id = NEResourceType.RT_GROUP_ICON)

        # READ THE AUDIO.
        self.audios = self.executable.resource_table.resources.get(ResourceType.AD_WAV)

        # FIND THE PALETTE RESOURCES.
        # Irritatingly, the resource type IDs are not consistent across modules.
        # Some modules give resources names, but most modules do not give them names.
        # And the IDs given in place of names are inconsistent. For instance,
        # BADDOG.AD gives palettes type ID 32513. But TOILET.AD gives palettes 
        # type ID 32516. Thus, the resource type IDs cannot be relied upon.
        # We must detect the types by looking at the data itself.
        if self.no_descriptive_resource_type_names:
            self.palettes = {}
            self.strings = {}
            self.rdats = {}
            self.rleas = {}
            # TODO: Is there any other way than manual inspection that we can find what is what?
            for resource_type, resource_list in self.executable.resource_table.resources.items():
                logging.warning('Resources were not given names in the executable. Using heuristics to identify resources. There may be trouble ahead...')
                first_resource = resource_list[0]
                # FIND THE RLEAs.
                # These are easy, as we just need to look for the signature.
                signature = first_resource.data.read(4)
                if signature == b'RLID':
                    pass
                elif signature == b'\x00\x00\x00\x00':
                    # RDAT
                    pass
                elif signature == b'\x00\x03\x00\x00':
                    # PALETTE
                    pass
                else:
                    # OUTPUT.
                    pass
        else:
            self.palettes = self.executable.resource_table.resources.get(ResourceType.AD_PALETTE)
            self.strings = self.executable.resource_table.resources.get(ResourceType.AD_STRINGS, {})
            self.rdats = self.executable.resource_table.resources.get(ResourceType.AD_IMAGECONFIG, {})
            self.rleas = self.executable.resource_table.resources.get(ResourceType.AD_IMAGES, {})

        assert self.rdats.keys() == self.rleas.keys()

    ## Some modules give resource types descriptive string IDs, which is really nice.
    ## But most modules assign high numeric IDs (>32500 or so) to resource types.
    @property
    def no_descriptive_resource_type_names(self) -> bool:
        for resource_type in self.executable.resource_table.resources.keys():
            # SEARCH FOR DESCRIPTIVE RESOURCE TYPE NAMES.
            # These will always be plain strings.
            if isinstance(resource_type, str):
                # INDICATE A DESCRIPTIVE TYPE NAME WAS FOUND.
                return False

        # INDICATE NO DESCRIPTIVE RESOURCE TYPE NAMES WERE FOUND.
        return True

shell_dll = Win16Module("/home/npgentry/reversing/after-dark/AFTERDRK/AD30/TOASTER3.AD")
print("HELLO")