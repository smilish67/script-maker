import os
import json


def audio_formatter(files, pre_path, actor_num, type):
    for audio_file in files:
        split = audio_file.split('-')
        audio_file_name = type+ '_' + split[1]+"_" + actor_num +"_"+ split[4]
        os.rename(pre_path + '/' + audio_file, f'../dataset/wavs/' + audio_file_name)
        
def json_formatter(files, pre_path, actor_num, type):
    all_text = {}
    for json_file in files:
        emotional_type = json_file.split('-')[1][:2]
        with open(pre_path + '/' + json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if emotional_type not in all_text:
                all_text[emotional_type] = []
            for i in range(len(data[0]['script']['normalized'])):
                all_text[emotional_type].append((data[0]['script']['normalized'][i], data[0]['script']['origin'][i]))
            f.close()
            
    for key in all_text:
        with open(f'../dataset/metadata{type}.csv', 'a', encoding='utf-8') as f:
            for i in range(len(all_text[key])):
                # 4 digit number
                emo = key[0]
                if emo == 'N':
                    emotion = 'neu'
                elif emo == 'A':
                    if key[1] == '1':
                        emotion = 'ana'
                    elif key[1] == '2':
                        emotion = 'anb'
                    elif key[1] == '3':
                        emotion = 'anc'
                elif emo == 'H':
                    if key[1] == '1':
                        emotion = 'haa'
                    elif key[1] == '2':
                        emotion = 'hab'
                    elif key[1] == '3':
                        emotion = 'hac'
                elif emo == 'S':
                    if key[1] == '1':
                        emotion = 'saa'
                    elif key[1] == '2':
                        emotion = 'sab'
                    elif key[1] == '3':
                        emotion = 'sac'
                if type == 'T':
                    f.write(type + '_' + key + '_'+ actor_num + '_'+ f'{i+101:04d}' + '|' + f'[{emotion}]'+ all_text[key][i][0] +'\n')
                else:
                    f.write(type + '_' + key + '_'+ actor_num + '_'+ f'{i+51:04d}' + '|' + f'[{emotion}]' + all_text[key][i][0] +'\n')
            f.close()

if __name__ == "__main__":
    # origin_dataset 폴더에 모든 성우 폴더를 넣어놓고 실행
    path = os.path.join(os.path.dirname(__file__), "../origin_dataset")

    train_audio_path = []
    train_label_path = []
    val_audio_path = []
    val_label_path = []
    
    #mkdir dataset folder
    os.makedirs('../dataset/wavs', exist_ok=True)
    
    #get all folder start with TL
    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)) and f.startswith('TL'):
            train_label_path.append(f)
        if os.path.isdir(os.path.join(path, f)) and f.startswith('TS'):
            train_audio_path.append(f)
        if os.path.isdir(os.path.join(path, f)) and f.startswith('VL'):
            val_label_path.append(f)
        if os.path.isdir(os.path.join(path, f)) and f.startswith('VS'):
            val_audio_path.append(f)
    
    print("train audio 작업 중")
    for audio_file_path in train_audio_path:
        actor_num = audio_file_path.split('_')[2]
        audio_files = os.listdir(os.path.join(path, audio_file_path))
        audio_formatter(audio_files, "../origin_dataset/"+audio_file_path, actor_num, 'T')
    
    print("val audio 작업 중")
    for audio_file_path in val_audio_path:
        actor_num = audio_file_path.split('_')[2]
        audio_files = os.listdir(os.path.join(path, audio_file_path))
        audio_formatter(audio_files, "../origin_dataset/"+audio_file_path, actor_num, 'V')

    #initial train metadata.csv
    # with open(f'../dataset/metadataT.csv', 'w', encoding='utf-8') as f:
    #     f.write("audio_file|text\n")
    #     f.close()
    
    print("train label 작업 중")
    for json_file_path in train_label_path:
        actor_num = json_file_path.split('_')[2]
        json_files = os.listdir(os.path.join(path, json_file_path))
        json_formatter(json_files, "../origin_dataset/"+json_file_path, actor_num, 'T')
    
    # with open(f'../dataset/metadataV.csv', 'w', encoding='utf-8') as f:
    #     f.write("audio_file|text\n")
    #     f.close()
        
    print("val label 작업 중")
    for json_file_path in val_label_path:
        actor_num = json_file_path.split('_')[2]
        json_files = os.listdir(os.path.join(path, json_file_path))
        json_formatter(json_files, "../origin_dataset/"+json_file_path, actor_num, 'V')


                
