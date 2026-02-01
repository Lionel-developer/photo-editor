# Photo Editor (Python)

A desktop photo editor application developed in **Python** using **PySide6 (Qt)** for the graphical user interface and **Pillow (PIL)** for image processing.

This project was created as an individual student assignment and demonstrates object-oriented programming principles, GUI development, and basic image manipulation.

---

## Technologies Used
- Python 3
- PySide6 (Qt for Python)
- Pillow (PIL)
- Git & GitHub

---

## Features
1. Open images (PNG, JPG, JPEG, BMP, WEBP)
2. Save edited images (PNG / JPG / WEBP)
3. Brightness adjustment using percentage slider
4. Contrast adjustment using percentage slider
5. Saturation adjustment using percentage slider
6. Image rotation using degrees
7. Crop image by percentage from each side
8. Reset all edits to the original image
9. Undo last operation (single-step undo)

---

## Object-Oriented Programming Concepts

- **Encapsulation**  
  The `ImageEditor` class encapsulates image data, editing parameters, and undo logic.

- **Abstraction**  
  The user interface interacts with the image editor through high-level methods such as `load()`, `render()`, `reset()`, and `save_as()` without accessing internal details.

- **Inheritance**  
  All image editing operations inherit from the base class `ImageOperation`.

- **Polymorphism**  
  Each operation (brightness, contrast, saturation, rotation, crop) implements its own version of the `apply()` method.

---

## Project Structure
