import subprocess, os
import ctypes, sys
import requests, re
from bs4 import BeautifulSoup
import shutil

# helper multi-entry to list
def convert_to_list(data):
  return data.split(',')

# Copy downloaded mods to the user selected folder
def copy_downloaded_mods(mod_ids, gameAppId, final_folder):
  mod_folder_base = os.path.join(os.path.dirname(__file__), f'/steamcmd/steamapps/workshop/content/{gameAppId}/')

  def innerC(mod_id):
    mod_folder_path = os.path.join(mod_folder_base, mod_id)
    mods_folder_path = os.path.join(mod_folder_path, 'mods')

    if os.path.exists(mods_folder_path) and os.path.isdir(mods_folder_path):
      for item in os.listdir(mods_folder_path):
        item_path = os.path.join(mods_folder_path, item)
        if os.path.isfile(item_path):
          target_path = os.path.join(final_folder, item)
          if os.path.exists(target_path):
            print('Existing file found! Removing...')
            os.remove(target_path)

          print('Copying file ' + item_path)
          shutil.copy(item_path, target_path)
        elif os.path.isdir(item_path):
          target_folder_path = os.path.join(final_folder, item)
          if os.path.exists(target_folder_path):
            print('Existing folder found! Removing...')
            shutil.rmtree(target_folder_path)

          print('Copying folder ' + item_path)
          shutil.copytree(item_path, target_folder_path)

  print('\n')

  if isinstance(mod_ids, list):
    for mod_id in mod_ids:
      innerC(mod_id)
  else:
    innerC(mod_ids)
    
# Look for mods that are already downloaded 'Gets only folder names/ so if they are broken or empty user has to redownload them while updating them'
def lookMods(mod_ids, gameAppId):
  non_mods = []

  # check for url choice
  for m_id in mod_ids:
    if '?id=' in m_id:
      m_id = m_id.split('?id=')[1]

  directory = os.path.join(os.path.dirname(__file__), f'/steamcmd/steamapps/workshop/content/{gameAppId}/')

  for item in os.listdir(directory):
    item_path = os.path.join(directory, item)

    if os.path.isdir(item_path):
      if item in mod_ids:
        if isinstance(mod_ids, list):
          mod_ids.remove(item)
        else:
          mod_ids = []
  
  non_mods = mod_ids
  return non_mods

# This is used for Subscriber list to get mods from the steamworkshopweb and find ids of mods in that list
def lookupMods(url):
  modsIds = []

  response = requests.get(url)

  if response.status_code == 200:
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    element_with_class = soup.find_all(class_="collectionItemDetails")

    for element in element_with_class:
      a_elements = element.find_all('a')

      for a_element in a_elements:
        href = a_element.get('href')
        if href :
          match = re.search(r'\?id=(\d+)', href)
          if match:
            id_number = match.group(1)
            modsIds.append(id_number)
  
  return modsIds

# Used to download mods via steamcmd
def download_mods(mod_ids):
  if not mod_ids:
    print('Found no mods to download! Exiting....')
    return
  
  steamcmd_path = "steamcmd.exe"

  cmd = []

  # check if its list or not
  if not isinstance(mod_ids, list):
    if '?id=' in mod_ids:
      mod_ids = mod_ids.split('?id=')[1]
    cmd.append("+workshop_download_item" + " 108600 " + mod_ids)
  else: 
    for mod_id in mod_ids:
      for m_id in mod_ids:
        if '?id=' in m_id:
          m_id = m_id.split('?id=')[1]
      cmd.append("+workshop_download_item" + " 108600 " + mod_id.strip())
  

  try:
    sub = subprocess.call([steamcmd_path, "+login anonymous"]+ cmd + ["+quit"])
    copy_downloaded_mods(mod_ids, '108600', final_folder)
    print('\nDownloaded and copied mods into {final_folder}!')
  except subprocess.CalledProcessError as e:
    print(f"Error running script as administrator: {e}")

if __name__ == "__main__":
  intro_message = """
  **********************************************
  Welcome to the Project Zomboid SteamCMD Mod Downloader
  **********************************************

  Before running this program, please ensure that:
  1. You have SteamCMD installed on your system.
  2. This program is located in the same folder as steamcmd.exe.

  This tool allows you to easily download and update mods for Project Zomboid using SteamCMD.

  **********************************************
  """

  print(intro_message)

  choice = input('Choose if you want to paste url, id, subscriber playlist [url, id, modlist]: ')

  final_folder = input('Please provide full path to your Project Zomboid mods folder: ')

  match choice:
    case 'url':
      if input('Do you want to update all the mods?[yes, no] ') == 'yes':
        download_mods(convert_to_list(input('Paste or enter one url or multiple that are separated by [,]: ')))
      else:
        download_mods(lookMods(convert_to_list(input('Paste or enter one url or multiple that are separated by [,]: ')), "108600"))
    case 'id':
      if input('Do you want to update all the mods?[yes, no] ') == 'yes':
        download_mods(convert_to_list(input('Paste or enter one id or multiple that are separated by [,]: ')))
      else:
        download_mods(lookMods(convert_to_list(input('Paste or enter one id or multiple that are separated by [,]: ')), "108600"))
    case 'modlist':
      modIds = lookupMods(input('Please paste whole url of a subscriber list: '))

      if input('Do you want to update all the mods?[yes, no] ') == 'yes':
        download_mods(modIds)
      else:
        download_mods(lookMods(modIds, "108600"))