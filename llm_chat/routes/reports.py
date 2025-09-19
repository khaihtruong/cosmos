import json
import tempfile
import os
from flask import Blueprint, jsonify, render_template, abort, request, send_file, Response
from flask_login import login_required, current_user
from ..models import Report, ChatWindow, User
from ..services.report_scheduler import ReportScheduler
from report.unified_report_generator import UnifiedReportGenerator

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/", methods=["GET"])
@login_required
def get_reports():
    """Get reports accessible to current user"""
    if current_user.is_patient():
        # Patients see their own reports
        reports = Report.query.filter_by(patient_id=current_user.id).order_by(Report.generated_at.desc()).all()
    elif current_user.is_provider():
        # Providers see reports for their patients
        reports = Report.query.filter_by(provider_id=current_user.id).order_by(Report.generated_at.desc()).all()
    elif current_user.is_admin():
        # Admins see all reports
        reports = Report.query.order_by(Report.generated_at.desc()).all()
    else:
        abort(403)

    return jsonify([r.to_dict() for r in reports])


@reports_bp.route("/<int:report_id>", methods=["GET"])
@login_required
def get_report(report_id):
    """Get a specific report"""
    report = Report.query.get_or_404(report_id)

    # Access control
    if current_user.is_patient() and report.patient_id != current_user.id:
        abort(403)
    elif current_user.is_provider() and report.provider_id != current_user.id:
        abort(403)

    return jsonify(report.to_dict())


@reports_bp.route("/patient/<int:patient_id>", methods=["GET"])
@login_required
def get_patient_reports(patient_id):
    """Get all reports for a specific patient (provider only)"""
    if not current_user.is_provider() and not current_user.is_admin():
        abort(403)

    # Verify provider can access this patient
    if current_user.is_provider() and not current_user.can_access_patient(patient_id):
        abort(403)

    reports = Report.query.filter_by(patient_id=patient_id).order_by(Report.generated_at.desc()).all()
    return jsonify([r.to_dict() for r in reports])


@reports_bp.route("/window/<int:window_id>", methods=["GET"])
@login_required
def get_window_report(window_id):
    """Get report for a specific window"""
    window = ChatWindow.query.get_or_404(window_id)

    # Access control
    if current_user.is_patient() and window.patient_id != current_user.id:
        abort(403)
    elif current_user.is_provider() and window.provider_id != current_user.id:
        abort(403)

    report = Report.query.filter_by(window_id=window_id, report_type='default').first()

    if not report:
        return jsonify({'error': 'Report not found'}), 404

    return jsonify(report.to_dict())


@reports_bp.route("/window/<int:window_id>/generate", methods=["POST"])
@login_required
def generate_window_report(window_id):
    """Manually generate a report for a window (provider only)"""
    if not current_user.is_provider() and not current_user.is_admin():
        abort(403)

    window = ChatWindow.query.get_or_404(window_id)

    # Verify provider owns this window
    if current_user.is_provider() and window.provider_id != current_user.id:
        abort(403)

    try:
        report = ReportScheduler.generate_report_for_window(window_id)
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route("/check-scheduler", methods=["POST"])
@login_required
def check_scheduler():
    """Manually trigger the report scheduler check (admin/provider only)"""
    if not current_user.is_provider() and not current_user.is_admin():
        abort(403)

    try:
        from ..services.report_scheduler import report_scheduler
        report_scheduler.check_and_generate_reports()
        return jsonify({'status': 'success', 'message': 'Report check completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route("/html/<int:report_id>", methods=["GET"])
@login_required
def get_report_html(report_id):
    """Get formatted HTML version of a report"""
    report = Report.query.get_or_404(report_id)

    # Access control
    if current_user.is_patient() and report.patient_id != current_user.id:
        abort(403)
    elif current_user.is_provider() and report.provider_id != current_user.id:
        abort(403)

    report_data = json.loads(report.report_data)

    # Always use unified generator for rendering
    generator = UnifiedReportGenerator(report.window_id)
    html_content = generator.render_html(report_data)

    return jsonify({'html': html_content})


# Enhanced report endpoint removed - use unified endpoint instead


@reports_bp.route("/window/<int:window_id>/config", methods=["GET", "PUT"])
@login_required
def window_report_config(window_id):
    """Get or update report configuration for a window"""
    if not current_user.is_provider() and not current_user.is_admin():
        abort(403)

    window = ChatWindow.query.get_or_404(window_id)

    # Verify provider owns this window
    if current_user.is_provider() and window.provider_id != current_user.id:
        abort(403)

    if request.method == "GET":
        return jsonify(window.get_report_config())

    elif request.method == "PUT":
        try:
            from ..extensions import db
            data = request.json or {}
            config = data.get('config', {})

            # Validate config keys
            valid_keys = {'ai_summary', 'saved_messages', 'descriptive_stats', 'nlp_analysis'}
            config = {k: v for k, v in config.items() if k in valid_keys}

            window.set_report_config(config)
            db.session.commit()

            return jsonify({'status': 'success', 'config': window.get_report_config()})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@reports_bp.route("/window/<int:window_id>/generate-unified", methods=["POST"])
@login_required
def generate_unified_window_report(window_id):
    """Generate a unified report using the new architecture"""
    if not current_user.is_provider() and not current_user.is_admin():
        abort(403)

    window = ChatWindow.query.get_or_404(window_id)

    # Verify provider owns this window
    if current_user.is_provider() and window.provider_id != current_user.id:
        abort(403)

    try:
        report = UnifiedReportGenerator.save_report(window_id)
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route("/download/<int:report_id>/<format>", methods=["GET"])
@login_required
def download_report(report_id, format):
    """Download report in specified format (html or pdf)"""
    report = Report.query.get_or_404(report_id)

    # Access control
    if current_user.is_patient() and report.patient_id != current_user.id:
        abort(403)
    elif current_user.is_provider() and report.provider_id != current_user.id:
        abort(403)

    window = ChatWindow.query.get(report.window_id)
    filename = f"report_{window.title.replace(' ', '_')}_{report.generated_at}.{format}"

    if format == 'html':
        # Always use unified generator for export
        html_content = UnifiedReportGenerator.export_html(report.window_id)

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name

        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/html'
        )

    elif format == 'pdf':
        # Generate actual PDF using unified generator
        try:
            pdf_bytes = UnifiedReportGenerator.export_pdf(report.window_id)

            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                f.write(pdf_bytes)
                temp_path = f.name

            return send_file(
                temp_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        except ImportError as e:
            # Fallback to HTML if weasyprint not available
            html_content = UnifiedReportGenerator.export_html(report.window_id)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                temp_path = f.name

            return send_file(
                temp_path,
                as_attachment=True,
                download_name=filename.replace('.pdf', '.html'),
                mimetype='text/html'
            )

    else:
        abort(400, "Invalid format. Use 'html' or 'pdf'")


@reports_bp.route("/live/<int:window_id>", methods=["GET"])
@login_required
def get_live_report(window_id):
    """Generate and return a live report without saving to database"""
    window = ChatWindow.query.get_or_404(window_id)

    # Access control
    if current_user.is_patient() and window.patient_id != current_user.id:
        abort(403)
    elif current_user.is_provider() and window.provider_id != current_user.id:
        abort(403)

    try:
        generator = UnifiedReportGenerator(window_id)
        report_data = generator.generate()
        html_content = generator.render_html(report_data)

        return jsonify({
            'html': html_content,
            'data': report_data,
            'window_id': window_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route("/capabilities", methods=["GET"])
@login_required
def get_report_capabilities():
    """Get available report capabilities (like PDF generation)"""
    from report.unified_report_generator import WEASYPRINT_AVAILABLE

    return jsonify({
        'pdf_generation': WEASYPRINT_AVAILABLE,
        'html_export': True,
        'json_export': True
    })