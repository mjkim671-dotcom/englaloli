import streamlit as st
import random
import re

st.set_page_config(page_title="MJ's 10-Step English Workbook", layout="wide")

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "passages" not in st.session_state:
    st.session_state.passages = {}
if "keywords" not in st.session_state:
    st.session_state.keywords = {}

# 🔒 비밀번호 게이트
if not st.session_state.authenticated:
    st.title("🔒 MJ's Private Exam Engine")
    pwd = st.text_input("Access Password:", type="password")
    if pwd == "mj1234":
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("Access Denied.")
    st.stop()

# 🛠️ 텍스트 분리 유틸리티
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

# 🧭 메뉴 구성 (이그잼포유 10단계 기반 세분화)
st.sidebar.title("🎯 WORKBOOK 10단계")
menu = st.sidebar.radio("학습 단계 선택", [
    "⚙️ [0단계] 지문 고속 탑재",
    "📚 [1~3단계] 지문 파악 & 빈칸 완성",
    "✍️ [4~6단계] 통영작 & 어법·어휘 마스터",
    "🔥 [7~10단계] 디테일 교정 & 순서 배열"
])

# ---------------------------------------------------------------- 0단계
if menu == "⚙️ [0단계] 지문 고속 탑재":
    st.title("⚙️ 수능특강 지문 고속 데이터 빌드")
    st.write("PDF에서 지문을 긁어와 붙여넣으면 10단계 워크북이 즉시 자동 생성됩니다.")
    
    p_name = st.text_input("지문 제목 (예: 수특영어 01강 1번)", placeholder="ex) 01-01")
    
    col1, col2 = st.columns(2)
    with col1:
        raw_en = st.text_area("영어 본문 전체 복사-붙여넣기", height=200)
    with col2:
        raw_ko = st.text_area("한글 해석 전체 복사-붙여넣기", height=200)
        
    kw_input = st.text_input("🔑 이 지문의 핵심 단어/동사 지정을 원하시면 적어주세요 (쉼표 구분)", placeholder="provide, opportunity, background")
    
    if st.button("🚀 10단계 워크북 생성하기", use_container_width=True):
        if p_name and raw_en and raw_ko:
            en_s = split_sentences(raw_en)
            ko_s = split_sentences(raw_ko)
            
            parsed = []
            for i in range(max(len(en_s), len(ko_s))):
                parsed.append({
                    "en": en_s[i] if i < len(en_s) else "",
                    "ko": ko_s[i] if i < len(ko_s) else ""
                })
            st.session_state.passages[p_name] = parsed
            st.session_state.keywords[p_name] = [x.strip() for x in kw_input.split(",") if x.strip()]
            st.success(f"🎯 '{p_name}' 지문 변형 완료! 학습 탭으로 이동하세요.")

# ---------------------------------------------------------------- 1~3단계
elif menu == "📚 [1~3단계] 지문 파악 & 빈칸 완성":
    st.title("📚 지문 파악 및 내포 어휘 완성 단계")
    if not st.session_state.passages:
        st.info("0단계에서 지문을 먼저 등록해 주세요.")
    else:
        selected = st.selectbox("지문 선택:", list(st.session_state.passages.keys()))
        t1, t2, t3 = st.tabs(["📝 1단계: 지문 연습하기", "🇰🇷 2단계: 빈칸 완성(우리말)", "🔤 3단계: 빈칸 완성(영문)"])
        
        with t1:
            st.subheader("영문과 우리말 해석을 대조하며 구문을 완벽하게 분석하세요.")
            for idx, s in enumerate(st.session_state.passages[selected]):
                st.markdown(f"**[{idx+1}] {s['en']}**")
                st.markdown(f"<span style='color: gray;'>↳ {s['ko']}</span>", unsafe_allow_html=True)
                st.write("")
                
        with t2:
            st.subheader("영문을 보고 핵심 한글 해석의 괄호를 머릿속으로 채워보세요.")
            for idx, s in enumerate(st.session_state.passages[selected]):
                st.markdown(f"**[{idx+1}] {s['en']}**")
                # 무작위 한글 단어 하나 숨기기 기본 매커니즘
                ko_words = s['ko'].split()
                if len(ko_words) > 2:
                    hidden_idx = len(ko_words) // 2
                    hint_ko = s['ko'].replace(ko_words[hidden_idx], "[ _______ ]")
                    st.markdown(f"↳ {hint_ko}")
                else:
                    st.markdown(f"↳ [ 전체 가림 ] (정답 확인 필요)")
                with st.expander("해석 정답 확인"):
                    st.write(s['ko'])
                st.write("")
                
        with t3:
            st.subheader("우리말 해석을 보고 영문의 핵심 어휘를 첫 글자 초성 힌트로 완성하세요.")
            kws = st.session_state.keywords.get(selected, [])
            for idx, s in enumerate(st.session_state.passages[selected]):
                txt = s['en']
                for kw in kws:
                    if kw.lower() in txt.lower():
                        pattern = re.compile(re.escape(kw), re.IGNORECASE)
                        txt = pattern.sub(f"**[{kw[0]}____]**", txt)
                st.markdown(f"**[{idx+1}]** {txt}")
                st.caption(f"뜻: {s['ko']}")

# ---------------------------------------------------------------- 4~6단계
elif menu == "✍️ [4~6단계] 통영작 & 어법·어휘 마스터":
    st.title("✍️ 고난도 서술형 통영작 및 구조 마스터")
    if not st.session_state.passages:
        st.info("등록된 지문이 없습니다.")
    else:
        selected = st.selectbox("지문 선택:", list(st.session_state.passages.keys()))
        t4, t5, t6 = st.tabs(["✍️ 4단계: 영작 연습하기 (전체 문장)", "⚙️ 5단계: 동사형 연습하기", "⚖️ 6단계: 어법·어휘 고르기"])
        
        with t4:
            st.subheader("🔥 [💡교정완료] 국어 해석만 보고 전체 문장을 영어 서술형으로 완벽하게 영작하세요.")
            for idx, s in enumerate(st.session_state.passages[selected]):
                st.markdown(f"**문장 {idx+1}. [해석] {s['ko']}**")
                u_ans = st.text_input("통영작 답안 입력:", key=f"step4_ans_{idx}")
                if u_ans:
                    if u_ans.strip().lower().replace(".","") == s['en'].strip().lower().replace(".",""):
                        st.success("🎉 토씨 하나 틀리지 않고 완벽합니다! (100점)")
                    else:
                        st.error("오타나 어순 오류가 있습니다. 아래 정답과 비교해 보세요.")
                        with st.expander("🔒 원문 정답 보기"):
                            st.code(s['en'])
                st.write("")
                
        with t5:
            st.subheader("동사의 원형 힌트를 기반으로 문맥에 맞는 수일치/시제형으로 교정하세요.")
            kws = st.session_state.keywords.get(selected, [])
            for idx, s in enumerate(st.session_state.passages[selected]):
                txt = s['en']
                has_verb = False
                for kw in kws:
                    if kw.lower() in txt.lower():
                        pattern = re.compile(re.escape(kw), re.IGNORECASE)
                        txt = pattern.sub(f"**[ {kw} (원형) -> 변형하시오 ]**", txt)
                        has_verb = True
                st.markdown(f"**[{idx+1}]** {txt}")
                st.caption(f"뜻: {s['ko']}")
                if has_verb:
                    with st.expander("원문 정답"):
                        st.success(s['en'])
                        
        with t6:
            st.subheader("내신 단골 어법 어휘 고르기! 올바른 한 쌍을 채택하세요.")
            kws = st.session_state.keywords.get(selected, [])
            for idx, s in enumerate(st.session_state.passages[selected]):
                txt = s['en']
                for kw in kws:
                    if kw.lower() in txt.lower():
                        pattern = re.compile(re.escape(kw), re.IGNORECASE)
                        txt = pattern.sub(f"**[ {kw} / {kw+'_incorrect'} ]**", txt)
                st.markdown(f"**[{idx+1}]** {txt}")

# ---------------------------------------------------------------- 7~10단계
elif menu == "🔥 [7~10단계] 디테일 교정 & 순서 배열":
    st.title("🔥 완벽한 1등급 안착을 위한 파이널 훈련")
    if not st.session_state.passages:
        st.info("등록된 지문이 없습니다.")
    else:
        selected = st.selectbox("지문 선택:", list(st.session_state.passages.keys()))
        t7, t8, t9, t10 = st.tabs(["🔍 7단계: 어색한 곳 고치기", "🧩 8단계: 단어 순서 배열", "⛓️ 9단계: 문단 순서 배열", "📝 10단계: 분석 노트 완료"])
        
        with t7:
            st.subheader("틀린 어법을 예리하게 찾아내는 훈련입니다.")
            for idx, s in enumerate(st.session_state.passages[selected]):
                st.markdown(f"**[{idx+1}]** {s['en']}")
                with st.expander("해석 힌트 열기"):
                    st.write(s['ko'])
                    
        with t8:
            st.subheader("뒤섞인 카드들을 배열하여 완벽한 문장 어순 밸런스를 잡으세요.")
            for idx, s in enumerate(st.session_state.passages[selected]):
                st.write(f"**문장 {idx+1}.** {s['ko']}")
                words = s['en'].replace(".", "").replace(",", "").split()
                if f"shuffle_{selected}_{idx}" not in st.session_state:
                    st.session_state[f"shuffle_{selected}_{idx}"] = random.sample(words, len(words))
                st.warning(f"제시 단어: {st.session_state[f'shuffle_{selected}_{idx}']}")
                st.text_input("순서대로 기입:", key=f"step8_txt_{idx}")
                st.write("")
                
        with t9:
            st.subheader("순서 추론 마스터! 뒤섞인 문장 카드를 읽고 원래의 문맥 흐름 번호를 마크하세요.")
            all_s = [s['en'] for s in st.session_state.passages[selected]]
            if f"final_flow_{selected}" not in st.session_state:
                indexed = list(enumerate(all_s))
                random.shuffle(indexed)
                st.session_state[f"final_flow_{selected}"] = indexed
                
            for c_idx, (orig_idx, string) in enumerate(st.session_state[f"final_flow_{selected}"]):
                st.info(f"**[문장 카드 {c_idx+1}]** : {string}")
            st.text_input("올바른 순서대로 숫자 카드 조합 입력 (예: 2, 4, 1, 3):")
            
        with t10:
            st.subheader("🏅 10단계 마스터 최종 완료인증!")
            st.text_area("이 지문에서 수능/내신에 변형되어 출제될 것 같은 나만의 핵심 포인트 코멘트 요약:", height=150)
            st.button("완료 도장 찍기", on_click=lambda: st.balloons())
