import asyncio
from typing import List

from whatsmyname.app.cli.args import get_default_args, arg_parser
from whatsmyname.app.models.enums.common import OutputFormat
from whatsmyname.app.models.schemas.cli import CliOptionsSchema
from whatsmyname.app.models.schemas.sites import SiteSchema
from whatsmyname.app.tasks.process import process_cli, filter_list_by
from whatsmyname.app.utilities.formatters import to_json, to_csv, to_table


async def start_check_for_presence():

    argparse = get_default_args()
    cli_options: CliOptionsSchema = arg_parser(argparse.parse_args())
    sites: List[SiteSchema] = await process_cli(cli_options)

    # filter the sites
    sites = filter_list_by(cli_options, sites)

    if cli_options.random_validate:
        cli_options.usernames = [cli_options.random_username]
        sites = await process_cli(cli_options)

    if cli_options.format == OutputFormat.JSON:
        to_json(cli_options, sites)
    elif cli_options.format == OutputFormat.CSV:
        to_csv(cli_options, sites)
    elif cli_options.format == OutputFormat.TABLE:
        to_table(cli_options, sites)

    if cli_options.output_stdout:
        with open(cli_options.output_file, 'r') as fp:
            lines: List[str] = fp.readlines()
            for line in lines:
                print('{}'.format(line.strip()))


def check_for_presence() -> None:
    asyncio.run(start_check_for_presence())
