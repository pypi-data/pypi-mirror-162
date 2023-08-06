# -- coding: utf-8 --
"""
        Copyright (C) 2022  Salvador, Bahia
        Gabriel Mascarenhas, Marco A. C. Simões, Rafael Fonseca
        
        This file is part of BahiaRT GYM.

        BahiaRT GYM is free software: you can redistribute it and/or modify
        it under the terms of the GNU Affero General Public License as
        published by the Free Software Foundation, either version 3 of the
        License, or (at your option) any later version.

        BahiaRT GYM is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU Affero General Public License for more details.

        You should have received a copy of the GNU Affero General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from setuptools import setup, find_packages
#from distutils.core import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
  name = 'bahiart_gym',     
  packages=find_packages(),  
  version = '1.0.4',      
  license='agpl-3.0',        
  description = 'A toolkit to develop openAI Gym environments on top of the RCSSSERVER3D simulator',
  long_description=long_description,
  long_description_content_type="text/markdown",   
  author = 'Gabriel Mascarenhas, Marco A. C. Simões, Rafael Fonseca',                  
  author_email = 'teambahiart@gmail.com',     
  url = 'https://bitbucket.org/bahiart3d/bahiart-gym/',   
  keywords = ['CUSTOM', 'ENVIRONMENT', 'GYM', 'OPTIMIZATION', 'MACHINE', 'LEARNING'],
  install_requires=[            
          'gym',
          'numpy',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU Affero General Public License v3',   
    'Programming Language :: Python :: 3.7', 
    'Topic :: Scientific/Engineering :: Artificial Intelligence',     
  ],
)
