import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='iphack',  # should match the package folder
    packages=['iphack'],  # should match the package folder
    version='1.0.5',  # important for updates
    license='MIT',  # should match your chosen license
    description='the most ideal tool for finding out information about IP',
    long_description=long_description,  # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='MishaKorzhik_He1Zen',
    author_email='developer.mishakorzhik@gmail.com',
    url='https://github.com/mishakorzik/IpHack',
    project_urls={  # Optional
        "Bug Tracker": "https://github.com/mishakorzik/IpHack/issues"
    },
    install_requires=['requests'],  # list all packages that your package uses
    keywords=["ip", "address", "iphack", "ips", "pypi", "pip"],  # descriptive meta-data
    classifiers=[  # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],

    download_url="https://github.com/mishakorzik/IpHack/archive/refs/tags/1.0.5.tar.gz",
)
