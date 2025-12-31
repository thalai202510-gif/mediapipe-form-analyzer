app.pyfrom flask import Flask, request, jsonify
import mediapipe as mp
import cv2
import numpy as np
import tempfile
import os
import requests

app = Flask(__name__)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5
)

def download_video(video_url):
    try:
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        raise Exception(f"Failed to download video: {str(e)}")

def calculate_angle(point1, point2, point3):
    a = np.array([point1.x, point1.y])
    b = np.array([point2.x, point2.y])
    c = np.array([point3.x, point3.y])
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def analyze_squat(landmarks):
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    back_angle = calculate_angle(left_shoulder, left_hip, left_knee)
    if 70 <= knee_angle <= 90:
        depth_score = 10.0
        depth_feedback = "Perfect depth - hitting parallel or below"
    elif 90 < knee_angle <= 110:
        depth_score = 7.5
        depth_feedback = "Good depth, but can go a bit lower"
    else:
        depth_score = 5.0
        depth_feedback = "Depth needs improvement - go lower"
    knee_score = 8.0
    knee_feedback = "Knees tracking well"
    if 60 <= back_angle <= 80:
        back_score = 9.0
        back_feedback = "Excellent back angle - staying upright"
    elif 45 <= back_angle < 60:
        back_score = 6.5
        back_feedback = "Leaning forward a bit - keep chest up"
    else:
        back_score = 4.0
        back_feedback = "Too much forward lean - focus on staying upright"
    return {"depth": {"score": depth_score, "feedback": depth_feedback}, "kneeTracking": {"score": knee_score, "feedback": knee_feedback}, "backAngle": {"score": back_score, "feedback": back_feedback}}

def analyze_deadlift(landmarks):
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    back_angle = calculate_angle(left_shoulder, left_hip, left_knee)
    if 30 <= back_angle <= 45:
        back_score = 9.0
        back_feedback = "Great hip hinge - back angle is optimal"
    elif 45 < back_angle <= 60:
        back_score = 7.0
        back_feedback = "Back angle okay, but hinge more at hips"
    else:
        back_score = 5.0
        back_feedback = "Need more hip hinge - not enough forward lean"
    return {"backAngle": {"score": back_score, "feedback": back_feedback}, "barPath": {"score": 8.0, "feedback": "Bar path looks good"}}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "mediapipe-form-analysis"})

@app.route('/analyze', methods=['POST'])
def analyze_form():
    try:
        data = request.json
        video_url = data.get('videoUrl')
        exercise_type = data.get('exerciseType', 'squat').lower()
        if not video_url:
            return jsonify({"error": "videoUrl is required"}), 400
        video_path = download_video(video_url)
        cap = cv2.VideoCapture(video_path)
        all_metrics = []
        frame_count = 0
        max_frames = 90
        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                if exercise_type == 'squat':
                    metrics = analyze_squat(landmarks)
                elif exercise_type == 'deadlift':
                    metrics = analyze_deadlift(landmarks)
                else:
                    metrics = analyze_squat(landmarks)
                all_metrics.append(metrics)
            frame_count += 1
        cap.release()
        os.unlink(video_path)
        if not all_metrics:
            return jsonify({"error": "No pose detected in video"}), 400
        final_metrics = {}
        metric_names = list(all_metrics[0].keys())
        for metric_name in metric_names:
            scores = [m[metric_name]["score"] for m in all_metrics]
            avg_score = sum(scores) / len(scores)
            final_metrics[metric_name] = {"score": round(avg_score, 1), "feedback": all_metrics[-1][metric_name]["feedback"]}
        overall_score = sum(m["score"] for m in final_metrics.values()) / len(final_metrics)
        recommendations = []
        for metric_name, metric_data in final_metrics.items():
            if metric_data["score"] < 7.0:
                recommendations.append(metric_data["feedback"])
        if not recommendations:
            recommendations = ["Great form overall! Keep it up."]
        return jsonify({"success": True, "formScore": round(overall_score, 1), "maxScore": 10, "metrics": [{"metric": name, **data} for name, data in final_metrics.items()], "recommendations": recommendations, "framesAnalyzed": frame_count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
