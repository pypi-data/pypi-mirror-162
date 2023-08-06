from distutils.core import setup
import os

# def package_files(directory):
#     paths = []
#     for (path, directories, filenames) in os.walk(directory):
#         for filename in filenames:
#             paths.append(os.path.join('..', path, filename))
#     return paths
#
#
# extra_files = package_files('./web_foundation')
# print(extra_files)

DEPTH = 20

setup(
    name='web-foundation',  # How you named your package folder (MyLib)
    packages=['web_foundation'],  # Chose the same as "name"
    package_data={
        'web_foundation': [('*/' * i).rstrip("/") for i in range(1, DEPTH)],
    },
    version='0.0.6.9',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Python microprocessors web-foundation',  # Give a short description about your library
    author='Yaroha',  # Type in your name
    author_email='yaroher2442@gmail.com',  # Type in your E-Mail
    keywords=['SOME', 'MEANINGFULL', 'KEYWORDS'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        "sanic==22.6.0",
        "dependency-injector>=4.0,<5.0"
        "sanic-ext==22.6.1",
        "tortoise-orm==0.19.1",
        "asyncpg==0.26.0",
        "pydantic==1.9.1",
        "aioprocessing==2.0.0",
        "pydantic==1.9.1",
        "dill==0.3.5.1",
        "pyee==9.0.4",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
)
