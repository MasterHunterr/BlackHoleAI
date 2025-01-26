import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# تحميل النماذج
primary_model = load_model('BlackHoleAI.h5')
secondary_model = load_model('BlackHoleAI2.h5')

def advanced_content_verification(img_path):
    """التحقق المتقدم من المحتوى باستخدام نموذجين"""
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    primary_prediction = primary_model.predict(img_array, verbose=0)[0][0]
    secondary_prediction = secondary_model.predict(img_array, verbose=0)[0][0]
    
    return primary_prediction > 0.6 or secondary_prediction > 0.6

def blur_inappropriate_content(img):
    """تغبيش المحتوى غير اللائق"""
    h, w, _ = img.shape
    x, y, w_, h_ = int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8)
    
    blur_techniques = [
        lambda x: cv2.GaussianBlur(x, (31, 31), 30),
        lambda x: cv2.medianBlur(x, 31),
        lambda x: cv2.bilateralFilter(x, 9, 75, 75)
    ]
    
    blur_func = np.random.choice(blur_techniques)
    img[y:y+h_, x:x+w_] = blur_func(img[y:y+h_, x:x+w_])
    return img

def process_video(input_path, output_dir):
    """معالجة الفيديو مع التغبيش السياقي"""
    filename = os.path.splitext(os.path.basename(input_path))[0]
    video_output_dir = os.path.join(output_dir, filename)
    os.makedirs(video_output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(input_path)
    frame_count = 0
    processed_frames = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_path = os.path.join(video_output_dir, f'frame_{frame_count:04d}.png')
        cv2.imwrite(frame_path, frame)
        frame_count += 1
    
    cap.release()
    
    # معالجة الفريمات
    frames = sorted([os.path.join(video_output_dir, f) for f in os.listdir(video_output_dir) if f.endswith('.png')])
    
    for i, frame_path in enumerate(frames):
        if advanced_content_verification(frame_path):
            # تغبيش 3 فريمات قبل وبعد المحتوى غير اللائق
            start_blur = max(0, i - 3)
            end_blur = min(len(frames), i + 4)
            
            for j in range(start_blur, end_blur):
                frame = cv2.imread(frames[j])
                blurred_frame = blur_inappropriate_content(frame)
                cv2.imwrite(frames[j], blurred_frame)
    
    # إعادة تجميع الفيديو
    output_video_path = os.path.join(output_dir, os.path.basename(input_path))
    create_video_from_frames(frames, output_video_path)

def create_video_from_frames(frames, output_video_path):
    """إنشاء فيديو من الفريمات"""
    if not frames:
        print("لا توجد فريمات للتحويل")
        return
    
    first_frame = cv2.imread(frames[0])
    height, width, layers = first_frame.shape
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (width, height))
    
    for frame_path in frames:
        frame = cv2.imread(frame_path)
        out.write(frame)
    
    out.release()
    print(f"تم إنشاء الفيديو: {output_video_path}")

def process_directory(input_dir, output_dir):
    """معالجة جميع الملفات في المجلد"""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        
        if os.path.isfile(input_path):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                process_video(input_path, output_dir)
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                output_path = os.path.join(output_dir, filename)
                try:
                    if advanced_content_verification(input_path):
                        original_img = cv2.imread(input_path)
                        blurred_img = blur_inappropriate_content(original_img)
                        cv2.imwrite(output_path, blurred_img)
                    else:
                        cv2.imwrite(output_path, cv2.imread(input_path))
                except Exception as e:
                    print(f"خطأ في معالجة {filename}: {e}")

# المسارات  
#اكتب الخاصه فيك
input_dir = ''
output_dir = ''

# معالجة المجلد
process_directory(input_dir, output_dir)