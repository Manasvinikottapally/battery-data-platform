
from scipy.io import loadmat
from pathlib import Path
from collections import Counter

# Location of the NASA battery file
file_path = Path("data/raw/nasa/batteries/B0005.mat")

# Load MATLAB data
data = loadmat(file_path)

# Display available variables
print("Variables in MATLAB file:")
print(data.keys())

# Read the battery record
battery = data["B0005"]

print("\nBattery data type:", type(battery))
print("Battery data shape:", battery.shape)
print("Battery fields:", battery.dtype.names)


# Access the cycle array inside the battery structure
cycles = battery[0, 0]["cycle"]

print("\nCycle array shape:", cycles.shape)

# Count recorded cycle entries
print("Total cycle records:", cycles.size)

# Inspect the first cycle
first_cycle = cycles[0, 0]

print("\nFirst cycle fields:", first_cycle.dtype.names)

# Read the cycle type
cycle_type = first_cycle["type"][0]

print("First cycle type:", cycle_type)

# Inspect the measurement structure
cycle_data = first_cycle["data"][0, 0]

print("Measurement fields:", cycle_data.dtype.names)

# Count the different operation types
cycle_types = []

for cycle in cycles[0]:
    operation = cycle["type"][0]
    cycle_types.append(operation)

counts = Counter(cycle_types)

print("\nBattery B0005 - Cycle Summary")

for operation, count in counts.items():
    print(f"{operation}: {count}")

# Inspect the first discharge cycle
for cycle in cycles[0]:
    if cycle["type"][0] == "discharge":
        discharge_data = cycle["data"][0, 0]

        print("\nFirst discharge measurement fields:")
        print(discharge_data.dtype.names)

        print("\nDischarge capacity:")
        print(discharge_data["Capacity"])

        break
