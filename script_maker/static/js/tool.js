let existingMenu = null;

function open_menu(characterElement) {
    // 이미 열려 있는 메뉴가 같은 캐릭터의 메뉴인지 확인
    if (existingMenu && existingMenu.parentElement === characterElement) {
        // 같은 메뉴라면 닫기만 수행
        close_menu();
        return; // 함수 종료
    }

    // 다른 메뉴가 열려 있다면 닫기
    if (existingMenu) {
        close_menu();
    }



    // 현재 클릭된 캐릭터 아래에 메뉴를 추가
    let menu = characterElement.querySelector('.menu-options');
    const currentName = characterElement.textContent.trim();
    if (!menu || $(menu).is(':empty')) {
        menu = document.createElement('div');
        menu.classList.add('menu-options');
        menu.innerHTML = `
            <button onclick="bulkEdit(this.closest('.character'),'${currentName}'); event.stopPropagation();">일괄 수정</button>
            <button onclick="setVoiceActor(this.closest('.character'),'${currentName}'); event.stopPropagation();">성우 설정</button>
        `;
        characterElement.appendChild(menu);
    }

    const nameElement = characterElement;
    if (nameElement) {
        // contenteditable 속성을 직접 지정하여 텍스트만 수정 가능하게 설정
        nameElement.setAttribute('contenteditable', 'true'); // 수정 가능하도록 설정
        nameElement.focus(); // 수정 시작
        // 자식 요소들에 대해서는 contenteditable을 false로 설정하여 수정 방지
        Array.from(nameElement.children).forEach(child => {
            child.setAttribute('contenteditable', 'false');
        });
        nameElement.onblur = () => {
            nameElement.removeAttribute('contenteditable'); // 수정 완료 후 비활성화
            Array.from(nameElement.children).forEach(child => {
                child.removeAttribute('contenteditable'); // 자식 요소도 비활성화
            });
        };
    }

    // 메뉴 표시
    existingMenu = menu;
    menu.style.display = 'block';
}

// 다른 곳을 클릭했을 때 메뉴 숨기기
function close_menu() {
    if (existingMenu) {
        // 메뉴를 DOM에서 완전히 삭제
        existingMenu.remove();  // 메뉴 요소 자체를 제거
        existingMenu = null;
    }
}

function bulkEdit(characterElement, name) {
    const nameElement = characterElement;
    if (nameElement) {
        // 배치 내 같은 이름의 캐릭터 수정
        const characters = document.querySelectorAll('.character');
        const dialog = document.querySelectorAll('.dialogue');
        characters.forEach(character => {
            if ($(character).html().split('<')[0] === name) {
                $(character).text($(nameElement).html().split('<')[0]);
            }
        });
        dialog.forEach(dialog => {
            const dialogHtml = $(dialog).html();
            if (dialogHtml.includes(name)) {
                // 다이얼로그의 모든 캐릭터 이름을 새로운 이름으로 변경
                const newName = $(nameElement).html().split('<')[0]; // `<` 이전의 텍스트만 추출
                const updatedHtml = dialogHtml.replaceAll(name, newName); // 모든 인스턴스를 대체
                $(dialog).html(updatedHtml);
            }
        });
    }
    existingMenu = characterElement.querySelector('.menu-options');
    close_menu();    
}


function setVoiceActor(characterElement, name) {
    open_modal(name);
    close_menu();
}

function edit_dialog(dialog){
    if (dialog) {
        // contenteditable 속성을 직접 지정하여 텍스트만 수정 가능하게 설정
        dialog.setAttribute('contenteditable', 'true'); // 수정 가능하도록 설정
        dialog.focus(); // 수정 시작
        // 자식 요소들에 대해서는 contenteditable을 false로 설정하여 수정 방지
        Array.from(dialog.children).forEach(child => {
            child.setAttribute('contenteditable', 'false');
        });
        dialog.onblur = () => {
            dialog.removeAttribute('contenteditable'); // 수정 완료 후 비활성화
            Array.from(dialog.children).forEach(child => {
                child.removeAttribute('contenteditable'); // 자식 요소도 비활성화
            });
        };
    }
}


