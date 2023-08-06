# ============================      myRoot  ============================

# + Importacion de librerias
import sys
sys.dont_write_bytecode = True
import os

class MasterRoot:
    def __init__(self):
        self.default_paths = ['App', 'Main', 'bookstore', 'modules'];

    def setRoot(self, extra_paths=[]):
        paths = self.default_paths + extra_paths if type(extra_paths)==list else self.default_paths + [extra_paths];

        folder_path = os.getcwd().replace('\\','/')+ '/'; 
        for sub_folder in paths:
            folder_path = folder_path.replace(f'/{sub_folder}', '');

        sys.path.insert(1,folder_path);
        return folder_path

# Setea la ruta por default
folder_path = MasterRoot().setRoot();