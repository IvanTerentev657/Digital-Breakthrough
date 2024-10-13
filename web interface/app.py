import streamlit as st
import pypandoc


import os

from pdf_to_json import pdf_to_json, pretty_save_json

from AtomSolvingMethod import CaseAndReglaments

def save_uploaded_file(uploadedfile):
  with open(os.path.join("tempDir",uploadedfile.name),"wb") as f:
     f.write(uploadedfile.getbuffer())
  return os.path.join("tempDir",uploadedfile.name)


if __name__ == "__main__":
    with st.expander("Use-cases"):
        st.header("Use-cases")
        uploaded_usecases = st.file_uploader(
            "Choose a docx file", accept_multiple_files=True, type=['docx', 'doc'], key=1,
        )
    
    with st.expander("Reglament"):
        st.header("Reglament")
        uploaded_reglaments = st.file_uploader(
            "Choose a pdf file", accept_multiple_files=True, type=['pdf'], key=2,
        )
        
    result = st.button('Run')
    
    k = 0
    
    if result:
        for uploaded_file in uploaded_usecases:
            with st.container(border = True):
                docxFilename = save_uploaded_file(uploaded_file)
                pypandoc.convert_file(docxFilename, 'plain', outputfile=os.path.join("Usecases",str(uploaded_file.name)[:-5] + '.txt'))
        
        for uploaded_file in uploaded_reglaments:
            with st.container(border = True):
                docxFilename = save_uploaded_file(uploaded_file)
                pretty_save_json(pdf_to_json(docxFilename), os.path.join("Reglaments",str(uploaded_file.name)[:-5] + '.json'))
        
        st.success('All files are encoded')
        
        text = ''
        
        for uploaded_case in uploaded_usecases:
            text += CaseAndReglaments(os.path.join("Usecases",str(uploaded_case.name)[:-5] + '.txt'),  'Reglaments')
        st.download_button("Download result", text) # there can be path to txt file
                