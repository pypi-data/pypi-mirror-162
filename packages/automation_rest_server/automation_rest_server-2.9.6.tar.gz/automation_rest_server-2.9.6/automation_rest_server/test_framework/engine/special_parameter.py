
import os
import sys
from test_framework.firmware_engine.models.firmware_path import FirmwareBinPath


class Parameters(object):

    def __init__(self):
        self.fw_path_manage = FirmwareBinPath()

    def pop_parm(self, parameters, key):
        if key in parameters.keys():
            parameters.pop(key)
        return parameters

    @staticmethod
    def get_default_base_path():
        if "win" in sys.platform.lower():
            base_path = r"\\172.29.190.4\share\sqa\FW_Release\redtail"
        else:
            base_path = "/home/share/sqa/FW_Release/redtail"
        return base_path

    def get_default_base_path_enhance(self, parameters):
        if "base_path" in parameters.keys():
            return parameters["base_path"]
        if "fw_path" in parameters.keys():
            print("fw_path in parameters.keys...")
            temp_path = parameters["fw_path"]
            if "172.29.190.4" in temp_path:
                if "win" in sys.platform.lower():
                    base_path = temp_path
                else:
                    temp_path1 = temp_path.replace("\\\\172.29.190.4", "/home")
                    base_path = temp_path1.replace("\\", "/")
                    print("Linux perses base path: ", base_path)
            else:
                print("can not find share and 172.29.190.4")
                base_path = self.get_default_base_path()
        else:
            print("fw_path not in parameters.keys()")
            base_path = self.get_default_base_path()
        return base_path

    def generate_redtail_images(self, parameters):
        output_parm = dict()
        volume = parameters.get("volume", "ALL")
        base_path = self.get_default_base_path_enhance(parameters)
        nand = parameters.get("nand", "BICS4")
        if "image1" not in parameters.keys() and "base_version" in parameters.keys():
            ret = self.get_image_path(base_path, volume, parameters["base_version"], nand)
            if ret is not None:
                output_parm["image1"] = ret
                output_parm["base_version"] = parameters["base_version"]
        if "image2" not in parameters.keys():
            if "target_version" in parameters.keys():
                ret = self.get_image_path(base_path, volume, parameters["target_version"], nand)
                if ret is not None:
                    output_parm["image2"] = ret
                    output_parm["target_version"] = parameters["target_version"]
            else:
                if "image1" in output_parm.keys():
                    output_parm["image2"] = output_parm["image1"]
                    output_parm["target_version"] = output_parm["base_version"]
        return output_parm

    def get_image_path(self, base_path, volume, commit_id, nand):
        nand = "ALL" if volume.lower() == "all" else nand
        _files = os.listdir(base_path)
        if os.path.exists(base_path):
            for item in _files:
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    ret = self.get_image_path(item_path, volume, commit_id, nand)
                    if ret is not None:
                        return ret
                elif ("_{}_".format(volume) in item) and ("preBootloader" not in item) and \
                        item.endswith(".bin") and ("_{}_".format(nand) in item):
                    return os.path.join(base_path, item)

    def update_perses_fw_path(self, parameters):
        if "fw_path" in parameters.keys():
            if os.path.exists(parameters["fw_path"]) is True and os.path.isfile(parameters["fw_path"]):
                return parameters  # when user send a bin file fw path skip update fw_path parameters
        if "commit" in parameters.keys():
            commit = parameters["commit"]
            volume = parameters.get("volume", "ALL")
            nand = parameters.get("nand", "BICS4")
            base_path = self.get_default_base_path_enhance(parameters)
            fw_path = self.get_image_path(base_path, volume, commit, nand)
            if fw_path is not None:
                parameters["fw_path"] = fw_path
        return parameters
