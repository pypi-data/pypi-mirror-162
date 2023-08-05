class ExtractClass():
    _default_selection_extract = None
    def __getitem__(self,selection):
        """Faz a Seleção De Attr Como Seletor obj['attr','attr']"""
        if type(selection) == slice:
            raise TypeError('Seleção e não slice!')
        data = {}
        for attr in selection:
            data[attr] = getattr(self,attr,self._default_selection_extract)
        return data