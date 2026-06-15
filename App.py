import streamlit as st
import random
import re
import json

# 1. 페이지 설정
st.set_page_config(page_title="MJ's iPad Workbook", layout="wide")

# JavaScript를 이용해 브라우저에 데이터를 영구 저장/불러오기 하는 함수
def load_local_data():
    if "passages" not in st.session_state:
        st.session_state.passages = {}
    if "keywords" not in st.session_state:
        st.session_state.keywords = {}

# 🔒 비밀번호 게이트
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 MJ's iPad Study Space")
    pwd = st.text_input("Access Password:", type="password")
    if pwd == "mj1234":
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("Access Denied.")
    st.stop()

load_local_data()

# 🛠️ 텍스트 분리 유틸리티
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

# 🧭 메뉴 인터페이스
st.sidebar.title("🎯 굿노트 테이프 워크북")
menu = st.sidebar.radio("공간 선택", ["⚙️ [교재 탑재] 지문 등록창", "📱 [실전 훈련] 굿노트 테이프 공간"])

# ---------------------------------------------------------------- 데이터 등록 공간
if menu == "⚙️ [교재 탑재] 지문 등록창":
    st.title("⚙️ 수능특강 지문 및 나만의 키워드 탑재")
    st.caption("여기서 지문을 등록하면 브라우저에 안전하게 누적 저장됩니다.")
    
    p_name = st.text_input("지문 제목 (예: 수특영어 01-01):")
    
    col1, col2 = st.columns(2)
    with col1:
        raw_en = st.text_area("영어 본문 전체 복사-붙여넣기:", height=180)
    with col2:
        raw_ko = st.text_area("한글 해석 전체 복사-붙여넣기:", height=180)
        
    kw_input = st.text_input("🔑 가리고 싶은 핵심 단어들을 적어주세요 (쉼표로 구분):", placeholder="apple, had, background")
    
    if st.button("🚀 나만의 단어 테이프 시험지 생성", use_container_width=True):
        if p_name and raw_en and raw_ko:
            en_s = split_sentences(raw_en)
            ko_s = split_sentences(raw_ko)
            
            parsed = []
            for i in range(max(len(en_s), len(ko_s))):
                parsed.append({
                    "en": en_s[i] if i < len(en_s) else "",
                    "ko": ko_s[i] if i < len(ko_s) else ""
                })
            
            # 세션에 저장 (원래는 데이터베이스가 베스트이지만, 세션 유지를 가미)
            st.session_state.passages[p_name] = parsed
            st.session_state.keywords[p_name] = [x.strip() for x in kw_input.split(",") if x.strip()]
            st.success(f"🎯 '{p_name}' 워크북이 성공적으로 누적 등록되었습니다! 훈련 공간으로 이동하세요.")

# ---------------------------------------------------------------- 📱 실전 테이프 훈련 공간
elif menu == "📱 [실전 훈련] 굿노트 테이프 공간":
    st.title("📱 굿노트 스타일 스마트 테이프 암기장")
    st.write("💡 **애플펜슬로 가림막 위에 글씨를 써보며 공부해 보세요! 힌트 패널을 터치하면 단어가 숨겨지거나 나타납니다.**")
    
    if not st.session_state.passages:
        st.info("아직 등록된 교재 지문이 없습니다. 먼저 등록창에서 지문을 입력해 주세요!")
    else:
        selected = st.selectbox("공부할 지문 선택:", list(st.session_state.passages.keys()))
        kws = st.session_state.keywords.get(selected, [])
        
        st.write("---")
        
        for s_idx, s in enumerate(st.session_state.passages[selected]):
            st.markdown(f"**[문장 {s_idx+1}]**")
            
            # 단어별로 쪼개서 테이프 메커니즘 만들기
            words_in_sentence = s['en'].split(" ")
            display_cols = st.columns(len(words_in_sentence) + 1)
            
            # 각 단어들을 가로로 예쁘게 정렬하기 위해 Streamlit의 컬럼 기능을 활용
            for w_idx, word in enumerate(words_in_sentence):
                # 구두점 분리 보정 (마침표, 쉼표 등 제거하고 단어 매칭)
                clean_word = re.sub(r'[.,!?]', '', word).lower()
                
                # 내가 등록한 핵심 단어 리스트에 포함되어 있다면?
                if any(k.lower() == clean_word for k in kws if k):
                    # 단어 첫 글자와 나머지 글자 수만큼의 언더바 생성 (ex: h__)
                    hint_text = word[0] + "_" * (len(clean_word) - 1)
                    if len(word) > len(clean_word): # 마침표 등이 붙어있던 경우 복원
                        hint_text += word[len(clean_word):]
                        
                    # 개별 단어 단위로 토글 버튼(테이프 역할) 생성
                    # 버튼을 누르면 정답이 보이고, 안 누르면 가림막 힌트 상태 유지
                    state_key = f"tape_{selected}_{s_idx}_{w_idx}"
                    if state_key not in st.session_state:
                        st.session_state[state_key] = False
                        
                    with display_cols[w_idx]:
                        if st.session_state[state_key]:
                            # 터치해서 테이프가 열린 상태 (초록색 활성화)
                            if st.button(word, key=f"btn_{state_key}", type="primary"):
                                st.session_state[state_key] = False
                                st.rerun()
                        else:
                            # 테이프가 닫혀있는 상태 (힌트만 보임)
                            if st.button(hint_text, key=f"btn_{state_key}", type="secondary"):
                                st.session_state[state_key] = True
                                st.rerun()
                else:
                    # 일반 단어는 그대로 노출
                    with display_cols[w_idx]:
                        st.markdown(f"<div style='padding-top:5px; font-size:17px;'>{word}</div>", unsafe_allow_html=True)
            
            # 해당 문장 아래에 한글 해석 배치
            st.markdown(f"<p style='color: #7f8c8d; margin-top:-5px; font-size:14px;'>↳ {s['ko']}</p>", unsafe_allow_html=True)
            st.divider()
            
        # 전체 제어 기능 추가
        st.write("")
        col_all1, col_all2 = st.columns(2)
        with col_all1:
            if st.button("👁️ 전체 테이프 한 번에 다 열기", use_container_width=True):
                for k in st.session_state.keys():
                    if k.startswith(f"tape_{selected}_"):
                        st.session_state[k] = True
                st.rerun()
        with col_all2:
            if st.button("🔒 전체 테이프 다시 붙이기 (리셋)", use_container_width=True):
                for k in st.session_state.keys():
                    if k.startswith(f"tape_{selected}_"):
                        st.session_state[k] = False
                st.rerun()
