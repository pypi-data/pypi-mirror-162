from setuptools import setup

setup(
    name='dualsense',
    author='Matthew Wildoer',
    author_email='mawildoer@gmail.com',
    version='0.0.3',
    py_modules=['dualsense',],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=['evdev']
)
