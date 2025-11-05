import streamlit as st
from st_aggrid import AgGrid
import pandas as pd

st.title('Streamlit + AgGrid Check ?')
df = pd.DataFrame({'ID':[1,2,3],'Name':['A','B','C']})
AgGrid(df)
