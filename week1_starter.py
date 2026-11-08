# %% [markdown]
# # Week 1 — 파이썬·판다스로 경제 시계열 다루기
#
# 실행 방법
#   1) 설치:  pip install pandas numpy matplotlib
#   2) VS Code에서 이 파일을 열고 각 "# %%" 셀 위의 "Run Cell"을 눌러 셀 단위로 실행
#      (전체 실행: 터미널에서  python week1_starter.py )
#   3) TODO 부분을 채운 뒤 맨 아래 main 셀을 실행하면 self_check()가 채점용 검사를 돌립니다.
#
# 폴더 구조(자동 생성)
#   data/raw/     FRED에서 받은 CSV 캐시
#   outputs/      그림 저장 위치

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

print("pandas", pd.__version__)  # 2.2 이상 권장 (빈도 별칭 'ME', 'QE')

DATA_DIR = Path("data/raw")
OUT_DIR = Path("outputs")
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"


def load_fred(series_id: str, start: str = "1999-01-01", refresh: bool = False) -> pd.Series:
    """FRED 시리즈 하나를 float Series(DatetimeIndex)로 돌려준다. 한 번 받으면 data/raw에 캐시.

    - FRED CSV의 결측치는 "." 으로 표기되므로 na_values="." 로 처리한다.
    - 첫 열(날짜) 이름이 DATE / observation_date 등으로 바뀌어도 index_col=0 이라 상관없다.
    """
    cache = DATA_DIR / f"{series_id}.csv"
    if refresh or not cache.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        url = FRED_URL.format(sid=series_id)
        try:
            raw = pd.read_csv(url, index_col=0, parse_dates=True, na_values=".")
        except Exception as e:  # 네트워크·SSL 문제 등
            raise RuntimeError(
                f"[{series_id}] 다운로드 실패: {e}\n"
                f"→ 브라우저로 {url} 를 열어 CSV를 저장한 뒤 {cache} 위치에 두고 다시 실행하세요."
            ) from e
        raw.to_csv(cache)

    df = pd.read_csv(cache, index_col=0, parse_dates=True, na_values=".")
    s = df.iloc[:, 0].astype(float).rename(series_id)
    s.index.name = "date"
    return s.loc[start:]


# %% [markdown]
# ## 매일 드릴 (각 10~15분)

# %%
# Day 1 (월) — Series·인덱싱
# TODO: 2024-01 ~ 2024-12 월초 날짜(freq="MS")로 가상 물가지수 Series를 만들고 3~5월만 꺼내 보세요.
# 힌트: pd.date_range("2024-01-01", periods=12, freq="MS"), np.linspace(100, 103, 12), .loc["2024-03":"2024-05"]


# %%
# Day 2 (화) — CSV 읽기·날짜 슬라이싱
# TODO: cpi = load_fred("CPIAUCSL") 로 불러와 2008년만 슬라이스하고, 최댓값이 나온 달을 찾으세요.
# 힌트: .loc["2008"], .idxmax()


# %%
# Day 3 (수) — 변화율
# TODO: YoY(%) = (P_t / P_{t-12} - 1) * 100 과 로그차분 * 100 = (ln P_t - ln P_{t-12}) * 100 을 구하고
#       두 값의 차이가 가장 큰 시점을 찾으세요. 왜 그 시점인지 한 줄로 설명.
# 힌트: .pct_change(12), np.log(cpi).diff(12), (a - b).abs().idxmax()


# %%
# Day 4 (목) — 결합·빈도 변환
# TODO: unrate = load_fred("UNRATE") 를 분기 평균과 분기 말 값으로 각각 바꿔 보세요.
# 힌트: .resample("QE").mean(), .resample("QE").last()


# %% [markdown]
# ## 미니 과제 #1 — 미국 인플레이션과 기준금리
# 아래 다섯 함수의 TODO를 채우세요. 함수 이름·반환 형태는 바꾸지 마세요(self_check가 검사합니다).

# %%
def build_monthly(cpi: pd.Series, fedfunds: pd.Series, unrate: pd.Series) -> pd.DataFrame:
    """세 시리즈를 열 이름 cpi, fedfunds, unrate 인 하나의 월별 DataFrame으로 합친다.

    요구사항
    - 세 시리즈 모두 값이 있는 기간만 남길 것 (inner join 효과)
    - 인덱스는 오름차순 DatetimeIndex
    힌트: pd.concat([...], axis=1, keys=[...]) 또는 pd.concat 후 .rename(columns=...), .dropna()
    """
    # TODO
    raise NotImplementedError


def add_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """변환 열을 추가한 *새* DataFrame을 반환한다 (원본 df를 바꾸지 말 것: df = df.copy()).

    추가할 열 (모두 % 단위)
    - infl_yoy     : 전년동월대비 CPI 상승률            = (P_t / P_{t-12} - 1) * 100
    - infl_mom_ann : 전월대비 상승률의 연율화           = ((P_t / P_{t-1}) ** 12 - 1) * 100
    - infl_logdiff : 12개월 로그차분                    = (ln P_t - ln P_{t-12}) * 100
    - real_rate    : 사후 실질금리(근사)                = fedfunds - infl_yoy
    - infl_yoy_ma12: infl_yoy의 12개월 이동평균
    - infl_yoy_sd12: infl_yoy의 12개월 이동표준편차
    마지막에 2001-01 이후만 남겨 앞부분 NaN을 잘라낼 것.
    """
    df = df.copy()
    # TODO
    raise NotImplementedError


def to_quarterly(df: pd.DataFrame) -> pd.DataFrame:
    """월별 df를 분기 데이터로 바꾼다.

    - cpi 는 분기 말 값(last), 나머지 열은 분기 평균(mean)
    - 왜 cpi만 last로 하는지 해석 메모에 한 줄로 적을 것
    힌트: df.resample("QE").agg({"cpi": "last", "fedfunds": "mean", ...})
    """
    # TODO
    raise NotImplementedError


def plot_dashboard(df: pd.DataFrame) -> plt.Figure:
    """3단 패널 그림을 반환한다 (x축 공유).

    1단: infl_yoy 와 fedfunds (한 축에 두 선, 범례 포함)
    2단: real_rate (0 기준 수평선 포함)
    3단: unrate
    모든 패널에 세로 점선 3개: 2008-09 (리먼), 2020-03 (코로나), 2022-03 (연준 첫 인상)
    축 라벨에 단위(%) 표기
    힌트: fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True); ax.axvline(pd.Timestamp(...), ls="--")
    """
    # TODO
    raise NotImplementedError


def lagged_corr(x: pd.Series, y: pd.Series, max_lag: int = 24) -> pd.Series:
    """k = 0..max_lag 에 대해 corr(x_t, y_{t+k}) 를 담은 Series (index = k)를 반환한다.

    즉 "x가 k개월 뒤의 y와 얼마나 같이 움직이나".
    힌트: y.shift(-k) 는 t 시점에 y_{t+k} 값을 가져온다. x.corr(...)는 NaN을 알아서 제외한다.
    """
    # TODO
    raise NotImplementedError


# %% [markdown]
# ## 자동 검사 (수정하지 마세요)

# %%
def self_check(m: pd.DataFrame, q: pd.DataFrame, lc: pd.Series) -> None:
    errors = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            errors.append(msg)

    need = ["cpi", "fedfunds", "unrate", "infl_yoy", "infl_mom_ann",
            "infl_logdiff", "real_rate", "infl_yoy_ma12", "infl_yoy_sd12"]
    missing = [c for c in need if c not in m.columns]
    check(not missing, f"월별 df에 없는 열: {missing}")
    check(isinstance(m.index, pd.DatetimeIndex), "월별 df 인덱스가 DatetimeIndex가 아님")
    check(m.index.is_monotonic_increasing, "월별 df 인덱스가 오름차순이 아님")
    check(m.index.min() >= pd.Timestamp("2001-01-01"), "2001-01 이전 행이 남아 있음")

    if not missing:
        check(not m[need].isna().any().any(), "월별 df에 NaN이 남아 있음")
        # 재계산 값과 비교 (2002년 이후는 shift(12)에 필요한 과거값이 df 안에 있음)
        mm = m.loc["2002":]
        yoy = (m["cpi"] / m["cpi"].shift(12) - 1) * 100
        check(np.allclose(mm["infl_yoy"], yoy.loc["2002":], atol=1e-6), "infl_yoy 계산이 다름")
        mom = ((m["cpi"] / m["cpi"].shift(1)) ** 12 - 1) * 100
        check(np.allclose(mm["infl_mom_ann"], mom.loc["2002":], atol=1e-6), "infl_mom_ann 계산이 다름")
        check(np.allclose(m["real_rate"], m["fedfunds"] - m["infl_yoy"], atol=1e-9), "real_rate 계산이 다름")
        check((m["infl_logdiff"] <= m["infl_yoy"] + 1e-9).all(),
              "로그차분은 항상 YoY 이하여야 함 (ln(1+g) <= g) — 계산 확인")

    check(isinstance(q.index, pd.DatetimeIndex) and pd.infer_freq(q.index) in ("QE-DEC", "Q-DEC"),
          "분기 df 인덱스가 분기 말(QE) 빈도가 아님")
    if not missing and "cpi" in q.columns:
        last_q = q.index[-2]  # 마지막 분기는 미완성일 수 있으니 하나 앞 분기로 검사
        check(np.isclose(q.loc[last_q, "cpi"], m.loc[m.index <= last_q, "cpi"].iloc[-1]),
              "분기 cpi가 분기 말 값(last)이 아님")

    check(list(lc.index) == list(range(len(lc))), "lagged_corr 인덱스는 0,1,2,...,max_lag 이어야 함")
    check(lc.between(-1, 1).all(), "상관계수가 [-1, 1] 범위를 벗어남")

    if errors:
        print("❌ 검사 실패:")
        for e in errors:
            print("  -", e)
    else:
        print("✅ 모든 검사 통과")


# %% [markdown]
# ## 실행

# %%
if __name__ == "__main__" or "get_ipython" in globals():
    cpi = load_fred("CPIAUCSL")   # 소비자물가지수(계절조정, 1982-84=100)
    ff = load_fred("FEDFUNDS")    # 실효 연방기금금리(%)
    ur = load_fred("UNRATE")      # 실업률(%)

    monthly = add_transforms(build_monthly(cpi, ff, ur))
    quarterly = to_quarterly(monthly)
    lc = lagged_corr(monthly["infl_yoy"], monthly["fedfunds"], max_lag=24)

    self_check(monthly, quarterly, lc)

    OUT_DIR.mkdir(exist_ok=True)
    fig = plot_dashboard(monthly)
    fig.savefig(OUT_DIR / "week1_dashboard.png", dpi=150, bbox_inches="tight")
    print("그림 저장:", OUT_DIR / "week1_dashboard.png")

    print("\n[분석 질문용 출력]")
    print("최대 상관 lag(개월):", lc.idxmax(), " 상관:", round(lc.max(), 3))
    print(monthly.loc["2021":"2024", ["infl_yoy", "fedfunds"]].idxmax())
