# Eco Flight Finder

Eco Flight Finder is a web application designed to help travelers make more environmentally conscious decisions when booking flights. By integrating real-time flight data with carbon emission estimates, the platform empowers users to prioritize sustainability alongside traditional factors like flight duration and schedule.

## Project Overview

The core philosophy of this project is to make environmental impact a visible and actionable part of the travel planning process. Most flight search engines focus primarily on price and convenience. Eco Flight Finder shifts this focus by ranking flights based on an eco-score, which combines carbon emission data with flight duration to surface the most efficient travel options.

## Key Features

### Environmental Ranking System
Flights are not just listed; they are ranked. Our proprietary recommendation engine evaluates each flight segment based on estimated CO2 emissions. Options with significantly lower carbon footprints are highlighted with green indicators, while those exceeding standard emission thresholds are flagged for visibility.

### Split Round Trip Management
To simplify the booking of complex itineraries, round trip searches are presented as distinct segments. You can browse and select your outbound and return flights independently, each with its own dedicated pagination and environmental breakdown.

### Direct Booking Integration
Once you have identified a flight that fits your schedule and environmental goals, you can proceed directly to book it. Each result includes a direct link to Kayak, pre-configured with your specific route and date information, ensuring a seamless transition from search to booking.

### User Experience and Personalization
- Intelligent Search: Autocomplete functionality for airports makes starting a search quick and accurate.
- Search History: Your previous searches are saved securely, allowing you to quickly re-run them or clear your history at any time.
- Profile Customization: Adjust your preferences, such as the number of results per page, to tailor the interface to your needs.
- Global Synchronization: All times and dates across the application are synchronized to Pacific Standard Time, providing consistency regardless of your physical location.

## Technical Architecture

The application is built using a modern, decoupled architecture to ensure performance and maintainability.

### Backend
- Framework: FastAPI (Python)
- Database: SQLAlchemy for persistent user and history management.
- External APIs: 
  - AviationStack for real-time flight schedules and airline details.
  - Google Flight Emissions API for accurate, segment-specific carbon data.

### Frontend
- Framework: React with Vite.
- Styling: Custom Vanilla CSS focusing on a premium, glassmorphism-inspired aesthetic that feels high-tech yet organic.
- State Management: React Hooks for dynamic search results and user session handling.

## Installation and Setup

To run this project locally, you will need to set up both the backend and frontend environments.

### Prerequisites
- Python 3.8+
- Node.js and npm

### Configuration
Create a .env file in the root directory and provide your AviationStack API key:
```
API_KEY=your_aviationstack_key_here
```

### Backend Setup
1. Navigate to the backend directory.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the FastAPI server: `uvicorn api:app --reload`.

### Frontend Setup
1. Navigate to the front-end directory.
2. Install dependencies: `npm install`.
3. Start the development server: `npm run dev`.

The application will typically be available at http://localhost:5173.

## Data Transparency

The emission data displayed is derived from industry-average models and specific aircraft information where available. While we strive for the highest accuracy, please note that external API availability (especially on free tiers) may occasionally impact the specificity of real-time results for future dates.