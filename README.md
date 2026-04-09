# Court-Data Fetcher & Mini-Dashboard

## Objective
This project is a small web application that fetches case metadata and the latest hearing details for specific cases from the Delhi High Court. It is built to demonstrate programmatic web scraping, data parsing, and dashboard-style display in a full-stack application.

## Features
- **User Interface:** A simple web form to input case details (Case Type, Case Number, Filing Year).
- **Automated Scraping:** Programmatically navigates the Delhi High Court's public portal to find case information.
- **Data Parsing:** Extracts key details such as parties' names, hearing dates, and order/judgment links.
- **Database Logging:** Logs every query and the raw response to an SQLite database for record-keeping.
- **User-Friendly Display:** Renders the fetched data on a simple, dark-themed dashboard-style interface.
- **Downloadable Orders:** Allows downloading of linked PDFs directly from the UI.
- **Robust Error Handling:** Provides user-friendly messages for invalid inputs or site issues.

## Court Chosen
- **Delhi High Court:** `https://delhihighcourt.nic.in/`
- **Specific Search URL:** `https://delhihighcourt.nic.in/app/get-case-type-status`

## Prerequisites
- **Python 3.8+**
- `pip` (Python package installer)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/court_data_app.git](https://github.com/your-username/court_data_app.git)
    cd court_data_app
    ```

2.  **Create and activate a Python virtual environment:**
    - **On Windows:**
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - **On macOS/Linux:**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Install the project dependencies:**
    This will install Flask, Playwright, Flask-SQLAlchemy, and other necessary libraries.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browser binaries:**
    ```bash
    playwright install
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```

The application will start running on `http://127.0.0.1:5000`.

## Screenshots

<p align="center">
  <img src="./assets/screenshot1.png" width="700"/>
</p>

<p align="center">
  <img src="./assets/screenshot2.png" width="700"/>
</p>

## Usage

1.  Open your web browser and navigate to `http://127.0.0.1:5000`.
2.  Fill out the form with a **valid Case Type, Case Number, and Filing Year** from the Delhi High Court.
3.  Click "Fetch Case Details".
4.  A Playwright browser window will appear, the form will be filled automatically, and the fetched case data will be displayed on your dashboard.

## CAPTCHA Strategy

The Delhi High Court's case status portal uses a simple text-based CAPTCHA. Our scraper handles this by:
1.  Locating the `<span>` element that contains the CAPTCHA code.
2.  Directly reading the text content from this element.
3.  Filling the corresponding input field with the read value.

This approach eliminates the need for manual intervention or a third-party CAPTCHA-solving service, making the scraping process fully automated and reliable for this specific implementation.

## Database
The application uses SQLite as its database. Each query made by the user is logged to a `query_log` table, which stores the query details, the raw HTML response from the court site, and the outcome (success/error). The database file (`court_data.db`) is automatically created inside the `instance/` folder upon the first run.

## License
This project is licensed under the **MIT License**.