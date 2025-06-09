from flask import Blueprint, render_template, jsonify, session, redirect, url_for, request
from helpers import load_json, save_json
import time

marketplace_bp = Blueprint('marketplace', __name__)

MARKETPLACE_FILE = 'marketplace.json'
ANIMATIONS_FILE = 'animations.json'

def load_marketplace():
    try:
        data = load_json(MARKETPLACE_FILE)
        # Optional validation can be added here
        return data
    except Exception as e:
        print("Marketplace load failed:", e)
        return []

@marketplace_bp.route('/marketplace')
def marketplace():
    raw_data = load_marketplace()
    animations = {}
    for item in raw_data:
        if 'type' in item:
            animations[item['type']] = {
                "id": item.get("id"),
                "name": item.get("title", "Untitled"),
                "type": item['type'],
                "description": item.get("description", ""),
                "price": item.get("price", 0),
                "previewImage": item.get("previewImage", "/static/previews/default.png")
            }

    merchant_api_key = "your-api-key-here"

    return render_template('marketplace.html', animations=animations, merchant_api_key=merchant_api_key)


@marketplace_bp.route('/buy_animation/<int:animation_id>', methods=['POST'])
def buy_animation(animation_id):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['user']
    marketplace = load_marketplace()
    animation = next((a for a in marketplace if a['id'] == animation_id), None)
    if not animation:
        return jsonify({"error": "Animation not found"}), 404

    animations = load_json(ANIMATIONS_FILE)
    user_animations = animations.get(username, [])

    if any(a.get('original_id') == animation_id for a in user_animations):
        return jsonify({
            "success": True,
            "already_owned": True,
            "message": f"You already own '{animation['title']}'."
        })

    # Here, implement real payment processing or simulate success
    # For now assume free or paid animation but payment succeeded

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
    save_json(ANIMATIONS_FILE, animations)

    return jsonify({
        "success": True,
        "already_owned": False,
        "message": f"You bought '{animation['title']}'!"
    })


@marketplace_bp.route('/fake_payment/<int:animation_id>', methods=['GET', 'POST'])
def fake_payment(animation_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    marketplace = load_marketplace()
    animation = next((a for a in marketplace if a['id'] == animation_id), None)
    if not animation:
        return "Animation not found", 404

    if request.method == 'POST':
        import time, random
        time.sleep(2)

        if random.random() < 0.9:
            return redirect(url_for('marketplace.confirm_purchase', animation_id=animation_id))
        else:
            return render_template('fake_payment.html', animation=animation, error="Payment failed. Please try again.")

    return render_template('fake_payment.html', animation=animation)


@marketplace_bp.route('/confirm_purchase/<int:animation_id>')
def confirm_purchase(animation_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    username = session['user']
    marketplace = load_marketplace()
    animation = next((a for a in marketplace if a['id'] == animation_id), None)
    if not animation:
        return "Animation not found", 404

    animations = load_json(ANIMATIONS_FILE)
    user_animations = animations.get(username, [])

    if any(a.get('original_id') == animation_id for a in user_animations):
        return f"You already own '{animation['title']}'."

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
    save_json(ANIMATIONS_FILE, animations)

    return f"Payment successful! You now own '{animation['title']}'. <a href='/marketplace'>Back to Marketplace</a>"
