import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV files (update file paths as needed)
transcribed_videos = pd.read_csv('Transcribed videos containing well-being - Arkusz1.csv')
non_wellbeing_videos = pd.read_csv('Videos not containing well-being - Arkusz1.csv')

# Convert the 'positivity' column to float
transcribed_videos['positivity'] = transcribed_videos['positivity'].str.replace(',', '.').astype(float)
non_wellbeing_videos['positivity'] = non_wellbeing_videos['positivity'].str.replace(',', '.').astype(float)

# Calculate basic statistics
transcribed_stats = transcribed_videos['positivity'].describe()
non_wellbeing_stats = non_wellbeing_videos['positivity'].describe()

print("Statistics for Videos Containing Well-being:")
print(transcribed_stats)
print("\nStatistics for Videos Not Containing Well-being:")
print(non_wellbeing_stats)

###############################################################################
# 1) KDE Plot
###############################################################################
plt.figure(figsize=(10, 6))
sns.kdeplot(
    data=transcribed_videos['positivity'],
    fill=True, label='Containing Well-being',
    alpha=0.5, clip=(0, 1)
)
sns.kdeplot(
    data=non_wellbeing_videos['positivity'],
    fill=True, label='Not Containing Well-being',
    alpha=0.5, clip=(0, 1)
)
plt.title('Positivity Distribution - KDE Plot')
plt.xlabel('Positivity')
plt.ylabel('Density')
plt.legend()
plt.grid(True)
plt.savefig('positivity_distribution_kde_plot.png')
plt.show()

###############################################################################
# 2) Histogram (Histplot)
###############################################################################
plt.figure(figsize=(10, 6))
sns.histplot(
    transcribed_videos['positivity'],
    color='blue',
    label='Containing Well-being',
    alpha=0.5,
    binwidth=0.1
)
sns.histplot(
    non_wellbeing_videos['positivity'],
    color='orange',
    label='Not Containing Well-being',
    alpha=0.5,
    binwidth=0.1
)
plt.title('Positivity Distribution - Histogram')
plt.xlabel('Positivity')
plt.ylabel('Count')
plt.legend()
plt.grid(True)
plt.savefig('positivity_distribution_histogram.png')
plt.show()
