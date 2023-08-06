# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forge', 'forge.auth', 'forge.forms', 'forge.views']

package_data = \
{'': ['*'],
 'forge': ['templates/*'],
 'forge.auth': ['templates/registration/*'],
 'forge.forms': ['templates/django/forms/*',
                 'templates/django/forms/errors/list/*']}

install_requires = \
['Django>=4.0,<5.0',
 'click>=8.1.0,<9.0.0',
 'dj-database-url>=1.0.0,<2.0.0',
 'django-widget-tweaks>=1.4.12,<2.0.0',
 'forge-core<1.0.0',
 'forge-db>=0.3.0,<0.4.0',
 'forge-format<1.0.0',
 'forge-heroku<1.0.0',
 'forge-tailwind<1.0.0',
 'forge-work<1.0.0',
 'hiredis>=2.0.0,<3.0.0',
 'ipdb>=0.13.9,<0.14.0',
 'pytest-django>=4.5.2,<5.0.0',
 'pytest>=7.0.0,<8.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'redis>=4.2.2,<5.0.0',
 'whitenoise>=6.0.0,<7.0.0']

entry_points = \
{'console_scripts': ['forge = forge.cli:cli']}

setup_kwargs = {
    'name': 'forge',
    'version': '0.16.0',
    'description': 'Quickly build a professional web app using Django.',
    'long_description': '# Forge\n\n<img height="100" width="100" src="https://user-images.githubusercontent.com/649496/176748343-3829aad8-4bcf-4c25-bb5d-6dc1f796fac0.png" align="right" />\n\n**Quickly build a professional web app using Django.**\n\nForge is a set of opinions for how to build with Django.\nIt guides how you work,\nchooses what tools you use,\nand makes decisions so you don\'t have to.\n\nAt it\'s core,\nForge *is* Django.\nBut we\'ve taken a number of steps to make it even easier to build and deploy a production-ready app on day one.\n\nIf you\'re an experienced Django user,\nyou\'ll understand and (hopefully) agree with some of Forge\'s opinions.\nIf you\'re new to Django or building web applications,\nwe\'ve simply removed questions that you might not even be aware of.\n\nForge will get you from *zero to one* on a revenue-generating SaaS, internal business application, or hobby project.\n\n## Quickstart\n\nStart a new project in 5 minutes:\n\n```sh\ncurl -sSL https://forgepackages.com/quickstart.py | python3 - my-project\n```\n\n[![Forge Django quickstart](https://user-images.githubusercontent.com/649496/173145833-e4f96a4c-efb6-4cc3-b118-184be1a007f1.png)](https://www.youtube.com/watch?v=wYMRxTGDmdU)\n\n\n### What\'s included\n\nThings that come with Forge,\nthat you won\'t get from Django itself:\n\n- Configure settings with environment variables\n- A minimal `settings.py` with sane, opinionated defaults\n- Extraneous files (`manage.py`, `wsgi.py`, `asgi.py`) have been removed unless you need to customize them\n- Send emails using Django templates (ex. `templates/email/welcome.html`)\n- Default form rendering with Tailwind classes\n- Login in with email address (in addition to usernames)\n- Abstract models for common uses (UUIDs, created_at, updated_at, etc.)\n- Test using [pytest](https://docs.pytest.org/en/latest/) and [pytest-django](https://pytest-django.readthedocs.io/en/latest/)\n- Default HTTP error templates (400, 403, 404, 500)\n- Default Tailwind-styled password change and password reset templates\n- Default Tailwind-styled login template\n- Default Tailwind-styled sign up template\n- Start with a custom user model (`users.User`)\n- Start with a "team" model (`teams.Team`)\n\nWe\'re also able to make some decisions about what tools you use *with* Django -- things that Django (rightfully) doesn\'t take a stance on:\n\n- Deploy using [Heroku](https://heroku.com/)\n- Manage Python dependencies using [Poetry](https://python-poetry.org/)\n- Style using [Tailwind CSS](https://tailwindcss.com/)\n- Format your code using [black](https://github.com/psf/black) and [isort](https://github.com/PyCQA/isort)\n- CI testing with [GitHub Actions](https://github.com/features/actions)\n\nAll of this comes together with a `forge` CLI.\n\n\n## Existing projects\n\nA lot (but not all) of the Forge features can be integrated into existing projects by installing select packages:\n\n- [forge-work](https://github.com/forgepackages/forge-work)\n- [forge-tailwind](https://github.com/forgepackages/forge-tailwind)\n- [forge-db](https://github.com/forgepackages/forge-db)\n- [forge-heroku](https://github.com/forgepackages/forge-heroku)\n- [forge-format](https://github.com/forgepackages/forge-format)\n\nYou can also look at the [Forge starter-template](https://github.com/forgepackages/starter-template),\nwhich is what the quickstart uses to start a new project.\n\n\n## Inspired by\n\n- [create-react-app](https://create-react-app.dev/)\n- [Bullet Train](https://bullettrain.co/)\n- [SaaS Pegasus](https://www.saaspegasus.com/)\n- [Laravel Spark](https://spark.laravel.com/)\n',
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.forgepackages.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
