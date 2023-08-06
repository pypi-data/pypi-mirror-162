# ============================      myRoot  ============================

# + Importacion de librerias
import sys
sys.dont_write_bytecode = True
import os

class MasteRoot:

    def __init__(self, extra_paths=[]):
        self.default_paths = ['App', 'Main', 'bookstore', 'modules'];
        self.extra_paths = extra_paths;

    def setRoot(self):
        paths = self.default_paths + self.extra_paths;

        folder_path = os.getcwd().replace('\\','/')+ '/'; 
        for sub_folder in paths:
            folder_path = folder_path.replace(f'/{sub_folder}', '');

        sys.path.insert(1,folder_path);
        return folder_path

