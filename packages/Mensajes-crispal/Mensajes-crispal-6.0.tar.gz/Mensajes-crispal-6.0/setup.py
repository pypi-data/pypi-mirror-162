from struct import pack
from setuptools import setup, find_packages


setup(
    name="Mensajes-crispal",
    version="6.00",
    description="Un paquete para saludar y despedir",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Hector Costa",
    author_email="hola@hektorprofe.com",
    url="http://www.hektorprofe.net",
    license_files=['LICENSE'],
    packages=find_packages(), # importando el find_pakages el programa buscara toos lo que esta dentro del paquete.
    scripts=[],
    test_suite='tests',
    install_requires=[paquete.strip() 
                        for paquete in open("requirements.txt").readlines()],
    classifiers=[
        'Environment :: Console', # Para consola pc
        'Intended Audience :: Developers', # La audiencia serian desarrolladores
        'License :: OSI Approved :: MIT License',# lisencia MIT
        'Operating System :: OS Independent', # Sistema operativo, independiente porque funciona en todos
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities', # topico utilidades
    ],
)
