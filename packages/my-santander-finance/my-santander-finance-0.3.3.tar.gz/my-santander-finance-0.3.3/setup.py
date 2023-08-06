# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['my_santander_finance',
 'my_santander_finance.config',
 'my_santander_finance.logger',
 'my_santander_finance.util',
 'my_santander_finance.web_scraping']

package_data = \
{'': ['*'], 'my_santander_finance': ['database/*', 'driver/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'Markdown>=3.4.1,<4.0.0',
 'PyAutoGUI>=0.9.53,<0.10.0',
 'SQLAlchemy>=1.4.39,<2.0.0',
 'black>=22.6.0,<23.0.0',
 'bumpversion>=0.6.0,<0.7.0',
 'click>=8.1.3,<9.0.0',
 'flake8>=4.0.1,<5.0.0',
 'isort>=5.10.1,<6.0.0',
 'mkdocs-material>=8.3.9,<9.0.0',
 'mkdocs[i18n]>=1.3.0,<2.0.0',
 'numpy>=1.23.0,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pre-commit>=2.19.0,<3.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pywin32>=304,<305',
 'requests>=2.28.1,<3.0.0',
 'selenium>=4.3.0,<5.0.0',
 'typer>=0.6.1,<0.7.0',
 'webdriver-manager>=3.7.1,<4.0.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['sanfi = my_santander_finance.sanfi:main']}

setup_kwargs = {
    'name': 'my-santander-finance',
    'version': '0.3.3',
    'description': 'automated process to obtain the consumption of the bank credit and debit cards, classify them and generate a dashboard',
    'long_description': "# App para Automatizacion (web scrapping) de Banco Santander\nAplicacion para la gestion de cuentas del banco Santander de Argentina, permite:\n\n* [x] obtener el resumen de la cuenta(download) de los ultimos 60 dias\n* [x] transformarlos y cargarlos en una base de datos (sqlite)\n* [ ] clasificar y etiquetar los consumos\n* [ ] generar reportes\n\n## Instalacion\n\n_se requiere tener instalado python_\n\nInstalar utilizando pip, desde la consola(cmd.exe):\n\n```bash\n  pip install my-santander-finance\n```\n\n## Actualizacion\n\nActualizar utilizando pip\n\n```bash\n  pip install --upgrade my-santander-finance\n```\n\nLuego verificar version\n```bash\n  sanfi --version\n```\n\n\n## Configuracion\n\nLa aplicacion crea un directorio en el 'home' del usuario con el nombre '.sanfi', por ejemplo en Windows seria en:\n\nc:\\Users\\Oscar\\.sanfi\\\n\nPara poder realizar el web scrapping de la pagina de Santander Argentina, es necesario definir tres(3) variables de entorno, ya sea como variables de entorno propiamente dichas o bien en un archivo en el raiz del directorio de la app llamado .env, por ejemplo:\n\nc:\\Users\\Oscar\\.sanfi\\.env\n\n### Environment Variables\n\nLas tres(3) variables de entorno son:\n\n`DNI`\n\n`CLAVE`\n\n`USUARIO`\n\n_Estos datos, son los requeridos para el login en la web de Santander._ \n\nPara mas informacion de como trabajar con las variables de entorno hacer click en este link [variables de entorno](docs/es/environment_variables.md)\n\n## Utilizacion\n\nDesde la consola, ejecutar para obtener la ayuda:\n```bash\nsanfi --help\n```\n\nEn el caso de querer realizar el download de los consumos:\n```bash\nsanfi --download\n```\nLa informacion se guarda en una base de datos sqlite (santander.sqlite). Se puede consultar el formato de las tablas en [sqlite](my_santander_finance/sqlite.sql)\n\nPara trabajar directamente con la base de datos sqlite, utilizo la siguiente herramienta grafica free para Windows [HeidiSQL](https://www.heidisql.com/)\n\nObviamente, tambien es posible utlizar al consola proporcionada por sqlite desde la linea de comandos:\n\n```bash\nsqlite3 --help\n```\nPara mas informacion, click en [sqlite3](docs/es/sqlite3.md)\n\n## Crontab\n\nPara mas informacion, click en [crontab](docs/es/crontab.md)\n\n## Feedback\n\nContactarme a opaniagu@gmail.com\n\n## Authors\n\n- [@opaniagu](https://www.github.com/opaniagu)\n\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n",
    'author': 'Oscar Paniagua',
    'author_email': 'opaniagu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opaniagu/my-santander-finance',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
