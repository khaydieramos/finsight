from pathlib import Path
import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data_utils import load_transactions, monthly_cashflow, spending_by_category, summarize
from db import initialize, import_transactions, fetch_transactions
from reporting import monthly_report, category_report, summary_report
from assistant import answer

st.set_page_config(page_title="FinSight | Financial Intelligence", page_icon=str(Path(__file__).parent / "finsight_icon.png"), layout="wide", initial_sidebar_state="expanded")
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [data-testid="stApp"] {font-family:Inter,system-ui,sans-serif;}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {background:#f4f7fc; color:#12213d;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stMainBlockContainer"], .block-container {max-width: none !important; width:100% !important; padding:1.6rem 2.1rem 3rem !important;}
[data-testid="stSidebar"] {background:linear-gradient(170deg,#1c304f,#101f37);}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] small {color:#e8f0ff !important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:9px 7px;border-radius:9px;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:#2b4775;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#bdcce3 !important;}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {background:#243958;color:white;border-color:#3b5174;}
h1,h2,h3 {color:#0c1940;letter-spacing:-.025em;}
.hero-title {font-size:clamp(1.8rem,2.5vw,2.5rem);font-weight:800;color:#0c1940;letter-spacing:-1px;line-height:1.2;margin-bottom:8px;}
.hero-title span {color:#2869f5;}
.finsight-subtitle {font-size:.95rem;color:#607293;margin-bottom:1.15rem;}
.kpi {background:white;border:1px solid #e7edf7;border-radius:15px;padding:21px 18px;box-shadow:0 4px 18px rgba(24,49,88,.055);min-height:144px;}
.kpi-label {font-size:.87rem;color:#5c6b85;font-weight:600;}
.kpi-value {font-size:clamp(1.22rem,1.6vw,1.8rem);font-weight:800;color:#0c1940;margin:10px 0;letter-spacing:-.03em;}
.kpi-foot {font-size:.76rem;color:#71809b;}
.kpi-icon {font-size:1.5rem;float:right;background:#eef4ff;border-radius:12px;padding:7px;}
.section-heading {font-size:1.12rem;font-weight:800;color:#0c1940;margin:0 0 4px;}
.section-sub {font-size:.8rem;color:#71809b;margin:0 0 10px;}
[data-testid="stVerticalBlockBorderWrapper"] {background:#fff;border:1px solid #e7edf7 !important;border-radius:15px !important;box-shadow:0 4px 18px rgba(24,49,88,.045);}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:15px !important;}
[data-testid="stDataFrame"] {border:1px solid #e8edf5;border-radius:11px;overflow:hidden;}
.stButton > button[kind="primary"], .stDownloadButton button[kind="primary"] {background:#2563eb;border-radius:10px;border:0;}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {border-radius:10px;}
[data-testid="stPlotlyChart"] {width:100%;}
@media(max-width:850px) {.block-container,[data-testid="stMainBlockContainer"] {padding:1rem .9rem 2rem !important;}.kpi{min-height:125px;padding:13px}.kpi-value{font-size:1.3rem}}


/* Final visual polish */
html {font-size: 17px;}
[data-testid="stSidebar"] {min-width: 255px;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {font-size: .92rem !important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding: 11px 9px;}
.brand {font-size:1.75rem;letter-spacing:-.045em;font-weight:800;color:white;line-height:1.3;margin:4px 0 7px;}
.brand span {color:#fff;}
.hero-title {font-size:clamp(2rem,2.6vw,2.7rem);margin-top:4px;}
.finsight-subtitle {font-size:1rem;}
.kpi {min-height:156px;padding:20px 22px;}
.kpi-top {display:flex;justify-content:space-between;align-items:center;gap:8px;}
.kpi-label {font-size:.95rem;}
.kpi-value {font-size:clamp(1.55rem,1.8vw,2.05rem);margin:12px 0 10px;}
.kpi-foot {font-size:.82rem;}
.kpi-icon {float:none;display:inline-flex;align-items:center;justify-content:center;min-width:45px;height:45px;font-size:1.4rem;}
.kpi-icon.green {background:#dcf8e9;color:#138b58;}
.kpi-icon.red {background:#ffe5ea;color:#e43b5b;}
.kpi-icon.blue {background:#e4efff;color:#2563eb;}
.kpi-icon.purple {background:#eee8ff;color:#7549d7;}
.section-heading {font-size:1.27rem;}
.section-sub {font-size:.9rem;}
[data-testid="stVerticalBlockBorderWrapper"] {background:#fff !important; padding:4px !important;}
[data-testid="stDataFrame"] {font-size:.94rem;}
[data-testid="stTextArea"] textarea {background:#fff !important;}
.assistant-hint {color:#6c7c98;font-size:.76rem;font-weight:800;letter-spacing:.075em;margin:7px 0 2px;}
[data-testid="stButton"] button {border-radius:10px;font-weight:600;min-height:39px;}
[data-testid="stMain"] [data-testid="stHorizontalBlock"] {row-gap:12px;}
@media(max-width:1050px) {.kpi{padding:14px;min-height:136px}.kpi-value{font-size:1.4rem}}

/* Professional vector icon system */
.fi-icon {display:inline-block;vertical-align:middle;flex-shrink:0;}
.brand {display:flex;align-items:center;gap:12px;}
.brand-mark {color:#4a8bff;display:inline-flex;align-items:center;justify-content:center;}
.brand-mark svg {width:32px;height:32px;stroke-width:2.8;}
.kpi-icon svg {width:26px;height:26px;}
.section-heading {display:flex;align-items:center;gap:9px;}
.section-heading svg {color:#2869f5;}
/* Consistent, icon-free sidebar navigation. Native radio circles remain visible. */
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 12px !important;
    padding: 12px 14px !important;
    margin: 0 !important;
    min-height: 48px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    border-radius: 12px !important;
    position: relative !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label::before {
    content: none !important;
    display: none !important;
    background-image: none !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {
    flex: 0 0 auto !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label p {
    margin: 0 !important;
    line-height: 1.4 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    background: #294a82 !important;
}
</style>
"""

ICON_PATHS = {'chart': '<rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/>', 'wallet': '<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 9h18"/><path d="M16 14h2"/>', 'coins': '<ellipse cx="9" cy="6" rx="6" ry="3"/><path d="M3 6v5c0 1.7 2.7 3 6 3s6-1.3 6-3V6M3 11v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"/><path d="M16 11c3 0 5 1 5 3s-2 3-5 3M16 17c3 0 5 1 5 3"/>', 'credit-card': '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>', 'pie': '<path d="M21 12a9 9 0 1 1-9-9v9z"/><path d="M13 2a9 9 0 0 1 9 9h-9z"/>', 'file-text': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h8"/>', 'home': '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21v-8h6v8"/>', 'message': '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-.9L3 21l1.9-5A8.6 8.6 0 0 1 3 11.5a9 9 0 0 1 18 0z"/>', 'download': '<path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>', 'database': '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>', 'upload': '<path d="M12 16V3m-5 5 5-5 5 5M4 16v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4"/>', 'sparkles': '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3zM19 17l.8 2.2L22 20l-2.2.8L19 23l-.8-2.2L16 20l2.2-.8L19 17z"/>', 'check': '<path d="m4 12 5 5L20 6"/>', 'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>', 'arrow-up': '<path d="M12 19V5m-6 6 6-6 6 6"/>', 'line': '<path d="M3 17l6-6 4 3 8-9"/><path d="M3 3v18h18"/>'}

def icon(name, size=22, css_class=""):
    """Small inline SVG icons, no emoji or external icon library required."""
    paths = ICON_PATHS[name]
    return (f'<svg class="fi-icon {html.escape(css_class)}" width="{int(size)}" height="{int(size)}" '
            'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{paths}</svg>')

st.markdown(CSS, unsafe_allow_html=True)

def money(n): return f"${n:,.2f}"

def set_suggested_question(key, question):
    st.session_state[key] = question

def question_composer(prefix, start, end):
    """Reusable assistant composer with clickable suggested questions."""
    examples = [
        ('Highest expense month', 'Which month had the highest expenses?'),
        ('Top spending categories', 'What were my top spending categories?'),
        ('Monthly cash flow', 'Show monthly cash flow'),
        ('Income and net cash flow', 'What is my total income and net cash flow?'),
    ]
    st.markdown('<div class="assistant-hint">TRY A SUGGESTED QUESTION</div>', unsafe_allow_html=True)
    row1 = st.columns(2, gap='small')
    row2 = st.columns(2, gap='small')
    for (label, prompt), col in zip(examples, [*row1, *row2]):
        with col:
            st.button(label, key=f'{prefix}_suggest_{label}', use_container_width=True,
                      on_click=set_suggested_question, args=(f'{prefix}_question', prompt))
    st.text_area('Ask a question about your financial data', key=f'{prefix}_question',
                 placeholder='e.g. Which month had the highest expenses?', height=86)
    use_llm = st.toggle('Use OpenAI to interpret my question', value=False, key=f'{prefix}_llm')
    if st.button('Get answer', type='primary', key=f'{prefix}_ask', use_container_width=True):
        render_answer(st.session_state.get(f'{prefix}_question', ''), start, end, use_llm)

def section(title,subtitle="",icon_name=None):
    st.markdown(f'<div class="section-heading">{icon(icon_name,21) if icon_name else ""}{html.escape(title)}</div><div class="section-sub">{html.escape(subtitle)}</div>',unsafe_allow_html=True)
def icon_svg(name, size=22):
    return icon(name, size)

def kpi(label,value,icon,foot):
    tone = {'Total Income':'green','Income':'green','Total Expenses':'red','Expenses':'red','Net Cash Flow':'blue','Net':'blue'}.get(label,'purple')
    st.markdown(
        f'<div class="kpi"><div class="kpi-top"><span class="kpi-label">{html.escape(label)}</span>'
        f'<span class="kpi-icon {tone}">{icon_svg(icon, 26)}</span></div>'
        f'<div class="kpi-value">{html.escape(str(value))}</div>'
        f'<div class="kpi-foot">{html.escape(foot)}</div></div>',
        unsafe_allow_html=True)

def monthly_figure(frame):
    """Grouped income/expense bars with net cash-flow overlay."""
    data = frame.copy()
    data['month'] = data['month'].astype(str)
    if 'net' not in data.columns:
        data['net'] = data['income'] - data['expenses']
    fig = go.Figure()
    fig.add_bar(x=data['month'], y=data['income'], name='Income', marker_color='#35B779',
                hovertemplate='%{x}<br>Income: $%{y:,.2f}<extra></extra>')
    fig.add_bar(x=data['month'], y=data['expenses'], name='Expenses', marker_color='#F45B70',
                hovertemplate='%{x}<br>Expenses: $%{y:,.2f}<extra></extra>')
    fig.add_scatter(x=data['month'], y=data['net'], name='Net cash flow', mode='lines+markers',
                    line=dict(color='#2563EB', width=3), marker=dict(size=8, color='#2563EB',
                    line=dict(color='white', width=2)),
                    hovertemplate='%{x}<br>Net: $%{y:,.2f}<extra></extra>')
    fig.update_layout(barmode='group', bargap=.28)
    return chart_style(fig, 370)

def chart_style(fig,height=340):
    fig.update_layout(height=height,margin=dict(l=12,r=12,t=38,b=14),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Inter, Arial',color='#526381',size=13),legend=dict(orientation='h',y=1.18,x=0,font=dict(size=13)),hovermode='x unified')
    fig.update_xaxes(showgrid=False,tickfont=dict(size=12))
    fig.update_yaxes(gridcolor='#edf1f7',zerolinecolor='#edf1f7',tickfont=dict(size=12),tickprefix='$',separatethousands=True)
    return fig

with st.sidebar:
    st.markdown(f'<div class="brand"><span class="brand-mark">{icon("chart",32)}</span><span>FinSight</span></div>', unsafe_allow_html=True)
    st.caption('Financial intelligence · PostgreSQL + AI')
    st.divider()
    page=st.radio('Navigation',['Dashboard','Transactions','SQL Financial Reports','Ask FinSight (AI)','Export & Settings'],label_visibility='collapsed')
    st.divider()
    st.markdown(f'{icon("database",17)} **Data Source**', unsafe_allow_html=True)
    source_mode=st.selectbox('Choose source',['PostgreSQL','CSV prototype'],label_visibility='collapsed')
    st.caption('Connected to PostgreSQL' if source_mode=='PostgreSQL' else 'CSV preview mode')
    st.divider()
    st.markdown(f'{icon("upload",17)} **Import Transactions**', unsafe_allow_html=True)
    uploaded=st.file_uploader('Choose a CSV file',type='csv',label_visibility='collapsed')
    source=uploaded if uploaded is not None else Path(__file__).parent/'data'/'sample_transactions.csv'
    if source_mode=='PostgreSQL' and st.button('Import CSV into PostgreSQL',use_container_width=True):
        try:
            initialize()
            import_transactions(load_transactions(source))
            st.success('Import complete. Duplicates are skipped.')
            st.rerun()
        except Exception as exc: st.error(f'Import failed: {exc}')
    st.caption('Use synthetic data for this portfolio demo. Do not upload confidential records.')

try:
    if source_mode=='PostgreSQL':
        initialize()
        df=fetch_transactions()
    else: df=load_transactions(source)
except Exception as exc:
    st.error(f'Could not load transactions: {exc}')
    st.stop()

st.markdown('<div class="hero-title">Welcome to <span>FinSight</span></div>',unsafe_allow_html=True)
st.markdown('<div class="finsight-subtitle">Your financial analytics workspace, powered by PostgreSQL and AI.</div>',unsafe_allow_html=True)
if df.empty:
    st.info('No transactions found. Import the sample CSV from the sidebar to get started.')
    st.stop()
first,last=df['date'].min().date(),df['date'].max().date()
period=st.date_input('Reporting period',value=(first,last),min_value=first,max_value=last,key='global_period')
if not isinstance(period,(tuple,list)) or len(period)!=2:
    st.info('Select a start date and end date.')
    st.stop()
start,end=period
period_df=df[(df['date'].dt.date>=start)&(df['date'].dt.date<=end)].copy()
if source_mode=='PostgreSQL':
    try:
        stats=summary_report(start,end)
        monthly=monthly_report(start,end)
        spending=category_report(start,end)
    except Exception as exc:
        st.error(f'SQL reporting failed: {exc}')
        st.stop()
else:
    stats=summarize(period_df)
    stats['transaction_count']=len(period_df)
    monthly=monthly_cashflow(period_df)
    spending=spending_by_category(period_df)


def render_answer(question,start,end,use_llm):
    if not question.strip():
        st.warning('Enter a question first.')
        return
    try:
        result=answer(question,start,end,use_llm=use_llm)
        st.success(result['message'])
        frame=result['data']
        if frame is not None and not frame.empty:
            st.dataframe(frame,hide_index=True,use_container_width=True)
            if result['operation'] in ('monthly','highest_expense_month'):
                fig=px.bar(frame,x='month',y=['income','expenses'],barmode='group',color_discrete_sequence=['#3fb982','#fa5a72'])
            else:
                fig=px.bar(frame,x='category',y='spent',color_discrete_sequence=['#2869f5'])
            st.plotly_chart(chart_style(fig,280),use_container_width=True)
    except Exception as exc:
        st.error(f'Could not answer question: {exc}')

if page=='Dashboard':
    cols=st.columns(4,gap='medium')
    cards=[('Total Income',money(stats['income']),'coins','Income during selected period'),('Total Expenses',money(stats['expenses']),'credit-card','Spending during selected period'),('Net Cash Flow',money(stats['net']),'pie','Income minus expenses'),('Transactions',f"{stats['transaction_count']:,}",'file-text','Transactions in selected period')]
    for col,card in zip(cols,cards):
        with col:kpi(*card)
    left,right=st.columns([1.5,1],gap='medium')
    with left:
        with st.container(border=True):
            section('Monthly Income vs. Expenses','Financial performance over time')
            if not monthly.empty:
                st.plotly_chart(monthly_figure(monthly),use_container_width=True)
            else:st.info('No monthly data in this period.')
    with right:
        with st.container(border=True):
            section('Top Spending Categories','Where your expenses are going')
            if not spending.empty:
                fig=px.pie(spending,names='category',values='spent',hole=.62,color_discrete_sequence=['#2664aa','#4998ec','#67c5e3','#65cc90','#ffce65','#ff9d4d','#fb647a','#9ca9ba'])
                fig.update_traces(textposition='inside',textinfo='percent',marker=dict(line=dict(color='white',width=2)))
                total_spent = float(spending['spent'].sum())
                fig.add_annotation(text=f'<span style="font-size:13px;color:#64748b">Total expenses</span><br><b>{money(total_spent)}</b>',
                                   x=.5,y=.5,showarrow=False,font=dict(size=17,color='#13234a'))
                fig.update_layout(showlegend=True,legend=dict(orientation='v',x=1.02,y=.95,font=dict(size=13)),
                                  margin=dict(l=4,r=8,t=15,b=15),height=370,paper_bgcolor='rgba(0,0,0,0)',
                                  font=dict(family='Inter, Arial',color='#526381',size=13))
                st.plotly_chart(fig,use_container_width=True)
            else:st.info('No expenses in this period.')
    left,right=st.columns([1.15,1],gap='medium')
    with left:
        with st.container(border=True):
            section('Recent Transactions','Latest records from your selected data source')
            recent=period_df.sort_values('date',ascending=False).head(7)
            st.dataframe(recent,use_container_width=True,hide_index=True,height=300,column_config={'date':st.column_config.DatetimeColumn('Date',format='MMM D, YYYY'),'amount':st.column_config.NumberColumn('Amount',format='$%.2f')})
            if st.button('View all transactions',use_container_width=True):st.session_state['show_all']=not st.session_state.get('show_all',False)
            if st.session_state.get('show_all'):st.dataframe(period_df.sort_values('date',ascending=False),hide_index=True,use_container_width=True,height=360)
    with right:
        with st.container(border=True):
            section('Ask FinSight | Financial Assistant','Ask questions about your finances in natural language','message')
            if source_mode=='PostgreSQL':
                st.caption('Approved read-only SQL reports · Transaction rows stay in PostgreSQL')
                question_composer('home', start, end)
            else:st.info('Select PostgreSQL in the sidebar to use the AI assistant.')
elif page=='Transactions':
    section('Transactions','Search, filter and export your financial records')
    search=st.text_input('Search description or category',placeholder='e.g. Grocery, Salary, Rent')
    cats=sorted(period_df['category'].dropna().unique().tolist())
    chosen=st.multiselect('Categories',cats,default=cats)
    view=period_df[period_df['category'].isin(chosen)]
    if search:view=view[view['description'].astype(str).str.contains(search,case=False,na=False)|view['category'].astype(str).str.contains(search,case=False,na=False)]
    st.dataframe(view.sort_values('date',ascending=False),hide_index=True,use_container_width=True)
    st.download_button('Download filtered transactions',view.to_csv(index=False),file_name='finsight_transactions.csv',mime='text/csv')
elif page=='SQL Financial Reports':
    section('SQL Financial Reports','Database-powered aggregations and downloadable reporting')
    if source_mode!='PostgreSQL':st.warning('Select PostgreSQL to run SQL financial reports.')
    else:
        a,b,c,d=st.columns(4)
        for col,card in zip((a,b,c,d),[('Income',money(stats['income']),'coins','Selected period'),('Expenses',money(stats['expenses']),'credit-card','Selected period'),('Net',money(stats['net']),'pie','Selected period'),('Transactions',str(stats['transaction_count']),'file-text','Selected period')]):
            with col:kpi(*card)
        with st.container(border=True):
            section('Monthly SQL Summary','Aggregated by PostgreSQL')
            st.dataframe(monthly,hide_index=True,use_container_width=True)
            if not monthly.empty:
                st.plotly_chart(monthly_figure(monthly),use_container_width=True)
            st.download_button('Download monthly report',monthly.to_csv(index=False),file_name='finsight_monthly_sql_report.csv',mime='text/csv')
        with st.container(border=True):
            section('Spending by Category','SQL aggregation of expense transactions')
            st.dataframe(spending,hide_index=True,use_container_width=True)
            st.download_button('Download category report',spending.to_csv(index=False),file_name='finsight_category_sql_report.csv',mime='text/csv')
elif page=='Ask FinSight (AI)':
    section('Ask FinSight | Financial Assistant','Natural-language questions grounded in approved SQL reports','message')
    if source_mode!='PostgreSQL':st.warning('Select PostgreSQL to enable financial questions.')
    else:
        st.info('OpenAI classifies the question into an approved report type. PostgreSQL calculates the answer. No transaction rows are sent to the model.')
        question_composer('ai', start, end)
else:
    section('Export & Settings','Download financial reports and manage your data source')
    st.write(f'**Current source:** {source_mode}  ·  **Reporting period:** {start} to {end}')
    st.download_button('Download transactions CSV',period_df.to_csv(index=False),file_name='finsight_transactions.csv',mime='text/csv')
    if source_mode=='PostgreSQL':
        st.download_button('Download monthly SQL report',monthly.to_csv(index=False),file_name='finsight_monthly_report.csv',mime='text/csv')
        st.download_button('Download category SQL report',spending.to_csv(index=False),file_name='finsight_category_report.csv',mime='text/csv')
    st.caption('This is a portfolio prototype using synthetic transactions, not a production banking application.')
