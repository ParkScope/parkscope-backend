from flask import Flask, request
import boto3
import time, os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION')
BUCKET_NAME = os.getenv('BUCKET_NAME')

# boto3 S3 클라이언트 생성
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

@app.route('/upload', methods=['POST'])
def upload_image():
    device_id = request.args.get('device_id')
    if not device_id:
        return 'Missing device_id', 400

    if request.data:
        # 1. 파일 이름 생성
        filename = f"{device_id}_{int(time.time())}.jpg"
        local_dir = 'uploads'
        os.makedirs(local_dir, exist_ok=True)

        # 2. 로컬 경로로 저장
        local_path = os.path.join(local_dir, filename)
        abs_path = os.path.abspath(local_path)
        with open(local_path, 'wb') as f:
            f.write(request.data)
        print(f"[Local] 저장 성공: {local_path}")

        # 3. S3 업로드 경로 설정
        s3_key = f"uploads/{filename}"

        # 4. S3 업로드
        try:
            s3.upload_file(
                abs_path,
                BUCKET_NAME,
                s3_key,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            print(f"[S3] 업로드 성공: {s3_key}")
        except Exception as e:
            print(f"[S3] 업로드 실패: {e}")
            return 'S3 upload failed', 500

        return 'Upload successful', 200
    else:
        return 'No image data received', 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
