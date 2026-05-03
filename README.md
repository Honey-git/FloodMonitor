# Flood Monitoring and Alert System

## Overview
This project implements a real-time Flood Monitoring and Alert System designed to detect rising water levels and provide early warnings in flood-prone areas. The system primarily relies on sensor-based measurements and rule-based decision logic for fast and reliable flood level classification.

In addition to the rule-based core, a machine learning (Logistic Regression) model is used as a **validation layer** to verify and analyze the consistency of the generated flood risk levels. This hybrid approach improves confidence in system outputs while preserving real-time performance.

---

## Objectives
- Monitor water levels continuously using sensors
- Classify flood risk levels using predefined rules
- Validate rule-based decisions using an ML model
- Display real-time data and alert status
- Provide a reliable and low-latency flood monitoring solution

---

## System Components

### Hardware Components
- **ESP32 Microcontroller** – Central controller for sensor input and rule execution
- **Ultrasonic Sensor** – Measures distance to water surface
- **LCD Display** – Displays water level and alert status
- **Power Supply** – Provides stable operation

---

### Software Components
- Embedded firmware for ESP32
- Rule-based flood level classification logic
- Machine learning model for validation and analysis
- Display control logic

---

## Working Principle

1. The ultrasonic sensor measures water level in real time.
2. The ESP32 processes sensor data and applies predefined threshold rules.
3. Flood risk is classified into levels such as Safe, Warning, or Danger.
4. The classified output is displayed on the LCD.
5. Sensor readings and rule-based outputs are passed to the ML model.
6. The ML model evaluates the consistency of the classification and validates escalation levels.
7. Any discrepancies can be flagged for analysis or future system tuning.

---

## Flood Level Classification (Rule-Based Core)

The primary decision-making mechanism uses deterministic threshold rules:

- **Safe Level** – Water level within normal limits  
- **Warning Level** – Rising water level requiring attention  
- **Danger Level** – Critical water level indicating possible flooding  

This ensures:
- Fast response
- Predictable behavior
- Independence from training data during real-time operation

---

## Machine Learning Validation Layer

The ML model is **not used for real-time prediction or control**.  
Instead, it serves as a **secondary validation mechanism**.

### Purpose of ML Integration
- Validate rule-based flood level classifications
- Analyze escalation patterns
- Reduce false alerts through consistency checks
- Support future system optimization

### Key Characteristics
- Operates alongside the rule-based system
- Does not override hardware decisions
- Used for analytical validation rather than actuation
- Can be trained on historical or simulated data

This architecture ensures reliability while enabling data-driven insights.

---

## Testing and Validation

### Hardware Testing
- Individual testing of ESP32, ultrasonic sensor, and LCD
- Verification of sensor accuracy and display updates

### Rule-Based Validation
- Threshold testing using controlled water level variations
- Verification of correct alert triggering

### ML-Based Validation
- Comparison of ML outputs with rule-based classifications
- Evaluation of consistency across different water level scenarios
- Analysis of misclassification or edge cases

---

## Design Considerations
- Real-time responsiveness prioritized
- Rule-based logic retained as authoritative
- ML kept decoupled from hardware control
- Suitable for resource-constrained environments

---

## Limitations
- ML model does not perform real-time prediction
- Accuracy depends on sensor calibration
- Thresholds require location-specific tuning
- No remote alerting or cloud integration in current version

---

## Future Enhancements
- Full IoT-based remote monitoring
- Automated threshold tuning using ML feedback
- SMS / mobile notifications
- Multi-sensor fusion (rainfall, flow rate)
- Cloud-based analytics dashboard

---

## Applications
- Flood-prone urban areas
- Drainage and sewage monitoring
- Bridge and river level monitoring
- Local early warning systems

---

## Conclusion
This project demonstrates a hybrid flood monitoring approach that combines real-time rule-based decision-making with machine learning–based validation. The system prioritizes reliability and responsiveness while enabling intelligent analysis, making it suitable for practical deployment and future smart infrastructure integration.

---

## Author
Developed as an academic project for flood monitoring and early warning applications.
