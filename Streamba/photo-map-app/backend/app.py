from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Database configuration
# Load environment variables from .env file
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory for uploaded files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit to 16 MB
db = SQLAlchemy(app)

# Model for storing photos
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)

db.create_all()

@app.route('/upload', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    # Validate file type (only allow image files)
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'error': 'File type not supported. Please upload an image.'}), 400

    # Save file to the uploads directory
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Use dummy coordinates for now
    lat, lon = 51.505, -0.09  # Placeholder coordinates

    new_photo = Photo(url=file_path, lat=lat, lon=lon)
    db.session.add(new_photo)
    db.session.commit()

    return jsonify({'message': 'Photo uploaded successfully!'}), 201

@app.route('/photos', methods=['GET'])
def get_photos():
    photos = Photo.query.all()
    return jsonify([{'id': p.id, 'url': p.url, 'lat': p.lat, 'lon': p.lon} for p in photos])

if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
