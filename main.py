import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="🎬 영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_movie_summary_data():
    """kobis_movies.csv 데이터를 불러와 정제 및 전처리를 수행합니다."""
    data_url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    
    # CSV 데이터 로드
    df = pd.read_csv(data_url)
    
    # 장르 정제: 세로막대 기호(|)로 연결된 경우 첫 번째 장르만 사용
    if 'genre' in df.columns:
        df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if pd.notna(x) else '미상')
    
    # 숫자형 데이터 변환
    numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # 개봉일 변환 (YYYYMMDD 포맷)
    if 'openDt' in df.columns:
        df['openDt_str'] = df['openDt'].astype(str)
        df['openDt_dt'] = pd.to_datetime(df['openDt_str'], format='%Y%m%d', errors='coerce')
        
    return df

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("""
박스오피스 10위권에 등재되었던 216편의 영화 요약 데이터를 바탕으로 **장르·국가별 분포와 주요 변수 간의 관계**를 분석하는 도감입니다.
""")
st.divider()

try:
    with st.spinner("영화 요약 데이터를 불러오는 중입니다..."):
        df = load_movie_summary_data()
except Exception as e:
    st.error(f"❌ 데이터를 불러오는 도중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바 데이터 요약 지표
st.sidebar.header("📊 데이터 요약")
st.sidebar.metric("총 분석 영화 수", f"{len(df)} 편")

if 'nation' in df.columns:
    st.sidebar.metric("수록 제작 국가 수", f"{df['nation'].nunique()} 개국")

if 'genre' in df.columns:
    st.sidebar.metric("수록 장르 수", f"{df['genre'].nunique()} 개 장르")

st.sidebar.markdown("---")
st.sidebar.info("📌 향후 다양한 분포 및 상관관계 그래프가 계속 업데이트됩니다.")


# ==========================================
# 📌 구역 1: 장르별 영화 편수 분포 (도넛 그래프)
# ==========================================
st.header("📌 구역 1: 장르별 영화 편수 분포 (Donut Chart)")
st.caption("기간 내 개봉 및 차트인한 216편 영화의 장르별 비중과 편수를 도넛 그래프로 보여줍니다.")

# 장르별 영화 편수 집계
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화편수']

# Plotly 도넛 그래프 생성 (hole=0.4 적용)
fig1 = px.pie(
    genre_counts,
    names='장르',
    values='영화편수',
    title="<b>개봉 영화 장르별 편수 비중</b>",
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# 툴팁 및 트레이스 설정 (호버 시 편수와 비율 표기)
fig1.update_traces(
    textposition='inside',
    textinfo='percent+label',
    hovertemplate="<b>장르: %{label}</b><br>영화 편수: %{value}편<br>점유율: %{percent}<extra></extra>"
)

fig1.update_layout(
    height=500,
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(
        title="🎬 장르 목록",
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.05
    )
)

st.plotly_chart(fig1, use_container_width=True)

# 가장 비중이 높은 장르 정보 추출
top_genre = genre_counts.iloc[0]['장르']
top_genre_count = genre_counts.iloc[0]['영화편수']
top_genre_pct = (top_genre_count / len(df)) * 100

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** "
    f"흥행 10위권에 오른 영화 중 **[{top_genre}]** 장르가 {top_genre_count}편({top_genre_pct:.1f}%)으로 가장 높은 비중을 차지하여, "
    f"극장가에서 가장 대중적으로 제작되고 선호되는 대표 장르임을 한눈에 알 수 있습니다."
)

st.divider()
