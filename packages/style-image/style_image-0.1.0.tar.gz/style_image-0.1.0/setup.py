# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['style_image', 'style_image.core', 'style_image.util']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'numpy>=1.23.1,<2.0.0',
 'tensorflow-hub>=0.12.0,<0.13.0',
 'tensorflow>=2.9.1,<3.0.0',
 'typer[all]>=0.6.1,<0.7.0',
 'validators>=0.20.0,<0.21.0']

entry_points = \
{'console_scripts': ['style_image = style_image.main:app']}

setup_kwargs = {
    'name': 'style-image',
    'version': '0.1.0',
    'description': '',
    'long_description': '## Style_Image\n\nThis simple python package takes two images, the style image, and the content image, and performs style transfer. It was created to explain how to build python packages using poetry.\n\n`style_image` uses the `magenta/arbitrary-image-stylization-v1-256` model under the hood available in TensorflowHub.\n\n To get more info about the model check this link : [magenta/arbitrary-image-stylization-v1-256](https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2)\n### Installation\n\nTo install the package, run the following command:\n\n```bash\npip install style_image\n```\n\nYou can use `style_image` from the command line or using the python API.\n\n### use in the terminal\n\nFor running `style_image` from the terminal, run the command below.\n```bash\nstyle_image -s picasso_violin -c /Users/haruiz/style_image/data/content_image.jpg -sz 800\n```\nTo get more information about the parameters that need to be provided, run the command `style_image --help`. \n\n### Use from code\n \n```python\nfrom style_image import StyleImage\n\nif __name__ == "__main__":\n\n    content_image_path = "data/content_image.jpg"\n    style_image_path = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1024px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"\n\n    stylized_image = (\n        StyleImage(style_image_path)\n        .transfer(content_image_path, output_image_size=800)\n        .save("stylized_image.jpg")\n    )\n```\n',
    'author': 'Henry Ruiz ',
    'author_email': 'henryruiz22@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
