import sqlite3
import pandas as pd
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

def clean_text(text):
    return re.sub(r'[^a-zA-Z\s]', '', text)

# Connect to the SQLite database
db_file = "temp_out/p-info.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Fetch context and visual_category from the database
cursor.execute("SELECT context, visual_category FROM reels")
data = cursor.fetchall()

# Create a DataFrame from the fetched data
df = pd.DataFrame(data, columns=["context", "visual_category"])

# Clean the text in the 'context' and 'visual_category' columns
df['cleaned_context'] = df['context'].apply(clean_text)
df['cleaned_visual_category'] = df['visual_category'].apply(clean_text)

# Load the saved vectorizer (from training)
vectorizer = joblib.load('data/tfidf_vectorizer.joblib')

# Vectorize both the 'context' and 'visual_category' columns
context_features = vectorizer.transform(df['cleaned_context'])
visual_category_features = vectorizer.transform(df['cleaned_visual_category'])

# Combine the features from context and visual_category
all_features = hstack([context_features, visual_category_features])

# Load the trained classifier
clf = joblib.load('data/mbti_classifier.joblib')

# Ensure the number of features in the input matches the number of features the model was trained on
expected_features = clf.coef_.shape[1]
if all_features.shape[1] > expected_features:
    all_features = all_features[:, :expected_features]

# Predict MBTI types for each entry in the database based on the combined features
reels_mbti_predictions = clf.predict(all_features)

# Add the predictions to the DataFrame
df['Predicted_MBTI'] = reels_mbti_predictions

# Get the list of all MBTI types from the trained model (classes_ contains the labels)
all_mbti_types = clf.classes_

# Aggregate the MBTI predictions and calculate the percentages
aggregated_mbti = df['Predicted_MBTI'].value_counts(normalize=True) * 100  # Normalize to get percentages

# Combine the aggregated predictions with all MBTI types, filling missing types with 0
aggregated_mbti = pd.Series(0, index=all_mbti_types).add(aggregated_mbti, fill_value=0)

# Filter out personality types with 0% occurrence
aggregated_mbti = aggregated_mbti[aggregated_mbti > 0]

# Sort the aggregated predictions by percentage in descending order
aggregated_mbti_sorted = aggregated_mbti.sort_values(ascending=False)

# Query to fetch the top 10 most seen hashtags, excluding those with count <= 1
cursor.execute("SELECT hashtag, total_seen FROM hashtags WHERE total_seen > 1 ORDER BY total_seen DESC LIMIT 10")
top_10_hashtags_data = cursor.fetchall()

top_10_hashtags = [data[0] for data in top_10_hashtags_data]
top_10_total_seen = [data[1] for data in top_10_hashtags_data]

# Query to fetch all reels and their emotional tone categories
cursor.execute("SELECT emotional_tone_text FROM reels")
reels_data = cursor.fetchall()

cursor.execute("SELECT emotional_tone_hashtag FROM reels")
reels_data = reels_data + cursor.fetchall()

# Initialize sentiment counters
positive_count = 0
negative_count = 0

# Count the occurrences of each emotional tone category
for reel in reels_data:
    tone = reel[0].lower() if reel[0] else ''
    if tone == 'positive':
        positive_count += 1
    elif tone == 'negative':
        negative_count += 1

# Close the database connection
conn.close()

# Create a function to calculate the percentage of Optimists and Pessimists
def calculate_sentiment_percentage(positive_count, negative_count):
    total_sentiments = positive_count + negative_count
    if total_sentiments == 0:
        return 0, 0  # Avoid division by zero
    
    optimist_percentage = (positive_count / total_sentiments) * 100
    pessimist_percentage = (negative_count / total_sentiments) * 100

    return optimist_percentage, pessimist_percentage

# Get sentiment percentages (Optimist and Pessimist)
optimist_percentage, pessimist_percentage = calculate_sentiment_percentage(positive_count, negative_count)

# Prepare the report output in the desired format
report_filename = 'temp_out/temp_out_x1.txt'

with open(report_filename, 'w') as f:
    # Format MBTI results as required
    mbti_result = ",".join([f"{mbti_type}:{percentage:.2f}%" for mbti_type, percentage in aggregated_mbti_sorted.items()])
    f.write(f"MBTI<{mbti_result}>\n")

    # Format Top 10 hashtags as required
    hashtags_result = ",".join([f"{hashtag}:{count}" for hashtag, count in zip(top_10_hashtags, top_10_total_seen)])
    f.write(f"HTG<{hashtags_result}>\n")

    # Format sentiment result as required with percentages
    f.write(f"SENT<Optimist:{optimist_percentage:.2f}%,Pessimist:{pessimist_percentage:.2f}%>\n")

# Optionally, you can add a print statement to confirm the report generation
print(f"Report has been generated and saved to {report_filename}")
