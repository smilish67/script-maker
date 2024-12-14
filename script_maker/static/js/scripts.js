// 요소 선택
const overlay = document.getElementById('overlay');
const modal = document.getElementById('modal');
const closeModalButton = document.getElementById('close-modal');
let char_id = document.getElementById('char_id');
let cur_act_id = document.getElementById('cur_actor_id');
actor_info = {
}

function open_modal(name) {
    overlay.style.display = 'block';  // 오버레이 표시
    modal.style.display = 'block';   // 모달 창 표시
    cur_act_id.textContent = get_actor_info(name);
    char_id.textContent = name;
}

// 모달 닫기
closeModalButton.addEventListener('click', () => {
    overlay.style.display = 'none';  // 오버레이 숨김
    modal.style.display = 'none';   // 모달 창 숨김
});

// 오버레이 클릭 시 모달 닫기
overlay.addEventListener('click', () => {
    overlay.style.display = 'none';  // 오버레이 숨김
    modal.style.display = 'none';   // 모달 창 숨김
});

function setActor(actorElement) {
    const name = actorElement.textContent.trim();
    actor_info[char_id.textContent] = name;
    closeModalButton.click();
    // 모든 오디오 중단
    const allAudioElements = document.querySelectorAll("audio");
    allAudioElements.forEach(audio => {
        audio.pause();
        audio.currentTime = 0; // Reset to the beginning
    });
}


function get_actor_info(name) {
    return actor_info[name];
}

function playAudio(audioId) {
    const audioElement = document.getElementById(audioId);
    
    // Pause other audio elements to prevent overlapping sounds
    const allAudioElements = document.querySelectorAll("audio");
    allAudioElements.forEach(audio => {
        if (audio.id !== audioId) {
            audio.pause();
            audio.currentTime = 0; // Reset to the beginning
        }
    });

    // Play the selected audio
    if (audioElement.paused) {
        audioElement.play();
    } else {
        audioElement.pause();
    }
}


async function audioMaker(id) {
    const element = document.getElementById(id);
    const name = element.getElementsByClassName('character')[0].textContent.trim(); // 첫 번째 'character' 요소
    const actor = await get_actor_info(name)

    if (actor === undefined) {
        alert(name + "의 성우를 선택해주세요.")
        return
    }

    const dialog = element.getElementsByClassName('dialogue')[0].textContent.trim(); // 첫 번째 'dialogue' 요소
    const batch = id.split('-')[1] + '-' + id.split('-')[2]

    if (element.getElementsByClassName('audio')[0].textContent.trim() === "변환하기") {
        element.getElementsByClassName('audio')[0].textContent = "변환중.."; // 첫 번째 'audio' 요소
        element.style.pointerEvents = "none"; // 클릭 비활성화
        element.style.opacity = "0.5"; // 시각적으로 비활성화 효과

        await fetch('/audioMaker', {
            method: 'POST',
            body: JSON.stringify({
                webtoon: "gongik",
                fileName: batch,
                actor: actor,
                dialog: dialog
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())  // 응답을 JSON으로 변환
        .then(data => {
            path = data.file_url;
            element.style.pointerEvents = "auto"; // 클릭 활성화
            element.style.opacity = "1"; // 시각적으로 활성화 효과
            const audioID = 'audio-' + batch;
            const audioElement = document.getElementById(audioID);
            // 템플릿 리터럴 사용하여 동적으로 src 설정
            audioElement.src = `/static/${path}`;
            element.getElementsByClassName('audio')[0].textContent = "재생하기";
            // 클릭 이벤트 리스너 설정
            element.getElementsByClassName('audio')[0].onclick = () => audio_play(audioID);
            }
        ).catch(error => {
            console.error('Error:', error);
            element.style.pointerEvents = "auto"; // 클릭 활성화
            element.style.opacity = "1"; // 시각적으로 활성화 효과
        });
    }
}

function audio_play(id) {
    const element = document.getElementById(id);
    element.play();
}


async function convertBatchAudio(id) {
    const batch = document.getElementById(id);
    const allBatchScripts = batch.querySelectorAll('.script');

    for (let script of allBatchScripts) {
        const scriptId = script.id; // script-0-0, script-0-1 같은 ID
        if (script.querySelector('.audio').textContent.trim() === "변환하기") {
            await audioMaker(scriptId);
        }
    }
}

async function playBatchAudio(id) {
    const batch = document.getElementById(id);
    const allBatchScripts = batch.querySelectorAll('.script');
    //순서대로 실행 다음 대사가 실행되기 전까지 대기
    for (let script of allBatchScripts) {
        const scriptId = script.id; // script-0-0, script-0-1 같은 ID
        const audioId = 'audio-' + scriptId.split('-')[1] + '-' + scriptId.split('-')[2];
        const audioElement = document.getElementById(audioId);
        if (audioElement.src !== "") {
            audioElement.play();
            await new Promise(resolve => {
                audioElement.onended = resolve;
            });
        }
    }
}