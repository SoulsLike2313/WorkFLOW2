import streamlit as st
import uuid

st.set_page_config(page_title="Cortex Progress", page_icon="⚡", layout="wide")


st.markdown(
    """
    <style>
    :root {
        --rz-bg: #060a06;
        --rz-panel: #0b120b;
        --rz-panel-2: #101810;
        --rz-neon: #66ff00;
        --rz-neon-soft: #3cbd12;
        --rz-text: #e9ffe0;
        --rz-muted: #8fa88a;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% -10%, #1c4010 0%, transparent 35%),
            radial-gradient(circle at 90% 0%, #173f0f 0%, transparent 30%),
            var(--rz-bg);
        color: var(--rz-text);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
    }

    .hero {
        border: 1px solid #20461a;
        background: linear-gradient(130deg, #0b140b 0%, #121d12 55%, #0f180f 100%);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 0 0 1px #163015 inset, 0 0 28px rgba(102, 255, 0, 0.08);
        margin-bottom: 0.9rem;
    }

    .hero h1 {
        margin: 0;
        letter-spacing: 0.08em;
        font-weight: 800;
        color: var(--rz-neon);
        text-shadow: 0 0 10px rgba(102, 255, 0, 0.45);
        font-size: 1.8rem;
    }

    .hero p {
        margin: 0.35rem 0 0 0;
        color: var(--rz-muted);
        font-size: 0.95rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #1f4d1a;
        border-radius: 14px;
        background: linear-gradient(180deg, #0c120c 0%, #101810 100%);
        padding: 0.65rem 0.9rem;
        box-shadow: 0 0 18px rgba(60, 189, 18, 0.14);
    }

    div[data-testid="stMetric"] label {
        color: #9fbe97 !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--rz-neon);
        text-shadow: 0 0 10px rgba(102, 255, 0, 0.35);
    }

    div[data-testid="stForm"] {
        border: 1px solid #1f4d1a;
        border-radius: 14px;
        background: linear-gradient(180deg, #0c120c 0%, #111a11 100%);
        padding: 0.85rem 0.9rem 0.25rem;
        margin-top: 0.25rem;
    }

    .row-head {
        margin-top: 0.55rem;
        border: 1px solid #214a1a;
        border-radius: 12px;
        background: #0d160d;
        padding: 0.5rem 0.7rem;
        font-weight: 700;
        color: #c8f0be;
    }

    .task-row {
        margin-top: 0.42rem;
        border: 1px solid #1b3f16;
        border-radius: 12px;
        background: linear-gradient(180deg, #0b120b 0%, #0f170f 100%);
        padding: 0.38rem 0.6rem;
    }

    .badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.18rem 0.6rem;
        font-weight: 700;
        font-size: 0.82rem;
    }

    .badge-done {
        background: rgba(102, 255, 0, 0.12);
        border: 1px solid rgba(102, 255, 0, 0.38);
        color: #99ff57;
    }

    .badge-progress {
        background: rgba(255, 189, 89, 0.14);
        border: 1px solid rgba(255, 189, 89, 0.36);
        color: #ffd27a;
    }

    .badge-todo {
        background: rgba(170, 179, 170, 0.14);
        border: 1px solid rgba(170, 179, 170, 0.35);
        color: #c6d0c6;
    }

    .cat-chip {
        display: inline-block;
        border-radius: 999px;
        padding: 0.12rem 0.56rem;
        background: rgba(102, 255, 0, 0.1);
        border: 1px solid rgba(102, 255, 0, 0.28);
        color: #b5ff8a;
        font-weight: 600;
        font-size: 0.82rem;
    }

    div[data-baseweb="slider"] > div > div {
        background-color: #274f24 !important;
    }

    div[data-baseweb="slider"] [role="slider"] {
        background-color: var(--rz-neon) !important;
        border: 2px solid #143f0d !important;
        box-shadow: 0 0 10px rgba(102, 255, 0, 0.5) !important;
    }

    .stButton > button, .stForm button {
        border: 1px solid #2f6e22;
        border-radius: 10px;
        background: linear-gradient(180deg, #1f5a16 0%, #18460f 100%);
        color: #e8ffd6;
        font-weight: 700;
    }

    .stButton > button:hover, .stForm button:hover {
        border-color: #66ff00;
        color: #ffffff;
        box-shadow: 0 0 16px rgba(102, 255, 0, 0.35);
    }

    .stTextInput > div > div > input {
        background-color: #0b120b;
        color: #e9ffe0;
        border: 1px solid #285a1f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {
            "id": str(uuid.uuid4()),
            "title": "Изучить основы Python",
            "category": "Обучение",
            "status": "В процессе",
            "progress": 60,
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Подготовить квартальный отчет",
            "category": "Работа",
            "status": "Готово",
            "progress": 100,
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Записаться в спортзал",
            "category": "Личное",
            "status": "К выполнению",
            "progress": 0,
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Прочитать книгу по дизайну",
            "category": "Обучение",
            "status": "В процессе",
            "progress": 25,
        },
    ]


def add_task(title, category):
    if title.strip():
        st.session_state.tasks.append(
            {
                "id": str(uuid.uuid4()),
                "title": title.strip(),
                "category": category.strip() if category.strip() else "Без категории",
                "status": "К выполнению",
                "progress": 0,
            }
        )


def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]


def on_progress_change(task_id):
    new_progress = st.session_state[f"slider_{task_id}"]
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["progress"] = new_progress
            if new_progress == 0:
                task["status"] = "К выполнению"
            elif new_progress == 100:
                task["status"] = "Готово"
            else:
                task["status"] = "В процессе"
            break


def status_badge(status):
    if status == "Готово":
        return '<span class="badge badge-done">✅ ГОТОВО</span>'
    if status == "В процессе":
        return '<span class="badge badge-progress">⏳ В ПРОЦЕССЕ</span>'
    return '<span class="badge badge-todo">⚪ К ВЫПОЛНЕНИЮ</span>'


st.markdown(
    """
    <div class="hero">
      <h1>CORTEX TASK CONTROL</h1>
      <p>Неоновая панель управления задачами и прогрессом в стиле gaming performance tools.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


total_tasks = len(st.session_state.tasks)
completed_tasks = sum(1 for t in st.session_state.tasks if t["progress"] == 100)
avg_progress = (
    sum(t["progress"] for t in st.session_state.tasks) // total_tasks if total_tasks > 0 else 0
)

col1, col2 = st.columns(2)
with col1:
    st.metric("⚡ Выполнено / Всего", f"{completed_tasks} / {total_tasks}")
with col2:
    st.metric("📈 Средний прогресс", f"{avg_progress}%")

with st.form("add_task_form", clear_on_submit=True):
    col_title, col_cat, col_btn = st.columns([3, 2, 1])

    with col_title:
        new_title = st.text_input("Что нужно сделать?", placeholder="Введите название задачи...")
    with col_cat:
        new_category = st.text_input("Категория", placeholder="Например: Работа")
    with col_btn:
        st.write("")
        st.write("")
        submitted = st.form_submit_button("+ Добавить", use_container_width=True)

    if submitted and new_title:
        add_task(new_title, new_category)
        st.rerun()

if not st.session_state.tasks:
    st.info("Список задач пуст. Добавьте первую задачу выше.")
else:
    st.markdown(
        """
        <div class="row-head">
          Статус | Задача | Категория | Прогресс | Действия
        </div>
        """,
        unsafe_allow_html=True,
    )

    for task in st.session_state.tasks:
        st.markdown('<div class="task-row">', unsafe_allow_html=True)
        col_stat, col_title, col_cat, col_prog, col_del = st.columns([1.8, 3, 1.7, 3, 1], vertical_alignment="center")

        col_stat.markdown(status_badge(task["status"]), unsafe_allow_html=True)

        if task["status"] == "Готово":
            col_title.markdown(f"~~{task['title']}~~")
        else:
            col_title.markdown(f"**{task['title']}**")

        col_cat.markdown(f'<span class="cat-chip">{task["category"]}</span>', unsafe_allow_html=True)

        col_prog.slider(
            "Прогресс",
            min_value=0,
            max_value=100,
            step=5,
            value=task["progress"],
            key=f"slider_{task['id']}",
            on_change=on_progress_change,
            args=(task["id"],),
            label_visibility="collapsed",
        )

        if col_del.button("🗑", key=f"del_{task['id']}", help="Удалить задачу"):
            delete_task(task["id"])
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
