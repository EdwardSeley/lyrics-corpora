from setuptools import setup

#long_description = open('README.md').read()

setup(
    name='lyricscorpora',
    version='0.0.5',
    description='Lyrics API',
    long_description='Lyrics API',
    install_requires=['billboard.py', 'requests', 'bs4'],
    url='https://github.com/edwardseley/lyrics-corpora',
    author='Edward Seley',
    author_email='edwardseley@gmail.com',
    license='No license',
    py_modules=['lyricscorpora'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Topic :: Multimedia :: Sound/Audio',
        'Natural Language :: English',
    ],
    keywords='lyrics LyricWikia music billboard songs scrape',
    entry_points={
        'console_scripts': [
            'lyricscorpora=lyricscorpora:main',
        ],
    },
)