from flask import Flask, redirect, request, session, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace with your own secret key

# Your LinkedIn app credentials
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'YOUR_REDIRECT_URI'

@app.route('/')
def home():
    return redirect(url_for('signup'))

@app.route('/signup')
def signup():
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect(f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=r_liteprofile%20r_emailaddress")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code received", 400

    access_token = exchange_code_for_access_token(code)
    if access_token:
        user_profile = fetch_user_profile(access_token)
        user_email = fetch_user_email(access_token)
        # Handle user account creation or linking here
        return f"User Profile: {user_profile}, Email: {user_email}"
    else:
        return "Error: Unable to get access token", 400

def exchange_code_for_access_token(auth_code):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(url, data=payload)
    return response.json().get('access_token')

def fetch_user_profile(access_token):
    url = "https://api.linkedin.com/v2/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_user_email(access_token):
    url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == '__main__':
    app.run(debug=True)
