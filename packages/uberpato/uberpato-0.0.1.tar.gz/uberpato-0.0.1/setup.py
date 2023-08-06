import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uberpato",
    version="0.0.1",
    author="Uberduck",
    author_email="s@uberduck.ai",
    description="Convenient calling of your favorite TTS APIs",
    url="https://github.com/uberduck-ai/pato",
    license="MIT",
    packages=["pato"],
    install_requires=["requests", "boto3"],
)
