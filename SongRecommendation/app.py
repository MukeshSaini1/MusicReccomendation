import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster_and_urls(music_title):
    try:
        response = requests.get(f"https://saavn.dev/api/search/songs?query={music_title}")
        response.raise_for_status()
        data = response.json()

        if 'data' in data and isinstance(data['data']['results'], list) and len(data['data']['results']) > 0:
            result = data['data']['results'][0]
            poster_url = result['image'][2]['url']
            download_urls = result['downloadUrl']

            # Extract URLs and sort by quality (highest quality first)
            urls = {quality['quality']: quality['url'] for quality in download_urls}
            sorted_qualities = sorted(urls.keys(), key=lambda x: int(x.replace('kbps', '')), reverse=True)
            default_quality = sorted_qualities[0] if sorted_qualities else None
            default_url = urls.get(default_quality)

            return poster_url, default_url
        else:
            raise ValueError("Unexpected data format or no results found.")

    except requests.exceptions.RequestException as e:
        st.error(f"API request error: {e}")
        return "https://i.postimg.cc/0QNxYz4V/social.png", None
    except (IndexError, KeyError, ValueError) as e:
        st.error(f"Error fetching poster or URL: {e}")
        return "https://i.postimg.cc/0QNxYz4V/social.png", None

def recommender(song):
    song_index = songs[songs['track_name'] == song].index
    if not song_index.empty:
        song_index = song_index[0]
        distances = similarity[song_index]
        song_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_songs = []

        for i in song_list:
            song_id = i[0]
            song_name = songs.iloc[i[0]].track_name
            recommended_songs.append(song_name)
        return recommended_songs
    else:
        return []

# Streamlit Layout
st.title('Music Recommendation System')
st.write("Welcome to the Music Recommendation System! Select a song to get recommendations.")

# Load song list and similarity matrix
song_list = pickle.load(open('SongRecommendation/musicForLovers.pkl', 'rb'))
songs = pd.DataFrame(song_list)
similarity = pickle.load(open('https://github.com/AdarshVerma5/MusicReccomendation/blob/main/SongRecommendation/similarityFounded.pkl', 'rb'))

# User selects a song
selected_song = st.selectbox(
    'Which song would you like to recommend?',
    songs['track_name'].values
)

if st.button('Recommend'):
    if selected_song in songs['track_name'].values:
        recommendations = recommender(selected_song)
        if recommendations:
            st.write(f"Recommendations for **{selected_song}**:")

            cols = st.columns(3)  # Create 3 columns for layout

            with cols[0]:
                st.write("**Track Name**")

            with cols[1]:
                st.write("**Poster**")

            with cols[2]:
                st.write("**Play**")

            for song in recommendations:
                poster_url, download_url = fetch_poster_and_urls(song)

                # Use columns to display data in rows
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(song)

                with col2:
                    st.image(poster_url, width=200)

                with col3:
                    if download_url:
                        st.audio(download_url)  # Use st.audio to play song
                    else:
                        st.write("No preview available.")
        else:
            st.warning(f"No recommendations found for **{selected_song}**.")
    else:
        st.warning(f"The song **{selected_song}** is not in the playlist. Please select another song.")
