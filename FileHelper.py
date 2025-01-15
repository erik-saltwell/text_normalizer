from os import path

class FileHelper:
    @staticmethod    
    def LoadString(file_path : str)->str:
        output:str = ''
        with open(file_path, 'r', encoding='utf-8') as f:
            output = f.read()
        return output
    
    @staticmethod
    def SaveString(filename:str, output_dir : str, text : str)->None:
        file_path = path.join(output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            output = f.write(text)