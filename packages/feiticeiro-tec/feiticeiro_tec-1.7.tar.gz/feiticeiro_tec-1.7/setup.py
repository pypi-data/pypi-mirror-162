from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name='feiticeiro_tec',
    version='1.7',
    url='https://github.com/feiticeiro-tec/feiticeiro-tec',
    license='MIT License',
    author='Silvio Henrique Cruz Da Silva',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='silviohenriquecruzdasilva@gmail.com',
    keywords='Pacote',
    description=u'Um Pacote Das Mais Diversas Utilidades.',
    packages=['feiticeiro_tec', 'feiticeiro_tec/generator', 'feiticeiro_tec/generator/project', 'feiticeiro_tec/route', 'feiticeiro_tec/secury','feiticeiro_tec/station', 'feiticeiro_tec/station/extraction', 'feiticeiro_tec/station/processing', 'feiticeiro_tec/station/validation'],
    install_requires=['pyjwt'],
    extras_require={
        'server': [
            'flask',
            'flask-sqlalchemy',
            'flask-cors',
            'werkzeug'
        ]
    })