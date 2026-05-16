import serial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

PORT = 'COM3'
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("3D Motion + Stable IR Dot Running")

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x_vals, y_vals, z_vals = [], [], []

SMOOTH = 0.85
THRESH = 0.01
SCALE = 20

px = py = pz = 0

# hold dot visibility
last_detect_time = 0

while True:
    line = ser.readline()

    if not line:
        continue

    try:
        parts = line.decode().strip().split(',')

        if len(parts) != 4:
            continue

        x = float(parts[0])
        y = float(parts[1])
        z = float(parts[2])
        ir = int(parts[3])

    except:
        continue

    # smoothing
    x = SMOOTH * px + (1 - SMOOTH) * x
    y = SMOOTH * py + (1 - SMOOTH) * y
    z = SMOOTH * pz + (1 - SMOOTH) * z

    px, py, pz = x, y, z

    # noise cut
    if abs(x) < THRESH: x = 0
    if abs(y) < THRESH: y = 0
    if abs(z) < THRESH: z = 0

    # scale
    x *= SCALE
    y *= SCALE
    z *= SCALE

    x_vals.append(x)
    y_vals.append(y)
    z_vals.append(z)

    if len(x_vals) > 30:
        x_vals.pop(0)
        y_vals.pop(0)
        z_vals.pop(0)

    ax.clear()

    # path
    ax.plot(x_vals, y_vals, z_vals)

    # arrow
    ax.quiver(0, 0, 0, x, y, z, length=1.2, normalize=False)

    # IR detection logic (stable)
    if ir == 0:
        last_detect_time = time.time()

    if time.time() - last_detect_time < 0.5:
        ax.scatter(0, 0, 0, s=80)

    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    ax.set_zlim(-20, 20)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.set_title("3D Motion")

    plt.pause(0.01)
