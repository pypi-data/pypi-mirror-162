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
    name="ffostrame",
    version=get_version(),
    install_requires=read_requirements(),
    include_package_data=True,
    scripts=[
        "ff/ff.py"
    ],
    entry_points="""
        [console_scripts]
        ff=ff:cli
    """,
)
