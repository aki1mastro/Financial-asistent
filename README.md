# 💰 ФинДиректор

Личный финансовый дневник с Firebase базой данных и Streamlit админкой.

---

## 🚀 Установка и настройка

### 1. Создай Firebase проект
1. Зайди на https://console.firebase.google.com
2. **Add project** → название: `findirektor`
3. Включи **Firestore Database** → Create database → Start in test mode
4. Перейди в **Project Settings** (⚙️)

### 2. Получи конфиг для сайта (frontend)
1. Project Settings → **Your Apps** → Web app (</>) → Register
2. Скопируй `firebaseConfig` объект
3. Вставь в файл `firebase-config.js`

### 3. Получи ключ для админки (backend)
1. Project Settings → **Service Accounts** → Generate new private key
2. Сохрани файл как `serviceAccountKey.json` в папку проекта
3. ⚠️ Этот файл НИКОГДА не заливать на GitHub!

### 4. Залей на GitHub Pages
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/ТВО_ИМЯUSERNAME/findirektor.git
git push -u origin main
```
Потом: Settings → Pages → Source: main → Save

### 5. Запусти Streamlit админку локально
```bash
pip install -r requirements.txt
streamlit run web_admin.py
# или двойной клик на run_admin.bat
```

---

## 📁 Структура проекта

```
findirektor/
├── index.html           # Главная страница (Firebase JS SDK)
├── style.css            # Стили
├── firebase-config.js   # Конфиг Firebase (заполни своими данными)
├── web_admin.py         # Streamlit панель управления
├── requirements.txt     # Python зависимости
├── run_admin.bat        # Запуск админки (Windows)
├── .gitignore           # serviceAccountKey.json исключён!
└── README.md
```

## 🗄️ Структура Firestore

Коллекция `expenses`:
```
{
  cat:      "food",              // ID категории
  amt:      15000,               // Сумма в тенге
  note:     "Продукты — Мясо",  // Заметка
  date:     "2026-04-01T...",   // ISO дата
  monthKey: "2026-3"            // Год-месяц (JS: 0-based)
}
```

## ⚠️ Важно

- `serviceAccountKey.json` содержит приватный ключ — **не заливать в Git!**
- Если случайно залил — сразу иди в Firebase → Service Accounts → Generate New Key
