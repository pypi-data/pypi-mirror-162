# pyzeptrion

This library can be used to access Zeptrion devices (made by the Feller company, Schneider Electric).
I don't have any affiliations with the company and the code has not been reviewed, approved or released by Feller AG. 
The library was originally intended to be used to integrate a so-called "component" with home-assistant. 
I tested the code only with the two following products (which I call "Zeptrion Devices"):


    [2 channel module](https://online-katalog.feller.ch/kat_details.php?fnr=3340-2-B.ZEP&_ga=2.89688093.760657227.1660056309-67432971.1660056309)
    [4 channel module](https://online-katalog.feller.ch/kat_details.php?fnr=3340-4-B.FMI.61&_ga=2.21997757.760657227.1660056309-67432971.1660056309)

I don't have access to other products, but the API provided by Feller AG is well documented and easy to implement.

 _____


## Requirements
To use this library you must have:

- Some Zeptrion devices installed (these are actually switches)
- One or more supported consumer like bulbs or blinds wired to the switches
- Network connection to your local network

 _____

## Installation

    $ pip3 install pyzeptrion

 _____

## Examples

You'll find an example file in the examples directory and you can try to launch it as follows:

    python3 -m examples.example

The example code implements a few simple scenarios, like turning on and off a bulb, moving a blind or closing and opening all the discovered blinds in the network. The library relies heavily on asynchroneous calls (using the aiohttp and asyncio libraries) and implements three classes, one for the `ZeptrionDevice` (device.py) and two derived classes `ZeptrionBulb` (bulb.py) and `ZeptrionBlind` (blind.py). To create a corresponding object, you only need to know the IP address and the channel of the consumer (you can find these information via the Feller Zeptrion app or using the command line interface included in the library)

 _____

## Command Line Interface (cli)

There is also a command line interface tool. Here are a few examples on how to us it:


    python3 -m pyzeptrion.cli discover

This will discover all the Zeptrion devices in your local network using the zeroconf protocol. You'll get a list of all the consumers attached to a Zeptrion device with their IP addresses, channels and type of consumer as defined through the Feller Zeptrion app.

    python3 -m pyzeptrion.cli set -a 192.168.0.181 -c 1 -p on

This will turn on the bulb with the address 192.168.0.181 in the first channel of the Zeptrion device

    python3 -m pyzeptrion.cli set -a 192.168.0.185 -c 2 -p move_close

This will close the blind attached to the channel 2 of the Zeptrion device with the IP address 19.168.0.185

The allowed command for a bulb are:
- on
- off
- toggle
- dim_down
- dim_up

And for the blinds:
- move_close
- move_open
- stop

The library supports a few more options (like dim_down and stop after a specified amount of time in milliseconds) but I didn't implement them in the command line tool.

