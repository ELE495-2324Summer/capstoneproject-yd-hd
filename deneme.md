# Jetson Nano JetBot AI Project

This repository contains the code and documentation for a JetBot AI project using the Nvidia Jetson Nano. The JetBot is programmed to park in specific spaces, detect objects, and follow lines using a variety of sensors and a CSI camera.

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

This project demonstrates the capabilities of the Nvidia Jetson Nano in robotics and AI applications. The JetBot is equipped with a CSI camera, ultrasonic sensors, and color sensors to perform tasks such as object detection, line following, and autonomous parking.

## Hardware Requirements

- Nvidia Jetson Nano (with Jetpack 4.5.1)
- Waveshare JetBot AI Kit
- CSI Camera
- Ultrasonic Sensors
- Color Sensors

## Software Requirements

- Ubuntu 18.04 (for Jetson Nano)
- Python 3.6.9
- OpenCV 4.5.1
- PyTorch
- Roboflow (for model training and deployment)
- Custom object detection models (e.g., YOLOv8, SSD-MobileNet-v2)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/jetbot-project.git
   cd jetbot-project
