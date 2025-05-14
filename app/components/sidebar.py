import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("智能合同审查系统")
        
        # 导航菜单
        page = st.radio(
            "导航菜单",
            ["上传合同", "合同分析", "分析进度", "审查报告", "预算监控", "价格库管理"]
        )
        
        # 显示系统状态
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 系统状态")
        st.sidebar.success("✓ 系统运行正常")
        
        # 显示版本信息
        st.sidebar.markdown("---")
        st.sidebar.markdown("版本：v1.0.0")
        
    return page