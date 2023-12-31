from src.db.db import Slot, serialize_slot
from flask import Blueprint, make_response, jsonify, request, Response
from src.db.db import db
from datetime import datetime


slots = Blueprint('slots', __name__)


def jsonify_response(data, status_code) -> tuple[Response, int]:
    response = make_response(jsonify(data))
    response.status_code = status_code
    return response


@slots.route('/slots', methods=['GET'])
def all_slots() -> tuple[Response, int]:
    slots = Slot.query.order_by(Slot.startTime).all()
    data = {'message': 'Slots read successfully', 'slots': [serialize_slot(slot) for slot in slots]}
    return jsonify_response(data, 200)


@slots.route('/create', methods=['POST'])
def create_slot() -> tuple[Response, int]:
    data = request.get_json()

    start_time = datetime.strptime(data['startTime'], '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(data['endTime'], '%Y-%m-%d %H:%M:%S')

    if start_time >= end_time:
        error_data = {'message': 'Start time must be before end time'}
        return jsonify_response(error_data, 400)

    slot = Slot(startTime=data['startTime'], endTime=data['endTime'], sport=data['sport'], subSection=data['subSection'])
    db.session.add(slot)
    db.session.commit()

    inserted_slot = {
        'slotID': slot.slotID,
        'startTime': slot.startTime.isoformat(),
        'endTime': slot.endTime.isoformat(),
        'sport': slot.sport,
        'subSection': slot.subSection,
        'createdAt': slot.createdAt.isoformat(),
        'updatedAt': slot.updatedAt.isoformat(),
    }

    data = {"message": "Slot created successfully", "slot": inserted_slot}
    return jsonify_response(data, 201)


@slots.route('/slot/<int:slot_id>', methods=['GET'])
def slot_detail(slot_id) -> tuple[Response, int]:
    slot = db.get_or_404(Slot, slot_id)
    data = {'message': 'Slot read successfully', 'slot': serialize_slot(slot)}
    return jsonify_response(data, 200)


@slots.route('/update/<int:slot_id>', methods=['PUT'])
def update_slot(slot_id) -> tuple[Response, int]:
    slot = db.get_or_404(Slot, slot_id)
    data = request.get_json()

    for field in ['startTime', 'endTime', 'sport', 'subSection']:
        if field in data:
            setattr(slot, field, data[field])

    db.session.commit()

    data = {'message': 'Slot updated successfully', 'slot': serialize_slot(slot)}
    return jsonify_response(data, 200)


@slots.route("/slot/<int:slot_id>/delete", methods=["POST"])
def slot_delete(slot_id) -> tuple[Response, int]:
    slot = db.get_or_404(Slot, slot_id)

    db.session.delete(slot)
    db.session.commit()

    data = {'message': 'Slot deleted successfully'}
    return jsonify_response(data, 200)
