# Location-based-NitrousOxide-Level
Location based NitrousOxide Level



Location-based Nitrous Oxide Level App
This Python application fetches and displays the nitrous oxide (NO₂) levels based on a user-specified location. The application uses PyQt5 for the GUI and integrates with APIs for geocoding and nitrous oxide data retrieval.

Features

User Input for Location: Users can enter any location, and the app will fetch the corresponding nitrous oxide levels.

Real-time Data: The app retrieves real-time NO₂ levels for the specified location.

Structured Output: The NO₂ concentration, measurement time, and source are displayed in a clear and structured format.

Easy to Use: Simple GUI interface built with PyQt5.


Prerequisites

Before you begin, ensure you have met the following requirements:

Python 3.x installed on your machine.

An active internet connection (to fetch data from the APIs).

API keys for the following services:

RapidAPI Map Geocoding API

RapidAPI Nitrous Oxide Levels API

Installation

Clone the repository:


git clone https://github.com/Sherin-SEF-AI/Location-based-NitrousOxide-Level.git

cd Location-based-NitrousOxide-Level

Install dependencies:

Install the required Python packages using pip:




pip install PyQt5

Configure API keys:

Replace the placeholder API keys in the code with your own API keys from RapidAPI.

Usage

Run the application:


python nitrousoxidelevel.py

Enter a location:


Type in the location you want to query (e.g., "Kochi").

Click "Fetch Data" to retrieve the nitrous oxide levels for that location.

View results:


The NO₂ levels, measurement time, and source will be displayed in the application window.
