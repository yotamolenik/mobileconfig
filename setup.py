from pathlib import Path

from setuptools import setup, find_packages

BASE_DIR = Path(__file__).parent.resolve(strict=True)
VERSION = '1.0.0'
PACKAGE_NAME = 'mobileconfig'
DATA_FILES_EXTENSIONS = ['*.txt', '*.json', '*.js']
PACKAGES = [p for p in find_packages() if not p.startswith('tests')]


def parse_requirements():
    reqs = []
    with open(BASE_DIR / 'requirements.txt', 'r') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line:
                reqs.append(line)
    return reqs


def get_description():
    return (BASE_DIR / 'README.md').read_text()


if __name__ == '__main__':
    setup(
        version=VERSION,
        name=PACKAGE_NAME,
        description='Parse .mobileconfig files',
        long_description=get_description(),
        long_description_content_type='text/markdown',
        cmdclass={},
        packages=PACKAGES,
        author='Yotam',
        author_email='yotamolenik@gmail.com',
        license='GNU GENERAL PUBLIC LICENSE - Version 3, 29 June 2007',
        install_requires=parse_requirements(),
        entry_points={
            'console_scripts': ['mobileconfig=mobileconfig.__main__:cli',
                                ],
        },
        classifiers=[
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
        ],
        url='https://github.com/yotamolenik/mobileconfig',
        project_urls={
            'mobileconfig': 'https://github.com/yotamolenik/mobileconfig'
        },
        tests_require=['pytest', ],
    )
