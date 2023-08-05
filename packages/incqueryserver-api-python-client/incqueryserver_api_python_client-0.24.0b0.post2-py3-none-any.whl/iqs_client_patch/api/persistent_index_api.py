from io import BytesIO
from zipfile import ZipFile

import requests


class TransformedModelCompartmentDownload(object):

    def __init__(self, content, metadata):
        self.file_info = metadata
        self.content = content

    def get_file_content(self):
        return self.content

    def get_file_name(self):
        return self.file_info.filename

    def get_file_size(self):
        return self.file_info.file_size

    def get_compress_size(self):
        return self.file_info.compress_size


# Downloads transformed compartment from IQS
# Returns: array of TransformedModelCompartmentDownload
def monkey_patch_download_transformed_compartment(
        self,
        model_compartment_with_model_format,
        **kwargs
):
    config = self.api_client.configuration

    response = requests.post(
        "{}/persistent-index.downloadTransformedModelCompartment".format(config.host),
        auth=(config.username, config.password),
        json=model_compartment_with_model_format
    )

    if response.status_code == 200:
        files_array = []

        try:
            file = ZipFile(BytesIO(bytearray(response.content)), "r")
            for file_info in file.infolist():
                files_array.append(
                    TransformedModelCompartmentDownload(
                        metadata=file_info,
                        content=file.read(file_info.filename).decode("utf-8")
                    )
                )

            file.close()

            return files_array
        except Exception as error:
            raise error
    else:
        return response
