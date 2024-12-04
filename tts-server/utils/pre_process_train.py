import sys
import os
import json

if __name__ == "__main__":
    # 인자를 개별적으로 사용 액터넘버 같이 주시면 됩니다.
    # ex) python pre_process.py 01
    if len(sys.argv) > 1:
        audio_num = sys.argv[1]

        json_files_path = f'../dataset/TL_' + audio_num
        audio_files_path = f'../dataset/TS_' + audio_num

        #get all audio files
        audio_files = os.listdir(audio_files_path)
        
        #re name audio files
        first_idx = 0
        for i, audio_file in enumerate(audio_files):
            if i==0:
                first_idx = int(audio_file.split('.')[0][-4:])
            audio_file_name = audio_file.split('.')[0][2:4] + audio_file.split('.')[0][-4:] + '.wav'
            os.makedirs(f'../dataset/actors/{audio_num}/' + audio_file.split('.')[0][2:4]+ '/wavs', exist_ok=True)
            os.rename(audio_files_path + '/' + audio_file, f'../dataset/actors/{audio_num}' + '/'+ audio_file.split('.')[0][2:4] +'/wavs/' + audio_file_name)

        all_text = {}
        #iterate each json file
        for json_file in os.listdir(json_files_path):
            emotional_type = json_file.split('.')[0][2:4]
            with open(json_files_path + '/' + json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = data[0]['script']['normalized']
                text2 = data[0]['script']['origin']
                for i in range(len(text)):
                    if emotional_type not in all_text:
                        all_text[emotional_type] = []
                    all_text[emotional_type].append((text[i], text2[i]))
                f.close()
        
        #save all text csv
        for key in all_text:
            with open(f'../dataset/actors/{audio_num}/{key}/metadata.csv', 'w', encoding='utf-8') as f:
                for i in range(len(all_text[key])):
                    # 4 digit number
                    f.write(key + f'{i+first_idx:04d}' + '|' + all_text[key][i][0] +'|'+ all_text[key][i][1]+ '\n')
                f.close()
                    

                
