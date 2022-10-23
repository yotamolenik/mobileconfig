import csv
import plistlib
from pathlib import Path
from typing import Mapping

import click
import mdutils

from mobileconfig.mobileconfig import MobileConfig, ManagedPayload

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
@click.argument('output_file', type=click.File('w'), required=True)
@click.argument('output_type', type=click.Choice(['csv', 'md']), required=True)
@click.pass_context
def payload_types(ctx, output_file, output_type):
    """ Print all PayloadTypes to either a csv or md file """
    if output_type == 'csv':
        output_file = csv.writer(output_file)
    if output_type == 'md':
        mdfile = mdutils.MdUtils(file_name=output_file.name, title='Profiles')

    header = ['Display Name', 'PayloadType', 'Description']

    if output_type == 'csv':
        output_file.writerow(header)

    rows = ['Display Name', 'PayloadType', 'Description']
    for plist in ctx.obj['plists']:
        mobileconfig = MobileConfig(plist)
        display_name = mobileconfig.payload_display_name
        for payload_content in mobileconfig.payload_content:
            payload_type = payload_content.payload_type

            if isinstance(payload_content, ManagedPayload):
                for domain in payload_content.domains:
                    rows.extend([display_name, payload_type, f'{domain.domain}: {", ".join(domain.keys)}'])
            else:
                description = str(payload_content)
                rows.extend([display_name, payload_type, description])

    if output_type == 'csv':
        output_file.writerows(rows)

    if output_type == 'md':
        mdfile.new_table(columns=3, rows=len(rows) // 3, text=rows, text_align='left')
        mdfile.create_md_file()


@cli.command()
@click.argument('output', type=click.Path(dir_okay=True, file_okay=False, exists=False))
@click.pass_context
def extract(ctx, output):
    """ Extract the plists into given directory """
    output = Path(output)
    output.mkdir(0o777, exist_ok=True, parents=True)
    for plist in ctx.obj['plists']:
        display_name = plist["PayloadDisplayName"]
        filename = display_name.replace('/', '_') + '.plist'
        (output / filename).write_bytes(plistlib.dumps(plist))


if __name__ == '__main__':
    cli()
