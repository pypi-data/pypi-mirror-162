from setuptools import setup


with open("README.md") as readme_file:
    LONG_DESCRIPTION = readme_file.read()


setup(
    name="beautiful_repr",
    version="0.0.3",
    url="https://github.com/TheArtur128/Beautiful-repr",
    download_url="https://github.com/TheArtur128/Beautiful-repr/archive/refs/heads/master.zip",
    author="Arthur",
    author_email="s9339307190@gmail.com",
    description="Library for beautiful object formatting",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires='>=3.10',
    packages=["beautiful_repr"],
)
