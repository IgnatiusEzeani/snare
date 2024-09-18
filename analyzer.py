import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import streamlit as st

def plot_emotions(selected_emotions, fileids, with_combined=True):
    """
    Function to plot emotions across testimony segments for multiple files.

    Args:
    - selected_emotions (list): List of emotions to plot.
    - fileids (list): List of file IDs for the specific files to plot.
    - with_combined (bool): If True, include the combined results from all files in the plot.
    - save_path (str or None): Path to save the plot. If None, the plot is not saved.
    """
    all_file_scores_df = pd.read_csv(f"llm_emotion_scores/all_file_scores.tsv", sep='\t')
    if len(selected_emotions) < 1:
        print("Please select at least one emotion to plot.")
        return

    title = "Plotting the journeys of\n" + ', '.join([f"'{e}'" for e in selected_emotions[:-1]]) + f" and '{selected_emotions[-1]}'\nacross testimony segments."
    # Set up the subplots in a 4x2 grid
    fig, axes = plt.subplots(5, 2, figsize=(16, 20), sharex=True, sharey=True)
    
    # Flatten axes array for easy indexing
    axes = axes.flatten()
    
    # Get data based on fileids (All or multiple specific files)
    data1 = all_file_scores_df[selected_emotions].rolling(10).mean().dropna()
    data2_list = [pd.read_csv(f"llm_emotion_scores/{f}_scores.tsv", sep='\t')[selected_emotions].rolling(10).mean().dropna() for f in fileids]
    
    for idx, data2 in enumerate(data2_list):
        st.write(f"Data for file ID {fileids[idx]}:")
        st.write(data2.head())  # Print the first few rows to verify

    # Define limits for x and y axis based on the entire data range
    x_limits = (min([data.index.min() for data in data2_list]), max([data.index.max() for data in data2_list]))
    y_limits = (min([data.min().min() for data in data2_list]), max([data.max().max() for data in data2_list]))  # Ensure the same y-axis scale for all plots

    # Plot each emotion in a separate subplot
    for i, emotion in enumerate(selected_emotions):
        ax = axes[i]
        if with_combined:
            # Plot for "All 998 Testimonies" first
            data1[emotion].plot(ax=ax, kind='line', title=emotion, fontsize=12, label='All 998 Testimonies', linestyle='--')

            # Plot for each fileid separately
            for idx, data2 in enumerate(data2_list):
                data2[emotion].plot(ax=ax, kind='line', title=emotion, fontsize=12, label=f"Testimony ID '{fileids[idx]}'")
        else:
            # Plot for each fileid separately
            for idx, data2 in enumerate(data2_list):
                data2[emotion].plot(ax=ax, kind='line', title=emotion, fontsize=12, label=f"Testimony ID '{fileids[idx]}'")

        # Set limits for x and y axes
        ax.set_xlim(x_limits)
        ax.set_ylim(y_limits)
        
        # Add legend
        ax.legend()
        
        # Set plot labels
        ax.set_ylabel("Emotion Score", fontsize=10)
        ax.set_xlabel("Segments", fontsize=10)
        
        # Hide unnecessary spines
        ax.spines[['top', 'right']].set_visible(False)

    # Hide any unused subplots
    for i in range(len(selected_emotions), len(axes)):
        fig.delaxes(axes[i])

    # Set overall title
    plt.suptitle(title, fontsize=20)

    # Optionally set a global x-axis label
    fig.text(0.5, 0.04, 'Testimony Segments: 0 --> 100', ha='center', fontsize=12)  # Global x-axis label

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