from distutils.core import setup, Extension
setup(name='rootfinder', version='1.0',  \
      ext_modules=[Extension('rootfinder', ['python_rootfinder_iface.c'])])