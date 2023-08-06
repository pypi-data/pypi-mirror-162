# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nextcord_ormar',
 'nextcord_ormar.nxalembic',
 'nextcord_ormar.nxalembic.template']

package_data = \
{'': ['*']}

install_requires = \
['alembic>=1.8,<2.0', 'nextcord>=2.0,<3.0', 'ormar>=0.11,<0.12']

extras_require = \
{'docs': ['Sphinx>=5.1,<6.0',
          'releases>=1.6,<2.0',
          'sphinx-argparse>=0.3.1,<0.4.0',
          'six>=1.16.0,<2.0.0',
          'tomlkit>=0.11.2,<0.12.0']}

entry_points = \
{'console_scripts': ['nxalembic = nextcord_ormar.nxalembic:main']}

setup_kwargs = {
    'name': 'nextcord-ormar',
    'version': '0.3.3',
    'description': 'Database integration for Nextcord with Ormar',
    'long_description': '# Nextcord-Ormar\n\n[![Documentation Status](https://readthedocs.org/projects/nextcord-ormar/badge/?version=latest&style=for-the-badge)](https://nextcord-ormar.readthedocs.io/en/latest/?badge=latest)\n\n[Formerly Nextcord-Tortoise](docs/goodbye-tortoise.md)\n\nNextcord-Ormar is a library to help integrate the async Django-inspired ORM\n[Ormar](https://github.com/collerek/ormar) with a [Nextcord](https://github.com/nextcord/nextcord/) bot. It\'s \ndesigned to compliment the modular cog system of Nextcord. It also comes with NXAlembic, a preconfigured version of\n[Alembic](https://github.com/sqlalchemy/alembic) to help with creating and applying database migrations.\n\nNextcord-Ormar is still in active development, there may be breaking changes as the library is polished up. If you have \nany feedback, feel free to open an issue!\n\n## Quickstart\n\nInstall Nextcord-Ormar and Ormar with the correct [database backend](https://collerek.github.io/ormar/install/).\n\n```shell\npip install nextcord-ormar ormar[sqlite]\n```\n\n\nImport Nextcord-Ormar\'s bot class and pass it your [database URL](https://nextcord-ormar.readthedocs.io/en/latest/connections.html).\n\n```python\nfrom nextcord_ormar import Bot\n\nbot = Bot(command_prefix="$", database_url="sqlite:///db.sqlite")\n```\n\nIn your cog file, import OrmarApp to create an app, then use AppModel to create a database model. Define your model \nlike a [normal Ormar model](https://collerek.github.io/ormar/models/).\n\nIf you prefer, you can also define your models elsewhere and import them into your cog.\n\n```python\nimport ormar\nfrom nextcord_ormar import OrmarApp, AppModel\n\nModelMeta = OrmarApp.create_app("example")\n\nclass ExampleTable(AppModel):\n    class Meta(ModelMeta):\n        pass\n    \n    id = ormar.Integer(primary_key=True)\n    discord_id = ormar.BigInteger()\n    message = ormar.Text()\n```\n\nYou can then use this model in your cog.\n\n```python\nfrom nextcord.ext import commands\n\nclass Example(commands.Cog):\n    def __init__(self, nextcord):\n        self.nextcord = nextcord\n\n    @commands.command("example")\n    async def example(self, ctx: commands.Context, *args):\n        new_example = await ExampleTable.objects.create(discord_id=ctx.author.id, message=args[0])\n        await ctx.send("Hello!")\n```\n\nBefore you can start the bot though, you\'ll need to set up migrations and the database. Create a file called \n`nxalembic.ini` in your project root folder and tell it how to import your bot.\n\n```ini\n[nxalembic]\nmodule = example.demo\nbot = bot\n```\n\nYou can think of this as `from module import bot`, or in this instance, `from example.demo import bot`. NXAlembic will \nuse it to import your bot along with your definitions for each model.\n\nIn the same folder, you can now use the `nxalembic` tool. Create migrations with\n\n```shell\nnxalembic migrate\n```\n\nUpgrade the database\n\n```shell\nnxalembic update\n```\n\nYour bot is now ready to start!\n\n\n### Roadmap\n\nOther than bug fixes as they arise, the current plan is to just add the rest of the Alembic commands to NXAlembic. \nIf there is a specific feature you want that is missing from either the bot integration or NXAlembic, feel free to \nopen an issue.\n\n### Thanks to\n\nMiguel Grinberg for [Flask-Migrations](https://github.com/miguelgrinberg/Flask-Migrate) which was a useful example.\n\n[Mike Bayer](https://github.com/zzzeek) for [SQLAlchemy](https://www.sqlalchemy.org/) and [Alembic](https://github.com/sqlalchemy/alembic/)\n\n\n',
    'author': 'Peter DeVita',
    'author_email': 'mewtwo2643@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pmdevita/nextcord-ormar',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
