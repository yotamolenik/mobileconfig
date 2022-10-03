import csv
import plistlib
from pathlib import Path
from typing import Mapping

import click

from mobileconfig.mobileconfig import MobileConfig

XML_HEADER = b'<?xml '
XML_TAIL = b'</plist>'


def get_plist(file: bytes) -> Mapping:
    return plistlib.loads(XML_HEADER + file.split(XML_HEADER, 1)[1].split(XML_TAIL, 1)[0] + XML_TAIL)


@click.group()
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True))
@click.pass_context
def cli(ctx, directory):
    """ Parse .mobileconfig files in a given directory """
    ctx.ensure_object(dict)
    ctx.obj['directory'] = directory
    ctx.obj['plists'] = []
    for file in Path(directory).glob('*.mobileconfig'):
        ctx.obj['plists'].append(get_plist(file.read_bytes()))


@cli.command()
@click.pass_context
def consents(ctx):
    """ Print all user consents """
    for plist in ctx.obj['plists']:
        consent_text = plist['ConsentText']
        consent_text_en = consent_text.get('default', consent_text.get('en'))
        print(consent_text_en)


@cli.command()
@click.argument('output_file', type=click.File('w'), required=False)
@click.pass_context
def payload_types(ctx, output_file):
    """ Print all PayloadTypes with an optional csv file """
    if output_file:
        output_file = csv.writer(output_file)

    header = ['Display Name', 'PayloadType', 'Description']

    if output_file:
        output_file.writerow(header)

    rows = []
    for plist in ctx.obj['plists']:
        mobileconfig = MobileConfig(plist)
        display_name = mobileconfig.payload_display_name
        print('display name is', display_name)
        for payload_content in mobileconfig.payload_content:
            print('payload content is ', payload_content)
            payload_type = payload_content.payload_type
            description = str(payload_content)
            rows.append((display_name, payload_type, description))

    if output_file:
        output_file.writerows(rows)


@cli.command()
@click.argument('output', type=click.Path(dir_okay=True, file_okay=False, exists=False))
@click.pass_context
def extract(ctx, output):
    """ Extract .plist into given directory """
    output = Path(output)
    output.mkdir(0o777, exist_ok=True, parents=True)
    for plist in ctx.obj['plists']:
        display_name = plist["PayloadDisplayName"]
        filename = display_name.replace('/', '_') + '.plist'
        (output / filename).write_bytes(plistlib.dumps(plist))


if __name__ == '__main__':
    cli()
