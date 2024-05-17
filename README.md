# Machine to Human Vision

Senior Design Project for Iowa State University CPRE/CYBE/EE/SE 491/492 - Fall 2023 to Spring 2024

## Authors

#### Project Contact: Alexander Stoychev

- @Alexander Black
- @Jacob Burns
- @Jacob Lyons
- @Sergio Perez-Valentin
- @Sami Bensellam
- @Yogi Chander

## Project Abstract

The primary objective of this endeavor is to develop an advanced navigation solution tailored for individuals with visual impairments. This endeavor seeks to harness the capabilities of machine vision and machine learning technologies to devise an innovative alternative perception approach. Through the integration of these cutting-edge advancements, the intention is to convey relevant information to users through the senses of touch and sound.

The crux of the proposed feedback mechanism revolves around two critical aspects: firstly, the determination of object proximity achieved through the application of stereo triangulation; secondly, the precise identification of objects facilitated by sophisticated machine learning algorithms. This holistic feedback mechanism serves as a fundamental guide for users, allowing them to comprehend their surroundings, navigate through obstacles, and gain a comprehensive understanding of their environment.

#### Haptic Feedback for Object Proximity

Employing stereoscopic cameras, the system will meticulously gauge depth information, subsequently conveying these depth metrics to users via haptic feedback motors that generate vibrations. Notably, there are 16 distinct haptic feedback motors deployed within the design. These motors serve as conduits of tactile information, translating the concept of proximity into distinct and discernible vibrational patterns. The vibrational intensity emitted by each motor is calibrated in accordance with the relative distance of objects.

We determine object proximity based on the image disparity (the farther away, the smaller the disparity).

#### Object Identification

Use the camera images and identify objects within the image. There are many existing apis that can be used to identify objects within an image. This could be expanded to identify individuals similar to google photos. After identification, the aim is to utilize an existing text-to-speech converter to read all of the objects that are identified within the image.

## Expected Deliverables

* Determining the most suitable existing stereo camera system to buy.
* Developing a working prototype utilizing a laptop for stereo only.
* Determining the best API for object identification and getting it to work with the existing stereo system.
* Getting a fully functional prototype for the project using a computer by combining the two functionalities.
* Shifting the project towards creating a mobile application that:
    - Gets Stereo camera image data.
    - Uses the existing code in the prototype and implements that functionality within the application.
    - Move the image processing to the cloud.
* Bring a person with visual impairments to use the product and provide feedback.

## Set-Up

1. Download PyCharm at https://www.jetbrains.com/pycharm/download/?section=windows
2. Clone this repository from the PyCharm start screen.
3. Open the terminal and install openCV with `pip install opencv-python`

## Styling
https://peps.python.org/pep-0008/#naming-conventions
