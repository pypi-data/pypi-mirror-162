from contextlib import suppress
def xml_get_column(text: str,column:str, after=[]):
    """Pega o text De Uma String Com Estrutura De XML.

    text = '''
    <ColumnaA>
        <ColumnaB>
            <ColumnaA>
                <ColumnaB></ColumnaB>
            </ColumnaA>
            <ColumnaA>
                <ColumnaB></ColumnaB>
            </ColumnaA>
            <ColumnaB> Aqui </ColumnaB>
        </ColumnaB>
    </ColumnaA>
    '''

    column = 'ColumnaB'

    after = ['</ColumnaA>','</ColumnaA>']

    """
    with suppress(Exception):
        for col in after:
            text = text[text.find(col)+len(col):]
        start = f'<{column}>'
        end = f'</{column}>'
        if text.find(start) == -1 or text.find(start) == -1:
            return False
        text = text[text.find(start)+len(start):]
        text = text[:text.find(end)]
        return text