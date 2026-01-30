import flet as ft
import pyrebase # تأكد من كتابتها بالأحرف الصغيرة

# --- إعدادات Firebase (ضع قيمك الحقيقية هنا) ---
config = {
    "apiKey": "AIzaSyBPwIst6T4yCElZ5ejco_Ipyu5HNTCesuo",
    "authDomain": "mosul-blood-bank.firebaseapp.com",
    "projectId": "mosul-blood-bank",
    "storageBucket": "mosul-blood-bank.firebasestorage.app",
    "messagingSenderId": "679206897612",
    "appId": "1:679206897612:web:126c3287ea09a767b47f69",
    "databaseURL":  "https://mosul-blood-bank-default-rtdb.europe-west1.firebasedatabase.app" 
}

# تهيئة الاتصال بالسحابة
firebase = pyrebase.initialize_app(config)
db = firebase.database()

def main(page: ft.Page):
    page.title = "مصرف الدم الرئيسي في الموصل"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 450
    page.window_height = 800
    page.assets_dir = "assets"
    
    def get_storage():
        try: return page.client_storage
        except: return None

    storage = get_storage()

    # --- دالة الحفظ السحابي (إضافة جديدة) ---
    def save_to_firebase(data):
        try:
            # نستخدم رقم الهاتف كعنوان لكل متبرع في القاعدة
            db.child("donors").child(data['phone']).set(data)
            return True
        except:
            return False

    # --- 1. واجهة الدخول (الهاتف) ---
    def show_login_view():
        page.clean()
        page.appbar = ft.AppBar(
            title=ft.Text("مصرف الدم الرئيسي في الموصل", weight="bold"),
            center_title=True, bgcolor=ft.Colors.RED_900, color="white"
        )
        
        quran_section = ft.Column([
            ft.Text("بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ", size=22, weight="bold", font_family="Farsi Simple"),
            ft.Text("﴿وَمَنْ أَحْيَاهَا فَكَأَنَّما أَحْيَا النَّاسَ جَمِيعًا﴾", 
                    size=32, color=ft.Colors.RED_900, text_align="center", weight="bold", font_family="Farsi Simple"),
            ft.Text("صَدَقَ اللهُ العَلِيُّ العَظِيمُ", size=22,font_family="Farsi Simple"),
        ], horizontal_alignment="center", spacing=5)

        phone_in = ft.TextField(label="رقم الهاتف", prefix_icon=ft.Icons.PHONE, width=350)

        page.add(ft.Container(content=ft.Column([
            ft.Icon(ft.Icons.WATER_DROP, size=70, color="red"),
            quran_section,
            ft.Divider(height=20),
            phone_in,
            ft.FilledButton("إرسال رمز التأكيد", width=350, bgcolor=ft.Colors.RED_800, 
                            on_click=lambda _: show_otp_view(phone_in.value))
        ], horizontal_alignment="center"), padding=20))

    # --- 1.1 واجهة الرمز (OTP) ---
    def show_otp_view(phone_number):
        page.clean()
        otp_in = ft.TextField(label="أدخل الرمز (123456)", prefix_icon=ft.Icons.LOCK_OUTLINE, text_align="center", width=300)
        
        def verify(e):
            if otp_in.value == "123456": show_registration_view(phone_number)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("الرمز خاطئ")); page.snack_bar.open = True; page.update()

        page.add(ft.Container(content=ft.Column([
            ft.Icon(ft.Icons.SMS_OUTLINED, size=50, color="blue"),
            ft.Text(f"تأكيد الرقم: {phone_number}", weight="bold"),
            otp_in,
            ft.FilledButton("تأكيد الدخول", width=300, bgcolor="green", on_click=verify),
            ft.TextButton("رجوع لتعديل الرقم", on_click=lambda _: show_login_view())
        ], horizontal_alignment="center", spacing=20), padding=40))

    # --- 2. واجهة تسجيل البيانات ---
    def show_registration_view(phone_val=""):
        page.clean()
        user_data = storage.get("user_info") if storage else {}
        
        name_in = ft.TextField(label="الاسم الرباعي", icon=ft.Icons.PERSON, value=user_data.get("name", ""))
        mother_in = ft.TextField(label="اسم الأم الثلاثي", icon=ft.Icons.PERSON_OUTLINE, value=user_data.get("mother", ""))
        id_in = ft.TextField(label="رقم البطاقة الموحدة", icon=ft.Icons.FINGERPRINT, value=user_data.get("id_card", ""))
        phone_in = ft.TextField(label="رقم الهاتف للتواصل", icon=ft.Icons.PHONE, value=phone_val if phone_val else user_data.get("phone", ""))
        gender_in = ft.Dropdown(label="الجنس", value=user_data.get("gender"), options=[ft.dropdown.Option("ذكر"), ft.dropdown.Option("أنثى")])
        
        dob = user_data.get("dob", "//").split("/")
        day_in, month_in, year_in = ft.TextField(label="يوم", width=80, value=dob[0]), ft.TextField(label="شهر", width=80, value=dob[1]), ft.TextField(label="سنة", width=110, value=dob[2])
        
        job_in = ft.Dropdown(label="المهنة", value=user_data.get("job"), options=[
            ft.dropdown.Option("كاسب"), ft.dropdown.Option("موظف"),
            ft.dropdown.Option("عسكري - دفاع"), ft.dropdown.Option("عسكري - داخلية"), ft.dropdown.Option("عسكري - حشد شعبي")
        ])
        
        address_in = ft.TextField(label="عنوان السكن", icon=ft.Icons.HOME, value=user_data.get("address", ""))
        mark_in = ft.TextField(label="أقرب نقطة دالة", icon=ft.Icons.LOCATION_ON, value=user_data.get("landmark", ""))
        blood_in = ft.Dropdown(label="الفصيلة", value=user_data.get("blood"), options=[ft.dropdown.Option(f) for f in ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]])

        def save(e):
            data = {
                "name": name_in.value, "mother": mother_in.value, "id_card": id_in.value, "phone": phone_in.value,
                "gender": gender_in.value, "dob": f"{day_in.value}/{month_in.value}/{year_in.value}",
                "job": job_in.value, "address": address_in.value, "landmark": mark_in.value, "blood": blood_in.value
            }
            # الحفظ المحلي
            if storage: storage.set("user_info", data)
            
            # الحفظ السحابي في Firebase
            cloud_success = save_to_firebase(data)
            
            if cloud_success:
                page.snack_bar = ft.SnackBar(ft.Text("تم المزامنة مع السحابة بنجاح"), bgcolor="green")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("تم الحفظ محلياً (لا يوجد اتصال سحابي)"), bgcolor="orange")
            
            page.snack_bar.open = True
            show_dashboard_view(data)

        page.add(ft.ListView(expand=True, padding=20, spacing=15, controls=[
            name_in, mother_in, id_in, phone_in, gender_in,
            ft.Column([ft.Text("تاريخ التولد:"), ft.Row([day_in, month_in, year_in])]),
            job_in, address_in, mark_in, blood_in,
            ft.FilledButton("حفظ البيانات والدخول", bgcolor="green", on_click=save)
        ]))

    # --- 3. الواجهة الرئيسية (بياناتي + إشعارات + فوائد) ---
    def show_dashboard_view(data_from_save=None):
        page.clean()
        user_data = data_from_save if data_from_save else (storage.get("user_info") if storage else {})
        
        def get_profile():
            details = [
                (ft.Icons.PERSON, "الاسم", user_data.get("name")),
                (ft.Icons.PERSON_OUTLINE, "اسم الأم", user_data.get("mother")),
                (ft.Icons.FINGERPRINT, "البطاقة الموحدة", user_data.get("id_card")),
                (ft.Icons.PHONE, "الهاتف", user_data.get("phone")),
                (ft.Icons.MALE, "الجنس", user_data.get("gender")),
                (ft.Icons.CAKE, "التولد", user_data.get("dob")),
                (ft.Icons.WORK, "المهنة", user_data.get("job")),
                (ft.Icons.HOME, "السكن", user_data.get("address")),
                (ft.Icons.LOCATION_ON, "نقطة دالة", user_data.get("landmark")),
            ]
            return ft.ListView(expand=True, padding=10, controls=[
                ft.Container(
                    padding=15, bgcolor=ft.Colors.RED_50, border_radius=15,
                    content=ft.Column([
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=70, color="red"),
                        ft.Text(user_data.get("name", ""), size=20, weight="bold"),
                        ft.Text(f"فصيلة الدم: {user_data.get('blood', '')}", size=18, color="red", weight="bold"),
                        ft.Divider(),
                        *[ft.ListTile(leading=ft.Icon(icon), title=ft.Text(f"{label}: {val}")) for icon, label, val in details],
                        ft.TextButton("تعديل البيانات الشخصية", icon=ft.Icons.EDIT, on_click=lambda _: show_registration_view()),
                        ft.TextButton("تسجيل الخروج", icon=ft.Icons.LOGOUT, icon_color="red", on_click=lambda _: (storage.remove("user_info"), show_login_view()))
                    ], horizontal_alignment="center")
                )
            ])

        def get_notifications():
            return ft.ListView(expand=True, padding=15, controls=[
                ft.Text("مركز الإشعارات", size=22, weight="bold"),
                ft.Divider(),
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.REPORT_PROBLEM, color="white"),
                        title=ft.Text("حالة طارئة في المشفى العام", color="white", weight="bold"),
                        subtitle=ft.Text("مطلوب متبرعين فصيلة A+ فوراً", color="white")
                    ), bgcolor=ft.Colors.RED_800, border_radius=12, margin=ft.margin.only(bottom=10)
                ),
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.INFO_OUTLINE, color="white"),
                        title=ft.Text("تحديث المخزون", color="white"),
                        subtitle=ft.Text("نقص حاد في فصائل O- و B+", color="white")
                    ), bgcolor=ft.Colors.BLUE_800, border_radius=12
                ),
            ])

        def get_benefits():
            benefits_list = [
                ("تنشيط النخاع العظمي", "لإنتاج خلايا دم جديدة."),
                ("تقليل الحديد المترسب", "يحمي القلب والكبد."),
                ("تقليل مخاطر الجلطات", "يحسن تدفق الدم."),
                ("فحص طبي مجاني", "اطمئنان دوري على صحتك."),
                ("حرق السعرات", "يساعد في التخلص من 650 سعرة."),
                ("إنقاذ الأرواح", "تبرعك ينقذ حياة 3 أشخاص."),
                ("تحسين المزاج", "العطاء يقلل التوتر."),
            ]
            return ft.ListView(expand=True, padding=15, controls=[
                ft.Text("فوائد التبرع بالدم", size=22, weight="bold", color="red"),
                ft.Divider(),
                *[ft.ListTile(leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="green"), title=ft.Text(t), subtitle=ft.Text(s)) for t, s in benefits_list]
            ])

        content_area = ft.Container(content=get_profile(), expand=True)

        def nav_change(e):
            if e.control.selected_index == 0: content_area.content = get_profile()
            elif e.control.selected_index == 1: content_area.content = get_notifications()
            elif e.control.selected_index == 2: content_area.content = get_benefits()
            page.update()

        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="بياناتي"),
                ft.NavigationBarDestination(icon=ft.Icons.NOTIFICATIONS, label="إشعارات"),
                ft.NavigationBarDestination(icon=ft.Icons.HEALTH_AND_SAFETY, label="فوائد"),
            ], on_change=nav_change, selected_index=0
        )
        page.add(content_area)

    if storage and storage.contains_key("user_info"): show_dashboard_view()
    else: show_login_view()

ft.app(target=main) # تم تغيير run إلى app لضمان التوافقية
