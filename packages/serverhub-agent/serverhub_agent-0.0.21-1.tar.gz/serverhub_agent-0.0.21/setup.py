import setuptools

setuptools.setup(
    name="serverhub_agent",
    version="0.0.21",
    description="Runtime interface to running docker containers",
    url="https://github.yandex-team.ru/skills/serverhub-agent",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "aiohttp==3.7.4.post0",
        "marshmallow-dataclass==7.5.2",
        "marshmallow_enum==1.5.1",
        "marshmallow_union==0.1.15",
        "psutil",
    ],
)
