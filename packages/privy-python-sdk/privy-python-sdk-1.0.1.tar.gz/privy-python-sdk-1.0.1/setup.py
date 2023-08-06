# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['privy_python_sdk']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'privy-python-sdk',
    'version': '1.0.1',
    'description': 'Python SDK for Privy Digital Signature',
    'long_description': '# Privy Python SDK\nPython SDK for Privy Digital Signature https://console.privy.id/\n\n\n## API Documentation\nPlease check [Privy Api Reference](https://console.privy.id/documentation).\n\n## Requirements\nPython 3.7 or later\n\n## Installation\n```python\npip install privy-python-sdk\n```\n## Usage\n\n### Initialization\n\n```python\nfrom privy_python_sdk.privy import Privy\n\nprv = Privy(\n    privy_enterprise_token="key-123",\n    privy_merchant_key="xxxxxxxxxxxxx",\n    privy_username="foo",\n    privy_password="bar",\n    privy_id=\'TE1111\',\n    production=False\n)\n```\n### Privy User Registration\n**Args**:\n- `email` *string* - User\'s email\n- `phone` *string* - User\'s phone (e.g: 08233324223)\n- `selfie` *string* - Close up photo of registrant (.png, .jpg, or .jpeg)\n- `ktp` *string* - KTP Photo of the user (.png, .jpg, or .jpeg)\n- `nik` *string* - NIK must be 16 digits and the sixteenth digit can\'t be 0\n- `name` *string* - name of the user\n- `date_of_birth` *string* - date of birth of the user (1983-01-02)\n\n**Returns**: <br />\n    Return reference https://console.privy.id/documentation#registration\n\n```python\nprv.register_user(\n        date_of_birth="1983-01-02",\n        email="foo@bar.com",\n        ktp="/upload/ktp.jgp",\n        selfie="/upload/selfie.jgp",\n        name="foo bar",\n        nik="1234567891234567",\n        phone="08233324223"\n)\n```\n\n### Get User\'s Registration Status\nCheck registration status of user.\n\n**Args**:\n- `token` *string* - User\'s token from Registration API\n\n**Returns**: <br />\n    Return reference https://console.privy.id/documentation#check-registration-status\n\n```python\nprv.register_status(token="b3lkdfaoir0294058klkadfk45qeorlkldakfgh")\n```\n\n### Upload Document\n**Args**:\n- `title` *string* - title of the document\n- `document_path` *string* - path of the document\n- `recipient` *string* - recipient of the document\n- `owner` *string* - owner of the document\n\n**Returns**: <br />\nReturn reference https://console.privy.id/documentation#upload-document\n\n```python\nprv.upload_document(\n        document_path="/upload/document.jgp",\n        title="foo bar",\n        recipient="LA1234"\n    )\n```\n\n### Get Document Status\n**Args**:\n- `doc_Token` *string* - Document\'s token\n\n**Returns**: <br />\nReturn reference https://console.privy.id/documentation#check-document-status\n```python\nprv.document_status(\n        doc_token="b3lkdfaoir0294058klkadfk45qeorlkldakfgh"\n    )\n```\n\n## License\n\n**privy-python-sdk** is released under the MIT License. Check License file for detail.',
    'author': 'LandX Engineering',
    'author_email': 'tech@landx.id',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/landx-id/privy-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
