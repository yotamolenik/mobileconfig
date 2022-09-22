import csv
import plistlib
from pathlib import Path
from typing import Mapping

import click
from humanfriendly.tables import format_smart_table

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
@click.argument('csv_summary', type=click.File('w'), required=False)
@click.pass_context
def payload_types(ctx, csv_summary):
    """ Print all PayloadType's (with an optional .csv output) """
    if csv_summary:
        csv_summary = csv.writer(csv_summary)

    header = ['Display Name', 'PayloadType', 'Description']

    if csv_summary:
        csv_summary.writerow(header)

    rows = []
    for plist in ctx.obj['plists']:
        display_name = plist['PayloadDisplayName']
        for payload_content in plist['PayloadContent']:
            payload_type = payload_content['PayloadType']

            description = ''
            if payload_type == 'com.apple.system.logging':
                subsystems = payload_content.get('Subsystems')
                if subsystems:
                    description = 'Subsystems: '
                    description += ', '.join(subsystems.keys())
            elif payload_type == 'com.apple.defaults.managed':
                for inner_payload_content in payload_content['PayloadContent']:
                    domain = inner_payload_content.get('DefaultsDomainName')
                    data_keys = ', '.join(inner_payload_content.get('DefaultsData').keys())
                    description = f'{domain}: {data_keys}'

            rows.append((display_name, payload_type, description))

    if csv_summary:
        csv_summary.writerows(rows)

    print(format_smart_table(rows, header))


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
