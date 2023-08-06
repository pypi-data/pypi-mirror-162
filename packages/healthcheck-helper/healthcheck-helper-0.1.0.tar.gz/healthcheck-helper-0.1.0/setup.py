from importlib.metadata import entry_points
import setuptools

setuptools.setup(
    name="healthcheck-helper",
    version='0.1.0',
    packages=setuptools.find_packages(exclude=["tests"]),
    author='M. Hakim Adiprasetya',
    author_email='m.hakim.adiprasetya@gmail.com',
    install_requires=[
        'fastapi==0.79.0',
        'uvicorn==0.18.2',
        'aiohttp==3.8.1',
        'typer==0.6.1'
    ],
    extras_require={
        'tests': ['pytest', 'pytest-mock', 'pytest-asyncio']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'healthcheck-helper = healthcheck_helper.main:run'
        ]
    }
)
