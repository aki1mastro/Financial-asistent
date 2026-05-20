import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# --- НАСТРОЙКИ ---
KEY_PATH = "serviceAccountKey.json"

# --- ПОДКЛЮЧЕНИЕ К FIREBASE ---
@st.cache_resource
def init_firebase():
    if not os.path.exists(KEY_PATH):
        st.error(f"Не найден файл ключа: {KEY_PATH}")
        st.stop()
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(KEY_PATH)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        st.error(f"Ошибка подключения к Firebase: {e}")
        st.stop()

db = init_firebase()

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="ФинДиректор Admin", page_icon="💰", layout="wide")

st.title("💰 ФинДиректор — Панель управления")
st.markdown("---")

MONTHS = ['Январь','Февраль','Март','Апрель','Май','Июнь',
          'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']

CATS = {
    'food':      '🛒 Продукты',
    'cafe':      '☕ Кафе/Рестораны',
    'transport': '🚗 Транспорт',
    'housing':   '🏠 Жильё/ЖКХ',
    'health':    '💊 Здоровье',
    'entertain': '🎮 Развлечения',
    'gifts':     '🎁 Подарки/She',
    'credit':    '💳 Кредиты',
    'charity':   '🕌 Пожертвования',
    'family':    '👨‍👩‍👧 Семья/Родные',
    'fines':     '🚨 Штрафы',
    'other':     '💼 Прочее',
}

def fmt(n):
    return f"{int(n):,}".replace(',', ' ')

# --- ЗАГРУЗКА ДАННЫХ ---
@st.cache_data(ttl=30)
def load_expenses():
    docs = db.collection('expenses').stream()
    items = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    return items

# --- БОКОВАЯ ПАНЕЛЬ: ФИЛЬТРЫ ---
st.sidebar.header("🔍 Фильтры")
now = datetime.now()
sel_year  = st.sidebar.selectbox("Год",  [now.year - 1, now.year], index=1)
sel_month = st.sidebar.selectbox("Месяц", list(range(12)), index=now.month - 1, format_func=lambda i: MONTHS[i])
sel_cat   = st.sidebar.selectbox("Категория", ['Все'] + list(CATS.values()))

if st.sidebar.button("🔄 Обновить данные"):
    st.cache_data.clear()
    st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ ---
all_expenses = load_expenses()

# Фильтрация
month_key = f"{sel_year}-{sel_month}"
filtered = [e for e in all_expenses if e.get('monthKey') == month_key]
if sel_cat != 'Все':
    cat_id = next((k for k,v in CATS.items() if v == sel_cat), None)
    if cat_id:
        filtered = [e for e in filtered if e.get('cat') == cat_id]

# --- МЕТРИКИ ---
col1, col2, col3, col4 = st.columns(4)
total = sum(e.get('amt', 0) for e in filtered)
total_all = sum(e.get('amt', 0) for e in all_expenses)
months_count = len(set(e.get('monthKey','') for e in all_expenses))

col1.metric("💰 Итого за месяц",    f"{fmt(total)} тг")
col2.metric("📊 Записей за месяц",  len(filtered))
col3.metric("📅 Месяцев в базе",    months_count)
col4.metric("💾 Всего в базе",      f"{fmt(total_all)} тг")

st.markdown("---")

# --- ВКЛАДКИ ---
tab_list, tab_add, tab_stats = st.tabs(["📋 Список расходов", "➕ Добавить вручную", "📊 Статистика по месяцу"])

# === СПИСОК РАСХОДОВ ===
with tab_list:
    if not filtered:
        st.info(f"Нет расходов за {MONTHS[sel_month]} {sel_year}")
    else:
        # Сортировка по дате
        try:
            filtered_sorted = sorted(filtered, key=lambda x: x.get('date',''), reverse=True)
        except:
            filtered_sorted = filtered

        for item in filtered_sorted:
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
                date_str = ''
                try:
                    d = datetime.fromisoformat(item.get('date','').replace('Z',''))
                    date_str = d.strftime('%d.%m.%Y')
                except: pass

                cat_label = CATS.get(item.get('cat','other'), '💼 Прочее')
                c1.markdown(f"**{date_str}**")
                c2.markdown(f"{cat_label}  \n{item.get('note','—')}")
                c3.markdown(f"**{fmt(item.get('amt',0))} тг**")

                if c4.button("❌", key=f"del_{item['id']}"):
                    db.collection('expenses').document(item['id']).delete()
                    st.cache_data.clear()
                    st.toast("Запись удалена")
                    st.rerun()

        # Итого
        st.markdown("---")
        st.markdown(f"**Итого: {fmt(total)} тг** за {MONTHS[sel_month]} {sel_year} ({len(filtered)} записей)")

# === ДОБАВИТЬ ВРУЧНУЮ ===
with tab_add:
    st.subheader(f"Добавить расход за {MONTHS[sel_month]} {sel_year}")

    col_a, col_b = st.columns(2)
    with col_a:
        in_cat  = st.selectbox("Категория", list(CATS.keys()), format_func=lambda k: CATS[k])
        in_amt  = st.number_input("Сумма (тг)", min_value=0.0, step=100.0)
    with col_b:
        in_date = st.date_input("Дата", value=datetime(sel_year, sel_month+1, 1))
        in_note = st.text_input("Заметка")

    if st.button("💾 Сохранить в Firebase", type="primary", use_container_width=True):
        if in_amt > 0:
            d = datetime(in_date.year, in_date.month, in_date.day)
            mk = f"{d.year}-{d.month - 1}"  # JS месяцы 0-based
            data = {
                'cat':      in_cat,
                'amt':      float(in_amt),
                'note':     in_note,
                'date':     d.isoformat(),
                'monthKey': mk,
            }
            db.collection('expenses').add(data)
            st.cache_data.clear()
            st.success("✅ Запись добавлена!")
            st.rerun()
        else:
            st.warning("Введи сумму!")

# === СТАТИСТИКА ===
with tab_stats:
    if not filtered:
        st.info(f"Нет данных за {MONTHS[sel_month]} {sel_year}")
    else:
        # По категориям
        by_cat = {}
        for e in filtered:
            cat = e.get('cat','other')
            by_cat[cat] = by_cat.get(cat, 0) + e.get('amt', 0)

        st.subheader(f"Расходы по категориям — {MONTHS[sel_month]} {sel_year}")

        cats_sorted = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
        for cat_id, amount in cats_sorted:
            pct = amount / total * 100 if total else 0
            label = CATS.get(cat_id, '💼 Прочее')
            col_l, col_r = st.columns([4, 1])
            col_l.progress(pct/100, text=f"{label} — {fmt(amount)} тг")
            col_r.markdown(f"**{pct:.1f}%**")

        st.markdown("---")
        st.subheader("📅 Сравнение по всем месяцам")

        monthly = {}
        for e in all_expenses:
            mk = e.get('monthKey','')
            monthly[mk] = monthly.get(mk, 0) + e.get('amt', 0)

        for mk, amt in sorted(monthly.items()):
            try:
                parts = mk.split('-')
                y, m = int(parts[0]), int(parts[1])
                label = f"{MONTHS[m]} {y}"
            except:
                label = mk
            st.markdown(f"**{label}:** {fmt(amt)} тг")
