import os
from flask import Flask, render_template, request, session, jsonify, redirect, url_for, flash
from datetime import date, timedelta, time, datetime

# --- Flask App Initialization ---
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', FLASK_SECRET_KEY')

# --- Constants ---
DEFAULT_START_TIME = time(8, 0)
# Use a single color or the first one if you prefer variation later
DEFAULT_EVENT_COLOR = "#1E90FF" # Example color

# --- Helper Function: Generate Calendar Event Data ---
# MODIFIED: Simplified for a single medication input (still expects a list with one item)
def generate_event_data(medication_list, pet_name="Your Pet"):
    """Generates the list of event dictionaries for the calendar for a single medication."""
    temp_events = []
    if not medication_list: # Expecting a list containing zero or one medication
        return []

    med = medication_list[0] # Get the single medication
    drug_name = med.get('name', 'Unknown Med')
    # Use the default color
    current_color = DEFAULT_EVENT_COLOR

    for step in med.get('steps', []):
        required_keys = ('start_date', 'duration_days', 'dosage', 'type', 'frequency_hr')
        if not all(k in step for k in required_keys):
            app.logger.warning(f"Skipping malformed step in medication: {drug_name}")
            continue

        try:
            step_start_date_obj = date.fromisoformat(step['start_date'])
            step_duration = int(step['duration_days'])
            frequency_hr = int(step.get('frequency_hr', 24))
            if frequency_hr <= 0: frequency_hr = 24

            step_end_date_obj = step_start_date_obj + timedelta(days=step_duration - 1)

            try:
                dosage_val = float(step['dosage'])
                dosage_str = f"{dosage_val:.2f} {step['type']}"
            except (ValueError, TypeError):
                dosage_str = f"{step['dosage']} {step['type']}"

            event_title = dosage_str # Just dosage

            current_dose_dt = datetime.combine(step_start_date_obj, DEFAULT_START_TIME)
            dose_counter = 1

            while current_dose_dt.date() <= step_end_date_obj:
                start_dt_iso = current_dose_dt.isoformat()
                end_dt_iso = (current_dose_dt + timedelta(hours=1)).isoformat()

                temp_events.append({
                    "title": event_title,
                    "start": start_dt_iso,
                    "end": end_dt_iso,
                    "color": current_color, # Single color
                    "allDay": False,
                    "extendedProps": {
                        "pet": pet_name,
                        "drug": drug_name,
                        "dosage": dosage_str,
                        "frequency_hr": frequency_hr,
                        "notes": f"Dose {dose_counter}"
                    }
                })

                current_dose_dt += timedelta(hours=frequency_hr)
                dose_counter += 1

        except (ValueError, TypeError) as e:
             app.logger.error(f"Error processing step for medication {drug_name}: {e}")
             continue

    return sorted(temp_events, key=lambda x: x['start'])

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main page."""
    session.setdefault('pet_details', {})
    # MODIFIED: Use 'current_medication', default to None
    session.setdefault('current_medication', None)
    # Remove med_id_counter if not needed elsewhere
    # session.setdefault('med_id_counter', 0) # Likely no longer needed

    return render_template('index.html',
                           pet_details=session['pet_details'],
                           # MODIFIED: Pass the single medication object
                           current_medication=session.get('current_medication'))

# --- update_pet route remains the same ---
@app.route('/update_pet', methods=['POST'])
def update_pet():
    """Handles updates to pet details from the form."""
    try:
        session['pet_details'] = {
            'name': request.form.get('pet_name', '').strip(),
            'type': request.form.get('pet_type', 'Dog'),
            'age': int(request.form.get('pet_age', 0)),
            'weight': float(request.form.get('pet_weight', 0.0))
        }
        if session['pet_details']['age'] < 0: session['pet_details']['age'] = 0
        if session['pet_details']['weight'] < 0: session['pet_details']['weight'] = 0.0
        session.modified = True
        flash("Pet details updated.", "success")
    except ValueError:
        flash("Invalid input for pet age or weight.", "error")
    except Exception as e:
        flash(f"An error occurred updating pet details: {e}", "error")
    return redirect(url_for('index'))


@app.route('/set_med', methods=['POST']) # MODIFIED: Renamed route for clarity
def set_med():
    """Handles setting or updating the single medication."""
    try:
        med_name = request.form.get('med_name', '').strip()
        if not med_name:
            flash("Medication Name is required.", "error")
            return redirect(url_for('index'))

        dosages = request.form.getlist('dosage_step')
        types = request.form.getlist('type_step')
        freq_hrs = request.form.getlist('freq_hr_step')
        durations = request.form.getlist('duration_step')
        start_dates = request.form.getlist('start_date_step')

        num_steps = len(dosages)
        if not (num_steps > 0 and all(len(lst) == num_steps for lst in [types, freq_hrs, durations, start_dates])):
            flash("Inconsistent medication step data received. Please try again.", "error")
            return redirect(url_for('index'))

        med_steps = []
        is_valid = True
        for i in range(num_steps):
            try:
                # ... (validation for each step remains the same) ...
                dosage = float(dosages[i])
                freq_hr = int(freq_hrs[i])
                duration = int(durations[i])
                start_date = start_dates[i]
                med_type = types[i]

                if not (dosage > 0 and freq_hr >= 1 and duration >= 1 and start_date and med_type):
                    is_valid = False
                    flash(f"Invalid data in dosage step {i+1}. Please check all fields.", "warning")
                    break
                date.fromisoformat(start_date)

                med_steps.append({
                    "dosage": dosage, "type": med_type, "frequency_hr": freq_hr,
                    "duration_days": duration, "start_date": start_date
                })
            except (ValueError, TypeError):
                is_valid = False
                flash(f"Invalid numeric or date input in dosage step {i+1}.", "error")
                break

        if is_valid:
            # MODIFIED: Create the single medication entry
            # No ID needed if there's only one
            medication_entry = {
                "name": med_name,
                "steps": med_steps
            }
            # MODIFIED: Store directly into 'current_medication', replacing any previous one
            session['current_medication'] = medication_entry
            session.modified = True
            flash(f"Medication '{med_name}' set successfully.", "success")

    except Exception as e:
        app.logger.error(f"Error in set_med: {e}")
        flash(f"An unexpected error occurred setting medication: {e}", "error")

    return redirect(url_for('index'))


# MODIFIED: Renamed route and simplified logic
@app.route('/clear_medication', methods=['POST'])
def clear_medication():
    """Clears the current medication."""
    if session.get('current_medication'):
        session['current_medication'] = None
        session.modified = True
        flash("Medication cleared.", "info")
    else:
        flash("No medication was set to clear.", "warning")
    return redirect(url_for('index'))


# MODIFIED: Clear the single medication entry
@app.route('/clear_all', methods=['POST'])
def clear_all():
    """Clears the current medication and pet details (optional)."""
    session['current_medication'] = None
    # Optionally clear pet details too
    # session['pet_details'] = {}
    session.modified = True
    flash("Medication cleared.", "info") # Changed message slightly
    return redirect(url_for('index'))


@app.route('/get_schedule_events', methods=['GET'])
def get_schedule_events():
    """API endpoint to fetch calendar event data as JSON."""
    # MODIFIED: Get the single medication object
    current_med = session.get('current_medication')
    pet_name = session.get('pet_details', {}).get('name', 'Your Pet')

    med_list_for_generator = []
    if current_med:
        med_list_for_generator.append(current_med) # Pass as a list with one item

    if not med_list_for_generator:
        return jsonify([])
    try:
        # Pass the list containing the single medication
        event_data = generate_event_data(med_list_for_generator, pet_name)
        return jsonify(event_data)
    except Exception as e:
        app.logger.error(f"Error generating schedule: {e}")
        return jsonify({"error": "An internal error occurred generating the schedule."}), 500

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)