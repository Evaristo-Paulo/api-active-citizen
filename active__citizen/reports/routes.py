from active__citizen import db
from flask import request, jsonify, Blueprint
from sqlalchemy import desc
from datetime import date, time
from flask_login import current_user, login_required
from active__citizen.models import Report
from active__citizen.reports.utils import save_picture

reports = Blueprint('reports', __name__)

# REPORT
@reports.route('/api/reports/add', methods=["POST"])
@login_required
def add_report():
    data = request.json
    logged_user_id = int(current_user.id)

    

    if 'date' in data and 'time' in data and 'location' in data and 'description' in data:
        # GENERATE DATE
        str_date = data['date']
        list_date = [int(item) for item in str_date.split('-')]
        year, month, days = list_date
        datetime_date = date(year, month, days)

        # GENERATE TIME
        str_time = data['time']
        list_time = [int(item) for item in str_time.split(':')]
        hours, min = list_time
        datetime_time = time(hours, min, 0)

        # GENERATE MEDIA FILE
        file = ''
        if 'file' in data:
            file = save_picture(data['file'])

        report = Report(user_id=logged_user_id, file=file, date=datetime_date, time=datetime_time, location=data['location'], description=data['description'])

        db.session.add(report)
        db.session.commit()

        return jsonify({"message": "Report stored successfully"})
    
    return jsonify({"message": "Invalid report data"}), 400
    

@reports.route('/api/reports/delete/<int:report_id>', methods=["DELETE"])
@login_required
def delete_report(report_id):
    logged_user_id = int(current_user.id)

    report = Report.query.filter(
        Report.user_id==logged_user_id, 
        Report.id==report_id
        ).first()

    if report:
        db.session.delete(report)
        db.session.commit()

        return jsonify({"message": "Report deleted successfully"})
    
    return jsonify({"message": "Report not found"}), 404


@reports.route('/api/reports/show/<int:report_id>', methods=['GET'])
def get_report_details(report_id):
    report = Report.query.get(report_id)

    if report: 
        return jsonify({ 
            "id": report.id,
            "date": report.date,
            "time": str(report.time),
            "location": report.location,
            "file": report.file,
            "description": report.description,
            "active_citizen_id": report.user_id,
            "active_citizen_name": report.user.username,
        })
    
    return jsonify({"message": "Report not found"}), 404


@reports.route('/api/reports/update/<int:report_id>', methods=["PUT"])
@login_required
def update_report(report_id):
    report = Report.query.get(report_id)

    logged_user_id = int(current_user.id)

    report = Report.query.filter(
        Report.user_id==logged_user_id, 
        Report.id==report_id
        ).first()

    if report is None:
        return jsonify({"message": "Report not found"}), 404

    data = request.json

    if 'date' in data:
        # GENERATE DATE
        str_date = data['date']
        list_date = [int(item) for item in str_date.split('-')]
        year, month, days = list_date
        datetime_date = date(year, month, days)
        report.date = datetime_date
    
    if 'time' in data:
        # GENERATE TIME
        str_time = data['time']
        list_time = [int(item) for item in str_time.split(':')]
        hours, min = list_time
        datetime_time = time(hours, min, 0)
        report.time = datetime_time

    if 'location' in data:
        report.location = data['location']

    if 'description' in data:
        report.description = data['description']

    if 'file' in data:
        report.file = save_picture(data['file'])
    
    db.session.commit()
    return jsonify({"message": "Report updated successfully"})


@reports.route('/api/reports/', methods=["GET"])
@login_required
def get_reports():
    logged_user_id = int(current_user.id)

    reports = Report.query.filter(
        Report.user_id==logged_user_id, 
        ).order_by(desc(Report.id))

    items = list()

    for report in reports:
        item = { 
            "id": report.id,
            "date": report.date,
            "location": report.location,
            "description": report.description,
            "active_citizen_name": report.user.username,
        }
        items.append(item)

    return jsonify({"Reports": items})


if __name__ == '__main__':
    print(f'routes.py')