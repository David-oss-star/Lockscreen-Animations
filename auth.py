import json
import os
from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import load_json, save_json

auth = Blueprint('auth', __name__)

USER_FILE = 'users.json'


@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Initialize users dict if file missing or invalid
        if not os.path.exists(USER_FILE):
            with open(USER_FILE, 'w') as f:
                json.dump({}, f)

        users = load_json(USER_FILE)
        if username in users:
            return jsonify({'error': 'User already exists'}), 400

        hashed_password = generate_password_hash(password)

        users[username] = {
            'password': hashed_password,
            'purchased_animations': []
        }

        save_json(USER_FILE, users)

        return jsonify({'message': 'Registered successfully'}), 200

    except Exception as e:
        print(f"Registration Error: {e}")
        return jsonify({'error': 'Server error'}), 500


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and password are required.")
            return render_template('login.html')

        users = load_json(USER_FILE)
        user = users.get(username)

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('animations.create'))
        else:
            flash("Invalid credentials.")

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
