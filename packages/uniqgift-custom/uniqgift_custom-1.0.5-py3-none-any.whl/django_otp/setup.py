import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='uniqgift-django-otp',  
     version='0.1',
     author="John Fang",
     author_email="john.fang@uniqgift.com",
     description="A modified version of django-otp",
     long_description=long_description,
   long_description_content_type="text/markdown",
     packages=['django_otp'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
