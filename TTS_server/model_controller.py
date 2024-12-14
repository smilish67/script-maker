from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import torchaudio, torch, os



class ModelController:
    def __init__(
            self,
    ):
        self.model =  None

        CHECKPOINT_DIR = "./jimin/"
        CHECKPOINT_PATH = os.path.join(CHECKPOINT_DIR, "best_model_ji.pth")
        # 설정 로드
        print("Loading config...")
        config = XttsConfig()
        config.load_json(os.path.join(CHECKPOINT_DIR, "config.json"))
        config.model_args.tokenizer_file = os.path.join(CHECKPOINT_DIR, "vocab.json")
        config.model_args.dvae_checkpoint = os.path.join(CHECKPOINT_DIR, "dvae.pth")
        config.model_args.mel_norm_file = os.path.join(CHECKPOINT_DIR, "mel_stats.pth")

        # 모델 초기화 및 체크포인트 로드
        print("Loading model...")
        model = Xtts.init_from_config(config)
        model.load_checkpoint(config, checkpoint_path=CHECKPOINT_PATH)
        model.cuda()

        self.model = model
    
    def get_model(self):
        return self.model

    