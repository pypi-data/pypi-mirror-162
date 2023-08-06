"""
MIT License

Copyright (c) 2022 gx1285

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
ver = "v1.0.2"
def version_v():
    return ver
from typing import Type
import requests
import time
def version_check():
    """Check to see if a new version has been released.
    Added in Ver 1.0"""
    ctp_version = requests.get('https://raw.githubusercontent.com/gx1285/color-printtext/main/version.txt')
    if f"{ver}\n" != ctp_version.text:
        print(f"Latest Version{ctp_version.text}has been released.\nYour version is\n{ver}So, it needs to be updated.\nPlease update with pip.")
        return f"Latest Version{ctp_version.text}has been released.\nYour version is\n{ver}So, it needs to be updated.\nPlease update with pip."
    print("The latest version is installed.({ver})")
    return "The latest version is installed.({ver})"
def sleep(seconds=None):
  """Sleeps the operation for the specified number of seconds.
Added in Ver 1.0"""
  ctp_version = requests.get('https://raw.githubusercontent.com/gx1285/color-printtext/main/version.txt')
  if f"{ver}\n" != ctp_version.text:
        print(f"Latest Version{ctp_version.text}has been released.\nYour version is\n{ver}So, it needs to be updated.\nPlease update with pip.")
  if seconds == None:
      raise TypeError('The number of seconds of sleep is not specified.')
  elif type(seconds) == str:
      raise TypeError('an integer is required (got type str)')
  time.sleep(seconds)

def version():
  """Shows the current version.
Added in ver 1.0"""
  ctp_version = requests.get('https://raw.githubusercontent.com/gx1285/color-printtext/main/version.txt')
  if f"{ver}\n" != ctp_version.text:
        print(f"Latest Version{ctp_version.text}has been released.\nYour version is\n{ver}So, it needs to be updated.\nPlease update with pip.")
  print(f"Color-PrintText version {ver}")
  return f"Color-PrintText version {ver}"
def cprint(text=None,color=None):
  """
  colored print
  Added in ver 1.0
  """
  ctp_version = requests.get('https://raw.githubusercontent.com/gx1285/color-printtext/main/version.txt')
  if f"{ver}\n" != ctp_version.text:
        print(f"Latest Version{ctp_version.text}has been released.\nYour version is\n{ver}So, it needs to be updated.\nPlease update with pip.")
  if color == None:
    raise TypeError('Argument "color" is missing.')
  elif text == None:
    raise TypeError('Argument "text" is missing.')
  elif type(color) == int:
    raise TypeError('This argument is type str, but we got type int.')
  elif type(color) == int:
    raise TypeError('This argument is type str, but we got type int.')
  elif color == "nomal":
    print('\033[01m'+ text +'\033[0m')
  elif color == "translucent":
    print('\033[02m'+ text +'\033[0m')
  elif color == "special-character":
    print('\033[03m'+ text +'\033[0m')
  elif color == "underline":
    print('\033[04m'+ text +'\033[0m')
  elif color == "color-inversion":
    print('\033[07m'+ text +'\033[0m')
  elif color == "transparency":
    print('\033[08m'+ text +'\033[0m')
  elif color == "strikethrough":
    print('\033[09m'+ text +'\033[0m')
  elif color == "special-character2":
    print('\033[21m'+ text +'\033[0m')
  elif color == "black":
    print('\033[30m'+ text +'\033[0m')
  elif color == "red":
    print('\033[31m'+ text +'\033[0m')
  elif color == "green":
    print('\033[32m'+ text +'\033[0m')
  elif color == "ocher":
    print('\033[33m'+ text +'\033[0m')
  elif color == "blue":
    print('\033[34m'+ text +'\033[0m')
  elif color == "purple":
    print('\033[35m'+ text +'\033[0m')
  elif color == "turquoise":
    print('\033[36m'+ text +'\033[0m')
  elif color == "nomal2":
    print('\033[37m'+ text +'\033[0m')
  elif color == "black-background":
    print('\033[40m'+ text +'\033[0m')
  elif color == "red-background":
    print('\033[41m'+ text +'\033[0m')
  elif color == "green-background":
    print('\033[42m'+ text +'\033[0m')
  elif color == "ocher-background":
    print('\033[43m'+ text +'\033[0m')
  elif color == "light-blue-background":
    print('\033[44m'+ text +'\033[0m')
  elif color == "purple-background":
    print('\033[45m'+ text +'\033[0m')
  elif color == "turquoise-background":
    print('\033[46m'+ text +'\033[0m')
  elif color == "white-background":
    print('\033[47m'+ text +'\033[0m')
