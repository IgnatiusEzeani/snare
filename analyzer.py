import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
import math

def map_emotions():
    df = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
        columns=['lat', 'lon'])
    st.map(df)

def plot_emotions(selected_emotions, fileids, with_combined=True, barchart=False,
                  males=False, females=False):
    """
    Function to plot emotions across testimony segments for multiple files.

    Args:
    - selected_emotions (list): List of emotions to plot.
    - fileids (list): List of file IDs for the specific files to plot.
    - with_combined (bool): If True, include the combined results from all files in the plot.
    """
    all_file_scores_df = pd.read_csv(f"llm_emotion_scores/all_file_scores.tsv", sep='\t')
    males_df = pd.read_csv(f"llm_emotion_scores/male_scores.tsv", sep='\t')
    females_df = pd.read_csv(f"llm_emotion_scores/female_scores.tsv", sep='\t')

    if len(selected_emotions) < 1:
        return "Error: You must select at least one emotion label!"
    
    if len(fileids) < 1:
        return "Error: You must select at least one testimony ID!"

    if len(selected_emotions) > 4:
        title = "Plotting the journeys of\n" + ', '.join([f"'{e}'" for e in selected_emotions[:-1]]) + f" and '{selected_emotions[-1]}'\nacross testimony segments."
    else:
        title = "Plotting the journeys of " + ', '.join([f"'{e}'" for e in selected_emotions[:-1]]) + f" and '{selected_emotions[-1]}' across testimony segments."

    # Dynamically allocate the number of rows based on the number of emotions
    n_emotions = len(selected_emotions)
    n_cols = 2  # Fixed number of columns
    n_rows = math.ceil(n_emotions / n_cols) + 1 # Compute the number of rows needed

    # Set up the subplots grid based on the computed rows and columns
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4 * n_rows), sharex=True, sharey=True)
    
    # Flatten axes array for easy indexing
    axes = axes.flatten()
    
    # Get data based on fileids (All or multiple specific files)
    data1 = all_file_scores_df[selected_emotions].rolling(10).mean().dropna()
    male_data = males_df[selected_emotions].rolling(10).mean().dropna()
    female_data = females_df[selected_emotions].rolling(10).mean().dropna()
    data2_list = [pd.read_csv(f"llm_emotion_scores/{f}_scores.tsv", sep='\t')[selected_emotions].rolling(10).mean().dropna() for f in fileids]
    
    # Define limits for x and y axis based on the entire data range
    x_limits = (min([data.index.min() for data in data2_list]), max([data.index.max() for data in data2_list]))
    y_limits = (min([data.min().min() for data in data2_list]), max([data.max().max() for data in data2_list]))  # Ensure the same y-axis scale for all plots

    # Create a list to hold plot lines for the legend
    handles = []
    labels = []

    # Plot each emotion in a separate subplot
    for i, emotion in enumerate(selected_emotions):
        ax = axes[i]
        ax.set_title(emotion, fontsize=14)
        if with_combined:
            # Plot for "All 998 Testimonies" first
            line = ax.plot(data1.index, data1[emotion], linestyle='--', color='red', label='All 998 Testimonies')
            if i == 0:  # Only add the label once to avoid duplication
                handles.append(line[0])
                labels.append('All 998 Testimonies')
        if males:
            # Include female scores
            line = ax.plot(male_data.index, male_data[emotion], linestyle='--', color='blue', label='Male testimonies')
            if i == 0:  # Only add the label once to avoid duplication
                handles.append(line[0])
                labels.append('Male testimonies')
        if females:
            # Include female scores
            line = ax.plot(female_data.index, female_data[emotion], linestyle='--', color='green', label='Female testimonies')
            if i == 0:  # Only add the label once to avoid duplication
                handles.append(line[0])
                labels.append('Female testimonies')

        # Plot for each fileid separately
        for idx, data2 in enumerate(data2_list):
            if barchart: bar = ax.bar(data2.index, data2[emotion], label=f"Testimony ID '{fileids[idx]}'", alpha=0.7) 
            else: line = ax.plot(data2.index, data2[emotion], label=f"Testimony ID '{fileids[idx]}'")

            if i == 0:  # Only add the label once
                handles.append(bar[0] if barchart else line[0])
                labels.append(f"Testimony ID '{fileids[idx]}'")

        # Set limits for x and y axes
        ax.set_xlim(x_limits)
        ax.set_ylim(y_limits)
        
        # Set plot labels
        ax.set_ylabel(f"Moving average scores '{emotion}'", fontsize=12)
        # ax.set_xlabel("Segments", fontsize=12)
        
        # Hide unnecessary spines
        ax.spines[['top', 'right']].set_visible(False)


    # Add the legend to the last occupied subplot
    ax = axes[len(selected_emotions)]
    ax.axis('off')  # Turn off the axis for the subplot used for legend
    ax.legend(handles=handles, labels=labels, loc='center', fontsize=14)

    # Hide any unused subplots (besides the last one)
    for i in range(len(selected_emotions)+1, len(axes)):
        fig.delaxes(axes[i])

    # Set overall title
    plt.suptitle(title, fontsize=16)

    # Optionally set a global x-axis label
    fig.text(0.5, 0.04, 'Testimony Segments: 0 --> 100', ha='center', fontsize=14)  # Global x-axis label

    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Leave space for the global x-axis label

    # Render the plot in Streamlit
    st.pyplot(fig)

    # Optionally provide a download button for the plot
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=300, bbox_inches='tight')
    buffer.seek(0)
    
    st.download_button(
        label="Download plot as PNG",
        data=buffer,
        file_name="emotions_plot.png",
        mime="image/png"
    )