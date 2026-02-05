# DestinAI

DestinAI is an AI-powered travel companion that helps users discover their next destination and plan the perfect trip. It combines machine learning for personalized recommendations with generative AI for detailed itinerary creation.

## Project History

This project started as a 6-man team project for our engineering lesson. What began as a simple assignment ended up becoming something much more significant and evolved into the application you see here.

## Technical Architecture

DestinAI operates as a full-stack application with a Python Flask backend and a vanilla HTML/JavaScript frontend. It can be deployed to any local network.

### Backend (`/backend`)
The backend is built with **Flask** and integrates several key technologies:
-   **Machine Learning**: Uses a custom K-Nearest Neighbors (KNN) model (`scikit-learn`, `joblib`) to recommend cities based on user preferences (Budget, Culture, Adventure, etc.) using a pre-processed dataset (`destinai_final_dataset.csv`).
-   **Generative AI**: Integrates with the **OpenAI API** to generate detailed, day-by-day personalized travel itineraries based on the user's selected city and preferences.
-   **External APIs**: Utilizes services like **TripAdvisor** (via `services/tripadvisor.py`) to fetch hotel and location data.
-   **CSV Persistence**: Stores user reviews locally in `reviews.csv`.

### Frontend (`/frontend`)
The frontend is a lightweight, responsive web interface built with standard HTML, CSS, and JavaScript. It communicates with the backend via RESTful API endpoints.

## AI Disclosure

Generative AI tools were used when needed by me and my team members during the development of this project, specifically for content generation and coding assistance.

## Setup & specific instructions

### Prerequisites
- Python 3.8+
- OpenAI API Key
- TripAdvisor API Key (optional/mocked if missing)

### Installation

1.  **Backend Setup**:
    Navigate to the `backend` directory and install dependencies:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Environment Configuration**:
    Create a `.env` file in the `backend/` directory. **This file is required** and must contain your secrets (not included in repo):
    ```env
    OPENAI_API_KEY=your_openai_key_here
    T_API_KEY=your_tripadvisor_key_here
    HOST=0.0.0.0
    ```

3.  **Run the Application**:
    ```bash
    python app.py
    ```
    The backend will start on `http://localhost:5000` (or your network IP).

4.  **Frontend**:
    Open `frontend/MainPage.html` in your browser.
