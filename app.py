import io
from flask import Flask, request, jsonify, send_file, url_for
from celery.result import AsyncResult
from tasks import celery_app, upscale_task

app = Flask(__name__)

@app.route('/upscale', methods=['POST'])
def upscale_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    image_bytes = file.read()
    task = upscale_task.delay(image_bytes)
    
    return jsonify({'task_id': task.id}), 202

@app.route('/tasks/<task_id>', methods=['GET'])
def get_status(task_id):
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        'status': result.status,
    }
    
    if result.ready():
        if result.successful():
            response['result'] = url_for('get_processed_file', task_id=task_id, _external=True)
        else:
            response['error'] = str(result.result)
            
    return jsonify(response)

@app.route('/processed/<task_id>', methods=['GET'])
def get_processed_file(task_id):
    result = AsyncResult(task_id, app=celery_app)
    if not result.ready() or not result.successful():
        return jsonify({'error': 'File not ready or task failed'}), 404
    
    image_bytes = result.result
    return send_file(
        io.BytesIO(image_bytes),
        mimetype='image/png',
        as_attachment=True,
        download_name=f'upscaled_{task_id}.png'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
