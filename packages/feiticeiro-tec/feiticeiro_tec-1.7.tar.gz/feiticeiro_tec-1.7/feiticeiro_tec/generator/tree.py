from ..station import OpenFile
import os
def generate_tree(path_root,tree_dict,text_dict,target=''):
    """Gera Uma Árvore De Arquivos e Escrever Em Cada Arquivo.

    tree_dict = {
    'root':{
        "database":['__init__.py'],
        "blueprints":['__init__.py'],
        "templates":['base.html']}
    }
    text_dict = {
        "/root/database/__init__.py":'databse',
        "/root/blueprints/__init__.py":'blueprints',
        "/root/templates/base.html":'templates'
    }
    """
    for key,value in tree_dict.items():
        OpenFile(path_root+'/'+key,True)
        if type(value) == dict:
            generate_tree(path_root+'/'+key,value,text_dict,target+'/'+key)
        elif type(value) in (tuple,list):
            for file in value:
                if type(file) == dict:
                    generate_tree(path_root+'/'+key, file,text_dict, target+'/'+key)
                elif type(file) in (tuple, list):
                    for i in file:
                        if type(text_dict[target+'/'+key+'/'+i]) == str:
                            with OpenFile(path_root+'/'+key+'/'+i, 'w', True) as filer:
                                filer.write(text_dict[target+'/'+key+'/'+i])
                elif type(text_dict[target+'/'+key+'/'+file]) == str:
                    with OpenFile(path_root+'/'+key+'/'+file,'w',True) as filer:
                        filer.write(text_dict[target+'/'+key+'/'+file])
                else:
                    with OpenFile(path_root+'/'+key+'/'+file,'wb',True) as filer:
                        filer.write(text_dict[target+'/'+key+'/'+file])
