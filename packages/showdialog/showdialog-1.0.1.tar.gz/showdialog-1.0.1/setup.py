import setuptools  # type: ignore

with open('README.md', 'rt') as f:
    long_description = f.read()

setuptools.setup(
    name='showdialog',
    version='1.0.1',
    author='Chechkenev Andrey (@DarkCat09)',
    author_email='aacd0709@mail.ru',
    description='Simple module for showing GTK dialog',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: X11 Applications :: GTK'
    ],
    install_requires=[
        'PyGObject>=3.42.2'
    ],
    packages=['showdialog'],
    python_requires=">=3.6",
)
