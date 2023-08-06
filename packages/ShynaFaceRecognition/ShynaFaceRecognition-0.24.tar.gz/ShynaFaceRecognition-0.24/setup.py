from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup_args = dict(
     name='ShynaFaceRecognition',
     version='0.24',
     packages=find_packages(),
     author="Shivam Sharma",
     author_email="shivamsharma1913@gmail.com",
     description="This package will take care of face recognition.",
     long_description=long_description,
     long_description_content_type="text/markdown",
    )

install_requires = ['ShynaDatabase', 'ShynaTime', 'ShynaProcess', 'face_recognition', 'setuptools', 'wheel']

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
