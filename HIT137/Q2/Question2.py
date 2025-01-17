
import os
import pandas as pd

# Define seasons
seasons = {
    "Summer": ["December", "January", "February"],
    "Autumn": ["March", "April", "May"],
    "Winter": ["June", "July", "August"],
    "Spring": ["September", "October", "November"]
}

# Input and output folders
input_folder = "temperature_data"
output_folder = "outputs"
os.makedirs(output_folder, exist_ok=True)

# Initialize data
season_totals = {season: [] for season in seasons}  # For seasonal averages
station_temperatures = {}  # For tracking all temperatures for each station
station_ranges = {}  # For largest temperature range

# Check if input folder exists
if not os.path.exists(input_folder):
    print(f"Error: Input folder '{input_folder}' does not exist.")
    exit()

# Process each file in the input folder
csv_files = [file for file in os.listdir(input_folder) if file.endswith(".csv")]
if not csv_files:
    print("Error: No CSV files found in the input folder.")
    exit()

print(f"Found {len(csv_files)} CSV files in the folder.")

for file in csv_files:
    print(f"Processing file: {file}")  # Print the file name
    file_path = os.path.join(input_folder, file)
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading file '{file}': {e}")
        continue  # Skip this file and proceed to the next

    # Check if required columns exist
    required_columns = ["STATION_NAME"] + list(seasons.keys())
    if not all(col in data.columns for col in required_columns):
        print(f"Error: File '{file}' is missing required columns.")
        continue

    # Iterate through each row (station)
    for _, row in data.iterrows():
        station_name = row["STATION_NAME"]

        # Extract temperatures and handle missing data
        try:
            temperatures = pd.to_numeric(row[4:], errors="coerce")
        except Exception as e:
            print(f"Error processing temperatures for station '{station_name}' in file '{file}': {e}")
            continue

        # Update station data for warmest, coolest, and range calculations
        if station_name not in station_temperatures:
            station_temperatures[station_name] = []
            station_ranges[station_name] = {"min": float("inf"), "max": float("-inf")}
        
        station_temperatures[station_name].extend(temperatures.dropna())
        station_ranges[station_name]["min"] = min(station_ranges[station_name]["min"], temperatures.min())
        station_ranges[station_name]["max"] = max(station_ranges[station_name]["max"], temperatures.max())

        # Calculate seasonal averages
        for season, months in seasons.items():
            # Get valid column indices for the months, and ensure indices are within bounds
            try:
                month_indices = [data.columns.get_loc(month) for month in months if month in data.columns]
                valid_month_indices = [index for index in month_indices if index < len(temperatures)]

                if valid_month_indices:  # Ensure that valid month indices are available
                    seasonal_values = temperatures[valid_month_indices].dropna()

                    if not seasonal_values.empty:
                        season_totals[season].extend(seasonal_values)
            except Exception as e:
                print(f"Error calculating seasonal averages for station '{station_name}' in file '{file}': {e}")
                continue

# Task 1: Calculate average temperatures for each season across all years
try:
    season_averages = {season: round(sum(values) / len(values), 2) if values else None for season, values in season_totals.items()}
    with open(os.path.join(output_folder, "average_temp.txt"), "w") as f:
        f.write("Average Seasonal Temperatures:\n")
        for season, avg in season_averages.items():
            f.write(f"{season}: {avg}\n")
except Exception as e:
    print(f"Error writing seasonal averages to file: {e}")

# Task 2: Find the station(s) with the largest temperature range
try:
    largest_range = max((values["max"] - values["min"]) for values in station_ranges.values())
    largest_range_stations = [station for station, values in station_ranges.items() if (values["max"] - values["min"]) == largest_range]
    with open(os.path.join(output_folder, "largest_temp_range_station.txt"), "w") as f:
        f.write("Station(s) with the Largest Temperature Range:\n")
        f.write("\n".join(largest_range_stations))
except Exception as e:
    print(f"Error identifying stations with largest temperature range: {e}")

# Task 3: Find the warmest and coolest station(s)
try:
    station_avg_temps = {station: round(sum(temps) / len(temps), 2) if temps else None for station, temps in station_temperatures.items()}
    warmest_temp = max(station_avg_temps.values())
    coolest_temp = min(station_avg_temps.values())
    warmest_stations = [station for station, avg_temp in station_avg_temps.items() if avg_temp == warmest_temp]
    coolest_stations = [station for station, avg_temp in station_avg_temps.items() if avg_temp == coolest_temp]
    with open(os.path.join(output_folder, "warmest_and_coolest_station.txt"), "w") as f:
        f.write("Warmest Station(s):\n")
        f.write("\n".join(warmest_stations) + "\n")
        f.write("Coolest Station(s):\n")
        f.write("\n".join(coolest_stations))
except Exception as e:
    print(f"Error identifying warmest and coolest stations: {e}")

# Indicate completion
print("Processing complete. Results saved to output folder.")