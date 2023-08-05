import os
from feiticeiro_tec.generator.tree import generate_tree
class Project():
    def __init__(self,file_root,project_name):
        self.root_path = os.path.dirname(file_root)
        self.project_name = project_name
    def start(self):
        tree = {
            self.project_name:[
                ['__init__.py'],
                {"database":['__init__.py',{"models":["model.py"]}]},
                {"blueprints": ['__init__.py']},
                {"templates": ['base.html']}
            ]
        }
        textos = {
            f'/{self.project_name}/__init__.py': open(f'{os.path.dirname(__file__)}/app.txt').read().format(project_name=self.project_name),
            f'/{self.project_name}/database/__init__.py': open(f'{os.path.dirname(__file__)}/database.txt').read(),
            f'/{self.project_name}/database/models/model.py':open(f'{os.path.dirname(__file__)}/model.txt').read(),
            f'/{self.project_name}/blueprints/__init__.py': open(f'{os.path.dirname(__file__)}/blueprint.txt').read(),
            f'/{self.project_name}/templates/base.html': open(f'{os.path.dirname(__file__)}/base.txt').read()
        }
        generate_tree(self.root_path,tree,textos)
