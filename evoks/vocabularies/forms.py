from django import forms


class Vocabulary_Terms_Form(forms.Form):
    OPTIONS = (
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E'),
        ('f', 'F'),
        ('g', 'G'),
        ('h', 'H'),
        ('i', 'I'),
        ('j', 'J'),
        ('k', 'K'),
        ('l', 'L'),
        ('m', 'M'),
        ('n', 'N'),
        ('o', 'O'),
        ('p', 'P'),
        ('q', 'Q'),
        ('r', 'R'),
        ('s', 'S'),
        ('t', 'T'),
        ('u', 'U'),
        ('v', 'V'),
        ('w', 'W'),
        ('x', 'X'),
        ('y', 'Y'),
        ('z', 'Z'),
    )
    initial_letter = forms.ChoiceField(required=False, choices=OPTIONS)


class Property_Predicate_Form(forms.Form):
    OPTIONS = (
        ('skos:altLabel', 'Synonym (Freetext)'),
        ('skos:definition', 'Definition (Freetext)'),
        ('skos:broader', 'Broader term (semantic relation)'),
        ('skos:narrower', 'Narrower term (semantic relation)'),
        # ('dc:description', 'dc:description'),
    )
    PREFIXES = (
        ('skos', 'skos'),
        # ('dc', 'dc'),
    )
    DATATYPE_PREFIXES = (
        ('xsd', 'xsd'),
    )
    DATATYPE_OPTIONS = (
        ('xsd:boolean', 'xsd:boolean'),
        ('xsd:decimal', 'xsd:decimal'),
        ('xsd:float', 'xsd:float'),
        ('xsd:double', 'xsd:double'),
        ('xsd:duration', 'xsd:duration'),
        ('xsd:dateTime', 'xsd:dateTime'),
        ('xsd:time', 'xsd:time'),
        ('xsd:date', 'xsd:date'),
        ('xsd:gYearMonth', 'xsd:gYearMonth'),
        ('xsd:gYear', 'xsd:gYear'),
        ('xsd:gMonthDay', 'xsd:gMonthDay'),
        ('xsd:gDay', 'xsd:gDay'),
        ('xsd:gMonth', 'xsd:gMonth'),
        ('xsd:hexBinary', 'xsd:hexBinary'),
        ('xsd:base64Binary', 'xsd:base64Binary'),
        ('xsd:anyURI', 'xsd:anyURI'),
        ('xsd:QName', 'xsd:QName'),
        ('xsd:NOTATION', 'xsd:NOTATION'),
    )
    predicate = forms.ChoiceField(required=False, choices=OPTIONS)
    prefix = forms.ChoiceField(required=False, choices=PREFIXES)
    datatype = forms.ChoiceField(required=False, choices=DATATYPE_OPTIONS)
    datatype_prefix = forms.ChoiceField(
        required=False, choices=DATATYPE_PREFIXES)


class CreateVocabularyForm(forms.Form):
    """Represents the input necessary to create a vocabulary

    Args:
        forms: Subclasses the Django Form class
    """
    name = forms.SlugField(max_length=50)
    urispace = forms.CharField(max_length=100, required=False)
