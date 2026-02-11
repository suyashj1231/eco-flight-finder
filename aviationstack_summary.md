# AviationStack API Documentation Summary

## Core Endpoints

### 1. Real-Time Flights (`/v1/flights`)
-   **Access**: Available on **All Plans** (Free Tier included).
-   **Purpose**: Returns real-time flight status (active, scheduled, landed, etc.).
-   **Key Parameters**:
    -   `access_key`: Your API key.
    -   `dep_iata` / `arr_iata`: Filter by origin/destination (e.g., 'SFO', 'JFK').
    -   `flight_status`: 'active', 'scheduled', 'landed'.
    -   `limit`: Number of results (default 100).
-   **Limitations**:
    -   **Historical Data**: Technically supported via `flight_date` param, but restricted on Free Plan (often returns no data for past dates).
    -   **Future Data**: Free plan usually only looks at "current/recent" window.

### 2. Future Schedules (`/v1/flightsFuture`)
-   **Access**: **Basic Plan ($29/mo) and higher ONLY**.
-   **Purpose**: Flight schedules for dates >7 days in the future.
-   **Relevance**: We **cannot** use this on the current Free Plan. We must stick to `/v1/flights` for near-term searches.

### 3. Airports (`/v1/airports`)
-   **Access**: **All Plans**.
-   **Purpose**: Database of airport details.
-   **Key Fields**: `iata_code`, `airport_name`, **`latitude`**, **`longitude`**, `country_name`.
-   **Strategic Value**: The `/v1/flights` endpoint **does not return flight distance**. To calculate accurate emissions, we need to:
    1.  Call `/v1/airports` to get coordinates for Departure/Arrival airports.
    2.  Calculate the "Great Circle Distance" between them.
    3.  Use this distance in the emissions formula.

### 4. Airlines & Aircraft (`/v1/airlines`, `/v1/airplanes`)
-   **Access**: All Plans.
-   **Purpose**: specific details like fleet size, aircraft engine type, etc.
-   **Relevance**: Useful for advanced filtering, but `/v1/flights` provides the necessary `aircraft.iata` code (e.g. "A320") for our fuel lookups.

## Recommendations for Eco Flight Finder
1.  **Distance Calculation**: Implement a lookup using `/v1/airports` or a local airport database (csv/json) to get Lat/Long. This fixes the "0 kg CO2" issue.
2.  **Date Filtering**: On the Free Plan, users should search for **current (today's) flights** or **active** flights. Historical/Future queries will reliably fail.
