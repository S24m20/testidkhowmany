import streamlit as st
import pandas as pd
import json
import plotly.express as px
from database import get_questions_for_review, update_question_manual, get_distinct_subjects, get_classification_stats
from config import CURRICULUM_FOLDER

def create_pie_chart(data, title):
    """Helper function to create a Plotly pie chart."""
    if not data:
        return None
    fig = px.pie(
        names=list(data.keys()),
        values=list(data.values()),
        title=title,
        hole=0.3
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05] * len(data))
    return fig

def load_curriculum_for_subject(subject):
    """Loads the curriculum structure for a given subject."""
    filepath = f"{CURRICULUM_FOLDER}/{subject}.json"
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    st.set_page_config(layout="wide", page_title="Ethiopian Quiz System - Review Interface")
    st.title("Classification Dashboard & Review")

    # Display analytics
    stats = get_classification_stats()
    st.header("Classification Analytics")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_subject = create_pie_chart(stats['by_subject'], "Questions by Subject")
        if fig_subject:
            st.plotly_chart(fig_subject, use_container_width=True)
    with col2:
        fig_confidence = create_pie_chart(stats['by_confidence'], "Classification Confidence")
        if fig_confidence:
            st.plotly_chart(fig_confidence, use_container_width=True)
    with col3:
        fig_review = create_pie_chart(stats['by_review'], "Review Status")
        if fig_review:
            st.plotly_chart(fig_review, use_container_width=True)

    st.markdown("---")
    st.header("Review Questions")

    # Sidebar for filtering
    st.sidebar.header("Filter Questions")
    subjects = get_distinct_subjects()
    selected_subject = st.sidebar.selectbox("Subject", ["All"] + subjects)

    confidence_levels = ["All", "Low", "Medium", "High"]
    selected_confidence = st.sidebar.selectbox("Confidence Level", confidence_levels)

    needs_review_only = st.sidebar.checkbox("Only show questions needing review", True)

    # Build filters dictionary
    filters = {}
    if selected_subject != "All":
        filters['subject'] = selected_subject
    if selected_confidence != "All":
        filters['confidence_level'] = selected_confidence
    if needs_review_only:
        filters['needs_review'] = True

    # Load and display data
    questions = get_questions_for_review(filters)
    if not questions:
        st.warning("No questions found matching the selected criteria.")
        return

    df = pd.DataFrame([dict(q) for q in questions])
    st.dataframe(df[['id', 'question_text', 'subject', 'grade', 'unit', 'subunit', 'classification_confidence', 'needs_review', 'review_priority']])

    st.subheader("Edit Question Classification")
    question_id_to_edit = st.number_input("Enter Question ID to Edit", min_value=1, step=1)

    question_to_edit = next((q for q in questions if q['id'] == question_id_to_edit), None)

    if question_to_edit:
        st.write(f"**Editing Question:** {question_to_edit['question_text']}")

        curriculum = load_curriculum_for_subject(question_to_edit['subject'])
        if not curriculum:
            st.error(f"Could not load curriculum for subject: {question_to_edit['subject']}")
            return

        # Grade selection
        grades = list(curriculum['grades'].keys())
        selected_grade_index = grades.index(question_to_edit['grade']) if question_to_edit['grade'] in grades else 0
        new_grade = st.selectbox("Grade", grades, index=selected_grade_index)

        # Unit selection
        units = [u['unit_title'] for u in curriculum['grades'][new_grade]['units']]
        selected_unit_index = units.index(question_to_edit['unit']) if question_to_edit['unit'] in units else 0
        new_unit = st.selectbox("Unit", units, index=selected_unit_index)

        # Sub-unit selection
        sub_units = [su['sub_unit_title'] for u in curriculum['grades'][new_grade]['units'] if u['unit_title'] == new_unit for su in u['sub_units']]
        selected_subunit_index = sub_units.index(question_to_edit['subunit']) if question_to_edit['subunit'] in sub_units else 0
        new_subunit = st.selectbox("Sub-unit", sub_units, index=selected_subunit_index)

        if st.button("Update Classification"):
            update_data = {
                'grade': new_grade,
                'unit': new_unit,
                'subunit': new_subunit
            }
            update_question_manual(question_id_to_edit, update_data)
            st.success(f"Question {question_id_to_edit} updated successfully!")
            # Refresh the page to show the updated data
            st.rerun()
    else:
        st.info("Enter a valid Question ID from the table above to start editing.")

if __name__ == '__main__':
    main()
