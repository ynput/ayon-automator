import sys
import os




def getVenvActivateCommand(venvPath):
    if sys.platform.startswith('win'):
        activate_script = os.path.join(venvPath, "Scripts", "activate")
        activate_cmd = f"{activate_script}"
    else:
        activate_script = os.path.join(venvPath, "bin", "activate")
        activate_cmd = f"source {activate_script} "
    return activate_cmd
