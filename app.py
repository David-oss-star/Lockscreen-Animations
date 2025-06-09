from flask import Flask, render_template, request, redirect, session, flash, jsonify, request, url_for
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USER_FILE = 'users.json'
ANIMATIONS_FILE = 'animations.json'
MARKETPLACE_FILE = 'marketplace.json'

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        if any(u['username'] == username for u in users):
            flash("Username already taken.")
            return redirect('/register')

        hashed_password = generate_password_hash(password)
        users.append({'username': username, 'password': hashed_password})
        save_users(users)

        # ✅ Automatically log the user in
        session['user'] = username
        flash("Registered and logged in!")
        return redirect('/create')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        user = next((u for u in users if u['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect('/create')
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/create')
def create():
    if 'user' not in session:
        return redirect('/login')
    return render_template('create.html')

def load_animations():
    if not os.path.exists(ANIMATIONS_FILE):
        return {}
    with open(ANIMATIONS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_animations(data):
    with open(ANIMATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/save_animation', methods=['POST'])
def save_animation():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['user']
    animation_data = request.get_json()

    if not animation_data:
        return jsonify({'error': 'No animation data provided'}), 400

    # Load existing animations from JSON
    animations = load_animations()

    # Get or initialize user animations
    user_animations = animations.get(username, [])

    # Use a unique ID (timestamp-based for simplicity)
    animation_entry = {
        'id': int(time.time() * 1000),
        'data': animation_data
    }

    # Append new animation
    user_animations.append(animation_entry)
    animations[username] = user_animations

    # Save updated data
    save_animations(animations)

    return jsonify({
        'message': 'Animation saved successfully',
        'animation_id': animation_entry['id']
    }), 200

@app.route('/delete_animation', methods=['POST'])
def delete_animation():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    animation_id = int(request.form.get("id"))

    animations = load_animations()
    if user in animations:
        animations[user] = [a for a in animations[user] if a['id'] != animation_id]
        save_animations(animations)

    return redirect(url_for('my_animations'))

@app.route('/my_animations')
def my_animations():
    user = session.get("user")
    if not user:
        return redirect(url_for('login'))

    animations = []
    filepath = 'animations.json'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            all_data = json.load(f)
            animations = all_data.get(user, [])

    return render_template('my_animations.html', user=user, animations=animations)

#Marketplace Routes
def load_marketplace():
    try:
        with open(MARKETPLACE_FILE) as f:
            data = json.load(f)
        for item in data:
            assert "name" in item and item["name"] is not None
            assert "type" in item and item["type"] is not None
            assert "description" in item
            assert "price" in item
        return data
    except Exception as e:
        print("💥 Marketplace load failed:", e)
        return []

def load_marketplace():
    try:
        with open(MARKETPLACE_FILE) as f:
            data = json.load(f)
        print("✅ Raw marketplace data:", data)  # <-- Add this line

        for item in data:
            assert "type" in item and item["type"] is not None
            assert "description" in item
            assert "price" in item
        return data
    except Exception as e:
        print("💥 Marketplace load failed:", e)
        return []


def save_animations(data):
    with open(ANIMATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/marketplace')
def marketplace():
    raw_data = load_marketplace()
    animations = {}
    for item in raw_data:
        if "type" in item:
            animations[item["type"]] = {
                "id": item.get("id"),
                "name": item.get("title", "Untitled"),  # fixed from "name" to "title"
                "type": item["type"],
                "description": item.get("description", ""),
                "price": item.get("price", 0),
                "previewImage": item.get("previewImage", "/static/previews/default.png")
            }

    print("🎨 Animations:", animations)
    return render_template("marketplace.html", animations=animations)

@app.route('/buy_animation/<int:animation_id>', methods=['POST'])
def buy_animation(animation_id):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['user']

    # Load marketplace data
    marketplace = load_marketplace()

    # Find the animation by id (numeric)
    animation = next((a for a in marketplace if a['id'] == animation_id), None)
    if not animation:
        return jsonify({"error": "Animation not found"}), 404

    # Load user animations
    animations = load_animations()
    user_animations = animations.get(username, [])

    # Check if user already owns this animation by matching marketplace id stored in 'original_id'
    already_owned = any(a.get('original_id') == animation_id for a in user_animations)
    if already_owned:
        return jsonify({"success": True, "message": f"You already own '{animation['title']}'."})

    # Here you would integrate payment process if price > 0
    # For now, assume payment success or free animation
    if animation['price'] > 0:
        # TODO: Payment integration here
        # If payment fails, return error JSON
        pass

    # Add the purchased animation to user's saved animations
    new_entry = {
        "id": int(time.time() * 1000),  # unique local id
        "original_id": animation_id,     # keep marketplace id reference
        "data": {
            "type": animation['type'],
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **animation.get('animationData', {})
        }
    }
    user_animations.append(new_entry)
    animations[username] = user_animations
    save_animations(animations)
    return jsonify({
        "success": True,
        "already_owned": False,
        "message": f"You bought '{animation['title']}'!"
    })


# Payment Gateway
@app.route('/fake_payment/<int:animation_id>', methods=['GET', 'POST'])
def fake_payment(animation_id):
    if 'user' not in session:
        return redirect(url_for('login'))  # Or your auth logic
    
    marketplace = load_marketplace()
    animation = next((a for a in marketplace if a['id'] == animation_id), None)
    if not animation:
        return "Animation not found", 404

    if request.method == 'POST':
        # Simulate payment processing delay
        import time
        time.sleep(2)  # 2 seconds delay

        # Simulate random success/failure
        import random
        if random.random() < 0.9:  # 90% success rate
            # Redirect to confirm purchase route on success
            return redirect(url_for('confirm_purchase', animation_id=animation_id))
        else:
            return render_template('fake_payment.html', animation=animation, error="Payment failed. Please try again.")

    return render_template('fake_payment.html', animation=animation)

@app.route('/confirm_purchase/<int:animation_id>')
def confirm_purchase(animation_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    marketplace = load_marketplace()
    animation = next((a for a in marketplace if a['id'] == animation_id), None)
    if not animation:
        return "Animation not found", 404

    # Load user animations
    animations = load_animations()
    user_animations = animations.get(username, [])

    # Check if user already owns this animation
    if any(a.get('original_id') == animation_id for a in user_animations):
        return f"You already own '{animation['title']}'."

    # Add purchased animation to user's library
    new_entry = {
        "id": int(time.time() * 1000),
        "original_id": animation_id,
        "data": {
            "type": animation['type'],
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **animation.get('animationData', {})
        }
    }
    user_animations.append(new_entry)
    animations[username] = user_animations
    save_animations(animations)

    return f"Payment successful! You now own '{animation['title']}'. <a href='/marketplace'>Back to Marketplace</a>"


if __name__ == '__main__':
    app.run(debug=True, port=5001)
