def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

@st.cache  
def read_img(fname,skip_rows=60):
    img = imread(fname)
    
    cm_out = img[skip_rows:-skip_rows,:,:]
    return cm_out
 
