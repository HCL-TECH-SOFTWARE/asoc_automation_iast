from setuptools import setup

setup(name='asoc_automation_iast',
      version='0.2',
      description='asoc interface for handling iast',
      url='http://github.com/hclproducts/asoc_automation_iast',
      author='Tali Rabetti',
      author_email='tali.raetti@hcl.com',
      packages=['asoc_automation_iast'],
      zip_safe=False, install_requires=['urllib3', 'requests'])
