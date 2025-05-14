import streamlit as st
import os
from datetime import datetime

def render_upload_page():
    st.title("合同上传")
    
    # 文件上传区域
    uploaded_file = st.file_uploader(
        "选择合同文件",
        type=["pdf", "docx", "txt"],
        help="支持PDF、Word和文本文件格式"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        st.success(f"文件 '{uploaded_file.name}' 上传成功！")
        
        # 文件基本信息
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"文件大小: {uploaded_file.size/1024:.2f} KB")
        with col2:
            st.write(f"上传时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 处理选项
        st.markdown("### 处理选项")
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox(
                "处理优先级",
                ["普通", "加急", "特急"]
            )
        with col2:
            notify = st.checkbox("处理完成后通知我", value=True)
        
        # 开始处理按钮
        if st.button("开始处理", type="primary"):
            # TODO: 实现文件处理逻辑
            st.info("文件已提交处理，请在'分析进度'页面查看进度。")
    
    # 使用说明
    with st.expander("使用说明"):
        st.markdown("""
        1. 点击上方区域或拖拽文件到该区域上传合同文件
        2. 支持的文件格式：PDF、Word文档(.docx)、文本文件(.txt)
        3. 文件大小限制：50MB
        4. 上传完成后，选择处理优先级并点击"开始处理"
        5. 可以在"分析进度"页面查看处理状态
        """)
