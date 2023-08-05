from contextlib import suppress
class CPF():
    def __init__(self,cpf:str):
        self._is_string(cpf)
        self._cpf = self._validation_len(cpf)

    def _is_string(self,cpf:str):
        if type(cpf) != str:
            raise TypeError('CPF Invalido, Requer String.')

    def _validation_len(self,cpf:str):
        cpf = cpf.strip()
        with suppress(Exception):
            if len(cpf) == 14:
                for index,valor in enumerate(cpf):
                    if index in (0,1,2,4,5,6,8,9,10,12,13) and not valor.isnumeric():
                        raise ValueError()
                    elif index in (3,7) and  valor != '.':
                        raise ValueError()
                    elif valor != '-':
                        raise ValueError()
                return cpf

        with suppress(Exception):
            if cpf.index('.')>=0:
                cpf = cpf.replace('.','')
        with suppress(Exception):
            if cpf.index('-')>=0:
                cpf = cpf.replace('-','')

        if len(cpf) == 11:
            for index,valor in enumerate(cpf):
                if not valor.isnumeric():
                    raise ValueError('Valores Não Numéricos Foram Passados.')
            return self.format_to_cpf(cpf)

    def format_to_cpf(self,cpf:str):
        cpf_ = ''
        cpf_ += cpf[:3]+'.'
        cpf_ += cpf[3:6]+'.'
        cpf_ += cpf[6:9]+'-'
        cpf_ += cpf[9:]
        return cpf_

    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self,cpf):
        self.__is_string(cpf)
        self._cpf = self.__validation_len(cpf)

    def __str__(self) -> str:
        return self._cpf
