# Stop the Bus (Państwa-Miasta) - Multiplayer Game

## Overview

**Stop the Bus** (known as **"Państwa-Miasta"** in Polish) is a classic word game where players compete to come up with unique answers for various categories starting with a given letter. This project implements a **multiplayer version** of the game using a **client-server architecture**, featuring **lobbies**, **real-time gameplay**, and **scoring**.

---

## Features

### Game Features

- **Menu System**: Create or join game lobbies  
- **Lobby Management**:  
  - Create new lobbies (up to 4 players)  
  - Join existing lobbies  
  - Ready/Unready system  
  - Lobby refresh  
- **Gameplay**:  
  - Real-time answer submission  
  - Countdown timer  
  - Category validation  
  - Dynamic scoring  
- **Results Display**:  
  - Round-by-round results  
  - Final leaderboard  
- **User Interface**:  
  - Pygame-based graphical interface  
  - Interactive buttons  
  - Visual feedback  

### Server Features

- **Lobby Server**:  
  - Manages game lobbies  
  - Handles player connections  
  - Tracks ready status  
- **Game Server**:  
  - Validates answers against category dictionaries  
  - Calculates scores  
  - Manages game rounds  
  - Enforces game rules  

---

## Installation

### Prerequisites

- **Python 3.x**  
- **pygame** library  
- **pandas** library  

### Setup

1. Clone the repository  
2. Install dependencies:  
pip install pygame pandas

3. Run the servers (in separate terminals):  
python server_lobby.py  
python server_game.py

5. Run the client:  
python client.py

---

## How to Play

### Main Menu

- Choose to create a new lobby or join an existing one  
- Enter your nickname  

### Lobby

- Wait for other players to join  
- Click **Ready** when prepared  
- Game starts automatically when all players are ready  

### Gameplay

- Each round starts with a random letter  
- Fill in answers for each category starting with that letter  
- Submit your answers before time runs out  
- Unique answers score more points  

### Results

- View round results after each submission  
- See final leaderboard after 3 rounds  

---

## Game Rules

- **Categories**: Country, City, Animal, Thing, Occupation, Movie  
- **Rounds**: 3 per game  
- **Scoring**:  
- **15 points**: Only correct answer in category  
- **10 points**: Correct and unique answer (but others answered too)  
- **5 points**: Duplicate correct answer  
- **0 points**: Incorrect or empty answer  
- **Time limit**: 10 seconds after the first player submits  

---

## Project Structure
game.py # Main game client with UI  
server_lobby.py # Lobby management server  
server_game.py # Game logic server  
dictionaries/ # Category validation files  
images/ # Game assets  

---

## Technical Details

- **Networking**: TCP socket communication  
- **Threading**: Multi-threaded servers handle multiple clients  
- **Data Validation**: Answers checked against category-specific dictionaries  
- **State Management**: Thread-safe operations with locking  

---

## Contributions

### Mikołaj Woźniak

### Szymon Róźycki

### Michal Sondej
- improved the visual presentation of the game
- added rules screen
- added exit game functionality
- added leave lobby functionality


---

## Credits

Developed as a **Python networking project**.  
Inspired by the classic game **"Państwa-Miasta"**.


