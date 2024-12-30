from datetime import datetime
from app import db

class MediaAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_result = db.Column(db.Text)
    media_type = db.Column(db.String(10))  # 'image' or 'video'
    processed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'analysis_result': self.analysis_result,
            'media_type': self.media_type,
            'processed': self.processed
        }
