# -*- coding: utf-8 -*-
"""
银发中国 · 数说老龄化
=====================================================================
中国人口老龄化与养老资源数据可视化（Streamlit 版 · 美化部署版）

技术栈：Python + Streamlit + Plotly
- 数据层复用 data.py（与 Dash 版同一数据源，保证口径一致）
- 11 张 plotly 图表函数与原作品一致，交互/布局为 Streamlit 范式
- 侧边栏为交互控制台（年份区间 / 省份高亮 / 排名范围）+ 章节导航
- 每个图表包入圆角阴影卡片，配色采用「养老红 + 米色」主题
- 部署：streamlit run streamlit_app.py   （默认 8501 端口）
=====================================================================
"""
import inspect
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import data as D

# =====================================================================
# 主题与样式常量（养老红 + 米色）
# =====================================================================
BG = "#F6F2EB"
CARD = "#FFFFFF"
INK = "#2B2A28"
SUB = "#7A7267"
RED = "#A63A2E"
RED_DK = "#7E2A22"
OCHRE = "#C98A4B"
TEAL = "#3F6B62"
INDIGO = "#3F5A70"
SAND = "#D9B382"
GREY = "#B9B2A6"
LINE = "#E7E1D6"

FONT = ('"Microsoft YaHei","PingFang SC","Hiragino Sans GB",'
        '"Noto Sans CJK SC","Source Han Sans SC",sans-serif')
SERIF = ('"Songti SC","SimSun","Source Han Serif SC","Noto Serif CJK SC",serif')

STAGE_COLORS = {
    "重度老龄化": "#8C2F26",
    "中度老龄化": "#C97C5D",
    "老龄化社会": "#D9B382",
    "尚未老龄化": "#B9B2A6",
}


def stage_of(pct: float) -> str:
    if pct >= 20:
        return "重度老龄化"
    if pct >= 14:
        return "中度老龄化"
    if pct >= 7:
        return "老龄化社会"
    return "尚未老龄化"


TPL = go.layout.Template()
TPL.layout.paper_bgcolor = "rgba(0,0,0,0)"
TPL.layout.plot_bgcolor = "rgba(0,0,0,0)"
TPL.layout.font = dict(family=FONT, size=13, color=INK)
TPL.layout.title = dict(font=dict(family=SERIF, size=18, color=INK), x=0.01, xanchor="left")
TPL.layout.margin = dict(l=56, r=28, t=24, b=46)
TPL.layout.hoverlabel = dict(
    font_family=FONT, font_size=13, bgcolor="#FFFFFF", bordercolor=LINE, font_color=INK
)
TPL.layout.legend = dict(
    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
    bgcolor="rgba(0,0,0,0)", font=dict(size=12)
)
TPL.layout.xaxis = dict(
    gridcolor=LINE, zeroline=False, linecolor=LINE,
    tickfont=dict(color=SUB, size=12), title=dict(font=dict(size=12, color=SUB))
)
TPL.layout.yaxis = dict(
    gridcolor=LINE, zeroline=False, linecolor=LINE,
    tickfont=dict(color=SUB, size=12), title=dict(font=dict(size=12, color=SUB))
)

GRAPH_CFG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}

# 兼容 plotly_chart 参数（不同 streamlit 版本 use_container_width / width 不同）
_PCH = inspect.signature(st.plotly_chart).parameters


def plotly_chart(fig, cfg=GRAPH_CFG):
    # 优先使用新版 width 参数（Streamlit >= 1.46），旧版回退 use_container_width
    if "width" in _PCH:
        st.plotly_chart(fig, width="stretch", config=cfg)
    elif "use_container_width" in _PCH:
        st.plotly_chart(fig, use_container_width=True, config=cfg)
    else:
        st.plotly_chart(fig, config=cfg)


def style_axes(fig, height=380, **kw):
    fig.update_layout(template=TPL, height=height, **kw)
    return fig


# =====================================================================
# 图表一：老龄化进程（65+ 人口柱 + 占比折线，双轴）
# =====================================================================
def make_trend_figure(y0: int, y1: int) -> go.Figure:
    rows = [r for r in D.ELDERLY_TREND
            if r["pct65"] is not None and y0 <= r["year"] <= y1]
    years = [r["year"] for r in rows]
    pops = [r["pop65"] for r in rows]
    pcts = [r["pct65"] for r in rows]

    fig = go.Figure()
    fig.add_bar(
        x=years, y=pops, name="65 岁及以上人口（万人）",
        marker=dict(color=SAND, line=dict(color="#FFFFFF", width=1)),
        hovertemplate="%{x} 年<br>65+ 人口 %{y:,.0f} 万人<extra></extra>",
    )
    fig.add_scatter(
        x=years, y=pcts, name="占总人口比重（%）", mode="lines+markers",
        yaxis="y2", line=dict(color=RED, width=3),
        marker=dict(size=7, color=RED, symbol="circle"),
        hovertemplate="%{x} 年<br>占比 %{y:.1f}%<extra></extra>",
    )
    for val, label, dash in [(7, "7% 老龄化社会", "dot"), (14, "14% 中度老龄化", "dash")]:
        fig.add_hline(
            y=val, yref="y2", line=dict(color=SUB, width=1, dash=dash),
            annotation_text=label, annotation_position="top left",
            annotation_font=dict(size=11, color=SUB),
        )
    fig.update_layout(
        yaxis=dict(title="人口（万人）"),
        yaxis2=dict(title="占比（%）", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)", range=[0, max(24, max(pcts) + 4)]),
        xaxis=dict(dtick=5 if (y1 - y0) > 15 else 1),
        hovermode="x unified",
    )
    return style_axes(fig, height=400,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))


# =====================================================================
# 图表二：60+ 与 65+ 占比双线
# =====================================================================
def make_60_65_figure() -> go.Figure:
    rows = [r for r in D.ELDERLY_TREND
            if r["pct60"] is not None and r["pct65"] is not None]
    years = [r["year"] for r in rows]
    fig = go.Figure()
    fig.add_scatter(
        x=years, y=[r["pct60"] for r in rows], name="60 岁及以上占比",
        mode="lines+markers", line=dict(color=OCHRE, width=3), marker=dict(size=7),
        hovertemplate="%{x} 年<br>60+ 占比 %{y:.1f}%<extra></extra>",
    )
    fig.add_scatter(
        x=years, y=[r["pct65"] for r in rows], name="65 岁及以上占比",
        mode="lines+markers", line=dict(color=RED, width=3), marker=dict(size=7),
        hovertemplate="%{x} 年<br>65+ 占比 %{y:.1f}%<extra></extra>",
    )
    fig.add_hrect(y0=20, y1=max(r["pct60"] for r in rows) + 2,
                  fillcolor=RED, opacity=0.06, line_width=0,
                  annotation_text="60+ 超 20%：中度老龄化", annotation_position="top left",
                  annotation_font=dict(size=11, color=SUB))
    fig.update_layout(yaxis=dict(title="占总人口比重（%）"), xaxis=dict(dtick=1),
                      hovermode="x unified")
    return style_axes(fig, height=360)


# =====================================================================
# 图表三：年龄结构三分构成（100% 堆叠）
# =====================================================================
def make_structure_figure() -> go.Figure:
    labels = [r["label"] for r in D.AGE_STRUCTURE]
    child = [r["child"] for r in D.AGE_STRUCTURE]
    labor = [r["labor"] for r in D.AGE_STRUCTURE]
    elder = [r["elder"] for r in D.AGE_STRUCTURE]

    fig = go.Figure()
    fig.add_bar(x=labels, y=child, name="少年儿童", marker=dict(color=TEAL),
                hovertemplate="%{x}<br>少年儿童 %{y:.1f}%<extra></extra>")
    fig.add_bar(x=labels, y=labor, name="劳动年龄人口", marker=dict(color=SAND),
                hovertemplate="%{x}<br>劳动年龄 %{y:.1f}%<extra></extra>")
    fig.add_bar(x=labels, y=elder, name="老年人口", marker=dict(color=RED),
                hovertemplate="%{x}<br>老年人口 %{y:.1f}%<extra></extra>")
    fig.update_layout(barmode="relative", yaxis=dict(title="构成（%）", range=[0, 100]),
                      hovermode="x unified")
    return style_axes(fig, height=360)


# =====================================================================
# 图表四：老年抚养比
# =====================================================================
def make_dependency_figure() -> go.Figure:
    years = [r["year"] for r in D.DEPENDENCY]
    vals = [r["ratio"] for r in D.DEPENDENCY]
    fig = go.Figure()
    fig.add_scatter(
        x=years, y=vals, mode="lines+markers+text", name="老年抚养比",
        line=dict(color=INDIGO, width=3), marker=dict(size=8, color=INDIGO),
        text=[f"{v}" for v in vals], textposition="top center",
        textfont=dict(size=11, color=INDIGO),
        hovertemplate="%{x} 年<br>老年抚养比 %{y:.1f}%<extra></extra>",
    )
    fig.add_hline(y=20, line=dict(color=SUB, width=1, dash="dash"),
                  annotation_text="20%：每 5 名劳动力负担 1 名老人",
                  annotation_position="top left", annotation_font=dict(size=11, color=SUB))
    fig.update_layout(yaxis=dict(title="老年人口 ÷ 劳动年龄人口（%）", range=[0, max(vals) + 6]),
                      xaxis=dict(dtick=1))
    return style_axes(fig, height=360)


# =====================================================================
# 图表五：出生率 / 死亡率 / 自然增长率
# =====================================================================
def make_vital_figure() -> go.Figure:
    years = [r["year"] for r in D.VITAL_STATS]
    fig = go.Figure()
    fig.add_bar(
        x=years, y=[r["birth_pop"] for r in D.VITAL_STATS], name="出生人口（万人）",
        marker=dict(color=SAND, line=dict(color="#FFFFFF", width=1)),
        hovertemplate="%{x} 年<br>出生人口 %{y:,.0f} 万人<extra></extra>",
    )
    fig.add_scatter(x=years, y=[r["birth_rate"] for r in D.VITAL_STATS],
                    name="出生率（‰）", yaxis="y2", mode="lines+markers",
                    line=dict(color=OCHRE, width=3), marker=dict(size=6),
                    hovertemplate="%{x} 年<br>出生率 %{y:.2f}‰<extra></extra>")
    fig.add_scatter(x=years, y=[r["death_rate"] for r in D.VITAL_STATS],
                    name="死亡率（‰）", yaxis="y2", mode="lines+markers",
                    line=dict(color=RED, width=3), marker=dict(size=6),
                    hovertemplate="%{x} 年<br>死亡率 %{y:.2f}‰<extra></extra>")
    fig.update_layout(
        yaxis=dict(title="出生人口（万人）", range=[0, 2100]),
        yaxis2=dict(title="率（‰）", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)", range=[0, 16]),
        xaxis=dict(dtick=1), hovermode="x unified",
    )
    return style_axes(fig, height=400)


# =====================================================================
# 图表六：31 省份方格地图（tile grid map）
# =====================================================================
def make_tilemap_figure(highlight: str = "全部") -> go.Figure:
    rows = sorted(D.PROVINCES_2024, key=lambda r: r["pct65"], reverse=True)
    xs = [r["x"] for r in rows]
    ys = [r["y"] for r in rows]
    vals = [r["pct65"] for r in rows]
    names = [r["name"] for r in rows]
    stages = [stage_of(v) for v in vals]

    fig = go.Figure()
    fig.add_scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(
            symbol="square", size=52,
            color=vals,
            colorscale=[[0, "#F0E2CB"], [0.45, "#D9985C"], [0.75, "#C1553C"], [1, "#8C2F26"]],
            cmin=6, cmax=22,
            line=dict(color="#FFFFFF", width=2),
        ),
        text=[f"{n}<br>{v:.2f}" for n, v in zip(names, vals)],
        textfont=dict(size=10, color="#FFFFFF", family=FONT),
        textposition="middle center",
        customdata=[[n, v, s, r["region"]] for n, v, s, r in zip(names, vals, stages, rows)],
        hovertemplate=("<b>%{customdata[0]}</b>（%{customdata[3]}）<br>"
                       "65+ 占比 %{customdata[1]:.2f}%<br>"
                       "阶段：%{customdata[2]}<extra></extra>"),
    )
    if highlight and highlight != "全部":
        sel = [r for r in D.PROVINCES_2024 if r["name"] == highlight]
        if sel:
            r = sel[0]
            fig.add_scatter(
                x=[r["x"]], y=[r["y"]], mode="markers",
                marker=dict(symbol="square-open", size=96,
                            line=dict(color=INK, width=3)),
                hoverinfo="skip", showlegend=False,
            )
    fig.update_layout(
        xaxis=dict(visible=False, range=[0.2, 9.0]),
        yaxis=dict(visible=False, range=[9.9, 0.4]),
        height=560, showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.update_layout(template=TPL)
    fig.update_yaxes(visible=False, range=[9.9, 0.4])
    fig.update_xaxes(visible=False, range=[0.2, 9.0])
    return fig


# =====================================================================
# 图表七：省份排名条形图
# =====================================================================
def make_rank_figure(mode: str = "全部 31 省份") -> go.Figure:
    rows = sorted(D.PROVINCES_2024, key=lambda r: r["pct65"], reverse=True)
    if mode == "前 10 名":
        rows = rows[:10]
    elif mode == "后 10 名":
        rows = rows[-10:]
    rows = rows[::-1]

    colors = [STAGE_COLORS[stage_of(r["pct65"])] for r in rows]
    fig = go.Figure()
    fig.add_bar(
        x=[r["pct65"] for r in rows], y=[r["name"] for r in rows],
        orientation="h", marker=dict(color=colors, line=dict(color="#FFFFFF", width=1)),
        text=[f"{r['pct65']:.2f}" for r in rows],
        textposition="outside", textfont=dict(size=11, color=SUB),
        customdata=[[stage_of(r["pct65"]), r["region"]] for r in rows],
        hovertemplate=("<b>%{y}</b>（%{customdata[1]}）<br>65+ 占比 %{x:.2f}%<br>"
                       "阶段：%{customdata[0]}<extra></extra>"),
    )
    fig.add_vline(x=D.NATIONAL_PCT65_2024, line=dict(color=INK, width=1.5, dash="dash"),
                  annotation_text=f"全国 {D.NATIONAL_PCT65_2024}%",
                  annotation_position="top", annotation_font=dict(size=11, color=INK))
    fig.update_layout(xaxis=dict(title="65 岁及以上人口占比（%）", range=[0, 26]),
                      showlegend=False, height=max(360, len(rows) * 26 + 120))
    return style_axes(fig, height=max(360, len(rows) * 26 + 120))


# =====================================================================
# 图表八：养老床位与机构设施
# =====================================================================
def make_beds_figure() -> go.Figure:
    years = [r["year"] for r in D.ELDERCARE]
    fig = go.Figure()
    fig.add_bar(x=years, y=[r["comm_beds"] for r in D.ELDERCARE],
                name="社区养老床位", marker=dict(color=SAND),
                hovertemplate="%{x} 年<br>社区床位 %{y:.1f} 万张<extra></extra>")
    fig.add_bar(x=years, y=[r["inst_beds"] for r in D.ELDERCARE],
                name="注册登记机构床位", marker=dict(color=RED),
                hovertemplate="%{x} 年<br>机构床位 %{y:.1f} 万张<extra></extra>")
    fig.add_scatter(x=years, y=[r["facilities"] for r in D.ELDERCARE],
                    name="机构与设施数（万个）", yaxis="y2", mode="lines+markers",
                    line=dict(color=INDIGO, width=3), marker=dict(size=8),
                    hovertemplate="%{x} 年<br>机构与设施 %{y:.1f} 万个<extra></extra>")
    fig.update_layout(
        barmode="stack",
        yaxis=dict(title="养老床位（万张）", range=[0, 900]),
        yaxis2=dict(title="机构与设施（万个）", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)", range=[0, 55]),
        xaxis=dict(dtick=1), hovermode="x unified",
    )
    return style_axes(fig, height=400)


# =====================================================================
# 图表九：护理型床位占比
# =====================================================================
def make_nursing_figure() -> go.Figure:
    years = [r["year"] for r in D.ELDERCARE]
    vals = [r["nursing_pct"] for r in D.ELDERCARE]
    fig = go.Figure()
    fig.add_bar(x=years, y=vals, name="护理型床位占比",
                marker=dict(color=TEAL, line=dict(color="#FFFFFF", width=1)),
                text=[f"{v}%" for v in vals], textposition="outside",
                textfont=dict(size=11, color=TEAL),
                hovertemplate="%{x} 年<br>护理型床位占比 %{y:.1f}%<extra></extra>")
    fig.add_hline(y=55, line=dict(color=RED, width=1.5, dash="dash"),
                  annotation_text="「十四五」规划目标 55%",
                  annotation_position="top left", annotation_font=dict(size=11, color=RED))
    fig.update_layout(yaxis=dict(title="护理型床位占比（%）", range=[0, 80]),
                      xaxis=dict(dtick=1), showlegend=False)
    return style_axes(fig, height=360)


# =====================================================================
# 图表十：每千名老人床位数（派生指标）
# =====================================================================
def make_intensity_figure() -> go.Figure:
    years = [r["year"] for r in D.ELDERCARE]
    vals = [D.beds_per_thousand_elderly(y) for y in years]
    fig = go.Figure()
    fig.add_scatter(x=years, y=vals, mode="lines+markers+text", name="每千名老人床位",
                    line=dict(color=RED, width=3), marker=dict(size=9, color=RED),
                    text=[f"{v}" for v in vals], textposition="top center",
                    textfont=dict(size=11, color=RED),
                    hovertemplate="%{x} 年<br>每千名 65+ 老人 %{y:.1f} 张床位<extra></extra>")
    fig.update_layout(yaxis=dict(title="张 / 每千名 65 岁及以上老人", range=[0, 55]),
                      xaxis=dict(dtick=1), showlegend=False)
    return style_axes(fig, height=360)


# =====================================================================
# 图表十一：情景外推
# =====================================================================
def make_projection_figure() -> go.Figure:
    rows = D.project_pct65(2035)
    actual = [r for r in rows if r["kind"] == "实际"]
    proj = [r for r in rows if r["kind"] == "外推"]
    fig = go.Figure()
    fig.add_scatter(x=[r["year"] for r in actual], y=[r["pct65"] for r in actual],
                    name="实际值（2015—2024）", mode="lines+markers",
                    line=dict(color=RED, width=3), marker=dict(size=7),
                    hovertemplate="%{x} 年<br>占比 %{y:.2f}%<extra></extra>")
    fig.add_scatter(x=[proj[0]["year"] - 1] + [r["year"] for r in proj],
                    y=[actual[-1]["pct65"]] + [r["pct65"] for r in proj],
                    name="线性外推（2025—2035）", mode="lines+markers",
                    line=dict(color=SUB, width=2.5, dash="dash"),
                    marker=dict(size=6, color=SUB),
                    hovertemplate="%{x} 年<br>外推占比 %{y:.2f}%<extra></extra>")
    fig.add_hline(y=20, line=dict(color="#8C2F26", width=1.5, dash="dot"),
                  annotation_text="20% 重度老龄化门槛",
                  annotation_position="top left", annotation_font=dict(size=11, color="#8C2F26"))
    fig.update_layout(yaxis=dict(title="65 岁及以上人口占比（%）"),
                      xaxis=dict(dtick=2), hovermode="x unified")
    return style_axes(fig, height=400)


# =====================================================================
# 静态图缓存（无交互参数，只生成一次）
# =====================================================================
@st.cache_data
def static_figs():
    return {
        "60_65": make_60_65_figure(),
        "structure": make_structure_figure(),
        "dependency": make_dependency_figure(),
        "vital": make_vital_figure(),
        "beds": make_beds_figure(),
        "nursing": make_nursing_figure(),
        "intensity": make_intensity_figure(),
        "projection": make_projection_figure(),
    }


# =====================================================================
# 页面样式（注入 Streamlit）
# =====================================================================
CSS = """
:root{
  --bg:#F6F2EB; --card:#FFFFFF; --ink:#2B2A28; --sub:#7A7267;
  --red:#A63A2E; --red-dk:#7E2A22; --ochre:#C98A4B; --line:#E7E1D6;
}
html{scroll-behavior:smooth;}
body{font-family:"Microsoft YaHei","PingFang SC",sans-serif;}

/* 整体背景与居中 */
[data-testid="stAppViewContainer"]{background:var(--bg);}
[data-testid="stHeader"]{background:var(--bg);}
.main .block-container{max-width:1180px;padding-top:1rem;padding-bottom:3rem;}

/* 侧边栏 */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#FBF8F2 0%,#F3EDE2 100%);
  border-right:1px solid var(--line);}
[data-testid="stSidebar"] .block-container{padding-top:1.4rem;padding-bottom:1.4rem;}

/* Hero 区 */
.hero{background:linear-gradient(135deg,#A63A2E 0%,#7E2A22 100%);color:#fff;border-radius:22px;
  padding:34px 40px 30px;margin:0 0 8px;box-shadow:0 14px 38px rgba(126,42,34,.26);position:relative;overflow:hidden;}
.hero:after{content:"";position:absolute;right:-60px;top:-60px;width:220px;height:220px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.14),rgba(255,255,255,0) 70%);}
.hero .kicker{font-size:12.5px;opacity:.92;letter-spacing:.6px;margin:0 0 10px;}
.hero h1{color:#fff;font-size:36px;line-height:1.2;margin:0 0 6px;font-family:"Microsoft YaHei",sans-serif;font-weight:800;}
.hero .sub{font-size:15px;opacity:.95;margin:0 0 20px;}
.kpi-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:4px;}
.kpi{flex:1 1 168px;background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.24);
  border-radius:14px;padding:14px 16px;backdrop-filter:blur(2px);}
.kpi .v{font-size:23px;font-weight:800;letter-spacing:.3px;}
.kpi .l{font-size:13px;opacity:.96;margin-top:3px;}
.kpi .h{font-size:11px;opacity:.78;margin-top:5px;line-height:1.4;}
.hero .src{font-size:11.5px;opacity:.82;margin-top:18px;border-top:1px solid rgba(255,255,255,.22);padding-top:11px;line-height:1.6;}

/* 章节区块 */
.sec{scroll-margin-top:18px;margin-top:30px;}
.sec-head{display:flex;align-items:center;gap:14px;margin:6px 0 6px;}
.sec-no{font-family:"Songti SC","SimSun",serif;font-size:34px;font-weight:800;color:var(--red);
  line-height:1;opacity:.92;min-width:54px;}
.sec-titles h2{margin:0;font-size:23px;color:var(--ink);font-family:"Microsoft YaHei",sans-serif;font-weight:800;}
.sec-titles .lead{margin:4px 0 0;font-size:14px;color:var(--sub);line-height:1.7;max-width:880px;}
.sec-bar{height:4px;border-radius:3px;background:linear-gradient(90deg,var(--red),rgba(166,58,46,.15));
  margin:10px 0 16px;}

/* 图表卡片 */
.chart-card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px 14px;
  box-shadow:0 6px 20px rgba(43,42,40,.06);margin:6px 0 4px;}
.cc-title{font-size:16px;font-weight:800;color:var(--ink);font-family:"Microsoft YaHei",sans-serif;margin-bottom:2px;}
.cc-cap{font-size:12.5px;color:var(--sub);margin-bottom:8px;line-height:1.6;}
.note{background:#FBF8F2;border-left:4px solid var(--ochre);border-radius:0 8px 8px 0;padding:9px 14px;
  color:#5d564c;font-size:12.5px;line-height:1.65;margin-top:10px;}

/* 双列布局分隔 */
.col-gap{padding:0 6px;}

/* 侧边栏导航 */
.nav-title{font-size:13px;color:var(--sub);letter-spacing:.5px;margin:18px 0 8px;font-weight:700;}
.nav a{display:block;text-decoration:none;color:var(--ink);font-size:14px;padding:8px 12px;border-radius:10px;
  margin:2px 0;border:1px solid transparent;transition:all .15s;}
.nav a:hover{background:rgba(166,58,46,.08);border-color:rgba(166,58,46,.18);}
.nav a .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--red);margin-right:9px;vertical-align:middle;}
.nav a .n{color:var(--red);font-weight:800;margin-right:8px;font-family:"Songti SC",serif;}

/* 回到顶部 */
.to-top{position:fixed;right:22px;bottom:22px;z-index:999;background:var(--red);color:#fff;
  padding:9px 15px;border-radius:24px;font-size:13px;text-decoration:none;box-shadow:0 6px 18px rgba(126,42,34,.35);
  font-family:"Microsoft YaHei",sans-serif;}

/* 数据表 */
.stDataFrame{border-radius:12px;overflow:hidden;border:1px solid var(--line);}

/* 页脚 */
footer{visibility:hidden;}
.foot{text-align:center;color:#9a9183;font-size:12px;margin-top:34px;line-height:1.8;
  border-top:1px solid var(--line);padding-top:18px;}
.foot b{color:var(--ink);}
"""

HERO_HTML = """
<div class="hero">
  <p class="kicker">2026 年第十四届全国大学生数字媒体科技作品及创意竞赛 · 数字艺术与可视化设计类赛项</p>
  <h1>银发中国 · 数说老龄化</h1>
  <p class="sub">基于国家统计局与民政部公开数据的中国人口老龄化与养老资源交互式数据可视化</p>
  <div class="kpi-row">
    <div class="kpi"><div class="v">3.10 亿</div><div class="l">60 岁及以上人口</div><div class="h">占全国 22.0%（2024 年末）</div></div>
    <div class="kpi"><div class="v">2.20 亿</div><div class="l">65 岁及以上人口</div><div class="h">占全国 15.6%（2024 年末）</div></div>
    <div class="kpi"><div class="v">22.8%</div><div class="l">老年人口抚养比</div><div class="h">约 4.4 名劳动力负担 1 名老人</div></div>
    <div class="kpi"><div class="v">799.3 万张</div><div class="l">全国养老床位</div><div class="h">机构 507.7 万 + 社区 291.5 万张</div></div>
    <div class="kpi"><div class="v">79.0 岁</div><div class="l">人均预期寿命</div><div class="h">2024 年数据</div></div>
  </div>
  <p class="src">数据来源：国家统计局《2024 年国民经济和社会发展统计公报》《中国统计年鉴 2025》；
  民政部、全国老龄办《2024 年度国家老龄事业发展公报》</p>
</div>
"""

SIDEBAR_HEAD = """
<div style="background:linear-gradient(135deg,#A63A2E,#7E2A22);border-radius:16px;padding:18px 18px;color:#fff;box-shadow:0 8px 22px rgba(126,42,34,.22);">
  <div style="font-size:19px;font-weight:800;font-family:'Microsoft YaHei',sans-serif;">银发中国</div>
  <div style="font-size:12.5px;opacity:.9;margin-top:3px;">数说老龄化 · 交互式数据可视化</div>
</div>
"""

NAV_HTML = """
<div class="nav">
  <a href="#sec1"><span class="n">01</span><span class="dot"></span>老龄化进程</a>
  <a href="#sec2"><span class="n">02</span><span class="dot"></span>结构透视</a>
  <a href="#sec3"><span class="n">03</span><span class="dot"></span>驱动因素</a>
  <a href="#sec4"><span class="n">04</span><span class="dot"></span>区域差异</a>
  <a href="#sec5"><span class="n">05</span><span class="dot"></span>养老资源</a>
  <a href="#sec6"><span class="n">06</span><span class="dot"></span>趋势展望</a>
  <a href="#sec7"><span class="n">07</span><span class="dot"></span>数据说明</a>
</div>
"""

FOOTER_HTML = """
<div class="foot">
  <b>银发中国 · 数说老龄化</b>　|　中国人口老龄化与养老资源数据可视化作品<br>
  全部数据来源于国家统计局、民政部等公开渠道，外推结果仅为情景示意，不代表官方预测。作品由 Python + Streamlit + Plotly 构建。
</div>
"""


def anchor(aid: str):
    st.markdown(f'<span id="{aid}"></span>', unsafe_allow_html=True)


def section(num: str, title: str, lead: str = ""):
    anchor(f"sec{num}")
    st.markdown(
        f'<div class="sec"><div class="sec-head"><div class="sec-no">{num}</div>'
        f'<div class="sec-titles"><h2>{title}</h2>'
        + (f'<p class="lead">{lead}</p>' if lead else '')
        + '</div></div><div class="sec-bar"></div></div>',
        unsafe_allow_html=True,
    )


def chart_card(fig, *, title=None, caption=None, note=None):
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div class="cc-title">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="cc-cap">{caption}</div>', unsafe_allow_html=True)
    plotly_chart(fig)
    if note:
        st.markdown(f'<div class="note">{note}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# 主程序
# =====================================================================
def main():
    st.set_page_config(
        page_title="银发中国 · 数说老龄化",
        page_icon="🏵️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    st.markdown('<a id="top"></a>', unsafe_allow_html=True)

    # ---------------- 侧边栏：交互控制台 + 章节导航 ----------------
    with st.sidebar:
        st.markdown(SIDEBAR_HEAD, unsafe_allow_html=True)
        st.markdown('<div class="nav-title">交互探索</div>', unsafe_allow_html=True)
        yr = st.slider("老龄化进程 · 年份区间", 1990, 2024, (1990, 2024), step=1, key="yr")
        prov_opts = ["全部"] + [r["name"] for r in sorted(D.PROVINCES_2024, key=lambda x: -x["pct65"])]
        prov = st.selectbox("区域差异 · 高亮省份", prov_opts, key="prov", index=0)
        rank_mode = st.radio("省份排名 · 显示范围",
                             ["全部 31 省份", "前 10 名", "后 10 名"],
                             horizontal=True, key="rankmode")
        st.markdown('<div class="nav-title">章节导航</div>', unsafe_allow_html=True)
        st.markdown(NAV_HTML, unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:11px;color:#9a9183;line-height:1.6;margin-top:18px;'
            'border-top:1px solid #E7E1D6;padding-top:12px;">'
            '数据来源：国家统计局、民政部等公开渠道。外推结果仅为情景示意。</div>',
            unsafe_allow_html=True,
        )

    y0, y1 = int(yr[0]), int(yr[1])
    if y0 >= y1:
        y1 = min(2024, y0 + 1)

    # ---------------- Hero ----------------
    st.markdown(HERO_HTML, unsafe_allow_html=True)
    sf = static_figs()

    # ---------------- S1 老龄化进程 ----------------
    section("1", "老龄化进程：三十年的加速曲线",
            "1990 年我国 65 岁及以上人口占比仅 5.6%，2000 年跨过 7% 的「老龄化社会」门槛，"
            "2021 年突破 14% 进入中度老龄化。同样跨过 7 个百分点，法国用了 115 年，我国只用了 21 年。")
    chart_card(
        make_trend_figure(y0, y1),
        title="图 1　65 岁及以上人口规模与占比（双轴）",
        caption="柱形为 65 岁及以上人口规模，红色折线为占总人口比重；可拖动左侧年份区间观察不同阶段。",
        note="读图：2015 年后曲线斜率明显抬升，占比年均提高约 0.5 个百分点，老龄化进入加速期。",
    )
    c1, c2 = st.columns(2)
    with c1:
        chart_card(
            sf["60_65"],
            title="图 2　60+ 与 65+ 占比双线对比",
            caption="60 岁口径反映养老服务覆盖人群，65 岁口径为国际可比口径，两线间距体现低龄老人规模。",
            note="读图：两线间距由 2015 年的 5.6 个百分点扩大至 2024 年的 6.4 个百分点，"
                 "说明 60—64 岁低龄老人规模持续扩大，是当前养老服务需求的主要增量来源。",
        )
    with c2:
        chart_card(
            sf["structure"],
            title="图 3　人口年龄结构三分构成演变",
            caption="对比第六次人口普查、第七次人口普查与 2024 年统计公报口径。",
            note="口径提示：2024 年公报为 0—15 岁 / 16—59 岁 / 60 岁及以上，与普查年份口径略有差异。",
        )

    # ---------------- S2 结构透视 ----------------
    section("2", "结构透视：谁在变老，谁在养",
            "老龄化不是孤立的数字，而是人口结构整体重排的结果：少儿比重趋稳、劳动年龄人口收缩、老年比重抬升。")
    c1, c2 = st.columns(2)
    with c1:
        chart_card(
            sf["dependency"],
            title="图 4　老年人口抚养比（2015—2024）",
            caption="老年人口数与 16—64 岁劳动年龄人口数之比，衡量代际供养压力。",
            note="读图：十年间抚养比由 14.3% 升至 22.8%，相当于每名老人对应的劳动力从 7.0 人降至 4.4 人。",
        )

    # ---------------- S3 驱动因素 ----------------
    section("3", "驱动因素：少子化与长寿化的双重作用",
            "老龄化程度由「底部」（出生人口减少）与「顶部」（寿命延长）共同决定。近年出生人口下行是当前老龄化的主要推力。")
    chart_card(
        sf["vital"],
        title="图 5　出生人口、出生率与死亡率（2016—2024）",
        caption="柱形为出生人口规模，右轴曲线为出生率与死亡率；2022 年起自然增长率转负。",
        note="读图：出生率由 2016 年的 12.95‰ 降至 2024 年的 6.77‰，"
             "出生率与死亡率曲线在 2022 年前后交叉，人口自然增长进入负增长区间。",
    )

    # ---------------- S4 区域差异 ----------------
    section("4", "区域差异：一幅不均匀的中国",
            "31 个省份中，辽宁已进入重度老龄化，而西藏尚未跨过 7% 的门槛；"
            "省际最大差距达 15.6 个百分点，老龄化呈现明显的「北老南轻、东高西低」格局。")
    chart_card(
        make_tilemap_figure(prov),
        title="图 6　31 省份 65 岁及以上人口占比方格地图（2024）",
        caption="方格按相对方位排布，颜色深浅表示老龄化程度，仅作空间示意，不代表行政边界。可在左侧高亮省份。",
        note="说明：采用方格地图（tile grid map）替代传统分级统计地图，"
             "可避免面积大小对读数的干扰，让每个省份获得同等视觉权重。",
    )
    chart_card(
        make_rank_figure(rank_mode),
        title="图 7　省份老龄化程度排名",
        caption="颜色对应国际老龄化阶段划分，虚线为全国平均水平 15.6%。可在左侧切换显示范围。",
        note="读图：19 个省份 65+ 占比超过 14% 进入中度老龄化，其中 12 个位于北方地区；"
             "广东（10.18%）虽为经济大省，但受益于年轻劳动力流入，老龄化程度仅列第 29 位。",
    )

    # ---------------- S5 养老资源 ----------------
    section("5", "养老资源：总量增长与结构转型",
            "养老床位总量在 2022 年达到 829.4 万张的峰值后回落，但护理型床位占比由 2020 年的 48% 提升至 2024 年的 65.7%，"
            "供给正在从「有床位」转向「有护理能力的床位」。")
    c1, c2 = st.columns(2)
    with c1:
        chart_card(
            sf["beds"],
            title="图 8　养老床位与机构设施数（2020—2024）",
            caption="堆叠柱为机构床位与社区床位构成，折线为养老机构与设施总数。",
            note="读图：机构与设施数五年增长 23.4%，但床位总量小幅回落，"
                 "反映供给侧由规模扩张转向结构优化。",
        )
    with c2:
        chart_card(
            sf["nursing"],
            title="图 9　护理型床位占比提升",
            caption="护理型床位比例是衡量养老服务专业化的核心指标。",
            note="读图：2023 年首次超过《「十四五」国家老龄事业发展和养老服务体系规划》55% 的目标值，"
                 "2024 年进一步提升至 65.7%。",
        )
    chart_card(
        sf["intensity"],
        title="图 10　每千名 65 岁及以上老人拥有床位数（派生指标）",
        caption="计算式 = 当年养老床位总数 ÷ 当年 65 岁及以上人口 × 1000，用于衡量相对供给强度。",
        note="读图：该指标由 2020 年的 43.2 张降至 2024 年的 36.3 张。"
             "床位总量回落与老年人口快速增长叠加，意味着相对供给强度持续走弱，"
             "这是总量指标容易掩盖的结构性压力。",
    )

    # ---------------- S6 趋势展望 ----------------
    section("6", "趋势展望：通往 2035",
            "以 2015—2024 年 65 岁及以上人口占比序列拟合线性趋势并向后外推，用于呈现「若维持近十年增速」的示意情景。")
    chart_card(
        sf["projection"],
        title="图 11　65 岁及以上人口占比情景外推（2015—2035）",
        caption="实线为实际值，虚线为本作品线性外推结果，点线为 20% 重度老龄化门槛。",
        note=f"<b>重要声明：</b>{D.PROJECT_NOTE}",
    )

    # ---------------- S7 数据说明 ----------------
    section("7", "数据说明与方法",
            "本作品严格遵循竞赛对数据可视化作品的要求，完整披露数据来源、处理方法、信息结构与可视化逻辑。")
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="cc-title">数据来源清单</div>', unsafe_allow_html=True)
    st.markdown('<div class="cc-cap">逐条记录指标、发布机构与口径说明，全部为官方公开数据。</div>',
                unsafe_allow_html=True)
    src_rows = [
        {"模块": s.module, "指标": s.indicator, "来源": s.source, "口径说明": s.note or "—"}
        for s in D.SOURCE_TABLE
    ]
    st.dataframe(pd.DataFrame(src_rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="cc-title">数据处理方法</div>', unsafe_allow_html=True)
    st.markdown("""
    - 采集：全部指标取自国家统计局、民政部公开发布文件，逐条记录来源与发布年份。
    - 清洗：统一量纲（万人 / 万张 / 百分比），对 2010 年前后人口口径差异单独标注。
    - 缺失处理：1990—2013 年部分年份无 60 岁口径数据，保留为空并留白，不做插值虚构。
    - 派生指标：每千名老人床位数、抚养比倒数等均在代码中给出计算式，可复算。
    - 外推：仅对 2015—2024 年序列做一元线性拟合，明确标注为非官方预测。
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="cc-title">信息结构与可视化逻辑</div>', unsafe_allow_html=True)
    st.markdown("""
    - 叙事主线：规模（有多大）→ 结构（谁在变老）→ 成因（为什么）→ 空间（哪里最老）→ 供给（怎么应对）→ 未来（走向何处）。
    - 视觉编码：颜色仅用于表示老龄化程度与阶段，采用单色系深浅，避免彩虹色误导；红色系随程度加深，与「老龄化加剧」的语义一致。
    - 图表选择：时间趋势用折线、构成用堆叠、排名用条形、空间分布用方格地图以消除面积权重偏差。
    - 交互设计：年份区间滑块、省份高亮、排名范围切换，用于支持自主探索而非改变结论。
    - 每张图均配「读图提示」，把图形直接翻译为可核验的结论。
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.info(
        "人工智能工具使用情况说明：本作品使用 AI 编程助手辅助完成代码框架编写、调试与文案润色；"
        "选题立意、指标体系与叙事结构设计、图表类型与视觉编码决策、结论撰写与逐条数据核验均由团队人工完成。"
        "提交前请团队按实际情况核对修改，确保与实际创作过程一致。"
    )

    st.markdown(FOOTER_HTML, unsafe_allow_html=True)
    st.markdown('<a href="#top" class="to-top">↑ 回到顶部</a>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
