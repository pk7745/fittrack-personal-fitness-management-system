from app.services.fitness_service import calculate_bmi, get_bmi_category, calculate_goal_progress


def test_bmi_calculation():
    # Valid values: 70 kg, 175 cm -> 70 / (1.75^2) = 22.857... -> 22.9
    assert calculate_bmi(70.0, 175.0) == 22.9
    assert calculate_bmi(60.0, 165.0) == 22.0
    assert calculate_bmi(80.0, 180.0) == 24.7

    # Zero height or weight
    assert calculate_bmi(0, 175) is None
    assert calculate_bmi(70, 0) is None
    assert calculate_bmi(0, 0) is None

    # Negative height or weight
    assert calculate_bmi(-70, 175) is None
    assert calculate_bmi(70, -175) is None

    # Missing / None values
    assert calculate_bmi(None, 175) is None
    assert calculate_bmi(70, None) is None
    assert calculate_bmi(None, None) is None

    # Invalid types
    assert calculate_bmi("abc", 175) is None
    assert calculate_bmi(70, "xyz") is None


def test_bmi_categories_and_boundaries():
    assert get_bmi_category(16.0) == "Underweight"
    assert get_bmi_category(18.4) == "Underweight"
    assert get_bmi_category(18.5) == "Normal"
    assert get_bmi_category(24.9) == "Normal"
    assert get_bmi_category(25.0) == "Overweight"
    assert get_bmi_category(29.9) == "Overweight"
    assert get_bmi_category(30.0) == "Obese"
    assert get_bmi_category(35.0) == "Obese"
    assert get_bmi_category(None) == "Not Calculated"


def test_goal_progress_audit_cases():
    # 1. Weight Loss: Current = 80, Target = 70
    wl = calculate_goal_progress("Weight Loss", 70, 80)
    assert wl["percentage"] == 87.5
    assert wl["is_completed"] is False

    # Target achieved: Current = 70, Target = 70
    wl_done = calculate_goal_progress("Weight Loss", 70, 70)
    assert wl_done["percentage"] == 100.0
    assert wl_done["is_completed"] is True

    # Exceeded target: Current = 65, Target = 70
    wl_exceeded = calculate_goal_progress("Weight Loss", 70, 65)
    assert wl_exceeded["percentage"] == 100.0
    assert wl_exceeded["is_completed"] is True

    # 2. Weight Gain: Current = 60, Target = 70
    wg = calculate_goal_progress("Weight Gain", 70, 60)
    assert wg["percentage"] == 85.7
    assert wg["is_completed"] is False

    # Achieved: Current = 70, Target = 70
    wg_done = calculate_goal_progress("Weight Gain", 70, 70)
    assert wg_done["percentage"] == 100.0
    assert wg_done["is_completed"] is True

    # Exceeded: Current = 75, Target = 70
    wg_exceeded = calculate_goal_progress("Weight Gain", 70, 75)
    assert wg_exceeded["percentage"] == 100.0
    assert wg_exceeded["is_completed"] is True

    # 3. General Numeric Goal: Current = 40, Target = 100
    gen = calculate_goal_progress("Muscle Building", 100, 40)
    assert gen["percentage"] == 40.0
    assert gen["is_completed"] is False

    # Achieved: Current = 100, Target = 100
    gen_done = calculate_goal_progress("Endurance", 100, 100)
    assert gen_done["percentage"] == 100.0
    assert gen_done["is_completed"] is True

    # Exceeded: Current = 120, Target = 100
    gen_exceeded = calculate_goal_progress("General Fitness", 100, 120)
    assert gen_exceeded["percentage"] == 100.0
    assert gen_exceeded["is_completed"] is True

    # 4. Zero / Negative / Invalid edge cases
    assert calculate_goal_progress("General Fitness", 100, 0)["percentage"] == 0.0
    assert calculate_goal_progress("General Fitness", 100, -10)["percentage"] == 0.0
    assert calculate_goal_progress("General Fitness", 0, 50)["percentage"] == 0.0
    assert calculate_goal_progress("General Fitness", -50, 50)["percentage"] == 0.0
    assert calculate_goal_progress("General Fitness", None, 50)["percentage"] == 0.0
    assert calculate_goal_progress("General Fitness", "invalid", 50)["percentage"] == 0.0


def test_save_fitness_record(auth_client):
    res = auth_client.post('/api/fitness', json={
        'weight': 62.5,
        'water_intake': 2.5,
        'calories_consumed': 1950,
        'record_date': '2026-09-25'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['record']['weight'] == 62.5
    assert data['summary']['bmi'] is not None


def test_save_fitness_record_invalid(auth_client):
    # Negative water intake
    res = auth_client.post('/api/fitness', json={'water_intake': -5.0})
    assert res.status_code == 400

    # Invalid date format
    res2 = auth_client.post('/api/fitness', json={'record_date': '25-09-2026'})
    assert res2.status_code == 400
