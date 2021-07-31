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
