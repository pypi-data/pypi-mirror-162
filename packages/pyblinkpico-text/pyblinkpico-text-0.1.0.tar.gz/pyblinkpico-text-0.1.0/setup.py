from setuptools import setup

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(
    name='pyblinkpico-text',
    version='0.1.0',
    description='The BlinkPico text library',
    url='https://github.com/ID220/BlinkPico-Text',
    author='Nishant Nepal & Andrea Bianchi',
    author_email='andrea@kaist.ac.kr',
    license='MIT',
    packages=['pyblinkpico_text'],
    install_requires=['pyblinkpico'],
    keywords=['education', 'matrix_shield', 'HT16K33', 'RPI Pico'],
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        'Intended Audience :: Education',
        'Programming Language :: Python :: Implementation :: MicroPython'
    ],
)
