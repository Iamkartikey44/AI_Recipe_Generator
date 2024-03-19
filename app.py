from openai import OpenAI
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import streamlit as st
import requests

st.title("AI Recipe Generator😋")
load_dotenv()
client = OpenAI()
output_format = (
    """ 
        <h1> Fun Title of recipe </h1>
        <h1> Table of Contents</h1> <li> links of content </li>
        <h1> Introduction </h1><p> dish introduction</p>
        <h1> Country of Origin </h1><p> Country of Origin</p>
        <h1> Ingredients <h1><li>Ingredients list </li>
        <h1> FAQ </h1><p>question answers</p>
    """) 
recipe  = st.text_input("Enter your prompt",value='Pasta')
image_prompt = recipe + " realistic, cinematic"
def generate_image_openai(client,prompt,model='dall-e-3',size='1024x1024',n=1):
    response = client.images.generate(
        model = model,
        prompt=prompt,
        size=size,
        n=n
    )
    image_url = response.data[0].url
    image = requests.get(image_url)
    image = Image.open(BytesIO(image.content))

    return image
def generate_recipe_description(client,prompt,text_area_placeholder=None,
                                model='gpt-3.5-turbo',temperature=0.7,
                                max_tokens=3000,top_p=1,frequency_penalty=0,
                                presence_penalty=0,stream=True,html=False):
    
    response = client.chat.completions.create(
        model=model,
        messages=[{'role':'user','content':prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p = top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stream=stream
    )
    complete_response  = []

    for chunk in response:
        if chunk.choices[0].delta.content:
            complete_response.append(chunk.choices[0].delta.content)
            result_string = ''.join(complete_response)

            #Auto Scroll
            lines = result_string.count('\n') + 1
            avg_chars_per_line = 80
            lines += len(result_string)//avg_chars_per_line
            height_per_line = 20
            total_height = lines * height_per_line

            if text_area_placeholder:
                if html:
                    text_area_placeholder.markdown(result_string,unsafe_allow_html=True)
                else:
                    text_area_placeholder.text_area("Generated Text",value=result_string,height=total_height) 
    result_string = ''.join(complete_response)
    words = len(result_string.split())
    st.text(f"Total Words Generated: {words}")

    return result_string                    
    

if st.button("Create Recipe"):
    with st.spinner("Generating image..."):
        image = generate_image_openai(client,image_prompt)
        st.image(image,caption=recipe,use_column_width=True)

    with st.spinner("Generating Recipe..."):
        text_area_placeholder = st.markdown("",unsafe_allow_html=True)
        recipe_prompt = f" Create a detailed cooking recipe for the dish named {recipe}." \
                        f" Include preparation steps and cooking tips." \
                        f" Follow the following format {output_format}" 
        
        generate_recipe_description(client,recipe,text_area_placeholder,html=True)
