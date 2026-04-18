# Riot API Backend 🎮

This is an early-stage Python backend designed to interact with the **Riot Games API**. It serves as a foundation for a future web application that will provide detailed statistics and insights for League of Legends players.

## 🚀 Current Features

The script currently performs a complete data retrieval flow through the terminal:
1.  **Account Lookup:** Resolves a Riot ID (Name#Tag) to a unique `PUUID` using the Account-v1 endpoint.
2.  **Match History:** Retrieves the IDs of the 20 most recent matches for a specific player.
3.  **Detailed Stats:** Iterates through match data to extract specific performance metrics, including:
    * **Champion & Role:** Identity and position in the match.
    * **KDA:** Kill, Death, and Assist count.
    * **Economy & Farming:** Gold earned and total minions killed (CS).

## 🛠️ Technology Stack

* **Language:** Python 3.13
* **Libraries:** * `requests`: For handling HTTP communication with Riot's servers.
    * `python-dotenv`: For managing sensitive API credentials.

## 📋 Setup & Installation

### 1. Prerequisites
- A **Riot API Key** from the [Riot Developer Portal](https://developer.riotgames.com/).
- Python installed on your machine.

### 2. Configuration
Create a `.env` file in the root directory of the project to store your credentials:
```env
RIOT_API_KEY=your_api_key_here
```

### 3. Instalation
```pip install requests python-dotenv```

### 4. Running the project
```python main.py```

🗺️ Roadmap & Upcoming Changes
The project is currently in a "Proof of Concept" phase. Planned improvements include:

[X] Asynchronous Refactoring (Priority): Replacing requests with aiohttp and asyncio to allow concurrent API calls, significantly speeding up the retrieval of multiple match details.

[ ] Robust Error Handling: Implementing logic to handle Rate Limits (429), expired keys, and "Summoner Not Found" errors.

[ ] Data Persistence: Adding a database layer (such as PostgreSQL or MongoDB) to cache results and minimize API usage.

[ ] Web Framework Integration: Transitioning the logic into a REST API using FastAPI or Flask.

Note: This project is a work in progress and currently uses synchronous requests, which may result in slower execution times when fetching large volumes of match data.