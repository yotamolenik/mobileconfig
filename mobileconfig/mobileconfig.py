from collections import namedtuple
from typing import Mapping, List

Domain = namedtuple('Domain', 'domain keys')


class PayloadContent:
    @staticmethod
    def create(plist: Mapping) -> 'PayloadContent':
        return {
            'com.apple.system.logging': LoggingPayload,
            'com.apple.defaults.managed': ManagedPayload,
            'com.apple.corecapture.configure': CoreCapture,
            'com.apple.ManagedClient.preferences': ManagedClient
        }[plist['PayloadType']](plist)

    def __init__(self, plist: Mapping):
        self._plist = plist

    @property
    def payload_content(self) -> Mapping:
        return self._plist['PayloadContent']

    @property
    def payload_type(self) -> str:
        return self._plist['PayloadType']


class LoggingPayload(PayloadContent):
    def __repr__(self):
        subsystems = self._plist.get('Subsystems')
        description = ''
        if subsystems:
            description = 'Subsystems: '
            description += ', '.join(subsystems.keys())
        return description


class ManagedPayload(PayloadContent):
    @property
    def domains(self) -> List[Domain]:
        result = []
        for inner_payload_content in self.payload_content:
            domain = inner_payload_content.get('DefaultsDomainName')
            keys = inner_payload_content.get('DefaultsData').keys()
            result.append(Domain(domain, keys))
        return result

    def __repr__(self):
        description = ''
        for inner_payload_content in self.payload_content:
            domain = inner_payload_content.get('DefaultsDomainName')
            keys = ', '.join(inner_payload_content.get('DefaultsData').keys())
            description += f'{domain}: {keys}'
        return description


class CoreCapture(PayloadContent):
    @property
    def core_capture_config(self) -> List[str]:
        """ a special property present only in payloads of type com.apple.ManagedClient.preferences """
        return self._plist['CoreCaptureConfig'].keys()

    def __repr__(self):
        return str(self.core_capture_config)


class ManagedClient(PayloadContent):
    def __repr__(self):
        return str(self.payload_content)


class MobileConfig:
    def __init__(self, plist: Mapping):
        self._plist = plist

    @property
    def payload_display_name(self) -> str:
        return self._plist['PayloadDisplayName']

    @property
    def payload_content(self) -> List[PayloadContent]:
        return [PayloadContent.create(p) for p in self._plist['PayloadContent']]
