import argparse
import sys
import re
import json

from polishify import static

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

parser = argparse.ArgumentParser(description='Polishify by Marek Narozniak, a tool that helps you get rid of old encodings in Polish text.')
parser.add_argument('--silent',
                    required=False,
                    action='store_true',
                    help='Silent mode makes it not show any output.')
parser.add_argument('input',
                    help='Input file that contains polish text with unknown encoding.')
parser.add_argument('--out',
                    help='If present, writes the utf-8 encoded text there')
parser.add_argument('--dataset',
                    help='You may use your own words reference dataset json file.')
args = parser.parse_args()


def getLowercaseWords(text):
    remove = '0123456789!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~\r\n'
    lowered = text.lower()
    for r in remove:
        lowered = lowered.replace(r, ' ')
    lowered = re.sub(' +', ' ', lowered)
    words = lowered.split(' ')
    words = list(set(words))
    return words


def isPolish(text, dataset):
    polish = 'łąęźćżńó'
    words = getLowercaseWords(text)
    for j, p in enumerate(polish):
        required_words = dataset[p]
        common = [value for value in words if value in required_words]
        if len(common) == 0:
            return False
    return True


def main():
    dataset = None
    if args.dataset:
        with open(args.dataset, 'r') as f:
            dataset = json.load(f)
    else:
        with pkg_resources.open_binary(static, 'dataset.json') as f:
            dataset = json.load(f)

    encodings = ['utf-8', 'iso-8859-2', 'windows-1250']

    data = None
    with open(args.input, 'rb+') as f:
        data = f.read()

    target_encoding = None
    for encoding in encodings:
        try:
            decoded = data.decode(encoding)
        except:
            continue
        if isPolish(decoded, dataset):
            target_encoding = encoding
            if not args.silent:
                print('detected encoding is: ', encoding)
            break

    if args.out:
        if not args.silent:
            print('Writing to', args.out)
        decoded = data.decode(target_encoding)
        with open(args.out, 'w') as f:
            f.write(decoded)
