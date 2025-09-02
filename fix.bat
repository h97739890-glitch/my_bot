@echo off
cd /d C:\Users\hussain\Downloads\38833FF26BA1D.UnigramPreview_g9c9v27vpyspw!App\بوت2\بوت2

echo 🔹 البحث عن أي ملف index.lock قديم وحذفه ...
if exist .git\index.lock (
    del .git\index.lock
    echo ✔️ تم حذف index.lock القديم.
) else (
    echo ⚡ لا يوجد ملف index.lock.
)

echo 🔹 التأكد أن الفرع اسمه main ...
git branch -M main

echo 🔹 إضافة جميع الملفات (بما فيها runtime.txt) ...
git add .

echo 🔹 عمل commit ...
git commit -m "Fix: added runtime.txt and cleanup"

echo 🔹 رفع الملفات إلى GitHub ...
git push origin main

echo ✅ العملية انتهت.
pause
