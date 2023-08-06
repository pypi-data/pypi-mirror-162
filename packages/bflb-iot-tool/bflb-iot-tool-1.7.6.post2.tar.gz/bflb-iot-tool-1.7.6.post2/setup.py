#!/usr/bin/env python

from setuptools import setup, find_packages

longdesc = """
## Bouffalolab Iot Command Tool
============

The functions of bflb_iot_tool is the same as DevCube(IOT View) which is a GUI tool for image programing.
bflb_iot_tool is designed for the convenience of integrating into the compilation system after image buid,
and making it more easy for users who are accustomed to using command line operations.

### basic download config:

* --chipname：mandatory, name of chip(bl602/bl702/bl616...)
* --interface：1.uart, 2.jlink, 3.cklink, 4.openocd, default is uart
* --port：serial port or jlink serial number
* --baudrate：baudrate of serial port, default is 115200
* --xtal：xtal on the board, for bl602,1:24M,2:32M,3:38.4M,4:40M(default value when not specified),5:26M; for bl702,1:32M(default value when not specified); for bl616,just use value 7(auto adjust)
* --config：eflash loader configuration file, default is chips/blXXXX/eflash_loader/eflash_loader_cfg.ini
* --ota：dir of ota file, default is chips/blXXXX/ota

### files for download:

1.scattered files:
* --firmware：mandatory, select the firmware binary file which your sdk build out
* --dts：optional, select the device tree file you used
* --pt：mandatory, partition table of flash, default is located in chips/chipname/partition
* --boot2：mandatory,boot2 binary file as bootloader, default is located in chips/chipname/builtin_imgs/boot2_isp_xxxxx
* --mfg：optional, mfg binary file, only use when do RF test
* --romfs：optional, romfs dir to create romfs.bin

2.one whole image file:
* --addr：address to program, default is 0
* --single：the single file to be programmed ,the tool will add nothing for this file

### other options:

* --build：build image only,not program into flash

### EXAMPLE:
* bflb_iot_tool.exe --chipname=bl602 --port=COM28 --baudrate=2000000 --firmware="helloworld_bl602.bin" --pt="chips/bl602/partition/partition_cfg_2M.toml" --dts="chips/bl602/device_tree/bl_factory_params_IoTKitA_40M.dts"
* bflb_iot_tool.exe --chipname=bl602 --port=COM28 --baudrate=2000000 --firmware="helloworld_bl602.bin" --pt="chips/bl602/partition/partition_cfg_2M.toml" --dts="chips/bl602/device_tree/bl_factory_params_IoTKitA_40M.dts" --build
* bflb_iot_tool.exe --chipname=bl602 --port=COM28 --baudrate=2000000 --addr=0x0 --firmware="helloworld_bl602.bin" --single
"""

packages = [
    'bflb_iot_tool',
    'bflb_iot_tool.core',
    'bflb_iot_tool.libs',
    'bflb_iot_tool.libs.bl616',
    'bflb_iot_tool.libs.bl602',
    'bflb_iot_tool.libs.bl702',
    'bflb_iot_tool.libs.bl808',
]

entry_points = {'console_scripts': ['bflb-iot-tool = bflb_iot_tool.__main__:run_main']}

setup(
    name="bflb-iot-tool",
    version="1.7.6.post2",
    author="bouffalolab",
    author_email="jxtan@bouffalolab.com",
    description="Bouffalolab Iot Tool",
    long_description=longdesc,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://pypi.org/project/bflb-iot-tool/",
    packages=packages,  # 包的代码主目录
    #package_data=package_data,
    include_package_data=True,
    entry_points=entry_points,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: Unix',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'ecdsa>=0.15',
        'pycryptodome==3.9.8',
        'bflb-crypto-plus==1.0',
        'pycklink>=0.0.7',
        'pyserial==3.5',
        'pylink-square==0.5.0',
        'portalocker==2.0.0'
    ],
    python_requires='>3.0,<4.0',
    zip_safe=False,
)
