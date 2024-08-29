import os
import shutil
from src.utils import Utilities


class StartUp:
    def __init__(self):
        self.startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        self.program_batfilename = Utilities.load_params()['program_batfilename']

    def add_to_startup(self):
        if self.is_program_batfile_in_startup_dir():
            print("Shortcut already exists in startup.")
            return
        
        program_batfile_abspath = os.path.abspath(self.program_batfilename)
        path_of_program_batfile_in_startup_dir = self.get_program_batfilepath_in_start_up_dir()
        print(f"abspath is: {path_of_program_batfile_in_startup_dir}")

        if not os.path.exists(program_batfile_abspath):
            raise Exception("Program batfile does't exist. Setting as startup app. failed.")
        
        shutil.copy(program_batfile_abspath, path_of_program_batfile_in_startup_dir)
        print("Shortcut added to startup.")
            

    def is_program_batfile_in_startup_dir(self):
        path_of_program_batfile_in_startup_dir = self.get_program_batfilepath_in_start_up_dir()
        
        if os.path.exists(path_of_program_batfile_in_startup_dir):
            return True
        else:
            return False

    def get_program_batfilepath_in_start_up_dir(self):
        return os.path.join(self.startup_folder, self.program_batfilename)
    

if __name__ == "__main__":
    start_up = StartUp()
    start_up.add_to_startup()
