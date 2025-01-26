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

        # إدخال الفيديو
        video_frame = tk.LabelFrame(self.master, text="إدخال الفيديو", padx=10, pady=10)
        video_frame.pack(fill="x", padx=10, pady=5)
        
        self.video_btn = tk.Button(video_frame, text="اختر فيديو", command=self.select_video)
        self.video_btn.pack(side="left", padx=5)
        
        self.video_label = tk.Label(video_frame, text="لم يتم اختيار فيديو")
        self.video_label.pack(side="left", fill="x", expand=True)
        
        self.remove_video_btn = tk.Button(video_frame, text="إزالة الفيديو", command=self.remove_video)
        self.remove_video_btn.pack(side="right", padx=5)

        # إدخال الصور
        image_frame = tk.LabelFrame(self.master, text="إدخال الصور", padx=10, pady=10)
        image_frame.pack(fill="x", padx=10, pady=5)
        
        self.image_btn = tk.Button(image_frame, text="اختر صور", command=self.select_images)
        self.image_btn.pack(side="left", padx=5)
        
        self.image_label = tk.Label(image_frame, text="لم يتم اختيار صور")
        self.image_label.pack(side="left", fill="x", expand=True)

        self.remove_image_btn = tk.Button(image_frame, text="إزالة الصور", command=self.remove_images)
        self.remove_image_btn.pack(side="right", padx=5)

        # قائمة منسدلة لاختيار الملفات لإزالة
        self.remove_files_label = tk.Label(self.master, text="اختر ملف لإزالته")
        self.remove_files_label.pack(pady=5)

        self.remove_files_combobox = ttk.Combobox(self.master, state="readonly")
        self.remove_files_combobox.pack(pady=5)

        # زر لإزالة الملف المحدد من القائمة
        self.remove_selected_btn = tk.Button(self.master, text="إزالة الملف المحدد", command=self.remove_selected)
        self.remove_selected_btn.pack(pady=5)

        # زر لإزالة جميع الصور والفيديوهات
        self.remove_all_btn = tk.Button(self.master, text="إزالة جميع الملفات", command=self.remove_all)
        self.remove_all_btn.pack(pady=5)

        # إخراج
        output_frame = tk.LabelFrame(self.master, text="دليل الإخراج", padx=10, pady=10)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        self.output_btn = tk.Button(output_frame, text="اختر دليل الإخراج", command=self.select_output)
        self.output_btn.pack(side="left", padx=5)
        
        self.output_label = tk.Label(output_frame, text="لم يتم اختيار دليل الإخراج")
        self.output_label.pack(side="left", fill="x", expand=True)

        # التقدم
        self.progress = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)

        # الحالة
        self.status_label = tk.Label(self.master, text="جاهز", fg="green")
        self.status_label.pack(pady=10)

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

    def select_video(self):
        files = filedialog.askopenfilenames(filetypes=[("ملفات الفيديو", "*.mp4 *.avi *.mov *.mkv")])
        if files:
            self.current_video = files
            self.video_label.config(text=f"{len(files)} فيديوهات مختارة")
            self.update_file_list()

    def select_images(self):
        files = filedialog.askopenfilenames(filetypes=[("ملفات الصور", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif")])
        if files:
            self.current_images = files
            self.image_label.config(text=f"{len(files)} صور مختارة")
            self.update_file_list()

    def update_file_list(self):
        file_list = []
        if hasattr(self, 'current_video'):
            file_list.extend(self.current_video)
        if hasattr(self, 'current_images'):
            file_list.extend(self.current_images)
        
        self.remove_files_combobox['values'] = file_list

    def remove_selected(self):
        selected_file = self.remove_files_combobox.get()
        if selected_file:
            if selected_file in self.current_video:
                self.current_video.remove(selected_file)
            elif selected_file in self.current_images:
                self.current_images.remove(selected_file)
            
            self.update_file_list()
            messagebox.showinfo("تم الحذف", f"تم إزالة {selected_file}")
        else:
            messagebox.showwarning("تحذير", "يرجى اختيار ملف من القائمة لإزالته.")

    def remove_all(self):
        if hasattr(self, 'current_video'):
            self.current_video = []
        if hasattr(self, 'current_images'):
            self.current_images = []

        self.update_file_list()
        messagebox.showinfo("تم الحذف", "تم إزالة جميع الصور والفيديوهات المحددة.")

    def remove_video(self):
        if hasattr(self, 'current_video') and self.current_video:
            self.current_video = []
            self.video_label.config(text="لم يتم اختيار فيديو")
            self.update_file_list()
        else:
            messagebox.showwarning("تحذير", "لا يوجد فيديو لحذفه.")

    def remove_images(self):
        if hasattr(self, 'current_images') and self.current_images:
            self.current_images = []
            self.image_label.config(text="لم يتم اختيار صور")
            self.update_file_list()
        else:
            messagebox.showwarning("تحذير", "لا توجد صور لحذفها.")

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
            if self.advanced_content_verification(img_path):
                img = cv2.imread(img_path)
                h, w = img.shape[:2]
                x, y, w_, h_ = int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8)
                img[y:y+h_, x:x+w_] = cv2.GaussianBlur(img[y:y+h_, x:x+w_], (31, 31), 30)
                cv2.imwrite(output_path, img)
                return True
            return False
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
            
            for i, frame_path in enumerate(frames):
                if self.advanced_content_verification(frame_path):
                    start = max(0, i-3)
                    end = min(len(frames), i+4)
                    
                    for j in range(start, end):
                        frame = cv2.imread(frames[j])
                        h, w = frame.shape[:2]
                        x, y, w_, h_ = int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8)
                        frame[y:y+h_, x:x+w_] = cv2.GaussianBlur(frame[y:y+h_, x:x+w_], (31, 31), 30)
                        cv2.imwrite(frames[j], frame)
                
                # تحديث التقدم
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
        
        files_to_process = []
        if hasattr(self, 'current_video'):
            files_to_process.extend(self.current_video)
        if hasattr(self, 'current_images'):
            files_to_process.extend(self.current_images)
        
        self.total_files = len(files_to_process)
        self.processed_files = 0
        self.progress['value'] = 0
        self.processing = True
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        
        # تشغيل المعالجة في ثيل منفصل
        processing_thread = threading.Thread(target=self.process_files, args=(files_to_process,))
        processing_thread.start()

    def process_files(self, files):
        try:
            for file_path in files:
                if not self.processing:
                    break
                
                output_path = os.path.join(self.output_dir, os.path.basename(file_path))
                
                if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    self.process_video(file_path, output_path)
                else:
                    self.process_image(file_path, output_path)
                    self.processed_files += 1
                    self.progress['value'] = (self.processed_files / self.total_files) * 100
                    self.master.update_idletasks()
                
                # إزالة الملف من القائمة بعد المعالجة
                if file_path in self.current_video:
                    self.current_video.remove(file_path)
                elif file_path in self.current_images:
                    self.current_images.remove(file_path)

                # تحديث القائمة بعد إزالة الملفات المعالجة
                self.update_file_list()

            self.status_label.config(text="تمت المعالجة بنجاح!", fg="green")
        except Exception as e:
            self.status_label.config(text=f"خطأ: {str(e)}", fg="red")
        finally:
            self.processing = False
            self.start_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")

    def cancel_processing(self):
        self.processing = False
        self.status_label.config(text="تم إلغاء المعالجة", fg="orange")

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaProcessorApp(root)
    root.mainloop()
