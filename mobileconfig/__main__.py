import csv
import plistlib
from pathlib import Path
from typing import Mapping
import mdutils

import click

# im not yet sure why, but pycharm thinks this import is wrong. in fact it works perfectly fine on my terminal
from mobileconfig import MobileConfig

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
# @click.option('--output_type', type=click.Choice(['csv', 'md']))
@click.pass_context
def payload_types(ctx, output_file):
    """ Print all PayloadTypes to either a csv or md file """
    if output_file:
        output_file = csv.writer(output_file)

    header = ['Display Name', 'PayloadType', 'Description']

    if output_file:
        output_file.writerow(header)
    # if output_type == 'md':
    #     mdfile = mdutils.MdUtils(file_name='Example_Markdown', title='Markdown File Example')

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
    # if output_type == 'md':
    #     mdfile.create_md_file()


@cli.command()
@click.pass_context
def gist(ctx):
    """ create a markdown file containing device configurations in input dir for all profiles """
    mdfile = mdutils.MdUtils(file_name='profiles', title='profiles list')
    for plist in ctx.obj['plists']:
        display_name = plist['PayloadDisplayName']
        mdfile.new_header(level=1, title='Profile Name: ' + display_name)
        mdfile.new_header(level=2, title='payload types:')
        for payload_content in plist['PayloadContent']:
            payload_type = payload_content['PayloadType']
            mdfile.new_header(level=3, title='payload type: ' + payload_type)
            if payload_type == 'com.apple.system.logging':
                subsystems = payload_content.get('Subsystems')
                if subsystems:
                    for subsystem in payload_content['Subsystems']:
                        mdfile.new_header(level=4, title='subsystem: ' + subsystem)
            elif payload_type == 'com.apple.defaults.managed':
                for inner_payload_content in payload_content['PayloadContent']:
                    mdfile.new_header(level=3, title='Domain name: ' + inner_payload_content['DefaultsDomainName'])
                    mdfile.new_header(level=4, title='inner payload values: ' + str(inner_payload_content['DefaultsData']))
    mdfile.create_md_file()


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
