import os, json, pathlib


#================================================
#  ?                    ABOUT
#  @author      : illushun
#  @repo        : N/A
#  @createdOn   : 05/08/2022
#  @description : Used for handling / creating configurations with json files.
#================================================


TEMP_STORAGE_LOCATION = 'file_handling/temp/storage.txt'


#================================================
#                FILE HANDLING
#================================================


class File:
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def create(self):
        '''
            Creates the file if it doesn't exist.
        '''
        if not os.path.exists(self.file_path):
            if not len(os.path.dirname(self.file_path)) <= 0:
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w"): pass
        return

    def get_name(self, file_extension: str):
        '''
            Returns the name of the file without the extension.
        '''
        nameSplit = self.file_path.split("/")
        for split in nameSplit:
            if split.__contains__(file_extension):
                return split.split(".")[0]
        return nameSplit(len(nameSplit) - 1).split(".")[0]
    
    def get_lines(self):
        '''
            Returns a list of lines in the file.
        '''
        self.create()
        with open(self.file_path, "r") as file:
            return file.readlines()
    
    def write(self, text: str):
        '''
            Writes the text to the file.
        '''
        self.create()
        with open(self.file_path, "w") as file:
            file.write(text)
        return

    def remove_value(self, text: str):
        '''
            Removes a value from the file.
        '''
        fileLines = self.get_lines()
        backupFileName = self.file_path + ".bak"
        File(backupFileName).create()
        
        with open(self.file_path, "w") as file:
            for line in fileLines:
                if line.find(text) == -1:
                    file.write(line)
        os.replace(backupFileName, self.file_path)
        return
    
    def contains_value(self, text: str):
        '''
            Returns true if the file contains the text.
        '''
        self.create()
        with open(self.file_path, "r") as file:
            return text in file.read()
    
    def get_value(self, key: str, backup_value: str=None):
        '''
            Returns the value of the key if it exists, otherwise returns the backup value.
        '''
        if not self.contains_value(key):
            if backup_value is not None:
                self.write(key + backup_value)
            return backup_value
        
        fileLines = self.get_lines()
        for line in fileLines:
            if line.__contains__(key):
                return line.split(":")[1].replace("\n", "")
        return backup_value
    
    def update_value(self, key: str, value: str):
        '''
            Updates the value of the key if it exists, otherwise creates the key and value.
        '''
        self.create()
        if self.contains_value(key):
            self.remove_value(key)
        self.write(value)
        return
 

#================================================
#                FOLDER HANDLING
#================================================
    
    
class Folder:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
    
    def get_files(self, file_extension: str, return_extension: bool=False):
        '''
            Returns a list of files in the folder with the given file extension.
        '''
        fileList = []
        for file in os.listdir(self.folder_path):
            if file.__contains__(file_extension):
                if return_extension:
                    fileList.append(file)
                else:
                    fileList.append(file.replace(file_extension, ""))
        return fileList
    
    def contains_file(self, file_name: str):
        '''
            Returns true if the folder contains the given file.
        '''
        return os.listdir(self.folder_path).__contains__(file_name)


#================================================
#                JSON MANAGER
#================================================


class JsonManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def convert_string(self, object: str):
        '''
            Converts a string to a json object.
        '''
        return json.loads(object)
    
    def get_object(self):
        '''
            Returns the json object of the file_path.
        '''
        File(self.file_path).create()
        if not File(self.file_path).contains_value("{"):
            File(self.file_path).write("{}")
            
        with open(self.file_path, "r") as file:
            jsonData = json.load(file)
        return jsonData

    def get_list(self, key: str):
        '''
            Returns the list of values of the key.
        '''
        return self.get_object()[key]
    
    def add_section(self, key: str, sub_section: dict):
        '''
            Adds a section to the json object.
        '''
        json_obj = self.get_object()
        with open(self.file_path, "w") as file:
            json_obj[key] = json.dumps(sub_section)
            json.dump(json_obj, file, indent=4)
        return
    
    def remove_section(self, key: str, sub_sections: list):
        '''
            Removes a section from the json object.
        '''
        json_obj = self.get_object()
        with open(self.file_path, "w") as file:
            for sub_section in sub_sections:
                del json_obj[key][sub_section]
            del json_obj[key]
            json.dump(json_obj, file, indent=4)
        return

    def remove_sub_section(self, key: str, sub_section: str):
        '''
            Removes a sub section from the json object.
        '''
        json_obj = self.get_object()
        with open(self.file_path, "w") as file:
            del json_obj[key][sub_section]
            json.dump(json_obj, file, indent=4)
        return
    
    def add_list_value(self, key: str, value):
        '''
            Adds a value to the list of the key.
        '''
        json_obj = self.get_object()
        with open(self.file_path, "w") as file:
            json_obj[key].append(value)
            json.dump(json_obj, file, indent=4)
        return
    
    def edit_list_value(self, key: str, index: int, value):
        '''
            Edits a value of the list of the key.
        '''
        json_obj = self.get_object()
        with open(self.file_path, "w") as file:
            json_obj[key][index] = value
            json.dump(json_obj, file, indent=4)
        return
    
    def remove_list_value(self, key: str, index: int):
        '''
            Removes a value of the list of the key.
        '''
        json_obj = self.get_object()
        with open(self.file_path, "w") as file:
            json_obj[key].pop(index)
            json.dump(json_obj, file, indent=4)
        return
   
   
#================================================
#                CONFIG HANDLING
#================================================
   
    
class Config:
    '''
        Create json configs.
    '''
    def __init__(self, config_path: str):
        self.config_path = config_path
    
    def load_config(self, default_section: dict):
        '''
            Loads the config file if it exists, otherwise creates the config file and loads the default section.
            
            Example Section:
                
            "sub_section_name": {
                "sub_section_value" = "my_value"
            },
            "new_sub_section": {
                "something_here" = 10000,
                "something_else" = "hello"
            },
            "final_sub_section": {
                "my_value" = "have you got the hang of this yet?",   
            }
        '''
        if len(File(self.config_path).get_lines()) <= 0:
            JsonManager(self.config_path).add_section("default", default_section)
        configName = File(self.config_path).get_name(".json")
        File(TEMP_STORAGE_LOCATION).update_value("loaded_config:", "loaded_config:{}".format(configName))
        return
    
    def get_loaded(self):
        '''
            Returns the name of the loaded config.
        '''
        return File(TEMP_STORAGE_LOCATION).get_value("loaded_config:")