##############################################################################
# Copyright 2015 SoundHound, Incorporated.  All rights reserved.
##############################################################################
from setuptools import setup, Extension
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


SPEEX_SRC_DIR = "pySHSpeex/soundhound-speex"
SOURCES = "cb_search.c exc_10_32_table.c exc_8_128_table.c filters.c gain_table.c hexc_table.c high_lsp_tables.c " \
          "lsp.c ltp.c speex.c stereo.c vbr.c vq.c bits.c exc_10_16_table.c exc_20_32_table.c exc_5_256_table.c " \
          "exc_5_64_table.c gain_table_lbr.c hexc_10_32_table.c lpc.c lsp_tables_nb.c modes.c modes_wb.c nb_celp.c " \
          "quant_lsp.c sb_celp.c speex_callbacks.c speex_header.c window.c soundhound.c "
SOURCES = [SPEEX_SRC_DIR + "/src/%s" % x for x in SOURCES.split()]

ext_modules = [Extension('pySHSpeex',
                         sources=['pySHSpeex/pySHSpeexmodule.c'] + SOURCES,
                         include_dirs=[SPEEX_SRC_DIR + '/include'],
                         define_macros=[('FIXED_POINT', '1')])]

setup(name='Houndify',
      packages=['houndify'],
      ext_modules=ext_modules,
      version='2.0.10',
      license='MIT',
      description='Houndify libraries and SoundHound speex encoder',
      long_description=README,
      long_description_content_type='text/markdown',
      url='https://www.houndify.com/sdks#python',
      author_email='pypi-maintainer@soundhound.com',
      author='Soundhound Inc.',
      maintainer='Soundhound Inc.',
      keywords=['houndify'],
      classifiers=[
          'Programming Language :: Python :: 3'
      ]
      )
