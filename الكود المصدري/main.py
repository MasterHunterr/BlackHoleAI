import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

# إعداد المسارات
base_dir = 'dataset'
train_dir = os.path.join(base_dir, 'train')
val_dir = os.path.join(base_dir, 'val')

# إعداد معالجات البيانات مع التوسيع التلقائي للبيانات
train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=40,  # تدوير الصور
    width_shift_range=0.2,  # تحريك الصور أفقيًا
    height_shift_range=0.2,  # تحريك الصور عموديًا
    shear_range=0.2,  # تحريف الصور
    zoom_range=0.2,  # تكبير الصور
    horizontal_flip=True,  # التبديل الأفقي
    fill_mode='nearest'  # ملء الفراغات في الصورة
)

val_datagen = ImageDataGenerator(rescale=1.0/255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(150, 150),  # حجم الصور
    batch_size=32,
    class_mode='binary'  # الفئتان: مناسبة/غير مناسبة
)

val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='binary'
)

# إنشاء النموذج
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')  # مخرجات ثنائية (0 أو 1)
])

# إعداد النموذج للتدريب
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# تدريب النموذج
history = model.fit(
    train_generator,
    epochs=10,
    validation_data=val_generator
)

# حفظ النموذج
model.save('BlackHoleAI.h5')
