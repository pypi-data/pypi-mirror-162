from slackclient import SlackClient

"""
Usage:
    >>> from pyconn.slack import SlackAgent
    >>> slack_agent = SlackAgent(YOUR_TOKEN)
    >>> slack_agent.send_text('#myChannel', 'hello world')
    >>> slack_agent.send_text('@myFriend', 'path/to/the/file.png', 'hello world')
"""


class SlackAgent:
    def __init__(self, token):
        """
        :param token: The slack authentication token. You can create a token here <https://api.slack.com/docs/oauth>
        """
        self._slack_client = SlackClient(token)

    def send_text(self, channel: str, text: str, **kwargs) -> dict:
        response = self._slack_client.api_call('chat.postMessage', channel=channel, text=text, **kwargs)
        if not response['ok']:
            raise ValueError(response['error'])
        return response

    def send_file(self, channel: str, file_path: str, file_comment='', **kwargs) -> dict:
        file_handle = open(file_path, 'rb')
        response = self._slack_client.api_call('files.upload', channels=channel, file=file_handle,
                                               initial_comment=file_comment, **kwargs)
        file_handle.close()
        if not response['ok']:
            raise ValueError(response['error'])
        return response
