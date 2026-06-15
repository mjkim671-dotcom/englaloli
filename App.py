import streamlit as st
import random
import re

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="MJ's Advanced English Space", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "passages" not in st.session_state:
    st.session_state.passages = {}
if "user_selected_words" not in st.session_state:
    st.session_state.user_selected_words = {} # {passage_name: [words]}
if "user_selected_phrases" not in st.session_state:
    st.session_state.user_selected_phrases = {} # {passage_name: [phrases]}
if "review_sentences" not in st.session_state:
    st.session_state.review_sentences = []

# ---------------------------------------------------------------- 🔑 PASSWORD GATEway
if not st.session_state.authenticated:
    st.title("🔒 MJ's Private English Space")
    password_input = st.text_input("Enter password to access:", type="password")
    if password_input == "mj1234": 
        st.session_state.authenticated = True
        st.rerun()
    elif password_input:
        st.error("Incorrect password.")
    st.stop() 

# ---------------------------------------------------------------- 🔓 MAIN INTERFACE
st.sidebar.title("📚 수능특강 페이스메이커")
menu = st.sidebar.radio(
    "이동할 공간:",
    ["⚙️ 1초 지문 폭탄 등록", "1. 본문 학습 & 실시간 단어/구 Pick", "2. 빈칸 & 문장 연습 공간", "3. 내 오답 플립북 & 영작"]
)

# 문장 쪼개기 내장 함수 (마침표, 물음표, 느낌표 기준)
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

# ---------------------------------------------------------------- SPACE 0: EASY REGISTRATION
if menu == "⚙️ 1초 지문 폭탄 등록":
    st.title("⚙️ 1초 지문 폭탄 등록")
    st.subheader("PDF에서 지문을 통째로 복사해서 붙여넣으세요. 분리는 프로그램이 합니다!")
    
    p_name = st.text_input("지문 제목 (ex: 수특 영어 3강 1번):")
    
    col1, col2 = st.columns(2)
    with col1:
        raw_en = st.text_area("영어 지문 전체 복사-붙여넣기:", height=250)
    with col2:
        raw_ko = st.text_area("한글 해석 전체 복사-붙여넣기:", height=250)
        
    if st.button("🔥 지문 자동 매칭 및 등록"):
        if p_name and raw_en and raw_ko:
            en_sentences = split_into_sentences(raw_en)
            ko_sentences = split_into_sentences(raw_ko)
            
            # 영어와 한글 문장 개수 맞추기 기본 보정
            parsed_list = []
            max_len = max(len(en_sentences), len(ko_sentences))
            for i in range(max_len):
                en_s = en_sentences[i] if i < len(en_sentences) else ""
                ko_s = ko_sentences[i] if i < len(ko_sentences) else ""
                parsed_list.append({"en": en_s, "ko": ko_s})
                
            st.session_state.passages[p_name] = parsed_list
            st.session_state.user_selected_words[p_name] = []
            st.session_state.user_selected_phrases[p_name] = []
            st.success(f"✅ 총 {len(parsed_list)}개의 문장이 번호 매겨져 자동으로 등록되었습니다!")

# ---------------------------------------------------------------- SPACE 1: LIVE PICK LEARNING
elif menu == "1. 본문 학습 & 실시간 단어/구 Pick":
    st.title("🌱 1. 본문 학습 & 실시간 단어/구 Pick")
    
    if not st.session_state.passages:
        st.info("지문 등록 공간에서 먼저 지문을 등록해 주세요!")
    else:
        selected_p = st.selectbox("학습할 지문 선택:", list(st.session_state.passages.keys()))
        
        # 실시간 단어/구 등록 서브 패널
        with st.sidebar.expander("🔍 읽으면서 바로 빈칸 만들기", expanded=True):
            st.write("아래에 단어나 구를 적으면 실시간으로 빈칸 시험지가 생성됩니다.")
            new_word = st.text_input("나만의 픽 - 어려운 단어:")
            if st.button("단어 등록") and new_word:
                if new_word.strip() not in st.session_state.user_selected_words[selected_p]:
                    st.session_state.user_selected_words[selected_p].append(new_word.strip())
                    st.toast(f"'{new_word}' 단어 시험 등록!")
                    
            new_phrase = st.text_input("나만의 픽 - 어려운 구문/절:")
            if st.button("구문 등록") and new_phrase:
                if new_phrase.strip() not in st.session_state.user_selected_phrases[selected_p]:
                    st.session_state.user_selected_phrases[selected_p].append(new_phrase.strip())
                    st.toast("구문 시험 등록!")
                    
        st.write("---")
        # 지문 시각화
        for idx, sentence in enumerate(st.session_state.passages[selected_p]):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"**[{idx+1}] {sentence['en']}**")
                st.caption(f"↳ {sentence['ko']}")
            with col2:
                if st.checkbox("문장 영작 추가", key=f"rev_{selected_p}_{idx}"):
                    if sentence not in st.session_state.review_sentences:
                        st.session_state.review_sentences.append(sentence)
                        st.toast("오답/영작 코너로 전송됨!")
            st.divider()

# ---------------------------------------------------------------- SPACE 2: AUTOMATIC BLANK
elif menu == "2. 빈칸 및 문장 연습 공간":
    st.title("✏️ 2. 빈칸 및 문장 연습 공간")
    
    if not st.session_state.passages:
        st.info("등록된 지문이 없습니다.")
    else:
        selected_p = st.selectbox("연습할 지문 선택:", list(st.session_state.passages.keys()))
        
        tab_word, tab_phrase, tab_sentence = st.tabs(["🔤 내가 뽑은 단어 테스트", "🌿 내가 뽑은 구 테스트", "🧩 문장 자동 셔플 (한글 없음)"])
        
        with tab_word:
            st.subheader("1번 공간에서 내가 뽑은 단어들이 자동으로 `첫 글자 힌트` 빈칸이 됩니다.")
            picked_words = st.session_state.user_selected_words.get(selected_p, [])
            
            for idx, sentence in enumerate(st.session_state.passages[selected_p]):
                display_text = sentence['en']
                has_blank = False
                
                # 내가 이 지문에서 뽑은 단어들을 모두 찾아 빈칸 처리
                for word in picked_words:
                    if word.lower() in display_text.lower():
                        # 대소문자 매칭을 위한 처리
                        pattern = re.compile(re.escape(word), re.IGNORECASE)
                        hint = word[0] + "_" * (len(word) - 1)
                        display_text = pattern.sub(f" [ {hint} ] ", display_text)
                        has_blank = True
                
                st.markdown(f"**{idx+1}. {display_text}**")
                st.caption(f"뜻: {sentence['ko']}")
                if has_blank:
                    with st.expander("정답 확인"):
                        st.success(", ".join([w for w in picked_words if w.lower() in sentence['en'].lower()]))
                st.write("")

        with tab_phrase:
            st.subheader("내가 지정한 핵심 구문 덩어리가 통째로 뚫립니다.")
            picked_phrases = st.session_state.user_selected_phrases.get(selected_p, [])
            
            for idx, sentence in enumerate(st.session_state.passages[selected_p]):
                display_text = sentence['en']
                has_blank = False
                
                for pr in picked_phrases:
                    if pr.lower() in display_text.lower():
                        pattern = re.compile(re.escape(pr), re.IGNORECASE)
                        display_text = pattern.sub(" [ ________________________ ] ", display_text)
                        has_blank = True
                        
                st.markdown(f"**{idx+1}. {display_text}**")
                st.caption(f"뜻: {sentence['ko']}")
                if has_blank:
                    with st.expander("정답 확인"):
                        st.success(", ".join([p for p in picked_phrases if p.lower() in sentence['en'].lower()]))
                st.write("")

        with tab_sentence:
            st.subheader("⚠️ 한국어 해석 없음! 오직 뒤섞인 단어 카드로만 문장 구조를 맞추세요.")
            for idx, sentence in enumerate(st.session_state.passages[selected_p]):
                st.markdown(f"### 📋 문제 {idx+1}")
                words = sentence['en'].replace(".", "").replace(",", "").split()
                if f"shuf_{selected_p}_{idx}" not in st.session_state:
                    random.shuffle(words)
                    st.session_state[f"shuf_{selected_p}_{idx}"] = words
                
                st.info(f"제시된 단어들:  [ {' / '.join(st.session_state[f'shuf_{selected_p}_{idx}'])} ]")
                user_ans = st.text_input("원래 문장 복원 입력:", key=f"rest_{selected_p}_{idx}")
                if user_ans:
                    if user_ans.strip().replace(".", "").lower() == sentence['en'].strip().replace(".", "").lower():
                        st.success("🎉 정답입니다!")
                    else:
                        st.error("구조가 틀렸습니다.")
                        with st.expander("원본 보기"):
                            st.code(sentence['en'])
                st.write("---")

# ---------------------------------------------------------------- SPACE 3: FLIPBOOK & COMPOSITION
elif menu == "3. 내 오답 플립북 & 영작":
    st.title("🎴 3. 내 오답 플립북 & 영작")
    
    tab_flip, tab_comp = st.tabs(["🎴 실시간 단어 플립북", "🧩 한글 기반 순서 배열 영작"])
    
    with tab_flip:
        # 모든 지문에서 뽑은 단어들 총집합 플립북
        all_words = []
        for p, words in st.session_state.user_selected_words.items():
            for w in words:
                all_words.append({"word": w, "origin": p})
                
        if not all_words:
            st.info("1번 공간 사이드바에서 모르는 단어를 등록하면 여기에 플립 카드가 생성됩니다.")
        else:
            for idx, item in enumerate(all_words):
                with st.container(border=True):
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.subheader(f"단어 {idx+1}: `{item['word']}`")
                        st.caption(f"출처: {item['origin']}")
                    with col2:
                        flip = st.button("뜻/본문 보기", key=f"flip_vocab_{idx}")
                    if flip:
                        st.warning("💡 이 단어가 포함된 본문 문장을 찾아 학습해 보세요!")

    with tab_comp:
        if not st.session_state.review_sentences:
            st.info("1번 공간에서 문장 옆 '문장 영작 추가'를 체크하면 여기가 활성화됩니다.")
        else:
            for idx, card in enumerate(st.session_state.review_sentences):
                st.markdown(f"**한글 해석**")
                words = card['en'].replace(".", "").replace(",", "").split()
                st.warning(f"제시 단어 힌트: {', '.join(random.sample(words, len(words)))}")
                user_comp = st.text_input("영작문 입력:", key=f"final_comp_{idx}")
                if user_comp:
                    if user_comp.strip().replace(".", "").lower() == card['en'].strip().replace(".", "").lower():
                        st.success("🎉 영작 성공!")
                    else:
                        st.error("틀렸습니다. 다시 순서를 맞춰보세요.")
                st.write("---")
