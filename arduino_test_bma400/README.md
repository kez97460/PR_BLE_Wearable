# Testing the BMA400 accelerometer from any arduino-compatible board

## Obective

This folder contains a PlatformIO project that uses the Arduino framework to test the BMA400 from any compatible microcontroller. 

## Requirements 

It is recommended to use the PlatformIO VSCode extension. To install it please follow the instructions from the [official website](https://platformio.org/install/ide?install=vscode).

It is also possible to use the CLI version. 

## Using different microcontrollers

The project was created to be used with ST's **Nucleo L432KC** board. 

However, PlatformIO allows the project to be used with different boards ([list available here](https://docs.platformio.org/en/latest/boards/index.html)). 

To use a different board, simply modify the `platformio.ini` file (see commented lines in the file). 
