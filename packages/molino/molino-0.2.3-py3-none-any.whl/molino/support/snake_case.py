from re import sub

def snake_case(string):
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        string.replace('-', ' '))
    ).split()).lower()