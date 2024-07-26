# Jetson Nano JetBot AI Project

This repository contains the code and documentation for a JetBot AI project using the Nvidia Jetson Nano. The JetBot is programmed to park in specific spaces, detect numbers, and follow lines using a variety of sensors and a CSI camera.

## Table of Contents

- [Introduction](#introduction)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Overview](#project-overview)
  - [Number Recognition](#number-recognition)
  - [Line Following](#line-following)
  - [Parking System](#parking-system)
- [Custom Models](#custom-models)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project, undertaken as part of the TOBB University of Economics and Technology 2023-2024 summer term graduation project, aims to develop an "autonomous parking mobile robot." The robot, named JetBot, is controlled by an NVIDIA Jetson Nano board and equipped with a CSI camera for image processing.

### Project Requirements

- **Task:** The JetBot must autonomously identify and park in a designated spot based on a given license plate number, without touching any red lines. Each contact with a red line results in a point deduction.
- **Autonomy:** The robot operates autonomously after receiving a start signal, with no manual intervention.
- **Feedback:** After parking, the total points deducted and the completion signal are sent to a personal computer via a web interface.
- **Flexibility:** During the demo, if the license plate number is changed, the robot must re-park in the new designated spot.
- **Time Constraint:** The parking process should not exceed five minutes.
- **Budget Constraint:** The total cost of materials, excluding VAT, should not exceed 4000 TL.

### Implementation Strategies

1. **Color Masking:** Uses OpenCV2 to mask red and black lines, retrieving their pixel coordinates (x, y).
2. **Object Detection:** Implements the YOLO NAS Object Detection (Accurate) model via Roboflow, an online tool for labeling and training models for object detection, classification, and segmentation.

This project showcases the capabilities of the NVIDIA Jetson Nano in robotics and AI applications, emphasizing autonomous functionality and real-time image processing.


## Hardware Requirements

- Nvidia Jetson Nano (with Jetpack 4.5.1)
- Waveshare JetBot AI Kit
- CSI Camera
- HC-SR04 Ultrasonic Sensor
- TCS34725 Color Sensors

## Software Requirements

- Ubuntu 18.04 (for Jetson Nano)
- Python 3.6.9
- OpenCV 4.5.1
- Roboflow (for model training and deployment)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/jetbot-project.git
   cd jetbot-project
