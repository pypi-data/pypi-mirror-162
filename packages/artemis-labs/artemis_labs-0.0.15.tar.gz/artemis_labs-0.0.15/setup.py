import setuptools

setuptools.setup(
    name="artemis_labs",
    version="0.0.15",
    author="Artemis Labs",
    author_email="austinmccoy@artemisar.com",
    description="Artemis Labs",
    packages= setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    entry_points ={
        'console_scripts': [
            'artemis_labs = artemis_labs.artemis_labs:main'
        ]
    },
    python_requires='>=3.6',
    install_requires=[
        'imageio',
        'websockets',
        'numpy',
        'matplotlib'
    ]
)