from setuptools import setup  # , find_packages

# Clasificadores: https://pypi.org/pypi?%3Aaction=list_classifiers


def get_readme():
    readme_txt = ""
    try:
        readme_txt = open('README.md').read()
    except Exception as e:
        print("Ha ocurrido un inconveniente: " + str(e))
    return readme_txt


setup(
    name='ecom-utils',
    version='1.2.0',
    author='Ecom Developers',
    author_email='simono@ecom.com.ar',
    description=('Core de módulos para PyPI'),
    long_description=get_readme(),
    license='BSD',
    keywords='ecom utils',
    url='https://git.ecom.com.ar/python-dev/ecom-utils',
    packages=["ecom_utils", "ecom_utils.tgd", "ecom_utils.pon", "ecom_utils.scient", "ecom_utils.scient.airflow", "ecom_utils.scient.airflow.core", "ecom_utils.scient.airflow.sql", "ecom_utils.scient.airflow.sql.mssql", "ecom_utils.scient.airflow.sql.postgres", "ecom_utils.scient.airflow.sql.core"],
    package_data={
        # 'starwars_ipsum': ['*.txt']
    },
    install_requires=["requests"],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ]
)
