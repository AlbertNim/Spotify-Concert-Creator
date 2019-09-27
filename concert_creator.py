import sys
import os
import subprocess
import spotipy
import spotipy.util as util
import json
import requests
import csv
import math

def get_setlist():
	setlist_api = input("Enter your Setlist.fm API Key: ")
	artist = input("Input the MusicBrainz ID of the artist you want to find information on: ")
	url = 'https://api.setlist.fm/rest/1.0/artist/' + artist + '/setlists?p=1'
	headers = {'Accept': 'application/json', 'x-api-key': setlist_api}
	r = requests.get(url, headers=headers)
	data = r.json()
	
	try:	
		totalshows = int(data['total'])
	except:
		print('Artist not found in concert database!')
		sys.exit(1)

	#create the songlist
	most_recent_concert = data['setlist'][0]
	return most_recent_concert

def find_date(concert_info):
	concert_date = concert_info['eventDate']
	return concert_date

def find_song_list(concert_info):
	song_list = []
	for song_set in concert_info['sets']['set']:
		for song in song_set['song']:
			song_list.append(song['name'])
	return song_list


def create_setlist(artist_name, event_date, song_list):
	SPOTIFY_CLIENT_ID = input('Implement your Spotify Client ID Here')
	SPOTIFY_CLIENT_SECRET=input('Implement your Spotify Secret ID Here')
	SPOTIPY_REDIRECT_URI= input('Choose a Redirect URI')
	
	os.environ["SPOTIPY_CLIENT_ID"] = SPOTIFY_CLIENT_ID
	os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIFY_CLIENT_SECRET
	os.environ["SPOTIPY_REDIRECT_URI"] = SPOTIPY_REDIRECT_URI

	user_id = input('Enter in your spotify user ID')
	scope='user-library-read playlist-modify-public'
	playlist_name = artist_name + '_' + event_date + '_Concert'

	token = util.prompt_for_user_token(user_id, scope, redirect_uri='http://localhost:8888/callback')
	playlist_id = ''
	if token:
		sp = spotipy.Spotify(auth=token)
		playlists = sp.user_playlist_create(user_id, playlist_name, public=True)
		playlist_id = playlists['id']
		added = add_songs_playlist(user_id, playlist_id, song_list, artist_name, sp)
	else:
		print('Could not create a playlist!')
		sys.exit(1)
	
	return added

def add_songs_playlist(user_id, playlist_id, song_list, artist_name, sp):
	#translate a list of songs into a list of spotify ids
	id_list = []
	for song in song_list:
		val = sp.search(q='artist:' + artist_name + ' track:' + song, type='track')
		for x in val['tracks']['items']:
			if (x['name'].lower() == song.lower() or (x['name'].lower() == (song + " (Remastered)").lower())) and val['tracks']['items'][0]['artists'][0]['name'].lower() == artist_name.lower():
				for values in x['artists']:
					if values['name'] == artist_name:
						id_list.append(x['id'])
						break
			break
	try:
		if id_list:
			sp.user_playlist_add_tracks(user_id, playlist_id, id_list, position=None)
			return True
	except:
		return False
def main():
	artist_name = input("Enter in a artist name:" )
	user_id = input("Enter in your username")
	set_list = get_setlist()
	event_date = find_date(set_list)
	song_list = find_song_list(set_list)
	if create_setlist(artist_name, event_date, song_list):
		print("Playlist created! Enjoy the concert!")
	else:
		print("Error adding songs to the playlist. Please check your settings again!") 

main()