impo import streamlit as st
import random

# 1. Page Configuration & Session State Initialization
st.set_page_config(page_title="MJ's Private English Space", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "passages" not in st.session_state:
    # Default sample data to prevent errors on first launch
    st.session_state.passages = {
        "Sample 1": [
            {
                "en": "Industrial design bridges the gap between art and engineering.", 
                "ko": "산업 디자인은 예술과 공학 사이의 간극을 메운다.", 
                "word": "bridges", 
                "phrase": "between art and engineering"
            }
        ]
    }
if "flipped_cards" not in st.session_state:
    st.session_state.flipped_cards = []

# ---------------------------------------------------------------- 🔑 PASSWORD GATEWAY
if not st.session_state.authenticated:
    st.title("🔒 MJ's Private English Space")
    st.write("This space is restricted to authorized users only.")
    
    password_input = st.text_input("Enter password to access:", type="password")
    
    # Change your password here if you want!
    if password_input == "mj1234": 
        st.session_state.authenticated = True
        st.rerun()
    elif password_input:
        st.error("Incorrect password. Please try again.")
    st.stop() 

# ---------------------------------------------------------------- 🔓 AUTHENTICATED ACCESS
st.sidebar.title("📚 Study Menu")

menu = st.sidebar.radio(
    "Go to space:",
    ["⚙️ Register & Manage Passages", "1. Learning & Analysis Space", "2. Blank & Sentence Practice", "3. Word Flipbook Space", "4. Korean-Based Scrambled Composition"]
)

# ---------------------------------------------------------------- SPACE 0: REGISTRATION
if menu == "⚙️ Register & Manage Passages":
    st.title("⚙️ Register & Manage Passages")
    st.subheader("Add your English material here sentence by sentence.")
    
    with st.form("new_passage_form"):
        p_name = st.text_input("Passage/Source Name (ex: Midterm Unit 3, June Mock Exam Q21):")
        st.caption("Please input a single sentence configuration below:")
        p_en = st.text_input("English Sentence:")
        p_ko = st.text_input("Korean Translation:")
        p_word = st.text_input("Target Vocabulary (Used for Word-level blank practice):")
        p_phrase = st.text_input("Target Phrase (Used for Phrase-level blank practice):")
        
        submit = st.form_submit_button("Add Sentence to Passage")
        
        if submit and p_name and p_en and p_ko and p_word and p_phrase:
            if p_name not in st.session_state.passages:
                st.session_state.passages[p_name] = []
            
            st.session_state.passages[p_name].append({
                "en": p_en.strip(),
                "ko": p_ko.strip(),
                "word": p_word.strip(),
                "phrase": p_phrase.strip()
            })
            st.success(f"✅ Successfully added to '{p_name}'!")

    st.write("---")
    st.subheader("📦 Currently Registered Passages")
    for name, sentences in st.session_state.passages.items():
        st.markdown(f"**• {name}** ({len(sentences)} sentence(s) loaded)")

# ---------------------------------------------------------------- SPACE 1: ANALYSIS
elif menu == "1. Learning & Analysis Space":
    st.title("🌱 1. Learning & Analysis Space")
    selected_p = st.selectbox("Select a passage to study:", list(st.session_state.passages.keys()))
    
    if selected_p:
        for idx, sentence in enumerate(st.session_state.passages[selected_p]):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"**[{idx+1}] {sentence['en']}**")
                st.caption(f"↳ {sentence['ko']}")
            with col2:
                if st.checkbox("Add to Review Book", key=f"add_{selected_p}_{idx}"):
                    if sentence not in st.session_state.flipped_cards:
                        st.session_state.flipped_cards.append(sentence)
                        st.toast("Sent to review spaces!")
            st.divider()

# ---------------------------------------------------------------- SPACE 2: BLANK PRACTICE
elif menu == "2. Blank & Sentence Practice":
    st.title("✏️ 2. Blank & Sentence Practice")
    selected_p = st.selectbox("Select a passage to practice:", list(st.session_state.passages.keys()))
    
    if selected_p:
        tab_word, tab_phrase, tab_sentence = st.tabs(["🔤 Word Level (First Letter Hint)", "🌿 Phrase Level (Contextual)", "🧩 Sentence Level (No Korean Hint)"])
        
        with tab_word:
            st.subheader("Guess the core vocabulary using the initial character hint.")
            for idx, sentence in enumerate(st.session_state.passages[selected_p]):
                target_word = sentence['word']
                if target_word in sentence['en']:
                    hint_word = target_word[0] + "_" * (len(target_word) - 1)
                    blanked_text = sentence['en'].replace(target_word, f" [ {hint_word} ] ")
                    st.markdown(f"**{idx+1}. {blanked_text}**")
                    st.caption(f"Meaning: {sentence['ko']}")
                    with st.expander("Show Answer"):
                        st.success(target_word)
                    st.write("")

        with tab_phrase:
            st.subheader("Deduce the missing syntactic phrase using context and the translation.")
            for idx, sentence in enumerate(st.session_state.passages[selected_p]):
                target_phrase = sentence['phrase']
                if target_phrase in sentence['en']:
                    blanked_text = sentence['en'].replace(target_phrase, " [ ________________________ ] ")
                    st.markdown(f"**{idx+1}. {blanked_text}**")
                    st.caption(f"Meaning: {sentence['ko']}")
                    with st.expander("Show Answer"):
                        st.success(target_phrase)
                    st.write("")

        with tab_sentence:
            st.subheader("⚠️ No Korean Translation Provided! Reconstruct the correct syntax from the scrambled pool.")
            for idx, sentence in enumerate(st.session_state.passages[selected_p]):
                st.markdown(f"### 📋 Question {idx+1}")
                words = sentence['en'].replace(".", "").replace(",", "").split()
                if f"shuffle_{selected_p}_{idx}" not in st.session_state:
                    random.shuffle(words)
                    st.session_state[f"shuffle_{selected_p}_{idx}"] = words
                
                st.info(f"Scrambled Words:  [ {' / '.join(st.session_state[f'shuffle_{selected_p}_{idx}'])} ]")
                user_ans = st.text_input("Restore the full sentence:", key=f"restore_{selected_p}_{idx}")
                if user_ans:
                    if user_ans.strip().replace(".", "").lower() == sentence['en'].strip().replace(".", "").lower():
                        st.success("🎉 Perfect syntax structure!")
                    else:
                        st.error("Incorrect. Double-check your structural order.")
                        with st.expander("Reveal Original Sentence"):
                            st.code(sentence['en'])
                st.write("---")

# ---------------------------------------------------------------- SPACE 3: FLIPBOOK
elif menu == "3. Word Flipbook Space":
    st.title("🎴 3. Word Flipbook Space")
    if not st.session_state.flipped_cards:
        st.info("Sentences checked for review in Space 1 will compile flashcards here.")
    else:
        for idx, card in enumerate(st.session_state.flipped_cards):
            with st.container(border=True):
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.subheader(f"Card {idx+1}: `{card['word']}`")
                with col2:
                    flip = st.button("Flip Card", key=f"card_flip_{idx}")
                if flip:
                    st.info(f"Translation: {card['ko']}\n\nContextual Usage: {card['en']}")

# ---------------------------------------------------------------- SPACE 4: SCRAMBLED COMPOSITION
elif menu == "4. Korean-Based Scrambled Composition":
    st.title("🧩 4. Korean-Based Scrambled Composition")
    st.subheader("Translate the Korean meaning into proper English syntax using the shuffled options.")
    if not st.session_state.flipped_cards:
        st.info("Sentences checked for review in Space 1 will display composition tests here.")
    else:
        for idx, card in enumerate(st.session_state.flipped_cards):
            st.markdown(f"**Meaning**")
            words = card['en'].replace(".", "").replace(",", "").split()
            st.warning(f"Word Pool: {', '.join(random.sample(words, len(words)))}")
            user_comp = st.text_input("Compose sentence:", key=f"korean_eng_{idx}")
            if user_comp:
                if user_comp.strip().replace(".", "").lower() == card['en'].strip().replace(".", "").lower():
                    st.success("🎉 Excellent translation accuracy!")
                else:
                    st.error("Syntax mismatch. Try rearranging the pool.")
            st.write("---")
