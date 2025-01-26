import os
import cv2
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import requests
import webbrowser
from PIL import Image, ImageTk
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class MediaProcessorApp:
    def __init__(self, master):
        self.master = master
        master.title("معالج الوسائط الذكية - BlackHole AI")
        master.geometry("1000x700")
        
        # التحقق من التحديثات
        self.check_for_updates()
        
        # تحميل النماذج
        self.primary_model = load_model('BlackHoleAI.h5')
        self.secondary_model = None
        self.use_secondary = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.processing = False
        self.total_files = 0
        self.processed_files = 0

    def check_for_updates(self):
        try:
            # جلب البيانات من الرابط
            response = requests.get("https://raw.githubusercontent.com/MasterHunterr/BlackHoleAI/refs/heads/main/app.updata")
            if response.status_code == 200:
                app_status = response.text.strip()
                if app_status == "1":
                    messagebox.showinfo("تحديث متاح", "هناك تحديث جديد متاح للتطبيق! سيتم فتح الرابط في المتصفح لتحديث التطبيق.")
                    # فتح الرابط في المتصفح
                    webbrowser.open("https://github.com/MasterHunterr/BlackHoleAI")
                elif app_status == "0":
                    print("لا يوجد تحديثات جديدة.")
            else:
                print("فشل في الوصول إلى رابط التحديث.")
        except Exception as e:
            print(f"خطأ في التحقق من التحديثات: {str(e)}")

    def create_widgets(self):
        # إطار النماذج
        model_frame = tk.LabelFrame(self.master, text="إعدادات النموذج", padx=10, pady=10)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        self.secondary_check = tk.Checkbutton(
            model_frame, 
            text="تمكين النموذج الثانوي",
            variable=self.use_secondary,
            command=self.toggle_secondary_model
        )
        self.secondary_check.pack(side="right", padx=5)

        # إدخال الصور والفيديو
        media_frame = tk.LabelFrame(self.master, text="إدخال الوسائط (صور وفيديوهات)", padx=10, pady=10)
        media_frame.pack(fill="x", padx=10, pady=5)
        
        self.media_btn = tk.Button(media_frame, text="اختر صور وفيديوهات", command=self.select_media)
        self.media_btn.pack(side="left", padx=5)
        
        self.media_label = tk.Label(media_frame, text="لم يتم اختيار أي ملفات")
        self.media_label.pack(side="left", fill="x", expand=True)

        # إخراج
        output_frame = tk.LabelFrame(self.master, text="دليل الإخراج", padx=10, pady=10)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        self.output_btn = tk.Button(output_frame, text="اختر دليل الإخراج", command=self.select_output)
        self.output_btn.pack(side="left", padx=5)
        
        self.output_label = tk.Label(output_frame, text="لم يتم اختيار دليل الإخراج")
        self.output_label.pack(side="left", fill="x", expand=True)

        # التقدم العام
        self.progress = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)

        # الحالة
        self.status_label = tk.Label(self.master, text="جاهز", fg="green")
        self.status_label.pack(pady=10)

        # عرض اسم العملية الجارية
        self.current_file_label = tk.Label(self.master, text="العملية الحالية: لا شيء", fg="blue")
        self.current_file_label.pack(pady=5)

        # شريط التقدم للعملية الجارية
        self.current_file_progress = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="determinate")
        self.current_file_progress.pack(pady=5)

        # التحكم
        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=20)
        
        self.start_btn = tk.Button(control_frame, text="ابدأ المعالجة", command=self.start_processing)
        self.start_btn.pack(side="left", padx=10)
        
        self.cancel_btn = tk.Button(control_frame, text="إلغاء", command=self.cancel_processing, state="disabled")
        self.cancel_btn.pack(side="left", padx=10)

    def toggle_secondary_model(self):
        if self.use_secondary.get():
            try:
                self.secondary_model = load_model('BlackHoleAI2.h5')
                self.status_label.config(text="تم تمكين النموذج الثانوي", fg="green")
            except Exception as e:
                self.status_label.config(text=f"خطأ في تحميل النموذج الثانوي: {str(e)}", fg="red")
                self.use_secondary.set(False)
        else:
            self.secondary_model = None
            self.status_label.config(text="تم تعطيل النموذج الثانوي", fg="orange")

    def select_media(self):
        files = filedialog.askopenfilenames(filetypes=[("الوسائط", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.mp4 *.avi *.mov *.mkv")])
        if files:
            self.media_files = list(files)
            self.media_label.config(text=f"تم اختيار {len(files)} ملف/ملفات")
        else:
            self.media_label.config(text="لم يتم اختيار أي ملفات")

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_label.config(text=folder)
            self.output_dir = folder

    def advanced_content_verification(self, img_path):
        img = image.load_img(img_path, target_size=(150, 150))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        primary_pred = self.primary_model.predict(img_array, verbose=0)[0][0]
        secondary_pred = self.secondary_model.predict(img_array, verbose=0)[0][0] if self.secondary_model else 0
        
        return (primary_pred > 0.6) or (secondary_pred > 0.6 and self.use_secondary.get())

    def process_image(self, img_path, output_path):
        try:
            self.current_file_label.config(text=f"معالجة الصورة: {img_path}")
            self.master.update_idletasks()
            
            if self.advanced_content_verification(img_path):
                img = cv2.imread(img_path)
                h, w = img.shape[:2]
                x, y, w_, h_ = int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8)
                img[y:y+h_, x:x+w_] = cv2.GaussianBlur(img[y:y+h_, x:x+w_], (31, 31), 30)
                cv2.imwrite(output_path, img)
                self.current_file_progress['value'] = 100  # اكتمال
            return True
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return False

    def process_video(self, input_path, output_path):
        try:
            cap = cv2.VideoCapture(input_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_count = 0
            
            # إنشاء مجلد مؤقت للفريمات
            temp_dir = os.path.join(self.output_dir, "temp_frames")
            os.makedirs(temp_dir, exist_ok=True)
            
            # استخراج الفريمات
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
                cv2.imwrite(frame_path, frame)
                frame_count += 1
            
            cap.release()
            
            # معالجة الفريمات
            frames = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.png')])
            self.total_files = len(frames)
            self.processed_files = 0
            
            for i, frame_path in enumerate(frames):
                self.current_file_label.config(text=f"معالجة الإطار: {frame_path}")
                self.current_file_progress['value'] = (i / len(frames)) * 100
                self.master.update_idletasks()
                
                if self.advanced_content_verification(frame_path):
                    start = max(0, i-3)
                    end = min(len(frames), i+4)
                    
                    for j in range(start, end):
                        frame = cv2.imread(frames[j])
                        h, w = frame.shape[:2]
                        x, y, w_, h_ = int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8)
                        frame[y:y+h_, x:x+w_] = cv2.GaussianBlur(frame[y:y+h_, x:x+w_], (31, 31), 30)
                        cv2.imwrite(frames[j], frame)
                
                # تحديث التقدم العام
                self.processed_files += 1
                self.progress['value'] = (self.processed_files / self.total_files) * 100
                self.master.update_idletasks()
            
            # إعادة تجميع الفيديو
            self.create_video_from_frames(frames, output_path)
            
            # تنظيف الملفات المؤقتة
            for f in frames:
                os.remove(f)
            os.rmdir(temp_dir)
            
        except Exception as e:
            print(f"Video processing error: {str(e)}")

    def create_video_from_frames(self, frame_paths, output_path):
        if not frame_paths:
            return
        
        frame = cv2.imread(frame_paths[0])
        h, w, _ = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (w, h))
        
        for path in frame_paths:
            frame = cv2.imread(path)
            out.write(frame)
        
        out.release()

    def start_processing(self):
        if not hasattr(self, 'output_dir'):
            self.status_label.config(text="يرجى اختيار دليل الإخراج", fg="red")
            return
        
        if not hasattr(self, 'media_files') or not self.media_files:
            self.status_label.config(text="يرجى اختيار صور وفيديوهات", fg="red")
            return
        
        self.total_files = len(self.media_files)
        self.processed_files = 0

        # تشغيل المعالجة في خيط منفصل
        self.processing_thread = threading.Thread(target=self.process_files)
        self.processing_thread.start()

    def process_files(self):
        for media_file in self.media_files:
            output_path = os.path.join(self.output_dir, os.path.basename(media_file))
            if media_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                self.process_image(media_file, output_path)
            elif media_file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                self.process_video(media_file, output_path)

        self.status_label.config(text="تمت المعالجة بنجاح!", fg="green")
        self.cancel_btn.config(state="normal")
        
    def cancel_processing(self):
        if hasattr(self, 'processing_thread') and self.processing_thread.is_alive():
            self.status_label.config(text="تم إلغاء المعالجة", fg="orange")
            self.processing_thread.join()  # الانتظار حتى ينتهي الخيط

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaProcessorApp(root)
    root.mainloop()
