import os
class OpenFile():
    def __init__(self,path,modo='r',force=True):
        """Abre Um Arquivo De Forma Forçada."""
        self.path = path
        path_list = path.split('/')
        relative = path[0]
        self.modo = modo
        if force and not(os.path.isfile(path) or os.path.isdir(path)):
            for index,p in enumerate(path_list):
                if not os.path.isdir(relative):
                    os.mkdir(relative)
                if index != 0:
                    relative+=f'/{p}'

                if index == len(path_list)-1:
                    if self.is_filename(p):
                        with open(path,'w') as file:
                            ...

    def is_filename(self,path):
        return '.' in path

    def __enter__(self):
        self.file = open(self.path,self.modo)
        return self.file
    def __exit__(self,*args):
        self.file.close()
