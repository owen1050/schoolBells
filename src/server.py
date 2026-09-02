from flask import Flask, request, jsonify, render_template, session
import databaseQuerys as db

app = Flask(__name__, static_folder='static')
app.secret_key = 'super_secret_key_change_in_production'

# Initialize database on startup
db.init_db()


# ---------------------------------------------------------
# FRONTEND ROUTES
# ---------------------------------------------------------

@app.route('/')
def home():
    return app.send_static_file('index.html')


@app.route('/admin')
def admin():
    return app.send_static_file('admin.html')


# ---------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------

@app.route('/api/schools', methods=['GET'])
def get_schools():
    return jsonify(db.get_all_schools())


@app.route('/api/schedule/today/<int:school_id>', methods=['GET'])
def get_today(school_id):
    schedule = db.get_todays_schedule(school_id)

    if schedule:
        return jsonify(schedule)

    return jsonify({"error": "No schedule found"}), 404


# ---------------------------------------------------------
# ADMIN LOGIN
# ---------------------------------------------------------

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json

    school_id = data.get('school_id')
    password = data.get('password')

    if db.verify_admin(school_id, password):
        session['admin_school_id'] = school_id

        return jsonify({"success": True})

    return jsonify({
        "success": False,
        "message": "Invalid password"
    }), 401


# ---------------------------------------------------------
# ADMIN SCHEDULES
# ---------------------------------------------------------

@app.route('/api/admin/schedules', methods=['GET', 'POST'])
def manage_schedules():

    school_id = session.get('admin_school_id')

    if not school_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        return jsonify(db.get_school_schedules(school_id))

    if request.method == 'POST':

        data = request.json

        new_id = db.create_schedule(
            school_id,
            data.get('name')
        )

        return jsonify({
            "success": True,
            "schedule_id": new_id
        })


# ---------------------------------------------------------
# BELL OFFSET
# ---------------------------------------------------------

@app.route('/api/admin/offset', methods=['GET', 'POST'])
def manage_offset():

    school_id = session.get('admin_school_id')

    if not school_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        return jsonify({
            "offset_seconds": db.get_school_offset(school_id)
        })

    data = request.json

    try:
        offset_seconds = int(data.get('offset_seconds', 0))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Offset must be a number."
        }), 400

    db.update_school_offset(
        school_id,
        offset_seconds
    )

    return jsonify({
        "success": True,
        "offset_seconds": offset_seconds
    })


# ---------------------------------------------------------
# SET TODAY'S SCHEDULE
# ---------------------------------------------------------

@app.route('/api/admin/set_today', methods=['POST'])
def set_today():

    school_id = session.get('admin_school_id')

    if not school_id:
        return jsonify({"error": "Unauthorized"}), 401

    schedule_id = request.json.get('schedule_id')

    db.set_todays_schedule(
        school_id,
        schedule_id
    )

    return jsonify({"success": True})


# ---------------------------------------------------------
# SCHEDULE SETTINGS
# ---------------------------------------------------------

@app.route('/api/admin/schedule_settings', methods=['POST'])
def save_schedule_settings():

    school_id = session.get('admin_school_id')

    if not school_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    schedule_id = data.get('schedule_id')
    end_of_school = data.get('end_of_school', '')

    if not schedule_id:
        return jsonify({
            "error": "Missing schedule_id"
        }), 400

    db.update_schedule_settings(
        schedule_id,
        end_of_school
    )

    return jsonify({
        "success": True
    })


# ---------------------------------------------------------
# PERIODS
# ---------------------------------------------------------

@app.route('/api/admin/schedule_periods', methods=['POST'])
def save_periods():

    school_id = session.get('admin_school_id')

    if not school_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    schedule_id = data.get('schedule_id')
    periods = data.get('periods')

    if not schedule_id or not periods:
        return jsonify({
            "error": "Missing data"
        }), 400

    db.update_schedule_periods(
        schedule_id,
        periods
    )

    return jsonify({
        "success": True
    })


@app.route(
    '/api/admin/schedule_periods/<int:schedule_id>',
    methods=['GET']
)
def get_periods(schedule_id):

    school_id = session.get('admin_school_id')

    if not school_id:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(
        db.get_schedule_periods(schedule_id)
    )


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------

if __name__ == '__main__':
    app.run(
        debug=True,
        port=5007
    )