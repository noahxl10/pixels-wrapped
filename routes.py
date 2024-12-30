from flask import render_template, request, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from app import app, db
from models import MediaAnalysis
from media_processor import MediaProcessor

# Initialize the media processor
processor = MediaProcessor()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'media' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    files = request.files.getlist('media')
    
    if not files or all(file.filename == '' for file in files):
        return jsonify({'success': False, 'error': 'No selected file'})

    analyses = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # Process the file based on its type
                if file.content_type.startswith('image/'):
                    with open(file_path, 'rb') as f:
                        compressed_data = processor.compress_image(f.read())
                        analysis_result = processor.analyze_media(compressed_data)
                elif file.content_type.startswith('video/'):
                    frames = processor.process_video(file_path)
                    # Analyze the first frame for demo purposes
                    analysis_result = processor.analyze_media(frames[0]) if frames else None
                
                # Create database entry
                media_analysis = MediaAnalysis(
                    filename=filename,
                    media_type='image' if file.content_type.startswith('image/') else 'video',
                    analysis_result=str(analysis_result),
                    processed=True
                )
                db.session.add(media_analysis)
                analyses.append(media_analysis)
                
            except Exception as e:
                app.logger.error(f"Error processing {filename}: {str(e)}")
                flash(f'Error processing {filename}', 'danger')
                continue
            
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    if analyses:
        db.session.commit()
        return jsonify({'success': True, 'redirect': url_for('results')})
    
    return jsonify({'success': False, 'error': 'No files were successfully processed'})

@app.route('/results')
def results():
    analyses = MediaAnalysis.query.order_by(MediaAnalysis.upload_date.desc()).all()
    summary = generate_yearly_summary(analyses)
    return render_template('results.html', analyses=analyses, summary=summary)

def generate_yearly_summary(analyses):
    if not analyses:
        return "No media has been analyzed yet."
    
    # Group analyses by month and compile key findings
    events = []
    for analysis in analyses:
        if analysis.analysis_result:
            try:
                result = eval(analysis.analysis_result)
                if 'description' in result:
                    events.append(result['description'])
            except:
                continue
    
    if not events:
        return "Your media has been processed, but no significant events were detected."
    
    # Create a narrative summary
    summary = "Here's what your year looked like: "
    summary += " ".join(events[:5])  # Limit to first 5 events for brevity
    return summary
