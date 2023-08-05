import json

import requests


class FileForAcquisition(object):

    def __init__(self, file, file_format, base_uri):
        self.file = file
        self.file_format = file_format
        self.base_uri = base_uri

    def create_metadata_entry(self):
        return {
            "linkedDataFormat": self.file_format,
            "baseURI": self.base_uri,
            "documentFileName": self.file["metadata"]["name"]
        }

    def create_file_entry(self):
        return "documents", (self.file["metadata"]["name"], self.file["content"])


"""
Linked Data acquisition method:
@:param linked_data_acquisition_request_multipart (dict)
    compartment_uri: string
    documents: array<dict>
        file: dict
            metadata: dict
                name: string
            content: bytes
        file_format: string
        base_uri: string
"""


def monkey_patch_acquire_linked_data(
        self,
        linked_data_acquisition_request_multipart,
        **kwargs
):
    config = self.api_client.configuration

    documents = linked_data_acquisition_request_multipart["documents"]
    compartment_uri = linked_data_acquisition_request_multipart["compartment_uri"]
    files = []
    for document in documents:
        files.append(FileForAcquisition(document["file"], document["file_format"], document["base_uri"]))

    request = list(
        map(lambda file: file.create_file_entry(), files)
    )

    metadata = json.dumps({
        "modelCompartment": {
            "compartmentURI": compartment_uri
        },
        "documentMetadataEntries": list(
            map(lambda file: file.create_metadata_entry(), files)
        )
    })

    request.append(
        ("metadata", (None, metadata))
    )

    response = requests.post(
        "{}/demo.acquireLinkedData".format(config.host),
        auth=(config.username, config.password),
        files=request
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.reason)
    else:
        return response.json()
