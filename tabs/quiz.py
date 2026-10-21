"""The Quiz tab: setup, questions, results."""

import math
import random

import streamlit as st

from core.settings import EXCEPTIONS, FAMILY_COLOURS, TRENDS
from core.data import PROPERTIES
from core.helpers import (
    colour_value, display_group, element_row_by_symbol, fmt_prop, iupac_name,
    option_name, pretty_config,
)


QUIZ_TOPICS = ["Periodic Trends", "Exceptions", "Blocks", "Families",
               "Configurations", "IUPAC Names"]

LEVELS = {"Easy": 20, "Medium": 36, "Hard": 86}

LEVEL_HELP = {
    "Easy": "Elements 1–20, hydrogen to calcium.",
    "Medium": "Elements 1–36, up to krypton.",
    "Hard": "Elements up to 86, plus the d- and f-blocks.",
}

QUIZ_COMPARE = {
    "Atomic Radius": "larger atomic radius",
    "Ionisation Enthalpy": "higher first ionisation enthalpy",
    "Electronegativity": "higher electronegativity",
    "Electron Gain Enthalpy": "more negative electron gain enthalpy",
}

EXCEPTION_PAIRS = [
    ("Ionisation Enthalpy", "Be", "B"), ("Ionisation Enthalpy", "N", "O"),
    ("Ionisation Enthalpy", "Mg", "Al"), ("Ionisation Enthalpy", "P", "S"),
    ("Electron Gain Enthalpy", "F", "Cl"), ("Atomic Radius", "Al", "Ga"),
    ("Electronegativity", "Al", "Ga"),
]


def wide_button(where, label, **kwargs):
    """A button that fills its column (works on newer and older Streamlit)."""
    try:
        return where.button(label, width="stretch", **kwargs)
    except TypeError:
        return where.button(label, use_container_width=True, **kwargs)


def level_limit(level, wide=False):
    return 103 if (wide and level == "Hard") else LEVELS[level]



def compare_question(a, b, prop_name, tail):
    p = PROPERTIES[prop_name]
    ca, cb = colour_value(a[p["col"]], p), colour_value(b[p["col"]], p)
    if ca is None or cb is None or abs(ca - cb) < 1e-9:
        return None
    win, lose = (a, b) if ca > cb else (b, a)
    options = [option_name(a), option_name(b)]
    random.shuffle(options)
    return dict(
        question=f"Which has the {QUIZ_COMPARE[prop_name]}?",
        options=options, answer=option_name(win),
        explanation=(f"{option_name(win)}: {fmt_prop(win[p['col']], prop_name)} vs "
                     f"{option_name(lose)}: {fmt_prop(lose[p['col']], prop_name)}. {tail}"))



def question_trends(df, level):
    pool = df[df["block"].isin(["s", "p"]) & (df["atomic_number"] <= level_limit(level))]
    props = [q for q in QUIZ_COMPARE if q in PROPERTIES]
    for _ in range(300):
        prop_name = random.choice(props)
        a = pool.sample(1).iloc[0]
        along = random.choice(["period", "group_id"])
        others = pool[(pool[along] == a[along]) & (pool["atomic_number"] != a["atomic_number"])]
        if others.empty:
            continue
        b = others.sample(1).iloc[0]
        across, down, _, _ = TRENDS[prop_name]
        if along == "period":
            tail = f"Both are in period {int(a['period'])}, and across a period it {across}."
        else:
            tail = f"Both are in group {int(a['group_id'])}, and down a group it {down}."
        for el in (a, b):
            if (prop_name, el["symbol"]) in EXCEPTIONS:
                tail += f" Watch out, {el['symbol']} is an exception: {EXCEPTIONS[(prop_name, el['symbol'])]}"
        q = compare_question(a, b, prop_name, tail)
        if q:
            return q
    return question_block(df, level)



def question_exception(df, level):
    limit = level_limit(level)
    pairs = [pr for pr in EXCEPTION_PAIRS if pr[0] in PROPERTIES]
    fitting = [pr for pr in pairs if all(element_row_by_symbol(df, s)["atomic_number"] <= limit
                                         for s in pr[1:])]
    prop_name, s1, s2 = random.choice(fitting or pairs)
    a, b = element_row_by_symbol(df, s1), element_row_by_symbol(df, s2)
    odd = s1 if (prop_name, s1) in EXCEPTIONS else s2
    q = compare_question(a, b, prop_name,
                         f"This breaks the usual trend. {EXCEPTIONS[(prop_name, odd)]}")
    return q or question_trends(df, level)



def question_block(df, level):
    el = df[df["atomic_number"] <= level_limit(level, wide=True)].sample(1).iloc[0]
    answer = f"{el['block']}-block"
    return dict(question=f"Which block is {option_name(el)} in?",
                options=["s-block", "p-block", "d-block", "f-block"], answer=answer,
                explanation=f"Its configuration is {pretty_config(el['electronic_configuration'])}, "
                            f"so it belongs to the {answer}.")



def question_family(df, level):
    pool = df[df["family"].isin(FAMILY_COLOURS) & (df["atomic_number"] <= level_limit(level, wide=True))]
    el = pool.sample(1).iloc[0]
    options = random.sample([f for f in FAMILY_COLOURS if f != el["family"]], 3) + [el["family"]]
    random.shuffle(options)
    return dict(question=f"Which family does {option_name(el)} belong to?",
                options=options, answer=el["family"],
                explanation=f"{el['name']} is in group {display_group(el['atomic_number'], el['group_id'])}, "
                            f"period {int(el['period'])}: one of the {el['family'].lower()}.")



def question_config(df, level):
    pool = df[df["atomic_number"] <= level_limit(level)]
    el = pool.sample(1).iloc[0]
    near = pool[((pool["atomic_number"] - el["atomic_number"]).abs() <= 4)
                & (pool["atomic_number"] != el["atomic_number"])]
    wrong = near.sample(min(3, len(near)))
    options = [option_name(w) for _, w in wrong.iterrows()] + [option_name(el)]
    random.shuffle(options)
    return dict(
        question=f"Which element has the configuration {pretty_config(el['electronic_configuration'])}?",
        options=options, answer=option_name(el),
        explanation=f"Count the electrons: this configuration holds {int(el['atomic_number'])}, "
                    f"which is the atomic number of {el['name']}.")



def question_iupac(df, level):
    z = random.randint(104, 130)
    answer, _, parts = iupac_name(z)
    wrong = set()
    while len(wrong) < 3:
        other = iupac_name(random.choice([z + 1, z - 1, z + 10, z - 10, z + 2, z - 2]))[0]
        if other != answer:
            wrong.add(other)
    options = list(wrong) + [answer]
    random.shuffle(options)
    return dict(question=f"What is the IUPAC temporary name for element {z}?",
                options=options, answer=answer,
                explanation=f"Read the digits {' '.join(str(z))} as {' + '.join(parts)} + ium = {answer}.")


QUESTION_MAKERS = {
    "Periodic Trends": question_trends,
    "Exceptions": question_exception,
    "Blocks": question_block,
    "Families": question_family,
    "Configurations": question_config,
    "IUPAC Names": question_iupac,
}


def build_quiz(df, settings):
    questions, seen = [], set()
    for _ in range(settings["count"] * 40):
        if len(questions) >= settings["count"]:
            break
        topic = random.choice(settings["topics"])
        q = QUESTION_MAKERS[topic](df, settings["level"])
        key = q["question"] + q["answer"]
        if key in seen:
            continue
        seen.add(key)
        q["topic"] = topic
        questions.append(q)
    return questions



def start_quiz(df, settings, questions=None):
    ss = st.session_state
    ss.quiz_settings = settings
    ss.quiz_questions = questions if questions is not None else build_quiz(df, settings)
    ss.quiz_index = 0
    ss.quiz_answers = []
    ss.quiz_choice = None
    ss.quiz_stage = "playing"
    ss.quiz_round = ss.get("quiz_round", 0) + 1
    ss.quiz_streak = 0



def start_from_setup(df):
    ss = st.session_state
    settings = dict(
        name=(ss.get("qs_name") or "").strip(),
        topics=ss.get("qs_topics") or QUIZ_TOPICS,
        level=ss.get("qs_level") or "Medium",
        count=ss.get("qs_count") or 10,
    )
    start_quiz(df, settings)



def start_from_setup_same(df):
    start_quiz(df, st.session_state.quiz_settings)



def answer_question(option):
    ss = st.session_state
    if ss.quiz_choice is not None:
        return
    q = ss.quiz_questions[ss.quiz_index]
    ss.quiz_choice = option
    correct = option == q["answer"]
    ss.quiz_answers.append(dict(q=q, chosen=option, correct=correct))
    ss.quiz_streak = ss.get("quiz_streak", 0) + 1 if correct else 0
    ss.quiz_best_streak = max(ss.get("quiz_best_streak", 0), ss.quiz_streak)



def finish_quiz():
    ss = st.session_state
    ss.quiz_stage = "done"
    answered = len(ss.quiz_answers)
    if answered:
        pct = 100 * sum(a["correct"] for a in ss.quiz_answers) / answered
        ss.quiz_best = max(ss.get("quiz_best", 0), pct)
        ss.quiz_rounds_played = ss.get("quiz_rounds_played", 0) + 1
        # Remember how you do in each topic across every round this session
        totals = ss.setdefault("topic_totals", {})
        for a in ss.quiz_answers:
            got, n = totals.get(a["q"]["topic"], (0, 0))
            totals[a["q"]["topic"]] = (got + a["correct"], n + 1)



def next_question():
    ss = st.session_state
    ss.quiz_index += 1
    ss.quiz_choice = None
    if ss.quiz_index >= len(ss.quiz_questions):
        finish_quiz()



def retry_mistakes(df):
    wrong = []
    for a in st.session_state.quiz_answers:
        if not a["correct"]:
            q = dict(a["q"])
            q["options"] = random.sample(q["options"], len(q["options"]))
            wrong.append(q)
    start_quiz(df, st.session_state.quiz_settings, questions=wrong)



def practise_topic(df, topic):
    settings = dict(st.session_state.quiz_settings)
    settings["topics"] = [topic]
    start_quiz(df, settings)



def back_to_setup():
    st.session_state.quiz_stage = "setup"



def quiz_setup(df):
    ss = st.session_state
    prev = ss.get("quiz_settings") or dict(name="", topics=QUIZ_TOPICS, level="Medium", count=10)
    ss.setdefault("qs_name", prev["name"])
    ss.setdefault("qs_topics", list(prev["topics"]))
    ss.setdefault("qs_level", prev["level"])
    ss.setdefault("qs_count", prev["count"])

    with st.container(key="card_quiz_setup"):
        st.markdown("### Test Yourself")
        st.caption("Pick what to practise. Every answer comes with an explanation, and at the "
                   "end you'll see which topics to work on.")
        st.text_input("Your Name (Optional)", key="qs_name", placeholder="So the quiz can cheer you on")
        if hasattr(st, "pills"):
            st.pills("Topics", QUIZ_TOPICS, selection_mode="multi", key="qs_topics")
        else:
            st.multiselect("Topics", QUIZ_TOPICS, key="qs_topics")
        level = st.radio("Level", list(LEVELS), horizontal=True, key="qs_level")
        st.caption(LEVEL_HELP.get(level or "Medium"))
        st.radio("Number of Questions", [5, 10, 20], horizontal=True, key="qs_count")
        wide_button(st, "Start Quiz", type="primary", on_click=start_from_setup, args=(df,))

    if ss.get("quiz_rounds_played"):
        st.caption(f"Rounds played this session: {ss.quiz_rounds_played} · "
                   f"Best score: {ss.quiz_best:.0f}%")



GREEN, RED = "#15803D", "#B91C1C"


def stat_chip(label, value, colour="#0F1B2D"):
    return (f"<div style='padding:8px 14px;border-radius:12px;background:#F4F6FA;"
            f"border:1px solid #E3E8F0'><div style='font-size:11px;color:#55627A;"
            f"text-transform:uppercase;letter-spacing:.06em'>{label}</div>"
            f"<div style='font-size:18px;font-weight:700;color:{colour}'>{value}</div></div>")


def answered_option(option, q, chosen):
    """How an option looks once you've answered: green if right, red if your wrong pick."""
    if option == q["answer"]:
        colour, bg, mark = GREEN, "rgba(21,128,61,0.10)", "✓"
    elif option == chosen:
        colour, bg, mark = RED, "rgba(185,28,28,0.08)", "✗"
    else:
        colour, bg, mark = "#55627A", "#F8FAFC", ""
    return (f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"min-height:52px;padding:0 16px;margin-bottom:10px;border-radius:12px;border:1.5px solid {colour};"
            f"background:{bg};color:{colour};font-weight:600'>"
            f"<span>{option}</span><span style='font-size:18px'>{mark}</span></div>")


def quiz_playing():
    ss = st.session_state
    total = len(ss.quiz_questions)
    if total == 0:
        st.warning("Couldn't make questions for those settings. Try adding more topics.")
        st.button("Change Settings", on_click=back_to_setup)
        return
    q = ss.quiz_questions[ss.quiz_index]
    score = sum(a["correct"] for a in ss.quiz_answers)
    name = ss.quiz_settings["name"]
    answered = ss.quiz_choice is not None

    if ss.quiz_index == 0 and total < ss.quiz_settings["count"] and not ss.quiz_answers:
        st.caption(f"Only {total} different questions exist for these settings, "
                   "so this round is shorter.")

    with st.container(key="card_quiz_question"):
        streak = ss.get("quiz_streak", 0)
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:10px;align-items:center;"
            "justify-content:space-between'>"
            f"<div><div style='font-size:13px;color:#55627A'>Question {ss.quiz_index + 1} of {total}"
            f"</div><div style='display:inline-block;margin-top:4px;padding:3px 10px;"
            f"border-radius:999px;background:#E6EDFD;color:#1D4ED8;font-size:12px;"
            f"font-weight:600'>{q['topic']}</div></div>"
            "<div style='display:flex;gap:8px'>"
            + stat_chip("Score", f"{score} / {len(ss.quiz_answers)}")
            + stat_chip("Streak", streak, "#E4572E" if streak >= 3 else "#0F1B2D")
            + "</div></div>",
            unsafe_allow_html=True)
        st.progress((ss.quiz_index + (1 if answered else 0)) / total)
        st.markdown(f"### {q['question']}")

        if not answered:
            cols = st.container(key="quiz_options").columns(2, gap="small")
            for i, option in enumerate(q["options"]):
                wide_button(cols[i % 2], option, key=f"q{ss.quiz_round}_{ss.quiz_index}_{i}",
                            on_click=answer_question, args=(option,))
        else:
            cols = st.columns(2, gap="small")
            for i, option in enumerate(q["options"]):
                cols[i % 2].markdown(answered_option(option, q, ss.quiz_choice),
                                     unsafe_allow_html=True)

            right = ss.quiz_choice == q["answer"]
            if right:
                cheer = random.choice(["Correct!", "Spot on!", "Nice!", "Exactly right!"])
                if streak >= 3:
                    cheer = f"{streak} in a row!"
                heading = f"{cheer}{' Well done, ' + name + '.' if name and streak >= 3 else ''}"
            else:
                heading = f"Not quite. The answer is {q['answer']}."
            colour = GREEN if right else RED
            st.markdown(
                f"<div class='pe-feedback' style='margin-top:6px;padding:14px 16px;border-radius:12px;"
                f"border-left:0;background:{'rgba(21,128,61,0.08)' if right else 'rgba(185,28,28,0.06)'}'>"
                f"<div style='font-weight:700;color:{colour};margin-bottom:4px'>{heading}</div>"
                f"<div style='font-size:15px;line-height:1.5'>{q['explanation']}</div></div>",
                unsafe_allow_html=True)
            last = ss.quiz_index + 1 >= total
            st.button("See My Results" if last else "Next Question →", type="primary",
                      on_click=next_question)

    st.button("End Quiz Now", on_click=finish_quiz, type="tertiary")


def quiz_results(df):
    ss = st.session_state
    answers = ss.quiz_answers
    name = ss.quiz_settings["name"]
    if not answers:
        st.info("You ended the quiz before answering anything.")
        st.button("Back to Quiz Settings", on_click=back_to_setup)
        return

    right = sum(a["correct"] for a in answers)
    pct = 100 * right / len(answers)
    if pct >= 90:
        headline, colour = "Outstanding", GREEN
    elif pct >= 70:
        headline, colour = "Great work", "#1D4ED8"
    elif pct >= 50:
        headline, colour = "Good effort", "#B45309"
    else:
        headline, colour = "Keep practising", RED

    stats = {}
    for a in answers:
        t = a["q"]["topic"]
        got, n = stats.get(t, (0, 0))
        stats[t] = (got + a["correct"], n + 1)

    # A ring that fills up to your score
    radius, circ = 52, 2 * math.pi * 52
    ring = (f"<svg width='132' height='132' viewBox='0 0 132 132' role='img' "
            f"aria-label='{pct:.0f} percent correct'>"
            f"<circle cx='66' cy='66' r='{radius}' fill='none' stroke='#E3E8F0' stroke-width='12'/>"
            f"<circle class='pe-ring' cx='66' cy='66' r='{radius}' fill='none' stroke='{colour}' stroke-width='12' "
            f"stroke-linecap='round' stroke-dasharray='{circ * pct / 100:.1f} {circ:.1f}' "
            f"transform='rotate(-90 66 66)'/>"
            f"<text x='66' y='74' text-anchor='middle' font-size='28' font-weight='700' "
            f"fill='#0F1B2D' font-family='Space Grotesk, Inter, sans-serif'>{pct:.0f}%</text></svg>")
    chips = (stat_chip("Score", f"{right} / {len(answers)}")
             + stat_chip("Best streak", ss.get("quiz_best_streak", 0))
             + stat_chip("Best this session", f"{ss.get('quiz_best', pct):.0f}%")
             + stat_chip("Level", ss.quiz_settings["level"]))
    with st.container(key="card_quiz_results"):
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:24px;align-items:center'>"
            f"<div>{ring}</div><div style='flex:1;min-width:240px'>"
            f"<div style='font-family:Space Grotesk,Inter,sans-serif;font-size:30px;"
            f"font-weight:700;color:{colour}'>{headline}{', ' + name if name else ''}!</div>"
            f"<div style='display:flex;flex-wrap:wrap;gap:8px;margin-top:12px'>{chips}</div>"
            "</div></div>", unsafe_allow_html=True)

        st.markdown("#### By Topic")
        bars = ""
        for topic, (got, n) in stats.items():
            share = got / n
            bar_colour = GREEN if share >= 0.7 else ("#B45309" if share >= 0.4 else RED)
            bars += (f"<div style='margin-bottom:10px'><div style='display:flex;"
                     f"justify-content:space-between;font-size:14px;margin-bottom:4px'>"
                     f"<span>{topic}</span><b>{got} / {n}</b></div>"
                     f"<div style='height:10px;border-radius:5px;background:#EEF1F6'>"
                     f"<div class='pe-bar' style='width:{share * 100:.0f}%;height:10px;border-radius:5px;"
                     f"background:{bar_colour}'></div></div></div>")
        st.markdown(bars, unsafe_allow_html=True)

    # Your weakest topic, based on every round you've played this session
    totals = ss.get("topic_totals") or stats
    weakest = min(totals, key=lambda t: totals[t][0] / totals[t][1])
    weak_score = totals[weakest][0] / totals[weakest][1]
    if len(totals) > 1 and weak_score < 1:
        st.info(f"Your weakest topic so far is **{weakest}**: {weak_score * 100:.0f}% correct "
                f"across {totals[weakest][1]} question{'s' if totals[weakest][1] != 1 else ''} "
                f"this session.")

    wrong = [a for a in answers if not a["correct"]]
    if wrong:
        st.markdown("**Review Your Mistakes**")
        for a in wrong:
            with st.expander(a["q"]["question"]):
                st.markdown(f"You said **{a['chosen']}**. The answer is **{a['q']['answer']}**.")
                st.write(a["q"]["explanation"])

    st.markdown("**What Next?**")
    b1, b2, b3, b4 = st.container(key="quiz_actions").columns(4, gap="small")
    wide_button(b1, "Play Again", type="primary", on_click=start_from_setup_same, args=(df,))
    if wrong:
        wide_button(b2, f"Retry My {len(wrong)} Mistake{'s' if len(wrong) > 1 else ''}",
                  on_click=retry_mistakes, args=(df,))
    if weak_score < 1 and len(totals) > 1:
        wide_button(b3, f"Practise {weakest}", on_click=practise_topic, args=(df, weakest))
    wide_button(b4, "Change Settings", on_click=back_to_setup)



@st.fragment
def quiz_tab(df):
    stage = st.session_state.get("quiz_stage", "setup")
    if stage == "playing":
        quiz_playing()
    elif stage == "done":
        quiz_results(df)
    else:
        quiz_setup(df)
