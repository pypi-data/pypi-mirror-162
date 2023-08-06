#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
               ..
              ( '`<
               )(
        ( ----'  '.
        (         ;
         (_______,' 
    ~^~^~^~^~^~^~^~^~^~^~
    Author: thong
    Company: M O B I O
    Date Created: 11/08/2022
"""

import os
import shutil

FOLDER_HOME, _ = os.path.split(os.path.abspath(__file__))


def main():
    # Source path
    folder_source = FOLDER_HOME + "/config/"
    project_path = input("Nhap duong dan thu muc project (Mac dinh lay thu muc hien tai):")
    if not project_path:
        project_path = os.path.abspath(os.getcwd())
    # List files and directories
    print("Before copying file:")
    print(os.listdir(folder_source))
    print("Destination directory: ", project_path)
    # fetch all files
    for file_name in os.listdir(folder_source):
        # construct full file path
        source = folder_source + file_name
        destination = project_path +"/"+ file_name
        # copy only files
        if os.path.isfile(source):
            shutil.copy(source, destination)
            print('copied', file_name)


if __name__ == '__main__':
    main()
