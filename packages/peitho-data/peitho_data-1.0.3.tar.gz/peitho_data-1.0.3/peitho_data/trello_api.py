import json
import os

import requests

# Read Trello API auth credentials from local
# The credential is store in a local JSON file whose location is defined in a system environment variable called
# "TRELLO_API_CONFIG_PATH"
# The credential file is a JSON map of the form
# {
#     "key": "<API key>"
#     "token": <token>
# }
# see https://trello.com/app-key
# see https://gcallah.github.io/DevOps/workflow/trelloapi.html
CONFIG_FILE_PATH = os.getenv("TRELLO_API_CONFIG_PATH")

if CONFIG_FILE_PATH:
    api_credential = json.load(open(os.getenv("TRELLO_API_CONFIG_PATH")))
    key = api_credential["key"]
    token = api_credential["token"]
else:
    key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_API_TOKEN")


def delete_attachment_by_name(card_id: str, name: str) -> None:
    """
    Delete a specified attachment of a Trello card.

    :param card_id: The ID of the Trello card whose attachments are to be deleted
    :param name: The display name of the attachment being deleted
    """

    attachments = requests.get(
        "https://api.trello.com/1/cards/{}/attachments?key={}&token={}".format(card_id, key, token)
    ).json()

    for attatchment in attachments:
        if attatchment["name"] == name:
            requests.delete(
                "https://api.trello.com/1/cards/{}/attachments/{}?key={}&token={}".format(
                    card_id,
                    attatchment["id"],
                    key,
                    token
                )
            )


def delete_all_attachments(card_id: str) -> None:
    """
    Delete all attachments of a Trello card.

    :param card_id: The ID of the Trello card whose attachments are to be deleted
    """

    attachments = requests.get(
        "https://api.trello.com/1/cards/{}/attachments?key={}&token={}".format(card_id, key, token)
    ).json()

    for attatchment in attachments:
        requests.delete(
            "https://api.trello.com/1/cards/{}/attachments/{}?key={}&token={}".format(
                card_id,
                attatchment["id"],
                key,
                token
            )
        )


def upload_attachment(card_id: str, attachment_name: str, attachment_relative_path: str) -> requests.models.Response:
    """
    Uploads file to a Trello card as attachment.

    :param card_id:  The ID of the Trello card against whihc the attachment is to be uploaded
    :param attachment_name:  Attachment display name, e.g. book.pdf
    :param attachment_relative_path:  Attachment file path relative to the location of this scrip invocation
    """
    # Define the credential info
    params = (
        ('key', key),
        ('token', token),
    )

    # Define file to be attached to Trello card
    files = {
        'file': (attachment_name, open(attachment_relative_path, 'rb')),
    }

    # Define API URL
    url = "https://api.trello.com/1/cards/{}/attachments".format(card_id)

    # Fire API request to upload attachment
    return requests.post(url, params=params, files=files)


if __name__ == "__main__":
    pass
