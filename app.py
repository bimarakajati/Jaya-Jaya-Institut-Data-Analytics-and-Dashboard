import streamlit as st
import pandas as pd
import joblib
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Prediksi Performa Akademik Mahasiswa",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎓"
)

# --- Configuration and Loading ---
MODEL_DIR = 'model/'
MODEL_PATH = os.path.join(MODEL_DIR, 'dropout_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'dropout_scaler.pkl')
FEATURES_PATH = os.path.join(MODEL_DIR, 'features_list.pkl') # Columns of X_encoded
ENCODER_PATH = os.path.join(MODEL_DIR, 'target_encoder.pkl')

@st.cache_resource # Cache resource for efficiency (prevents reloading on every interaction)
def load_artifacts():
    """Loads the model, scaler, features list, and target encoder."""
    # Check for file existence first, to avoid Streamlit commands before set_page_config if files are missing
    if not all([os.path.exists(p) for p in [MODEL_PATH, SCALER_PATH, FEATURES_PATH, ENCODER_PATH]]):
        return None, None, None, None
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        features_list = joblib.load(FEATURES_PATH) # These are X_encoded.columns
        target_encoder = joblib.load(ENCODER_PATH)
        return model, scaler, features_list, target_encoder
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat model: {e}")
        return None, None, None, None

model, scaler, features_list, target_encoder = load_artifacts()

# --- Mappings for Selectboxes (from your data description) ---
# These help make the UI more user-friendly.
marital_status_options = {
    1: "Lajang", 2: "Menikah", 3: "Duda/Janda", 4: "Bercerai", 5: "Serikat Faktual", 6: "Pisah Secara Hukum"
}
application_mode_options = {
    1: "Fase 1 - Kontingen Umum", 2: "Peraturan No. 612/93", 5: "Fase 1 - Kontingen Khusus (Pulau Azores)",
    7: "Pemegang Gelar Pendidikan Tinggi Lain", 10: "Peraturan No. 854-B/99", 15: "Mahasiswa Internasional (Sarjana)",
    16: "Fase 1 - Kontingen Khusus (Pulau Madeira)", 17: "Fase 2 - Kontingen Umum", 18: "Fase 3 - Kontingen Umum",
    26: "Peraturan No. 533-A/99, butir b2) (Rencana Berbeda)", 27: "Peraturan No. 533-A/99, butir b3 (Institusi Lain)",
    39: "Usia di atas 23 tahun", 42: "Transfer", 43: "Ganti Program Studi", 44: "Pemegang Diploma Spesialisasi Teknologi",
    51: "Ganti Institusi/Program Studi", 53: "Pemegang Diploma Siklus Pendek", 57: "Ganti Institusi/Program Studi (Internasional)"
}
course_options = {
    33: "Teknologi Produksi Biofuel", 171: "Desain Animasi dan Multimedia", 8014: "Pelayanan Sosial (kelas malam)",
    9003: "Agronomi", 9070: "Desain Komunikasi", 9085: "Keperawatan Hewan", 9119: "Teknik Informatika",
    9130: "Ilmu Kuda", 9147: "Manajemen", 9238: "Pelayanan Sosial", 9254: "Pariwisata", 9500: "Keperawatan",
    9556: "Kebersihan Mulut", 9670: "Manajemen Periklanan dan Pemasaran", 9773: "Jurnalisme dan Komunikasi",
    9853: "Pendidikan Dasar", 9991: "Manajemen (kelas malam)"
}
attendance_options = {1: "Pagi", 0: "Malam"}
prev_qual_options = {
    1: "Pendidikan menengah", 2: "Pendidikan tinggi - sarjana", 3: "Pendidikan tinggi - gelar",
    4: "Pendidikan tinggi - magister", 5: "Pendidikan tinggi - doktor", 6: "Sedang menempuh pendidikan tinggi",
    9: "Kelas 12 - belum selesai", 10: "Kelas 11 - belum selesai",
    12: "Lainnya - kelas 11", 14: "Kelas 10", 15: "Kelas 10 - belum selesai",
    19: "Pendidikan dasar siklus ke-3 (kelas 9/10/11) atau setara", 38: "Pendidikan dasar siklus ke-2 (kelas 6/7/8) atau setara",
    39: "Kursus spesialisasi teknologi", 40: "Pendidikan tinggi - gelar (siklus 1)",
    42: "Kursus teknis profesional tinggi", 43: "Pendidikan tinggi - magister (siklus 2)"
}
nationality_options = {
    1: "Portugis", 2: "Jerman", 6: "Spanyol", 11: "Italia", 13: "Belanda", 14: "Inggris", 17: "Lituania",
    21: "Angola", 22: "Tanjung Verde", 24: "Guinea", 25: "Mozambik", 26: "Sao Tome dan Principe", 32: "Turki",
    41: "Brasil", 62: "Rumania", 100: "Moldova (Republik)", 101: "Meksiko", 103: "Ukraina",
    105: "Rusia", 108: "Kuba", 109: "Kolombia"
}
# For Parent's Qualifications/Occupations, which have many categories,
# providing full selectboxes would be ideal. For this example, we use number_input
# and expect the user to know the codes.
# See your data dictionary for the full list of codes.
yes_no_options = {1: "Ya", 0: "Tidak"}
gender_options = {1: "Laki-laki", 0: "Perempuan"}

# --- Streamlit UI ---
st.title("🎓 Prediksi Performa Akademik Mahasiswa")
st.markdown("""
Selamat datang! Aplikasi ini dapat memprediksi kemungkinan hasil akademik mahasiswa: **Dropout (Putus Kuliah)**, **Enrolled (Masih Kuliah)**, atau **Graduate (Lulus)**.
Prediksi didasarkan pada informasi yang biasanya tersedia saat pendaftaran dan performa akademik pada dua semester pertama.
Silakan isi detail mahasiswa di bawah ini.
""")

if model and scaler and features_list and target_encoder:
    with st.form("prediction_form"):
        st.header("👤 Informasi Mahasiswa")
        # Layout with columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Demografi & Latar Belakang")
            marital_status = st.selectbox("Status Pernikahan", options=list(marital_status_options.keys()), format_func=lambda x: f"{x} - {marital_status_options[x]}", help="Pilih status pernikahan mahasiswa.")
            age_at_enrollment = st.number_input("Usia Saat Masuk", min_value=15, max_value=70, value=20, step=1, help="Usia mahasiswa saat mendaftar.")
            # Nama kolom pada CSV adalah 'Nacionality'
            nacionality_key = st.selectbox("Kewarganegaraan", options=list(nationality_options.keys()), format_func=lambda x: f"{x} - {nationality_options[x]}", help="Kewarganegaraan mahasiswa.")
            gender = st.selectbox("Jenis Kelamin", options=list(gender_options.keys()), format_func=lambda x: gender_options[x], help="Jenis kelamin mahasiswa.")
            displaced = st.selectbox("Terdampak (Berasal dari wilayah berbeda?)", options=list(yes_no_options.keys()), format_func=lambda x: yes_no_options[x])
            international = st.selectbox("Mahasiswa Internasional", options=list(yes_no_options.keys()), format_func=lambda x: yes_no_options[x])
            educational_special_needs = st.selectbox("Kebutuhan Khusus Pendidikan", options=list(yes_no_options.keys()), format_func=lambda x: yes_no_options[x])

        with col2:
            st.subheader("Aplikasi & Pendidikan Sebelumnya")
            application_mode = st.selectbox("Mode Aplikasi", options=list(application_mode_options.keys()), format_func=lambda x: f"{x} - {application_mode_options.get(x, 'Tidak diketahui')}", help="Metode pendaftaran yang digunakan oleh mahasiswa.")
            application_order = st.number_input("Urutan Aplikasi", min_value=0, max_value=9, value=1, step=1, help="0 untuk pilihan pertama, hingga 9 untuk pilihan terakhir.")
            course = st.selectbox("Program Studi", options=list(course_options.keys()), format_func=lambda x: f"{x} - {course_options.get(x, 'Tidak diketahui')}", help="Program studi yang diambil mahasiswa.")
            previous_qualification = st.selectbox("Kualifikasi Sebelumnya", options=list(prev_qual_options.keys()), format_func=lambda x: f"{x} - {prev_qual_options.get(x, 'Tidak diketahui')}", help="Kualifikasi sebelum pendaftaran ini.")
            previous_qualification_grade = st.number_input("Nilai Kualifikasi Sebelumnya", min_value=0.0, max_value=200.0, value=120.0, step=0.1, help="Nilai untuk kualifikasi sebelumnya (skala 0-200).")
            admission_grade = st.number_input("Nilai Masuk", min_value=0.0, max_value=200.0, value=120.0, step=0.1, help="Nilai masuk untuk program studi saat ini (skala 0-200).")
            daytime_evening_attendance = st.selectbox("Kehadiran Pagi/Malam", options=list(attendance_options.keys()), format_func=lambda x: attendance_options[x])

        with col3:
            st.subheader("Orang Tua & Keuangan")
            mothers_qualification = st.number_input("Kualifikasi Ibu (Kode)", min_value=1, max_value=44, value=19, help="Masukkan kode numerik untuk kualifikasi ibu (lihat data dictionary).")
            fathers_qualification = st.number_input("Kualifikasi Ayah (Kode)", min_value=1, max_value=44, value=19, help="Masukkan kode numerik untuk kualifikasi ayah (lihat data dictionary).")
            mothers_occupation = st.number_input("Pekerjaan Ibu (Kode)", min_value=0, max_value=194, value=9, help="Masukkan kode numerik untuk pekerjaan ibu (lihat data dictionary).")
            fathers_occupation = st.number_input("Pekerjaan Ayah (Kode)", min_value=0, max_value=195, value=9, help="Masukkan kode numerik untuk pekerjaan ayah (lihat data dictionary).")
            debtor = st.selectbox("Debitur (Memiliki tunggakan di institusi?)", options=list(yes_no_options.keys()), format_func=lambda x: yes_no_options[x])
            tuition_fees_up_to_date = st.selectbox("Biaya Kuliah Sudah Lunas", options=list(yes_no_options.keys()), format_func=lambda x: yes_no_options[x])
            scholarship_holder = st.selectbox("Penerima Beasiswa", options=list(yes_no_options.keys()), format_func=lambda x: yes_no_options[x])

        st.header("📚 Performa Akademik - Semester 1")
        col4, col5, col6 = st.columns(3)
        with col4:
            curricular_units_1st_sem_credited = st.number_input("Semester 1: Mata Kuliah Diakui", min_value=0, max_value=30, value=0, step=1)
            curricular_units_1st_sem_enrolled = st.number_input("Semester 1: Mata Kuliah Diambil", min_value=0, max_value=30, value=6, step=1)
        with col5:
            curricular_units_1st_sem_evaluations = st.number_input("Semester 1: Evaluasi Mata Kuliah", min_value=0, max_value=50, value=6, step=1, help="Jumlah evaluasi yang dilakukan.")
            curricular_units_1st_sem_approved = st.number_input("Semester 1: Mata Kuliah Lulus", min_value=0, max_value=30, value=5, step=1)
        with col6:
            curricular_units_1st_sem_grade = st.number_input("Semester 1: Rata-rata Nilai", min_value=0.0, max_value=20.0, value=12.0, step=0.1, help="Rata-rata nilai untuk mata kuliah yang lulus (skala 0-20).")
            curricular_units_1st_sem_without_evaluations = st.number_input("Semester 1: Mata Kuliah Tanpa Evaluasi", min_value=0, max_value=20, value=0, step=1)

        st.header("📖 Performa Akademik - Semester 2")
        col7, col8, col9 = st.columns(3)
        with col7:
            curricular_units_2nd_sem_credited = st.number_input("Semester 2: Mata Kuliah Diakui", min_value=0, max_value=30, value=0, step=1)
            curricular_units_2nd_sem_enrolled = st.number_input("Semester 2: Mata Kuliah Diambil", min_value=0, max_value=30, value=6, step=1)
        with col8:
            curricular_units_2nd_sem_evaluations = st.number_input("Semester 2: Evaluasi Mata Kuliah", min_value=0, max_value=50, value=6, step=1, help="Jumlah evaluasi yang dilakukan.")
            curricular_units_2nd_sem_approved = st.number_input("Semester 2: Mata Kuliah Lulus", min_value=0, max_value=30, value=5, step=1)
        with col9:
            curricular_units_2nd_sem_grade = st.number_input("Semester 2: Rata-rata Nilai", min_value=0.0, max_value=20.0, value=12.0, step=0.1, help="Rata-rata nilai untuk mata kuliah yang lulus (skala 0-20).")
            curricular_units_2nd_sem_without_evaluations = st.number_input("Semester 2: Mata Kuliah Tanpa Evaluasi", min_value=0, max_value=20, value=0, step=1)

        st.header("📊 Konteks Sosial Ekonomi")
        col10, col11, col12 = st.columns(3)
        with col10:
            unemployment_rate = st.number_input("Tingkat Pengangguran (%)", min_value=0.0, max_value=50.0, value=10.0, step=0.1)
        with col11:
            inflation_rate = st.number_input("Tingkat Inflasi (%)", min_value=-5.0, max_value=10.0, value=1.0, step=0.1)
        with col12:
            gdp = st.number_input("Pertumbuhan PDB (%)", min_value=-10.0, max_value=10.0, value=1.0, step=0.1)
            
        submitted = st.form_submit_button("🚀 Prediksi Status Mahasiswa")

        if submitted:
            # Consolidate inputs into a dictionary.
            input_data = {
                'Marital_status': marital_status,
                'Application_mode': application_mode,
                'Application_order': application_order,
                'Course': course,
                'Daytime_evening_attendance': daytime_evening_attendance,
                'Previous_qualification': previous_qualification,
                'Previous_qualification_grade': previous_qualification_grade,
                'Nacionality': nacionality_key, # CSV column name
                'Mothers_qualification': mothers_qualification,
                'Fathers_qualification': fathers_qualification,
                'Mothers_occupation': mothers_occupation,
                'Fathers_occupation': fathers_occupation,
                'Admission_grade': admission_grade,
                'Displaced': displaced,
                'Educational_special_needs': educational_special_needs,
                'Debtor': debtor,
                'Tuition_fees_up_to_date': tuition_fees_up_to_date,
                'Gender': gender,
                'Scholarship_holder': scholarship_holder,
                'Age_at_enrollment': age_at_enrollment,
                'International': international,
                'Curricular_units_1st_sem_credited': curricular_units_1st_sem_credited,
                'Curricular_units_1st_sem_enrolled': curricular_units_1st_sem_enrolled,
                'Curricular_units_1st_sem_evaluations': curricular_units_1st_sem_evaluations,
                'Curricular_units_1st_sem_approved': curricular_units_1st_sem_approved,
                'Curricular_units_1st_sem_grade': curricular_units_1st_sem_grade,
                'Curricular_units_1st_sem_without_evaluations': curricular_units_1st_sem_without_evaluations,
                'Curricular_units_2nd_sem_credited': curricular_units_2nd_sem_credited,
                'Curricular_units_2nd_sem_enrolled': curricular_units_2nd_sem_enrolled,
                'Curricular_units_2nd_sem_evaluations': curricular_units_2nd_sem_evaluations,
                'Curricular_units_2nd_sem_approved': curricular_units_2nd_sem_approved,
                'Curricular_units_2nd_sem_grade': curricular_units_2nd_sem_grade,
                'Curricular_units_2nd_sem_without_evaluations': curricular_units_2nd_sem_without_evaluations,
                'Unemployment_rate': unemployment_rate,
                'Inflation_rate': inflation_rate,
                'GDP': gdp
            }
            
            input_df = pd.DataFrame([input_data])
            
            try:
                input_df_ordered = input_df[features_list] 
            except KeyError as e:
                st.error(
                    f"Feature mismatch error during column ordering: {e}. "
                    f"This means the input fields might not perfectly match the expected features. "
                    f"Expected features are: {features_list}"
                )
                st.stop() 

            try:
                input_scaled = scaler.transform(input_df_ordered)
            except Exception as e:
                st.error(f"Error during scaling: {e}")
                st.stop()
            
            try:
                prediction_encoded = model.predict(input_scaled)
                prediction_proba = model.predict_proba(input_scaled)
            except Exception as e:
                st.error(f"Error during prediction: {e}")
                st.stop()

            prediction_label = target_encoder.inverse_transform(prediction_encoded)[0]
            
            st.subheader("🎯 Hasil Prediksi:")
            if prediction_label == "Dropout":
                st.error(f"Status yang Diprediksi: **{prediction_label}** 😟")
            elif prediction_label == "Graduate":
                st.success(f"Status yang Diprediksi: **{prediction_label}** 🎉")
            else: # Enrolled
                st.info(f"Status yang Diprediksi: **{prediction_label}** 📚")

            st.subheader("Tingkat Keyakinan (Probabilitas):")
            proba_df = pd.DataFrame(prediction_proba, columns=target_encoder.classes_)
            st.write(proba_df.style.format("{:.2%}"))

else:
    # This error will be displayed if any of the model artifacts are missing.
    st.error(
        "Satu atau lebih file model tidak ditemukan! 😟 "
        "Pastikan file 'dropout_model.pkl', 'dropout_scaler.pkl', "
        "'features_list.pkl', dan 'target_encoder.pkl' sudah tersedia di direktori 'model/'."
    )

st.sidebar.header("ℹ️ Tentang Aplikasi Ini")
st.sidebar.info("""
Aplikasi ini menggunakan model machine learning [Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) untuk memprediksi hasil akademik mahasiswa.

**Petunjuk Penggunaan:**
1.  Isi semua kolom input di panel utama.
2.  Klik tombol "🚀 Prediksi Status Mahasiswa".
3.  Hasil prediksi dan tingkat kepercayaan akan ditampilkan.
""")

st.sidebar.markdown("### ⚠️ Informasi Tambahan")
st.sidebar.warning("""
**File yang diperlukan (di direktori 'model/'):**
- dropout_model.pkl (Model Random Forest yang sudah dilatih)
- dropout_scaler.pkl (StandardScaler yang sudah fit)
- features_list.pkl (Daftar nama fitur yang digunakan saat pelatihan)
- target_encoder.pkl (LabelEncoder yang sudah fit untuk variabel target)
""")

st.sidebar.markdown("---")
st.sidebar.markdown("👉 Created by [bimarakajati](https://www.dicoding.com/users/bimarakajati)")