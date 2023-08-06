from setuptools import setup


def read_requirements():
    with open("requirements.txt", "r") as req:
        content = req.read()
        requirements = content.split("\n")

    return requirements


def get_version():
    version_file = open("ff/version.txt", "r")
    version = version_file.read()
    version_file.close()

    return version


setup(
    name="ffostrame",
    version=get_version(),
    install_requires=read_requirements(),
    include_package_data=True,
    scripts=[
        "ff/ff.py",
        "ff/version.txt",
        "ff/utils.py",
        "ff/news.py",
        "ff/get.py"
    ],
    entry_points="""
        [console_scripts]
        ff=ff:cli
    """,
)
