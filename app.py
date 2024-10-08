# import re
# import streamlit as st
# from streamlit_sortables import sort_items
# from openai import OpenAI
# import pymongo
# import os

# # MongoDB setup
# client = pymongo.MongoClient("mongodb+srv://admin:admin@clustermark.hvrmb.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMark")
# db = client["product_description_db"]
# collection = db["descriptions"]

# os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
# client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# MODEL = "gpt-4o"

# # Initialize session state variables
# if "step" not in st.session_state:
#     st.session_state["step"] = 0
# if "product_name" not in st.session_state:
#     st.session_state["product_name"] = ""
# if "usps" not in st.session_state:
#     st.session_state["usps"] = []
# if "selected_usps" not in st.session_state:
#     st.session_state["selected_usps"] = {}
# if "final_usps" not in st.session_state:
#     st.session_state["final_usps"] = []
# if "long_description" not in st.session_state:
#     st.session_state["long_description"] = ""
# if "short_bullets" not in st.session_state:
#     st.session_state["short_bullets"] = ""
# if "short_paragraph" not in st.session_state:
#     st.session_state["short_paragraph"] = ""
# if "custom_usps" not in st.session_state:
#     st.session_state["custom_usps"] = []
# if "dragged_usps" not in st.session_state:
#     st.session_state["dragged_usps"] = []
# if "custom_usp_form_visible" not in st.session_state:
#     st.session_state["custom_usp_form_visible"] = False
# if "attribute_counter" not in st.session_state:
#     st.session_state["attribute_counter"] = 0
# if "edit_mode" not in st.session_state:
#     st.session_state["edit_mode"] = {
#         "long": False,
#         "bullets": False,
#         "paragraph": False
#     }
# if "edited_long_description" not in st.session_state:
#     st.session_state["edited_long_description"] = ""
# if "edited_short_bullets" not in st.session_state:
#     st.session_state["edited_short_bullets"] = ""
# if "edited_short_paragraph" not in st.session_state:
#     st.session_state["edited_short_paragraph"] = ""

# # Function to reset relevant session state variables
# def reset_session_state():
#     st.session_state["product_name"] = ""
#     st.session_state["usps"] = []
#     st.session_state["selected_usps"] = {}
#     st.session_state["final_usps"] = []
#     st.session_state["long_description"] = ""
#     st.session_state["short_bullets"] = ""
#     st.session_state["short_paragraph"] = ""
#     st.session_state["custom_usps"] = []
#     st.session_state["dragged_usps"] = []
#     st.session_state["custom_usp_form_visible"] = False
#     st.session_state["attribute_counter"] = 0

# # Helper function to remove numbers from the start of USP names
# def remove_numbers(text):
#     return re.sub(r"^\d+\.\s*", "", text)

# # Step 0: Dashboard with product table and description links
# def dashboard():
#     st.title("My Product Descriptions")
    
#     # Fetch past products from MongoDB
#     past_products = list(collection.find())
    
#     if len(past_products) > 0:
#         st.write("---")
#         st.write("**Products**")
        
#         for product in past_products:
#             cols = st.columns([4, 2, 2, 2, 1])  # Adjusted the width to align the delete button
            
#             # Product Name
#             cols[0].write(f"**{product['name']}**")
            
#             # Long description link
#             if cols[1].button("Long Description", key=f"long_{product['_id']}"):
#                 show_description(product, "long")

#             # Short description with bullets link
#             if cols[2].button("Short - Bullets", key=f"bullets_{product['_id']}"):
#                 show_description(product, "no_bullets")

#             # Short description without bullets link
#             if cols[3].button("Short - No Bullets", key=f"no_bullets_{product['_id']}"):
#                 show_description(product, "bullets")

#             # Delete product button
#             if cols[4].button("❌", key=f"delete_{product['_id']}"):
#                 delete_product(product['_id'])
    
#     st.write("---")
    
#     if st.button("+ Add New Product"):
#         reset_session_state()
#         st.session_state["step"] = 1
#         st.rerun()

# # Show selected description
# def show_description(product, description_type):
#     st.subheader(f"{product['name']} - {description_type.capitalize()} Description")
    
#     if description_type == "long":
#         st.write(product["long_description"])
#     elif description_type == "bullets":
#         st.write(product["short_description"].split("\n\n")[0])
#     elif description_type == "no_bullets":
#         st.write(product["short_description"].split("\n\n")[1])
    
#     if st.button("Go back to Dashboard"):
#         st.session_state["step"] = 0
#         st.rerun()

# def delete_product(product_id):
#     collection.delete_one({"_id": product_id})
#     st.success("Product deleted successfully!")
#     st.session_state["step"] = 0
#     st.rerun()

# def add_new_product():
#     st.subheader("STEP 1: Enter Product Name")
#     product_name = st.text_input("Enter the name of the product")
    
#     if st.button("Submit"):
#         if product_name:
#             st.session_state["product_name"] = product_name
#             st.session_state["step"] = 2
#             st.rerun()

# # Step 2: Generate USPs
# def generate_usps():
#     st.subheader(f"Generating product attributes for {st.session_state['product_name']}...")

#     if not st.session_state["usps"]:
#         prompt_usp = f"""
#         You are working with a Kirana store owner to generate a good product description for {st.session_state['product_name']}. 
#         Create two different lists of Unique Selling Propositions (USPs). 
#         First, there should be a generic list of USPs that apply to all {st.session_state['product_name']}. 
#         Second, there should be a specific list of USPs that are based on attributes specific only to certain types of {st.session_state['product_name']}. 
#         The header of each item on the second list should be followed by *. 
#         Make sure there are not more than 6 items in each of the lists. Number the lists in a continuous sequence. 
#         For both the lists, mention only the items in the list without a title for the lists. Please give me the response like this USP name: USP description only.
#         """
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=[{"role": "user", "content": prompt_usp}],
#             max_tokens=500
#         )
#         usps_raw = response.choices[0].message.content.strip()
#         usps_list = usps_raw.split("\n")
#         usps_parsed = []
#         for usp in usps_list:
#             if ':' in usp:
#                 name, description = usp.split(':', 1)
#                 usps_parsed.append((remove_numbers(name.strip()), description.strip()))  # Remove numbers
#         st.session_state["usps"] = usps_parsed

#     st.write("Select the attributes you want to include (Max 6):")

#     # Only one checkbox in the dropdown (no numbers)
#     for index, (name, description) in enumerate(st.session_state["usps"]):
#         with st.expander(f"{name}", expanded=False):
#             st.write(f"{description}")
#             selected = st.checkbox(f"{name}", key=f"usp_{index}")
#             if selected and len(st.session_state["selected_usps"]) < 6:
#                 st.session_state["selected_usps"][name] = description
#             elif selected and len(st.session_state["selected_usps"]) >= 6:
#                 st.error("Maximum of 6 USPs allowed")
#             elif not selected and name in st.session_state["selected_usps"]:
#                 del st.session_state["selected_usps"][name]
    
#     if st.button("Submit") and st.session_state["selected_usps"]:
#         st.session_state["final_usps"] = st.session_state["selected_usps"]
#         st.session_state["step"] = 3
#         st.rerun()

# # Step 3: Finalize USPs (Drag & Drop, Add/Delete Custom USP)
# def finalize_usps():
#     st.subheader("STEP 3: Finalize USPs")

#     usps = list(st.session_state["final_usps"].keys()) + [usp['name'] for usp in st.session_state["custom_usps"]]

#     st.write("Drag to reorder USPs according to priority:")
#     dragged_usps = sort_items(items=usps, direction="vertical", key="usp_sortable_list")
#     st.session_state["dragged_usps"] = dragged_usps

#     # Add Custom USP
#     if st.button("Add Custom USP"):
#         st.session_state["custom_usp_form_visible"] = True

#     if st.session_state["custom_usp_form_visible"]:
#         custom_usp_name = st.text_input("Custom USP Name (Max 6 words)", max_chars=50)
#         custom_usp_description = st.text_area("Custom USP Description (Max 20 words)", max_chars=150)

#         if st.button("Submit Custom USP"):
#             if len(custom_usp_name.split()) <= 6 and len(custom_usp_description.split()) <= 20:
#                 st.session_state["custom_usps"].append({
#                     "name": custom_usp_name, 
#                     "description": custom_usp_description
#                 })
#                 st.session_state["dragged_usps"].append(custom_usp_name)
#                 st.session_state["final_usps"][custom_usp_name] = custom_usp_description
#                 st.session_state["custom_usp_form_visible"] = False
#                 st.rerun()
#             else:
#                 st.error("Custom USP name should be up to 6 words and description up to 20 words.")

#     # Delete USP button
#     if st.session_state["dragged_usps"]:
#         for usp in st.session_state["dragged_usps"]:
#             if st.button(f"❌ Delete {usp}", key=f"delete_usp_{usp}"):
#                 st.session_state["dragged_usps"].remove(usp)
#                 if usp in st.session_state["final_usps"]:
#                     del st.session_state["final_usps"][usp]
#                 st.rerun()

#     if st.button("Finalize USPs"):
#         st.session_state["final_usps"] = {
#             usp: st.session_state["final_usps"].get(usp, usp)
#             for usp in st.session_state["dragged_usps"]
#         }
#         st.session_state["step"] = 4
#         st.rerun()

# # Step 4: Generate Long Product Description using OpenAI API
# def generate_long_description():
#     st.subheader("STEP 4: Generating Long Product Description")
    
#     usps = st.session_state["final_usps"]
#     product_name = st.session_state["product_name"]

#     if not st.session_state["long_description"]:
#         prompt_desc = f"""
#         Generate a product description with the USPs mentioned. 
#         Start with a paragraph of information which is not the same as the USPs and not more than 60 words, 
#         from the following: the problem the product solves for the customer, where and when is the customer going to use the product, 
#         how is the product better than other products in the market for the buyer? 
#         Then, add the USPs mentioned. Use simple language understood by a grade 5 student but retain important terms or keywords about the {product_name}.
#         """
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=[{"role": "user", "content": prompt_desc + "\n\n" + "\n".join(usps)}],
#             max_tokens=300
#         )
#         st.session_state["long_description"] = response.choices[0].message.content.strip()

#     show_editable_description("long", st.session_state["long_description"])

#     if st.button("Submit"):
#         st.session_state["step"] = 5
#         st.rerun()

# # Step 5: Generate Short Product Description (bulleted)
# def generate_short_description():
#     st.subheader("STEP 5: Generating Short Product Description (Bullets)")

#     if not st.session_state["short_bullets"]:
#         long_description = st.session_state["long_description"]
#         prompt_bullets = f"""
#         Create a brief product description around 60-80 words with the USPs as bullet points for the following product description:
#         {long_description}
#         """
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=[{"role": "user", "content": prompt_bullets}],
#             max_tokens=150
#         )
#         st.session_state["short_bullets"] = response.choices[0].message.content.strip()

#     show_editable_description("bullets", st.session_state["short_bullets"])

#     if st.button("Submit"):
#         st.session_state["step"] = 6
#         st.rerun()

# # Step 6: Generate Short Product Description (paragraph)
# def generate_short_paragraph():
#     st.subheader("STEP 6: Generating Short Product Description (Paragraph)")

#     if not st.session_state["short_paragraph"]:
#         short_bullets = st.session_state["short_bullets"]
#         prompt_paragraph = f"""
#         Rewrite the below short product description in paragraph form in not more than 60-80 words. 
#         Keep the USPs in bold letters in sentence case:
#         {short_bullets}
#         """
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=[{"role": "user", "content": prompt_paragraph}],
#             max_tokens=150
#         )
#         st.session_state["short_paragraph"] = response.choices[0].message.content.strip()

#     show_editable_description("paragraph", st.session_state["short_paragraph"])

#     if st.button("Submit"):
#         save_product()
#         st.rerun()

# def show_editable_description(key, content):
#     if st.session_state["edit_mode"][key]:
#         edited_text = st.text_area(f"Edit {key.capitalize()} Description", value=content)
#         if st.button(f"Save {key.capitalize()} Description"):
#             st.session_state[f"edited_{key}_description"] = edited_text  # Save edited version
#             st.session_state["edit_mode"][key] = False
#     else:
#         st.markdown(content)
#         if st.button(f"Edit {key.capitalize()} Description"):
#             st.session_state["edit_mode"][key] = True

# # Save product to MongoDB
# def save_product():
#     product_data = {
#         "name": st.session_state["product_name"],
#         "usps": st.session_state["final_usps"],
#         "long_description": st.session_state["edited_long_description"] or st.session_state["long_description"],
#         "short_description": (st.session_state["edited_short_bullets"] or st.session_state["short_bullets"]) + "\n\n" + (st.session_state["edited_short_paragraph"] or st.session_state["short_paragraph"])
#     }
    
#     collection.insert_one(product_data)
#     st.session_state["submitted_product"] = product_data
#     st.session_state["step"] = 0
#     reset_session_state()
#     st.rerun()

# if __name__ == "__main__":
#     if st.session_state["step"] == 0:
#         dashboard()
#     elif st.session_state["step"] == 1:
#         add_new_product()
#     elif st.session_state["step"] == 2:
#         generate_usps()
#     elif st.session_state["step"] == 3:
#         finalize_usps()
#     elif st.session_state["step"] == 4:
#         generate_long_description()
#     elif st.session_state["step"] == 5:
#         generate_short_description()
#     elif st.session_state["step"] == 6:
#         generate_short_paragraph()



import re
import streamlit as st
from streamlit_sortables import sort_items
from openai import OpenAI
import pymongo
import os

# MongoDB setup
client = pymongo.MongoClient("mongodb+srv://admin:admin@clustermark.hvrmb.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMark")
db = client["product_description_db"]
collection = db["descriptions"]

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

MODEL = "gpt-4o"

# Initialize session state variables
if "step" not in st.session_state:
    st.session_state["step"] = 0
if "product_name" not in st.session_state:
    st.session_state["product_name"] = ""
if "usps" not in st.session_state:
    st.session_state["usps"] = []
if "selected_usps" not in st.session_state:
    st.session_state["selected_usps"] = {}
if "final_usps" not in st.session_state:
    st.session_state["final_usps"] = []
if "long_description" not in st.session_state:
    st.session_state["long_description"] = ""
if "short_bullets" not in st.session_state:
    st.session_state["short_bullets"] = ""
if "short_paragraph" not in st.session_state:
    st.session_state["short_paragraph"] = ""
if "custom_usps" not in st.session_state:
    st.session_state["custom_usps"] = []
if "dragged_usps" not in st.session_state:
    st.session_state["dragged_usps"] = []
if "custom_usp_form_visible" not in st.session_state:
    st.session_state["custom_usp_form_visible"] = False
if "attribute_counter" not in st.session_state:
    st.session_state["attribute_counter"] = 0
if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = {
        "long": False,
        "bullets": False,
        "paragraph": False
    }
if "edited_long_description" not in st.session_state:
    st.session_state["edited_long_description"] = ""
if "edited_short_bullets" not in st.session_state:
    st.session_state["edited_short_bullets"] = ""
if "edited_short_paragraph" not in st.session_state:
    st.session_state["edited_short_paragraph"] = ""

# Function to reset relevant session state variables
def reset_session_state():
    st.session_state["product_name"] = ""
    st.session_state["usps"] = []
    st.session_state["selected_usps"] = {}
    st.session_state["final_usps"] = []
    st.session_state["long_description"] = ""
    st.session_state["short_bullets"] = ""
    st.session_state["short_paragraph"] = ""
    st.session_state["custom_usps"] = []
    st.session_state["dragged_usps"] = []
    st.session_state["custom_usp_form_visible"] = False
    st.session_state["attribute_counter"] = 0

# Helper function to remove numbers from the start of USP names
def remove_numbers(text):
    return re.sub(r"^\d+\.\s*", "", text)

# Step 0: Dashboard with product table and description links
def dashboard():
    st.title("My Product Descriptions")
    
    # Fetch past products from MongoDB
    past_products = list(collection.find())
    
    if len(past_products) > 0:
        st.write("---")
        st.write("**Products**")
        
        for product in past_products:
            cols = st.columns([4, 2, 2, 2, 1])  # Adjusted the width to align the delete button
            
            # Product Name
            cols[0].write(f"**{product['name']}**")
            
            # Long description link
            if cols[1].button("Long Description", key=f"long_{product['_id']}"):
                show_description(product, "long")

            # Short description with bullets link
            if cols[2].button("Short - Bullets", key=f"bullets_{product['_id']}"):
                show_description(product, "bullets")

            # Short description without bullets link
            if cols[3].button("Short - No Bullets", key=f"no_bullets_{product['_id']}"):
                show_description(product, "no_bullets")

            # Delete product button
            if cols[4].button("❌", key=f"delete_{product['_id']}"):
                delete_product(product['_id'])
    
    st.write("---")
    
    if st.button("+ Add New Product"):
        reset_session_state()
        st.session_state["step"] = 1
        st.rerun()

# Show selected description
def show_description(product, description_type):
    st.subheader(f"{product['name']} - {description_type.capitalize()} Description")
    
    if description_type == "long":
        st.write(product["long_description"])
    elif description_type == "bullets":
        st.write(product["short_description"].split("\n\n")[0])
    elif description_type == "no_bullets":
        st.write(product["short_description"].split("\n\n")[1])
    
    if st.button("Go back to Dashboard"):
        st.session_state["step"] = 0
        st.rerun()

def delete_product(product_id):
    collection.delete_one({"_id": product_id})
    st.success("Product deleted successfully!")
    st.session_state["step"] = 0
    st.rerun()

# Step 1: Enter Product Name
def add_new_product():
    st.subheader("STEP 1: Enter Product Name")
    product_name = st.text_input("Enter the name of the product")
    
    if st.button("Submit"):
        if product_name:
            st.session_state["product_name"] = product_name
            st.session_state["step"] = 2
            st.rerun()

    if st.button("Cancel", key="cancel_add_product"):
        st.session_state["step"] = 0
        st.rerun()

# Step 2: Select Attributes
def generate_usps():
    st.subheader(f"STEP 2: Select Attributes for {st.session_state['product_name']}")

    if not st.session_state["usps"]:
        prompt_usp = f"""
        You are working with a Kirana store owner to generate a good product description for {st.session_state['product_name']}. 
        Create two different lists of Unique Selling Propositions (USPs). 
        First, there should be a generic list of USPs that apply to all {st.session_state['product_name']}. 
        Second, there should be a specific list of USPs that are based on attributes specific only to certain types of {st.session_state['product_name']}. 
        The header of each item on the second list should be followed by *. 
        Make sure there are not more than 6 items in each of the lists. Number the lists in a continuous sequence. 
        For both the lists, mention only the items in the list without a title for the lists. Please give me the response like this USP name: USP description only.
        """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_usp}],
            max_tokens=500
        )
        usps_raw = response.choices[0].message.content.strip()
        usps_list = usps_raw.split("\n")
        usps_parsed = []
        for usp in usps_list:
            if ':' in usp:
                name, description = usp.split(':', 1)
                usps_parsed.append((remove_numbers(name.strip()), description.strip()))  # Remove numbers
        st.session_state["usps"] = usps_parsed

    st.write("Select the attributes you want to include (Max 6):")

    selected_count = len(st.session_state["selected_usps"])

    # Add custom CSS to align checkboxes and titles properly
    st.markdown("""
        <style>
        .checkbox-container {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .checkbox-container .stCheckbox {
            margin-right: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    for index, (name, description) in enumerate(st.session_state["usps"]):
        # Create a new container with checkbox and title on the same line
        cols = st.columns([1, 9])  # Two columns: 1 for checkbox, 9 for title

        # Prevent adding more than 6 USPs
        if selected_count >= 6 and name not in st.session_state["selected_usps"]:
            selected = cols[0].checkbox("", key=f"usp_{index}", disabled=True)  # Disable extra selections
        else:
            selected = cols[0].checkbox("", key=f"usp_{index}")
        
        # Align checkbox and title
        cols[1].markdown(f"<div class='checkbox-container'><strong>{name}</strong></div>", unsafe_allow_html=True)

        # Expander to show description
        with cols[1].expander(f"More about {name}"):
            st.write(description)

        # Add or remove USPs based on the checkbox selection
        if selected and name not in st.session_state["selected_usps"]:
            st.session_state["selected_usps"][name] = description
            selected_count += 1
        elif not selected and name in st.session_state["selected_usps"]:
            del st.session_state["selected_usps"][name]
            selected_count -= 1
    
    if st.button("Submit") and st.session_state["selected_usps"]:
        st.session_state["final_usps"] = st.session_state["selected_usps"]
        st.session_state["step"] = 3
        st.rerun()

    if st.button("Cancel", key="cancel_generate_usps"):
        st.session_state["step"] = 0
        st.rerun()

def finalize_usps():
    st.subheader("STEP 3: Finalize USPs")

    # Combine selected and custom USPs into one list for sorting
    usps = list(st.session_state["final_usps"].keys()) + [usp['name'] for usp in st.session_state["custom_usps"]]

    st.write("Drag to reorder USPs according to priority:")
    
    # Sort and display USPs
    dragged_usps = sort_items(items=usps, direction="vertical", key="usp_sortable_list")
    st.session_state["dragged_usps"] = dragged_usps

    # Prevent adding duplicates by introducing a session flag
    if "usp_added" not in st.session_state:
        st.session_state["usp_added"] = False

    # Add Custom USP form
    with st.form(key="custom_usp_form"):
        custom_usp_name = st.text_input("Custom USP Name (Max 6 words)", max_chars=50, key="custom_usp_name_input")
        custom_usp_description = st.text_area("Custom USP Description (Max 20 words)", max_chars=150, key="custom_usp_description_input")
        
        # Submit the form
        submit_custom_usp = st.form_submit_button("Submit Custom USP")

        if submit_custom_usp and not st.session_state["usp_added"]:
            # Check the number of words in both inputs
            name_word_count = len(custom_usp_name.split())
            description_word_count = len(custom_usp_description.split())

            if name_word_count <= 6 and description_word_count <= 20 and len(st.session_state["dragged_usps"]) < 6:
                # Ensure the custom USP is added only once
                if custom_usp_name not in st.session_state["final_usps"] and all(cusp["name"] != custom_usp_name for cusp in st.session_state["custom_usps"]):
                    # Add to custom_usps and final_usps
                    st.session_state["custom_usps"].append({
                        "name": custom_usp_name,
                        "description": custom_usp_description
                    })
                    # Append to dragged_usps only if it's not already there
                    if custom_usp_name not in st.session_state["dragged_usps"]:
                        st.session_state["dragged_usps"].append(custom_usp_name)
                        
                    # Add to final_usps
                    st.session_state["final_usps"][custom_usp_name] = custom_usp_description

                    # Set the flag to True to prevent multiple submissions
                    st.session_state["usp_added"] = True

                    # Force rerun to refresh the state
                    st.rerun()
            else:
                st.error(f"Custom USP name should be up to 6 words (currently {name_word_count}), "
                         f"description up to 20 words (currently {description_word_count}), "
                         f"and you can't have more than 6 USPs in total.")
    
    # Display and allow deletion of USPs
    if st.session_state["dragged_usps"]:
        for index, usp in enumerate(st.session_state["dragged_usps"]):
            if st.button(f"❌ Delete {usp}", key=f"delete_usp_{usp}_{index}"):
                # Remove from dragged_usps, final_usps, and custom_usps
                st.session_state["dragged_usps"].remove(usp)
                if usp in st.session_state["final_usps"]:
                    del st.session_state["final_usps"][usp]

                # Remove from custom_usps if it is a custom USP
                st.session_state["custom_usps"] = [cusp for cusp in st.session_state["custom_usps"] if cusp["name"] != usp]
                
                # Reset the usp_added flag after deletion so new USPs can be added
                st.session_state["usp_added"] = False

                # Force UI refresh after deletion
                st.rerun()

    # Finalize USPs button
    if st.button("Finalize USPs", key="finalize_usps_unique"):
        # Update the final USPs list with the dragged order
        st.session_state["final_usps"] = {
            usp: st.session_state["final_usps"].get(usp, usp)
            for usp in st.session_state["dragged_usps"]
        }
        st.session_state["step"] = 4
        st.rerun()

    # Cancel button
    if st.button("Cancel", key="cancel_finalize_usps_unique"):  # Ensure unique key
        st.session_state["step"] = 0
        st.rerun()




# Step 4: Create the Long Product Description
def generate_long_description():
    st.subheader("STEP 4: Create the Long Product Description")
    
    usps = st.session_state["final_usps"]
    product_name = st.session_state["product_name"]

    if not st.session_state["long_description"]:
        prompt_desc = f"""
        Generate a product description with the USPs mentioned. 
        Start with a paragraph of information which is not the same as the USPs and not more than 60 words, 
        from the following: the problem the product solves for the customer, where and when is the customer going to use the product, 
        how is the product better than other products in the market for the buyer? 
        Then, add the USPs mentioned. Use simple language understood by a grade 5 student but retain important terms or keywords about the {product_name}.
        """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_desc + "\n\n" + "\n".join(usps)}],
            max_tokens=300
        )
        st.session_state["long_description"] = response.choices[0].message.content.strip()

    show_editable_description("long", st.session_state["long_description"])

    if st.button("Submit"):
        st.session_state["step"] = 5
        st.rerun()

    if st.button("Cancel", key="cancel_long_desc"):
        st.session_state["step"] = 0
        st.rerun()

# Step 5: Create the Short Product Description
def generate_short_description():
    st.subheader("STEP 5: Create the Short Product Description")

    if not st.session_state["short_bullets"]:
        long_description = st.session_state["long_description"]
        prompt_bullets = f"""
        Create a brief product description around 60-80 words with the USPs as bullet points for the following product description:
        {long_description}
        """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_bullets}],
            max_tokens=150
        )
        st.session_state["short_bullets"] = response.choices[0].message.content.strip()

    show_editable_description("bullets", st.session_state["short_bullets"])

    if st.button("Submit"):
        st.session_state["step"] = 6
        st.rerun()

    if st.button("Cancel", key="cancel_short_desc"):
        st.session_state["step"] = 0
        st.rerun()

# Editable description function
def show_editable_description(key, content):
    if st.session_state["edit_mode"][key]:
        edited_text = st.text_area(f"Edit {key.capitalize()} Description", value=content)
        if st.button(f"Save {key.capitalize()} Description"):
            st.session_state[f"edited_{key}_description"] = edited_text  # Save edited version
            st.session_state["edit_mode"][key] = False
    else:
        st.markdown(content)
        if st.button(f"Edit {key.capitalize()} Description"):
            st.session_state["edit_mode"][key] = True

# Save product to MongoDB
def save_product():
    product_data = {
        "name": st.session_state["product_name"],
        "usps": st.session_state["final_usps"],
        "long_description": st.session_state["edited_long_description"] or st.session_state["long_description"],
        "short_description": (st.session_state["edited_short_bullets"] or st.session_state["short_bullets"]) + "\n\n" + (st.session_state["edited_short_paragraph"] or st.session_state["short_paragraph"])
    }
    
    collection.insert_one(product_data)
    st.session_state["submitted_product"] = product_data
    st.session_state["step"] = 0
    reset_session_state()
    st.rerun()

if __name__ == "__main__":
    if st.session_state["step"] == 0:
        dashboard()
    elif st.session_state["step"] == 1:
        add_new_product()
    elif st.session_state["step"] == 2:
        generate_usps()
    elif st.session_state["step"] == 3:
        finalize_usps()
    elif st.session_state["step"] == 4:
        generate_long_description()
    elif st.session_state["step"] == 5:
        generate_short_description()
