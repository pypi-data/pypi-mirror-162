from struct import pack
from setuptools import setup, find_packages


setup(
     name="Mensajes",
    version="3.00",
    description="Un paquete para saludar y despedir",
    author="Hector Costa",
    author_email="hola@hektorprofe.com",
    url="http://www.hektorprofe.net",
    packages=find_packages(), # importando el find_pakages el programa buscara toos lo que esta dentro del paquete.
    scripts=['test.py'],
    install_requires=['numpy']
)
