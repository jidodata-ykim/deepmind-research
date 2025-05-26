#!/usr/bin/env python3

import re

def test_parsing():
    # Read a small portion of the file to test parsing
    file_path = '../data/wikitext-103/wiki.train.tokens'
    
    with open(file_path, 'rb') as f:
        content = f.read(2000)  # Read first 2000 bytes
    content = content.decode('utf-8')
    
    print("First 500 characters:")
    print(repr(content[:500]))
    print("\n" + "="*50 + "\n")
    
    # Test original regex
    title_re = re.compile(r'(\n = ([^=].*) = \n \n)')
    parts = title_re.split(content)
    print(f"Original regex found {len(parts)} parts")
    print("Parts:", parts[:10])
    print("\n" + "="*50 + "\n")
    
    # Test modified regex
    title_re2 = re.compile(r'(\n = ([^=].*) = \n)')
    parts2 = title_re2.split(content)
    print(f"Modified regex found {len(parts2)} parts")
    print("Parts:", parts2[:10])
    print("\n" + "="*50 + "\n")
    
    # Test another pattern
    title_re3 = re.compile(r'( = ([^=].*) = \n)')
    parts3 = title_re3.split(content)
    print(f"Another regex found {len(parts3)} parts")
    print("Parts:", parts3[:10])

if __name__ == '__main__':
    test_parsing()
