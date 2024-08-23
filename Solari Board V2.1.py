import time
import json
import os
import requests
from datetime import datetime

Choose_A_Station = 'R20'  # <<<< Input your station code here (UPPERCASE Letters) <<<<<<
print("Running...")


def get_stop_times(station):
    # Fetch stop times data
    stop_times_url = f"https://demo.transiter.dev/systems/us-ny-subway/stops/{station}"
    stop_times_response = requests.get(stop_times_url)
    stop_times_data = stop_times_response.json()

    result = []
    for stop_time in stop_times_data['stopTimes']:
        if "departure" in stop_time and "time" in stop_time["departure"]:
            route_id = stop_time['trip']['route']['id']
            last_stop_name = stop_time['trip']['destination']['name']
            stop_id = stop_times_data['name']
            api_time = datetime.fromtimestamp(int(stop_time["departure"]["time"])).strftime('%H:%M:%S')
            seconds_to_leave = int(stop_time["departure"]["time"]) - time.time()
            arrival_time = int(seconds_to_leave // 60)

            # Only include if arrival_time is >= 0
            if arrival_time > 0:
                result.append({
                    "route_id": route_id,
                    "arrival_time": arrival_time,
                    "current_stop": stop_id,
                    "last_stop_name": last_stop_name,
                })
            elif arrival_time == 0:
                result.append({
                    "route_id": route_id,
                    "arrival_time": "0",
                    "current_stop": stop_id,
                    "last_stop_name": last_stop_name,
                })

    return result


def get_transfer_stations(station):
    # Fetch transfer data
    transfers_url = "https://demo.transiter.dev/systems/us-ny-subway/transfers"
    transfers_response = requests.get(transfers_url)
    transfers_data = transfers_response.json()

    transfer_stations = []
    for transfer in transfers_data["transfers"]:
        if transfer["fromStop"]["id"] == station:
            transfer_stations.append(transfer["toStop"]["id"])

    return transfer_stations

def contains_delay(value):
    return "MAINTENANCE" in value.upper()

def get_service_status():
    # Fetch route data
    routes_url = 'https://demo.transiter.dev/systems/us-ny-subway/routes'
    routes_response = requests.get(routes_url)
    routes_data = routes_response.json()

    results = {}
    for route in routes_data.get("routes", []):
        route_id = route.get("id")
        results[route_id] = {"status": ""}

        alerts = route.get("alerts", [])
        if not alerts:
            results[route_id]["status"] = "Good Service"
        else:
            delay_found = False
            for alert in alerts:
                cause = alert.get("cause", "")
                effect = alert.get("effect", "")
                if contains_delay(cause) or contains_delay(effect):
                    results[route_id]["status"] = "SERVICE CHANGE"
                    delay_found = True
                    break
            if not delay_found:
                results[route_id]["status"] = "DELAYS"

    return results

def main():
    station = Choose_A_Station

    # Get stop times for the original station
    result = get_stop_times(station)

    # Get transfer stations
    transfer_stations = get_transfer_stations(station)

    # Get stop times for transfer stations
    for transfer_station in transfer_stations:
        transfer_results = get_stop_times(transfer_station)
        result.extend(transfer_results)

    # Get service status
    service_status = get_service_status()

    # Combine result and service status
    combined_results = []
    for stop in result:
        route_id = stop["route_id"]
        combined_results.append({
            "route_id": route_id,
            "arrival_time": stop["arrival_time"],
            "current_stop": stop["current_stop"],
            "last_stop_name": stop["last_stop_name"],
            "service_status": service_status.get(route_id, {}).get("status", "Unknown")
        })

    # Sort combined_results by arrival_time in ascending order, handling both int and str types
    combined_results = sorted(combined_results, key=lambda x: x["arrival_time"] if isinstance(x["arrival_time"], int) else float('inf'))

    # Output the combined results
    with open('output.json', 'w') as file:
        json.dump(combined_results, file, indent=4)

    time.sleep(20)

if __name__ == "__main__":
    while True:
        main()
