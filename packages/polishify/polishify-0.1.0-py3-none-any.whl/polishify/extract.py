# import string
# print(string.printable)

import argparse
import re
import json

parser = argparse.ArgumentParser(description='Polishify by Marek Narozniak, a tool that helps you get rid of old encodings in Polish text.')
parser.add_argument('input',
                    help='Input file that contains polish text to generate the dataset')
parser.add_argument('output',
                    help='Output file that will store the dataset')
parser.add_argument('--encoding',
                    default='utf-8',
                    help='Encoding of the file.')
args = parser.parse_args()

def main():
    data = None
    with open(args.input, 'rb+') as f:
        data = f.read()

    decoded = data.decode(args.encoding).lower()

    keep = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    remove = '0123456789!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~\r\n'

    for r in remove:
        decoded = decoded.replace(r, ' ')

    decoded = re.sub(' +', ' ', decoded)

    words = decoded.split(' ')
    words = list(set(words))

    polish = 'łąęźćżńó'
    dataset = {}

    for p in polish:
        selected = []
        for word in words:
            if p in word:
                selected.append(word)
        print(p, len(selected))
        dataset[p] = selected

    with open(args.output, 'w') as f:
        json.dump(dataset, f, ensure_ascii=False)
