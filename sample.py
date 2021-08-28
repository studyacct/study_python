from collections import defaultdict
import hashlib
import os
import pathlib
import sys


class File:
    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
        self._file_path = os.path.join(self.path, self.name)
        self._hash = hashlib.md5()
        self.size_bytes = os.path.getsize(self._file_path)

    def calculate_hash(self) -> None:
        """Calculate file hash by the first 64 kb"""
        chunk_bytes = 64 * 1024
        with open(self._file_path, 'rb') as rb:
            while True:
                data = rb.read(chunk_bytes)
                if not data:
                    break
                self._hash.update(data)

    def __str__(self) -> str:
        return f'{self._hash.hexdigest()}:{self.size_bytes}'


def find_duplicates(start_path: str) -> dict:
    d = defaultdict(list)

    seen_count = 0
    for path, dirs, files in os.walk(start_path):
        for file in files:
            print(f'Working on file ({seen_count + 1:,}): {file[:80]:<80}', end='\r')
            f = File(path, file)
            f.calculate_hash()
            d[str(f)].append(f)
            seen_count += 1

    print('*' * 80)
    dups = {key:files for key, files in d.items() if len(set(files)) > 1}

    return dups


if __name__ == '__main__':
    try:
        start_path = sys.argv[1]
    except IndexError:
        start_path = pathlib.Path.cwd()

    print(f'Start dir: {start_path}\n')

    duplicates = find_duplicates(start_path)

    if not duplicates:
        print(f'No duplicates in {start_path}')
        sys.exit(0)

    sorted_big_to_small = {
        k: v for k, v 
        in sorted(
            duplicates.items(),
            key=lambda item: item[1][0].size_bytes, 
            reverse=True
        )
    }

    print('Duplicates')
    for k, files in sorted_big_to_small.items():
        for file in files:
            print(f'{k} - {os.path.join(file.path, file.name)}')
        print('-' * 50)
