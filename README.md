# OpenCV-Based Human Tracking and Proximity Alert System

A computer vision and Arduino-based mini project that detects and tracks a human face using OpenCV and controls hardware using Arduino Uno.

## Features

- Real-time face detection using OpenCV
- Python to Arduino serial communication
- Servo motor movement
- Ultrasonic distance measurement
- 16x2 I2C LCD display
- RGB LED proximity indication
- Buzzer alert when a person comes too close

## Hardware Used

- Arduino Uno
- HC-SR04 Ultrasonic Sensor
- Servo Motor
- 16x2 I2C LCD
- RGB LED
- Buzzer
- Breadboard
- Jumper Wires
- Laptop with built-in camera

## Software Used

- Python
- OpenCV
- PySerial
- Arduino IDE
- VS Code

## Working

The laptop camera detects a face using OpenCV.

Python determines the face position and sends commands to Arduino through serial communication.

Arduino then controls the servo motor, ultrasonic sensor, LCD, RGB LED, and buzzer.

The ultrasonic sensor continuously measures the distance of the person from the system.

When the person comes within the danger range, the red LED and buzzer are activated.

## Project Flow

Camera  
↓  
OpenCV + Python  
↓  
Serial Communication  
↓  
Arduino Uno  
↓  
Servo + Ultrasonic Sensor + LCD + RGB LED + Buzzer

## Future Improvements

- Face recognition
- Person identification
- ESP32-CAM integration
- Wireless alerts
- Telegram notifications
- IoT dashboard
- Data logging