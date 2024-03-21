from setuptools import setup

setup(name='asoc_automation_iast',
      version='0.17',
      description='asoc interface for handling iast',
      url='https://github.com/HCL-TECH-SOFTWARE/asoc_automation_iast',
      author='Tali Rabetti',
      author_email='tali.rabetti@hcl.com',
      packages=['asoc_automation_iast'],
      zip_safe=False, install_requires=['urllib3', 'requests'])
