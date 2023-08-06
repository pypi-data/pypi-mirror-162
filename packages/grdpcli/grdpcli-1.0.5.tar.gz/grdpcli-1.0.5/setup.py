#!/usr/bin/env python
import os
import sys

from distutils.core import setup

package_version = os.environ.get('CI_COMMIT_TAG', '1.0')
package_name = 'grdpcli'

data_files=[
        ('grdpcli/__init__.py'),
        ('grdpcli/commands.py'),
        ('grdpcli/variable.py'),
    ]

def package_files(data_files, directory_list):

    paths_dict = {}

    for directory in directory_list:

        for (path, directories, filenames) in os.walk(directory):

            for filename in filenames:

                file_path = os.path.join(path, filename)
                install_path = os.path.join('share', package_name, path)

                print(install_path)

                if install_path in paths_dict.keys():
                    paths_dict[install_path].append(file_path)

                else:
                    paths_dict[install_path] = [file_path]

    for key in paths_dict.keys():
        data_files.append((key, paths_dict[key]))

    return data_files


setup(name='grdpcli',
      version=package_version,
      description='Gitlab Rapid Development Platform CLI client',
      author='Anton Marusenko',
      author_email='anton.marusenko@onix-systems.com',
      url='https://onix-systems.com',
      data_files=package_files(data_files, ['grdpcli/']),
      install_requires=[
          'requests',
      ],
      scripts=["grdp"],
     )
