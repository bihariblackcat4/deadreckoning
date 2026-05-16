# Technical Report: 3D Inertial Dead Reckoning with IMU and Sensor Fusion

## 1. System Overview
This project implements a real-time **3D Dead Reckoning Navigation System** utilizing an **MPU6050 Inertial Measurement Unit (IMU)** and an **Infrared (IR) Stability sensor**. The system captures raw physical acceleration vectors, processes them through sequential digital signal processing (DSP) filters to eliminate sensor artifacts, and applies kinematic double-integration to track and reconstruct a physical trajectory in 3D spatial coordinates.

---

## 2. Hardware Architecture & Pin Mapping
The firmware is developed for microcontroller platforms (such as the ESP32) utilizing hardware-level I2C communication protocols and digital GPIO state sampling.

| Sensor Module | Physical Pin / Protocol | Function |
| :--- | :--- | :--- |
| **MPU6050 IMU** | SDA (GPIO 21), SCL (GPIO 22) | Multi-axis Linear Acceleration (ax, ay, az) |
| **IR Sensor** | GPIO 4 (Digital Input) | Event Marker / Spatial Landmark Initialization |
| **Serial Interface** | UART via USB (115200 Baud) | Real-time Data Streaming to Host Machine |

---

## 3. Digital Signal Processing & Filter Design

To extract meaningful spatial trajectories from noisy micro-electromechanical systems (MEMS) sensors, a multi-stage DSP pipeline was designed and executed across both the firmware and software levels.

### A. Static DC Offset Calibration
MEMS accelerometers suffer from inherent manufacturing bias (zero-g offset). To eliminate this systemic error, a static calibration routine samples the stationary sensor N = 1000 times upon boot.
This calculated DC bias (ax_off, ay_off, az_off) is dynamically subtracted from all subsequent runtime sensor readings to center the acceleration vector precisely around the origin.

### B. Exponential Moving Average (EMA) Low-Pass Filter
High-frequency mechanical vibrations and structural noise introduce significant variance into the raw data stream. An **Exponential Moving Average (EMA)** filter acts as a digital low-pass filter to smooth the acceleration signal.
* **Firmware Layer (alpha = 0.6):** Provides lightweight, real-time smoothing directly on the microcontroller to suppress high-frequency jitter before transmission.
* **Software Layer (alpha = 0.85):** Aggressively stabilizes the incoming data stream on the host side, prioritizing trend consistency over instant structural spikes to prepare the vector for integration.

### C. Threshold-Based Dead-Zone (Noise Gate)
Even after smoothing, minute baseline fluctuations around the zero-point accumulate rapidly during integration, causing catastrophic position drift when the device is completely stationary. A non-linear **Noise Gate Threshold** is implemented:
By assigning a threshold (THRESH = 0.01G to 0.05G), low-level white noise is clipped to absolute zero, halting false velocity accumulation.

### D. Software-Level Window Debouncing (IR Stability Filter)
The digital IR sensor input is prone to optical contact bounce and edge transition noise. A non-blocking asynchronous timer routine handles software debouncing using the system clock:
If delta_t > 50 ms, the state transition is validated and latched. This guarantees that real-world triggers are registered cleanly without stalling the critical execution loops of the system.

---

## 4. Dead Reckoning Tracking Logic

True dead reckoning maps an absolute position trajectory over time relative to a known starting coordinate. The Python execution layer performs real-time double integration on the filtered data stream.
### Step 1: Physical Unit Scaling
Raw measurements from the MPU6050 are scaled based on the configured sensitivity range (16384 LSB/G). The normalized values are converted to standard metric acceleration ($m/s^2$) by multiplying by Earth's gravitational constant ($g = 9.81 m/s^2$).

### Step 2: First Linear Integration (Velocity Tracking)
Using the dynamic time step (dt), which measures the exact time elapsed between consecutive serial reads, velocity (v) is updated via Riemann sum integration:
*Decay Mitigation:* If the noise gate clamps acceleration (a = 0), the velocity vector is scaled down by an artificial dampening factor (v * 0.9) to force the system back to rest and prevent infinite velocity drift.

### Step 3: Second Linear Integration (Position Tracing)
The current physical position coordinate (s) is updated using the kinematic equations of motion, factoring in the contribution of constant acceleration over the micro-interval:
*Decay Mitigation:* If the noise gate clamps acceleration (a = 0), the velocity vector is scaled down by an artificial dampening factor (v * 0.9) to force the system back to rest and prevent infinite velocity drift.

### Step 3: Second Linear Integration (Position Tracing)
The current physical position coordinate (s) is updated using the kinematic equations of motion, factoring in the contribution of constant acceleration over the micro-interval:
