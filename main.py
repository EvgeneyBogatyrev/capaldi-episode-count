import os
from pathlib import Path

import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup as bs

import json
from tqdm import tqdm

def main():

    stats = {}
    for season in range(34,37):
        for episode in tqdm(range(0, 20)):
            filename = parse_html(f"http://www.chakoteya.net/DoctorWho/{season}-{episode}.html", f"Season {season-26}")
            if filename is not None:
                total_words, doctors_words, percentage = count_words_in_episode(filename)
                stats[filename] = {
                    "total" : total_words,
                    "doctor" : doctors_words,
                    "%" : percentage
                }

    with open("results.json", "w") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)


def parse_html(url, output_folder):
    try:
        response = requests.get(url)
        response.raise_for_status()
        #print(response.text)
        #exit()

        soup = bs(response.text, 'html.parser')

        for title in soup.find_all("title"):
            name = str(title).replace("<title>The Doctor Who Transcripts - ", "").replace("</title>", "")
            break

        soup_text = soup.decode().replace("\n", " ").replace("\r", " ")

        soup = bs(soup_text, "html.parser")

        for br in soup.find_all("br"):
            br.replace_with("\n")

        text = soup.get_text(separator=' ').strip()
        #text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
        
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        filename = os.path.join(output_folder, name + ".txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(text.strip())
        return filename
    except requests.exceptions.HTTPError:
        return None

def count_words_in_episode(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    lines = list(lines)

    df_dict = []
    for line in lines:
        if ":" not in line:
            continue
        words = line.strip().split(": ")
        name  = words[0]

        speech = ": ".join(words[1:])

        df_dict.append({
            "name" : name,
            "speech" : speech
        })
        
    df = pd.DataFrame(df_dict)
    names = list(np.unique(df["name"]))
    names = [x for x in names if "DOCTOR" in x]
    doctor = df[df["name"].isin(names)]


    doctor_speeches = list(doctor["speech"].to_list())
    count = sum([len(x.split(" ")) for x in list(df["speech"].to_list())])
    d_count = sum([len(x.split(" ")) for x in doctor_speeches])
    return count, d_count, d_count/count


main()