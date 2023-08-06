import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='github-utils',
    version=__import__('github_utils').__version__,
    author='HE Yaowen',
    author_email='he.yaowen@hotmail.com',
    description='A command-line tool to manage repositories of GitHub.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/he-yaowen/github-utils',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    entry_points={
        'console_scripts': [
            'gutils = github_utils.__main__:main'
        ]
    }
)
