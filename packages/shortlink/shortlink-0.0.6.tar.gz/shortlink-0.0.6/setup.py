import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='shortlink',  # should match the package folder
    packages=['shortlink'],  # should match the package folder
    version='0.0.6',  # important for updates
    license='MIT',  # should match your chosen license
    description='Powerfull url shortener',
    long_description=long_description,  # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='MishaKorzhik_He1Zen',
    author_email='developer.mishakorzhik@gmail.com',
    url='https://github.com/mishakorzik/mask-url',
    project_urls={  # Optional
        "Bug Tracker": "https://github.com/mishakorzik/mask-url/issues"
    },
    install_requires=['requests'],  # list all packages that your package uses
    keywords=["api", "pypi", "pip", "short", "shortener", "link", "url"],  # descriptive meta-data
    classifiers=[  # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],

    download_url="https://github.com/mishakorzik/mask-url/archive/refs/tags/0.0.6.tar.gz",
)
