# IOT Miami - LoRa Mesh Chat

<script defer src="https://use.fontawesome.com/releases/v5.3.1/js/all.js"></script>

<link rel="stylesheet" href="https://cdnjs.com/libraries/bulma" />

## Overview

This is a demonstration of a long range mesh network chat system.  The mesh network protocol will be simple but capable for the purpose of this project, more information below.


## Requirements

Please make sure that the following sections are ready to go before starting with the actual implementation of the chat system.  There are several pieces of hardware and software involved in this demonstration.

### Hardware

The following hardware is used in this demonstration and its usage is assumed for the remainder of the document.  Other hardware can be used but modifications and matching of libraries are outside the support herein.

* Raspberry Pi 3+ unboxed and working.
* Sparkfun LoRa Gateway 1 Channel ESP32 and antenna.
    - A `3.07"` (inch) wire can be soldered onto the board for the `915 MHz` frequency.
    - _Note: The wire must include additional length so that the soldered part does not include the needed length but is additional to._
* A computer that will be used for development running modern Linux, macOS, or Windows.
* Internet connections for the development computer and Pi.

### Software

Checkout the requirements below for the different pieces of software needed for each hardware platform.

#### Development Computer

A computer running either Linux, macOS, or Windows is needed in order to connect to the different pieces of hardware and use the outlined software in this document.  Linux is the assumed operating system for this document but all steps should work with other configurations using additional software and/or modifications.

* Arduino IDE - The defacto standard and easiest entry point to embedded development.
    - Boards - Define communication and configurations for the IDE to interact with the different hardware provided by vendors.
        - [Expressif ESP32](https://github.com/espressif/arduino-esp32)
            - `https://dl.espressif.com/dl/package_esp32_index.json`
        - [Sparkfun](https://github.com/sparkfun/Arduino_Boards) (optional)
            - `https://raw.githubusercontent.com/sparkfun/Arduino_Boards/master/IDE_Board_Manager/package_sparkfun_index.json`
    - Libraries - Groupings of software that provide specific functions for usage with micro controllers.
        - [LoRa](https://github.com/sandeepmistry/arduino-LoRa) by Sandeep Mistry
* USB Drivers (optional) - If required for your system make sure to install the necessary USB drivers, this is most often with Windows.
* [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/) (optional) - The most popular and trusted SSH client for Windows.

#### Raspberry Pi

The Pi needs to have an operating system installed with SSH access already setup and working.  The remainder of the required software can be setup using the `./scripts/setup-pi.sh` bash script on the Pi while logged into SSH, instructions are provided below under Installation.

_Note: An easy way to enable SSH on the Raspberry Pi is right after you write the operating system ISO to the SD card is to create a new empty file called `ssh.txt` right on the SD card itself.  Another shortcut to enable SPI is to create another file on the SD card called `config.txt` with the contents of `dtparam=spi=on` inside it.  Now when you put the SD card inside the Pi and power it on you will have SSH and SPI already enabled._

Python 2.7 will be the target programming language on the Raspberry Pi and should be installed by default during the operating system installation process.  If not the setup script mentioned above will install them after updating.

__Helpful links:__

* [Raspbian](https://www.raspberrypi.org/downloads/raspbian/)
* [Python](https://www.python.org)


## Device Communication

Communication will be done on a serial connection between the LoRa Gateway module and the Raspberry Pi.  This will require a USB cable capable of connecting between them, this is not the power port on the Raspberry Pi.

The basic idea is that the LoRa module will act as a proxy between the LoRa WiFi communication and the Raspberry Pi. The Pi will perform all the logic outside the transmit and receive functions done by the module.

Receive = `LoRa -> USB -> Pi`

Transmit = `Pi -> USB -> LoRa`

An alternative approach is use a WiFi connection between the two modules and is outlined in the [WiFi Communication](docs/WIFI.md) documentation.


## Mesh Network

This LoRa chat demo will pass small messages over a LoRa mesh network that can span several miles.  The messages will need to be small to keep things simple.  For more information on mesh networking please refer to the [Wikipedia](https://en.wikipedia.org/wiki/Mesh_networking) page.

[LoRa](https://en.wikipedia.org/wiki/LoRa) will be used as the transmit mechanism for this demonstration. Because we are in the `USA` we will be using the `915 MHz` frequency, for more information about frequencies for other countries please refer to the LoRa library documentation on configuration changes.

### Mesh Terminology

* __Node__ - Is a module connected to the LoRa mesh network, as defined in this document, adhering to the chat protocol.  For this demonstration the LoRa Gateway module and Raspberry Pi are considered a node together because the Pi will function as the brain and the LoRa Gateway the mouth in our chat system.
* __Message__ - Is the full network byte array packet that was sent by a node on the network.  Its format and payloads are described in the following sections of this document.
* __Network Reset__ - All nodes and messages are stored on the network and in order to clear that information to start new after testing or whatever the reason may be a network reset is needed.  In order to do this all connected nodes must be reset or powered off then on again in order to clear its memory.
    - _Note: A software solution can be implemented as good way to expand upon what is provided here for something to automatically do this without manual interaction._
* __Sync Word__ - Is a way to identify a network and provide multiple networks on the same frequency.  For demonstration purposes this will be constant to `0x33`.
    - _Note: A software solution can be implemented as good way to expand upon what is provided here for something like private messaging._
* __ID__ - A single `byte` that identifies a node on the network and must be unique to each new node joining the network.  Once an ID is registered it can no longer be used by another node on the network unless a network reset is performed.
* __Sequence__ - The id sequence number that is randomly generated by the node and incremented by the node each message.  If the sequence number overflows it will start back at `1` automatically as part of the mesh network protocol.  If a message's sequence number is not the next number for an ID it should be ignored.

### Mesh Storage

To simply this implementation for demonstration services all data will be stored in memory allowing for network resets to be effective.  A map of network node ids to sequence numbers should be maintained for validation of messages, at the least.

### Mesh Protocol

All data sent over LoRa will be in big-endian `byte` arrays at fixed lengths according to type except for the `BLOCK` payload type defined in the chat protocol section will have a dynamic length with defined size.

The table directly below defines the mesh network message format that all nodes on the network must adhere to in order for consensus.

| Byte(s) | Name | Usage |
|---|---|---|
| 1 | ID | The `byte` id of the sending node. |
| 2 | SEQ | Sequence number that should be +1 from the stored value on the node, or reject. |
| 4 | UNIX | Is the number of seconds since unix epoch. |
| 1 | TYPE | The type of the payload contained in this message. |
| 1 | SIZE | The size of the payload but <240. |
| SIZE | PAYLOAD | The payload contained within the message that provides additional features. |

* The minimum size of a message is 9 bytes not including the payload.
* The ID should match an already registered node on the network unless the message is a registration message or ignore.
* The SEQ should be the next number for the node or ignore the message.
* The UNIX timestamp should not be less or more than 10 seconds ago or ignore for this demo at this time.
* The TYPE should be a valid type defined in this document or ignore.
* The SIZE should be the same length of the payload as expected and measured.
* The PAYLOAD should match in size with SIZE or TYPE expected sizes and should be <240 bytes in length.
* Messages should only be relayed 1 time but can this can be changed later to allow for defined hop numbers between nodes.

### Mesh Payloads

There is only 1 payload at this time for the mesh network protocol and that is to register nodes on the network.  This can easily be changed to expand on the network features.

#### Register Payload

This will register the id and sequence number on the network for the defined node in the message.  If the id is already used then the message will be ignored. If a size or payload is provided then the message is also ignored but this could easily change with the addition of cryptography.

| TYPE | SIZE | PAYLOAD |
|---|---|---|
| `0x00` | 0 | `NULL` payload as sequence number in message will be used for the starting point. |


## Chat

The following is an outline for the mesh network messages that are used for the demo.

### Chat Terminology

* __ACCT__ - The account name registered on the network using the chat protocol.  An account name is limited to 20 bytes and must be alphanumeric. This is what should be shown on the chat log for the network.
* __BLOCK__ - Block data that will be sent over the mesh network and stored on nodes for display.  Right now this limited to small SMS or tweet like messages due to limitations.

### Chat Storage

Just like with mesh storage, chat storage should be in memory to allow for network resets and should include a vector of payloads that can be displayed in the order they were received.

### Chat Protocol

The following is a basic protocol definition for the chat demonstration application.  It is lightweight and uses simple alphanumeric values

#### Chat Payloads

There are only a couple payloads defined for the chat protocol at this time but can be expanded upon very easily.

#### Account Payload

Register or change the name for a node on the network by sending an account message.

| TYPE | SIZE | PAYLOAD |
|---|---|---|
| `0x10` | <=20 | The name of the account to show in the logs matched with the node id. |

* If the `ACCT` name is registered then ignore, if ids are the same then change.

#### Block Payload

Send a block data over the mesh network to all of the connected nodes.  At this time the data is limited to SMS or tweet like messages but can easily be expanded upon.

| TYPE | SIZE | PAYLOAD |
|---|---|---|
| `0x11` | <200 | The message body for display in the log. |


## Installation

To upload, burn, or flash the hardware devices please follow the notes outlined for each.

### LoRa Gateway

First, setup the mouth of the chat platform by flashing a sketch onto the device over USB using the Arduino IDE.

* Connect the LoRa Gateway module to the development computer using the USB cable.
* Open the `./lora/lora.ino` Arduino IDE sketch and go to `Tools -> Board -> SparkFun LoRa Gateway 1-Channel`.
* Also select the upload speed by selecting `Tools -> Upload Speed -> 115200` to avoid possible issues.
* Also select the by port going to `Tools -> Port -> USB` where `USB` is the correct port for you connected device.
* Click on the Upload button to flash the sketch onto the module.

### Raspberry Pi

Second, get the brains of the chat platform running doing the following.

* Unplug the USB cable, connected to the LoRa module, from the development computer and plug it into one of the USB ports on the Pi.  There should be a USB connection between the LoRa Gateway and Raspberry Pi now.
* Login to the Pi using SSH and if on Windows use PuTTY.
* Execute `wget https://github.com/pagarba/IOTMiami/raw/master/lora-chat/scripts/setup-pi.sh` to download and setup the Pi.
* Now that we have the setup script run `bash setup-pi.sh` which will update the system, install software, and clone the repository.


## Running

To start the python script while still in a SSH connection do the following.

* Change into the Pi directory by executing `cd pi`.
* Start the Python script by running `env FLASK_APP=chat.py FLASK_ENVIRONMENT=development flask run`.
* You should see that the script is running and waiting for input.

