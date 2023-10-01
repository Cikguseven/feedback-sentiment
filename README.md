# SensiFeed

SensiFeed is a web-based platform built to capture feedback on change management initiatives and use AI-powered sentiment analysis to understand the sentiment behind the feedback. It's built with Flask and SQLite for the backend, and HTML and CSS for the frontend.

## Features

- **Feedback Collection**: Users can easily submit feedback through a form on the main page.
- **Sentiment Analysis**: Leveraging AI, the system analyzes and categorizes feedback sentiment as positive, neutral, or negative.
- **Feedback Display**: All feedback, along with its derived sentiment, is displayed below the submission box in a simple list format.

## Setup and Running the Project

### Prerequisites

Ensure you have the following installed:

- Python 3.7+
- Flask
- Flask_SQLAlchemy

### Installation

1. **Clone the Repository**:

   ```bash
   git clone [YOUR REPOSITORY LINK HERE]
   cd [YOUR DIRECTORY NAME]
   ```

2. **Set Up a Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**:

   Run the application once to initialize the SQLite database.

   ```bash
   python app.py
   ```

### Running the Application

Once set up, you can run the application using:

```bash
python app.py
```

This will start the Flask server, and the application should be accessible at `http://127.0.0.1:5000/`.

## License

[MIT](https://choosealicense.com/licenses/mit/)
