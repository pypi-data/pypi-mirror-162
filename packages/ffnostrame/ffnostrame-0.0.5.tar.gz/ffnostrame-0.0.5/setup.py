from setuptools import setup


def read_requirements():
    with open("requirements.txt", "r") as req:
        content = req.read()
        requirements = content.split("\n")

    return requirements


def get_version():
    version_file = open("version.txt", "r")
    version = version_file.read()
    version_file.close()

    return version


setup(
    name="ffnostrame",
    version="0.0.5",
    install_requires = ['click-shell==2.1', 'rich-click==1.5.1', 'click==7.1.2' ],
    # install_requires=read_requirements(),
    include_package_data=True,
    scripts=[],
    entry_points="""
        [console_scripts]
        1op=cli:cli
    """,
)
