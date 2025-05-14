import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import json
import os
import re
import requests
import base64
from io import BytesIO
from dotenv import load_dotenv
import textwrap

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="HR Skills Management Platform",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="👔"
)

# Custom CSS for professional UI
st.markdown("""
<style>
    /* Main Styling */
    .main-header {
        font-size: 2.3rem;
        color: #1E40AF;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E5E7EB;
        font-weight: 600;
    }

    /* Use Case Headers */
    .use-case-header {
        font-size: 1.8rem;
        color: #1E3A8A;
        padding-top: 1rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    /* Output Container Styling */
    .output-container {
        background-color: #F3F4F6;
        padding: 1.8rem;
        border-radius: 0.5rem;
        margin-top: 1.5rem;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Sidebar Styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #F9FAFB;
    }

    /* Cards for Input Fields */
    .stTextInput, .stSelectbox, .stMultiselect, .stTextArea {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border-radius: 0.25rem;
        transition: all 0.3s;
        font-weight: 500;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
    }

    th {
        background-color: #E5E7EB;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #1F2937;
    }

    td {
        padding: 0.75rem;
        border-bottom: 1px solid #E5E7EB;
    }

    tr:hover {
        background-color: #F9FAFB;
    }

    /* Download Links */
    a {
        display: inline-block;
        background-color: #2563EB;
        color: white !important;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        margin-top: 1rem;
        transition: all 0.3s;
        font-weight: 500;
    }

    a:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Card Layout for Case Navigation */
    .case-card {
        padding: 1.5rem;
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
        transition: all 0.3s;
    }

    .case-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }

    .case-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1E40AF;
    }

    .case-description {
        color: #6B7280;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* Improve the look of markdown */
    h3 {
        color: #1E40AF;
        font-size: 1.3rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }

    /* Skills Styling */
    .skill-item {
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 0.25rem;
        background-color: #EFF6FF;
        border-left: 3px solid #3B82F6;
    }

    /* Loading Spinner */
    .stSpinner > div > div {
        border-color: #3B82F6 !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3B82F6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Get API key
api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not api_key:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
if not api_key:
    api_key = st.text_input("Enter your Anthropic API Key:", type="password")
    if not api_key:
        st.warning("Please enter a valid API key to use the application.")
        st.stop()


# Use direct API calls with requests instead of the SDK
def ask_claude(prompt, system_prompt=None, model="claude-3-haiku-20240307"):
    """Send a prompt to Claude API directly using requests"""
    try:
        headers = {
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": model,
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            payload["system"] = system_prompt

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None

        response_data = response.json()
        return response_data["content"][0]["text"]
    except Exception as e:
        st.error(f"Error calling Claude API: {str(e)}")
        return None


# Function to create radar chart
def create_radar_chart(skills, values, role, level, size=7):
    import matplotlib.pyplot as plt
    import numpy as np

    plt.style.use('seaborn-v0_8-whitegrid')

    num_vars = len(skills)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Loop around to close the radar
    values_plot = values + values[:1]
    angles += angles[:1]

    # Create figure with dynamic size
    fig, ax = plt.subplots(figsize=(size, size), subplot_kw=dict(polar=True), facecolor='white')

    ax.plot(angles, values_plot, 'o-', linewidth=2.5, color='#2563EB')
    ax.fill(angles, values_plot, alpha=0.25, color='#60A5FA')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(skills, size=9, color='#1F2937')

    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], color='#4B5563')
    ax.set_ylim(0, 10)
    ax.grid(True, color='#E5E7EB')
    ax.spines['polar'].set_visible(False)

    plt.title(f"Skill Profile: {role} - {level} Level", size=18, y=1.1, color='#1E3A8A', fontweight='bold')

    for i, value in enumerate(values):
        angle = angles[i]
        align_offset = 0.8 if np.pi / 2 <= angle <= 3 * np.pi / 2 else 1.2
        ax.annotate(
            f"{value}",
            xy=(angle, value),
            xytext=(angle, value + align_offset),
            ha='center',
            va='center',
            fontsize=9,
            fontweight='bold',
            color='#1E3A8A',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#3B82F6', alpha=0.7)
        )

    fig.tight_layout()
    return fig


# Function to save plot as image and create download link
def get_image_download_link(fig, filename="plot.png", text="Download Chart"):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Load and encode the SVG file
with open("img/Ferris-logo-full.svg", "rb") as f:
    svg_data = f.read()
    b64_svg = base64.b64encode(svg_data).decode()

# HTML layout with base64-encoded logo, header text, and tagline
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 25px; margin-bottom: 10px;">
        <img src="data:image/svg+xml;base64,{b64_svg}" alt="Logo" style="height: 150px; width: 150px;">
        <div>
            <h1 style="margin: 0; align:center;">HR360</h1>
            <p style="font-size: 1.2rem; color: gray; margin-top: 4px;">
                HR Skills Management Platform
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Create a row with info cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style="padding: 1rem; background-color: #EFF6FF; border-radius: 0.5rem; height: 100%; border-left: 5px solid #3B82F6;">
        <h3 style="margin-top: 0; color: #1E40AF; font-size: 1.2rem;">Workforce Planning</h3>
        <p style="color: #4B5563;">• Identify needs roles & skills based on company strategy.</p>
        <p style="color: #4B5563;">• Capture current skills</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="padding: 1rem; background-color: #ECFDF5; border-radius: 0.5rem; height: 100%; border-left: 5px solid #10B981;">
        <h3 style="margin-top: 0; color: #065F46; font-size: 1.2rem;">Recruiting & Onboarding</h3>
        <p style="color: #4B5563;">• Identify needed skills per vacancy</p>
        <p style="color: #4B5563;">• Develop job posting based on skills</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="padding: 1rem; background-color: #FEF3C7; border-radius: 0.5rem; height: 100%; border-left: 5px solid #F59E0B;">
        <h3 style="margin-top: 0; color: #B45309; font-size: 1.2rem;"> Performance Management & Compensation</h3>
        <p style="color: #4B5563;">• Skill-based performance evaluation</p>
        <p style="color: #4B5563;">• Personalized development plans</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for better organization
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Skill Identifier",
    "📊 Skill Profiler",
    "📝 Job Poster",
    "❓ Interview Questions",
    "📈 Development Plan"
])

# Case 1: Skill Identifier
with tab1:
    st.markdown("<h2 class='use-case-header'>Skill Identifier</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem; background-color: #F3F4F6; border-radius: 0.5rem; margin-bottom: 1.5rem;">
        <p>Enter a job role or description to identify the most important technical and soft skills required for this position.</p>
    </div>
    """, unsafe_allow_html=True)

    job_role = st.text_input("Job Role or Description:", value="Electrical Engineer - Motor Control")

    if st.button("Identify Skills", key="identify_skills"):
        if job_role:
            with st.spinner("Analyzing skills with AI..."):
                # Prepare prompt for Claude
                prompt = f"""
                You are a skilled HR professional and job analyst. Based on the job role or description below, 
                identify and list the most important technical and soft skills required for this position.

                Job Role/Description: {job_role}

                Please format your response as a JSON array of strings, with each string being a specific skill.
                Example format: ["Skill 1", "Skill 2", "Skill 3"]

                Provide between 8-12 specific, relevant skills for this role.
                """

                system_prompt = "You are an HR skills analyst that identifies required skills for job roles. Always return your answer in valid JSON format as an array of strings."

                response = ask_claude(prompt, system_prompt)

                if response:
                    try:
                        # Extract JSON from response if needed
                        json_match = re.search(r'\[.*\]', response.replace('\n', ' '), re.DOTALL)
                        if json_match:
                            skills_json = json_match.group(0)
                            skills = json.loads(skills_json)
                        else:
                            skills = json.loads(response)

                        # Display skills in a professional layout
                        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
                        st.subheader(f"Skills for {job_role}")

                        # Create two columns for skills
                        left_col, right_col = st.columns(2)
                        half = len(skills) // 2 + len(skills) % 2

                        with left_col:
                            for skill in skills[:half]:
                                st.markdown(f"""
                                <div class="skill-item">
                                    <span style="font-weight: 500;">• {skill}</span>
                                </div>
                                """, unsafe_allow_html=True)

                        with right_col:
                            for skill in skills[half:]:
                                st.markdown(f"""
                                <div class="skill-item">
                                    <span style="font-weight: 500;">• {skill}</span>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)
                    except json.JSONDecodeError:
                        st.error(f"Could not parse JSON response. Raw response: {response}")
        else:
            st.warning("Please enter a job role or description.")

# Case 2: Skill Profiler
with tab2:
    st.markdown("<h2 class='use-case-header'>Skill Profiler</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem; background-color: #F3F4F6; border-radius: 0.5rem; margin-bottom: 1.5rem;">
        <p>Generate a skills radar chart and skill level descriptions for a specific role and experience level.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("Role:", value="Electrical Engineer - Motor Control", key="role_skill_profiler")
    with col2:
        level = st.selectbox("Level:", ["Junior", "Mid", "Senior"], key="level_skill_profiler")

    if st.button("Generate Skill Profile", key="generate_profile"):
        if role:
            with st.spinner("Generating skill profile with AI..."):
                skills_prompt = f"""
                You are an expert in skills assessment for technical roles.
                For the role of {role} at {level} level, please provide:

                1. A list of 8 key skills required for this role
                2. A rating from 1-10 for each skill based on the expected proficiency level ({level})

                Return your answer as a JSON object with this exact structure:
                {{
                    "skills": ["skill1", "skill2", ...],
                    "ratings": [7, 8, ...]
                }}

                Junior should have ratings mostly in the 3-5 range, Mid in the 5-8 range, and Senior in the 8-10 range.
                """
                system_prompt = "You are a skills assessment expert. Always return your answer in valid JSON format."

                skills_response = ask_claude(skills_prompt, system_prompt)

                if skills_response:
                    try:
                        json_match = re.search(r'\{.*\}', skills_response.replace('\n', ' '), re.DOTALL)
                        if json_match:
                            skills_json = json_match.group(0)
                            skills_data = json.loads(skills_json)
                        else:
                            skills_data = json.loads(skills_response)

                        skills = skills_data["skills"]
                        ratings = skills_data["ratings"]

                        st.markdown("<div class='output-container'>", unsafe_allow_html=True)

                        # Add CSS
                        st.markdown("""
                        <style>
                            .output-container { margin-top: 1rem; }

                            table {
                                width: 100%;
                                border-collapse: collapse;
                                margin-top: 1rem;
                                font-family: Arial, sans-serif;
                            }

                            th, td {
                                padding: 8px 12px;
                                border: 1px solid #ddd;
                            }

                            th {
                                background-color: #f3f4f6;
                                text-align: left;
                            }

                            td:last-child {
                                text-align: center;
                            }

                            tr:nth-child(even) {
                                background-color: #f9f9f9;
                            }
                        </style>
                        """, unsafe_allow_html=True)

                        # Layout
                        chart_col, data_col = st.columns([1, 1])

                        with chart_col:
                            fig = create_radar_chart(skills, ratings, role, level)
                            st.pyplot(fig)
                            st.markdown(get_image_download_link(fig, f"{role}_{level}_skills.png", "📥 Download Chart"),
                                        unsafe_allow_html=True)
                            plt.close()

                        with data_col:
                            st.subheader("Skills Profile Data")

                            # Create a clean table with CSS styling directly in the same markdown call
                            st.markdown(f"""
                            <style>
                                table {{
                                    width: 100%;
                                    border-collapse: collapse;
                                    border: 1px solid #e5e7eb;
                                }}

                                th {{
                                    background-color: #f3f4f6;
                                    padding: 8px 12px;
                                    text-align: left;
                                    border: 1px solid #e5e7eb;
                                    font-family: Arial, sans-serif;
                                }}

                                td {{
                                    padding: 8px 12px;
                                    border: 1px solid #e5e7eb;
                                    font-family: Arial, sans-serif;
                                }}

                                /* Make the rating column right-aligned */
                                th:last-child, td:last-child {{
                                    width: 80px;
                                    text-align: right;
                                    padding-right: 20px;
                                }}
                            </style>
                            <table>
                                <tr>
                                    <th>Skill</th>
                                    <th>Rating</th>
                                </tr>
                                {"".join([f"<tr><td>{skill}</td><td>{rating}</td></tr>" for skill, rating in zip(skills, ratings)])}
                            </table>
                            """, unsafe_allow_html=True)

                        # Get skill descriptions
                        desc_prompt = f"""
                        For each of these skills for a {level}-level {role}, provide a brief description of what this level of proficiency means.
                        Skills: {", ".join(skills)}

                        Format your response as a JSON object with skill names as keys and descriptions as values.
                        Example:
                        {{
                            "Skill Name": "Description of what {level} level means for this skill",
                            ...
                        }}
                        """

                        desc_response = ask_claude(desc_prompt, system_prompt)

                        if desc_response:
                            try:
                                # Extract JSON from response if needed
                                json_match = re.search(r'\{.*\}', desc_response.replace('\n', ' '), re.DOTALL)
                                if json_match:
                                    desc_json = json_match.group(0)
                                    descriptions = json.loads(desc_json)
                                else:
                                    descriptions = json.loads(desc_response)

                                # Display skill descriptions
                                st.markdown("<div class='output-container'>", unsafe_allow_html=True)
                                st.subheader(f"Skill Descriptions for {level}-Level {role}")

                                # Create grid for descriptions
                                desc_cols = st.columns(2)
                                for i, skill in enumerate(skills):
                                    col_idx = i % 2
                                    with desc_cols[col_idx]:
                                        st.markdown(f"""
                                        <div style="background-color: white; padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem; border: 1px solid #E5E7EB; border-left: 4px solid #3B82F6;">
                                            <div style="font-weight: 600; color: #1E40AF; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                                {skill} <span style="float: right; background-color: #EFF6FF; padding: 0 0.5rem; border-radius: 0.25rem; font-size: 0.9rem;">{ratings[i]}/10</span>
                                            </div>
                                            <div style="color: #4B5563;">
                                                {descriptions.get(skill, 'Description not available')}
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)

                                st.markdown("</div>", unsafe_allow_html=True)
                            except json.JSONDecodeError:
                                st.error(f"Could not parse JSON response for descriptions")
                    except (json.JSONDecodeError, KeyError) as e:
                        st.error(f"Error processing skill data: {str(e)}")
        else:
            st.warning("Please enter a role.")

# Case 3: Job Poster
with tab3:
    st.markdown("<h2 class='use-case-header'>Job Poster</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem; background-color: #F3F4F6; border-radius: 0.5rem; margin-bottom: 1.5rem;">
        <p>Generate a complete job description and get recommended job boards for a specific role and experience level.</p>
    </div>
    """, unsafe_allow_html=True)

    # Create two rows for inputs
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        role = st.text_input("Role:", value="Electrical Engineer - Motor Control", key="role_job_poster")
    with row1_col2:
        level = st.selectbox("Level:", ["Junior", "Mid", "Senior"], key="level_job_poster")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        company_name = st.text_input("Company Name (Optional):", "")
    with row2_col2:
        location = st.text_input("Location (Optional):", "")

    if st.button("Generate Job Description", key="generate_job"):
        if role:
            with st.spinner("Generating job description with AI..."):
                # Prepare prompt for Claude
                prompt = f"""
                Create a professional job description for a {level}-level {role} position
                {f'at {company_name}' if company_name else ''}{f' in {location}' if location else ''}.

                Include the following sections:
                1. Position title
                2. Location and job type
                3. About the company (generic if no company name provided)
                4. Responsibilities
                5. Required skills with proficiency levels
                6. Qualifications and experience
                7. Application instructions

                Format the job description in Markdown with appropriate headers and bullet points.
                Make it professional but engaging.
                """

                job_desc_response = ask_claude(prompt)

                if job_desc_response:
                    # Display job description
                    st.markdown("<div class='output-container'>", unsafe_allow_html=True)
                    st.markdown(job_desc_response)

                    # Add download link for job description
                    job_desc_bytes = job_desc_response.encode()
                    b64 = base64.b64encode(job_desc_bytes).decode()
                    filename = f"{role.replace(' ', '_')}_{level}_JobDescription.md"
                    st.markdown(
                        f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download Job Description</a>',
                        unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Get job board recommendations
                    boards_prompt = f"""
                    Recommend 5 specific job boards that would be most effective for posting a job listing for a {level}-level {role} position.

                    For each job board, explain why it's particularly suitable for this role.

                    Format your response as a JSON array of objects with "name" and "why" properties:
                    [
                      {{"name": "Job Board Name", "why": "Reason this board is good for this role"}},
                      ...
                    ]
                    """

                    system_prompt = "You are an HR recruitment expert. Always return your answer in valid JSON format."

                    boards_response = ask_claude(boards_prompt, system_prompt)

                    if boards_response:
                        try:
                            # Extract JSON from response if needed
                            json_match = re.search(r'\[.*\]', boards_response.replace('\n', ' '), re.DOTALL)
                            if json_match:
                                boards_json = json_match.group(0)
                                job_boards = json.loads(boards_json)
                            else:
                                job_boards = json.loads(boards_response)

                            # Display job boards in a professional card layout
                            st.markdown("<div class='output-container'>", unsafe_allow_html=True)
                            st.subheader("Recommended Job Boards")

                            # Create job board cards
                            for i, board in enumerate(job_boards):
                                st.markdown(f"""
                                <div style="background-color: white; padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem; border: 1px solid #E5E7EB;">
                                    <div style="font-weight: 600; color: #1E40AF; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                        {i + 1}. {board['name']}
                                    </div>
                                    <div style="color: #4B5563;">
                                        {board['why']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                            st.markdown("</div>", unsafe_allow_html=True)
                        except json.JSONDecodeError:
                            st.error("Could not parse job board recommendations")
        else:
            st.warning("Please enter a role.")

# Case 4: Interview Questions
with tab4:
    st.markdown("<h2 class='use-case-header'>Interview Questions Generator</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem; background-color: #F3F4F6; border-radius: 0.5rem; margin-bottom: 1.5rem;">
        <p>Generate targeted interview questions based on role, level, and question types.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("Role:", value="Electrical Engineer - Motor Control", key="role_interview")
    with col2:
        with col2:
            level = st.selectbox("Level:", ["Junior", "Mid", "Senior"], key="level_interview")

        # Question types with a modern multi-select
        question_type = st.multiselect(
            "Question Types:",
            ["Technical", "Behavioral", "Problem-solving", "Team Collaboration"],
            default=["Technical", "Problem-solving"],
            key="question_types"
        )

        if st.button("Generate Interview Questions", key="generate_questions"):
            if role:
                with st.spinner("Generating interview questions with AI..."):
                    # Get skills first
                    skills_prompt = f"""
                        List the 5 most important skills for a {level}-level {role}.
                        Return only a JSON array of strings.
                        Example: ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
                        """

                    system_prompt = "You are a technical recruiter creating interview questions. Return only valid JSON."

                    skills_response = ask_claude(skills_prompt, system_prompt)

                    if skills_response:
                        try:
                            # Extract JSON from response if needed
                            json_match = re.search(r'\[.*\]', skills_response.replace('\n', ' '), re.DOTALL)
                            if json_match:
                                skills_json = json_match.group(0)
                                skills = json.loads(skills_json)
                            else:
                                skills = json.loads(skills_response)

                            # Generate questions based on skills and question types
                            questions_prompt = f"""
                                Create interview questions for a {level}-level {role} position.

                                Key skills for this role: {", ".join(skills)}
                                Question types needed: {", ".join(question_type)}

                                Generate 2-3 questions for each skill, focusing on the selected question types.
                                Also include 2-3 general questions that cover the selected question types.

                                Format your response as a JSON object with this structure:
                                {{
                                  "skills": {{
                                    "Skill Name 1": ["Question 1", "Question 2", ...],
                                    "Skill Name 2": ["Question 1", "Question 2", ...],
                                    ...
                                  }},
                                  "general": ["General question 1", "General question 2", ...]
                                }}

                                Questions should be appropriate for the {level} experience level.
                                """

                            questions_response = ask_claude(questions_prompt, system_prompt)

                            if questions_response:
                                try:
                                    # Extract JSON from response if needed
                                    json_match = re.search(r'\{.*\}', questions_response.replace('\n', ' '), re.DOTALL)
                                    if json_match:
                                        questions_json = json_match.group(0)
                                        questions_data = json.loads(questions_json)
                                    else:
                                        questions_data = json.loads(questions_response)

                                    # Display questions in an elegant UI
                                    st.markdown("<div class='output-container'>", unsafe_allow_html=True)
                                    st.markdown(f"""
                                        <h3 style="color: #1E40AF; margin-bottom: 1.5rem; font-weight: 500;">
                                            Interview Questions for {level}-Level {role}
                                        </h3>
                                        """, unsafe_allow_html=True)

                                    # Create question tabs for better organization
                                    question_tabs = st.tabs(["Skills-Based Questions", "General Questions"])

                                    with question_tabs[0]:
                                        # Skill-specific questions
                                        if "skills" in questions_data:
                                            for skill, questions in questions_data["skills"].items():
                                                st.markdown(f"""
                                                    <div style="background-color: white; padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem; border: 1px solid #E5E7EB; border-left: 4px solid #3B82F6;">
                                                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                                            {skill}
                                                        </div>
                                                        <div>
                                                    """, unsafe_allow_html=True)

                                                for i, question in enumerate(questions, 1):
                                                    st.markdown(f"""
                                                        <div style="margin-bottom: 0.5rem; padding: 0.5rem; background-color: #F9FAFB; border-radius: 0.25rem;">
                                                            <span style="font-weight: 500; color: #4B5563;">Q{i}:</span> {question}
                                                        </div>
                                                        """, unsafe_allow_html=True)

                                                st.markdown("</div></div>", unsafe_allow_html=True)

                                    with question_tabs[1]:
                                        # General questions
                                        if "general" in questions_data:
                                            st.markdown(f"""
                                                <div style="background-color: white; padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem; border: 1px solid #E5E7EB; border-left: 4px solid #10B981;">
                                                    <div style="font-weight: 600; color: #065F46; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                                        General Questions
                                                    </div>
                                                    <div>
                                                """, unsafe_allow_html=True)

                                            for i, question in enumerate(questions_data["general"], 1):
                                                st.markdown(f"""
                                                    <div style="margin-bottom: 0.5rem; padding: 0.5rem; background-color: #F9FAFB; border-radius: 0.25rem;">
                                                        <span style="font-weight: 500; color: #4B5563;">Q{i}:</span> {question}
                                                    </div>
                                                    """, unsafe_allow_html=True)

                                            st.markdown("</div></div>", unsafe_allow_html=True)

                                    st.markdown("</div>", unsafe_allow_html=True)

                                    # Add download link for questions in a professional button
                                    questions_md = f"# Interview Questions for {level}-Level {role}\n\n"
                                    questions_md += "## Skill-Specific Questions\n\n"
                                    for skill, questions in questions_data.get("skills", {}).items():
                                        questions_md += f"### {skill}\n"
                                        for i, question in enumerate(questions, 1):
                                            questions_md += f"{i}. {question}\n"
                                        questions_md += "\n"

                                    if "general" in questions_data:
                                        questions_md += "## General Questions\n\n"
                                        for i, question in enumerate(questions_data["general"], 1):
                                            questions_md += f"{i}. {question}\n"

                                    questions_bytes = questions_md.encode()
                                    b64 = base64.b64encode(questions_bytes).decode()
                                    filename = f"{role.replace(' ', '_')}_{level}_Interview_Questions.md"
                                    st.markdown(f"""
                                        <a href="data:file/txt;base64,{b64}" download="{filename}" style="margin-top: 1.5rem;">
                                            📥 Download Interview Questions
                                        </a>
                                        """, unsafe_allow_html=True)
                                except json.JSONDecodeError:
                                    st.error("Could not parse interview questions")
                        except json.JSONDecodeError:
                            st.error("Could not parse skills response")
            else:
                st.warning("Please enter a role.")

        # Case 5: Development Plan
    with tab5:
        st.markdown("<h2 class='use-case-header'>Personalized Development Plan</h2>", unsafe_allow_html=True)
        st.markdown("""
            <div style="padding: 1rem; background-color: #F3F4F6; border-radius: 0.5rem; margin-bottom: 1.5rem;">
                <p>Generate a personalized development plan based on performance feedback for a specific role and level.</p>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            role = st.text_input("Role:", value="Electrical Engineer - Motor Control", key="role_dev_plan")
        with col2:
            level = st.selectbox("Level:", ["Junior", "Mid", "Senior"], key="level_dev_plan")

        employee_name = st.text_input("Employee Name (Optional):", "", key="employee_name")

        feedback = st.text_area(
            "Performance Feedback:",
            value="Strong in motor control theory. Needs improvement in embedded coding and circuit analysis. Poor documentation and project communication.",
            height=120,
            key="feedback"
        )

        if st.button("Generate Development Plan", key="generate_plan"):
            if role and feedback:
                with st.spinner("Generating development plan with AI..."):
                    # Prepare prompt for Claude
                    prompt = f"""
                        Create a personalized development plan for a {level}-level {role}
                        {f'named {employee_name}' if employee_name else ''} based on the following performance feedback:

                        "{feedback}"

                        Include:
                        1. A summary of strengths and areas for improvement
                        2. Specific development goals for each area needing improvement
                        3. Recommended learning resources (courses, books, etc.)
                        4. Actionable milestones with a 3-month timeline
                        5. Key performance indicators to measure progress

                        Format the development plan in detailed Markdown with clear sections and bullet points.
                        """

                    plan_response = ask_claude(prompt)

                    if plan_response:
                        # Display development plan in a professional format
                        st.markdown("<div class='output-container'>", unsafe_allow_html=True)

                        # Add a nice header with employee name if provided
                        if employee_name:
                            st.markdown(f"""
                                <div style="text-align: center; margin-bottom: 1.5rem;">
                                    <h3 style="color: #1E40AF; font-weight: 500; margin-bottom: 0.25rem;">Development Plan</h3>
                                    <h4 style="color: #1F2937; font-weight: 400; margin-top: 0;">for {employee_name}</h4>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style="text-align: center; margin-bottom: 1.5rem;">
                                    <h3 style="color: #1E40AF; font-weight: 500;">Development Plan</h3>
                                </div>
                                """, unsafe_allow_html=True)

                        # Display the plan with enhanced styling
                        # st.markdown will automatically render the markdown from Claude
                        st.markdown(plan_response)

                        # Add download link for development plan
                        plan_bytes = plan_response.encode()
                        b64 = base64.b64encode(plan_bytes).decode()
                        filename = f"{'Development_Plan' if not employee_name else employee_name.replace(' ', '_')}_Plan.md"
                        st.markdown(f"""
                            <a href="data:file/txt;base64,{b64}" download="{filename}">
                                📥 Download Development Plan
                            </a>
                            """, unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Please enter a role and performance feedback.")

        # Footer with branding
    st.markdown("""
        <div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #E5E7EB; text-align: center;">
            <p style="color: #6B7280; font-size: 0.9rem;">
                HR Skills Management Platform | Powered by Ferris.ai
            </p>
            <p style="color: #9CA3AF; font-size: 0.8rem;">
                © 2025 | Create professional HR content with AI assistance
            </p>
        </div>
        """, unsafe_allow_html=True)