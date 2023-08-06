#!/usr/bin/python3


CRED = '\033[31m'
CEND = '\033[0m'
CSI = '\x1B['

code = {
    'black': '0',
    'red': '1',
    'green': '2',
    'yellow': '3',
    'blue': '4',
    'purple': '5',
    'cyan': '6',
    'white': '7',
}

stl = dict()
stl['normal'] = '0'
stl['bold'] = '1'
stl['italic'] = '3'
stl['underline'] = '4'

fg = dict()
for color in code:
    fg[color] = '3' + code[color]

bg = dict()
for color in code:
    bg[color] = '4' + code[color]


class Template:
    @staticmethod
    def highlight_text( text='fill a text', style='normal', front='blue', back='yellow'):
        return CSI + stl[style] + ';' + fg[front] + ';' + bg[back] + 'm' + str(text) + CEND
    
    @staticmethod
    def color_text(text='fill a text', style='normal', front='blue', back='yellow'):
        return '\33[3' + code[front] + 'm' + str(text) + CEND
    
    @staticmethod
    def stylish_text(text='fill a text', style='normal', front='blue', back='yellow'):
        return'\33[' + stl[style] + 'm' + str(text) + CEND
